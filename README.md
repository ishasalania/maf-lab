# Building Multi-Agent AI Systems with MAF

> **From Copilot to Orchestrated Agents** — Build a production-grade multi-agent incident response system using Microsoft Agent Framework and Azure AI Foundry.

**WeAreDevelopers World Congress 2026** — Berlin, Friday 10 July | 12:15–14:15 | Room Ulm

*Isha Salania · Kiran Panchal · Ricardo Niepel*

---

## What Is This Workshop?

You've used Copilot. You've seen demos where an LLM calls a tool. But how do you go from *one agent answering questions* to a **fleet of agents collaborating in a production system** — with typed contracts, conditional routing, human oversight, and retry logic?

That's what this workshop teaches.

Over 2 hours, you'll build a **multi-agent incident response system** that automatically detects, triages, diagnoses, and remediates production outages. It uses the same framework and patterns Microsoft uses internally for enterprise-grade agent deployments.

### Who Is This For?

| Experience Level | What You'll Get |
|---|---|
| **Beginner** (Python + API experience) | Learn how agents actually work under the hood — beyond "prompt → response" |
| **Intermediate** (built chatbots or RAG) | Level up from single-agent to orchestrated multi-agent workflows |
| **Advanced** (production AI systems) | Discover MAF's graph engine, HITL patterns, and composition primitives |

> **No prior AI/ML experience required.** If you can write Python functions and call REST APIs, you can do this workshop.

---

## The Big Picture: Why Multi-Agent?

A single agent (like Copilot) handles one task at a time. Multi-agent systems split complex problems across **specialized agents** that each do one thing well:

```
Single Agent (Copilot):          Multi-Agent (MAF):
┌──────────────┐                 ┌────────┐    ┌──────────┐    ┌─────────┐
│  One LLM     │                 │ Triage │───→│ Diagnose │───→│ Approve │
│  does        │                 │ Agent  │    │ Agent    │    │ (Human) │
│  everything  │                 └────────┘    └──────────┘    └────┬────┘
└──────────────┘                                                    │
                                                              ┌─────▼─────┐
                                                              │  Execute  │
                                                              │  Agent    │
                                                              └─────┬─────┘
                                                              ┌─────▼─────┐
                                                              │  Verify   │
                                                              │  Agent    │
                                                              └───────────┘
```

**Why?** Because in production:
- You need **typed contracts** between agents (not free text parsing)
- Different situations need **different execution paths** (not one-size-fits-all)
- Dangerous actions need **human approval** before executing
- Failures need **automatic retry** with escalation

This workshop teaches all four.

---

## What You'll Build: The Scenario

It's 3 AM. A production alert fires: **"Payment API P99 latency > 30 seconds."**

Your multi-agent system handles it end-to-end:

```
                         ┌─ [CRITICAL] ─→ Diagnostics ─→ Remediation (HITL) ─→ Verify ─→ Comms
                         │
  Alert ─→ Triage ─→ Switch ─ [HIGH] ────→ Diagnostics ─→ Remediation ─→ Comms
                         │
                         └─ [LOW] ─────→ Monitor Only
```

Each step is an **agent** or **workflow executor**. The routing is **deterministic** — based on typed data, not LLM interpretation. The approval is **explicit** — the workflow literally pauses until a human responds.

### The Three Incidents

You'll process all three during the workshop — each one triggers a different path:

| # | What Happened | Severity | Workflow Path | What the Agent Does |
|---|---|---|---|---|
| 1 | Payment API P99 > 30s, pods OOMKilled | **CRITICAL** | Full pipeline + HITL approval | Restarts OOMKilled pod (after human approves) |
| 2 | Order Service cascading errors, 23% error rate | **HIGH** | Diagnostics → Remediation → Comms | Scales replicas from 3→5 |
| 3 | Notification emails failing, rate limited | **LOW** | Monitor only | Logs it, takes no action |

Same system, same code, different outcomes — because the **Triage Agent returns structured data** that the workflow uses for deterministic routing.

---

## What Makes This Workshop Different

