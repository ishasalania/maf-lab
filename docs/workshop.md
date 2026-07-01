---
published: true
type: workshop
title: Building Multi-Agent AI Systems with Microsoft Agent Framework
short_title: Multi-Agent with MAF
description: Build a production-grade multi-agent incident response system using Microsoft Agent Framework and Azure AI Foundry. Learn typed outputs, workflow graphs, conditional routing, and human-in-the-loop patterns.
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
  - Environment Setup
  - "Challenge 1: Structured Agents"
  - "Challenge 2: Workflow Graphs"
  - "Challenge 3: Human-in-the-Loop"
  - "Challenge 4: Advanced (Bonus)"
  - Wrap-up
---

# Building Multi-Agent AI Systems with MAF

> **From Copilot to Orchestrated Agents** — Build a production-grade multi-agent incident response system using Microsoft Agent Framework and Azure AI Foundry.

**WeAreDevelopers World Congress 2026** — Berlin, Friday 10 July · 12:15–14:15 · Room Ulm

## What You'll Build

It's 3 AM. A production alert fires: **"Payment API P99 latency > 30 seconds."**

Your multi-agent system handles it end-to-end:

```text
                         ┌─ [CRITICAL] ─→ Diagnostics ─→ Remediation (HITL) ─→ Verify ─→ Comms
                         │
  Alert ─→ Triage ─→ Switch ─ [HIGH] ────→ Diagnostics ─→ Remediation ─→ Comms
                         │
                         └─ [LOW] ─────→ Monitor Only
```

Each step is an **agent** or **workflow executor** in a typed graph. Routing is deterministic. Approvals are explicit.

## The MAF Stack

```text
┌───────────────────────────────────────────────┐
│               Your Application                 │
├───────────────────────────────────────────────┤
│  WorkflowBuilder  │  Agent  │  @executor      │  ← MAF orchestration
├───────────────────────────────────────────────┤
│  FoundryChatClient  │  @tool  │  Pydantic     │  ← MAF primitives
├───────────────────────────────────────────────┤
│  Azure AI Foundry  │  GPT-4.1  │  Azure CLI   │  ← Infrastructure
└───────────────────────────────────────────────┘
```

## Prerequisites

| Requirement | Details |
|---|---|
| Azure subscription | With permissions to create AI Foundry resources |
| Python | 3.10+ (3.11 in Codespaces) |
| Azure CLI | Installed and authenticated (`az login`) |
| GitHub account | For Codespaces or cloning |

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

# Challenge 0: Environment Setup

## Azure Resources Required

Your lab environment needs the following Azure resources pre-provisioned:

| Resource | Type | SKU | Purpose |
|----------|------|-----|---------|
| Resource Group | `Microsoft.Resources/resourceGroups` | — | Container for all resources |
| AI Foundry Account | `Microsoft.CognitiveServices/accounts` (kind: AIServices) | S0 | Hosts models + project management |
| Foundry Project | `Microsoft.CognitiveServices/accounts/projects` | — | Provides your project endpoint |
| GPT-4.1 Deployment | `Microsoft.CognitiveServices/deployments` | GlobalStandard, capacity 30 | The LLM all agents call |

### RBAC Roles (per attendee)

| Role | Scope | Why |
|------|-------|-----|
| `Cognitive Services OpenAI User` | AI Foundry account | Call the model (inference) |
| `Cognitive Services Contributor` | AI Foundry account | Create and manage agents |

### For Container Deployment (Bonus / Demo)

| Resource | Type | Purpose |
|----------|------|---------|
| Container Registry | `Microsoft.ContainerRegistry/registries` (Basic) | Store the Docker image |
| Container Apps Environment | `Microsoft.App/managedEnvironments` | Serverless hosting |
| Container App | `Microsoft.App/containerApps` | Runs the FastAPI API |
| Managed Identity | System-assigned on Container App | Passwordless auth to Foundry |

<div class="info" data-title="For coaches / tech team">

All infrastructure is codified in `infrastructure/` (Terraform). Run `terraform apply` to deploy everything including attendee RBAC. See `infrastructure/README.md` for details.

