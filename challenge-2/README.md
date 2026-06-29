# Challenge 2 — Specialized Agents with Tools

**Expected Duration: 25 minutes**

## Introduction

Now you'll build what the single agent couldn't do — **five specialized agents**, each owning specific infrastructure tools. This is the core of multi-agent design: **task decomposition** + **tool integration**.

Instead of one confused agent, you'll have experts:

| Agent | Role | Tools |
|-------|------|-------|
| **Triage Agent** | First responder — classify, check history, find runbook | `check_alert_history`, `get_runbook` |
| **Diagnostics Agent** | Investigator — find root cause with evidence | `get_metrics`, `get_logs`, `check_dependencies` |
| **Remediation Agent** | Operator — execute the fix | `restart_pod`, `scale_service`, `flush_cache`, `toggle_feature_flag` |
| **Verification Agent** | QA — confirm the fix worked | `get_health_status`, `run_smoke_test` |
| **Communications Agent** | Reporter — notify team, create tickets | `post_to_slack`, `create_incident_ticket`, `update_status_page` |

---

## What You're Building

```
Alert ──► Triage ──► Diagnostics ──► Remediation ──► Verification ──► Comms
          (2 tools)   (3 tools)       (5 tools)       (2 tools)        (3 tools)
```

Each agent:
- Has a **focused responsibility** (easier to prompt correctly)
- Owns **specific tools** (can't misuse tools meant for other tasks)
- Produces **structured output** for the next agent
- Is **testable in isolation** (you can run any agent alone)

---

## Tasks

Open `challenge-2/challenge.ipynb` and complete the following:

### Task 1: Build the Triage Agent
Write the agent instructions and run it on the alert. It should:
- Call `check_alert_history` to see if this is recurring
- Call `get_runbook` to find the playbook
- Output: severity, recurring status, recommended next steps

### Task 2: Build the Diagnostics Agent
Write instructions that make it systematically gather evidence:
- Call `get_metrics` → What are CPU/memory/latency numbers?
- Call `get_logs` → What errors are appearing?
- Call `check_dependencies` → Are upstream/downstream services affected?
- Output: specific root cause with evidence

### Task 3: Build the Remediation Agent
This agent has the "dangerous" tools. Its instructions must:
- ONLY act based on diagnostics findings
- Use exact pod/service names from the diagnostics
- Call `escalate_to_human` if auto-fix isn't allowed

### Task 4: Build the Verification Agent
Confirm the fix worked:
- Call `get_health_status` for service health
- Call `run_smoke_test` for functional tests
- Verdict: RESOLVED or NEEDS_ESCALATION

### Task 5: Build the Communications Agent
Handle all notifications:
- Post to Slack with brief summary
- Create an incident ticket with full details
- Update the status page

---

## Hints

<details>
<summary>💡 Hint: Writing good agent instructions</summary>

The key to good agent instructions:
1. State the role clearly ("You are a Triage Agent")
2. List the tools and when to use each one
3. Specify the output format you expect
4. Add constraints ("Do NOT guess — only use data from your tools")
</details>

<details>
<summary>💡 Hint: What the Diagnostics Agent should find</summary>

Look at what `get_metrics("payment-api")` returns — you'll see pod-3 has memory at 3891MB (limit 4096MB) and 4 restarts. The logs show OOMKilled errors. This tells you exactly which pod to restart.
</details>

<details>
<summary>💡 Hint: Remediation Agent safety</summary>

The runbook for "high_latency" has `auto_remediation_allowed: true`, so the agent CAN act. But for "certificate_expiry" incidents, it's `false` — the agent should escalate instead.
</details>

---

## Success Criteria

- [ ] Each agent calls its tools (not just generating text)
- [ ] Diagnostics agent identifies pod-3 OOM as root cause
- [ ] Remediation agent restarts the specific pod (not just "a pod")
- [ ] Verification agent confirms the fix worked
- [ ] Communications agent posts to Slack AND creates a ticket

---

## ➡️ Next Challenge

You're manually passing outputs between agents. What if verification fails? What if you want this to run unattended? Head to **[Challenge 3: Workflow Orchestration](../challenge-3/README.md)** to automate the pipeline.
