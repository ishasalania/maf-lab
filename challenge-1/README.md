# Challenge 1 — The Single-Agent Approach (Why It Fails)

**Expected Duration: 20 minutes**

## Introduction

In this challenge, you'll experience firsthand why a single "copilot" agent can't handle complex operational tasks. You'll send a real production alert to a generic agent and observe its limitations — setting the stage for **why** multi-agent systems exist.

---

## The Scenario

It's 2:41 AM. This alert just fired in your monitoring system:

```
🔴 ALERT: High Latency on payment-api
   p95 latency: 2340ms (threshold: 2000ms)
   Duration: 5 minutes
   Impact: Customers experiencing slow checkouts
```

Your job: handle this incident end-to-end — triage, diagnose, fix, verify, and notify the team.

---

## What You'll Observe

A single agent without tools will:
- **Guess** instead of checking real metrics
- **Suggest** instead of taking action
- **Generic advice** regardless of the specific incident
- **No verification** that anything actually worked
- **No memory** of past incidents

---

## Task

Open `challenge-1/challenge.ipynb` and run all cells.

1. Read the alert that fires
2. Run the single "copilot" agent
3. Read its response carefully
4. Answer: What's wrong with this response?

---

## Discussion Questions

After running the notebook, consider:

| Question | What you should notice |
|----------|----------------------|
| Does the agent know the actual CPU/memory usage? | No — it guesses |
| Can it restart a pod? | No — it can only suggest |
| Does it know this happened before? | No — no memory |
| How would you verify the fix worked? | You can't — no tools |
| Would you trust this at 3 AM without human oversight? | Absolutely not |

---

## Key Concept: Why Multi-Agent?

| Single Agent (Copilot) | Multi-Agent System |
|---|---|
| One prompt, one context window | Specialized experts per task |
| No tools | Each agent owns specific tools |
| No orchestration | Workflow with routing and retries |
| No memory | Learns from past incidents |
| Generic advice | Takes concrete action |

---

## Success Criteria

- [ ] You ran the single agent and got a response
- [ ] You can articulate 3 things wrong with the response
- [ ] You understand why tools + specialization + orchestration are needed

---

## Learning Resources

| Topic | Link |
|-------|------|
| Microsoft Agent Framework | [github.com/microsoft/agent-framework](https://github.com/microsoft/agent-framework) |
| Why multi-agent? | [Multi-agent design patterns](https://learn.microsoft.com/en-us/azure/ai-services/agents/concepts/multi-agent) |
| Task decomposition | [Agentic AI design patterns](https://www.deeplearning.ai/the-batch/agentic-design-patterns-part-2-reflection/) |

---

## ➡️ Next Challenge

Ready to build something better? Head to **[Challenge 2: Specialized Agents with Tools](../challenge-2/README.md)** where you'll create 5 focused agents that can actually do things.