</div>

## Goal

Get three things working:
1. Python environment with MAF installed
2. Azure CLI authenticated
3. A `.env` file with your project endpoint and model

## Quick Start

### Option A: Codespaces (Recommended)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ishasalania/maf-lab?quickstart=1)

Everything is pre-installed. Just add your `.env` and go.

### Option B: Local Setup

```bash
git clone https://github.com/ishasalania/maf-lab.git
cd maf-lab
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Fill in your values
```

## Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Fill in:

```text
FOUNDRY_PROJECT_ENDPOINT=https://<your-project>.services.ai.azure.com/api/projects/<project-id>
FOUNDRY_MODEL=gpt-4.1
```

## Authenticate

```bash
az login
az account set --subscription "<your-subscription-id>"
```

## Verify Setup

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

## The Problem

Typical agent output:

```text
The severity appears to be critical. The service seems to be experiencing
memory issues. I'd recommend restarting the pod, but we should also check...
```

How do you use this downstream? Regex? Prayer?

## The Fix: Pydantic `response_format`

Force the LLM to return a **typed JSON object**:

```python
TriageResult(
    severity="critical",               # Literal["critical", "high", "low"]
    incident_type="resource_exhaustion",
    recurrence_count=3,
    recommended_runbook="kb://oom-restart-procedure"
)
```

When Agent A returns typed data, Agent B (or a workflow router) can make **deterministic decisions** based on exact field values.

## Key Concepts

| Concept | What It Is |
|---------|------------|
| `Agent` | MAF's core class — wraps LLM + instructions + tools + output format |
| `FoundryChatClient` | Connection to Azure AI Foundry |
| `response_format` | Pydantic model as output schema — LLM is forced to match it |
| `@tool` | Gives agents abilities (query metrics, check logs) |
| `Literal[...]` | Limits LLM to exact allowed values |

## How It Works

```text
1. You define a Pydantic model (TriageResult)
2. MAF converts it to JSON Schema
3. The schema is sent to GPT-4.1 as response_format
4. GPT-4.1 is constrained to ONLY output valid JSON
5. MAF validates the JSON against your Pydantic model
6. You get a typed Python object — not a string
```

This is NOT prompt engineering — it's a **hard constraint** at model inference level.

## Your Task

Open `challenge-1/challenge.ipynb` and build four agents:

| Agent | Output Model | Purpose |
|-------|-------------|---------|
| **Triage** | `TriageResult` (provided) | Classify severity and incident type |
| **Diagnostics** | `DiagnosticsResult` (build it) | Identify root cause and affected components |
| **Remediation** | `RemediationPlan` (build it) | Generate action plan with risk level |
| **Verification** | `VerificationResult` (build it) | Confirm fix worked |

### Hints

- Each Pydantic model defines what fields the agent MUST return
- Use `Literal["value1", "value2"]` to constrain enums
- Use `Field(description="...")` so the LLM knows what each field means
- Give agents tools from `tools/mock_infra.py` so they can gather data

<div class="tip" data-title="Success Criteria">

Each agent returns a validated Pydantic object — no regex, no parsing, just typed data.

</div>

---

# Challenge 2: Workflow Graphs

## The Problem

Manual agent chaining doesn't scale:

```python
triage_result = await triage_agent.run(alert)
diagnostics_result = await diagnostics_agent.run(triage_result.text)
plan = await planner_agent.run(diagnostics_result.text)
```

Add 5 paths, 3 agents, error handling, state passing — unmaintainable spaghetti.

## The Fix: WorkflowBuilder

Declare your agent topology as a **directed acyclic graph (DAG)**:

```text
                                    ┌───────────┐
                                    │  SWITCH   │
                                    ├───────────┤
 ingest ─→ triage_agent ─→ parse ──│ critical  │──→ diagnostics ──→ comms
                                    │ high      │──→ diagnostics ──→ comms
                                    │ low       │──→ monitor_only
                                    └───────────┘
```

## Key Concepts

