# Challenge 1 — Structured Agents with FoundryChatClient

**Expected Duration: 30 minutes**

## Introduction

Most agent tutorials have agents return free text — then you regex-parse it and pray.
MAF agents return **Pydantic models** — typed, validated, machine-readable data that
downstream workflow nodes can consume reliably.

In this challenge you'll build agents that produce **structured outputs**, enabling
deterministic routing in Challenge 2.

## Key Concepts

| Concept | API | Why It Matters |
|---------|-----|----------------|
| Local agents | `Agent` + `FoundryChatClient` | Lightweight, no server resources needed |
| Structured outputs | `response_format=PydanticModel` | Typed data, no parsing errors |
| Tool integration | `@tool(approval_mode=...)` | Type-annotated functions as agent capabilities |
| Response validation | `Model.model_validate_json()` | Guaranteed schema compliance |

## What You'll Build

- **TriageResult** model (provided) — severity, recurrence, runbook info
- **DiagnosticsResult** model (YOUR TURN) — root cause, evidence, confidence
- **RemediationPlan** model (YOUR TURN) — action, target, risk, rollback
- **VerificationResult** model (YOUR TURN) — health status, test results

## Getting Started

Open the notebook:

```
challenge-1/challenge.ipynb
```

## Success Criteria

- [ ] All 4 Pydantic models defined with proper fields and types
- [ ] Triage Agent returns valid `TriageResult` (assertion passes)
- [ ] Diagnostics Agent returns valid `DiagnosticsResult` with evidence
- [ ] Remediation Planner returns valid `RemediationPlan` with rollback strategy
- [ ] Verification Agent returns valid `VerificationResult`
- [ ] All validation cells pass without errors

## Tips

- Study the Triage Agent reference implementation carefully — same pattern for all agents
- Use `Field(description=...)` for Pydantic fields — the LLM reads these descriptions
- `Literal["a", "b", "c"]` constrains the LLM to only those enum values
- Test each agent individually before moving to the next

## ➡️ Next Challenge

You've been manually passing typed outputs between agents. In Challenge 2,
you'll wire them into a **workflow graph** with conditional routing.

[Challenge 2: Workflow Graphs →](../challenge-2/README.md)
