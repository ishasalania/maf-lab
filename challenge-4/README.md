# Challenge 4 — Advanced Composition (Bonus)

**Expected Duration: 20+ minutes (stretch goal for fast teams)**

## Choose Your Adventure

Pick one or more of these advanced MAF patterns to implement.
Each builds on the workflow from Challenges 1–3.

---

### Option A: Workflow-as-Agent

Wrap your entire incident response workflow so it behaves like a single `Agent`.
This enables **hierarchical composition** — a supervisor agent can invoke the incident
pipeline just like calling any other agent.

```python
from agent_framework import Agent

# Your workflow becomes callable as an agent:
incident_agent = workflow.as_agent(
    name="IncidentResponder",
    instructions="Handle production incidents autonomously.",
)

# Now it's just another agent — composable with other agents
response = await incident_agent.run("Payment API is returning 503s")
```

**Success Criteria:**
- [ ] Wrap the Challenge 2 workflow with `workflow.as_agent()`
- [ ] Call it like a regular agent with natural language input
- [ ] Verify it routes correctly based on what it detects

---

### Option B: Sub-Workflow Composition

Extract the remediation + verification loop into a **sub-workflow** that
the main workflow invokes as a node.

```python
from agent_framework import WorkflowBuilder

# Remediation sub-workflow (own graph)
remediation_subworkflow = (
    WorkflowBuilder(start_executor=plan_executor)
    .add_edge(plan_executor, execute_executor)
    .add_edge(execute_executor, verify_executor)
    .add_edge(verify_executor, retry_or_complete, condition=needs_retry)
    .build()
)

# Main workflow uses it as a node
main_workflow = (
    WorkflowBuilder(start_executor=ingest)
    .add_edge(ingest, triage_agent)
    .add_edge(triage_agent, diagnostics_agent)
    .add_edge(diagnostics_agent, remediation_subworkflow.as_executor())
    .build()
)
```

**Success Criteria:**
- [ ] Create a sub-workflow for remediation + verification
- [ ] Wire it into the main workflow graph
- [ ] Show that the sub-workflow can be reused independently

---

### Option C: OpenTelemetry Observability

Add distributed tracing so you can see exactly what each agent does,
how long tools take, and where failures occur.

```python
# MAF has built-in OpenTelemetry instrumentation
# Just configure the exporter:
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

# Now all agent calls and tool invocations are automatically traced!
```

**Success Criteria:**
- [ ] Configure OpenTelemetry with console exporter
- [ ] Run the workflow and observe spans for each agent and tool call
- [ ] Identify the slowest tool call from the trace data

---

### Option D: Parallel Fan-Out for Multi-Service Incidents

When incident #1 (payment-api) cascades to incident #2 (order-service),
investigate BOTH services in parallel using fan-out edges.

```python
# Fan-out: diagnostics runs concurrently for both services
workflow = (
    WorkflowBuilder(start_executor=detect_affected_services)
    .add_edge(detect_affected_services, diagnostics_payment, condition=affects_payment)
    .add_edge(detect_affected_services, diagnostics_orders, condition=affects_orders)
    .add_edge(diagnostics_payment, aggregate_results)
    .add_edge(diagnostics_orders, aggregate_results)
    .build()
)
```

**Success Criteria:**
- [ ] Detect that incident #1 cascades to order-service (from dependency data)
- [ ] Run diagnostics for both services concurrently
- [ ] Aggregate results into a single remediation plan

---

## Resources

- [MAF Workflows Samples](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows)
- [Sub-Workflow Composition](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows/composition)
- [Parallelism (Fan-Out/Fan-In)](https://github.com/microsoft/agent-framework/tree/main/python/samples/03-workflows/parallelism)
- [Observability](https://github.com/microsoft/agent-framework/tree/main/python/samples/02-agents/observability)
