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
- POST: FR-14.2 - Verify credential strategy matches Step 1 configuration

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
| **Who Saves** | Quality gate (`qg_role` POST) |
| **When Saved** | On POST-VALIDATE pass |
| **File Written** | **YES - Immediately after POST validation passes** (DEF-051 fix) |
| **State Schema** | See below |

**DEF-051: Immediate File Write:**

After POST validation passes, `qg_role` immediately writes the Role file to disk:
- File path: `framework/roles/{workflow}/{role_name_snake_case}.py`
- Example: `framework/roles/auth/registered_user.py`
- Logged to audit trail with step number

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
| FR-14.2 | Credential strategy matches Step 1 config (static/dynamic/self-contained/none) |

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
| IC-08-07 | FR-14.2: Credential strategy must match Step 1 config | Validates that Role's credential handling (user_data param vs hardcoded) matches the strategy chosen in Step 1. Prevents semantic mismatch between configuration and implementation. | `validate_post()` via semantic rules |
| IC-08-08 | DD-49: No base_url parameter in Role constructor | URL configuration flows via conftest → environment_config.json → web.config. POMs access via `self.web.config['url']`. Roles/Tasks do NOT need base_url parameter. | `validate_post()` via semantic rule templates |
| IC-08-09 | Workflow subfolder pattern: import_path must include workflow namespace | Role import_path must follow `roles.{workflow}.{role_name}` pattern (NOT flat `roles.{role_name}`). Consistency with Tasks which use `tasks.{workflow}.{task_name}`. File path: `framework/roles/{workflow}/{role_name}.py` | `validate_post()` via `_check_workflow_subfolder_pattern()` |

**Date Added:** 2025-12-21 (IC-08-01 to IC-08-06), 2026-01-10 (IC-08-07), 2026-01-15 (IC-08-08), 2026-01-16 (IC-08-09)
**Task Reference:** Task 11.0 (qg_role), Task 36.0 (FR-14.2 semantic validation)

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

## K. Dynamic Credential Field Resolution (DEF-063)

**Purpose:** Auto-detect credential field name mismatches and provide dynamic resolution pattern.

**Problem:** Tool 5 may hardcode credential field names (`email`/`password`) that don't match `test_users.json` (which uses `username`/`password`), causing Role constructor to fail.

**Detection Logic:**

Gate checks if Role hardcodes credential field names:
- Looks for `self.email = user_data.get('email')` pattern
- Checks for `self.password = user_data.get('password')` without username fallback
- Returns NEEDS_RETRY if hardcoded fields detected

**Scaffolding Response Format:**

When hardcoded fields detected, gate returns `status: "NEEDS_RETRY"`:

```json
{
  "status": "NEEDS_RETRY",
  "fix_applied": "dynamic_credential_fields",
  "error": "Role hardcodes credential fields: email, password (no username fallback)",
  "message": "Make Role use dynamic credential field resolution:",
  "scaffolding_needed": [{
    "type": "code_pattern",
    "location": "Role constructor (__init__)",
    "template": "<dynamic pattern>",
    "reason": "Flexible credential field resolution for any application"
  }]
}
```

**AI Handling Instructions:**

When gate returns `NEEDS_RETRY`:
1. Read `scaffolding_needed[0].template`
2. Replace hardcoded field assignments in Role `__init__` with dynamic pattern
3. Retry qg_role POST with updated code
4. Verify gate returns `status: "pass"`

**NO human approval needed** - code quality fix, not config decision.

**Dynamic Pattern Template:**

```python
# Dynamic credential resolution - works with any field names
self.user_data = user_data
self.username = (
    user_data.get('username') or
    user_data.get('email') or
    user_data.get('user_id') or
    user_data.get('login')
)
self.password = (
    user_data.get('password') or
    user_data.get('pin') or
    user_data.get('secret')
)

# Validate credentials present
if not self.username or not self.password:
    raise ValueError(f"RegisteredUser requires username and password. Got: {list(user_data.keys())}")
```

**Idempotent:** If Role already uses dynamic pattern, gate returns `pass` (no scaffolding needed).

**Benefits:**
- ✓ Application-agnostic - Works with any credential field names
- ✓ Auto-healing - AI fixes code without human intervention
- ✓ Consistent pattern - Uses same NEEDS_RETRY pattern as DEF-060/DEF-062
- ✓ Future-proof - Handles new field name variations automatically

**Pattern Summary:**

| Aspect | DEF-063 |
|--------|---------|
| **Scaffolds** | Code pattern (dynamic credential resolution) |
| **Risk Level** | Low (code quality fix) |
| **Human Approval** | NO (auto-heal) |
| **Reasoning** | Code quality fix, not configuration decision |
| **Pattern** | NEEDS_RETRY → AI refactors code → Retry |

