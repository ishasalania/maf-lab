# Challenge 4 — Advanced Composition (Bonus)

**Expected Duration: 20+ minutes (stretch goal for fast teams)**

---

## Why This Challenge Exists

Challenges 1–3 gave you the core pattern: structured agents → workflow graphs → HITL. But real-world systems need more:

- **What if I have 50 workflows?** → Compose them hierarchically (workflow-as-agent)
- **What if remediation is reusable?** → Extract it as a sub-workflow
- **What if I need to debug latency?** → Add tracing (OpenTelemetry)
- **What if an incident affects 3 services?** → Fan-out investigation in parallel

These are the patterns that separate prototypes from production systems.

---

## Choose Your Adventure

Pick **one or more** of these advanced patterns. Each is independent — you don't need to do them in order.

| Option | Difficulty | What You'll Learn | Time |
|--------|-----------|-------------------|------|
| **A: Workflow-as-Agent** | ⭐⭐ | Hierarchical composition — workflows behave like agents | 10 min |
| **B: Sub-Workflow Composition** | ⭐⭐⭐ | Nested workflows as reusable graph nodes | 15 min |
| **C: OpenTelemetry** | ⭐ | Distributed tracing for every agent/tool call | 10 min |
| **D: Parallel Fan-Out** | ⭐⭐⭐ | Concurrent investigation of multiple services | 15 min |

---

## Option A: Workflow-as-Agent

### The Concept

Your entire incident response workflow from Challenges 1–3 becomes a **single callable agent**. A supervisor can invoke it alongside other "agents" without knowing it's actually a full graph internally.

This enables **hierarchical multi-agent systems** — a top-level orchestrator delegates to specialized sub-systems, each of which might be a single agent, a workflow, or another orchestrator.

```
┌─────────────────────────────────────────┐
│          Supervisor Agent                 │
│                                          │
│  "Handle this alert"                     │
│       │                                  │
│       ▼                                  │
│  ┌──────────────┐   ┌───────────────┐   │
│  │ Incident     │   │ Capacity      │   │
│  │ Workflow     │   │ Planning      │   │
│  │ (as agent)   │   │ Agent         │   │
│  └──────────────┘   └───────────────┘   │
│       ↑ internally:                      │
│       │ triage → route → diagnose → fix  │
└─────────────────────────────────────────┘
```

### Implementation

```python
from agent_framework import Agent

# Your workflow from Challenge 2 becomes callable as a single agent:
incident_agent = workflow.as_agent(
    name="IncidentResponder",
    instructions="Handle production incidents. Triage, diagnose, and remediate.",
)

# Now it's just another agent — composable with other agents
response = await incident_agent.run("Payment API is returning 503s, P99 > 30s")
print(response.text)  # Full workflow ran internally — you just see the output
```

### Why This Matters

- A supervisor doesn't need to know implementation details
- You can swap implementations (simple agent vs full workflow) without changing callers
- Teams can own their workflows independently — expose them as agents to other teams

### Success Criteria

- [ ] Wrap the Challenge 2 workflow with `workflow.as_agent()`
- [ ] Call it like a regular agent with natural language input
- [ ] Verify it routes correctly (CRITICAL vs LOW) without the caller knowing about routing

---

## Option B: Sub-Workflow Composition

### The Concept

Extract remediation + verification into a **reusable sub-workflow** that the main graph invokes as a node. Like calling a function from another function — but for workflows.

```
Main Workflow:
  ingest → triage → switch → diagnostics → [remediation_subworkflow] → comms

Remediation Sub-Workflow (reusable!):
  plan → approve → execute → verify → (retry or complete)
```

### Implementation

```python
from agent_framework import WorkflowBuilder

# 1. Build the sub-workflow independently
remediation_subworkflow = (
    WorkflowBuilder(start_executor=plan_executor)
    .add_edge(plan_executor, approve_executor)
    .add_edge(approve_executor, execute_executor)
    .add_edge(execute_executor, verify_executor)
    .add_edge(verify_executor, retry_or_complete, condition=needs_retry)
    .build()
)

# 2. Plug it into the main workflow as a single node
main_workflow = (
    WorkflowBuilder(start_executor=ingest)
    .add_edge(ingest, triage_agent)
    .add_edge(triage_agent, diagnostics_agent)
    .add_edge(diagnostics_agent, remediation_subworkflow.as_executor())
    .add_edge(remediation_subworkflow.as_executor(), comms)
    .build()
)
```

### Why This Matters

- **Reusability** — same remediation workflow for incidents, deployments, scaling events
- **Testability** — test the sub-workflow in isolation
- **Separation of concerns** — different teams own different sub-workflows
- **Replaceability** — swap out the remediation strategy without touching the main graph

### Success Criteria

