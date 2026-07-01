---
published: true
type: workshop
title: Building Multi-Agent AI Systems with Microsoft Agent Framework
short_title: Multi-Agent with MAF
description: Build a production-grade multi-agent incident response system using Microsoft Agent Framework (MAF) and Azure AI Foundry. Learn structured outputs, workflow graphs, conditional routing, and human-in-the-loop patterns.
level: intermediate
authors:
  - Isha Salania
  - Kiran Panchal
  - Ricardo Niepel
contacts:
  - "@ishasalania"
  - "@kiranpanchal"
  - "@intricatecloud"
duration_minutes: 120
tags: python, ai, agents, microsoft-agent-framework, azure-ai-foundry, multi-agent, workflow, human-in-the-loop
banner_url: assets/banner.jpg
navigation_levels: 2
navigation_numbering: true
sections_title:
  - Introduction
  - "What is MAF?"
  - Environment Setup
  - "Challenge 1: Structured Agents"
  - "Challenge 2: Workflow Graphs"
  - "Challenge 3: Human-in-the-Loop"
  - "Challenge 4: Advanced (Bonus)"
  - Wrap-up & Resources
---

# Building Multi-Agent AI Systems with MAF

> **From Copilot to Orchestrated Agents** — Build a production-grade multi-agent incident response system using Microsoft Agent Framework and Azure AI Foundry.

**WeAreDevelopers World Congress 2026** — Berlin, Friday 10 July · 12:15–14:15 · Room Ulm

## The Scenario

It's 3 AM. A production alert fires: **"Payment API P99 latency > 30 seconds."**

A single chatbot can't handle this. You need a system where **specialized agents collaborate** — one triages, one diagnoses, one plans a fix, one asks a human for approval, and one verifies the fix worked. Each agent does one thing well. The workflow graph connects them.

That's what you'll build in this workshop.

```text
                         ┌─ [CRITICAL] ─→ Diagnostics ─→ Remediation (HITL) ─→ Verify ─→ Comms
                         │
  Alert ─→ Triage ─→ Switch ─ [HIGH] ────→ Diagnostics ─→ Remediation ─→ Comms
                         │
                         └─ [LOW] ─────→ Monitor Only
```

## The Three Test Incidents

You'll process all three during the workshop — each triggers a different path through the same system:

| # | What Happened | Severity | Workflow Path |
|---|---|---|---|
| 1 | Payment API P99 > 30s, pods OOMKilled | **CRITICAL** | Full pipeline + human approval |
| 2 | Order Service cascading errors, 23% error rate | **HIGH** | Diagnostics → Remediation → Comms |
| 3 | Notification emails failing, rate limited | **LOW** | Monitor only |

Same code, different outcomes — because the Triage Agent returns **structured data** that the workflow uses for **deterministic routing**.

## Prerequisites

| Requirement | Details |
|---|---|
| Laptop | With a browser (for Codespaces) or Python 3.10+ locally |
| GitHub account | For Codespaces or cloning the repo |
| GitHub Copilot | VS Code extension (helpful, not required) |
| Azure CLI | Installed and authenticated (`az login`) |
| Python basics | Functions, pip, async/await |

Azure resources and credentials will be provided by your coaches.

## Workshop Flow

| Time | Activity | Duration |
|------|----------|----------|
| 12:15 | Introduction & Setup | 15 min |
| 12:30 | Challenge 1: Structured Agents | 30 min |
| 13:00 | Challenge 2: Workflow Graphs | 30 min |
| 13:30 | Break | 5 min |
| 13:35 | Challenge 3: Human-in-the-Loop | 25 min |
| 14:00 | Challenge 4: Advanced (Bonus) | 15 min |
| 14:15 | Wrap-up & Q&A | — |

---

# What is Microsoft Agent Framework?

## The Big Picture

