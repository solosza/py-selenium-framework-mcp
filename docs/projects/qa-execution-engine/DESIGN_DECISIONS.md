# Design Decisions: QA Execution Engine

Project-specific architectural decisions for the QA Execution Engine.

**Note:** Process/dev workflow decisions are in `docs/PROCESS_DECISIONS.md` (PD-XXX).

---

## DD-QEE-001: State Saved by Gates, Not Operations

**Date:** 2025-12-20
**Component:** State Manager / Gate Architecture

**Context:**
Design question: Should operation tools (Tool 1-6) save state, or should quality gates save state after validation passes?

**Decision:**
**Gates save state** after validation passes. Operations return data, gates validate and persist.

**Rationale:**
- Can't trust AI to call save_state() after operations
- Gates are the enforcement points
- State only saved when quality gate passes
- Prevents invalid state from being persisted

**Implementation:**
```python
# Gate pattern (Steps 4-9):
def qg_page_object(pom_output):
    # Validate
    if has_skeleton_code(pom_output):
        return {"status": "fail", "error": "..."}

    # Save state ONLY after validation passes
    state_manager.save(step=6, data=pom_output)
    return {"status": "pass"}
```

**Alternatives Considered:**
- Operations save state: Can be bypassed, no validation guarantee
- Separate save_state tool: AI can forget to call it

**Tradeoffs Accepted:**
- Gates have more responsibility (validation + persistence)
- Must ensure all gates call state_manager correctly

---

## DD-QEE-002: 10-Step Workflow with Quality Gates

**Date:** 2025-12-20
**Component:** Workflow Architecture

**Context:**
Original 9-step workflow lacked explicit quality gates. Steps could be skipped or executed out of order.

**Decision:**
Expand to **11-step workflow** with quality gates at every step:
- Steps 1-3: Configuration (POST-only gates)
- Steps 4-9: Operations (PRE+POST gates)
- Step 10: Final validation (PRE-only gate)

**Rationale:**
- Explicit gates at each step = enforceable contracts
- PRE gates block execution if previous step incomplete
- POST gates validate output before saving state
- Clear separation: config → operations → save/run

**Implementation:**
See `FRAMEWORK.md` Section 9 and step definition files in `.claude/skills/qa-management-layer/references/`.

**Alternatives Considered:**
- Keep 9 steps, add inline validation: Less clear separation
- Fewer steps with more per step: Harder to debug failures

**Tradeoffs Accepted:**
- More gates to implement and maintain
- More complex workflow orchestration

---

## DD-QEE-003: Gate Return Format

**Date:** 2025-12-20
**Component:** Gate API

**Context:**
Need consistent return format from all quality gates for AI to interpret results.

**Decision:**
All gates return JSON with standard structure:

```json
// Pass
{"status": "pass"}

// Fail
{"status": "fail", "error": "description", "fix_hint": "how to fix"}
```

**Rationale:**
- Consistent format = predictable handling
- `fix_hint` helps AI self-correct
- Simple boolean-like status for branching

**Implementation:**
BaseGate class provides `pass_response()` and `fail_response()` helpers.

---

## Index

| DD | Title | Component |
|----|-------|-----------|
| DD-QEE-001 | State Saved by Gates, Not Operations | State Manager |
| DD-QEE-002 | 10-Step Workflow with Quality Gates | Workflow Architecture |
| DD-QEE-003 | Gate Return Format | Gate API |

---

## Related

- Process decisions: `docs/PROCESS_DECISIONS.md`
- MCP tool chain DDs: `FRAMEWORK.md` (DD-01 to DD-28)
