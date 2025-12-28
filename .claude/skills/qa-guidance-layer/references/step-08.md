<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 8: Tool 5 - Generate Role

**Purpose:** Generate Role class code that orchestrates multiple Tasks into complete business workflows.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 8 - Generate Role (Tool 5) |
| **Dependencies** | Step 7 complete (task_code, task_metadata exist) |
| **Input** | `task_metadata` from Step 7, `role_name` from Step 2, `persona` from Step 2 |
| **Output** | `role_code`, `role_metadata` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | None (unless AI fails 3 times, then user decides resolution) |
| **AI** | Checks existing roles (DD-12), validates code completeness (DD-25), ensures NO return values, ensures workflow orchestration |
| **Tool** | `qg_role` validates input/output, `generate_role` generates Role code, operation saves state on SUCCESS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 7 complete (task_metadata exist in state)
- DD-12: Check if Role class already exists for this persona
  - IF EXISTS: Extend with new workflow methods, don't create new class
  - IF NOT EXISTS: Generate new Role class

ACTION:
- CALL qg_role (PRE-VALIDATE)
- CALL generate_role (OPERATION)
- CALL qg_role (POST-VALIDATE)

VALIDATE (DD-25 - Skeleton Code Quality Gate):
- POST: Verify NO skeleton code indicators
- POST: Verify @autologger.automation_logger("Role") decorator
- POST: Verify NO return values (roles return None)
- POST: Verify Task composition in constructor
- POST: Verify workflow methods call MULTIPLE task methods (not just one)

