# Multi-Agent Incident Response Workshop

Welcome to the Multi-Agent Incident Response Workshop. In this hands-on lab you will build a multi-agent system that triages, diagnoses, and remediates production incidents using **Microsoft Agent Framework** and **Azure AI Foundry**.

**WeAreDevelopers World Congress 2026** · Berlin, Friday 10 July · 12:15 - 14:15 · Room Ulm

## Introduction

Going from a single agent that answers questions to a coordinated system of agents that collaborate on complex tasks requires a different set of patterns: typed contracts between agents, declarative workflow graphs, conditional routing, human approval gates, and retry logic.

Using a code-first approach with **Microsoft Agent Framework (MAF)**, you will build a multi-agent incident response workflow that mirrors a real operations process: ingesting alerts, triaging severity, diagnosing root causes, planning remediation, obtaining human approval, and verifying the fix. The goal is a clear, testable workflow that can be reasoned about and iterated on.

> [!NOTE]
> No prior AI/ML experience is required. If you can write Python functions and call REST APIs, you are ready for this workshop.

## Learning Objectives

By participating in this workshop, you will learn how to:

- Build agents that return **typed structured outputs** using Pydantic schemas instead of free-text responses
- Design **workflow graphs** with conditional edges and switch-case routing for deterministic execution paths
- Implement **human-in-the-loop** patterns including tool-level approval and explicit workflow pause/resume
- Use **shared state management** to pass context across workflow executors without tight coupling
- Apply **retry and escalation** patterns so the system degrades gracefully instead of failing silently

## Scenario

This workshop uses a fictitious microservices platform as an example, but the patterns are applicable to any environment where incidents require coordinated response across multiple systems.

A production alert fires: the Payment API P99 latency has exceeded 30 seconds. Your multi-agent system handles the response end-to-end, routing through different paths based on severity:

```
                        ┌─ [CRITICAL] ──> Diagnostics ──> Remediation (HITL) ──> Verify ──> Comms
                        │
Alert ──> Triage ──> Switch ─ [HIGH] ────> Diagnostics ──> Remediation ──> Comms
                        │
                        └─ [LOW] ──────> Monitor Only
```

Each step is an agent or workflow executor. Routing is deterministic, based on typed data rather than LLM interpretation. Approval is explicit: the workflow pauses until a human responds.

### The Three Incidents

You will process three incidents during the workshop. Each triggers a different path through the same system:

| # | Description | Severity | Workflow Path | Outcome |
|---|-------------|----------|---------------|---------|
| 1 | Payment API P99 > 30s, pods OOMKilled | CRITICAL | Full pipeline with HITL approval | Restarts OOMKilled pod after human approves |
| 2 | Order Service cascading errors, 23% error rate | HIGH | Diagnostics, Remediation, Comms | Scales replicas from 3 to 5 |
| 3 | Notification emails failing, rate limited | LOW | Monitor only | Logs the incident, takes no action |

Same code, different outcomes. The Triage Agent returns structured data that the workflow uses for deterministic routing.

## Architecture

In this workshop you will build multiple agents in Python and connect them using a workflow graph in Microsoft Agent Framework. The focus is on the orchestration patterns rather than infrastructure complexity.

```
┌───────────────────────────────────────────────────────┐
│                  Your Application                     │
├───────────────────────────────────────────────────────┤
│  WorkflowBuilder  ·  Agent  ·  @executor              │  Orchestration
├───────────────────────────────────────────────────────┤
│  FoundryChatClient  ·  @tool  ·  Pydantic             │  Primitives
├───────────────────────────────────────────────────────┤
│  Azure AI Foundry  ·  GPT-4o  ·  Azure CLI            │  Infrastructure
└───────────────────────────────────────────────────────┘
```

Key components:

- **`Agent`** wraps an LLM with instructions, tools, and a typed output format
- **`FoundryChatClient`** connects to Azure AI Foundry (lightweight, no server-side resources)
- **`WorkflowBuilder`** declares a directed graph of executors with edges and conditions
- **`@executor`** is a node in the graph that receives messages and emits output
- **`@tool`** is a Python function the LLM can call, with optional human approval
- **`ctx`** is the workflow context for state, messaging, output, and human interaction

> [!NOTE]
> This workshop uses mock infrastructure tools that simulate Prometheus, Kubernetes, PagerDuty, and Slack APIs. No real infrastructure is affected during the exercises.

## Requirements

To complete this workshop, you will need the following:

