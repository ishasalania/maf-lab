# Challenge 3 — Human-in-the-Loop & Resilience

**Expected Duration: 25 minutes**

---

## The Problem: Autonomous Agents Are Dangerous

Your workflow from Challenge 2 routes correctly. But it runs **completely autonomously**. That means:

- `restart_pod("payment-api")` executes at 3 AM with no one watching
- A remediation plan with `risk_level: "high"` deploys without review
- If verification fails, the system just... stops

In production, this is terrifying. You need:

1. **Approval gates** — dangerous tools require explicit human sign-off
2. **Plan review** — the workflow pauses to show a human the plan before executing
3. **Retry logic** — if verification fails, try again (up to N times) before escalating

MAF provides all three as first-class features — not bolt-on hacks.

---

## What You'll Learn

| Concept | What It Is | Why It Matters |
|---------|------------|----------------|
| **`@tool(approval_mode="always_require")`** | Tool-level approval gate | Dangerous tools pause the workflow until a human approves |
| **`ctx.request_info()`** | Workflow-level pause | Explicitly ask a human a question mid-workflow |
| **`WorkflowRunState.IDLE_WITH_PENDING_REQUESTS`** | Paused state detection | Know when the workflow is waiting for human input |
| **`workflow.run(responses={...})`** | Resume paused workflow | Feed human's answer back in, workflow continues |
| **`@workflow` / `@step`** | Functional workflows | Plain Python async functions with checkpointing |
| **Retry loops** | Native for/while in functional workflows | Try verification up to 3x before escalating |

---

## The Three HITL Patterns

### Pattern 1: Tool Approval (Simplest)

The tool itself is marked as needing approval. When the LLM tries to call it, the workflow **automatically pauses**.

```python
@tool(approval_mode="always_require")
def restart_pod(service: Annotated[str, "Service to restart"]) -> str:
    """Restart all pods for a service. DESTRUCTIVE — requires approval."""
    return f"✅ Restarted pods for {service}"

# When the agent calls restart_pod(), MAF intercepts:
#   1. Workflow pauses
#   2. Human sees: "Agent wants to call restart_pod('payment-api'). Approve?"
#   3. Human approves (or rejects)
#   4. Workflow resumes (or tool call is blocked)
```

**When to use:** For individual dangerous operations (restart, delete, scale down).

### Pattern 2: Explicit Pause/Resume (Most Flexible)

The executor explicitly asks the human a question. The workflow pauses until they answer.

```python
@executor(id="confirm_plan")
async def confirm_plan(ctx, request):
    plan = ctx.get_state("remediation_plan")

    # Workflow PAUSES here — returns to caller with state IDLE_WITH_PENDING_REQUESTS
    approval = await ctx.request_info(
        f"Proposed plan: {plan.action} on {plan.target_service}. "
        f"Risk: {plan.risk_level}. Approve? (yes/no)"
    )

    if approval.lower() == "yes":
        ctx.send_message(plan)  # Continue to execution
    else:
        ctx.yield_output("❌ Plan rejected by operator.")
```

**When to use:** For complex decisions where you want to show the human rich context.

### Pattern 3: Retry with Escalation (Resilience)

A functional workflow with a loop — retry up to N times, then escalate.

```python
@workflow
async def verify_with_retry(ctx):
    for attempt in range(3):
        result = await ctx.run_step(check_health)
        if result.healthy:
            return f"✅ Verified on attempt {attempt + 1}"
        await ctx.run_step(wait_and_retry)

    # All retries exhausted — escalate
    await ctx.request_info("Verification failed 3x. Escalate to on-call?")
    return "⚠️ Escalated to human operator"
```

**When to use:** For operations that might fail transiently (network issues, cold starts).

---

## How the Approval Loop Works

This is the most confusing part for newcomers, so here's the full mental model:

```
YOUR CODE                          MAF ENGINE                         HUMAN
────────────────────────────────────────────────────────────────────────────────
                                                                     
events = workflow.run(input)        → Executes graph                 
                                    → Agent calls restart_pod()      
                                    → Tool has approval_mode         
                                    → Workflow PAUSES                 
                                                                     
events.get_final_state()            → Returns IDLE_WITH_PENDING_REQUESTS
                                                                     
events.get_request_info_events()    → Returns list of pending approvals
                                                                     Human sees:
                                                                     "Approve restart_pod('payment-api')?"
                                                                     Human types: "yes"
                                                                     
response = event.data               → Create approval response       
  .to_function_approval_response(                                    
    approved=True                                                    
  )                                                                  
                                                                     
events = workflow.run(              → Resume with approval           
  responses={event.id: response}                                     
)                                   → Tool executes                  
                                    → Workflow continues              
                                                                     
events.get_final_state()            → Returns IDLE (done!)           
```

