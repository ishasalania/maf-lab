# Challenge 2 — Workflow Graphs & Conditional Routing

**Expected Duration: 30 minutes**

---

## The Problem: Ad-Hoc Agent Chaining Doesn't Scale

In Challenge 1, you manually chained agents:

```python
triage_result = await triage_agent.run(alert)
diagnostics_result = await diagnostics_agent.run(triage_result.text)
plan = await planner_agent.run(diagnostics_result.text)
```

This works for one linear path. But production incidents need **branching**:
- CRITICAL → full pipeline with human approval
- HIGH → diagnostics + auto-remediation
- LOW → just log it

With manual chaining, you'd write nested if/else statements. Add 5 more paths, 3 more agents, error handling, state passing — it becomes unmaintainable spaghetti.

**The fix:** Declare your agent topology as a **directed acyclic graph (DAG)**. MAF's `WorkflowBuilder` executes it — you just define nodes (executors) and edges (with conditions).

---

## What You'll Learn

| Concept | What It Is | Why It Matters |
|---------|------------|----------------|
| **`WorkflowBuilder`** | Graph construction API | Declare topology, not control flow |
| **`@executor`** | A node in the workflow graph | Receives messages, emits output, accesses shared state |
| **`AgentExecutor`** | Wraps an `Agent` as a workflow node | Bridge between agents and the graph |
| **`add_edge()`** | Connect two nodes | Defines execution order |
| **`add_switch_case_edge_group()`** | One-of-N routing | Deterministic branching based on data |
| **`Case` / `Default`** | Switch-case targets | Which node to route to, with what condition |
| **`ctx.set_state()` / `ctx.get_state()`** | Shared state | Pass data between executors without tight coupling |
| **`ctx.send_message()`** | Message passing | Feed input to the next executor |
| **`ctx.yield_output()`** | Emit final result | What the workflow returns to the caller |

---

## How Workflow Graphs Work

### Mental Model

Think of it like a CI/CD pipeline:

```
GitHub Actions:                  MAF WorkflowBuilder:
┌────────┐                       ┌────────────────┐
│ Build  │──→ Test ──→ Deploy    │ ingest_alert   │──→ triage_agent ──→ parse_triage
└────────┘                       └────────────────┘         │
                                                            ▼
                                                      ┌───────────┐
                                                      │  SWITCH   │
                                                      ├───────────┤
                                                      │ critical  │──→ diagnostics ──→ comms
                                                      │ high      │──→ diagnostics ──→ comms
                                                      │ default   │──→ monitor_only
                                                      └───────────┘
```

Each node is an `@executor` function. Edges define what runs after what. Conditions on edges control *which* path is taken.

### The Execution Model

```
1. WorkflowBuilder.build() → creates a Workflow object
2. workflow.run(input) → starts execution at start_executor
3. Each executor:
   - Receives: ctx (context) + request (the message from upstream)
   - Can: read/write state, send messages, yield output, call agents
   - Returns: nothing (communicates via ctx)
4. Edges fire based on what the executor sent via ctx.send_message()
5. Edge conditions are just functions: (message) -> bool
6. Switch-case groups: exactly ONE case matches, or the default fires
```

### State vs Messages

| Mechanism | Use Case | Scope |
|-----------|----------|-------|
| `ctx.set_state("key", value)` | Store data any executor might need later | Workflow-wide |
| `ctx.send_message(msg)` | Feed input to the next specific executor | One edge |
| `ctx.yield_output(result)` | The workflow's final return value | Returned to caller |

**Rule of thumb:** Use state for "FYI" data. Use messages for "here's your input."

---

## What You'll Build

```
ingest_alert ──→ triage_agent ──→ parse_triage ──→ SWITCH:
                                                     │
                            ┌────────────────────────┼────────────────┐
                            ▼                        ▼                ▼
                    [severity == "critical"]  [severity == "high"]  [default]
                            │                        │                │
                            ▼                        ▼                ▼
                     to_diagnostics           to_diagnostics     monitor_only
                            │                        │           (yield output)
                            ▼                        ▼
                    diagnostics_agent         diagnostics_agent
                            │                        │
                            ▼                        ▼
                          comms                    comms
                     (yield output)           (yield output)
```

### The Executors

| Executor | Role | Provided? |
|----------|------|-----------|
| `ingest_alert` | Parses raw alert JSON, stores in state, sends to triage | ✅ Provided |
| `triage_agent` | Wraps your Triage Agent from Challenge 1 | ✅ Provided |
| `parse_triage` | Validates TriageResult, emits routing decision | ✅ Provided |
| `get_severity_condition()` | Factory: returns a condition function for edge routing | 🔨 YOU BUILD |
| `to_diagnostics` | Reads state, constructs input for diagnostics agent | 🔨 YOU BUILD |
| `monitor_only` | Terminal node for low-severity — yields output | 🔨 YOU BUILD |
| `comms` | Terminal node for critical/high — posts to Slack, yields | ✅ Provided |

### The Wiring (You'll Build This Too)