- [**GitHub account**](https://github.com/signup) to access the repository and run [**GitHub Codespaces**](https://github.com/features/codespaces)
- An active **Azure subscription** with permissions to create AI Foundry resources
- **Python 3.10** or higher (3.11 in Codespaces)
- **Azure CLI** installed and authenticated (`az login`)
- Familiarity with **Python** programming, including handling JSON and making API calls

## Challenges

This workshop is divided into five challenges, each building on the previous one. You will start by setting up your environment, then progressively build individual agents, wire them into a workflow, and add production-grade safety patterns.

### Challenge structure

Each challenge follows a consistent structure:

| Section | Description |
|---------|-------------|
| **Objective** | Learning goals for the challenge |
| **What You Need to Know** | Concepts and technical background |
| **What You'll Build** | Step-by-step instructions |
| **Success Criteria** | How to verify your work |
| **Tips and Common Mistakes** | Guidance for beginners and advanced users |

### Challenge list

The following challenges are included in this workshop:

- **Challenge 0**: **[Environment Setup](challenge-0/README.md)** (15 min). Set up your development environment, deploy Azure resources, configure credentials, and verify the connection with a test agent.
- **Challenge 1**: **[Structured Agents](challenge-1/README.md)** (30 min). Build four agents (Triage, Diagnostics, Remediation Planner, Verification) that return typed Pydantic outputs instead of free text.
- **Challenge 2**: **[Workflow Graphs](challenge-2/README.md)** (30 min). Wire agents into a directed graph with `WorkflowBuilder`, using switch-case routing to send different severities down different paths.
- **Challenge 3**: **[Human-in-the-Loop](challenge-3/README.md)** (25 min). Add tool-level approval gates, explicit workflow pause/resume, and retry loops with escalation.
- **Challenge 4**: **[Advanced Composition](challenge-4/README.md)** (20+ min, bonus). Explore workflow-as-agent, sub-workflow composition, OpenTelemetry tracing, and parallel fan-out.

> [!TIP]
> Challenges 1 through 3 are the core workshop. Challenge 4 is for participants who finish early. A complete reference implementation is available in `solution/full_workflow.py`.

## Quick Start

### Option A: GitHub Codespaces (recommended)

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/ishasalania/maf-lab?quickstart=1)

Everything is pre-installed. Add your `.env` credentials and proceed to [Challenge 0](challenge-0/README.md).

### Option B: Local setup

```bash
git clone https://github.com/ishasalania/maf-lab.git
cd maf-lab
python -m venv .venv && .venv\Scripts\activate   # Windows
# source .venv/bin/activate                      # macOS/Linux
pip install -r requirements.txt
cp .env.example .env                             # Fill in your values
```

Then follow [Challenge 0](challenge-0/README.md) to verify everything works.

## Repository Structure

```
maf-lab/
├── challenge-0/               # Setup and verification
│   ├── README.md              # Step-by-step environment setup guide
│   ├── challenge-0.ipynb      # Verification notebook
│   └── scripts/               # Optional: deploy Azure resources yourself
├── challenge-1/               # Structured agents with Pydantic outputs
│   ├── README.md              # Concept guide: structured outputs
│   └── challenge-1.ipynb      # Build Triage, Diagnostics, Remediation, Verification agents
├── challenge-2/               # Workflow graphs with conditional routing
│   ├── README.md              # Concept guide: workflow graphs and switch-case
│   └── challenge-2.ipynb      # Wire agents into WorkflowBuilder with routing
├── challenge-3/               # Human-in-the-loop and resilience
│   ├── README.md              # Concept guide: approval, pause/resume, retry
│   └── challenge-3.ipynb      # Add HITL gates, functional workflows, retry loops
├── challenge-4/               # Bonus: advanced composition patterns
│   └── README.md              # Workflow-as-agent, sub-workflows, OTel, fan-out
├── tools/
│   └── mock_infra.py          # All @tool functions (metrics, logs, restart, scale, etc.)
├── data/
│   └── incidents.json         # Three sample incidents (CRITICAL, HIGH, LOW)
├── solution/
│   └── full_workflow.py       # Complete reference implementation
├── .devcontainer/             # Codespaces config (Python 3.11, all deps pre-installed)
├── requirements.txt           # agent-framework, azure-identity, pydantic, dotenv
└── .env.example               # Template for Azure credentials
```

## Web Version

This workshop is also available as a web-rendered walkthrough on MOAW:

**[https://moaw.dev/workshop/gh:ishasalania/maf-lab/main/docs/](https://moaw.dev/workshop/gh:ishasalania/maf-lab/main/docs/)**

## Key Technologies

| Technology | Version | Role |
|------------|---------|------|
| [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) | >= 1.0.0 | Agent runtime, workflow graphs, tools, HITL, state management |
| [Azure AI Foundry](https://ai.azure.com) | - | Hosts GPT-4o model, provides project endpoint |
| [Pydantic](https://docs.pydantic.dev) | >= 2.0 | Typed output schemas that constrain LLM responses |
| [Azure Identity](https://learn.microsoft.com/python/api/azure-identity/) | >= 1.17 | Passwordless auth via CLI credentials |
| Python | >= 3.10 | Runtime (3.11 in Codespaces) |

## Presenters

| Name | Role |
|------|------|
| **Isha Salania** | Cloud Solution Architect, Microsoft |
| **Kiran Panchal** | Cloud Solution Architect, Microsoft |
| **Ricardo Niepel** | Cloud Solution Architect, Microsoft |

## Contributing

This workshop was created for WeAreDevelopers World Congress 2026. Issues and pull requests are welcome.

## License

MIT