| Concept | Purpose |
|---------|---------|
| `WorkflowBuilder` | Declare topology, not control flow |
| `@executor` | A node that receives messages and emits output |
| `AgentExecutor` | Wraps an Agent as a workflow node |
| `add_edge()` | Connect two nodes sequentially |
| `add_switch_case_edge_group()` | One-of-N routing based on data |
| `ctx.set_state()` / `ctx.get_state()` | Share data between executors |
| `ctx.send_message()` | Feed input to the next executor |
| `ctx.yield_output()` | Emit final workflow result |

## The Two Executor Patterns

### Function-based (simple nodes)

```python
@executor(id="ingest_alert")
async def ingest_alert(alert_json: str, ctx: WorkflowContext) -> None:
    alert = json.loads(alert_json)
    ctx.set_state("incident_id", alert["incident_id"])
    await ctx.send_message(f"Triage this: {alert['title']}")
```

### Class-based (for type-aware handlers)

```python
class ParseTriage(Executor):
    @handler
    async def handle(self, message: AgentExecutorResponse, ctx: WorkflowContext) -> None:
        result = json.loads(message.agent_response.text)
        ctx.set_state("severity", result["severity"])
        await ctx.send_message(RoutingDecision(severity=result["severity"]))
```

## Your Task

Open `challenge-2/challenge.ipynb`:

1. Define a `RoutingDecision` dataclass for switch-case routing
2. Build condition functions: `needs_diagnostics()`, `is_low()`
3. Wire the full workflow with `WorkflowBuilder`
4. Run all 3 incidents and verify routing

<div class="warning" data-title="Common Gotcha">

You cannot have two `Case` entries from the same source pointing to the same target. Combine CRITICAL + HIGH into a single `needs_diagnostics()` condition.

</div>

<div class="tip" data-title="Success Criteria">

- CRITICAL → diagnostics → comms
- HIGH → diagnostics → comms
- LOW → monitor_only

</div>

---

# Challenge 3: Human-in-the-Loop

## The Problem

Your workflow runs **completely autonomously**:
- `restart_pod("payment-api")` executes at 3 AM unreviewed
- A high-risk remediation plan deploys without approval
- If verification fails, the system just stops

## The Fix: MAF HITL Patterns

| Pattern | API | When to Use |
|---------|-----|-------------|
| Tool approval | `@tool(approval_mode="always_require")` | Dangerous operations |
| Explicit pause | `ctx.request_info(data, type)` | Business decisions |
| Resume | `workflow.run(responses={request_id: answer})` | Continue after human decision |
| Functional HITL | `@workflow` + `ctx.request_info()` | Simple linear flows |

## Pattern 1: Tool Approval

```python
@tool(approval_mode="always_require")
def restart_pod(service: Annotated[str, "Service to restart"]) -> str:
    """Restart pods. DESTRUCTIVE — requires approval."""
    return f"✅ Restarted pods for {service}"
```

When the agent calls this tool, MAF intercepts → workflow pauses → human approves or rejects → workflow resumes.

## Pattern 2: Explicit Pause/Resume

```python
class ApprovalGate(Executor):
    @handler
    async def handle(self, message: str, ctx: WorkflowContext) -> None:
        approval = await ctx.request_info(
            f"🚨 APPROVAL REQUIRED:\n{message}\n\nApprove? (yes/no)",
            str,
        )
        await ctx.send_message(approval)

    @response_handler
    async def on_response(self, original_request, response, ctx):
        """4 params required: self, original_request, response, ctx"""
        await ctx.send_message(response)
```

## Pattern 3: Tool Approval Loop

```python
events = await workflow.run("restart payment-api pod-3")
while events.get_final_state() == WorkflowRunState.IDLE_WITH_PENDING_REQUESTS:
    responses = {}
    for evt in events.get_request_info_events():
        responses[evt.request_id] = evt.data.to_function_approval_response(approved=True)
    events = await workflow.run(responses=responses)
```

## Your Task

Open `challenge-3/challenge.ipynb`:

1. Wire the `ApprovalGate` → `ExecuteAction` workflow and run it with pause/resume
2. Build a tool approval workflow with an agent + approval loop
3. (Stretch) Implement a functional `@workflow` with `ctx.request_info()`

