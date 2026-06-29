# Challenge 4 — Memory Patterns

**Expected Duration: 20 minutes**

## Introduction

Your workflow handles incidents autonomously — but every time, it investigates from scratch. A human SRE gets **faster** over time because they remember: "Oh, this is the same memory leak from last Tuesday."

In this challenge, you'll add **incident memory** so your system:
- Recognizes recurring issues instantly
- References past resolutions
- Provides estimated time-to-resolve based on history
- Gets smarter with every incident it handles

---

## What You're Building

```
Alert fires
    │
    ▼
┌─────────────────────┐
│ Memory Provider      │ ◄── Searches past incidents
│ "This matches INC-  │     Returns: root cause, resolution, TTR
│  from 2 days ago"   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Triage Agent         │  Now KNOWS this is recurring
│ (enhanced with       │  Skips unnecessary investigation
│  memory context)     │  Fast-tracks to known-good fix
└─────────────────────┘
          │
          ▼
    [Rest of workflow — faster because diagnosis is already known]
```

---

## Tasks

Open `challenge-4/challenge.ipynb` and complete the following:

### Task 1: Build an Incident Memory Store

Create an `IncidentMemoryStore` class that:
- Holds past incident resolutions (pre-seeded with 4 examples)
- Has a `search(service, keywords)` method to find relevant matches
- Has a `store(memory)` method to save new resolutions

### Task 2: Create a Memory Tool

Wrap the memory store as a callable tool function `search_incident_memory(service_name, keywords)` that agents can invoke.

### Task 3: Build a Memory-Enhanced Triage Agent

Create a triage agent with 3 tools:
1. `search_incident_memory` — check past incidents FIRST
2. `check_alert_history` — recent alert patterns
3. `get_runbook` — standard procedures

Observe how it immediately says: "This matches a past incident from 2 days ago — resolution was restarting pod-3."

### Task 4: Store New Resolutions

After the workflow resolves an incident, store the resolution in memory so the next occurrence benefits.

---

## Compare: Before vs. After Memory

| Without Memory (Challenge 2) | With Memory (Challenge 4) |
|---|---|
| Investigates from scratch every time | Immediately recognizes recurring issue |
| Triage takes full investigation | Fast-tracks with known pattern |
| No historical TTR estimate | "Expected resolution: 6-8 minutes" |
| No link to related tickets | "Related: JIRA-4521" |
| Remediation may try wrong fix first | Jumps to known-good fix |

---

## Production Patterns

In a real system, you'd enhance this with:

| Pattern | Implementation |
|---------|---------------|
| **Semantic search** | Azure AI Search with embeddings for fuzzy matching |
| **Confidence decay** | Recent resolutions weighted higher than old ones |
| **Human feedback loop** | SREs mark if suggested resolution was helpful |
| **Cross-service correlation** | "When payment-api goes down, order-service follows" |
| **Automated runbook updates** | Memory feeds back into runbook maintenance |

---

## Hints

<details>
<summary>💡 Hint: Pre-seeded memories</summary>

The memory store includes 4 past incidents:
1. payment-api memory leak (2 days ago) — restart pod-3
2. payment-api connection pool exhaustion (4 days ago) — restart + increase pool
3. notification-service rate limiting (yesterday) — toggle backup email
4. user-service cert expiry (24 days ago) — manual fix by security team

When you search for "payment-api", it should find incidents #1 and #2.
</details>

<details>
<summary>💡 Hint: The learning loop</summary>

After storing a new resolution, the next time the same alert fires, `search_incident_memory` will return it. The agent sees: "This happened 3 times now, same root cause, same fix." This is how the system gets progressively smarter.
</details>

---

## Success Criteria

- [ ] Memory-enhanced triage agent finds past incidents for payment-api
- [ ] Agent references the previous resolution in its output
- [ ] New incident resolution is stored in memory after completion
- [ ] System would handle the SAME alert faster the second time

---

## 🎉 Workshop Complete!

Congratulations! You've built a production-grade multi-agent incident response system.

### What You Achieved

| Challenge | Concept | What You Built |
|-----------|---------|----------------|
| 0 | Setup | Azure AI Foundry connection |
| 1 | Motivation | Saw why single agents fail |
| 2 | Task Decomposition + Tools | 5 specialized agents with 15 tools |
| 3 | Agent Coordination | Automated workflow with conditional routing |
| 4 | Memory Patterns | Learning system that improves over time |

### The Journey: Copilot → Orchestrated Agents

```
Single Agent          →  Specialized Agents  →  Workflow          →  Memory
(generic advice)         (real tools)            (autonomous)         (learns)
```

### Next Steps (After the Workshop)

| Topic | What to explore |
|-------|-----------------|
| **Human-in-the-loop** | Add approval gates before destructive actions |
| **Checkpointing** | Persist workflow state for long-running incidents |
| **MCP integration** | Connect to real Prometheus/PagerDuty via MCP protocol |
| **Observability** | Add OpenTelemetry tracing to monitor agent decisions |
| **Evaluation** | Red-team test with adversarial incident scenarios |

### Resources

- [Microsoft Agent Framework Docs](https://learn.microsoft.com/en-us/agent-framework/)
- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Azure AI Foundry](https://ai.azure.com)
- This workshop: [github.com/ishasalania/maf-lab](https://github.com/ishasalania/maf-lab)
