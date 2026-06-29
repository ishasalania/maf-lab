# Challenge 2 — Workflow Graphs & Conditional Routing

**Expected Duration: 30 minutes**

## Introduction

In Challenge 1, you manually chained agents: triage → diagnostics → plan → verify.
That's fine for one path, but production incidents need **conditional routing** —
different severities should take different paths through the system.

MAF's `WorkflowBuilder` models this as a **directed acyclic graph (DAG)** where
edges can have conditions, switch-case groups enable one-of-N routing, and
shared state flows through all executors.

## Key Concepts

| Concept | API | Why It Matters |
|---------|-----|----------------|
| Workflow graph | `WorkflowBuilder` + `add_edge()` | Explicit execution topology |
| Executors | `@executor(id="...")` | Nodes in the graph |
| Agent executors | `AgentExecutor(agent)` | Wrap agents as workflow nodes |
| Switch-case | `add_switch_case_edge_group()` | Deterministic one-of-N routing |
| Edge conditions | `condition=fn` | Boolean gates on edges |
| State | `ctx.set_state()` / `ctx.get_state()` | Shared data across executors |
| Output | `ctx.yield_output()` | Emit final workflow result |
| Messaging | `ctx.send_message()` | Pass data to downstream nodes |

## What You'll Build

```
ingest_alert → triage_agent → parse_triage → SWITCH:
    Case("critical") → to_diagnostics → diagnostics_agent → comms
    Case("high")     → to_diagnostics → diagnostics_agent → comms
    Default          → monitor_only
```

## Getting Started

Open the notebook:

```
challenge-2/challenge.ipynb
```

## Success Criteria

- [ ] Edge condition factory `get_severity_condition()` implemented
- [ ] `to_diagnostics` executor reads from state and constructs `AgentExecutorRequest`
- [ ] `monitor_only` executor yields output for low-severity alerts
- [ ] Full workflow graph wired with `WorkflowBuilder`
- [ ] CRITICAL incident routes through diagnostics → comms (validation passes)
- [ ] LOW incident routes through monitor_only (validation passes)

## Tips

- Edge conditions receive whatever the upstream executor sent — check `isinstance()` first
- `AgentExecutorRequest` needs `messages=[Message("user", contents=[...])]` and `should_respond=True`
- `WorkflowContext[Never, str]` means: no downstream messages, yields `str` as workflow output
- Use `ctx.set_state()` early — downstream executors will need the data

## ➡️ Next Challenge

Your workflow routes correctly but executes autonomously.
In Challenge 3, you'll add **human approval gates** and **retry logic**.

[Challenge 3: Human-in-the-Loop →](../challenge-3/README.md)
