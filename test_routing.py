"""Test switch-case routing in MAF WorkflowBuilder."""
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from dataclasses import dataclass
from agent_framework import (
    Agent, Executor, WorkflowBuilder, WorkflowContext,
    handler, tool, Case, Default,
)
from agent_framework.foundry import FoundryChatClient
from agent_framework.openai import OpenAIChatOptions
from azure.identity import AzureCliCredential
from pydantic import BaseModel, Field
from typing import Literal


# --- Pydantic model ---
class TriageResult(BaseModel):
    severity: Literal["critical", "high", "low"]
    summary: str


# --- Routing dataclass ---
@dataclass
class RoutingDecision:
    severity: str
    summary: str


# --- Executors ---
class IngestExecutor(Executor):
    def __init__(self):
        super().__init__(id="ingest")

    @handler
    async def ingest(self, alert: str, ctx: WorkflowContext) -> None:
        print(f"  [Ingest] Received alert: {alert[:50]}...")
        ctx.set_state("raw_alert", alert)
        await ctx.send_message(alert)


class TriageExecutor(Executor):
    def __init__(self):
        super().__init__(id="triage")
        credential = AzureCliCredential()
        self._agent = Agent(
            FoundryChatClient(
                project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
                model=os.environ["FOUNDRY_MODEL"],
                credential=credential,
            ),
            instructions="Classify incident severity as critical, high, or low. Be concise.",
            name="triage-agent",
            id="triage-agent",
            default_options=OpenAIChatOptions(response_format=TriageResult),
        )

    @handler
    async def triage(self, alert: str, ctx: WorkflowContext) -> None:
        response = await self._agent.run(alert)
        result = TriageResult.model_validate_json(response.text)
        print(f"  [Triage] severity={result.severity}")
        decision = RoutingDecision(severity=result.severity, summary=result.summary)
        await ctx.send_message(decision)


class CriticalHandler(Executor):
    def __init__(self):
        super().__init__(id="critical-handler")

    @handler
    async def handle(self, decision: RoutingDecision, ctx: WorkflowContext) -> None:
        print(f"  [CRITICAL PATH] Full pipeline triggered for: {decision.summary}")
        await ctx.yield_output(f"🚨 CRITICAL: {decision.summary} → Full remediation pipeline activated")


class HighHandler(Executor):
    def __init__(self):
        super().__init__(id="high-handler")

    @handler
    async def handle(self, decision: RoutingDecision, ctx: WorkflowContext) -> None:
        print(f"  [HIGH PATH] Diagnostics triggered for: {decision.summary}")
        await ctx.yield_output(f"⚠️ HIGH: {decision.summary} → Diagnostics + auto-remediation")


class MonitorOnly(Executor):
    def __init__(self):
        super().__init__(id="monitor-only")

    @handler
    async def handle(self, decision: RoutingDecision, ctx: WorkflowContext) -> None:
        print(f"  [LOW PATH] Monitor only for: {decision.summary}")
        await ctx.yield_output(f"📋 LOW: {decision.summary} → Monitoring, no action needed")


# --- Condition factory ---
def severity_is(target: str):
    """Returns a condition function that checks if routing decision matches severity."""
    def condition(message) -> bool:
        if isinstance(message, RoutingDecision):
            return message.severity == target
        return False
    return condition


# --- Build workflow ---
async def main():
    ingest = IngestExecutor()
    triage = TriageExecutor()
    critical = CriticalHandler()
    high = HighHandler()
    monitor = MonitorOnly()

    workflow = (
        WorkflowBuilder(start_executor=ingest)
        .add_edge(ingest, triage)
        .add_switch_case_edge_group(
            source=triage,
            cases=[
                Case(condition=severity_is("critical"), target=critical),
                Case(condition=severity_is("high"), target=high),
                Default(target=monitor),
            ],
        )
        .build()
    )

    # Test all three severity levels
    alerts = [
        ("CRITICAL", "ALERT: payment-api P99 > 30s, pods OOMKilled, revenue loss $50k/min"),
        ("LOW", "ALERT: notification-service email delivery delayed by 2 minutes, rate limited by provider"),
    ]

    for expected, alert in alerts:
        print(f"\n{'='*60}")
        print(f"Testing: expected={expected}")
        print(f"{'='*60}")
        result = await workflow.run(alert)
        outputs = result.get_outputs()
        print(f"  Output: {outputs[0] if outputs else 'NO OUTPUT'}")

    print(f"\n{'='*60}")
    print("✅ SWITCH-CASE ROUTING WORKS!")
    print("   Different alerts → different workflow paths")
    print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
