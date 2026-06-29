# Challenge 1 — Structured Agents with FoundryChatClient

**Expected Duration: 30 minutes**

---

## The Problem: Free Text Is Unreliable

Consider a typical "agent" response:

```
The severity appears to be critical. The service seems to be experiencing
memory issues. I'd recommend restarting the pod, but we should also check...
```

How do you use this downstream? You regex it. You pray. You get bitten when the LLM says "CRITICAL" one time and "Critical-level" the next.

**The fix:** Force the LLM to return a **Pydantic model** — a typed JSON object with defined fields, enums, and validation. If the output doesn't match the schema, it fails (and retries). No parsing, no ambiguity.

```python
# Instead of free text, you get:
TriageResult(
    severity="critical",               # Literal["critical", "high", "low"]
    incident_type="resource_exhaustion", # Constrained enum
    recurrence_count=3,                 # int, not "about 3 times"
    recommended_runbook="kb://oom-restart-procedure"
)
```

This is what makes multi-agent systems *possible* — when Agent A returns typed data, Agent B (or a workflow router) can make **deterministic decisions** based on exact field values.

---

## What You'll Learn

| Concept | What It Is | Why It Matters |
|---------|------------|----------------|
| **`Agent`** | MAF's core agent class | Wraps LLM + instructions + tools + output format |
| **`FoundryChatClient`** | Connection to Azure AI Foundry | Lightweight client — no server-side resource creation |
| **`response_format`** | Pydantic model as output schema | LLM is *forced* to return valid JSON matching this schema |
| **`@tool`** | Decorator for agent tools | Gives agents abilities (query metrics, check logs, etc.) |
| **`Field(description=...)`** | Pydantic field metadata | The LLM reads descriptions to understand what each field means |
| **`Literal[...]`** | Constrained string type | Limits LLM to exact allowed values (no creative spelling) |

### How Structured Output Works Under the Hood

```
┌─────────────────────────────────────────────────────────┐
│ 1. You define a Pydantic model (TriageResult)           │
│ 2. MAF converts it to JSON Schema                       │
│ 3. The schema is sent to GPT-4o as response_format      │
│ 4. GPT-4o is constrained to ONLY output valid JSON      │
│ 5. MAF validates the JSON against your Pydantic model   │
│ 6. You get a typed Python object — not a string         │
└─────────────────────────────────────────────────────────┘
```

This is NOT "prompt engineering" — it's a **hard constraint** at the model inference level. The LLM literally cannot return invalid output.

---

## What You'll Build

Four specialized agents, each with its own structured output model:

```
┌──────────────┐     ┌────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ Triage Agent │────→│ Diagnostics    │────→│ Remediation      │────→│ Verification     │
│              │     │ Agent          │     │ Planner Agent    │     │ Agent            │
├──────────────┤     ├────────────────┤     ├──────────────────┤     ├──────────────────┤
│ OUTPUT:      │     │ OUTPUT:        │     │ OUTPUT:          │     │ OUTPUT:          │
│ TriageResult │     │ Diagnostics-   │     │ RemediationPlan  │     │ Verification-    │
│  • severity  │     │ Result         │     │  • action        │     │ Result           │
│  • type      │     │  • root_cause  │     │  • target        │     │  • healthy       │
│  • runbook   │     │  • evidence    │     │  • risk_level    │     │  • tests_passed  │
│  • recurrence│     │  • confidence  │     │  • rollback      │     │  • latency_ms    │
└──────────────┘     └────────────────┘     └──────────────────┘     └──────────────────┘
```

| Agent | Pydantic Model | Key Fields | Tools Used |
|-------|----------------|------------|------------|
| **Triage** (provided as reference) | `TriageResult` | severity, incident_type, recurrence_count, recommended_runbook | `check_alert_history`, `get_runbook` |
| **Diagnostics** (you build) | `DiagnosticsResult` | root_cause, evidence, affected_services, confidence | `get_metrics`, `get_logs`, `check_dependencies` |
| **Remediation Planner** (you build) | `RemediationPlan` | action, target_service, risk_level, rollback_procedure, estimated_duration | None (pure reasoning) |
| **Verification** (you build) | `VerificationResult` | healthy, tests_passed, failed_checks, p99_latency_ms | `get_health_status`, `run_smoke_test` |

