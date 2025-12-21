# Step 7: Tool 4 - Generate Task

**Purpose:** Generate Task class code that orchestrates POM methods for domain operations.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 7 - Generate Task (Tool 4) |
| **Dependencies** | Step 6 complete (pom_code, pom_metadata exist) |
| **Input** | `pom_metadata` from Step 6, `domain` from Step 2, `intent` from Step 3 |
| **Output** | `task_code`, `task_metadata` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | None (unless AI fails 3 times, then user decides resolution) |
| **AI** | Checks existing tasks (DD-12), validates code completeness (DD-25), ensures NO return values |
| **Tool** | `qg_task` validates input/output, `generate_task` generates Task code, operation saves state on SUCCESS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 6 complete (pom_metadata exist in state)
- DD-12: Check if Task class already exists for this domain
  - IF EXISTS: Extend with new methods, don't create new class
  - IF NOT EXISTS: Generate new Task class

ACTION:
- CALL qg_task (PRE-VALIDATE)
- CALL generate_task (OPERATION)
- CALL qg_task (POST-VALIDATE)

VALIDATE (DD-25 - Skeleton Code Quality Gate):
- POST: Verify NO skeleton code indicators
- POST: Verify @autologger.automation_logger("Task") decorator
- POST: Verify NO return values (tasks return None)
- POST: Verify POM composition in constructor

RETRY:
- If POST-VALIDATE fails: AI completes the code (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_task` |
| **Quality Gate** | `qg_task` |
| **Gate Mode** | PRE+POST (validates metadata before, code quality after) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `task_code`, `task_metadata` (class name, methods, composed POMs) |
| **Who Saves** | Operation tool (`generate_task`) |
| **When Saved** | On operation SUCCESS (after POST-VALIDATE passes) |
| **State Schema** | See below |

```json
{
  "step": 7,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "task_code": "class AuthTasks:\n    @autologger.automation_logger('Task')\n    def log_in(self, email, password):\n        ...",
    "task_metadata": {
      "class_name": "AuthTasks",
      "file_path": "framework/tasks/auth/auth_tasks.py",
      "is_new": true,
      "methods": ["log_in", "log_out"],
      "composed_poms": ["LoginPage"]
    }
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-12 (check existing), DD-19 (tool import), DD-25 (no skeleton), DD-26 (data contracts), DD-27 (no locators in Task), framework architecture (no return values) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 8 until Task code complete** |

**PRE-Validation Checks:**

| Check | Rule |
|-------|------|
| `pom_metadata` | Present from Step 6 |
| `domain` | Valid domain (auth, catalog, cart, checkout) |
| Existing check (DD-12) | Scanned framework/tasks/ for existing class |

**POST-Validation Checks (DD-25, DD-27):**

| Check | Rule |
|-------|------|
| Constructor | Composes WebInterface and POM(s) |
| Decorator | `@autologger.automation_logger("Task")` on each method |
| Return value | Methods return None (not self, not values) |
| No skeleton | No `pass`, no `# Add...`, no empty bodies |
| Method body | Uses POM methods in fluent chain |
| **DD-27: No locators** | NO `By.` imports, NO `(By.CSS_SELECTOR, ...)` tuples, NO `driver.find_element()` |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| Missing POM metadata | Go back to Step 6 |
| Skeleton code detected | AI completes the code (max 3) |
| Return value found | AI removes return statement |
| After 3 total failures | STOP → REPORT → USER DECIDES |

**Known Defects:** Tools sometimes generate return values (violates framework pattern)

**Error Message Template (After 3 Failures):**

```
"I've attempted 3 times and cannot generate complete Task code.

Issues found:
[list what's wrong - skeleton, return values, missing decorator]

How should we proceed?
1. Re-generate POM - Go back to Step 6
2. Manual Task - You provide the code
3. Abort workflow - Stop and log issue"
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 7: TOOL 4 - GENERATE TASK                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 6 complete?      │
                         └────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  YES     │            │  NO      │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
              ┌─────────────────────┐     ┌─────────────────┐
              │  DD-12: Check if    │     │  BLOCKED        │
              │  Task already       │     │  Go to Step 6   │
              │  exists             │     └─────────────────┘
              └─────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
    ┌──────────┐                  ┌──────────┐
    │  EXISTS  │                  │  NEW     │
    └────┬─────┘                  └────┬─────┘
         │                             │
         ▼                             │
    ┌──────────────┐                   │
    │  EXTEND      │                   │
    │  existing    │                   │
    └──────────────┘                   │
         │                             │
         └──────────────┬──────────────┘
                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_task (PRE-VALIDATE)                                        │
│  - Validates inputs present                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  PASS    │            │  FAIL    │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
              ┌─────────────────────┐     ┌─────────────────┐
              │  OPERATION:         │     │  Go to Step 6   │
              │  generate_task      │     └─────────────────┘
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_task (POST-VALIDATE)                                       │
│  - DD-25: No skeleton code                                                  │
│  - No return values, decorator present                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  PASS    │            │  FAIL    │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
              ┌─────────────────────┐  ┌─────────────────────┐
              │  STATE SAVED        │  │  AI COMPLETES CODE  │
              │  (by operation)     │  │  (max 3 attempts)   │
              └─────────────────────┘  └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 8  │
              └─────────────────────┘
```

---

## H. Tool Chain Data Contracts (DD-26)

**Input Contract (from Step 6):**

```python
# CORRECT - Pass Tool 3 metadata:
arguments = {
    "task_name": "AuthTasks",
    "workflow": "auth",
    "pom_metadata": tool_3_result["metadata"],  # From Tool 3
    "workflow_description": "Authentication operations"
}
```

**WRONG - Do NOT omit pom_metadata:**
```python
# WRONG - missing pom_metadata produces skeleton:
arguments = {
    "task_name": "AuthTasks",
    "workflow_description": "..."  # Text only = skeleton output
}
```

**Output Contract (Tool 4 provides for Step 8):**

```json
{
  "code": "class AuthTasks:\n    @autologger...\n    def log_in(self, email, password):...",
  "metadata": {
    "class_name": "AuthTasks",
    "import_path": "tasks.auth.auth_tasks",
    "composed_pages": ["LoginPage"],
    "task_methods": [
      {
        "name": "log_in",
        "params": ["email: str", "password: str"],
        "calls": ["enter_email", "enter_password", "click_submit"]
      }
    ]
  }
}
```

**CRITICAL:** Pass `metadata` object to Tool 5 as `task_metadata`.

---

## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-07-01 | Task generator fallback skeleton code is a FAIL | Generator produces `pass` + `TODO` when POM metadata missing or invalid. Gate must catch this. See DEF-025. | `validate_post()` |
| IC-07-02 | `return` statements in Task methods is a FAIL | Framework pattern: Tasks return None. Any `return` (except bare `return` or `return None`) violates architecture. | `validate_post()` |
| IC-07-03 | DD-27 locator detection includes tuple patterns | Check for `By.` imports AND `(By.CSS_SELECTOR, ...)` tuple patterns AND `driver.find_element()` calls. | `validate_post()` |
| IC-07-04 | `@autologger.automation_logger("Task")` required on each method | Missing decorator = incomplete code. Constructor must NOT have decorator. | `validate_post()` |
| IC-07-05 | `pom_metadata` in PRE must have `class_name` and `action_methods` | Validates Tool 3 output was passed correctly. Empty `action_methods` may produce skeleton. | `validate_pre()` |

**Date Added:** 2025-12-21
**Task Reference:** Task 10.0 (qg_task)
**Related Defect:** DEF-025

---

*Next: Step 8 - Generate Role (Tool 5)*