This is NOT a "call an LLM and regex-parse the output" tutorial. You'll use production features from Microsoft Agent Framework:

| Problem | Naive Approach | MAF Solution | Challenge |
|---|---|---|---|
| Agent outputs are unreliable | Parse free text with regex | **Pydantic `response_format`** — LLM is forced to return valid typed JSON | 1 |
| Chaining agents is ad-hoc | If/else spaghetti | **WorkflowBuilder** — declare a DAG, let the engine execute it | 2 |
| Different inputs need different paths | Big switch statement | **`add_switch_case_edge_group()`** — one-of-N routing in the graph | 2 |
| Dangerous actions go unreviewed | YOLO | **`@tool(approval_mode="always_require")`** — workflow pauses for human | 3 |
| Operations fail sometimes | Crash and log | **Retry loops with `@step`** — checkpoint results, retry on failure | 3 |

### The MAF Stack

```
┌───────────────────────────────────────────────┐
│               Your Application                 │
├───────────────────────────────────────────────┤
│  WorkflowBuilder  │  Agent  │  @executor      │  ← MAF orchestration
├───────────────────────────────────────────────┤
│  FoundryChatClient  │  @tool  │  Pydantic     │  ← MAF primitives
├───────────────────────────────────────────────┤
│  Azure AI Foundry  │  GPT-4o  │  Azure CLI    │  ← Infrastructure
└───────────────────────────────────────────────┘
```

- **`Agent`** — wraps an LLM with instructions, tools, and output format
- **`FoundryChatClient`** — connects to Azure AI Foundry (lightweight, no server resources)
- **`WorkflowBuilder`** — declares a directed graph of executors with edges and conditions
- **`@executor`** — a node in the graph that receives messages and emits output
- **`@tool`** — a Python function the LLM can call (with optional human approval)
- **`ctx`** — the workflow context: state, messaging, output, human interaction

---

## Learning Objectives

By the end of this workshop, you will be able to:

1. **Build** agents that return typed structured outputs (not free text) using Pydantic schemas
2. **Design** workflow graphs with conditional edges and switch-case routing for deterministic execution paths
3. **Implement** human-in-the-loop patterns — both tool-level approval and explicit workflow pause/resume
4. **Use** shared state management to pass context across workflow executors without tight coupling
5. **Apply** retry and escalation patterns so your system degrades gracefully instead of crashing

---

## Prerequisites

| Requirement | Details | Check |
|---|---|---|
| **Azure subscription** | With permissions to create AI Foundry resources | `az account show` works |
| **Python** | 3.10 or higher (3.11 in Codespaces) | `python --version` |
| **Azure CLI** | Installed and authenticated | `az login` done |
| **GitHub account** | For Codespaces (recommended) or cloning | Can fork this repo |

### What You DON'T Need

- ❌ ML/AI experience
- ❌ LangChain/LlamaIndex knowledge
- ❌ Understanding of transformers or embeddings
- ❌ A GPU or powerful machine

If you've written Python functions, used pip, and called REST APIs — you're ready.

---

## Workshop Flow (2 Hours)

```
12:15 ─── Introduction & Setup ──────────────────── 15 min
           │  What is MAF? Quick demo. Fork repo.
           │  Deploy resources or get credentials.
           ▼
12:30 ─── Challenge 1: Structured Agents ────────── 30 min
           │  Build 4 agents with Pydantic outputs.
           │  Each returns typed data (not free text).
           ▼
13:00 ─── Challenge 2: Workflow Graphs ──────────── 30 min
           │  Wire agents into a DAG with WorkflowBuilder.
           │  Switch-case routing based on severity.
           ▼
13:30 ─── Break ─────────────────────────────────── 5 min
           ▼
13:35 ─── Challenge 3: Human-in-the-Loop ────────── 25 min
           │  Add approval gates. Workflow pauses.
           │  Human approves. Workflow resumes.
           │  Add retry logic for failures.
           ▼
14:00 ─── Challenge 4: Advanced (Bonus) ─────────── 15 min
           │  Workflow-as-agent. Sub-workflows.
           │  Parallelism. OpenTelemetry.
           ▼
14:15 ─── Wrap-up & Q&A
```

