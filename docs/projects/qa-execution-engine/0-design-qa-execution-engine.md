# Design: QA Execution Engine

**Version:** 1.0
**Created:** 2025-12-20
**Status:** Complete (Audited)

---

## 1. Overview

Design for a 11-step workflow execution engine with quality gates that enforces design decisions during test automation code generation.

**Problem:** MCP tools generate code but lack enforcement. AI can skip steps, pass incomplete data, and ignore design decisions.

**Solution:** Quality gates (qg_*) at each step boundary that validate, block on failure, and persist state.

**Terminology:**
- **QA Guidance Layer** = Skill that guides AI (`.claude/skills/qa-guidance-layer/`)
- **QA Execution Engine** = Implementation (quality gates, state manager) - THIS PROJECT

---

## 2. Architecture

### 2.1 Four-Layer Model

```
┌─────────────────────────────────────────────────────────────────────┐
│ SKILL (qa-guidance-layer)                                            │
│ - Guides AI through workflow                                         │
│ - Step references in .claude/skills/qa-guidance-layer/references/   │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ QUALITY GATES (qg_*)                      ← QA EXECUTION ENGINE      │
│ - Validates input before operation                                   │
│ - Validates output after operation                                   │
│ - NEVER does work, only validates                                    │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ OPERATION TOOLS (Tool 1-6)                                           │
│ - Does the actual work                                               │
│ - Existing tools, unchanged                                          │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STATE MANAGER                             ← QA EXECUTION ENGINE      │
│ - Persists workflow state after each step                           │
│ - Called internally by gates/operations                             │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 State Save Rules

| Step Type | Who Saves | When |
|-----------|-----------|------|
| Steps 1-3 (no operation) | Quality gate | On PASS |
| Steps 4-9 (has operation) | Operation tool | On SUCCESS |
| AI | Never | AI cannot call state_manager |

---

## 3. 10-Step Workflow

| Step | Name | Tool | Gate | Gate Mode |
|------|------|------|------|-----------|
| 1 | Pre-flight Configuration | - | qg_preflight | POST-only |
| 2 | User Input | - | qg_user_input | POST-only |
| 3 | AI Processing | - | qg_ai_processing | POST-only |
| 4 | Generate Tests | Tool 1 | qg_test_scenarios | PRE+POST |
| 5 | Discover Elements | Tool 2 | qg_discovered_elements | PRE+POST |
| 6 | Generate POM | Tool 3 | qg_page_object | PRE+POST |
| 7 | Generate Task | Tool 4 | qg_task | PRE+POST |
| 8 | Generate Role | Tool 5 | qg_role | PRE+POST |
| 9 | Generate Test Runner | Tool 6 | qg_test_runner | PRE+POST |
| 10 | Save & Run | - | qg_save_run | PRE-only |

---

## 4. Step Template (7 Sections)

Each step follows this template:

| Section | Content |
|---------|---------|
| A. Identity & Flow | Step name, dependencies, input, output |
| B. Persona Map | User/AI/Tool actions |
| C. Skill Instruction | PRE-CHECK, ACTION, VALIDATE, RETRY |
| D. Tools | Operation tool, quality gate, gate mode |
| E. State Management | What saves, who saves, when, schema |
| F. Enforcement | DDs that apply, validation checks |
| G. Error Handling | Failure behavior, error templates |
| H. Data Contracts | (Tool steps) Input/output format with examples |

---

## 5. Design Decisions Enforced

### By Step

| Step | DDs Enforced |
|------|--------------|
| 1 | DD-24 (credentials), DD-28 (test data) |
| 2 | DD-01 (persona), DD-02 (URL) |
| 3 | DD-03 (metadata), DD-09 (expected_states) |
| 4 | DD-19 (tool import), DD-23 (BDD format) |
| 5 | DD-19, DD-20 (dynamic elements), DD-21 (AI-SDET), DD-24 |
| 6 | DD-09, DD-19, DD-25 (skeleton), DD-26 (contracts) |
| 7 | DD-12 (check existing), DD-19, DD-25, DD-26, DD-27 (no locators) |
| 8 | DD-12, DD-19, DD-25, DD-26 |
| 9 | DD-15 (POM assertions), DD-16 (paths), DD-17 (params), DD-18 (imports), DD-19, DD-25, DD-26 |
| 10 | DD-22 (stop-and-discuss) |

### Coverage Summary

- **Covered:** 20/20 DDs
- **All gaps fixed** during design audit

---

## 6. Tool Chain Data Contracts (DD-26)

### Step 4 → Step 5

```
Tool 1 outputs:
{
  "test_scenarios": [{
    "title": "test_valid_login",
    "given": "...",
    "when": "...",
    "then": "..."
  }]
}
```

### Step 5 → Step 6

```
Tool 2 outputs:
{
  "elements": [{
    "suggested_name": "EMAIL",
    "element_type": "inputs",
    "locator_id": "#email"
  }]
}

