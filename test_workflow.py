"""End-to-end test: MAF workflow with structured outputs, tools, and WorkflowBuilder."""
import asyncio
import os
import sys

from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from typing import Literal
from agent_framework import Agent, Executor, WorkflowBuilder, WorkflowContext, handler, tool
from agent_framework.foundry import FoundryChatClient
from agent_framework.openai import OpenAIChatOptions
from azure.identity import AzureCliCredential


# --- Pydantic Models (structured outputs) ---
class TriageResult(BaseModel):
    severity: Literal["critical", "high", "low"]
    incident_type: str = Field(description="Type of incident (e.g., resource_exhaustion, network)")
    summary: str = Field(description="One-line summary")


class DiagnosticsResult(BaseModel):
    root_cause: str = Field(description="Root cause of the incident")
    confidence: float = Field(ge=0, le=1, description="Confidence 0-1")
    recommended_action: str = Field(description="What to do next")


# --- Tools (mock infrastructure) ---
@tool
def check_alert_history(service_name: str) -> str:
    """Check recent alert history for a service."""
    return f"{service_name}: 3 OOMKilled events in last hour, P99 spike at 02:47 UTC"


@tool
def get_metrics(service_name: str) -> str:
    """Get current service metrics."""
    return f"{service_name}: CPU 85%, Memory 94% (limit 512Mi), P99 30200ms, restarts: 4"


@tool
def get_logs(service_name: str) -> str:
    """Get recent error logs."""
    return f"{service_name}: java.lang.OutOfMemoryError at PaymentProcessor.processTransaction()"


# --- Client factory ---
credential = AzureCliCredential()


def make_client():
    return FoundryChatClient(
        project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
        model=os.environ["FOUNDRY_MODEL"],
        credential=credential,
    )


# --- Executors (class-based workflow nodes) ---
class TriageExecutor(Executor):
    def __init__(self):
        super().__init__(id="triage")
        self._agent = Agent(
            make_client(),
            instructions="Classify the incident severity and type. Use check_alert_history for context.",
            tools=[check_alert_history],
            name="triage-agent",
            id="triage-agent",
            default_options=OpenAIChatOptions(response_format=TriageResult),
        )

    @handler
    async def triage(self, alert: str, ctx: WorkflowContext) -> None:
        response = await self._agent.run(alert)
        result = TriageResult.model_validate_json(response.text)
        print(f"  [Triage] severity={result.severity}, type={result.incident_type}")
        ctx.set_state("triage_result", result.model_dump())
        await ctx.send_message(result.model_dump())


class DiagnosticsExecutor(Executor):
    def __init__(self):
        super().__init__(id="diagnostics")
        self._agent = Agent(
            make_client(),
            instructions="Diagnose the root cause using metrics and logs. Be specific.",
            tools=[get_metrics, get_logs],
            name="diagnostics-agent",
            id="diagnostics-agent",
            default_options=OpenAIChatOptions(response_format=DiagnosticsResult),
        )

    @handler
    async def diagnose(self, triage: dict, ctx: WorkflowContext) -> None:
        input_msg = (
            f"Incident: {triage['summary']}\n"
            f"Type: {triage['incident_type']}\n"
            f"Service: payment-api"
        )
        response = await self._agent.run(input_msg)
        result = DiagnosticsResult.model_validate_json(response.text)
        print(f"  [Diagnostics] root_cause={result.root_cause}, confidence={result.confidence}")
        await ctx.yield_output(
            f"Root cause: {result.root_cause} (confidence: {result.confidence}). "
            f"Action: {result.recommended_action}"
        )


# --- Build and run workflow ---
async def main():
    triage = TriageExecutor()
    diagnostics = DiagnosticsExecutor()

    workflow = (
        WorkflowBuilder(start_executor=triage)
        .add_edge(triage, diagnostics)
        .build()
    )

    print("=" * 60)
    print("Running MAF workflow: Triage → Diagnostics")
    print("=" * 60)
    result = await workflow.run("ALERT: payment-api P99 latency > 30s, multiple OOMKilled pods detected")

    outputs = result.get_outputs()
    print(f"\n{'=' * 60}")
    print(f"WORKFLOW OUTPUT: {outputs}")
    print(f"{'=' * 60}")
    print("\n✅ SUCCESS: Multi-agent workflow works end-to-end!")
    print("   - Structured outputs (Pydantic response_format)")
    print("   - Tool calling (@tool decorator)")
    print("   - WorkflowBuilder with edges")
    print("   - State management (ctx.set_state)")
    print("   - Message passing (ctx.send_message)")
    print("   - Output emission (ctx.yield_output)")


if __name__ == "__main__":
    asyncio.run(main())
