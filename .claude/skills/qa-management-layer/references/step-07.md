<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

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

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, Task class name, method counts, PRE/POST gate results, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
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
| **State Saved** | `task_code`, `task_metadata` |
| **Who Saves** | Quality gate (`qg_task` POST) |
| **When Saved** | On POST-VALIDATE pass |
| **File Written** | **YES - Immediately after POST validation passes** (DEF-051 fix) |
| **State Schema** | See below |

**DEF-051: Immediate File Write:**

After POST validation passes, `qg_task` immediately writes the Task file to disk:
- File path: `framework/tasks/{workflow}/{task_name_snake_case}.py`
- Example: `framework/tasks/auth/auth_tasks.py`
- Logged to audit trail with step number

**Note:** Unlike Step 6 (POMs), Tasks do NOT use multi-page loop tracking.
Tasks are per-domain (e.g., AuthTasks, CatalogTasks), not per-page.
Multiple pages may share the same Task class.

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

| Field | Purpose |
|-------|---------|
| `task_code` | Generated Task code |
| `task_metadata` | Task metadata for Step 8 |

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

## J. Self-Heal Pattern Template

**When AI must complete/fix Task code, use this pattern:**

```python
from interfaces.web_interface import WebInterface
from pages.auth.login_page import LoginPage
from pages.auth.registration_page import RegistrationPage
from resources.utilities import autologger


class AuthTasks:
    """Task module for authentication domain operations."""

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTOR - Compose WebInterface + POMs, NO inheritance, NO base_url
    # ═══════════════════════════════════════════════════════════════════════════
    def __init__(self, web: WebInterface):
        self.web = web
        # Compose page objects - they get URL from self.web.config
        self.login_page = LoginPage(web)
        self.registration_page = RegistrationPage(web)

    # ═══════════════════════════════════════════════════════════════════════════
    # TASK METHODS - Single domain operation, return None, use @autologger
    # ═══════════════════════════════════════════════════════════════════════════
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        """
        Single domain operation: authenticate user.

        NO return value - test asserts via login_page.is_logged_in()
        """
        # POM handles navigation (gets URL from self.web.config)
        (self.login_page
            .navigate()
            .enter_email(email)
            .enter_password(password)
            .click_submit())

        # NO return statement

    @autologger.automation_logger("Task")
    def log_out(self) -> None:
        """Single domain operation: end session."""
        self.login_page.click_logout()
        # NO return - test asserts via login_page.is_logged_out()

    @autologger.automation_logger("Task")
    def register_user(self, user_data: dict) -> None:
        """Single domain operation: create new account."""
        # POM handles navigation
        (self.registration_page
            .navigate()
            .enter_email(user_data["email"])
            .click_create_account())

        (self.registration_page
            .select_gender(user_data["gender"])
            .enter_first_name(user_data["first_name"])
            .enter_last_name(user_data["last_name"])
            .enter_password(user_data["password"])
            .click_register())

        # NO return - test asserts via registration_page.is_account_created()
```

**Task Pattern Rules (Checklist):**

| ✓ | Rule |
|---|------|
| ☐ | `@autologger.automation_logger("Task")` decorator on each method |
| ☐ | Compose `WebInterface` + POMs in `__init__`, NO inheritance |
| ☐ | **NO `base_url` parameter** - POM gets URL from `self.web.config` |
| ☐ | Navigation via POM `navigate()` method (never `self.web.navigate_to()`) |
| ☐ | Methods return `None` (type hint `-> None`) |
| ☐ | Call POM atomic methods in fluent chains |
| ☐ | One domain operation per method |
| ☐ | **NO `By.*` imports** (locators only in POMs) |
| ☐ | **NO locator tuples** `(By.CSS_SELECTOR, "...")` |
| ☐ | **NO `driver.find_element()`** calls |
| ☐ | NO return values (tests assert via POM state methods) |

**Anti-Patterns to Avoid (DD-27 Violations):**

```python
# ❌ WRONG: Locator import in Task
from selenium.webdriver.common.by import By  # NEVER in Task

# ❌ WRONG: Locator tuple in Task
def add_to_cart(self, product_index: int) -> None:
    locator = (By.CSS_SELECTOR, f"li:nth-child({product_index})")  # NO!
    self.web.click(*locator)

# ❌ WRONG: driver.find_element in Task
def get_product(self) -> None:
    element = self.web.driver.find_element(By.CSS_SELECTOR, ".product")  # NO!

# ❌ WRONG: Returning value
def log_in(self, email: str, password: str) -> bool:  # NO!
    ...
    return self.login_page.is_logged_in()  # NO!

# ❌ WRONG: Missing decorator
def log_in(self, email: str, password: str) -> None:  # Missing @autologger
    ...

# ❌ WRONG: Skeleton with pass
@autologger.automation_logger("Task")
def execute_workflow(self) -> None:
    pass  # NO! Must have actual POM calls
```

**Correct Pattern: Task calls POM, never has locators:**

```python
# ✅ CORRECT: Task delegates to POM
@autologger.automation_logger("Task")
def add_product_to_cart(self, product_index: int = 0) -> None:
    self.catalog_page.hover_product(product_index)  # POM method
    self.catalog_page.click_add_to_cart()           # POM method
    # Locators are INSIDE catalog_page, not here
```

---

*Next: Step 8 - Generate Role (Tool 5)*
