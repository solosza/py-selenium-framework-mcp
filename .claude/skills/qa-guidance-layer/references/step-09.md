# Step 9: Tool 6 - Generate Test Runner

**Purpose:** Generate pytest test code that calls Role workflow and asserts via POM state methods.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 9 - Generate Test Runner (Tool 6) |
| **Dependencies** | Step 8 complete (role_code, role_metadata exist), Step 6 (pom_metadata for assertions) |
| **Input** | `role_metadata` from Step 8, `pom_metadata` from Step 6, `test_scenarios` from Step 4 |
| **Output** | `test_code`, `test_metadata` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | None (unless AI fails 3 times, then user decides resolution) |
| **AI** | Injects actual parameter values (DD-17), fixes file paths (DD-16), validates imports (DD-18), ensures assertions use POM state methods (DD-15) |
| **Tool** | `qg_test_runner` validates input/output, `generate_test_runner` generates test code, operation saves state on SUCCESS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 8 complete (role_metadata exist in state)
- READ pom_metadata from Step 6 (for state method assertions)
- READ test_scenarios from Step 4 (for test structure)

ACTION:
- CALL qg_test_runner (PRE-VALIDATE)
- CALL generate_test_runner (OPERATION)
- AI POST-PROCESSING (before POST-VALIDATE):
  - DD-16: Override file paths to tests/test1/, tests/test2/, etc.
  - DD-17: Inject actual parameter values from requirement
  - DD-18: Validate import paths exist
  - DD-15: Ensure assertions use POM state methods from metadata
- CALL qg_test_runner (POST-VALIDATE)

VALIDATE (DD-25 - Skeleton Code Quality Gate):
- POST: Verify NO skeleton code (no placeholder tests)
- POST: Verify AAA pattern (Arrange, Act, Assert)
- POST: Verify assertions use POM state methods (not return values)
- POST: Verify correct imports