<div class="tip" data-title="Key Insight">

`@response_handler` signature MUST be 4 params: `(self, original_request, response, ctx)`. This is the most common error.

</div>

<div class="tip" data-title="Success Criteria">

- Workflow pauses with `IDLE_WITH_PENDING_REQUESTS`
- Human response resumes the workflow
- Tool approval loop auto-approves all tool calls

</div>

---

# Challenge 4: Advanced Composition (Bonus)

## Choose Your Adventure

Pick one or more patterns — each is independent:

| Option | Difficulty | What You'll Learn | Time |
|--------|-----------|-------------------|------|
| A: Workflow-as-Agent | ⭐⭐ | Hierarchical composition | 10 min |
| B: Sub-Workflow Composition | ⭐⭐⭐ | Nested reusable workflows | 15 min |
| C: OpenTelemetry | ⭐ | Distributed tracing | 10 min |
| D: Parallel Fan-Out | ⭐⭐⭐ | Concurrent investigation | 15 min |

## Option A: Workflow-as-Agent

Your entire incident response workflow becomes a **single callable agent**. A supervisor can invoke it without knowing it's a full graph internally.

```text
┌─────────────────────────────────────────┐
│          Supervisor Agent                 │
│       ┌──────────────┐   ┌───────────┐  │
│       │ Incident     │   │ Capacity  │  │
│       │ Workflow      │   │ Planning  │  │
│       │ (as agent)   │   │ Agent     │  │
│       └──────────────┘   └───────────┘  │
└─────────────────────────────────────────┘
```

## Option B: Sub-Workflow Composition

Extract remediation as a reusable sub-workflow. The main workflow invokes it as a node.

## Option C: OpenTelemetry Tracing

Add `opentelemetry` to trace every agent call, tool invocation, and workflow step. View traces in Azure Monitor.

## Option D: Parallel Fan-Out

When an incident affects multiple services, investigate them concurrently using fan-out/fan-in patterns.

<div class="info" data-title="Reference">

See `challenge-4/README.md` for detailed instructions and code snippets for each option.

</div>

---

# Wrap-up

## What You Built

A production-grade multi-agent incident response system with:

- ✅ **Typed structured outputs** — no regex parsing, Pydantic-validated JSON
- ✅ **Workflow graphs** — DAG-based topology with conditional routing
- ✅ **Switch-case routing** — deterministic paths based on data, not LLM interpretation
- ✅ **Human-in-the-loop** — tool approval, explicit pause/resume, functional workflows
- ✅ **Shared state** — context passed across executors without coupling

## Key Takeaway

> **Copilot** = one agent + free text + hope.
>
> **MAF** = typed agents + workflow graphs + conditional routing + human gates + retry logic.

You're not building a chatbot. You're building a **production orchestration system** with the same primitives used for real enterprise agent deployments at Microsoft.

## Keep Learning

| Resource | Link |
|----------|------|
| MAF GitHub | [github.com/microsoft/agent-framework](https://github.com/microsoft/agent-framework) |
| Azure AI Foundry | [ai.azure.com](https://ai.azure.com) |
| This Workshop | [github.com/ishasalania/maf-lab](https://github.com/ishasalania/maf-lab) |

## FAQ

**Q: Do I need ML experience?**
No. You're using a pre-trained model as a reasoning engine. The interesting part is the orchestration.

**Q: How is MAF different from LangChain/CrewAI/AutoGen?**
MAF is Microsoft's production framework — typed outputs, first-class workflow graphs, built-in HITL, deterministic routing. Designed for enterprise reliability, not prototyping.

**Q: Will this work after the conference?**
Yes. Create an Azure AI Foundry project, update `.env`, and run.

## Presenters

| Name | Role |
|------|------|
| **Isha Salania** | Cloud Solution Architect, Microsoft |
| **Kiran Panchal** | Cloud Solution Architect, Microsoft |
| **Ricardo Niepel** | Cloud Solution Architect, Microsoft |
