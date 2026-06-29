"""Complete solution: Full incident response workflow.

This is the reference implementation for Step 3.
Use this if you get stuck during the workshop.

Run with: python solution/full_workflow.py
"""

import asyncio
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

# Add parent dir to path so we can import tools
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

from agent_framework import WorkflowBuilder, WorkflowContext, executor
from agent_framework.azure import AzureAIAgentClient
from azure.identity.aio import AzureCliCredential

from tools.mock_infra import (
    check_alert_history, get_runbook,
    get_metrics, get_logs, check_dependencies,
    restart_pod, scale_service, flush_cache, toggle_feature_flag, escalate_to_human,
    get_health_status, run_smoke_test,
    post_to_slack, create_incident_ticket, update_status_page,
)

load_dotenv(Path(__file__).parent.parent / ".env")


@dataclass
class IncidentState:
    alert_title: str = ""
    alert_service: str = ""
    alert_severity: str = ""
    alert_description: str = ""
    triage_result: str = ""
    diagnostics_result: str = ""
    remediation_result: str = ""
    verification_result: str = ""
    comms_result: str = ""
    is_resolved: bool = False
    retry_count: int = 0
    max_retries: int = 1


@executor
async def triage(ctx: WorkflowContext[IncidentState]) -> str:
    state = ctx.state
    print(f"\n{'='*60}\n📋 TRIAGE\n{'='*60}")

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as client,
    ):
        agent = client.create_agent(
            name="TriageAgent",
            instructions="""You are an incident Triage Agent.
1. Use check_alert_history to see if this is recurring
2. Use get_runbook to find the playbook
3. Output: severity, recurring status, auto-remediation allowed, recommended incident type.
Be concise.""",
            tools=[check_alert_history, get_runbook],
        )

        result = await agent.run(
            f"Alert: {state.alert_title}\nService: {state.alert_service}\n"
            f"Severity: {state.alert_severity}\nDescription: {state.alert_description}"
        )
        state.triage_result = result.text
        print(f"\n{result.text}")

    return "diagnostics"


@executor
async def diagnostics(ctx: WorkflowContext[IncidentState]) -> str:
    state = ctx.state
    print(f"\n{'='*60}\n🔍 DIAGNOSTICS\n{'='*60}")

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as client,
    ):
        agent = client.create_agent(
            name="DiagnosticsAgent",
            instructions="""You are a Diagnostics Agent. Investigate using your tools.
1. get_metrics for resource utilization
2. get_logs for error patterns
3. check_dependencies for cascading failures
Output: specific root cause with evidence and exact remediation action needed.""",
            tools=[get_metrics, get_logs, check_dependencies],
        )

        result = await agent.run(
            f"Triage summary:\n{state.triage_result}\n\n"
            f"Service: {state.alert_service}\nInvestigate root cause."
        )
        state.diagnostics_result = result.text
        print(f"\n{result.text}")

    return "remediation"


@executor
async def remediation(ctx: WorkflowContext[IncidentState]) -> str:
    state = ctx.state
    print(f"\n{'='*60}\n🔧 REMEDIATION (attempt {state.retry_count + 1})\n{'='*60}")

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as client,
    ):
        agent = client.create_agent(
            name="RemediationAgent",
            instructions="""You are a Remediation Agent. Execute the fix based on diagnostics.
- OOM/memory leak → restart_pod
- High CPU/traffic → scale_service
- Stale cache → flush_cache
- External dependency failure → toggle_feature_flag
- Cannot auto-fix → escalate_to_human
Use exact names from diagnostics.""",
            tools=[restart_pod, scale_service, flush_cache, toggle_feature_flag, escalate_to_human],
        )

        result = await agent.run(
            f"Diagnostics:\n{state.diagnostics_result}\n\n"
            f"Service: {state.alert_service}\nExecute the fix."
        )
        state.remediation_result = result.text
        print(f"\n{result.text}")

    return "verification"


@executor
async def verification(ctx: WorkflowContext[IncidentState]) -> str:
    state = ctx.state
    print(f"\n{'='*60}\n✅ VERIFICATION\n{'='*60}")

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as client,
    ):
        agent = client.create_agent(
            name="VerificationAgent",
            instructions="""You are a Verification Agent. Check if the fix worked.
1. get_health_status for service health
2. run_smoke_test for functional tests
End with: VERDICT: RESOLVED or VERDICT: FAILED""",
            tools=[get_health_status, run_smoke_test],
        )

        result = await agent.run(
            f"Remediation:\n{state.remediation_result}\n\n"
            f"Service: {state.alert_service}\nVerify the fix."
        )
        state.verification_result = result.text
        print(f"\n{result.text}")

        if "RESOLVED" in result.text.upper():
            state.is_resolved = True
            return "communications"
        else:
            state.retry_count += 1
            if state.retry_count >= state.max_retries:
                return "communications"
            return "remediation"


@executor
async def communications(ctx: WorkflowContext[IncidentState]) -> None:
    state = ctx.state
    print(f"\n{'='*60}\n📢 COMMUNICATIONS\n{'='*60}")

    async with (
        AzureCliCredential() as credential,
        AzureAIAgentClient(async_credential=credential) as client,
    ):
        agent = client.create_agent(
            name="CommsAgent",
            instructions="""You are the Communications Agent.
1. Post summary to Slack #incidents
2. Create incident ticket
3. Update status page to 'operational' if resolved
Keep Slack message brief.""",
            tools=[post_to_slack, create_incident_ticket, update_status_page],
        )

        status = "RESOLVED" if state.is_resolved else "ESCALATED"
        result = await agent.run(
            f"Status: {status}\n"
            f"Service: {state.alert_service}\n"
            f"Triage: {state.triage_result[:200]}\n"
            f"Diagnostics: {state.diagnostics_result[:200]}\n"
            f"Remediation: {state.remediation_result[:200]}\n"
            f"Notify the team."
        )
        state.comms_result = result.text
        print(f"\n{result.text}")


async def main():
    # Build workflow
    workflow = (
        WorkflowBuilder[IncidentState]()
        .add_executor(triage, name="triage")
        .add_executor(diagnostics, name="diagnostics")
        .add_executor(remediation, name="remediation")
        .add_executor(verification, name="verification")
        .add_executor(communications, name="communications")
        .build()
    )

    # Load incident
    with open(Path(__file__).parent.parent / "data" / "incidents.json") as f:
        incidents = json.load(f)

    alert = incidents[0]
    print(f"🚨 INCIDENT RESPONSE: {alert['title']}")

    state = IncidentState(
        alert_title=alert["title"],
        alert_service=alert["service"],
        alert_severity=alert["severity"],
        alert_description=alert["description"],
    )

    final = await workflow.run(state=state)

    print(f"\n\n{'='*60}")
    print(f"🏁 DONE — Resolved: {'✅' if final.is_resolved else '❌'}")


if __name__ == "__main__":
    asyncio.run(main())
