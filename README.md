# Building Multi-Agent AI Systems with MAF

> **From Copilot to Orchestrated Agents** — Build an autonomous multi-agent incident response system using Microsoft Agent Framework and Azure AI Foundry.

**WeAreDevelopers World Congress 2026** — Berlin, Friday 10 July | 12:15–14:15 | Room Ulm

*Isha Salania · Kiran Panchal · Ricardo Niepel*

---

## Overview

In this hands-on workshop, you'll build a production-grade **multi-agent incident response system** that handles production alerts autonomously — triaging, diagnosing, fixing, verifying, and communicating — all without human intervention.

You'll start by seeing why a single "copilot" agent fails at complex operations, then progressively build specialized agents, wire them into orchestrated workflows, and add memory so the system learns from past incidents.

```
┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐    ┌───────┐
│  Triage  │───►│ Diagnostics  │───►│ Remediation │───►│  Verify  │───►│ Comms │
│  Agent   │    │    Agent     │    │    Agent    │    │  Agent   │    │ Agent │
└──────────┘    └──────────────┘    └─────────────┘    └────┬─────┘    └───────┘
 2 tools         3 tools             5 tools                │           3 tools
                                         ▲       FAIL       │
                                         └──────────────────┘
```

**5 specialized agents · 15 infrastructure tools · Conditional routing · Incident memory**

---

## Learning Objectives

By the end of this workshop, you will be able to:

1. **Explain** why single-agent architectures fail for complex operational tasks
2. **Design** multi-agent systems with task decomposition and tool integration
3. **Build** agents using Microsoft Agent Framework (MAF) with Azure AI Foundry
4. **Orchestrate** agent workflows with conditional routing and shared state
5. **Implement** memory patterns that make agent systems improve over time

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

| Challenge | Title | Duration | Description |
|---|---|---|---|
| [Challenge 0](challenge-0/README.md) | Environment Setup | 15 min | Fork repo, deploy Azure resources, verify connection |
| [Challenge 1](challenge-1/README.md) | The Single-Agent Approach | 20 min | See why a single "copilot" fails at incident response |
| [Challenge 2](challenge-2/README.md) | Specialized Agents with Tools | 25 min | Build 5 focused agents with 15 infrastructure tools |
| [Challenge 3](challenge-3/README.md) | Workflow Orchestration | 25 min | Wire agents into an automated pipeline with routing |
| [Challenge 4](challenge-4/README.md) | Memory Patterns | 20 min | Add incident memory so the system learns over time |
| [Challenge 5](challenge-5/README.md) | Advanced Patterns (Bonus) | 20+ min | Human-in-the-loop, structured output, observability |

---

## Repository Structure

```
maf-lab/
├── challenge-0/               # Setup & verification
│   ├── README.md              # Setup instructions
│   ├── verify-setup.ipynb     # Environment check notebook
│   └── scripts/               # Azure deployment scripts
├── challenge-1/               # Single agent limitations
│   ├── README.md
│   └── challenge.ipynb
├── challenge-2/               # Specialized agents + tools
│   ├── README.md
│   └── challenge.ipynb        # 4 agents to build (1 reference provided)
├── challenge-3/               # Workflow orchestration
│   ├── README.md
│   └── challenge.ipynb        # Build executors + routing logic
├── challenge-4/               # Memory patterns
│   ├── README.md
│   └── challenge.ipynb        # Implement memory store + search
├── challenge-5/               # Bonus: advanced patterns
│   └── README.md              # Human-in-the-loop, structured output, tracing
├── tools/
│   └── mock_infra.py          # 15 simulated infrastructure tools
├── data/
│   └── incidents.json         # 3 sample incidents
├── solution/
│   └── full_workflow.py       # Complete reference implementation
├── .devcontainer/             # Codespaces configuration
├── requirements.txt
└── .env.example
```

---

## The Scenario

It's 3 AM. An alert fires. Your multi-agent system:

1. **Triages** — Checks history, finds runbook, classifies severity
2. **Diagnoses** — Queries metrics, analyzes logs, identifies root cause
3. **Fixes** — Restarts pods, scales services, toggles feature flags
4. **Verifies** — Runs health checks and smoke tests
5. **Communicates** — Posts to Slack, creates tickets, updates status page

All without waking you up.

### Sample Incidents

| # | Alert | Service | Root Cause | Agent Decision |
|---|-------|---------|-----------|----------------|
| 1 | High Latency | payment-api | Memory leak → OOM on pod-3 | Restart pod |
| 2 | Error Rate Spike | order-service | Cascading failure | Scale replicas |
| 3 | Email Failures | notification-service | Provider rate limiting | Toggle feature flag |

Each incident triggers **different agent decisions** — demonstrating that the workflow adapts based on what agents discover.

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
| [Microsoft Agent Framework (MAF)](https://github.com/microsoft/agent-framework) | Agent runtime, workflow orchestration, tool integration |
| [Azure AI Foundry](https://ai.azure.com) | Model hosting (GPT-4o), project management |
| [Azure Identity](https://learn.microsoft.com/en-us/python/api/azure-identity/) | Passwordless authentication via Azure CLI |
| Python 3.10+ | Workshop runtime |

---

## Key Takeaway

> **Copilot** assists a human with one task.
> **Multi-agent systems** operate autonomously across multiple systems, make decisions, and take action.

You're not building a chatbot. You're building an **autonomous operations system**.

---

## Contributing

This workshop was created for WeAreDevelopers World Congress 2026. Issues and PRs welcome.

## License

MIT