RETRY:
- If POST-VALIDATE fails: AI completes the code (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_role` |
| **Quality Gate** | `qg_role` |
| **Gate Mode** | PRE+POST (validates metadata before, code quality after) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `role_code`, `role_metadata` (class name, workflow methods, composed Tasks) |
| **Who Saves** | Operation tool (`generate_role`) |
| **When Saved** | On operation SUCCESS (after POST-VALIDATE passes) |
| **State Schema** | See below |

```json
{
  "step": 8,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "role_code": "class RegisteredUser:\n    @autologger.automation_logger('Role')\n    def login_and_browse(self):\n        self.auth_tasks.log_in(...)\n        self.catalog_tasks.browse(...)",
    "role_metadata": {
      "class_name": "RegisteredUser",
      "file_path": "framework/roles/registered_user.py",
      "is_new": true,
      "workflow_methods": ["login_and_browse"],
      "composed_tasks": ["AuthTasks", "CatalogTasks"]
    }
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-12 (check existing), DD-19 (tool import), DD-25 (no skeleton), DD-26 (data contracts), framework architecture (no return, orchestrates multiple tasks) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 9 until Role code complete** |

**PRE-Validation Checks:**

| Check | Rule |
|-------|------|
| `task_metadata` | Present from Step 7 |
| `role_name` | Valid PascalCase class name |
| Existing check (DD-12) | Scanned framework/roles/ for existing class |

**POST-Validation Checks (DD-25):**

| Check | Rule |
|-------|------|
| Constructor | Composes WebInterface, user_data, and Task(s) |
| Decorator | `@autologger.automation_logger("Role")` on each method |
| Return value | Methods return None |
| Workflow | Each method calls MULTIPLE task methods (not single operation) |
| No skeleton | No `pass`, no `# Add...`, no empty bodies |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| Missing Task metadata | Go back to Step 7 |
| Skeleton code detected | AI completes the code (max 3) |
| Single task call | AI adds additional task orchestration |
| Return value found | AI removes return statement |
| After 3 total failures | STOP → REPORT → USER DECIDES |

**Known Defects:** Roles sometimes only call one task (should orchestrate multiple)

**Error Message Template (After 3 Failures):**

```
"I've attempted 3 times and cannot generate complete Role code.

Issues found:
[list what's wrong - skeleton, return values, single task only]

How should we proceed?
1. Re-generate Task - Go back to Step 7
2. Manual Role - You provide the code
3. Abort workflow - Stop and log issue"
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 8: TOOL 5 - GENERATE ROLE                            │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 7 complete?      │
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
              │  Role already       │     │  Go to Step 7   │
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
│  QUALITY GATE: qg_role (PRE-VALIDATE)                                        │
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
              │  OPERATION:         │     │  Go to Step 7   │
              │  generate_role      │     └─────────────────┘
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_role (POST-VALIDATE)                                       │
│  - DD-25: No skeleton code                                                  │
│  - No return values, decorator present                                      │
│  - Workflow orchestrates MULTIPLE tasks                                     │
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
              │  PROCEED TO STEP 9  │
              └─────────────────────┘
```

---

## H. Tool Chain Data Contracts (DD-26)

**Input Contract (from Step 7):**

```python
# CORRECT - Pass Tool 4 metadata:
arguments = {
    "role_name": "RegisteredUser",
    "workflow": "auth",
    "task_metadata": tool_4_result["metadata"]  # From Tool 4
}
```

**WRONG - Do NOT omit task_metadata:**
```python
# WRONG - missing task_metadata produces skeleton:
arguments = {
    "role_name": "RegisteredUser",
    "task_class": "AuthTasks"  # Legacy, no method info = skeleton
}
```

**Output Contract (Tool 5 provides for Step 9):**

```json
{
  "code": "class RegisteredUser:\n    @autologger...\n    def login(self):...",
  "metadata": {
    "class_name": "RegisteredUser",
    "import_path": "roles.registered_user",
    "composed_tasks": ["AuthTasks"],
    "workflow_methods": [
      {
        "name": "login",
        "params": [],
        "calls": ["auth_tasks.log_in"]
      }
    ]
  }
}
```

**CRITICAL:** Pass `metadata` to Tool 6 as `role_metadata`. Also pass `pom_metadata` from Step 6 for assertions.

---

## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-08-01 | Role generator placeholder methods with `pass` and `TODO` is a FAIL | Generator produces skeleton when task_metadata missing/invalid. Gate must catch this. | `validate_post()` |
| IC-08-02 | Single-task workflow methods are acceptable | FRAMEWORK.md's own `login()` example calls one task. "MULTIPLE tasks" applies to complex workflows, not all methods. | N/A (not enforced) |
| IC-08-03 | DD-27 applies to Roles - no locators allowed | Locators belong only in POMs. No `By.` imports, tuples, or `find_element()` in Role code. | `validate_post()` |
| IC-08-04 | `@autologger.automation_logger("Role")` required on workflow methods | Missing decorator = incomplete code. Constructor uses "Role Constructor". | `validate_post()` |
| IC-08-05 | `task_metadata` in PRE must have `class_name` and `task_methods` | Validates Tool 4 output was passed correctly. Empty `task_methods` may produce skeleton. | `validate_pre()` |
| IC-08-06 | Workflow methods must contain at least one task method call | Methods with only `pass` or no `self.xxx_tasks.method()` calls = skeleton code. | `validate_post()` |

**Date Added:** 2025-12-21
**Task Reference:** Task 11.0 (qg_role)

---

## J. Self-Heal Pattern Template

**When AI must complete/fix Role code, use this pattern:**

```python
from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.auth.auth_tasks import AuthTasks
from tasks.catalog.catalog_tasks import CatalogTasks
from tasks.checkout.checkout_tasks import CheckoutTasks
from resources.utilities import autologger


class RegisteredUser:
    """Role representing an authenticated user persona."""

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTOR - Compose WebInterface + Tasks, NO inheritance, NO base_url
    # ═══════════════════════════════════════════════════════════════════════════
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web: WebInterface, user_data: Dict[str, Any]):
        self.web = web
        self.user_data = user_data
        self.email = user_data.get("email")
        self.password = user_data.get("password")

        # Compose Task modules - NO base_url passed (Tasks get URL via POM -> web.config)
        self.auth_tasks = AuthTasks(web)
        self.catalog_tasks = CatalogTasks(web)
        self.checkout_tasks = CheckoutTasks(web)

    # ═══════════════════════════════════════════════════════════════════════════
    # WORKFLOW METHODS - Orchestrate Tasks, return None, use @autologger
    # ═══════════════════════════════════════════════════════════════════════════
    @autologger.automation_logger("Role")
    def login_and_browse_category(self, category: str) -> None:
        """
        Complete workflow: Login then browse products.

        Orchestrates MULTIPLE tasks into user journey.
        NO return value - test asserts via POM state methods.
        """
        self.auth_tasks.log_in(self.email, self.password)
        self.catalog_tasks.browse_category(category)
        # NO return - test asserts via catalog_page.has_products()

    @autologger.automation_logger("Role")
    def purchase_product(self, product_data: dict) -> None:
        """
        Complete workflow: Login -> Browse -> Add to Cart -> Checkout.

        This is what makes Role different from Task:
        - Role orchestrates MULTIPLE tasks
        - Role represents a complete user journey/story
        """
        self.auth_tasks.log_in(self.email, self.password)
        self.catalog_tasks.browse_category(product_data["category"])
        self.catalog_tasks.add_to_cart(product_data["name"])
        self.checkout_tasks.complete_purchase()
        # NO return - test asserts via checkout_page.is_order_confirmed()

    @autologger.automation_logger("Role")
    def login(self) -> None:
        """
        Simple workflow: Just login.

        Note: Single-task workflows ARE valid when that's all the story requires.
        """
        self.auth_tasks.log_in(self.email, self.password)
        # NO return - test asserts via login_page.is_logged_in()
```

**Role Pattern Rules (Checklist):**

| ✓ | Rule |
|---|------|
| ☐ | `@autologger.automation_logger("Role")` decorator on workflow methods |
| ☐ | `@autologger.automation_logger("Role Constructor")` on `__init__` |
| ☐ | Compose `WebInterface` + Tasks in `__init__`, NO inheritance |
| ☐ | **NO `base_url` parameter** - URL flows via Task -> POM -> `web.config` |
| ☐ | Task instantiation: `AuthTasks(web)` - NO base_url passed |
| ☐ | Methods return `None` (type hint `-> None`) |
| ☐ | Call Task methods (NOT POM methods directly) |
| ☐ | Store credentials in `self.user_data` or attributes |
| ☐ | **NO `By.*` imports** (locators only in POMs) |
| ☐ | **NO POM imports** (Roles use Tasks, not POMs) |
| ☐ | **NO direct POM method calls** (delegate to Tasks) |
| ☐ | NO return values (tests assert via POM state methods) |

**Anti-Patterns to Avoid:**

```python
# ❌ WRONG: POM import in Role
from pages.auth.login_page import LoginPage  # NO - Roles use Tasks

# ❌ WRONG: Locator import in Role
from selenium.webdriver.common.by import By  # NEVER in Role

# ❌ WRONG: Direct POM method call
@autologger.automation_logger("Role")
def login(self) -> None:
    self.login_page.enter_email(self.email)  # NO! Use Task
    self.login_page.enter_password(self.password)
    self.login_page.click_submit()

# ❌ WRONG: Returning value
@autologger.automation_logger("Role")
def login(self) -> bool:  # NO!
    self.auth_tasks.log_in(self.email, self.password)
    return self.login_page.is_logged_in()  # NO!

# ❌ WRONG: Missing decorator
def purchase_product(self, product: dict) -> None:  # Missing @autologger
    ...

# ❌ WRONG: Skeleton with pass
@autologger.automation_logger("Role")
def execute_workflow(self) -> None:
    pass  # NO! Must have actual Task calls

# ❌ WRONG: Inheritance
class RegisteredUser(BaseRole):  # NO - use composition
    pass
```

**Correct Pattern: Role calls Tasks, never POMs directly:**

```python
# ✅ CORRECT: Role orchestrates Tasks
@autologger.automation_logger("Role")
def add_product_and_checkout(self, product: dict) -> None:
    self.catalog_tasks.add_to_cart(product["name"])  # Task method
    self.checkout_tasks.proceed_to_checkout()        # Task method
    self.checkout_tasks.complete_purchase()          # Task method
    # POMs are used INSIDE Tasks, not here
```

---

*Next: Step 9 - Generate Test Runner (Tool 6)*