RETRY:
- If POST-VALIDATE fails: AI fixes the code (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_test_runner` |
| **Quality Gate** | `qg_test_runner` |
| **Gate Mode** | PRE+POST (validates metadata before, code quality after) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `test_code`, `test_metadata` (file path, test names, assertions) |
| **Who Saves** | Operation tool (`generate_test_runner`) |
| **When Saved** | On operation SUCCESS (after POST-VALIDATE passes) |
| **State Schema** | See below |

```json
{
  "step": 9,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "test_code": "@pytest.mark.auth\ndef test_valid_login(web_interface, config, test_data):\n    user = RegisteredUser(...)\n    user.login_and_browse()\n    assert login_page.is_logged_in()",
    "test_metadata": {
      "file_path": "tests/auth/test_login.py",
      "test_names": ["test_valid_login"],
      "assertions": ["is_logged_in", "is_logout_visible"],
      "imports": ["RegisteredUser", "LoginPage"]
    }
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-15 (POM state assertions), DD-16 (file paths), DD-17 (parameter injection), DD-18 (import validation), DD-19 (tool import), DD-25 (no skeleton), DD-26 (data contracts) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 10 until test code complete** |

**PRE-Validation Checks:**

| Check | Rule |
|-------|------|
| `role_metadata` | Present from Step 8 |
| `pom_metadata` | Present from Step 6 (for state methods) |
| `test_scenarios` | Present from Step 4 |

**POST-Validation Checks (DD-25):**

| Check | Rule |
|-------|------|
| AAA Pattern | Arrange (setup), Act (one role call), Assert (POM state checks) |
| Assertions | Use POM state methods (e.g., `is_logged_in()`), NOT return values |
| Imports | All imports resolve to existing files |
| Parameters | Actual values injected (no placeholders like `"category_name_value"`) |
| File path | Correct tests/{workflow}/ location |
| No skeleton | No placeholder tests, no `pass`, no `# TODO` |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| Missing Role metadata | Go back to Step 8 |
| Placeholder parameters | AI injects actual values from requirement |
| Wrong assertions | AI fixes to use POM state methods |
| Bad imports | AI fixes import paths |
| Skeleton code | AI completes the test |
| After 3 total failures | STOP → REPORT → USER DECIDES |

**Known Defects:**
- Tool sometimes generates placeholder parameter values (DD-17 violation)
- Tool sometimes uses return value assertions (DD-15 violation)

**Error Message Template (After 3 Failures):**

```
"I've attempted 3 times and cannot generate complete test code.

Issues found:
[list what's wrong - placeholders, bad assertions, bad imports]

How should we proceed?
1. Re-generate Role - Go back to Step 8
2. Manual test - You provide the code
3. Abort workflow - Stop and log issue"
```

---

## AI Post-Processing Examples

**DD-17 (Parameter Value Injection):**
```python
# Tool generates:
user.browse_category("category_name_value")

# AI must replace with actual value from requirement:
user.browse_category("Women")  # From "browse products in Women category"
```

**DD-15 (POM State Assertions):**
```python
# WRONG - assert on return value:
result = user.login()
assert result is True

# CORRECT - assert via POM state method:
user.login()
assert login_page.is_logged_in()
```

**DD-16 (File Path Override):**
```python
# Tool generates:
"tests/test_login.py"

# AI overrides to:
"tests/auth/test_login.py"  # Workflow-specific folder
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 9: TOOL 6 - GENERATE TEST RUNNER                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 8 complete?      │
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
              │  READ:              │     │  BLOCKED        │
              │  - role_metadata    │     │  Go to Step 8   │
              │  - pom_metadata     │     └─────────────────┘
              │  - test_scenarios   │
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_test_runner (PRE-VALIDATE)                                 │
│  - Validates all metadata present                                           │
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
              │  OPERATION:         │     │  Go back        │
              │  generate_test_     │     │  (missing data) │
              │  runner             │     └─────────────────┘
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  AI POST-PROCESSING │
              │  - DD-16: Fix paths │
              │  - DD-17: Inject    │
              │    actual values    │
              │  - DD-18: Validate  │
              │    imports          │
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_test_runner (POST-VALIDATE)                                │
│  - DD-25: No skeleton code                                                  │
│  - DD-15: POM state assertions                                              │
│  - AAA pattern enforced                                                     │
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
              │  STATE SAVED        │  │  AI FIXES CODE      │
              │  (by operation)     │  │  (max 3 attempts)   │
              └─────────────────────┘  └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 10 │
              └─────────────────────┘
```

---

## H. Tool Chain Data Contracts (DD-26)

**Input Contract (from Steps 6 and 8):**

Tool 6 requires BOTH role_metadata AND pom_metadata:

```python
# CORRECT - Pass both metadata objects:
arguments = {
    "test_name": "test_valid_login",
    "workflow": "auth",
    "role_metadata": tool_5_result["metadata"],  # From Tool 5
    "pom_metadata": tool_3_result["metadata"],   # From Tool 3 (for assertions)
    "scenario": {  # Optional, from Tool 1
        "description": "Verify user can login with valid credentials"
    }
}
```

**WRONG - Missing metadata produces generic template:**
```python
# WRONG - legacy format produces placeholder test:
arguments = {
    "test_name": "test_valid_login",
    "workflow": "auth",
    "role": "RegisteredUser"  # No methods known = placeholder
}
```

**Output Contract (Tool 6 provides for Step 10):**

```json
{
  "code": "@pytest.mark.auth\ndef test_valid_login(web_interface, config):\n    user = RegisteredUser(...)\n    user.login()\n    assert login_page.is_logged_in()",
  "metadata": {
    "file_path": "tests/auth/test_login.py",
    "test_methods": ["test_valid_login"],
    "role_used": "RegisteredUser",
    "page_used": "LoginPage",
    "assertions": ["is_logged_in"]
  }
}
```

**CRITICAL:** AI must apply DD-16 (override file path), DD-17 (inject actual values), DD-18 (validate imports) before saving.

---

## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-09-01 | test_scenarios from Step 4 required; scenario.description optional for docstrings | Tool uses description for docstring only; actual test structure from role_metadata | `validate_pre()` |
| IC-09-02 | Placeholder tests with `pass`/`TODO` are FAIL (DD-25) | Generator fallback produces skeleton when metadata incomplete | `validate_post()` |
| IC-09-03 | At least 1 role method call required; no max limit; multi-role allowed | Complex e2e scenarios (admin+user, buyer+seller) are legitimate | `validate_post()` |
| IC-09-04 | Assertions must use POM state methods (DD-15), not return values | Framework architecture: roles return None, tests assert via POM | `validate_post()` |
| IC-09-05 | @autologger.automation_logger("Test") required on test methods | Framework pattern consistency | `validate_post()` |

**Date Added:** 2025-12-21
**Task Reference:** Task 12.0 (qg_test_runner)

---

## J. Self-Heal Pattern Template

**When AI must complete/fix Test code, use this pattern:**

```python
import pytest
from typing import Dict, Any
from roles.auth.registered_user import RegisteredUser
from pages.auth.login_page import LoginPage
from pages.common.home_page import HomePage
from resources.utilities import autologger


class TestValidLogin:
    """Test suite for valid login scenarios."""

    # ═══════════════════════════════════════════════════════════════════════════
    # TEST METHOD - AAA pattern, Role calls, POM assertions
    # ═══════════════════════════════════════════════════════════════════════════
    @pytest.mark.auth
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_user_can_login_with_valid_credentials(
        self,
        web_interface,
        config: Dict[str, Any],
        test_data: Dict[str, Any]
    ) -> None:
        """
        Verify that a registered user can login with valid credentials.

        AAA Pattern:
        - Arrange: Create role and page objects
        - Act: Call ONE role workflow method (can be multiple for complex scenarios)
        - Assert: Verify state via POM state-check methods
        """
        # ═══════════════════════════════════════════════════════════════════════
        # ARRANGE - Create Role and POM instances for assertions
        # ═══════════════════════════════════════════════════════════════════════
        user = RegisteredUser(
            web=web_interface,
            user_data=test_data["valid_user"],
            base_url=config["base_url"]
        )
        login_page = LoginPage(web_interface)
        home_page = HomePage(web_interface)

        # ═══════════════════════════════════════════════════════════════════════
        # ACT - Call Role workflow method(s)
        # Note: Can call multiple Role methods for complex multi-persona scenarios
        # ═══════════════════════════════════════════════════════════════════════
        user.login()

        # ═══════════════════════════════════════════════════════════════════════
        # ASSERT - Use POM state-check methods, NOT return values
        # ═══════════════════════════════════════════════════════════════════════
        assert login_page.is_logged_in(), "User should be logged in"
        assert home_page.is_logout_link_visible(), "Logout link should be visible"


class TestMultiPersonaScenario:
    """Example of complex test with multiple roles."""

    @pytest.mark.e2e
    @autologger.automation_logger("Test")
    def test_admin_creates_user_then_user_logs_in(
        self,
        web_interface,
        config: Dict[str, Any],
        test_data: Dict[str, Any]
    ) -> None:
        """
        Complex scenario: Admin creates user, then user logs in.

        Multiple Role calls ARE valid for multi-persona workflows.
        """
        # ARRANGE
        admin = AdminUser(web_interface, test_data["admin"], config["base_url"])
        new_user = RegisteredUser(web_interface, test_data["new_user"], config["base_url"])
        admin_page = AdminPage(web_interface)
        login_page = LoginPage(web_interface)

        # ACT - Multiple Role calls (valid for complex scenarios)
        admin.login()
        admin.create_user(test_data["new_user"])
        admin.logout()
        new_user.login()

        # ASSERT
        assert admin_page.is_user_created(test_data["new_user"]["email"])
        assert login_page.is_logged_in()
```

**Test Pattern Rules (Checklist):**

| ✓ | Rule |
|---|------|
| ☐ | `@autologger.automation_logger("Test")` decorator on test methods |
| ☐ | `@pytest.mark.{workflow}` marker for categorization |
| ☐ | AAA pattern: Arrange, Act, Assert sections |
| ☐ | Call Role workflow methods (one or more) |
| ☐ | Assert via POM state-check methods |
| ☐ | Import POMs for assertions only (not for actions) |
| ☐ | **NO Task method calls** (delegate to Role) |
| ☐ | **NO POM action method calls** (delegate to Role) |
| ☐ | **NO orchestration logic** (that belongs in Role) |
| ☐ | NO assertions on return values (Roles return None) |

**Anti-Patterns to Avoid:**

```python
# ❌ WRONG: Task method call in test (bypasses Role)
def test_login(self, web_interface, config):
    auth_tasks = AuthTasks(web_interface, config["base_url"])
    auth_tasks.log_in(email, password)  # NO! Use Role

# ❌ WRONG: POM action method call in test (bypasses Role+Task)
def test_login(self, web_interface, config):
    login_page = LoginPage(web_interface)
    login_page.enter_email(email)    # NO! Use Role
    login_page.enter_password(password)
    login_page.click_submit()

# ❌ WRONG: Asserting on return value
def test_login(self, web_interface, config):
    user = RegisteredUser(...)
    result = user.login()       # Roles return None
    assert result is True       # NO! Assert via POM

# ❌ WRONG: Orchestrating workflow in test
def test_purchase(self, web_interface, config):
    user = RegisteredUser(...)
    user.login()                # Multiple calls that should be
    user.browse_category()      # ONE Role method like
    user.add_to_cart()          # user.purchase_product()
    user.checkout()             # This belongs in Role

# ❌ WRONG: Skeleton test
def test_placeholder(self):
    pass  # NO! Must have actual test logic

# ❌ WRONG: Missing decorator
def test_login(self, web_interface):  # Missing @autologger
    ...
```

**Correct Pattern: Test calls Role, asserts via POM:**

```python
# ✅ CORRECT: Single Role call for simple workflow
@autologger.automation_logger("Test")
def test_user_can_browse_products(self, web_interface, config, test_data):
    # Arrange
    user = GuestUser(web_interface, config["base_url"])
    catalog_page = CatalogPage(web_interface)

    # Act - ONE Role call
    user.browse_category("Women")

    # Assert - POM state method
    assert catalog_page.has_products(), "Products should be displayed"


# ✅ CORRECT: Multiple Role calls for multi-persona scenario
@autologger.automation_logger("Test")
def test_buyer_and_seller_transaction(self, web_interface, config, test_data):
    # Arrange
    seller = SellerUser(web_interface, test_data["seller"], config["base_url"])
    buyer = BuyerUser(web_interface, test_data["buyer"], config["base_url"])
    product_page = ProductPage(web_interface)

    # Act - Multiple Role calls (valid: different personas)
    seller.list_product(test_data["product"])
    buyer.purchase_product(test_data["product"])

    # Assert
    assert product_page.is_sold()
```

---

*Next: Step 10 - Save & Run*
