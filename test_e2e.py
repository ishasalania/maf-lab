"""End-to-end test: full incident response pipeline with Azure AI Foundry.
Tests: structured agents, workflow routing, HITL.
"""
import asyncio
import json
import os
import sys

sys.path.insert(0, ".")
from dotenv import load_dotenv

load_dotenv()

from pydantic import BaseModel, Field
from typing import Literal, Any

from agent_framework import (
    Agent, Executor, handler, response_handler,
    WorkflowBuilder, WorkflowContext, WorkflowRunState,
    AgentExecutorResponse,
    tool, Case, Default,
)
from agent_framework.foundry import FoundryChatClient
from agent_framework.openai import OpenAIChatOptions
from azure.identity import AzureCliCredential

from tools.mock_infra import (
    check_alert_history, get_runbook, get_metrics, get_logs,
    check_dependencies, get_health_status, run_smoke_test,
    restart_pod, scale_service, post_to_slack,
)

# ═══════════════════════════════════════════════════════════════════
# PYDANTIC MODELS (Structured Outputs)
# ═══════════════════════════════════════════════════════════════════

class TriageResult(BaseModel):
    severity: Literal["critical", "high", "low"] = Field(description="Incident severity")
    incident_type: Literal["resource_exhaustion", "cascading_failure", "dependency_issue", "rate_limiting"] = Field(description="Classification")
    recurrence_count: int = Field(description="Times this happened in past 7 days", ge=0)
    recommended_runbook: str = Field(description="Runbook ID or 'none'")
    summary: str = Field(description="One-line triage summary")


class DiagnosticsResult(BaseModel):
    root_cause: str = Field(description="Identified root cause")
    evidence: list[str] = Field(description="Evidence supporting the diagnosis")
    affected_services: list[str] = Field(description="Services impacted")
    confidence: float = Field(description="Confidence 0.0-1.0", ge=0.0, le=1.0)


class RemediationPlan(BaseModel):
    action: str = Field(description="Primary remediation action")
    target_service: str = Field(description="Service to act on")
    risk_level: Literal["low", "medium", "high"] = Field(description="Risk of this action")
    rollback_procedure: str = Field(description="How to undo if it fails")
    estimated_duration_seconds: int = Field(description="Expected time to complete", ge=0)


class VerificationResult(BaseModel):
    healthy: bool = Field(description="Whether the service is healthy after remediation")
    tests_passed: int = Field(description="Number of tests passed", ge=0)
    tests_total: int = Field(description="Total tests run", ge=0)
    p99_latency_ms: int = Field(description="Current P99 latency", ge=0)
    summary: str = Field(description="Verification summary")


# ═══════════════════════════════════════════════════════════════════
# CLIENT SETUP
# ═══════════════════════════════════════════════════════════════════

client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL"],
    credential=AzureCliCredential(),
)

# ═══════════════════════════════════════════════════════════════════
# AGENTS
# ═══════════════════════════════════════════════════════════════════

triage_agent = Agent(
    client,
    id="triage-agent",
    name="triage-agent",
    instructions="""You are an incident triage specialist. Analyze the alert and use your tools to:
1. Check alert history for recurrence patterns
2. Find the relevant runbook
Then classify the severity and type.""",
    tools=[check_alert_history, get_runbook],
    default_options=OpenAIChatOptions(response_format=TriageResult),
)

diagnostics_agent = Agent(
    client,
    id="diagnostics-agent",
    name="diagnostics-agent",
    instructions="""You are a diagnostics engineer. Use your tools to identify the root cause:
1. Check metrics (memory, latency, cpu, error_rate, connections)
2. Pull error logs
3. Check dependency health
Synthesize findings into a root cause analysis.""",
    tools=[get_metrics, get_logs, check_dependencies],
    default_options=OpenAIChatOptions(response_format=DiagnosticsResult),
)

remediation_agent = Agent(
    client,
    id="remediation-planner",
    name="remediation-planner",
    instructions="""You are a remediation planner. Based on the diagnostics, create a remediation plan.
Consider risk, rollback procedures, and estimated duration. Do NOT execute anything — just plan.""",
    default_options=OpenAIChatOptions(response_format=RemediationPlan),
)

verification_agent = Agent(
    client,
    id="verification-agent",
    name="verification-agent",
    instructions="""You are a verification engineer. After remediation, verify the service is healthy:
1. Check health endpoints
2. Run smoke tests
Report whether the fix worked.""",
    tools=[get_health_status, run_smoke_test],
    default_options=OpenAIChatOptions(response_format=VerificationResult),
)

# ═══════════════════════════════════════════════════════════════════
# EXECUTORS (Workflow Nodes)
# ═══════════════════════════════════════════════════════════════════

class IngestAlert(Executor):
    """Entry point: parses alert JSON, stores in state, forwards to triage."""
    def __init__(self):
        super().__init__(id="ingest-alert")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext) -> None:
        alert = json.loads(message) if isinstance(message, str) else message
        ctx.set_state("incident", alert)
        await ctx.send_message(
            f"Alert: {alert['title']} | Service: {alert['service']} | "
            f"Severity reported: {alert['severity']} | Description: {alert['description']}"
        )