- [ ] Create a standalone sub-workflow for remediation + verification
- [ ] Wire it into the main workflow graph as a single executor
- [ ] Run the sub-workflow independently to prove it works in isolation
- [ ] Run the full workflow end-to-end with the sub-workflow embedded

---

## Option C: OpenTelemetry Observability

### The Concept

MAF instruments all agent calls and tool invocations with OpenTelemetry spans automatically. You just configure an exporter and get full distributed tracing — see which agent took longest, which tool failed, and where the bottleneck is.

```
Trace: handle_incident (14.2s)
├── Span: ingest_alert (2ms)
├── Span: triage_agent (3.1s)
│   ├── Span: LLM call gpt-4o (2.8s)
│   ├── Span: tool:check_alert_history (120ms)
│   └── Span: tool:get_runbook (95ms)
├── Span: parse_triage (1ms)
├── Span: to_diagnostics (1ms)
├── Span: diagnostics_agent (4.8s)
│   ├── Span: LLM call gpt-4o (3.2s)
│   ├── Span: tool:get_metrics (340ms)
│   └── Span: tool:get_logs (280ms)
└── Span: comms (1.2s)
    └── Span: tool:post_to_slack (890ms)
```

### Implementation

```python
# MAF has built-in OpenTelemetry instrumentation — just configure the exporter
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Set up tracing (one time, at app startup)
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

# Now run your workflow — all spans are captured automatically
events = await workflow.run(input_message)

# Every agent call, tool invocation, and executor will appear as spans!
```

### Why This Matters

- **Debug latency** — instantly see which tool/agent is the bottleneck
- **Audit trail** — every decision the system made is recorded
- **Error diagnosis** — see exactly where a workflow failed
- **Production monitoring** — export to Jaeger/Azure Monitor for dashboards

### Success Criteria

- [ ] Configure OpenTelemetry with `ConsoleSpanExporter`
- [ ] Run the full Challenge 2 workflow and observe spans in console
- [ ] Identify the slowest operation from the trace output
- [ ] (Bonus) Export to Azure Monitor with `AzureMonitorTraceExporter`

---

## Option D: Parallel Fan-Out for Multi-Service Incidents

### The Concept

Incident #1 (payment-api OOMKilled) cascades to incident #2 (order-service errors) because order-service depends on payment-api. Instead of investigating sequentially, fan-out to **diagnose both services concurrently**.

```
                       ┌─── diagnostics_payment ───┐
detect_affected  ─────→│                           ├──→ aggregate_results → remediate
  services             └─── diagnostics_orders  ───┘
                       (runs in parallel!)
```

### Implementation

```python
# Fan-out: diagnostics runs concurrently for both affected services
workflow = (
    WorkflowBuilder(start_executor=detect_affected_services)
    .add_edge(detect_affected_services, diagnostics_payment, condition=affects_payment)
    .add_edge(detect_affected_services, diagnostics_orders, condition=affects_orders)
    # Fan-in: both converge to aggregation
    .add_edge(diagnostics_payment, aggregate_results)
    .add_edge(diagnostics_orders, aggregate_results)
    .add_edge(aggregate_results, remediate)
    .build()
)
```

### Why This Matters

- **Speed** — parallel investigation is 2x faster (or more for N services)
- **Completeness** — you see the full blast radius before remediating
- **Correlation** — aggregate_results can identify the *root* cause vs symptoms
- **Real-world** — cascading failures are the #1 source of production outages

### Success Criteria

- [ ] Detect that incident #1 cascades to order-service (from `check_dependencies` tool data)
- [ ] Run diagnostics for both services concurrently (parallel edges)
- [ ] Aggregate results into a single, unified remediation plan
- [ ] Prove that fixing the root cause (payment-api) resolves the symptom (order-service)

---

## General Tips for All Options

- The [solution/full_workflow.py](../solution/full_workflow.py) has patterns you can reference
- Don't try to be perfect — get a working prototype, then refine
- Ask your coach if you're stuck for more than 5 minutes on any option
- You can combine options (e.g., A + C: workflow-as-agent with tracing)

---

## Resources

- [MAF Workflows Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows)
- [Sub-Workflow Composition](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows/composition)
- [Parallelism (Fan-Out/Fan-In)](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows/parallelism)
- [Observability](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/observability)

---

## ➡️ Wrap-Up

Congratulations! You've built a production-grade multi-agent system with:

- ✅ Typed structured outputs (no free text parsing)
- ✅ Workflow graphs with deterministic routing
- ✅ Human-in-the-loop for safe operations
- ✅ Retry and escalation for resilience
- ✅ (Bonus) Composition, observability, or parallelism

**Take home:** The `maf-lab` repo is yours. Fork it, extend it, adapt it to your own use cases. The patterns here work for any domain — not just incident response.