---

## L. DD-49: Navigation Responsibility Pattern (No base_url Parameter)

**Purpose:** Enforce centralized URL configuration via environment config instead of parameter passing.

**Rule:** Only POMs call navigate(). URL comes from `self.web.config['url']` via conftest.py → environment_config.json flow.

**Architecture Flow:**

```
conftest.py (loads environment_config.json)
  ↓
{"parabank12": {"url": "https://parabank.parasoft.com"}}
  ↓
web_interface fixture
  ↓
WebInterface(driver, config, logger)
  ↓
POMs access via self.web.config['url']
  ↓
open_account_page.py: self.web.navigate_to(self.web.config['url'] + '/parabank/openaccount.htm')
```

**Old Pattern (DEPRECATED):**

```python
# ❌ WRONG: base_url parameter passed through layers
class RegisteredUser:
    def __init__(self, web: WebInterface, user_data: Dict[str, Any], base_url: str):
        self.base_url = base_url  # Stored but never used!
        self.auth_tasks = AuthTasks(web, base_url)  # Passed down
```

**New Pattern (CORRECT):**

```python
# ✅ CORRECT: No base_url parameter - POMs get URL from config
class RegisteredUser:
    def __init__(self, web: WebInterface, user_data: Dict[str, Any]):
        # No base_url parameter needed
        # Compose tasks without base_url
        self.auth_tasks = AuthTasks(web)
```

**POM Navigation Pattern:**

```python
# ✅ CORRECT: POM accesses URL directly from config
class OpenAccountPage:
    def navigate(self) -> "OpenAccountPage":
        self.web.navigate_to(self.web.config['url'] + '/parabank/openaccount.htm')
        return self
```

**Enforcement:**

- Semantic rule templates show NO base_url parameter (credential_strategy_rule.py)
- Gate validates Role constructor signature
- Protocol documents correct pattern (this section)

**Why This Pattern:**

- ✓ URL configuration belongs in environment config, not passed as parameters
- ✓ Centralized management via environment_config.json
- ✓ Easier multi-environment testing (dev/staging/prod)
- ✓ Cleaner Role/Task constructor signatures
- ✓ Follows framework principle: composition over parameter passing

**Smart Gate Layer 2:**

Semantic rule templates (credential_strategy_rule.py) automatically provide correct pattern without base_url parameter. AI generates code following this pattern by default.

---

## M. Workflow Subfolder Pattern (IC-08-09)

**Purpose:** Enforce consistent file organization between Tasks and Roles layers using workflow subfolders.

**Rule:** Role import_path must include workflow namespace: `roles.{workflow}.{role_name}`, matching Tasks pattern.

**Pattern Consistency:**

```
Tasks:  framework/tasks/{workflow}/task_name.py  → tasks.{workflow}.task_name
Roles:  framework/roles/{workflow}/role_name.py  → roles.{workflow}.role_name
```

**Old Pattern (DEPRECATED):**

```python
# ❌ WRONG: Flat structure
# File: framework/roles/registered_user.py
# Import: from roles.registered_user import RegisteredUser

# Problems:
# - Inconsistent with Tasks layer organization
# - All roles in single flat directory
# - No workflow grouping
```

**New Pattern (CORRECT):**

```python
# ✅ CORRECT: Workflow subfolder structure
# File: framework/roles/parabank12/registered_user.py
# Import: from roles.parabank12.registered_user import RegisteredUser

# Benefits:
# - Consistent with Tasks layer
# - Roles grouped by workflow/domain
# - Clear namespace separation
```

**Metadata Structure:**

```python
# Tool 5 output metadata
{
    "class_name": "RegisteredUser",
    "import_path": "roles.parabank12.registered_user",  # ✅ Includes workflow
    "composed_tasks": ["OpenAccountTasks"],
    "workflow_methods": [...]
}
```

**Enforcement:**

- Generator creates correct path with workflow parameter (`role_generator.get_file_path(role_name, workflow)`)
- Gate validates import_path structure (`_check_workflow_subfolder_pattern()`)
- Protocol documents correct pattern (this section)

**Why This Pattern:**

- ✓ Consistency across framework layers (Tasks + Roles)
- ✓ Clear workflow/domain grouping
- ✓ Scalable organization as framework grows
- ✓ Easier to find related components
- ✓ Matches industry best practices

**Smart Gate Layer 2:**

`qg_role._check_workflow_subfolder_pattern()` detects flat import paths and provides correct pattern template. AI generates fix by updating import_path to include workflow namespace.

**Defense-in-Depth:**

1. Generator creates correct path (prevention)
2. Gate validates correct path (enforcement)
3. Protocol documents correct pattern (guidance)

---

*Next: Step 9 - Generate Test Runner (Tool 6)*