class ParseTriage(Executor):
    """Parses triage agent output into routing decision."""
    def __init__(self):
        super().__init__(id="parse-triage")

    @handler
    async def handle(self, message: AgentExecutorResponse, ctx: WorkflowContext) -> None:
        text = message.agent_response.text
        triage = TriageResult.model_validate_json(text)
        ctx.set_state("triage_result", triage.model_dump())
        await ctx.send_message(triage.severity)


class ToDiagnostics(Executor):
    """Reads state and constructs input for diagnostics agent."""
    def __init__(self):
        super().__init__(id="to-diagnostics")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext) -> None:
        incident = ctx.get_state("incident")
        triage = ctx.get_state("triage_result")
        await ctx.send_message(
            f"Diagnose this incident:\n"
            f"Service: {incident['service']}\n"
            f"Type: {triage['incident_type']}\n"
            f"Description: {incident['description']}\n"
            f"Check metrics, logs, and dependencies."
        )


class ReviewPlan(Executor):
    """HITL: pauses workflow for human approval of remediation plan."""
    def __init__(self):
        super().__init__(id="review-plan")

    @handler
    async def handle(self, message: AgentExecutorResponse, ctx: WorkflowContext) -> None:
        text = message.agent_response.text
        plan = RemediationPlan.model_validate_json(text)
        ctx.set_state("remediation_plan", plan.model_dump())
        approval = await ctx.request_info(
            f"REMEDIATION PLAN:\n"
            f"  Action: {plan.action}\n"
            f"  Target: {plan.target_service}\n"
            f"  Risk: {plan.risk_level}\n"
            f"  Rollback: {plan.rollback_procedure}\n\n"
            f"Approve? (yes/no)",
            str,
        )
        await ctx.send_message(approval)

    @response_handler
    async def on_response(self, original_request: str, response: str, ctx: WorkflowContext) -> None:
        await ctx.send_message(response)


class ExecuteRemediation(Executor):
    """Executes the approved plan."""
    def __init__(self):
        super().__init__(id="execute-remediation")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext) -> None:
        plan = ctx.get_state("remediation_plan")
        if "yes" in message.lower():
            await ctx.yield_output(
                f"✅ APPROVED — Executing: {plan['action']} on {plan['target_service']}"
            )
        else:
            await ctx.yield_output(
                f"❌ REJECTED — Plan not executed. Escalating to on-call."
            )


class MonitorOnly(Executor):
    """Terminal node for low-severity alerts."""
    def __init__(self):
        super().__init__(id="monitor-only")

    @handler
    async def handle(self, message: str, ctx: WorkflowContext) -> None:
        incident = ctx.get_state("incident")
        await ctx.yield_output(
            f"📋 LOW SEVERITY — Monitoring only: {incident['title']}. No action required."
        )


class Comms(Executor):
    """Terminal node: posts to Slack and yields output."""
    def __init__(self):
        super().__init__(id="comms")

    @handler
    async def handle(self, message: AgentExecutorResponse, ctx: WorkflowContext) -> None:
        incident = ctx.get_state("incident")
        triage = ctx.get_state("triage_result")
        text = message.agent_response.text
        await ctx.yield_output(
            f"🔔 COMMS [{triage['severity'].upper()}]: {incident['title']}\n"
            f"   Diagnostics: {text[:200]}"
        )


# ═══════════════════════════════════════════════════════════════════
# WORKFLOW ASSEMBLY
# ═══════════════════════════════════════════════════════════════════

def build_incident_workflow():
    ingest = IngestAlert()
    parse = ParseTriage()
    to_diag = ToDiagnostics()
    monitor = MonitorOnly()
    comms = Comms()

    def needs_diagnostics(msg: Any) -> bool:
        return msg in ("critical", "high")

    workflow = (
        WorkflowBuilder(start_executor=ingest)
        .add_edge(ingest, triage_agent)
        .add_edge(triage_agent, parse)
        .add_switch_case_edge_group(
            source=parse,
            cases=[
                Case(condition=needs_diagnostics, target=to_diag),
                Default(target=monitor),
            ],
        )
        .add_edge(to_diag, diagnostics_agent)
        .add_edge(diagnostics_agent, comms)
        .build()
    )
    return workflow


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════

async def main():
    # Load incidents
    with open("data/incidents.json") as f:
        incidents = json.load(f)

    workflow = build_incident_workflow()

    for incident in incidents:
        print(f"\n{'='*60}")
        print(f"PROCESSING: {incident['title']} [{incident['severity'].upper()}]")
        print(f"{'='*60}")

        result = await workflow.run(json.dumps(incident))
        state = result.get_final_state()
        outputs = result.get_outputs()

        print(f"State: {state}")
        for out in outputs:
            print(f"Output: {out}")

        # Check for HITL
        if state == WorkflowRunState.IDLE_WITH_PENDING_REQUESTS:
            events = result.get_request_info_events()
            for evt in events:
                print(f"⏸️  HITL Request: {evt.data}")
                # Auto-approve for testing
                result2 = await workflow.run(responses={evt.request_id: "yes"})
                print(f"Resumed: {result2.get_final_state()}")
                for out in result2.get_outputs():
                    print(f"Output: {out}")

        print()


if __name__ == "__main__":
    asyncio.run(main())