---

## The Pattern (Same for All 4 Agents)

Every agent follows this pattern:

```python
# 1. Define the output schema
class MyAgentOutput(BaseModel):
    field_a: Literal["option1", "option2"]
    field_b: str = Field(description="What this field represents")
    field_c: int = Field(description="Numeric metric", ge=0)

# 2. Create the agent
my_agent = Agent(
    client=client,                          # FoundryChatClient
    name="MyAgent",
    instructions="Your system prompt...",   # Tells the agent its role
    default_options=OpenAIChatOptions[Any](response_format=MyAgentOutput),
    tools=[tool_a, tool_b],                 # Optional: @tool functions
)

# 3. Run it
response = await my_agent.run("Input context here")

# 4. Parse the typed result
result = MyAgentOutput.model_validate_json(response.text)
print(result.field_a)  # Type-safe access, IDE autocomplete works
```

---

## Getting Started

Open the notebook:

```
challenge-1/challenge.ipynb
```

The notebook provides:
- ✅ Full `TriageResult` model and Triage Agent as reference
- ✅ Import boilerplate and client setup
- 🔨 TODO scaffolding for the 3 models and agents you'll build
- ✅ Validation cells that assert your outputs match the expected schema

---

## Success Criteria

- [ ] All 4 Pydantic models defined with proper field types and descriptions
- [ ] Triage Agent returns valid `TriageResult` — severity is one of `critical/high/low`
- [ ] Diagnostics Agent returns `DiagnosticsResult` with root_cause and evidence list
- [ ] Remediation Planner returns `RemediationPlan` with action, risk_level, and rollback
- [ ] Verification Agent returns `VerificationResult` with boolean healthy and test results
- [ ] All validation cells (`assert isinstance(...)`) pass without errors

---

## Tips & Common Mistakes

### For Beginners

- **Copy the Triage Agent pattern exactly** — change the model, instructions, and tools
- **Use `Field(description="...")`** — the LLM reads these to understand what to put in each field
- **`Literal["a", "b", "c"]`** constrains the LLM to only those exact values
- **Don't overthink the instructions** — be clear and direct, not creative

### For Advanced Users

- `response_format` uses OpenAI's structured output mode (not function calling)
- The JSON Schema is injected at inference time — it's not just a prompt trick
- `model_validate_json()` will raise `ValidationError` if the schema doesn't match
- You can nest Pydantic models (`List[Evidence]`, `Optional[Rollback]`, etc.)
- In Challenge 2, these typed outputs become the *routing signal* for the workflow graph

### Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting `response_format` | Agent returns free text → `model_validate_json` crashes |
| Using `str` instead of `Literal[...]` | LLM returns creative spellings → downstream routing breaks |
| Not adding `Field(description=...)` | LLM guesses what the field means → wrong values |
| Putting tools on the Remediation Planner | It should PLAN only — execution happens in Challenge 3 |

---

## Deep Dive: Why This Architecture?

**Why separate "planning" from "execution"?**

The Remediation Planner has **no tools**. It can't restart pods or scale services. It only *reasons* about what should be done and outputs a typed plan.

Why? Because in Challenge 3, a human will **review the plan before it executes**. If the planner could execute directly, there'd be no chance to intervene. This separation of concerns is a core production pattern:

```
Plan (safe, reversible)  →  Human Review  →  Execute (dangerous, irreversible)
```

---

## ➡️ What's Next

You've been manually passing typed outputs between agents like a relay race. But what if you have 3 severity levels that need 3 different execution paths? If/else spaghetti?

In **Challenge 2**, you'll wire these agents into a **workflow graph** with `WorkflowBuilder` — and use **switch-case routing** so different inputs automatically take different paths through the system.

[Challenge 2: Workflow Graphs →](../challenge-2/README.md)