The key insight: **the workflow is stateful**. You call `workflow.run()` multiple times — each time either advancing the graph or providing human responses.

---

## What You'll Build

### Part A: HITL Workflow with Tool Approval

Wire up a workflow where the remediation agent has approval-gated tools:

```
prepare_remediation ──→ remediation_agent ──→ confirm_execution
                              │
                              │ (calls restart_pod)
                              │ → PAUSES for approval
                              │ ← Human approves
                              │ → Tool executes
                              │
                              ▼
                        confirm_execution ──→ yield output
```

### Part B: Functional Workflow with `ctx.request_info()`

Build a workflow that explicitly pauses to show the plan:

```python
@workflow
async def hitl_remediation(ctx):
    plan = await ctx.run_step(generate_plan)
    approval = await ctx.request_info(f"Execute {plan}? (yes/no)")
    if approval == "yes":
        result = await ctx.run_step(execute_plan, plan)
        return result
    return "Cancelled by operator"
```

### Part C: Retry Workflow

Build a verification loop with max 3 attempts:

```python
@workflow
async def verify_with_retry(ctx):
    for i in range(3):
        health = await ctx.run_step(check_health)
        if health.healthy:
            return f"✅ Healthy after {i+1} attempts"
    return await ctx.run_step(escalate)
```

---

## Getting Started

Open the notebook:

```
challenge-3/challenge.ipynb
```

The notebook provides:
- ✅ Remediation agent with approval-gated tools (reference)
- ✅ `prepare_remediation` and `confirm_execution` executors
- 🔨 TODO: Wire HITL workflow with `WorkflowBuilder`
- 🔨 TODO: Approval loop — process `get_request_info_events()` and respond
- 🔨 TODO: Functional workflow with `ctx.request_info()`
- 🔨 TODO: Retry workflow with max 3 attempts and escalation

---

## Success Criteria

- [ ] HITL workflow wired — `WorkflowBuilder.build()` succeeds
- [ ] Approval loop processes `get_request_info_events()` correctly
- [ ] After approval, workflow resumes and produces final output
- [ ] Functional workflow with `ctx.request_info()` pauses at the right moment
- [ ] Resume with `responses={...}` completes the functional workflow
- [ ] Retry workflow loops correctly and escalates after max retries

---

## Tips & Common Mistakes

### For Beginners

- **The workflow doesn't crash when it pauses** — it just returns with state `IDLE_WITH_PENDING_REQUESTS`
- **You call `workflow.run()` again** with the human's response — it picks up where it left off
- **`get_request_info_events()`** returns a list — iterate and respond to each one
- **Functional workflows are just async functions** — `@step` caches results across pauses

### For Advanced Users

- `WorkflowRunState.IDLE` = workflow complete. `IDLE_WITH_PENDING_REQUESTS` = paused.
- `event.data.to_function_approval_response(approved=True)` — this is the exact format
- In functional workflows, `@step` ensures a function isn't re-executed after resume
- The retry pattern works because functional workflows maintain state across `workflow.run()` calls
- You can combine tool approval + explicit `request_info()` in the same workflow

### Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Not checking `get_final_state()` | Think workflow is done when it's paused | Always check state before assuming completion |
| Wrong response format | Workflow errors on resume | Use `.to_function_approval_response()` helper |
| Forgetting `responses=` on resume | Workflow restarts from beginning | Pass the dict of `{event_id: response}` |
| Infinite retry loop | Never terminates | Always have a max count + escalation path |
| Using `@step` on non-idempotent functions | Stale cached results | `@step` is for expensive pure computations |

---

## Deep Dive: Why HITL Is a First-Class Concern

Most agent frameworks treat HITL as an afterthought — "just put a `input()` call somewhere." This breaks in production because:

1. **Workflows run on servers** — there's no terminal to prompt
2. **Approvals are async** — the human might respond hours later
3. **State must persist** — you can't hold a process in memory waiting
4. **Multiple approvals might be needed** — in the same workflow run

MAF solves this with a **stateful workflow engine** that can serialize its state, pause indefinitely, and resume from exactly where it stopped. The `responses={}` pattern means:

- The workflow can be paused for seconds or hours
- The approval can come from a UI, a Slack bot, or an API call
- Multiple workflows can be paused simultaneously
- The engine handles serialization/deserialization transparently

---

## ➡️ What's Next (Bonus)

You've built the full pipeline: structured agents → workflow routing → human approval → retry logic. If you finish early, head to **Challenge 4** for advanced composition patterns:

- **Workflow-as-Agent** — wrap entire workflows as callable agents
- **Sub-Workflow Composition** — nested workflows as graph nodes
- **OpenTelemetry** — trace every agent call and tool invocation
- **Parallel Fan-Out** — investigate multiple services concurrently

[Challenge 4: Advanced Composition →](../challenge-4/README.md)