---

## Challenges

| # | Challenge | Duration | What You'll Do | Key Concept |
|---|---|---|---|---|
| [0](challenge-0/README.md) | **Environment Setup** | 15 min | Deploy Azure resources, verify connection | Get running |
| [1](challenge-1/README.md) | **Structured Agents** | 30 min | Build 4 agents that return Pydantic models | `response_format` eliminates parsing |
| [2](challenge-2/README.md) | **Workflow Graphs** | 30 min | Wire agents into a graph with switch-case routing | `WorkflowBuilder` + conditional edges |
| [3](challenge-3/README.md) | **Human-in-the-Loop** | 25 min | Add approval gates, pause/resume, retry loops | Safe production deployment |
| [4](challenge-4/README.md) | **Advanced Composition** | 20+ min | Workflow-as-agent, sub-workflows, parallelism | Composition at scale |

Each challenge builds on the previous one. Challenges 1–3 are the core workshop. Challenge 4 is for teams that finish early.

---

## Repository Structure

```
maf-lab/
├── challenge-0/               # Setup & verification
│   ├── README.md              # Step-by-step environment setup guide
│   ├── verify-setup.ipynb     # Run this — all checks should show ✅
│   └── scripts/               # Optional: deploy Azure resources yourself
├── challenge-1/               # Structured agents with Pydantic outputs
│   ├── README.md              # Concept guide: what are structured outputs?
│   └── challenge.ipynb        # Build Triage, Diagnostics, Remediation, Verification agents
├── challenge-2/               # Workflow graphs with conditional routing
│   ├── README.md              # Concept guide: workflow graphs & switch-case
│   └── challenge.ipynb        # Wire agents into WorkflowBuilder with routing
├── challenge-3/               # Human-in-the-loop & resilience
│   ├── README.md              # Concept guide: approval, pause/resume, retry
│   └── challenge.ipynb        # Add HITL gates, functional workflows, retry loops
├── challenge-4/               # Bonus: advanced composition patterns
│   └── README.md              # 4 options: workflow-as-agent, sub-workflows, OTel, fan-out
├── tools/
│   └── mock_infra.py          # All @tool functions (metrics, logs, restart, scale, etc.)
├── data/
│   └── incidents.json         # 3 sample incidents (CRITICAL, HIGH, LOW)
├── solution/
│   └── full_workflow.py       # Complete reference implementation (don't peek early!)
├── .devcontainer/             # Codespaces config (Python 3.11, all deps pre-installed)
├── requirements.txt           # agent-framework, azure-identity, pydantic, dotenv
└── .env.example               # Template for your Azure credentials
```

---

## Quick Start (2 Minutes)

### Option A: Codespaces (Recommended — Zero Setup)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ishasalania/maf-lab?quickstart=1)

Everything is pre-installed. Just add your `.env` credentials and go.

### Option B: Local

```bash
git clone https://github.com/ishasalania/maf-lab.git
cd maf-lab
python -m venv .venv && .venv\Scripts\activate  # Windows
# source .venv/bin/activate                     # macOS/Linux
pip install -r requirements.txt
cp .env.example .env                            # Fill in your values
```

Then follow [Challenge 0](challenge-0/README.md) to verify everything works.

---

## Key Concepts Cheat Sheet

Use this as a quick reference during the workshop:

### Agents & Clients

```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from agent_framework.openai import OpenAIChatOptions

# Create a client (connects to Azure AI Foundry)
client = FoundryChatClient(
    project_endpoint=os.environ["FOUNDRY_PROJECT_ENDPOINT"],
    model=os.environ["FOUNDRY_MODEL"],
    credential=AzureCliCredential(),
)

# Create an agent with structured output
agent = Agent(
    client=client,
    name="MyAgent",
    instructions="Your system prompt here.",
    default_options=OpenAIChatOptions[Any](response_format=MyPydanticModel),
    tools=[my_tool],
)

# Run the agent
response = await agent.run("Your input message")
result = MyPydanticModel.model_validate_json(response.text)
```

