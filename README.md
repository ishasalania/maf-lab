# Building Multi-Agent AI Systems with MAF

> **From Copilot to Orchestrated Agents** — Build a production-grade multi-agent incident response system using Microsoft Agent Framework and Azure AI Foundry.

**WeAreDevelopers World Congress 2026** — Berlin, Friday 10 July | 12:15–14:15 | Room Ulm

*Isha Salania · Kiran Panchal · Ricardo Niepel*

---

## Overview

In this hands-on workshop, you'll build a **production-grade multi-agent incident response system** using Microsoft Agent Framework's graph-based workflow engine.

You'll progressively learn MAF's core architecture: **structured agents** with Pydantic outputs, **workflow graphs** with conditional routing, and **human-in-the-loop** patterns for safe production deployment — culminating in a system that triages, diagnoses, fixes, and verifies production incidents autonomously.

```
                         ┌─ [CRITICAL] ─→ Diagnostics ─→ Remediation (HITL) ─→ Verify ─→ Comms
                         │
  Alert ─→ Triage ─→ Switch ─ [HIGH] ────→ Diagnostics ─→ Remediation ─→ Comms
                         │
                         └─ [LOW] ─────→ Monitor Only
```

**Structured outputs · Switch-case routing · Tool approval gates · Retry loops**

---

## What Makes This Workshop Different

This is NOT a "call an LLM and parse the text" tutorial. You'll use MAF's actual production features:

| MAF Feature | What You'll Build |
|---|---|
| `FoundryChatClient` + `Agent` | Lightweight local agents (no server-side resource creation) |
| Pydantic `response_format` | Agents return typed, validated data — not free text |
| `WorkflowBuilder` + `add_edge()` | DAG-based workflow graphs with explicit execution order |
| `add_switch_case_edge_group()` | Deterministic one-of-N routing based on structured output fields |
| `ctx.set_state()` / `ctx.get_state()` | Shared state management across workflow executors |
| `@tool(approval_mode="always_require")` | Dangerous tools pause for human approval |
| `ctx.request_info()` | Explicit workflow pause/resume for human decisions |
| Functional workflows with `@step` | Retry loops, checkpointing, native Python control flow |

---

## Learning Objectives

By the end of this workshop, you will be able to:

1. **Build** agents with typed structured outputs using Pydantic `response_format`
2. **Design** workflow graphs with conditional edges and switch-case routing
3. **Implement** human-in-the-loop patterns for safe production deployment
4. **Use** MAF's state management to share context across workflow executors
5. **Apply** retry and escalation patterns for resilient agent systems

---

## Prerequisites

| Requirement | Details |
|---|---|
| **Azure subscription** | With permissions to create AI Foundry resources |
| **Python** | 3.10 or higher |
| **Azure CLI** | Installed and `az login` working |
| **GitHub account** | For Codespaces (recommended) or forking the repo |

> **No prior AI/ML experience required.** If you've written Python functions and used APIs, you're ready.

---

## Challenges

| Challenge | Title | Duration | Key MAF Concepts |
|---|---|---|---|
| [Challenge 0](challenge-0/README.md) | Environment Setup | 15 min | Deploy Azure resources, verify connection |
| [Challenge 1](challenge-1/README.md) | Structured Agents | 30 min | `Agent`, `FoundryChatClient`, `response_format`, `@tool` |
| [Challenge 2](challenge-2/README.md) | Workflow Graphs | 30 min | `WorkflowBuilder`, `@executor`, switch-case routing, state |
| [Challenge 3](challenge-3/README.md) | Human-in-the-Loop | 25 min | `ctx.request_info()`, tool approval, retry patterns |
| [Challenge 4](challenge-4/README.md) | Advanced Composition | 20+ min | Workflow-as-agent, sub-workflows, parallelism, observability |

---

## Repository Structure

```
maf-lab/
├── challenge-0/               # Setup & verification
│   ├── README.md
│   ├── verify-setup.ipynb
│   └── scripts/
├── challenge-1/               # Structured agents with Pydantic outputs
│   ├── README.md
│   └── challenge.ipynb        # Build 4 agents with typed response_format
├── challenge-2/               # Workflow graphs with conditional routing
│   ├── README.md
│   └── challenge.ipynb        # WorkflowBuilder, switch-case, state mgmt
├── challenge-3/               # Human-in-the-loop & resilience
│   ├── README.md
│   └── challenge.ipynb        # Tool approval, request_info, retry loops
├── challenge-4/               # Bonus: advanced composition
│   └── README.md              # Workflow-as-agent, sub-workflows, OTel
├── tools/
│   └── mock_infra.py          # @tool decorated infrastructure functions
├── data/
│   └── incidents.json         # 3 incidents (critical/high/low severity)
├── solution/
│   └── full_workflow.py       # Complete reference implementation
├── .devcontainer/             # Codespaces configuration
├── requirements.txt
└── .env.example
```

---

## The Scenario

It's 3 AM. A production alert fires. Your multi-agent workflow:

1. **Triages** (structured output) → classifies severity, checks history, finds runbook
2. **Routes** (switch-case) → CRITICAL gets full pipeline, LOW gets monitor-only
3. **Diagnoses** (tools + structured output) → queries metrics, logs, dependencies
4. **Plans** (structured output) → produces typed `RemediationPlan`
5. **Approves** (HITL) → workflow PAUSES, human reviews, workflow RESUMES
6. **Executes** (tool approval) → `restart_pod()` requires explicit approval
7. **Verifies** (retry loop) → health check + smoke tests, retry up to 3x

### Sample Incidents

| # | Alert | Severity | Route | Agent Decision |
|---|-------|----------|-------|----------------|
| 1 | Payment API P99 > 30s | CRITICAL | Full pipeline + HITL | Restart OOMKilled pod |
| 2 | Order Service Error Rate 23% | HIGH | Diagnostics + remediation | Scale replicas |
| 3 | Notification Email Failing | LOW | Monitor only | No action needed |

Different incidents trigger **different workflow paths** — demonstrating that routing is deterministic based on structured data.

---

## Quick Start

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ishasalania/maf-lab?quickstart=1)

Or manually:

```bash
git clone https://github.com/ishasalania/maf-lab.git
cd maf-lab
python -m venv .venv && .venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

Then follow [Challenge 0](challenge-0/README.md) to deploy Azure resources.

---

## Key Technologies

| Technology | Role |
|---|---|
| [Microsoft Agent Framework (MAF)](https://github.com/microsoft/agent-framework) | Workflow graphs, agent runtime, tool framework, HITL |
| [Azure AI Foundry](https://ai.azure.com) | Model hosting (GPT-4o), project endpoint |
| [Pydantic](https://docs.pydantic.dev) | Structured output schemas for agent responses |
| [Azure Identity](https://learn.microsoft.com/python/api/azure-identity/) | Passwordless auth via Azure CLI |

---

## Key Takeaway

> **Copilot** = one agent + free text + hope.
> **MAF** = typed agents + workflow graphs + conditional routing + human gates + retry logic.

You're not building a chatbot. You're building a **production orchestration system** with the same primitives used for real enterprise agent deployments.

---

## Contributing

This workshop was created for WeAreDevelopers World Congress 2026. Issues and PRs welcome.

## License

MIT
