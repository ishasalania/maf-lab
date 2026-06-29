# Challenge 3 — Workflow Orchestration

**Expected Duration: 25 minutes**

## Introduction

In Challenge 2, you built 5 great agents — but you're manually copying outputs between them. That's fine for testing, but useless at 3 AM when nobody's awake.

Now you'll wire them into a **MAF Workflow** — an automated pipeline that:
- Chains agents together with typed state
- Routes conditionally (fix worked → notify, fix failed → retry)
- Runs end-to-end with a single call
- Handles the same incident differently based on what the agents discover

---

## What You're Building

```
┌──────────┐    ┌──────────────┐    ┌─────────────┐    ┌──────────┐    ┌───────┐
│  Triage  │───►│ Diagnostics  │───►│ Remediation │───►│  Verify  │───►│ Comms │
└──────────┘    └──────────────┘    └─────────────┘    └────┬─────┘    └───────┘
                                           ▲                │
                                           │    FAIL        │
                                           └────────────────┘
```

Key concepts:
- **Executors**: Each agent wrapped as a workflow step
- **Shared State**: A `dataclass` that holds the full incident context as it flows through
- **Edges**: Return values from executors determine the next step (routing)
- **Retry Logic**: Verification can loop back to remediation if the fix didn't work

---

## Tasks

Open `challenge-3/challenge.ipynb` and complete the following:

### Task 1: Define Shared State

Create an `IncidentState` dataclass that holds:
- Alert info (title, service, severity, description)
- Results from each stage
- Control flow flags (is_resolved, retry_count)

### Task 2: Create Workflow Executors

Wrap each agent into an `@executor` function that:
- Reads from shared state
- Creates and runs the agent
- Stores the result back in state
- Returns the name of the next step

### Task 3: Add Conditional Routing

The verification executor should:
- Return `"communications"` if the fix worked (RESOLVED)
- Return `"remediation"` if the fix failed (FAILED) and retries remain
- Return `"communications"` if max retries exceeded (escalate)

### Task 4: Build and Run the Workflow

Use `WorkflowBuilder` to wire all executors together and run the full pipeline on the payment-api alert.

### Task 5: Try a Different Incident

Run the same workflow on incident #3 (notification-service email failures). Observe how the agents make **completely different decisions** — toggling a feature flag instead of restarting a pod.

---

## Key Concepts

| Concept | What it means |
|---------|--------------|
| `@executor` | Decorator marking a function as a workflow step |
| `WorkflowContext[State]` | Provides access to shared state within an executor |
| Return value | The name of the next executor to run (routing) |
| `Return None` | Signals the workflow is complete (terminal step) |
| Shared state dataclass | Type-safe container for data flowing through the pipeline |

---

## Hints

<details>
<summary>💡 Hint: How routing works</summary>

Each executor returns a string — the name of the next step. This is how you implement conditional routing:

```python
@executor
async def verification_executor(ctx: WorkflowContext[IncidentState]) -> str:
    # ... run agent, check result ...
    if "RESOLVED" in result.text.upper():
        return "communications"  # Success path
    else:
        return "remediation"     # Retry path
```
</details>

<details>
<summary>💡 Hint: Incident #3 should toggle a feature flag</summary>

When you run the notification-service incident, the diagnostics will show the email provider is rate-limited and the backup provider feature flag is OFF. The remediation agent should call `toggle_feature_flag("use_backup_email", True)` instead of restarting anything.
</details>

---

## Success Criteria

- [ ] Workflow runs end-to-end with one call (`workflow.run(state=...)`)
- [ ] Payment-api incident: agent restarts pod-3 and verifies
- [ ] Notification-service incident: agent toggles feature flag
- [ ] Verification routes correctly (resolved → comms)
- [ ] Final state shows `is_resolved=True`

---

## ➡️ Next Challenge

The workflow handles incidents — but starts from scratch every time. A human SRE gets faster because they remember past incidents. Head to **[Challenge 4: Memory Patterns](../challenge-4/README.md)** to make your system learn.