### Tools

```python
from agent_framework import tool
from typing import Annotated

@tool(approval_mode="never_require")  # or "always_require" for dangerous ops
def get_metrics(
    service_name: Annotated[str, "Name of the service to query"],
    time_range: Annotated[str, "Time range (e.g., '15m', '1h')"] = "15m",
) -> str:
    """Retrieve service performance metrics."""
    return f"CPU: 85%, Memory: 92%, P99: 30200ms for {service_name}"
```

### Workflow Graphs

```python
from agent_framework import WorkflowBuilder, executor

@executor(id="my_node")
async def my_executor(ctx, request):
    ctx.set_state("key", value)         # Store data for downstream nodes
    ctx.send_message(downstream_msg)    # Send to next node
    ctx.yield_output(final_result)      # Emit workflow result

# Build the graph
workflow = (
    WorkflowBuilder(start_executor=first_node)
    .add_edge(first_node, second_node)
    .add_switch_case_edge_group(
        source=router_node,
        cases=[Case("critical", target=critical_handler, condition=is_critical)],
        default=Default(target=default_handler),
    )
    .build()
)
```

### Human-in-the-Loop

```python
# Tool-level: mark dangerous tools
@tool(approval_mode="always_require")
def restart_pod(service: Annotated[str, "Service to restart"]) -> str: ...

# Workflow-level: explicit pause/resume
info = await ctx.request_info("Should we proceed with this plan?")
# Workflow pauses here — human responds — workflow resumes
```

---

## Key Technologies

| Technology | Version | Role in This Workshop |
|---|---|---|
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | ≥ 1.0.0 | Agent runtime, workflow graphs, tools, HITL, state management |
| [Azure AI Foundry](https://ai.azure.com) | — | Hosts GPT-4o model, provides project endpoint |
| [Pydantic](https://docs.pydantic.dev) | ≥ 2.0 | Defines typed output schemas that LLMs are forced to follow |
| [Azure Identity](https://learn.microsoft.com/python/api/azure-identity/) | ≥ 1.17 | Passwordless auth to Azure via CLI credentials |
| Python | ≥ 3.10 | Runtime (3.11 in Codespaces) |

---

## Key Takeaway

> **Copilot** = one agent + free text + hope.
>
> **MAF** = typed agents + workflow graphs + conditional routing + human gates + retry logic.

You're not building a chatbot. You're building a **production orchestration system** with the same primitives used for real enterprise agent deployments at Microsoft.

---

## FAQ

**Q: Do I need to understand machine learning?**
A: No. You're using a pre-trained model (GPT-4o) as a reasoning engine. The interesting part is the orchestration — how you wire agents together, route between them, and handle failures.

**Q: Can I use my own Azure subscription?**
A: Yes! Follow the deployment script in Challenge 0. Or your coach will provide shared credentials.

**Q: What if I get stuck?**
A: Each challenge has a reference solution in `solution/full_workflow.py`. Ask your coach before peeking!

**Q: Will this work after the conference?**
A: Absolutely. The repo is self-contained. Just create an Azure AI Foundry project and update `.env`.

**Q: How is MAF different from LangChain/CrewAI/AutoGen?**
A: MAF is Microsoft's production agent framework — typed outputs via `response_format`, first-class workflow graphs (not chains), built-in HITL, deterministic routing. It's designed for enterprise reliability, not prototyping.

---

## Presenters

| | Name | Role |
|---|---|---|
| 👩‍💻 | **Isha Salania** | Cloud Solution Architect, Microsoft |
| 👨‍💻 | **Kiran Panchal** | Cloud Solution Architect, Microsoft |
| 👨‍💻 | **Ricardo Niepel** | Cloud Solution Architect, Microsoft |

---

## Contributing

This workshop was created for WeAreDevelopers World Congress 2026. Issues and PRs welcome.

## License

MIT