[Microsoft Agent Framework (MAF)](https://github.com/microsoft/agent-framework) is an open-source framework for building **production-grade AI agents and multi-agent workflows** in Python and .NET. It was created by the teams behind [Semantic Kernel](https://github.com/microsoft/semantic-kernel) and [AutoGen](https://github.com/microsoft/autogen) — MAF is their direct successor, combining the best of both.

> MAF is the framework Microsoft uses internally for enterprise agent deployments. It's designed for **reliability and governance**, not just prototyping.

**Official resources:**
- [MAF GitHub Repository](https://github.com/microsoft/agent-framework) — Source code, samples, and docs
- [MAF Overview (MS Learn)](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview) — Architecture and concepts
- [MAF User Guide](https://learn.microsoft.com/agent-framework/user-guide/overview) — In-depth development guide
- [MAF Quick Start Tutorial](https://learn.microsoft.com/agent-framework/tutorials/quick-start) — Your first agent
- [PyPI: agent-framework-core](https://pypi.org/project/agent-framework-core/) — Python package
- [MAF Blog](https://devblogs.microsoft.com/agent-framework/) — New features and patterns

## Why Multi-Agent?

A single agent (like Copilot) handles one task at a time. For complex problems, you need **specialized agents that collaborate**:

```text
Single Agent (Copilot):          Multi-Agent (MAF):
┌──────────────┐                 ┌────────┐    ┌──────────┐    ┌─────────┐
│  One LLM     │                 │ Triage │───→│ Diagnose │───→│ Approve │
│  does        │                 │ Agent  │    │ Agent    │    │ (Human) │
│  everything  │                 └────────┘    └──────────┘    └────┬────┘
└──────────────┘                                                    │
                                                              ┌─────▼─────┐
                                                              │ Remediate │
                                                              │ Agent     │
                                                              └───────────┘
```

**Why?** Because in production:
- You need **typed contracts** between agents (not free text)
- Different situations need **different execution paths** (not one-size-fits-all)
- Dangerous actions need **human approval** before executing
- Failures need **retry logic** with escalation

## MAF Architecture: The Building Blocks

MAF provides two categories of capabilities:

| Category | Description |
|----------|-------------|
| **[Agents](https://learn.microsoft.com/agent-framework/agents/)** | Individual agents that use LLMs to process inputs, call tools, and generate responses |
| **[Workflows](https://learn.microsoft.com/agent-framework/workflows/)** | Graph-based workflows that connect agents and functions with type-safe routing, checkpointing, and HITL |

Here's how the pieces stack up:

```text
┌───────────────────────────────────────────────────────────────┐
│                    Your Application                            │
├───────────────────────────────────────────────────────────────┤
│  WorkflowBuilder  │  @executor  │  @workflow + @step          │  ← Orchestration
├───────────────────────────────────────────────────────────────┤
│  Agent  │  AgentExecutor  │  ctx (state, messaging, HITL)     │  ← Agent Layer
├───────────────────────────────────────────────────────────────┤
│  FoundryChatClient  │  @tool  │  Pydantic response_format     │  ← Primitives
├───────────────────────────────────────────────────────────────┤
│  Azure AI Foundry  │  GPT-4.1  │  AzureCliCredential          │  ← Infrastructure
└───────────────────────────────────────────────────────────────┘
```

### Key Classes You'll Use

| Class/Decorator | What It Does | Docs |
|-----------------|--------------|------|
| `Agent` | Wraps an LLM with instructions, tools, and output format. The core building block. | [Agent docs](https://learn.microsoft.com/agent-framework/agents/) |
| `FoundryChatClient` | Connects to Azure AI Foundry. Lightweight — no server-side resources created. | [Foundry integration](https://github.com/microsoft/agent-framework/tree/main/python/packages/foundry) |
| `@tool` | Marks a Python function as callable by an agent. Supports `approval_mode`. | [Tools docs](https://learn.microsoft.com/agent-framework/agents/tools/) |
| `response_format` | Pydantic model that constrains LLM output to valid typed JSON. | [Structured output](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents) |
| `WorkflowBuilder` | Declares a directed graph of executors with edges and conditions. | [Workflows docs](https://learn.microsoft.com/agent-framework/workflows/) |
| `@executor` | A node in the workflow graph. Receives messages, accesses shared state, emits output. | [Workflow samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows) |
| `AgentExecutor` | Wraps an `Agent` so it can be used as a node in a `WorkflowBuilder` graph. | [Workflow samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows) |
| `WorkflowContext` (`ctx`) | The context object in every executor — provides `set_state()`, `get_state()`, `send_message()`, `yield_output()`, `request_info()`. | [Workflow samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows) |

### How MAF Differs from Other Frameworks

| | MAF | LangChain | AutoGen | CrewAI |
|---|---|---|---|---|
| **Typed outputs** | `response_format` (hard constraint) | Output parsers (best-effort) | Free text | Free text |
| **Workflow engine** | Graph-based `WorkflowBuilder` | Chains (linear) | Group chat | Sequential tasks |
| **HITL** | First-class (`request_info`, tool approval) | Custom callbacks | Human proxy agent | Manual |
| **Routing** | Deterministic switch-case on data | LLM-decided | LLM-decided | LLM-decided |
| **State** | Built-in `ctx.set_state/get_state` | Manual | Shared messages | Shared memory |
| **Production focus** | Enterprise (governance, telemetry, durability) | Prototyping | Research | Prototyping |

<div class="info" data-title="For experts">

MAF is the direct successor to both Semantic Kernel and AutoGen, created by the same teams. It combines AutoGen's simple agent abstractions with Semantic Kernel's enterprise features — session-based state, type safety, middleware, telemetry — and adds graph-based workflows. [Learn more about the lineage](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview).

</div>

---

# Challenge 0: Environment Setup

## Azure Resources (Provided)

Your coaches have pre-provisioned these resources. You do NOT need to create them yourself.

| Resource | Purpose |
|----------|---------|
| AI Foundry Account (AIServices, S0) | Hosts the GPT-4.1 model |
| Foundry Project | Provides your project endpoint |
| GPT-4.1 Deployment (GlobalStandard) | The LLM all agents call |
| RBAC: `Cognitive Services OpenAI User` | Your permission to call the model |
| RBAC: `Cognitive Services Contributor` | Your permission to manage agents |

<div class="info" data-title="For coaches / tech team">

All infrastructure is codified in `infrastructure/` (Terraform). Run `terraform apply -var='attendee_object_ids=["oid1","oid2"]'` to deploy everything including attendee RBAC. See `infrastructure/README.md`.

</div>

## Step 1: Get the Code

### Option A: Codespaces (Recommended — Zero Setup)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ishasalania/maf-lab?quickstart=1)

Everything is pre-installed: Python 3.11, Azure CLI, all pip packages. Click the button, wait 60 seconds, done.

### Option B: Local Setup

```bash
git clone https://github.com/ishasalania/maf-lab.git
cd maf-lab
python -m venv .venv && source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate                            # Windows
pip install -r requirements.txt
```

## Step 2: Configure Environment

Your coach will provide the Foundry endpoint. Create your `.env` file:

```bash
cp .env.example .env
```

Fill in the values:

```text
FOUNDRY_PROJECT_ENDPOINT=https://<your-foundry>.services.ai.azure.com/api/projects/<project-name>
FOUNDRY_MODEL=gpt-4.1
```

## Step 3: Authenticate

```bash
az login
az account set --subscription "<your-subscription-id>"
```

### How Authentication Works

```text
Your Code → AzureCliCredential → az login session → Azure AD → Token → Foundry API
```

No API keys. No secrets in `.env`. Just `az login` and your Azure account does the rest. This is **passwordless authentication** — the recommended pattern for development.

## Step 4: Verify

Open `challenge-0/verify-setup.ipynb` and run all cells. You should see:

- ✅ Python version OK
- ✅ Dependencies installed
- ✅ Environment variables loaded
- ✅ Azure CLI authenticated
- ✅ Agent returns structured output

<div class="warning" data-title="Stuck?">

Don't spend more than 5 minutes on setup. Raise your hand — that's what coaches are for!

</div>

---

# Challenge 1: Structured Agents

## The Problem: Free Text Is Unreliable

A typical "agent" response:

```text
The severity appears to be critical. The service seems to be experiencing
memory issues. I'd recommend restarting the pod, but we should also check...
```

How do you use this downstream? You'd regex it. You'd pray. And you'd get bitten when the LLM says "CRITICAL" one time and "Critical-level" the next.

**This is the fundamental problem that makes multi-agent systems impossible** — if Agent A's output is unpredictable, Agent B can't make reliable decisions based on it.

## The Fix: Pydantic `response_format`

MAF solves this with **structured outputs** — you define a Pydantic model, and the LLM is **forced** to return valid JSON matching that schema. Not "encouraged" — *forced*. It's a hard constraint at the model inference level.

```python
from pydantic import BaseModel, Field
from typing import Literal

class TriageResult(BaseModel):
    severity: Literal["critical", "high", "low"]       # Only these 3 values allowed
    incident_type: str                                   # Free text, but must be present
    recurrence_count: int                                # Integer, not "about 3 times"
    recommended_runbook: str = Field(
        description="Runbook ID or 'NONE' if no match"   # LLM reads this description
    )
    summary: str                                         # Brief summary for humans
```

Then you pass it to the agent:

```python
from agent_framework import Agent
from agent_framework.openai import OpenAIChatOptions

agent = Agent(
    client=client,
    name="TriageAgent",
    instructions="You are an incident triage specialist...",
    tools=[check_alert_history, get_runbook],
    default_options=OpenAIChatOptions(response_format=TriageResult),
)

response = await agent.run("Payment API P99 > 30s, pods OOMKilled")
result = TriageResult.model_validate_json(response.text)
print(result.severity)  # "critical" — guaranteed to be one of the Literal values
```

### How It Works Under the Hood

```text
1. You define a Pydantic model (TriageResult)
2. MAF converts it to JSON Schema automatically
3. The schema is sent to GPT-4.1 as response_format parameter
4. GPT-4.1 is constrained to ONLY output valid JSON matching that schema
5. MAF validates the response against your Pydantic model
6. You get a typed Python object — not a string to parse
```

This is NOT prompt engineering — it's a **hard constraint** at model inference level. The LLM literally cannot return invalid output.

<div class="info" data-title="Deep dive">

The `response_format` parameter uses OpenAI's [Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) feature. MAF handles the schema conversion automatically — you just write a Pydantic model.

</div>

## Tools: Giving Agents Abilities

Agents aren't just LLMs — they can call **tools** (Python functions) to interact with the real world:

```python
from agent_framework import tool
from typing import Annotated

@tool
def get_metrics(
    service_name: Annotated[str, "Name of the service to query"],
    metric_type: Annotated[str, "Type: cpu, memory, latency, error_rate"] = "all",
) -> str:
    """Retrieve service performance metrics."""
    return f"CPU: 85%, Memory: 92%, P99: 30200ms for {service_name}"
```

The `Annotated[str, "description"]` tells the LLM what each parameter means. The docstring tells it when to use the tool. MAF handles the function-calling protocol automatically.

## Your Task

Open `challenge-1/challenge.ipynb` and build four agents:

| Agent | Output Model | Tools | Purpose |
|-------|-------------|-------|---------|
| **Triage** | `TriageResult` (provided) | `check_alert_history`, `get_runbook` | Classify severity and incident type |
| **Diagnostics** | `DiagnosticsResult` (build it) | `get_metrics`, `get_logs`, `check_dependencies` | Root cause analysis |
| **Remediation** | `RemediationPlan` (build it) | `restart_pod`, `scale_service`, `flush_cache` | Action plan with risk level |
| **Verification** | `VerificationResult` (build it) | `get_health_status`, `run_smoke_test` | Confirm the fix worked |

### Hints

- Use `Literal["value1", "value2"]` for constrained enums (severity, risk level, status)
- Use `Field(description="...")` so the LLM understands each field's purpose
- Use `Field(ge=0.0, le=1.0)` for bounded numeric fields like confidence scores
- Look at `tools/mock_infra.py` to see all available tools and their signatures

<div class="tip" data-title="Success Criteria">

Each agent returns a validated Pydantic object — no regex, no parsing, just typed data you can use programmatically.

</div>

---

# Challenge 2: Workflow Graphs

## The Problem: Ad-Hoc Chaining Doesn't Scale

In Challenge 1, you called agents manually in sequence:

```python
triage_result = await triage_agent.run(alert)
diagnostics_result = await diagnostics_agent.run(triage_result.text)
```

This works for one linear path. But production incidents need **branching**: CRITICAL goes through a full pipeline with human approval, HIGH skips approval, LOW just logs it. With manual chaining, you'd write nested if/else statements. Add 5 more paths, 3 more agents, error handling, state passing — it becomes unmaintainable.

## The Fix: WorkflowBuilder

MAF's `WorkflowBuilder` lets you declare your agent topology as a **directed acyclic graph (DAG)**. You define **what connects to what** — the engine handles execution, message passing, and state.

```text
                                    ┌───────────┐
                                    │  SWITCH   │
                                    ├───────────┤
 ingest ─→ triage_agent ─→ parse ──│ critical  │──→ to_diagnostics ──→ diagnostics_agent ──→ comms
                                    │ high      │──→ to_diagnostics ──→ diagnostics_agent ──→ comms
                                    │ low       │──→ monitor_only
                                    └───────────┘
```

### Executors: The Nodes of Your Graph

An **executor** is a node in the workflow graph. It receives a message, does work, and either sends a message downstream or emits a final output.

**Function-based executors** — for simple transformations:

```python
from agent_framework import executor, WorkflowContext

@executor(id="ingest_alert")
async def ingest_alert(alert_json: str, ctx: WorkflowContext) -> None:
    alert = json.loads(alert_json)
    ctx.set_state("service", alert["service"])       # Store for downstream nodes
    await ctx.send_message(f"Triage this: {alert}")   # Pass to next node
```

**Class-based executors** — when you need type-aware message handlers:

```python
from agent_framework import Executor, handler, AgentExecutorResponse

class ParseTriage(Executor):
    def __init__(self):
        super().__init__(id="parse-triage")

    @handler
    async def handle(self, message: AgentExecutorResponse, ctx: WorkflowContext) -> None:
        # message.agent_response.text contains the agent's JSON output
        result = json.loads(message.agent_response.text)
        ctx.set_state("severity", result["severity"])
        await ctx.send_message(RoutingDecision(severity=result["severity"]))
```

### The WorkflowContext (`ctx`)

Every executor receives a `ctx` object. This is your interface to the workflow engine:

| Method | Sync/Async | Purpose |
|--------|-----------|---------|
| `ctx.set_state(key, value)` | **Sync** | Store data for any downstream executor to read |
| `ctx.get_state(key)` | **Sync** | Retrieve data stored by any upstream executor |
| `await ctx.send_message(msg)` | **Async** | Send a message to the next node in the graph |
| `await ctx.yield_output(result)` | **Async** | Emit a final result the caller can read |
| `await ctx.request_info(data, type)` | **Async** | Pause the workflow and ask a human for input (Challenge 3) |

<div class="warning" data-title="Common mistake">

`ctx.set_state()` and `ctx.get_state()` are **synchronous** — don't `await` them.
`ctx.send_message()`, `ctx.yield_output()`, and `ctx.request_info()` are **async** — you MUST `await` them.

</div>

### AgentExecutor: Bridging Agents and Workflows

To use an `Agent` as a node in a workflow, wrap it in `AgentExecutor`:

```python
from agent_framework import AgentExecutor, AgentExecutorRequest, Message

triage_exec = AgentExecutor(triage_agent)

# To send input to an AgentExecutor, send an AgentExecutorRequest:
msg = Message("user", contents=["Triage this alert..."])
await ctx.send_message(AgentExecutorRequest(messages=[msg], should_respond=True))
```

The `AgentExecutor` receives the request, runs the agent, and passes an `AgentExecutorResponse` downstream. The response contains `agent_response.text` (the agent's output as a string).

### Switch-Case Routing

The most powerful feature of `WorkflowBuilder` — deterministic one-of-N routing based on data:

```python
from agent_framework import WorkflowBuilder, Case, Default

def needs_diagnostics(message) -> bool:
    return isinstance(message, RoutingDecision) and message.severity in ("critical", "high")

workflow = (
    WorkflowBuilder(start_executor=ingest_alert)
    .add_edge(ingest_alert, triage_exec)
    .add_edge(triage_exec, parse_triage)
    .add_switch_case_edge_group(parse_triage, [
        Case(condition=needs_diagnostics, target=to_diagnostics),
        Default(target=monitor_only),
    ])
    .add_edge(to_diagnostics, diagnostics_exec)
    .add_edge(diagnostics_exec, comms)
    .build()
)
```

## Your Task

Open `challenge-2/challenge.ipynb`:

1. Define a `RoutingDecision` dataclass for the switch-case
2. Build condition functions: `needs_diagnostics()` (for CRITICAL + HIGH)
3. Wire the full workflow: `ingest → triage → parse → switch → diagnostics/monitor → comms`
4. Run all 3 incidents and verify routing

<div class="warning" data-title="Critical Gotcha">

You **cannot** have two `Case` entries from the same source pointing to the same target. If both CRITICAL and HIGH go to diagnostics, combine them into a single `needs_diagnostics()` condition that checks `severity in ("critical", "high")`.

</div>

<div class="tip" data-title="Success Criteria">

- CRITICAL → diagnostics → comms
- HIGH → diagnostics → comms
- LOW → monitor_only

</div>

---

# Challenge 3: Human-in-the-Loop

## The Problem: Autonomous Agents Are Dangerous

Your workflow from Challenge 2 routes correctly. But it runs **completely autonomously**:

- `restart_pod("payment-api")` executes at 3 AM with no one watching
- A remediation plan with `risk_level: "high"` deploys without review
- If the fix fails, there's no human to intervene

In production, **trust must be explicit**. MAF provides three HITL patterns as first-class features.

## Pattern 1: Tool-Level Approval

Mark individual tools as needing approval. When the LLM tries to call the tool, the workflow **automatically pauses**:

```python
from agent_framework import tool

@tool(approval_mode="always_require")
def restart_pod(service: Annotated[str, "Service to restart"]) -> str:
    """Restart all pods. DESTRUCTIVE — requires approval."""
    return f"✅ Restarted pods for {service}"
```

When the agent calls `restart_pod()`, MAF intercepts:
1. Workflow pauses → state becomes `IDLE_WITH_PENDING_REQUESTS`
2. Caller gets `request_info_events()` showing what the agent wants to do
3. Caller approves or rejects with `to_function_approval_response(approved=True/False)`
4. Workflow resumes (or tool call is blocked)

**When to use:** For individual dangerous operations — restart, delete, scale down.

## Pattern 2: Explicit Pause/Resume

For business decisions (not just tool calls), use `ctx.request_info()` to pause the workflow and ask a human a question:

```python
class ApprovalGate(Executor):
    @handler
    async def handle(self, message: str, ctx: WorkflowContext) -> None:
        ctx.set_state("pending_action", message)
        # This line PAUSES the entire workflow:
        approval = await ctx.request_info(
            f"🚨 APPROVAL REQUIRED:\n{message}\n\nApprove? (yes/no)",
            str,
        )
        await ctx.send_message(approval)

    @response_handler
    async def on_response(self, original_request, response, ctx):
        """MUST be exactly 4 params: self, original_request, response, ctx"""
        await ctx.send_message(response)
```

The caller detects the pause and resumes with:

```python
result = await workflow.run("restart payment-api pod-3")
# result.get_final_state() == WorkflowRunState.IDLE_WITH_PENDING_REQUESTS

events = result.get_request_info_events()
req_id = events[0].request_id

# Human decides... then resume:
result2 = await workflow.run(responses={req_id: "yes"})
```

**When to use:** For plan review, budget approval, escalation decisions.

## Pattern 3: Tool Approval Loop

When an agent calls multiple tools, you need a loop that keeps approving until the agent is done:

```python
events = await workflow.run("Execute the remediation plan")
while events.get_final_state() == WorkflowRunState.IDLE_WITH_PENDING_REQUESTS:
    responses = {}
    for evt in events.get_request_info_events():
        # Auto-approve (in production, show to human and collect decision)
        responses[evt.request_id] = evt.data.to_function_approval_response(approved=True)
    events = await workflow.run(responses=responses)
print(events.get_outputs())
```

## Pattern 4: Functional Workflows

For simpler linear flows, MAF offers `@workflow` and `@step` — plain Python async functions with built-in checkpointing and HITL:

```python
from agent_framework import workflow, step, RunContext

@workflow
async def remediate_with_approval(plan: str, ctx: RunContext) -> str:
    approval = await ctx.request_info(
        f"Plan: {plan}\nApprove?",
        response_type=str,
        request_id="plan_approval",
    )
    if "yes" in approval.lower():
        return f"✅ Executing: {plan}"
    return f"❌ Aborted: {plan}"
```

## Your Task

Open `challenge-3/challenge.ipynb`:

1. Wire `ApprovalGate` → `ExecuteAction` and run with pause/resume
2. Build a tool approval workflow with an agent + approval loop
3. (Stretch) Implement a functional `@workflow` with `ctx.request_info()`

<div class="tip" data-title="Key Insight">

`@response_handler` signature MUST have 4 params: `(self, original_request, response, ctx)`. Missing a param is the #1 error in this challenge.

</div>

<div class="tip" data-title="Success Criteria">

- Workflow pauses with `IDLE_WITH_PENDING_REQUESTS`
- Human response resumes the workflow
- Tool approval loop handles all tool calls

</div>

---

# Challenge 4: Advanced Composition (Bonus)

These are stretch goals for teams that finish early. Each pattern is independent — pick what interests you.

| Option | Difficulty | What You'll Learn | Time |
|--------|-----------|-------------------|------|
| A: Workflow-as-Agent | ⭐⭐ | Hierarchical composition — workflows behave like agents | 10 min |
| B: Sub-Workflow Composition | ⭐⭐⭐ | Nested workflows as reusable graph nodes | 15 min |
| C: OpenTelemetry Tracing | ⭐ | Distributed tracing for every agent/tool call | 10 min |
| D: Parallel Fan-Out | ⭐⭐⭐ | Concurrent investigation of multiple services | 15 min |

## Option A: Workflow-as-Agent

Your entire incident response workflow becomes a **single callable agent**. A supervisor can invoke it alongside other "agents" without knowing it's actually a full graph internally.

```text
┌─────────────────────────────────────────┐
│          Supervisor Agent                 │
│       ┌──────────────┐   ┌───────────┐  │
│       │ Incident     │   │ Capacity  │  │
│       │ Workflow      │   │ Planning  │  │
│       │ (as agent)   │   │ Agent     │  │
│       └──────────────┘   └───────────┘  │
│       ↑ internally: triage → route →    │
│         diagnose → remediate → verify   │
└─────────────────────────────────────────┘
```

This enables **hierarchical multi-agent systems** — a top-level orchestrator delegates to specialized sub-systems.

## Option B: Sub-Workflow Composition

Extract remediation as a reusable sub-workflow. Anywhere in your system that needs "diagnose → remediate → verify" can invoke it as a single node.

## Option C: OpenTelemetry Tracing

Add [OpenTelemetry](https://opentelemetry.io/) to trace every agent call, tool invocation, and workflow step. MAF has [built-in OTel integration](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/observability) — view traces in Azure Monitor or Jaeger.

## Option D: Parallel Fan-Out

When an incident affects multiple services, investigate them concurrently. Use MAF's concurrent execution patterns to fan out investigation across services and fan in the results.

<div class="info" data-title="Reference">

See `challenge-4/README.md` for detailed implementation guidance and code snippets for each option.

</div>

---

# Wrap-up & Resources

## What You Built

A production-grade multi-agent incident response system with:

- ✅ **Typed structured outputs** — Pydantic `response_format` eliminates free text parsing
- ✅ **Workflow graphs** — `WorkflowBuilder` DAG with deterministic execution
- ✅ **Switch-case routing** — conditional paths based on typed data, not LLM interpretation
- ✅ **Human-in-the-loop** — tool approval, explicit pause/resume, functional workflows
- ✅ **Shared state** — `ctx.set_state/get_state` passes context without tight coupling

## Key Takeaway

> **Copilot** = one agent + free text + hope.
>
> **MAF** = typed agents + workflow graphs + conditional routing + human gates + retry logic.

You're not building a chatbot. You're building a **production orchestration system** with the same primitives used for enterprise agent deployments at Microsoft.

## Keep Learning

### Official Documentation

| Resource | Link |
|----------|------|
| MAF GitHub | [github.com/microsoft/agent-framework](https://github.com/microsoft/agent-framework) |
| MAF Overview (MS Learn) | [learn.microsoft.com/agent-framework/overview](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview) |
| MAF User Guide | [learn.microsoft.com/agent-framework/user-guide](https://learn.microsoft.com/agent-framework/user-guide/overview) |
| MAF Quick Start | [learn.microsoft.com/agent-framework/tutorials/quick-start](https://learn.microsoft.com/agent-framework/tutorials/quick-start) |
| MAF Blog | [devblogs.microsoft.com/agent-framework](https://devblogs.microsoft.com/agent-framework/) |

### Samples & Code

| Resource | Link |
|----------|------|
| Python Getting Started | [github.com/.../python/samples/01-get-started](https://github.com/microsoft/agent-framework/tree/main/python/samples/01-get-started) |
| Agent Concepts (tools, middleware, providers) | [github.com/.../python/samples/02-agents](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents) |
| Workflow Samples | [github.com/.../python/samples/03-workflows](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows) |
| Hosting (A2A, Azure Functions, Durable) | [github.com/.../python/samples/04-hosting](https://github.com/microsoft/agent-framework/tree/main/python/samples/04-hosting) |
| End-to-End Applications | [github.com/.../python/samples/05-end-to-end](https://github.com/microsoft/agent-framework/tree/main/python/samples/05-end-to-end) |

### Related Technologies

| Resource | Link |
|----------|------|
| Azure AI Foundry | [ai.azure.com](https://ai.azure.com) |
| Azure AI Foundry Docs | [learn.microsoft.com/azure/ai-foundry](https://learn.microsoft.com/azure/ai-foundry/) |
| Pydantic | [docs.pydantic.dev](https://docs.pydantic.dev) |
| MAF Community Discord | [discord.gg/b5zjErwbQM](https://discord.gg/b5zjErwbQM) |
| This Workshop Repo | [github.com/ishasalania/maf-lab](https://github.com/ishasalania/maf-lab) |

### Video

| Resource | Link |
|----------|------|
| Agent Framework Introduction (30 min) | [youtube.com/watch?v=AAgdMhftj8w](https://www.youtube.com/watch?v=AAgdMhftj8w) |
| DevUI Demo | [youtube.com/watch?v=mOAaGY4WPvc](https://www.youtube.com/watch?v=mOAaGY4WPvc) |

## FAQ

**Q: Do I need ML/AI experience?**
No. You're using a pre-trained model (GPT-4.1) as a reasoning engine. The interesting part is the orchestration — how you wire agents together, route between them, and handle failures.

**Q: How is MAF different from LangChain/CrewAI/AutoGen?**
MAF is the direct successor to Semantic Kernel and AutoGen, created by the same Microsoft teams. Key differences: typed outputs via `response_format` (hard constraint, not prompt engineering), first-class graph-based workflows (not chains), built-in HITL with `request_info` and tool approval, deterministic routing via switch-case on data. Designed for enterprise reliability, not prototyping.

**Q: Will this work after the conference?**
Absolutely. Create an Azure AI Foundry project, deploy GPT-4.1, update `.env`, and run. The repo is self-contained.

**Q: Can I use a different model?**
Yes — change `FOUNDRY_MODEL` in `.env`. Any model that supports structured outputs (GPT-4o, GPT-4.1, etc.) will work.

**Q: Where do I get help?**
[MAF Discord](https://discord.gg/b5zjErwbQM), [GitHub Issues](https://github.com/microsoft/agent-framework/issues), or [weekly office hours](https://github.com/microsoft/agent-framework/blob/main/COMMUNITY.md#public-community-office-hours).

## Presenters

| Name | Role |
|------|------|
| **Isha Salania** | Cloud Solution Architect, Microsoft |
| **Kiran Panchal** | Cloud Solution Architect, Microsoft |
| **Ricardo Niepel** | Cloud Solution Architect, Microsoft |