```python
workflow = (
    WorkflowBuilder(start_executor=ingest_alert)
    .add_edge(ingest_alert, triage_executor)
    .add_edge(triage_executor, parse_triage)
    .add_switch_case_edge_group(
        source=parse_triage,
        cases=[
            Case("critical", target=to_diagnostics, condition=get_severity_condition("critical")),
            Case("high", target=to_diagnostics, condition=get_severity_condition("high")),
        ],
        default=Default(target=monitor_only),
    )
    .add_edge(to_diagnostics, diagnostics_executor)
    .add_edge(diagnostics_executor, comms)
    .build()
)
```

---

## The Key Insight: Deterministic Routing

The `parse_triage` executor outputs a `RoutingDecision` dataclass:

```python
@dataclass
class RoutingDecision:
    severity: str       # "critical", "high", or "low"
    incident_id: str
    service: str
```

Edge conditions check this typed field:

```python
def get_severity_condition(target_severity: str):
    """Factory: returns a condition function that checks severity."""
    def condition(message) -> bool:
        if isinstance(message, RoutingDecision):
            return message.severity == target_severity
        return False
    return condition
```

This is NOT an LLM decision — it's a **deterministic check** on a typed field. The routing is 100% predictable based on the structured output from Challenge 1. This is why structured outputs matter.

---

## Getting Started

Open the notebook:

```
challenge-2/challenge.ipynb
```

The notebook provides:
- ✅ `ingest_alert`, `parse_triage`, and `comms` executors fully implemented
- ✅ `RoutingDecision` dataclass and state key constants
- 🔨 TODO: `get_severity_condition()` factory function
- 🔨 TODO: `to_diagnostics` executor (reads state, constructs AgentExecutorRequest)
- 🔨 TODO: `monitor_only` executor (terminal node, yields output)
- 🔨 TODO: Wire the full graph with `WorkflowBuilder`
- ✅ Two test runs: CRITICAL incident → full path, LOW incident → monitor only

---

## Success Criteria

- [ ] `get_severity_condition("critical")` returns a callable that matches `RoutingDecision(severity="critical")`
- [ ] `to_diagnostics` reads the incident from state and constructs a valid `AgentExecutorRequest`
- [ ] `monitor_only` calls `ctx.yield_output()` with a summary string
- [ ] Full workflow graph compiles without errors (`WorkflowBuilder.build()` succeeds)
- [ ] Running with CRITICAL incident → passes through diagnostics and comms (assertion passes)
- [ ] Running with LOW incident → goes to monitor_only, skips diagnostics (assertion passes)

---

## Tips & Common Mistakes

### For Beginners

- **Start with `get_severity_condition`** — it's the simplest TODO (a function that returns a function)
- **Edge conditions take ONE argument** — the message sent by the upstream executor
- **Always check `isinstance()` first** — the message might not be what you expect
- **Use the provided executors as templates** — copy the pattern, change the logic

### For Advanced Users

- `add_switch_case_edge_group` ensures exactly one path fires — if no Case matches, Default runs
- `AgentExecutorRequest(messages=[Message("user", contents=[Content(text="...")])], should_respond=True)` — that's the format
- State keys should be constants (avoid typo bugs): `STATE_INCIDENT = "incident"`
- `WorkflowBuilder` validates the graph at build time — unreachable nodes are an error
- In production, you'd use `ctx.yield_output()` to stream partial results to the caller

### Common Mistakes

| Mistake | Symptom | Fix |
|---------|---------|-----|
| Condition function returns wrong type | Edge never fires | Must return `bool`, not truthy |
| Forgot `ctx.send_message()` in executor | Downstream executor never runs | Edges only fire when upstream sends |
| Used wrong state key | `ctx.get_state()` returns `None` | Check spelling — use constants |
| Put `yield_output` in non-terminal node | Workflow ends early | Only terminal nodes should yield |
| Forgot `should_respond=True` in AgentExecutorRequest | Agent runs but response is lost | Always set this for nodes that need output |

---

## Deep Dive: Why Graphs Over Chains?

| Approach | Pros | Cons |
|----------|------|------|
| Manual chaining (if/else) | Simple, explicit | Unmaintainable at scale, no parallelism |
| LangChain LCEL | Composable pipes | Linear by default, routing is hacky |
| MAF WorkflowBuilder | DAG topology, typed routing, state mgmt, built-in HITL | Slightly more upfront design |

The graph approach means:
1. **Topology is declarative** — you can visualize it, test it, modify it
2. **Routing is deterministic** — based on typed data, not LLM guessing
3. **State is explicit** — no hidden globals or closure captures
4. **HITL is native** — the graph can pause mid-execution (Challenge 3)
5. **Composition works** — sub-workflows plug in as nodes

---

## ➡️ What's Next

Your workflow routes correctly, but it executes **autonomously**. The `restart_pod` tool runs without asking anyone. The remediation plan deploys without review.

In **Challenge 3**, you'll add **human-in-the-loop**: tool approval gates that pause execution, explicit `request_info()` that asks a human to review a plan, and retry loops for when automated verification fails.

[Challenge 3: Human-in-the-Loop →](../challenge-3/README.md)
