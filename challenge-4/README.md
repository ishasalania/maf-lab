# Challenge 4 — Advanced Patterns (Bonus)

**Expected Duration: 20+ minutes (stretch goal for fast teams)**

## Introduction

You've built a complete multi-agent incident response system. Now go further with production-grade patterns that make the system safer, observable, and more intelligent.

Pick **one or more** of the challenges below — they're independent.

---

## Option A: Human-in-the-Loop Approval Gate

**Problem**: The remediation agent can restart pods and toggle flags autonomously. In production, some actions (like scaling to 10x replicas, or toggling a billing flag) need human approval.

**Your Task**: Add an approval gate before destructive actions.

### Requirements
1. Create a `requires_approval(action, severity)` function that returns `True` for high-risk actions
2. Modify the remediation executor to pause and ask for confirmation when approval is needed
3. If denied, route to `escalate_to_human` instead

### Starter Code
```python
def requires_approval(action: str, service: str) -> bool:
    """Returns True if this action needs human approval."""
    HIGH_RISK_SERVICES = ["payment-api", "auth-service"]
    HIGH_RISK_ACTIONS = ["scale_service", "toggle_feature_flag"]
    
    # TODO: Your logic here
    # Hint: restart is usually safe, but scaling payment-api might not be
    pass
```

### Success Criteria
- [ ] `restart_pod` on non-critical services proceeds automatically
- [ ] `scale_service` on payment-api triggers approval prompt
- [ ] Denied actions route to `escalate_to_human`

---

## Option B: Structured Output Parsing

**Problem**: Agents return free-form text. Parsing "VERDICT: RESOLVED" with string matching is fragile. What if the agent says "partially resolved" or "Resolution confirmed"?

**Your Task**: Use structured output to get reliable, parseable responses.

### Requirements
1. Define a Pydantic model for each agent's output
2. Use `response_format` parameter to force structured JSON responses
3. Parse the output directly into your model

### Starter Code
```python
from pydantic import BaseModel, Field

class TriageOutput(BaseModel):
    severity: str = Field(description="critical, high, medium, or low")
    is_recurring: bool = Field(description="Whether this alert has fired before")
    auto_remediation_allowed: bool
    recommended_action: str
    incident_type: str = Field(description="For runbook lookup, e.g., high_latency")

class VerificationOutput(BaseModel):
    health_status: str
    smoke_test_results: list[str]
    verdict: str = Field(description="RESOLVED or FAILED")
    confidence: float = Field(description="0.0 to 1.0")
```

### Success Criteria
- [ ] Triage returns parseable JSON matching `TriageOutput`
- [ ] Verification verdict is a clean enum, not free text
- [ ] Routing logic uses `output.verdict == "RESOLVED"` instead of string search

---

## Option C: Observability with OpenTelemetry

**Problem**: When the workflow runs at 3 AM, you need to see what happened — which tools were called, how long each stage took, what the agents decided.

**Your Task**: Add tracing spans to each executor.

### Requirements
1. Create a span per executor with attributes (service, stage, duration)
2. Log tool calls as child spans
3. Record the final verdict and resolution time

### Starter Code
```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

# Setup
provider = TracerProvider()
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer("incident-response")

@executor
async def triage_executor(ctx: WorkflowContext[IncidentState]) -> str:
    with tracer.start_as_current_span("triage") as span:
        span.set_attribute("service", ctx.state.alert_service)
        span.set_attribute("severity", ctx.state.alert_severity)
        # ... your existing code ...
        span.set_attribute("result_length", len(ctx.state.triage_result))
    return "diagnostics"
```

### Success Criteria
- [ ] Console shows trace spans for each workflow stage
- [ ] Each span has service name, duration, and result summary
- [ ] You can identify which stage took longest

---

## Option D: Multi-Incident Parallel Processing

**Problem**: Three alerts fire simultaneously. The current workflow handles them sequentially. Can you process multiple incidents in parallel?

**Your Task**: Run the workflow on all 3 incidents concurrently.

### Requirements
1. Use `asyncio.gather` to run 3 workflow instances in parallel
2. Each instance has its own `IncidentState`
3. Show a summary table of all 3 resolutions

### Starter Code
```python
import asyncio

async def handle_all_incidents():
    states = [
        IncidentState(
            alert_title=inc["title"],
            alert_service=inc["service"],
            alert_severity=inc["severity"],
            alert_description=inc["description"],
        )
        for inc in incidents
    ]
    
    results = await asyncio.gather(*[
        workflow.run(state=state) for state in states
    ])
    
    # Print summary table
    print(f"\n{'Service':<25} {'Resolved':<10} {'Retries':<10}")
    print("-" * 45)
    for result in results:
        print(f"{result.alert_service:<25} {'✅' if result.is_resolved else '❌':<10} {result.retry_count:<10}")
```

### Success Criteria
- [ ] All 3 incidents processed (not just 1)
- [ ] Each resolved with different actions
- [ ] Total time less than 3x single-incident time (proves parallelism)

---

## Learning Resources

| Topic | Link |
|-------|------|
| Human-in-the-loop patterns | [MAF Middleware docs](https://github.com/microsoft/agent-framework) |
| Structured outputs | [OpenAI Structured Outputs](https://platform.openai.com/docs/guides/structured-outputs) |
| OpenTelemetry Python | [OTel Python SDK](https://opentelemetry.io/docs/languages/python/) |
| Async patterns | [Python asyncio docs](https://docs.python.org/3/library/asyncio.html) |

---

## 🎉 You've Gone Beyond the Workshop!

These patterns separate toy demos from production systems. If you implemented any of these, you understand multi-agent engineering at a professional level.
