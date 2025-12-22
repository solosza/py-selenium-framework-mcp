# Step 10: Save & Run

**Purpose:** Save all generated files to disk and execute the test.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 10 - Save & Run |
| **Dependencies** | Step 9 complete (all code generated: POM, Task, Role, Test) |
| **Input** | All generated code from Steps 6-9 |
| **Output** | Files saved, test execution result |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | Confirms ready to run, reviews results, decides on failures |
| **AI** | Saves files to correct locations, runs pytest, reports results, follows DD-22 on failure |
| **Tool** | `qg_save_run` validates all code present, `run_test` executes pytest (optional) |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 9 complete (test_code exist in state)
- Verify all code from Steps 6-9 is present and complete

ACTION:
- CALL qg_save_run (PRE-VALIDATE all code present)
- SAVE files to disk:
  - POM → framework/pages/{domain}/{page_name}.py
  - Task → framework/tasks/{domain}/{task_name}.py
  - Role → framework/roles/{role_name}.py
  - Test → tests/{domain}/test_{intent}.py
- ASK user: "Ready to run the test?"
- IF yes: RUN pytest
- REPORT results

VALIDATE:
- PRE: All code present, no skeleton code
- POST: Files saved successfully, test executed

ON TEST FAILURE (DD-22):
- STOP → REPORT failure details
- DISCUSS with user before any fix attempt
- USER DECIDES: fix, restart, or abort
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | File I/O (Write tool), `run_test` (optional) |
| **Quality Gate** | `qg_save_run` |
| **Gate Mode** | PRE-only (validates all code ready before save) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `files_saved`, `test_result` |
| **Who Saves** | AI (after successful file writes) |
| **When Saved** | After all files written and test executed |
| **State Schema** | See below |

```json
{
  "step": 10,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "files_saved": [
      "framework/pages/auth/login_page.py",
      "framework/tasks/auth/auth_tasks.py",
      "framework/roles/registered_user.py",
      "tests/auth/test_login.py"
    ],
    "test_result": {
      "executed": true,
      "passed": true,
      "duration": "2.3s",
      "output": "1 passed in 2.3s"
    }
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-22 (stop-and-discuss on failure) |
| **Gate Enforcement** | **BLOCKED: Cannot save until all code validated** |

**PRE-Validation Checks:**

| Check | Rule |
|-------|------|
| `pom_code` | Present from Step 6 |
| `task_code` | Present from Step 7 |
| `role_code` | Present from Step 8 |
| `test_code` | Present from Step 9 |
| All code | No skeleton indicators (DD-25 final check) |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| Missing code | Go back to relevant step (6, 7, 8, or 9) |
| File write error | Report error, retry or ask user |
| Test fails | DD-22: STOP → REPORT → DISCUSS → USER DECIDES |

**Known Defects:** None (final step)

**Test Failure Protocol (DD-22):**

```
"Test execution failed.

Test: test_valid_login
Error:
[show error message and stack trace]

Possible causes:
1. Element locator incorrect
2. Timing issue (element not ready)
3. Page state not as expected
4. Framework bug

How should we proceed?
1. Investigate failure - I'll analyze the error
2. Restart from Step 1 - Fresh generation
3. Manual fix - You fix the code
4. Abort - Stop workflow"
```

**CRITICAL:** Never attempt fixes without user consultation. DD-22 is enforced strictly.

---

## File Save Locations

| Code Type | Location Pattern |
|-----------|------------------|
| POM | `framework/pages/{domain}/{page_name}.py` |
| Task | `framework/tasks/{domain}/{task_name}.py` |
| Role | `framework/roles/{role_name}.py` |
| Test | `tests/{domain}/test_{intent}.py` |

**Example for login test:**
```
framework/pages/auth/login_page.py
framework/tasks/auth/auth_tasks.py
framework/roles/registered_user.py
tests/auth/test_login.py
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 10: SAVE & RUN                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 9 complete?      │
                         │  All code present?     │
                         └────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  YES     │            │  NO      │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
┌─────────────────────────────────┐     ┌─────────────────┐
│  QUALITY GATE: qg_save_run      │     │  BLOCKED        │
│  - All code present             │     │  Go to missing  │
│  - No skeleton code             │     │  step           │
└─────────────────────────────────┘     └─────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  SAVE FILES:        │
              │  - POM              │
              │  - Task             │
              │  - Role             │
              │  - Test             │
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  ASK USER:          │
              │  "Ready to run?"    │
              └─────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
    ┌──────────┐                  ┌──────────┐
    │  YES     │                  │  NO      │
    └────┬─────┘                  └────┬─────┘
         │                             │
         ▼                             ▼
    ┌──────────────┐             ┌──────────────┐
    │  RUN PYTEST  │             │  WORKFLOW    │
    │              │             │  COMPLETE    │
    └──────────────┘             │  (no run)    │
         │                       └──────────────┘
         │
         ▼
    ┌──────────────────────────────────────────┐
    │  TEST RESULT                              │
    └──────────────────────────────────────────┘
         │
         ├── PASS ──► WORKFLOW COMPLETE (success)
         │
         └── FAIL ──► DD-22: STOP → REPORT → DISCUSS
                            │
                            ▼
                      ┌──────────────┐
                      │  USER        │
                      │  DECIDES     │
                      │              │
                      │  1. Investigate
                      │  2. Restart  │
                      │  3. Manual   │
                      │  4. Abort    │
                      └──────────────┘
```

---

## Workflow Complete

Upon successful completion:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW COMPLETE                                         │
│                                                                              │
│  Files generated:                                                           │
│  ✓ framework/pages/auth/login_page.py                                       │
│  ✓ framework/tasks/auth/auth_tasks.py                                       │
│  ✓ framework/roles/registered_user.py                                       │
│  ✓ tests/auth/test_login.py                                                 │
│                                                                              │
│  Test result: PASSED (1 passed in 2.3s)                                     │
│                                                                              │
│  State saved to: mcp_server/state/workflow_state.json                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-10-01 | Primary: code from input_data; Fallback: code from state (resume scenario) | Normal flow passes code in input_data; resume/recovery reads from state | `validate_pre()` |
| IC-10-02 | PRE-only mode (no POST validation) | Gate validates before save; no output to validate after | `validate()` |
| IC-10-03 | Final skeleton sweep on ALL 4 layers (POM, Task, Role, Test) | Last line of defense before files hit disk (DD-25) | `validate_pre()` |
| IC-10-04 | Each code block validated independently; first failure stops validation | Fail-fast with clear error pointing to specific layer | `validate_pre()` |
| IC-10-05 | Missing code returns step hint (e.g., "Go back to Step 6 for POM") | Actionable fix guidance | `validate_pre()` |

**Date Added:** 2025-12-21
**Task Reference:** Task 13.0 (qg_save_run)

---

*End of 10-Step Workflow*
