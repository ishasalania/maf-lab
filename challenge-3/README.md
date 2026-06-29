# Challenge 3 — Human-in-the-Loop & Resilience

**Expected Duration: 25 minutes**

## Introduction

Your workflow routes correctly — but would you trust it to `restart_pod` in production
at 3 AM without asking anyone? What if the diagnostics confidence is only 60%?

Production agent systems need **human oversight** for dangerous operations and
**resilience patterns** when automated verification fails. MAF provides these
through tool-level approval, explicit workflow pause/resume, and native Python
control flow in functional workflows.

## Key Concepts

| Concept | API | Why It Matters |
|---------|-----|----------------|
| Tool approval | `@tool(approval_mode="always_require")` | Dangerous tool calls need human sign-off |
| Explicit HITL | `ctx.request_info()` | Pause workflow, ask human, resume |
| Workflow resume | `workflow.run(responses={...})` | Continue paused workflow with human input |
| Workflow state | `WorkflowRunState.IDLE_WITH_PENDING_REQUESTS` | Detect when workflow is waiting |
| Functional workflows | `@workflow` decorator | Plain Python async functions as workflows |
| Checkpointing | `@step` decorator | Cache expensive results across resume cycles |
| Retry loops | Native for/while | Python control flow in functional workflows |

## What You'll Build

1. **Tool approval workflow** — agent calls `restart_pod()`, workflow pauses, you approve
2. **Functional HITL workflow** — explicit `ctx.request_info()` to review a plan before execution
3. **Retry pattern** — verification loop that retries 3x before escalating

## Getting Started

Open the notebook:

```
challenge-3/challenge.ipynb
```

## Success Criteria

- [ ] HITL workflow wired with `WorkflowBuilder`
- [ ] Approval loop handles `get_request_info_events()` and responds
- [ ] Workflow resumes after approval and produces output
- [ ] Functional workflow with `ctx.request_info()` pauses correctly
- [ ] Resume with `responses={...}` completes the functional workflow
- [ ] Retry workflow uses a loop with max retries + escalation fallback

## Tips

- `events.get_final_state()` tells you if the workflow is paused (`IDLE_WITH_PENDING_REQUESTS`) or done (`IDLE`)
- `event.data.to_function_approval_response(approved=True)` creates the response format MAF expects
- In functional workflows, `@step` saves results — the function won't re-run on resume
- The approval loop pattern: `while request_info_events:` → process → `workflow.run(responses=...)` → check again

## ➡️ Bonus

If you finish early, head to [Challenge 4: Advanced Composition](../challenge-4/README.md) for
workflow-as-agent patterns, sub-workflow composition, parallelism, and observability.
