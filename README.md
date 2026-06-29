# Building Multi-Agent AI Systems with MAF
## From Copilot to Orchestrated Agents

**WeAreDevelopers World Congress 2026 — Berlin**
Friday 10 July | 12:15–14:15 | Room Ulm

Isha Salania · Kiran Panchal · Ricardo Niepel

---

## What You'll Build

An autonomous **multi-agent incident response system** that handles production alerts while you sleep.

```
┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐    ┌───────┐
│  Triage  │───►│ Diagnostics  │───►│ Remediation │───►│  Verify  │───►│ Comms │
│  Agent   │    │    Agent     │    │    Agent    │    │  Agent   │    │ Agent │
└──────────┘    └──────────────┘    └─────────────┘    └────┬─────┘    └───────┘
 2 tools         3 tools             5 tools                │           3 tools
                                         ▲       FAIL       │
                                         └──────────────────┘
```

5 specialized agents • 15 infrastructure tools • Conditional routing • Incident memory

---

## Workshop Flow (2 hours)

| Time | Step | What You Do |
|------|------|-------------|
| 12:15–12:30 | **Setup** | Clone, install, verify Azure connection |
| 12:30–12:50 | **Step 1** | Run a single "copilot" agent — see why it fails |
| 12:50–13:15 | **Step 2** | Build 5 specialized agents with real tools |
| 13:15–13:40 | **Step 3** | Wire them into an automated workflow with routing |
| 13:40–13:55 | **Step 4** | Add memory so the system learns from past incidents |
| 13:55–14:15 | **Experiment** | Try different incidents, see different agent decisions |

---

## Prerequisites

- Python 3.10+
- Azure CLI installed (`az login` working)
- An Azure AI Foundry project with a GPT-4o deployment

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/ishasalania/maf-lab.git
cd maf-lab

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
copy .env.example .env
# Edit .env with your Azure AI project endpoint

# 5. Verify setup
# Open 0-verify-setup.ipynb and run all cells
```

---

## Repository Structure

```
maf-lab/
├── 0-verify-setup.ipynb       # Verify your environment works
├── 1-single-agent.ipynb       # The "copilot" approach (see it fail)
├── 2-specialized-agents.ipynb # Build agents with tools (YOUR CODE HERE)
├── 3-workflow.ipynb           # Orchestrate into a workflow (YOUR CODE HERE)
├── 4-memory.ipynb             # Add incident memory (YOUR CODE HERE)
├── tools/
│   └── mock_infra.py          # 15 simulated infrastructure tools
├── data/
│   └── incidents.json         # 3 sample incidents to process
├── solution/                  # Complete solutions (if you get stuck)
└── requirements.txt
```

---

## Topics Covered

- **Task Decomposition** — Splitting a complex problem into specialist agents
- **Tool Integration** — Giving agents access to infrastructure APIs
- **Agent Coordination** — Workflow orchestration with conditional routing
- **Memory Patterns** — Learning from past incidents to resolve faster

---

## The Scenario

It's 3 AM. An alert fires. Your multi-agent system:

1. **Triages** — Checks history, finds runbook, classifies severity
2. **Diagnoses** — Queries metrics, analyzes logs, identifies root cause
3. **Fixes** — Restarts pods, scales services, toggles feature flags
4. **Verifies** — Runs health checks and smoke tests
5. **Communicates** — Posts to Slack, creates tickets, updates status page

All without waking you up.

---

## Sample Incidents Included

| # | Alert | Service | Root Cause |
|---|-------|---------|-----------|
| 1 | High Latency | payment-api | Memory leak → OOM on pod-3 |
| 2 | Error Rate Spike | order-service | Cascading failure from payment-api |
| 3 | Email Failures | notification-service | Provider rate limiting |

Each incident triggers **different agent decisions** — restart vs. scale vs. feature flag.

---

## Key Takeaway

> **Copilot** assists a human with one task.
> **Multi-agent systems** operate autonomously across multiple systems, make decisions, and take action.

You're not building a chatbot. You're building an **autonomous operations system**.
