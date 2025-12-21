# QA Guidance Layer

**Purpose:** Guide AI through the 10-step QA test generation workflow with enforced quality gates.

**Applies to:** QA test automation generation using MCP tools.

**Part of:** QA Execution Engine (guidance layer + quality gates + operations + state)

---

## When to Use This Skill

Use when:
- User wants to generate test automation code
- User provides a user story or test requirement
- Starting the 10-step workflow from Step 1

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         10-STEP QA WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  Step 1: Pre-flight Config    ──► credential_strategy, test_data_location
      │
      ▼
  Step 2: User Input           ──► persona, URL, role_name, domain
      │
      ▼
  Step 3: AI Processing        ──► bdd_scenarios, expected_states, intent
      │
      ▼
  Step 4: Generate Tests       ──► test_scenarios (Tool 1)
      │
      ▼
  Step 5: Discover Elements    ──► discovered_elements (Tool 2)
      │
      ▼
  Step 6: Generate POM         ──► page_object_code (Tool 3)
      │
      ▼
  Step 7: Generate Task        ──► task_code (Tool 4)
      │
      ▼
  Step 8: Generate Role        ──► role_code (Tool 5)
      │
      ▼
  Step 9: Generate Test Runner ──► test_code (Tool 6)
      │
      ▼
  Step 10: Save & Run          ──► files saved, test executed
```

---

## Step References

| Step | Reference | Description |
|------|-----------|-------------|
| 1 | `references/step-01.md` | Pre-flight Configuration |
| 2 | `references/step-02.md` | User Input |
| 3 | `references/step-03.md` | AI Processing |
| 4 | `references/step-04.md` | Generate Tests |
| 5 | `references/step-05.md` | Discover Elements |
| 6 | `references/step-06.md` | Generate POM |
| 7 | `references/step-07.md` | Generate Task |
| 8 | `references/step-08.md` | Generate Role |
| 9 | `references/step-09.md` | Generate Test Runner |
| 10 | `references/step-10.md` | Save & Run |

---

## Execution Rules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CRITICAL RULES                                     │
└─────────────────────────────────────────────────────────────────────────────┘

1. SEQUENTIAL EXECUTION
   - Must complete Step N before Step N+1
   - Quality gate must PASS before proceeding
   - No skipping steps

2. GATE ENFORCEMENT
   - Each step has a quality gate (qg_*)
   - Gate validates input AND output
   - BLOCKED until gate passes

3. STATE PERSISTENCE
   - Each step saves state on success
   - State enables resume on failure
   - Accumulated data flows through steps

4. STOP-AND-DISCUSS (DD-22)
   - On ANY blocker: STOP → REPORT → DISCUSS → PROCEED
   - Never loop through fixes without user
   - User decides resolution path
```

---

## Flow Per Step

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  READ step reference                                                         │
│      │                                                                       │
│      ▼                                                                       │
│  PREPARE input (from previous step or user)                                  │
│      │                                                                       │
│      ▼                                                                       │
│  CALL qg_* to validate input                                                 │
│      │                                                                       │
│      ├── FAIL ──► STOP → REPORT → ASK USER → RETRY                          │
│      │                                                                       │
│      ▼ PASS                                                                  │
│  CALL operation tool (if applicable)                                         │
│      │                                                                       │
│      ▼                                                                       │
│  STATE saved automatically                                                   │
│      │                                                                       │
│      ▼                                                                       │
│  PROCEED to next step                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `FRAMEWORK.md` Section 9 | Full step definitions with examples |
| `design-execution-engine/` | Meta-skill for engine design patterns |
| `CLAUDE.md` | Quick reference and DDs |

---

*Living document - update as workflow evolves.*