Pass elements[] directly to Tool 3.
```

### Step 6 → Step 7

```
Tool 3 outputs:
{
  "metadata": {
    "class_name": "LoginPage",
    "action_methods": [...],
    "state_methods": [...]
  }
}

Pass metadata as pom_metadata to Tool 4.
```

### Step 7 → Step 8

```
Tool 4 outputs:
{
  "metadata": {
    "class_name": "AuthTasks",
    "task_methods": [...]
  }
}

Pass metadata as task_metadata to Tool 5.
```

### Step 8 → Step 9

```
Tool 5 outputs:
{
  "metadata": {
    "class_name": "RegisteredUser",
    "workflow_methods": [...]
  }
}

Pass metadata as role_metadata to Tool 6.
Also pass pom_metadata from Step 6 for assertions.
```

---

## 7. Design Artifacts

### Step Definitions

| File | Purpose |
|------|---------|
| `.claude/skills/qa-guidance-layer/references/step-01.md` | Pre-flight Configuration |
| `.claude/skills/qa-guidance-layer/references/step-02.md` | User Input |
| `.claude/skills/qa-guidance-layer/references/step-03.md` | AI Processing |
| `.claude/skills/qa-guidance-layer/references/step-04.md` | Generate Tests (Tool 1) |
| `.claude/skills/qa-guidance-layer/references/step-05.md` | Discover Elements (Tool 2) |
| `.claude/skills/qa-guidance-layer/references/step-06.md` | Generate POM (Tool 3) |
| `.claude/skills/qa-guidance-layer/references/step-07.md` | Generate Task (Tool 4) |
| `.claude/skills/qa-guidance-layer/references/step-08.md` | Generate Role (Tool 5) |
| `.claude/skills/qa-guidance-layer/references/step-09.md` | Generate Test Runner (Tool 6) |
| `.claude/skills/qa-guidance-layer/references/step-10.md` | Save & Run |

### Architecture References

| File | Purpose |
|------|---------|
| `FRAMEWORK.md` Section 9 | QA-specific architecture |
| `.claude/skills/design-execution-engine/SKILL.md` | Meta-template (all verticals) |
| `.business/architecture/isagawa_internal_ruleset_factory.md` | Isagawa 5-layer model |

---

## 8. Design Audit Results

**Audit Date:** 2025-12-20

### DD Coverage

| Status | Count |
|--------|-------|
| ✅ Covered | 20/20 |
| ❌ Missing | 0 |

### Architecture Alignment

| Isagawa Layer | Our Implementation | Status |
|---------------|-------------------|--------|
| Domain Knowledge | User input | ✅ |
| Ruleset Creation | Step definitions, DDs | ✅ |
| Enforcement | Quality gates | ✅ |
| Execution | Operation tools | ✅ |
| Delivery | Step 10 (Save & Run) | ✅ (v1 scope) |

### Tool Contract Validation

| Status | Count |
|--------|-------|
| ✅ Match | 6/6 tool steps |
| ⚠️ Mismatch | 0 (fixed during audit) |

---

## 9. Design Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Gate implementation | MCP tools (qg_*) | AI can call them, validates at tool boundary |
| State persistence | JSON file | Simple, debuggable, no external deps |
| State save responsibility | Gate/Operation (not AI) | Can't be skipped |
| Retry policy | 3 attempts, then user | Consistent across all steps |
| Section H (Data Contracts) | Added to all tool steps | Prevents format mismatches |

---

## 10. Open Design Questions (Resolved)

| Question | Resolution |
|----------|------------|
| Who saves state? | Gates (Steps 1-3), Operations (Steps 4-9) |
| Where do data contracts live? | Section H in each step file |
| How to validate skeleton code? | DD-25 checks in POST-validation |
| Credential handling in Step 5? | Reads from Step 1 state, applies before discovery |

---

*Design complete. Proceed to PRD.*
