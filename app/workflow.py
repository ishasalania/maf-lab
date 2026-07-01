"""Workflow builder extracted for production use."""

import json
import os
import sys
from dataclasses import dataclass
from typing import Any, Literal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from agent_framework import (
    Agent,
    AgentExecutor,
    AgentExecutorRequest,
    AgentExecutorResponse,
    Case,
    Default,
    Message,
    WorkflowBuilder,
    WorkflowContext,
    executor,
)
from agent_framework.foundry import FoundryChatClient
from agent_framework.openai import OpenAIChatOptions
from azure.identity import DefaultAzureCredential
from typing_extensions import Never

from tools.mock_infra import (
    check_alert_history,
    check_dependencies,
    flush_cache,
    get_health_status,
    get_logs,
    get_metrics,
    get_runbook,
    post_to_slack,
    create_incident_ticket,
    restart_pod,
    run_smoke_test,
    scale_service,
    toggle_feature_flag,
)

load_dotenv()

# =============================================================================
# STRUCTURED OUTPUT MODELS
# =============================================================================


class TriageResult(BaseModel):
    severity: Literal["critical", "high", "medium", "low"]
    is_recurring: bool
    auto_remediation_allowed: bool
    root_cause_hypothesis: str
    recommended_action: str
    escalation_threshold_minutes: int


class DiagnosticsResult(BaseModel):
    root_cause: str
    evidence: list[str]
    affected_components: list[str]
    confidence: float = Field(ge=0.0, le=1.0)
    recommended_fix: str
    requires_restart: bool


class RemediationPlan(BaseModel):
    action: Literal["restart_pod", "scale_service", "flush_cache", "toggle_feature_flag", "escalate"]
    target_service: str
    target_details: str
    risk_level: Literal["low", "medium", "high"]
    estimated_downtime_seconds: int
    rollback_strategy: str
    requires_approval: bool


class VerificationResult(BaseModel):
    service_healthy: bool
    tests_passed: int
    tests_failed: int
    verification_status: Literal["pass", "fail", "degraded"]
    details: str


# =============================================================================
# AGENT FACTORIES
# =============================================================================


def make_client() -> FoundryChatClient:
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL"],
        credential=DefaultAzureCredential(),
    )


def create_triage_agent() -> Agent:
    return Agent(
        client=make_client(),
        name="TriageAgent",
        instructions=(
            "You are an incident Triage Agent. When given an alert:\n"
            "1. Call check_alert_history with the service name\n"
            "2. Call get_runbook with the incident_type\n"
            "Classify severity and recommend next steps."
        ),
        tools=[check_alert_history, get_runbook],
        default_options=OpenAIChatOptions(response_format=TriageResult),
    )


def create_diagnostics_agent() -> Agent:
    return Agent(
        client=make_client(),
        name="DiagnosticsAgent",
        instructions=(
            "You are an incident Diagnostics Agent. Investigate root cause:\n"
            "1. Call get_metrics for relevant metrics (memory, latency, error_rate)\n"
            "2. Call get_logs with severity='error'\n"
            "3. Call check_dependencies\n"
            "Synthesize findings with confidence score."
        ),
        tools=[get_metrics, get_logs, check_dependencies],
        default_options=OpenAIChatOptions(response_format=DiagnosticsResult),
    )


def create_remediation_agent() -> Agent:
    return Agent(
        client=make_client(),
        name="RemediationExecutor",
        instructions=(
            "You execute remediation plans. Call the appropriate tool:\n"
            "- restart_pod for pod restarts\n"
            "- scale_service for scaling\n"
            "- flush_cache for cache issues\n"
            "- toggle_feature_flag for flag changes\n"
            "Provide a clear 'reason' for the audit trail."
        ),
        tools=[restart_pod, scale_service, flush_cache, toggle_feature_flag],
    )


# =============================================================================
# WORKFLOW EXECUTORS
# =============================================================================


@dataclass
class RoutingDecision:
    severity: str
    service: str


@executor(id="ingest_alert")
async def ingest_alert(alert_json: str, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    alert = json.loads(alert_json)
    ctx.set_state("alert", alert)
    ctx.set_state("service", alert["service"])
    user_msg = Message("user", contents=[
        f"New alert:\nTitle: {alert['title']}\nService: {alert['service']}\n"
        f"Type: {alert['incident_type']}\nDescription: {alert['description']}"
    ])
    await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))


@executor(id="parse_triage")
async def parse_triage(response: AgentExecutorResponse, ctx: WorkflowContext[RoutingDecision]) -> None:
    triage = TriageResult.model_validate_json(response.agent_response.text)
    ctx.set_state("triage_result", triage)
    await ctx.send_message(RoutingDecision(severity=triage.severity, service=ctx.get_state("service")))


def needs_diagnostics(message: Any) -> bool:
    return isinstance(message, RoutingDecision) and message.severity in ("critical", "high")


@executor(id="to_diagnostics")
async def to_diagnostics(routing: RoutingDecision, ctx: WorkflowContext[AgentExecutorRequest]) -> None:
    triage: TriageResult = ctx.get_state("triage_result")
    service = ctx.get_state("service")
    user_msg = Message("user", contents=[
        f"Investigate incident:\nService: {service}\n"
        f"Hypothesis: {triage.root_cause_hypothesis}\n"
        f"Investigate: {triage.recommended_action}"
    ])
    await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))


@executor(id="monitor_only")
async def monitor_only(routing: RoutingDecision, ctx: WorkflowContext[Never, str]) -> None:
    alert = ctx.get_state("alert")
    await ctx.yield_output(
        f"LOW severity: {alert['title']} — monitoring only, no remediation required."
    )


@executor(id="comms")
async def comms(response: AgentExecutorResponse, ctx: WorkflowContext[Never, str]) -> None:
    diag = DiagnosticsResult.model_validate_json(response.agent_response.text)
    service = ctx.get_state("service")
    triage: TriageResult = ctx.get_state("triage_result")
    ctx.set_state("diagnostics_result", diag)
    report = (
        f"\U0001f6a8 INCIDENT RESPONSE REPORT\n"
        f"{'='*40}\n"
        f"Service: {service}\n"
        f"Severity: {triage.severity.upper()}\n"
        f"Root Cause: {diag.root_cause}\n"
        f"Confidence: {diag.confidence:.0%}\n"
        f"Affected: {', '.join(diag.affected_components)}\n"
        f"Recommended Fix: {diag.recommended_fix}\n"
        f"Requires Restart: {diag.requires_restart}\n"
    )
    await ctx.yield_output(report)


# =============================================================================
# BUILD WORKFLOW
# =============================================================================


def build_workflow():
    triage_agent_executor = AgentExecutor(create_triage_agent())
    diagnostics_agent_executor = AgentExecutor(create_diagnostics_agent())

    return (
        WorkflowBuilder(start_executor=ingest_alert)
        .add_edge(ingest_alert, triage_agent_executor)
        .add_edge(triage_agent_executor, parse_triage)
        .add_switch_case_edge_group(parse_triage, [
            Case(condition=needs_diagnostics, target=to_diagnostics),
            Default(target=monitor_only),
        ])
        .add_edge(to_diagnostics, diagnostics_agent_executor)
        .add_edge(diagnostics_agent_executor, comms)
        .build()
    )
