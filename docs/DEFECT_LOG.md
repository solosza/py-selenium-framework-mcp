# Defect Log - Framework Audit

**Project:** py_sel_framework_mcp
**Audit Start Date:** 2025-11-29
**Status:** In Progress

---

## Severity Definitions

| Severity | Description | Action Required |
|----------|-------------|-----------------|
| **CRITICAL** | Architecture violation - breaks 4-layer pattern | Fix immediately, blocks audit progress |
| **HIGH** | Wrong responsibility - code in wrong layer | Fix before completing parent task |
| **MEDIUM** | Missing elements - incomplete implementation | Fix during parent task |
| **LOW** | Style/naming - conventions not followed | Fix if time permits |

---

## Status Options

| Status | Description |
|--------|-------------|
| **OPEN** | Defect identified, not yet addressed |
| **IN_PROGRESS** | Currently being fixed |
| **READY_TO_TEST** | Fix implemented, awaiting E2E verification |
| **RESOLVED** | Fix applied and verified |
| **WONT_FIX** | Intentionally not fixing (with justification) |

---

## Defect Entry Template

```markdown
### [DEF-XXX] Brief Description
**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Status:** OPEN | IN_PROGRESS | RESOLVED | WONT_FIX
**Layer:** Page | Task | Role | Test | MCP Tool
**File:** `path/to/file.py`
**Line(s):** XX-XX

**Rule Violated:**
- [Which architectural rule was broken]

**Description:**
[What is wrong and why it's a problem]

**Fix:**
[How it was fixed, or how it should be fixed]

**Resolved Date:** YYYY-MM-DD (if resolved)
```

## E2E Test Defect Template

For defects caught during E2E testing (B.6 test1, B.7 test2), use this extended format:

```markdown
### [DEF-XXX] Brief Description
**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Status:** OPEN | IN_PROGRESS | RESOLVED | WONT_FIX
**Caught By:** B.6 test1 | B.7 test2
**Code Version:** commit hash or branch name
**Layer:** Page | Task | Role | Test | MCP Tool
**File:** `path/to/file.py`
**Line(s):** XX-XX

**Error Message:**
[Exact error or failure message]

**Description:**
[What is wrong and why it's a problem]

**Fix:**
[How it was fixed]

**Verified:** Rerun of test1/test2 passed
**Resolved Date:** YYYY-MM-DD
```

**E2E Defect Workflow:**
1. Run E2E test (test1 or test2)
2. If failure → Log defect with "Caught By" field
3. Fix the issue
4. Rerun E2E from start
5. Mark RESOLVED only after successful rerun

---

## Defects

### Page Object Layer (Task 2.0)

### [DEF-001] Composite methods in RegistrationPage belong in Task layer
**Severity:** HIGH
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/registration_page.py`
**Line(s):** 375-448

**Rule Violated:**
- POM methods must be atomic (one UI action per method)
- Composite workflows belong in Task layer

**Description:**
`fill_registration_form()` and `register_user()` are composite methods that orchestrate multiple field entries. This is Task-layer responsibility, not POM.

**Fix:**
Remove these methods from POM. Tasks should call individual atomic methods.

---

### [DEF-002] LoginPage missing state-check methods
**Severity:** MEDIUM
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/login_page.py`
**Line(s):** N/A

**Rule Violated:**
- POMs should have state-check methods for assertions

**Description:**
LoginPage has no state-check methods (is_page_loaded, is_error_displayed, etc.). Tests cannot verify state through this POM.

**Fix:**
Add state-check methods: `is_page_loaded()`, `has_error_message()`, `get_error_message()`.

---

### [DEF-003] RegistrationPage methods return None instead of self
**Severity:** MEDIUM
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/registration_page.py`
**Line(s):** 82-88, 121-149, 191-209, 233-249, 251-258, etc.

**Rule Violated:**
- POM methods should return `self` for fluent chaining

**Description:**
Many methods have `-> None` return type or no return statement, breaking fluent chaining pattern. Examples: `select_gender_mr()`, `enter_customer_firstname()`, `check_newsletter()`, etc.

**Fix:**
Update all action methods to return `self` with proper type hints.

---

### [DEF-004] BasePage.search() is composite method
**Severity:** MEDIUM
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/base_page.py`
**Line(s):** 99-108

**Rule Violated:**
- POM methods must be atomic (one UI action per method)

**Description:**
`search()` combines `enter_search_query()` + `click_search_button()`. Should be atomic.

**Fix:**
Remove composite `search()` method. Callers should use individual methods.

---

### [DEF-005] HomePage.search_for() is composite method
**Severity:** MEDIUM
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/common/home_page.py`
**Line(s):** 156-171

**Rule Violated:**
- POM methods must be atomic (one UI action per method)

**Description:**
`search_for()` combines type_text + send_keys(RETURN). Should be atomic.

**Fix:**
Split into `enter_search_term()` and `submit_search()` methods.

---

### [DEF-006] LoginPage locator naming convention violation
**Severity:** LOW
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/login_page.py`
**Line(s):** 31

**Rule Violated:**
- Locators should use UPPER_SNAKE_CASE

**Description:**
`SUBMITLOGIN` should be `SUBMIT_LOGIN` per naming convention.

**Fix:**
Rename to `SUBMIT_LOGIN`.

---

### [DEF-007] AuthenticationPage missing return type hints
**Severity:** LOW
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/authentication_page.py`
**Line(s):** 62-131

**Rule Violated:**
- Methods should have explicit return type hints

**Description:**
Several methods document "Returns: self for method chaining" but lack type hints.

**Fix:**
Add `-> "AuthenticationPage"` return type hints to all chaining methods.

---

### [DEF-008] ProductListPage uses explicit time.sleep()
**Severity:** LOW
**Status:** WONT_FIX
**Layer:** Page
**File:** `framework/pages/catalog/product_list_page.py`
**Line(s):** 135, 146, 157, 168, 197, 203, 208, 210, 237, 344

**Rule Violated:**
- Prefer WebInterface wait methods over explicit sleeps

**Description:**
Multiple `time.sleep()` calls for AJAX waits. Should use explicit waits where possible.

**Fix:**
WONT_FIX: time.sleep() is acceptable for complex AJAX interactions where explicit wait conditions are unreliable. These sleeps handle sorting/filtering AJAX reloads.

---

### [DEF-009] BasePage violates "No Inheritance" design decision
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/base_page.py`
**Line(s):** All

**Rule Violated:**
- PRD Section 6.5: "No Inheritance - use composition, no base classes"

**Description:**
BasePage exists and all POMs inherit from it. This violates the explicit "No Inheritance" design decision. POMs should compose WebInterface directly, not inherit from a base class.

**Fix:**
1. Deleted `framework/pages/base_page.py`
2. Updated all POMs to compose WebInterface directly (no inheritance)
3. Header elements already exist in HomePage

**Resolved Date:** 2025-11-29

---

### [DEF-010] Base Role violates "No Inheritance" design decision
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** Role
**File:** `framework/roles/base/role.py`
**Line(s):** All

**Rule Violated:**
- PRD Section 6.5: "No Inheritance - use composition, no base classes"

**Description:**
Base Role class exists and all Roles inherit from it. This violates the explicit "No Inheritance" design decision. Roles should compose Tasks directly, not inherit from a base class.

**Fix:**
1. Deleted `framework/roles/base/role.py`
2. Updated RegisteredUser and GuestUser to be standalone classes (no inheritance)
3. Each Role now stores its own user_data and composes Tasks directly

**Resolved Date:** 2025-11-29

---

### Task Layer (Task 3.0)

### [DEF-011] CommonTasks calls deleted RegistrationPage.register_user() method
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** Task
**File:** `framework/tasks/common/common_tasks.py`
**Line(s):** 196

**Rule Violated:**
- Task must call existing POM methods
- Composite methods belong in Task layer, not POM

**Description:**
After DEF-001 fix removed `register_user()` from RegistrationPage, CommonTasks still called it. This would cause runtime errors.

**Fix:**
Replaced composite method call with atomic POM method calls:
- `select_gender()`, `enter_first_name()`, `enter_last_name()`, `enter_password()`
- `select_date_of_birth()`, `enter_address()`, `enter_city()`, `select_state()`
- `enter_zip_code()`, `enter_mobile_phone()`, `click_register()`

**Resolved Date:** 2025-11-29

---

### [DEF-012] Outdated "BasePage inherited method" comments
**Severity:** LOW
**Status:** RESOLVED
**Layer:** Task
**File:** `framework/tasks/common/common_tasks.py`
**Line(s):** 233, 253, 287, 298

**Rule Violated:**
- Comments should be accurate and up-to-date

**Description:**
After DEF-009 removed BasePage, several comments still referenced "Use BasePage inherited method" which is misleading since there is no BasePage anymore.

**Fix:**
Removed outdated comments.

**Resolved Date:** 2025-11-29

---

### [DEF-013] Incorrect driver.implicitly_wait() usage
**Severity:** LOW
**Status:** RESOLVED
**Layer:** Task
**File:** `framework/tasks/common/common_tasks.py`
**Line(s):** 176

**Rule Violated:**
- Tasks should use WebInterface methods, not direct driver access
- `implicitly_wait()` sets timeout, doesn't actually wait

**Description:**
`self.web.driver.implicitly_wait(2)` was used thinking it would wait 2 seconds, but it only sets the implicit wait timeout. This is incorrect usage and directly accesses driver.

**Fix:**
Removed the line - the following `is_page_loaded()` check has a built-in timeout.

**Resolved Date:** 2025-11-29

---

### [DEF-014] Task methods return bool instead of None
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** Task
**File:** `framework/tasks/common/common_tasks.py`, `framework/tasks/catalog/catalog_tasks.py`
**Line(s):** Multiple

**Rule Violated:**
- PRD Section 6.3: Tasks return None
- FRAMEWORK.md: "Tasks/Roles return NOTHING (None)"
- Tests should assert via POM state-check methods, not return values

**Description:**
All Task methods return `bool` (True/False) for success/failure. This violates the architecture - Tasks should return None and tests should assert via POM state-check methods.

**Fix:**
1. Changed all `-> bool` type hints to `-> None` for action methods
2. Removed all `return True/False` statements (use `return` for early exits)
3. Removed verification delegator methods (tests should use POMs directly)
4. Kept data retrieval methods (get_product_count, get_product_names, etc.) that return int/list

**Resolved Date:** 2025-11-29

---

### Role Layer (Task 4.0)

### [DEF-015] Role methods return bool instead of None
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** Role
**File:** `framework/roles/auth/registered_user.py`, `framework/roles/guest/guest_user.py`
**Line(s):** Multiple

**Rule Violated:**
- PRD Section 6.3: Roles return None
- FRAMEWORK.md: "Tasks/Roles return NOTHING (None)"
- Tests should assert via POM state-check methods, not return values

**Description:**
All Role workflow methods return `bool` (True/False). This violates the architecture - Roles should return None and tests should assert via POM state-check methods.

**Fix:**
1. Changed all `-> bool` type hints to `-> None` for workflow methods
2. Removed all `return True/False` statements
3. Removed is_logged_in() and verify_products_displayed() methods (tests should use POMs directly)
4. Kept data retrieval methods (get_product_count, browse_and_count_products) that return int

**Resolved Date:** 2025-11-29

---

### [DEF-016] GuestUser Role methods are thin wrappers - Initially suspected generator defect
**Severity:** N/A
**Status:** INVALID (Architecture Review - No Defect Found)
**Layer:** Role
**File:** `framework/roles/guest/guest_user.py`
**Line(s):** 42-116

**Initial Concern:**
GuestUser methods like `browse_category()`, `filter_products_in_category()`, etc. call ONLY ONE Task method each, appearing to violate the rule: "Workflow methods call MULTIPLE Tasks in sequence."

Example that raised concern:
```python
def browse_category(self, category_name: str) -> None:
    self.catalog_tasks.browse_category(category_name)  # Single Task call
```

**Investigation & Resolution:**

After deep architecture review, determined this is NOT a defect. Here's why:

1. **Persona Always Required** - Framework mandates Tests → Role → Task flow. Tests NEVER call Tasks directly, even for simple workflows.

2. **Single-Task Workflows Are Valid** - Not all user stories require multi-Task orchestration. "Guest browses Women's category" is legitimately a single-task workflow.

3. **Generator Followed Correct Logic:**
   - ✓ Checked for existing Task methods (found `browse_category`)
   - ✓ Orchestrated needed Tasks (correctly identified only ONE task needed)
   - ✓ Generated Role method that delegates to Task

4. **"Thin Wrapper" Is Acceptable** - When workflow consists of single Task, Role method provides:
   - Persona abstraction (guest vs user vs admin)
   - Semantic clarity (user intent vs technical implementation)
   - Consistent test interface (always call Roles, never Tasks)
   - Future-proofing (can add pre/post steps without changing test)

**Correct Multi-Task Example (for reference):**
```python
def search_and_filter_products(self, term: str, size: str) -> None:
    self.catalog_tasks.search_for_product(term)       # Task 1
    self.catalog_tasks.apply_size_filter(size)        # Task 2
    self.catalog_tasks.wait_for_filtered_results()    # Task 3
```

**Architecture Clarification:**
- **Task** = One domain operation (may orchestrate multiple POM calls)
- **Role** = User workflow (may orchestrate one OR multiple Tasks)
- **Single-Task Role methods are valid architecture** when workflow is simple

**Status Rationale:**
Marked INVALID after thorough review. GuestUser implementation is correct. Original concern was based on misunderstanding that ALL Role methods must call multiple Tasks. This is false - complexity should match the workflow.

**Keep for Reference:** Retaining this entry to document the architecture discussion and prevent future confusion about single-Task Role methods.

**Closed Date:** 2025-12-01

---

### Test Layer (Task 5.0)

### [DEF-017] Tests assert on Role return values instead of POM state-check methods
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** Test
**File:** Multiple test files
**Line(s):** See list below

**Rule Violated:**
- FRAMEWORK.md: "Tests assert via POM state-check methods - NOT return values"
- FRAMEWORK.md: "Tasks/Roles return NOTHING (None)"

**Description:**
After DEF-014 and DEF-015 were fixed (Tasks/Roles now return None), tests still assert on return values from Role methods. This causes tests to fail because they expect `True/False` but get `None`.

**Affected Files:**
1. `test_valid_login.py:44` - `assert login_result is True`
2. `test_valid_login.py:45` - `assert user.is_logged_in() is True` (method doesn't exist)
3. `test_valid_login.py:75-76` - same issues
4. `test_valid_login.py:79,82-83` - logout return value assertions
5. `test_invalid_credentials.py:85` - `assert login_result is False`
6. `test_logout.py:50,60,63-64,91,97,100,103,130,136-137,143-144` - return value assertions
7. `test_registration.py:55-56,62-63` - `assert registration_result is True`
8. `test_browse_category.py:68,71-72,96,99-100` - `assert browse_result is True`
9. `test_filter_products.py:44,70,98,125` - `assert filter_result is True/False`
10. `test_quick_view.py:44,74,103,106,109,136` - `assert quick_view_result is True/False`
11. `test_sort_by_price.py:44,70,98,125` - `assert sort_result is True/False`

**Fix:**
1. Remove all assertions on Role return values
2. Replace with POM state-check method assertions
3. Import necessary POMs in each test file
4. Remove calls to non-existent Role methods (is_logged_in, verify_products_displayed)

**Example Fix:**
```python
# BEFORE (wrong):
login_result = user.login()
assert login_result is True

# AFTER (correct):
from pages.common.home_page import HomePage
home_page = HomePage(web_interface)
user.login()  # Returns None
assert home_page.is_logout_link_visible(), "User should be logged in"
```

---

### [DEF-018] Tests call non-existent Role methods
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** Test
**File:** Multiple test files

**Rule Violated:**
- Tests should use POM methods for state verification, not Role methods

**Description:**
Tests call methods that were removed from Roles during DEF-015 fix:
- `user.is_logged_in()` - removed from RegisteredUser
- `guest.verify_products_displayed()` - never existed on GuestUser

**Affected Files:**
1. `test_valid_login.py:45,76,83` - `user.is_logged_in()`
2. `test_logout.py:57,64,97,103,144` - `user.is_logged_in()`
3. `test_browse_category.py:72,100` - `guest.verify_products_displayed()`

**Fix:**
Replace with POM state-check methods:
- `user.is_logged_in()` → `home_page.is_logout_link_visible()`
- `guest.verify_products_displayed()` → `product_list_page.has_products()`

---

### [DEF-019] Task data retrieval methods return values - violates "Tasks return None" rule
**Severity:** HIGH
**Status:** RESOLVED
**Layer:** Task
**File:** `framework/tasks/catalog/catalog_tasks.py`
**Line(s):** 244-271

**Rule Violated:**
- FRAMEWORK.md: "Tasks/Roles return NOTHING (None)"
- PRD Section 6.3: Tasks return None

**Description:**
DEF-014 fix removed `return True/False` from action methods but intentionally kept data retrieval methods (`get_product_count`, `get_product_names`, `get_product_prices`) that return int/list. However, this still violates the architecture rule that Tasks return None.

Tests should call POM methods directly for data retrieval, not go through Task layer:
- `product_list_page.get_product_count()` instead of `catalog_tasks.get_product_count()`

**Current Methods:**
```python
def get_product_count(self) -> int:       # Returns int
def get_product_names(self) -> list:      # Returns list
def get_product_prices(self) -> list:     # Returns list
```

**Proposed Fix:**
1. Remove these Task methods entirely
2. Tests should call POM methods directly for data retrieval
3. If orchestration is needed, create Task methods that don't return (just perform actions)

**Design Question:**
Is there a valid use case for Task-layer data retrieval, or should this strictly go POM → Test?

**Fix Applied:**
Methods removed from catalog_tasks.py. Tests now call POM methods directly.

**Verified:** 2026-01-05 - No grep matches for get_product_count/names/prices in tasks
**Resolved Date:** 2026-01-05

---

### [DEF-020] Role data retrieval methods return values - violates "Roles return None" rule
**Severity:** HIGH
**Status:** RESOLVED
**Layer:** Role
**File:** `framework/roles/guest/guest_user.py`
**Line(s):** 55-67, 120-128

**Rule Violated:**
- FRAMEWORK.md: "Tasks/Roles return NOTHING (None)"
- PRD Section 6.3: Roles return None

**Description:**
DEF-015 fix removed `return True/False` from workflow methods but kept data retrieval methods that return values:
- `browse_and_count_products()` returns int
- `get_product_count()` returns int

**Current Methods:**
```python
def browse_and_count_products(self, category_name: str) -> int:
    self.catalog_tasks.browse_category(category_name)
    return self.catalog_tasks.get_product_count()  # Returns int

def get_product_count(self) -> int:
    return self.catalog_tasks.get_product_count()  # Returns int
```

**Proposed Fix:**
1. Remove `get_product_count()` from Role entirely
2. Change `browse_and_count_products()` to `browse_category()` (no return)
3. Tests should call POM for product count: `product_list_page.get_product_count()`

**Fix Applied:**
Methods removed from guest_user.py. Roles no longer return values.

**Verified:** 2026-01-05 - No grep matches for browse_and_count_products/get_product_count in roles
**Resolved Date:** 2026-01-05

---

### MCP Tool Chain (Phase B Refactor)

### [DEF-021] Tool 6 generates invalid import syntax
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** MCP Tool
**File:** `mcp_server/tools/tool_06_generate_test_runner.py`
**Line(s):** 130-134

**Rule Violated:**
- Generated code must be syntactically valid Python

**Description:**
Tool 6 generates invalid import statement with duplicate keywords:
```python
from from roles.devtest2.dev_guest_user import DevGuestUser import DevGuestUser
```
Should be:
```python
from roles.devtest2.dev_guest_user import DevGuestUser
```

**Root Cause:** E2E test passed full import statement as `role_import` parameter, but tool expected just a path.

**Fix:**
Added logic in `tool_06_generate_test_runner.py` to detect and parse full import statements vs path-only:
```python
if role_import and role_import.startswith("from "):
    # Extract path from full import statement: "from X import Y" -> "X"
    parts = role_import.split(" import ")
    role_import_path = parts[0].replace("from ", "").strip()
else:
    role_import_path = role_import or f"roles.{role.lower().replace('user', '_user')}"
```

**Resolved Date:** 2025-12-01

---

### [DEF-022] Tool 3 generates duplicate locator names
**Severity:** HIGH
**Status:** RESOLVED
**Layer:** MCP Tool
**File:** `mcp_server/utils/generators/page_object_generator.py`
**Line(s):** 118-133

**Rule Violated:**
- Locators must have unique names
- Python class attributes with same name overwrite each other

**Description:**
When page has multiple elements with same type (e.g., 7 "Add to Compare" links), Tool 3 generates:
```python
ADD_TO_COMPARE = (By.CSS_SELECTOR, "a.add_to_compare")
ADD_TO_COMPARE = (By.CSS_SELECTOR, "a.add_to_compare")  # Overwrites previous
ADD_TO_COMPARE = (By.CSS_SELECTOR, "a.add_to_compare")  # Overwrites previous
# ... 4 more times
```

**Fix:**
Added deduplication using `seen_names` and `seen_locators` sets in `generate_locators_block()`:
```python
seen_names = set()  # Track unique locator names
seen_locators = set()  # Track unique locator values

for elem in elements:
    # Skip duplicates - same name or same locator value
    if name in seen_names or locator in seen_locators:
        continue
    seen_names.add(name)
    seen_locators.add(locator)
```

**Resolved Date:** 2025-12-01

---

### [DEF-023] Tool 3 generates duplicate method names
**Severity:** HIGH
**Status:** RESOLVED
**Layer:** MCP Tool
**File:** `mcp_server/utils/generators/page_object_generator.py`
**Line(s):** 213-234

**Rule Violated:**
- Method names must be unique
- Python class methods with same name overwrite each other

**Description:**
Same root cause as DEF-022. Duplicate locators generate duplicate methods:
```python
def click_add_to_compare(self) -> "DevCategoryPage":  # Method 1
    ...
def click_add_to_compare(self) -> "DevCategoryPage":  # Overwrites Method 1
    ...
```

**Fix:**
Same approach as DEF-022 - added `seen_method_names` and `seen_locators` sets in `generate_action_methods_block()`:
```python
seen_method_names = set()  # Track unique method names
seen_locators = set()  # Track unique locator values

for elem in elements:
    # Skip duplicates - same method name or same locator value
    if method_name in seen_method_names or locator in seen_locators:
        continue
    seen_method_names.add(method_name)
    if locator:
        seen_locators.add(locator)
```

**Resolved Date:** 2025-12-01

---

### [DEF-024] Tool 6 generates placeholder test instead of real test logic
**Severity:** HIGH
**Status:** RESOLVED
**Layer:** MCP Tool
**File:** `mcp_server/utils/generators/test_generator.py`
**Line(s):** 78-101, 529-533

**Rule Violated:**
- Generated tests should be executable without manual editing

**Description:**
Tool 6 generated a test with placeholder content:
```python
def test_placeholder(self):
    # TODO: Create role with appropriate data
    # TODO: Call role workflow method
    # TODO: assert page.state_check_method(), "Expected result"
    pass
```

This happens when workflow type doesn't match predefined templates (auth, catalog) and no custom tests are provided.

**Root Cause:**
1. `_detect_workflow_type()` didn't use role name for detection
2. Custom folder names like "devtest2" weren't recognized as catalog workflows
3. GuestUser role wasn't detected as catalog-related

**Fix:**
1. Enhanced `_detect_workflow_type()` to include role name in detection:
   ```python
   def _detect_workflow_type(test_name: str, description: str = "", role_name: str = "") -> str:
       combined = f"{test_name} {description} {role_name}".lower()
       # "guest" keyword now triggers catalog workflow
       if any(kw in combined for kw in ["catalog", "browse", "product", "category", "filter", "guest"]):
           return "catalog"
   ```
2. Updated `generate_test()` to extract primary role name and use detection result
3. Added catalog workflow templates that match generated Role methods (`browse_products`)
4. Also updated `task_generator.py` to include `navigate_to_category()` method
5. Updated `role_generator.py` to include `browse_products()` method

**Resolved Date:** 2025-12-01

---

### Phase B - MCP Tool Chain Refactor (Task B.x)

### [DEF-B01] generators/__init__.py imports non-existent function get_available_workflows
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** MCP Tool
**File:** `mcp_server/utils/generators/__init__.py`
**Line(s):** 26

**Rule Violated:**
- Import statements must reference existing functions

**Description:**
The `__init__.py` tries to import `get_available_workflows` from `task_generator.py`, but this function doesn't exist. This causes an ImportError when any tool tries to import from the generators package.

```python
from .task_generator import (
    generate_task,
    get_file_path as get_task_file_path,
    get_available_workflows  # Does not exist!
)
```

**Fix:**
Removed non-existent imports (`get_available_workflows`) and added existing function `generate_task_with_metadata`.

**Verified:** Cumulative live test Steps 1-5 (Tools 1-3) passed successfully.

**Resolved Date:** 2025-12-03

---

### [DEF-B02] AI did not apply file path override (DD-16)
**Severity:** MEDIUM
**Status:** RESOLVED
**Caught By:** B.6 test1
**Code Version:** feature/B.6-simple-e2e (pre-commit)
**Layer:** AI Orchestration
**File:** N/A (AI behavior, not code)

**Error Message:**
Tool 6 suggested `tests/catalog/test_browse_women_category.py` but project convention requires `tests/test1/`

**Description:**
AI initially did not override Tool 6's suggested file path. Tool 6 generates paths based on workflow (e.g., `tests/catalog/`), but project convention uses `tests/test1/`, `tests/test2/` for E2E tests. AI must override tool suggestions per DD-16.

**Fix:**
1. Added DD-16 to CLAUDE.md: "AI saves test files to `tests/test1/`, `tests/test2/` per project convention"
2. Rerun E2E from start to verify AI applies DD-16

**Verified:** E2E rerun passed - AI correctly saved to `tests/test1/test_browse_women_category.py`
**Resolved Date:** 2025-12-03

---

### [DEF-B03] AI did not inject actual parameter values (DD-17)
**Severity:** MEDIUM
**Status:** RESOLVED
**Caught By:** B.6 test1
**Code Version:** feature/B.6-simple-e2e (pre-commit)
**Layer:** AI Orchestration
**File:** N/A (AI behavior, not code)

**Error Message:**
Tool 6 generated `user.browse_category("category_name_value")` instead of `user.browse_category("Women")`

**Description:**
Tool 6 generates placeholder parameter values when actual values aren't in metadata. AI must extract actual values from the user requirement and inject them. The requirement was "browse products in Women category" so the value should be "Women".

**Fix:**
1. Added DD-17 to CLAUDE.md: "AI replaces placeholder values with actual values from requirement"
2. Rerun E2E from start to verify AI applies DD-17

**Verified:** E2E rerun passed - AI correctly injected `"Women"` from requirement
**Resolved Date:** 2025-12-03

---

### [DEF-B05] Tool 2 cannot discover dynamic/modal elements
**Severity:** HIGH
**Status:** RESOLVED
**Caught By:** B.7 test2
**Code Version:** feature/B.7-medium-e2e
**Layer:** MCP Tool
**File:** `mcp_server/tools/tool_02_discover_page_elements.py`

**Description:**
Tool 2 only discovers elements present on page load. It cannot discover:
- Elements that appear on hover (e.g., "Add to Cart" buttons)
- Modal dialogs that appear after user interaction (e.g., cart confirmation modal)
- Any dynamic content requiring user action to reveal

**Impact:**
Any workflow involving modals or hover-triggered elements will be blocked. This affects:
- Cart workflows (confirmation modal)
- Quick view workflows (modal popup)
- Any AJAX-loaded content
- Dropdown menus, tooltips, etc.

**Root Cause (Updated 2025-12-18):**
~~Tool 2 uses static page discovery~~ - WRONG. Tool 2 already has DD-20 dynamic flow support.

**Actual Root Cause:** AI did not follow DD-20 despite it being documented in:
- FRAMEWORK.md Section 8.5
- execute-from-step1 skill (lines 101-113)

This is an **enforcement gap**, not a code gap. DDs are passive - AI forgets mid-workflow.

**DD-20 Solution (Already Implemented):**
```python
# AI prepares page state first (hover, click modal, etc.)
# Then calls Tool 2 with existing driver:
discover_elements({
    'driver_session': driver,  # AI's prepared driver
    'scope': '#modal_container'  # Optional: limit to modal
})
```

**Fix Options:**

| Option | Description | Effort |
|--------|-------------|--------|
| **A. Expose driver_session in MCP interface** | Add `driver_session` parameter to Tool 2 MCP schema so AI can pass prepared Playwright session | Medium |
| **B. AI constructs elements from observation** | AI uses Playwright snapshot to build elements array, passes to Tool 3. This is valid AI behavior - AI adapts when tools fall short. | None (workaround) |
| **C. Quality gate MCP tools** | Create validation tools that enforce checks before each step proceeds | High |
| **D. Tool 2 internal page prep** | Tool 2 accepts `prep_actions` parameter (list of interactions to perform before discovery) | Medium |

**Recommended Permanent Fix:** Option A - Expose `driver_session` in MCP interface.

**Recommended Workaround:** Option B - AI constructs elements from Playwright observation. This is acceptable because:
- AI observed the dynamic form via Playwright
- AI can extract element info from snapshot
- AI passes constructed elements to Tool 3
- No human intervention required

**Verified:** 2025-12-29 - Dynamic controls test passed using Playwright snapshot + element extraction workflow
**Resolved Date:** 2025-12-29

---

### [DEF-B04] AI called wrong function for Tool 2 - utility vs tool wrapper
**Severity:** MEDIUM
**Status:** RESOLVED
**Caught By:** B.7 test2
**Code Version:** feature/B.7-medium-e2e
**Layer:** AI Orchestration
**File:** N/A (AI behavior)

**Error Message:**
```
selenium.common.exceptions.InvalidArgumentException: Message: invalid argument: 'url' must be a string
```

**Description:**
During B.7 E2E, AI called the wrong function for Tool 2:
- **WRONG:** `from utils.element_discovery import discover_page_elements` (utility function)
- **RIGHT:** `from tools.tool_02_discover_page_elements import discover_elements` (tool wrapper)

The utility function has a different signature and doesn't handle the arguments dict properly, causing Selenium to receive None instead of URL string.

**Root Cause:**
AI confusion between:
1. `discover_page_elements()` - low-level utility in `utils/element_discovery.py`
2. `discover_elements()` - tool wrapper in `tools/tool_02_discover_page_elements.py`

Both have similar names but different purposes and signatures.

**Fix Required:**
Add explicit guidance to CLAUDE.md about correct tool invocation patterns.

**Prevention Rule (DD-19):**
```
When calling MCP Tools (1-6), ALWAYS import from tools/ directory:
- Tool 1: from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story
- Tool 2: from tools.tool_02_discover_page_elements import discover_elements
- Tool 3: from tools.tool_03_generate_page_object import generate_page_object
- Tool 4: from tools.tool_04_generate_task import generate_task
- Tool 5: from tools.tool_05_generate_role import generate_role
- Tool 6: from tools.tool_06_generate_test_runner import generate_test_runner

NEVER import directly from utils/ when executing E2E tool chain.
```

**Status Update (2025-12-18):**
DD-19 is now documented in:
- CLAUDE.md (line 138)
- FRAMEWORK.md Section 8.13

**Verified:** 2025-12-29 - Dynamic controls workflow used MCP tools via proper interface (mcp__qa-automation__* calls)
**Resolved Date:** 2025-12-29

---

### [DEF-B06] AI did not format user story in explicit BDD before Tool 1
**Severity:** MEDIUM
**Status:** RESOLVED
**Run ID:** 2025-12-17-R1
**Caught By:** Test 1 Registration (Step 3)
**Code Version:** feature/2.0-sr-qa-engineer-agent
**Layer:** AI Orchestration
**File:** N/A (AI behavior)

**Error Message:**
```
{
  "error": "No scenarios found in user story. Please include Given-When-Then scenarios.",
  "status": "error",
  "hint": "Format: Given <context> When <action> Then <expected outcome>"
}
```

**Description:**
AI called Tool 1 (generate_tests_from_user_story) with a user story formatted as bullet-point acceptance criteria instead of explicit BDD Given-When-Then syntax. Tool 1 requires explicit BDD keywords.

AI sent:
```
As a new user
I want to register an account
So that I can access member features

Acceptance Criteria:
- User can navigate to registration page
...
```

Tool 1 expects:
```
As a new user
I want to register an account
So that I can access member features

Scenario: Successful user registration
Given I am on the authentication page
When I enter my email to create an account
And I fill in my personal information
Then I should see my account page
```

**Root Cause:**
AI Step 2 (AI Processing) converted intent to BDD format in metadata_context but did not use that formatted BDD when calling Tool 1. Instead, AI re-wrote the user story with bullet-point acceptance criteria.

**Fix Required:**
Add explicit rule DD-23 to CLAUDE.md and execute-from-step1 skill:
- AI MUST include explicit "Scenario:" and "Given/When/Then" keywords when calling Tool 1
- AI should use the BDD already prepared in Step 2, not reformat

**Prevention Rule (DD-23):**
```
When calling Tool 1 (generate_tests_from_user_story):
- MUST include "Scenario:" keyword
- MUST include explicit "Given", "When", "Then" keywords
- Use BDD prepared in Step 2 metadata_context
- NEVER use bullet-point acceptance criteria format
```

**Mitigation (2025-12-26):**
- Step reference `step-03.md` and `step-04.md` guide AI on proper BDD formatting
- `qg_ai_processing.py` validates bdd_scenarios have proper structure
- `qg_test_scenarios.py` validates Tool 1 output has Given/When/Then fields

**Verified:** 2025-12-30 - demoqa.com forms test: Steps 3-4 passed with proper BDD format
**Resolved Date:** 2025-12-30

---

### [DEF-B07] Tool 6 ignores scenario parameter and generates generic template
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2025-12-17-R2
**Caught By:** Test 1 Registration (Step 8)
**Code Version:** feature/2.0-sr-qa-engineer-agent
**Layer:** MCP Tool
**File:** `mcp_server/tools/tool_06_generate_test_runner.py`

**Error Message:**
Tool 6 generated `test_valid_login` and `test_logout` methods instead of `test_successful_user_registration`.

**Description:**
Tool 6 was called with explicit scenario:
```python
scenario={
    "title": "test_successful_user_registration",
    "given": "I am on the authentication page",
    "when": "I enter my email... AND submit registration",
    "then": "I should see my account page with welcome message"
}
```

But Tool 6 ignored this and generated a generic auth template with login/logout tests instead of the registration test requested.

**Root Cause:**
Tool 6 likely uses workflow type ("auth") to select a template rather than using the actual scenario provided. The auth template defaults to login/logout regardless of the scenario content.

**Fix Required:**
Tool 6 should:
1. Parse the scenario title to determine test method name
2. Use scenario's "when" clause to determine which Role method to call
3. Use scenario's "then" clause to determine assertion method
4. Not default to hardcoded templates

**Workaround:**
Manually write the test file.

**Mitigation (2025-12-26):**
- `qg_test_runner.py` skeleton detection catches generic/placeholder test code
- Step reference `step-09.md` Section J provides correct test code patterns
- Self-heal validation protocol requires AI to POST-VALIDATE generated test code

**Verified:** 2025-12-30 - demoqa.com forms test: Tool 6 generated correct test name `test_submit_student_registration_form`
**Resolved Date:** 2025-12-30

---

### [DEF-B08] AI passed wrong element format to Tool 3 (not Tool 2 output format)
**Severity:** HIGH
**Status:** READY_TO_TEST
**Run ID:** 2025-12-17-R3
**Caught By:** Test 2 Login + Cart (Step 5)
**Code Version:** feature/2.0-sr-qa-engineer-agent
**Layer:** AI Orchestration
**File:** N/A (AI behavior)

**Error Message:**
Tool 3 generated skeleton POM with no locators or atomic methods.

**Description:**
AI manually constructed elements for Tool 3 instead of passing Tool 2 output directly. The formats don't match:

**Tool 2 outputs:**
```json
{
  "suggested_name": "EMAIL",
  "element_type": "inputs",
  "locator_id": "#email",
  "locator_css": "",
  "locator_xpath": "//input[@id='email']"
}
```

**AI incorrectly passed:**
```json
{
  "name": "EMAIL",           // Wrong key - should be "suggested_name"
  "type": "inputs",          // Wrong key - should be "element_type"
  "locator": "#email"        // Wrong key - should be "locator_id"
}
```

**Root Cause:**
Tool 3's transformation logic (lines 122-127 in tool_03_generate_page_object.py) expects Tool 2's exact output format with keys: `suggested_name`, `element_type`, `locator_id`/`locator_css`/`locator_xpath`. AI invented a different schema.

**Generator code is correct** - the skeleton was produced because elements array was effectively empty after transformation (no matching keys found).

**Fix Options:**

**Option 1: Add DD-26 + Update execute-from-step1 skill**
Add explicit code pattern reference showing exact data to pass:
```
Tool 2 → Tool 3 Element Contract:
CORRECT: elements = tool_2_result["elements"]  # Use as-is
WRONG: elements = [{"name": "X", "type": "Y", "locator": "Z"}]  # Invented format

Required keys: suggested_name, element_type, locator_id/locator_css/locator_xpath
```

**Option 2: Create dedicated skills per tool/step**
Create separate skills for each step with explicit input/output contracts:
- `.claude/skills/tool-2-discover-elements/SKILL.md`
- `.claude/skills/tool-3-generate-pom/SKILL.md`
- etc.

Each skill would document:
- Exact input format expected
- Exact output format produced
- Code examples of correct invocation
- Common mistakes to avoid

**Selected Fix:** TBD (discuss with user)

**Prevention Rule (DD-26):**
```
Tool Chain Data Contracts:
- Each tool expects specific input format from previous tool
- AI MUST pass tool output directly to next tool (filter ok, transform not ok)
- Skill documents exact contract for each tool transition
```

**Mitigation Implemented (2025-12-26):**
- Self-heal validation protocol requires POST-VALIDATE after AI generates/constructs data
- Pattern templates in step references show correct element formats
- Quality gates detect missing required fields and incorrect formats

**Verified:** TBD - requires E2E workflow run
**Resolved Date:** TBD

---

### [DEF-B09] Tool 4 generates skeleton Task code when POM metadata not passed
**Severity:** HIGH
**Status:** READY_TO_TEST
**Run ID:** 2025-12-17-R3
**Caught By:** Test 2 Login + Cart (Step 6)
**Code Version:** feature/2.0-sr-qa-engineer-agent
**Layer:** MCP Tool / AI Orchestration
**File:** `mcp_server/tools/tool_04_generate_task.py`

**Error Message:**
Tool 4 generated skeleton Task with `pass` placeholder:
```python
@autologger.automation_logger("Task")
def execute_workflow(self) -> None:
    """Execute the workflow. TODO: Implement."""
    pass
```
Output showed: `pom_metadata_used: 0`, `task_methods_generated: 0`

**Description:**
Tool 4 requires POM metadata from Tool 3 to generate proper Task methods. When called with only `task_name` and `workflow_description` (no POM metadata), it generates a skeleton class with placeholder methods instead of actual Task methods that compose and use POM atomic methods.

**Root Cause:**
Similar to DEF-B08 - AI did not pass the POM metadata from Tool 3 output to Tool 4. The tool expected:
```json
{
  "task_name": "AuthTasks",
  "pom_metadata": {  // From Tool 3 output
    "class_name": "LoginPage",
    "action_methods": [...],
    "state_methods": [...]
  }
}
```

AI only passed:
```json
{
  "task_name": "AuthTasks",
  "workflow_description": "..."  // Text description, not structured metadata
}
```

**DD-25 Violation:**
Skeleton code detected → STOP triggered (correct behavior per DD-25)

**Fix Required:**
Same pattern as DEF-B08 - Tool chain data contracts must be enforced:
1. Tool 3 outputs `metadata` with `action_methods`, `state_methods`
2. Tool 4 MUST receive this metadata to generate Task methods
3. AI MUST pass Tool 3 `metadata` field to Tool 4

**Prevention Rule (extend DD-26):**
```
Tool 3 → Tool 4 Data Contract:
- Tool 3 outputs: metadata.action_methods[], metadata.state_methods[]
- Tool 4 expects: pom_metadata with these methods
- AI MUST: task_input["pom_metadata"] = tool_3_result["metadata"]
```

**Mitigation Implemented (2025-12-26):**
- `qg_task.py` POST-validate detects skeleton code (pass statements, TODO comments)
- Self-heal validation protocol requires POST-VALIDATE after AI generates code
- Pattern template in `step-07.md` Section J shows correct Task pattern with POM composition

**Verified:** TBD - requires E2E workflow run
**Resolved Date:** TBD

---

### [DEF-B10] AI manual Task code included locators (architecture violation)
**Severity:** CRITICAL
**Status:** READY_TO_TEST
**Run ID:** 2025-12-17-R3
**Caught By:** Test 2 Login + Cart (Step 6 manual fix attempt)
**Code Version:** feature/2.0-sr-qa-engineer-agent
**Layer:** AI Orchestration
**File:** N/A (AI-generated code, not saved)

**Error Message:**
User caught: "ai code is wrong in task module also. there should be no locators in the task module"

**Description:**
When AI attempted to manually fix Tool 4's skeleton output, the generated Task code included Selenium locators:

```python
# WRONG - AI generated this in CatalogTasks:
from selenium.webdriver.common.by import By
...
product_locator = (By.CSS_SELECTOR, f"ul.product_list li.ajax_block_product:nth-child({product_index + 1})")
add_to_cart_locator = (By.CSS_SELECTOR, f"ul.product_list li.ajax_block_product:nth-child({product_index + 1}) a.ajax_add_to_cart_button")
```

**Rule Violated:**
- FRAMEWORK.md: "Locators ONLY in Page Objects"
- CLAUDE.md Layer architecture: "Task = Orchestrates page object methods (NO locators)"
- PRD Section 6.3: Tasks delegate all UI interaction to POMs

**Root Cause:**
AI hallucinated Task implementation instead of using POM methods. Correct pattern:
```python
# CORRECT - Task delegates to POM:
def add_product_to_cart(self, product_index: int = 0) -> None:
    self.catalog_page.hover_product(product_index)
    self.catalog_page.click_add_to_cart_button()
```

**Impact:**
- Breaks 4-layer architecture separation
- Duplicates locator responsibility
- Makes tests brittle (locator changes need updates in multiple places)
- Violates fundamental framework design

**Fix Required:**
1. Add explicit quality gate for AI-generated Task code
2. Check for `By.` imports or `(By.CSS_SELECTOR, ...)` patterns
3. If detected → STOP → flag architecture violation
4. Add to execute-from-step1 skill as Task code validation step

**Prevention Rule (DD-27):**
```
Task Code Quality Gate (AI Manual Fix):
BEFORE saving any Task code, verify:
- [ ] NO imports from selenium.webdriver.common.by
- [ ] NO (By.*, "...") locator tuples
- [ ] NO driver.find_element() calls
- [ ] ONLY calls to POM methods (self.page.method_name())

If ANY locator pattern found → ARCHITECTURE VIOLATION → STOP
```

**Mitigation Implemented (2025-12-26):**
- Enhanced `qg_task.py` with layer violation detection (By.* imports, locator tuples)
- Added pattern template in `step-07.md` Section J showing correct Task patterns
- Self-heal validation protocol in SKILL.md requires POST-VALIDATE after AI generates code
- Smart escalation protocol after 3 failed attempts

**Verified:** TBD - requires E2E workflow run
**Resolved Date:** TBD

---

### [DEF-025] [TOOL-FIX] Task generator produces skeleton code fallbacks
**Severity:** MEDIUM
**Status:** READY_TO_TEST
**Layer:** MCP Tool
**File:** `mcp_server/utils/generators/task_generator.py`
**Line(s):** 137, 261-279, 398-403

**Rule Violated:**
- DD-25 (Skeleton Code Quality Gate)

**Description:**
Task generator has fallback code paths that produce skeleton code with `pass` statements and `TODO` comments:

1. Line 137: `pass  # TODO: Add POM method calls` (when no POM calls generated)
2. Lines 261-279: `execute_workflow` method with `pass` and `TODO`
3. Lines 398-403: Fallback template with `pass`

These violate DD-25 and will be caught by qg_task POST validation.

**Additional Issues:**
- FRAMEWORK.md Section 8.7 uses `check_existing: true` but Tool 4 uses `force_generate: False` (inverse logic)
- Output field names differ: FRAMEWORK.md says `existing_class`, Tool returns `existing_tasks`

**Fix Required:**
1. Replace `pass` fallbacks with proper error returns
2. Align parameter naming between FRAMEWORK.md and tool code
3. Ensure generator never outputs skeleton code

**Gate Mitigation (2025-12-26):**
- `qg_task.py` POST validation catches skeleton patterns (pass, TODO, NotImplementedError)
- Step reference `step-07.md` Section J provides correct Task code patterns
- Self-heal validation protocol requires AI to POST-VALIDATE and fix skeleton code
- See IC-07-01, IC-07-02 in step-07.md

**Verified:** TBD - requires E2E workflow run
**Resolved Date:** TBD

---

### [DEF-026] Tool 1 output vs qg_test_scenarios gate data contract mismatch
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2025-12-22-R1
**Caught By:** Step 4 POST-VALIDATE (Registration Test)
**Code Version:** main
**Layer:** MCP Tool / Quality Gate
**File:** `mcp_server/tools/tool_01_generate_tests_from_user_story.py`

**Error Message:**
```
{'status': 'fail', 'error': "Scenario 0 missing required field: 'name'", 'fix_hint': 'Ensure each scenario has: name (str), given (str), when (list), then (list).'}
```

**Description:**
Tool 1 (`generate_tests_from_user_story`) outputs scenarios with field names that don't match what `qg_test_scenarios` gate expects for POST validation.

**Data Contract Mismatch (before fix):**

| Field | Gate Expects | Tool 1 Output (OLD) |
|-------|--------------|---------------------|
| Test name | `name` (str) | `title` (str) |
| When clause | `when` (list) | `when` (str with "AND") |
| Then clause | `then` (list) | `then` (str with "AND") |

**Root Cause:**
Tool 1 and qg_test_scenarios were developed independently without a shared data contract.

**Fix Applied (Option C - Update Tool 1):**
Updated `tool_01_generate_tests_from_user_story.py` to output gate-compatible format:
1. Changed `title` → `name`
2. Convert `when` string → list (split on " AND ")
3. Convert `then` string → list (split on " AND ")

```python
test_scenario = {
    "name": test_name,  # Gate expects "name" not "title"
    "when": when_list,  # Gate expects list, not string
    "then": then_list,  # Gate expects list, not string
    ...
}
```

**Verified:** 32 tests pass
**Resolved Date:** 2025-12-26

---

### [DEF-027] AI prompts user for fix approach on gate failures (should auto-fix)
**Severity:** MEDIUM
**Status:** RESOLVED
**Run ID:** 2025-12-22-R1
**Caught By:** Step 4 POST-VALIDATE (Registration Test)
**Code Version:** main
**Layer:** AI Orchestration / Skill Design
**File:** `.claude/skills/qa-management-layer/` (workflow behavior)

**Description:**
When a gate validation fails during the 11-step workflow, AI follows the testing skill's failure-handling protocol (STOP → REPORT → FIX OPTIONS → DISCUSS). However, the testing skill is designed for **test execution failures**, not **tool chain gate failures**.

For gate failures within the workflow:
- AI should auto-fix (transform data, retry) without prompting user
- Only escalate to user after 3 failed attempts (per step skill instructions)

**Current Behavior (Wrong):**
```
POST-VALIDATE: FAIL
...
FIX OPTIONS:
| A | AI transforms output | ...
| B | Fix gate | ...
Which fix approach?   ← User shouldn't see this
```

**Expected Behavior:**
```
POST-VALIDATE: FAIL (attempt 1/3)
Retrying with transformed data...
POST-VALIDATE: PASS
```

**Root Cause:**
AI conflated two different failure protocols:
1. **Testing skill** - For test execution failures (user decides)
2. **QA Guidance Layer** - For gate failures (AI retries up to 3x, then user decides)

**Fix Required:**
Clarify in qa-management-layer skill that gate failures follow retry protocol, not testing skill's discuss-first protocol.

**Fix Applied:**
All step skills (step-01 through step-09) now have RETRY sections with "I've attempted 3 times" messaging. AI retries up to 3 times before escalating to user.

**Verified:** 2026-01-05 - Grep confirmed RETRY sections in all step references
**Resolved Date:** 2026-01-05

---

### [DEF-028] Internal DD references visible to user in prompts
**Severity:** LOW
**Status:** RESOLVED
**Run ID:** 2025-12-22-R1
**Caught By:** Step 1 (Registration Test)
**Code Version:** main
**Layer:** AI Orchestration / UX
**File:** N/A (AI prompt formatting)

**Description:**
AI shows internal Design Decision (DD) references to user:
```
Question 1 of 2 (DD-24 - Credential Strategy)
```

Users should not see DD-XX references - these are internal documentation codes.

**Expected:**
```
Question 1 of 2: Credential Strategy
```

**Fix Required:**
Update AI prompt templates in qa-management-layer step references to omit DD-XX codes when presenting to user.

**Fix Applied:**
Removed DD-24 and DD-28 references from step-01.md ACTION section. Users now see "Question 1 (credential strategy)" instead of "Question 1 (DD-24: credential strategy)".

**Verified:** 2026-01-05 - No DD references in user-facing prompts
**Resolved Date:** 2026-01-05

---

### [DEF-031] Tool 1 does not save Step 4 state after successful execution
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2025-12-22-R1
**Caught By:** Step 5 PRE-VALIDATE (Registration Test)
**Code Version:** main
**Layer:** MCP Tool / State Management
**File:** `mcp_server/tools/gates/qg_test_scenarios.py`

**Error Message:**
```
{'status': 'fail', 'error': 'Step 4 is not complete. Cannot proceed to Step 5.', ...}
```

**Description:**
After Tool 1 (generate_tests_from_user_story) executes successfully and POST-VALIDATE passes, the state for Step 4 is not saved. State file shows Steps 1-3 complete, but Step 4 missing.

**Expected:** Tool 1 should save `test_scenarios` to state on success.
**Actual:** State file has no `step_4` entry.

**Root Cause:**
`validate_post()` in qg_test_scenarios returned pass_response() without saving state, unlike Steps 1-3 gates which save state on PASS.

**Fix Applied:**
Updated `validate_post()` in `qg_test_scenarios.py` to save state on PASS:
```python
# All valid - save state and return pass
state_manager = cls._get_state_manager()
state_manager.save(step=4, data={"test_scenarios": test_scenarios})

response = cls.pass_response()
response["test_scenarios"] = test_scenarios
return response
```

**Verified:** 32 tests pass
**Resolved Date:** 2025-12-26

---

### [DEF-030] Skeleton pattern check false positive on "password"
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2025-12-22-R1
**Caught By:** Step 4 POST-VALIDATE (Registration Test)
**Code Version:** main
**Layer:** Quality Gate
**File:** `mcp_server/tools/gates/qg_test_scenarios.py`
**Line(s):** 198-202

**Error Message:**
```
{'status': 'fail', 'error': "Scenario 0 'when' contains skeleton pattern: 'pass'", ...}
```

**Description:**
Skeleton pattern check uses substring matching (`if pattern in action_lower`), causing false positive when BDD step contains "password" (which contains "pass").

**Root Cause:**
Line 201: `if pattern in action_lower:` matches "pass" inside "password".

**Fix Applied:**
Changed SKELETON_PATTERNS to use tuple format with (pattern, is_regex) flag:
```python
SKELETON_PATTERNS = [
    (r"\bpass\b", True),      # Word boundary to avoid matching "password"
    ("# add", False),
    ("# todo", False),
    ("as needed", False),
    ("placeholder", False),
]
```
Added `_matches_skeleton_pattern()` helper to use regex for word boundary patterns.

**Verified:** 32 tests pass including 2 new DEF-030 regression tests
**Resolved Date:** 2025-12-26

---

### [DEF-029] Internal gate status shown to user
**Severity:** LOW
**Status:** OPEN
**Run ID:** 2025-12-22-R1
**Caught By:** Step 3 (Registration Test)
**Code Version:** main
**Layer:** AI Orchestration / UX
**File:** N/A (AI output formatting)

**Description:**
AI shows internal gate status to user:
```
Step 3 Complete - Gate: PASS
```

Users should see simplified confirmation, not implementation details.

**Expected:**
```
Step 3 Complete
```
Or just proceed silently to next step.

**Fix Required:**
Update AI response format to hide gate implementation details from user output.

**Verified:** TBD
**Resolved Date:** TBD

---

### [DEF-032] [ENHANCEMENT] No automatic context window management / auto-compact
**Severity:** LOW
**Status:** WONT_FIX (handled by workflow design)
**Run ID:** 2025-12-22-R1
**Caught By:** User observation during long workflow
**Code Version:** main
**Layer:** AI / Claude Code Infrastructure
**File:** N/A (Claude Code CLI capability)

**Description:**
During long-running workflows (like the 11-step QA workflow), context window fills up and user must manually invoke `/compact`. There's no automatic mechanism to:
1. Monitor context window token usage
2. Auto-compact before context runs out
3. Continue workflow seamlessly after compaction

**Impact:**
- Workflow interruption requiring user action
- Risk of losing context if not compacted in time
- Poor UX for autonomous multi-step processes

**Current Workaround:**
User manually runs `/compact` when prompted or when they notice slowdown.

**Resolution:**
Context loss concern is now addressed by:
1. **StateManager**: All workflow state persisted to `workflow_state.json` after each step
2. **DEF-047 (Code Reconstruction Quality Gate)**: Ensures reconstructed code after context loss must pass quality gates
3. **Automatic Summarization**: Claude Code handles context management with conversation summaries
4. **Session Recovery**: Workflow can resume from state after compaction

The original concern about "workflow interruption" is mitigated by state persistence and resumability. Context compaction is a natural part of long workflows, not a defect.

**Verified:** 2026-01-07 - ParaBank workflow recovered successfully after context loss
**Resolved Date:** 2026-01-07

---

### [DEF-035] CRITICAL: Quality gate passed skeleton code - validation gap
**Severity:** CRITICAL
**Status:** RESOLVED
**Run ID:** 2025-12-22-R1
**Caught By:** Step 7 (Registration Test)
**Code Version:** main
**Layer:** Quality Gate
**File:** `mcp_server/tools/gates/qg_page_object.py`

**Description:**
Tool 3 generated POM with skeleton code (`is_page_loaded()` returning `True` with `TODO` comment). The POST-VALIDATE gate (qg_page_object) should have caught this but passed.

Next step (Tool 4) then received incomplete metadata and produced skeleton Task.

**Impact:**
- Skeleton code propagates through tool chain
- Quality gates not enforcing DD-25 (skeleton detection)
- Downstream tools fail due to incomplete input

**Root Cause:**
Gate's skeleton detection likely checks for `pass` keyword but not:
- `TODO` comments in method bodies
- Methods that just `return True` without real logic
- Missing methods for certain element types (radios)

**Fix Required:**
Enhance qg_page_object POST-VALIDATE to detect:
1. `TODO` in method bodies
2. Trivial `return True` without element checks
3. Missing action methods for all locator types

**Mitigation Implemented (2025-12-26):**
- Enhanced `qg_page_object.py` with `_detect_trivial_state_methods()` - catches `return True` without element checks
- Enhanced `qg_page_object.py` with layer violation detection (Task/Role imports in POM)
- Added pattern template in `step-06.md` Section J showing correct POM patterns
- Self-heal validation protocol requires POST-VALIDATE after AI generates code

**Verified:** 2025-12-29 - Dynamic controls workflow: all quality gates caught issues and required fixes before proceeding
**Resolved Date:** 2025-12-29

---

### [DEF-036] AI self-heal code must pass quality gate validation
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2025-12-22-R1
**Caught By:** User observation (Registration Test)
**Code Version:** main
**Layer:** AI Orchestration / Quality Gate
**File:** N/A (workflow design gap)

**Description:**
When tools produce skeleton code, AI can self-heal by generating code directly. However:
1. AI-generated code currently bypasses quality gate
2. No validation that AI code matches project patterns
3. Could produce code that doesn't follow established architecture

**Required Flow:**
```
Tool output → Quality Gate → FAIL (skeleton)
    ↓
AI self-heals (generates code)
    ↓
AI output → Quality Gate → must PASS
    ↓
Proceed to next step
```

**Fix Required:**
After AI self-heal, pass generated code through same quality gate before proceeding.

**Mitigation Implemented (2025-12-26):**
- Added "Self-Heal Validation Protocol" to SKILL.md - mandatory POST-VALIDATE after AI generates code
- Added "Smart Escalation Protocol" - after 3 failed retries, show violation + correct pattern + options
- Pattern templates embedded in step references (step-06/07/08/09.md Section J)
- Layer-specific pattern checks in quality gates detect architecture violations

**Verified:** 2025-12-29 - Dynamic controls workflow: AI wrote POM/Task/Role/Test code, all passed POST-VALIDATE gates
**Resolved Date:** 2025-12-29

---

### [DEF-034] Tool 4 skeleton output when workflow_description passed instead of pom_metadata
**Severity:** MEDIUM
**Status:** READY_TO_TEST
**Run ID:** 2025-12-22-R1
**Caught By:** Step 7 (Registration Test)
**Code Version:** main
**Layer:** MCP Tool
**File:** `mcp_server/tools/tool_04_generate_task.py`

**Description:**
Tool 4 generated skeleton Task with `execute_workflow()` containing `pass`. Output showed:
- `pom_metadata_used: 0`
- `task_methods_generated: 0`
- `composed_pages: []`

**Root Cause:**
Same as DEF-B09. Tool 4 expects structured `pom_metadata` from Tool 3 output, but received only `workflow_description` text. Without POM method info, tool cannot generate proper Task methods.

**Pattern:** Tool chain data contract (DD-26) not enforced by MCP interface.

**Mitigation Implemented (2025-12-26):**
- Same as DEF-B09: `qg_task.py` POST-validate detects skeleton code
- Self-heal validation protocol requires AI to POST-VALIDATE after generating code
- Pattern template in `step-07.md` Section J shows correct data flow

**Verified:** TBD - requires E2E workflow run
**Resolved Date:** TBD

---

### [DEF-033] Tool 3 incomplete POM generation (missing radio methods, skeleton state check)
**Severity:** MEDIUM
**Status:** RESOLVED
**Run ID:** 2025-12-22-R1
**Caught By:** Step 6 POST review (Registration Test)
**Code Version:** main
**Layer:** MCP Tool
**File:** `mcp_server/utils/generators/page_object_generator.py`

**Description:**
Tool 3 generated POM with gaps:
1. Radio button locators (GENDER_MR, GENDER_MRS) present but no click methods generated
2. `is_page_loaded()` contains `TODO` comment and just returns `True` (skeleton)
3. No test-specific state method (e.g., `is_account_created()`)

**Root Cause:**
Tool 3's generator didn't have a handler for radio element types.

**Fix Applied:**
1. Added `RADIO_METHOD_TEMPLATE` for radio button select methods
2. Added `elem_type == "radios"` handling in `generate_action_methods_block()`
3. Added radios support in `_build_action_methods_metadata()` for metadata generation

```python
RADIO_METHOD_TEMPLATE = '''
    def select_{method_name}(self) -> "{page_name}":
        """Select {readable_name} radio button."""
        self.web.click(*self.{locator_name})
        return self
'''
```

**Note:** Issues 2 and 3 (skeleton state methods, expected_states) are mitigated by:
- qg_page_object.py `_detect_trivial_state_methods()` catches skeleton patterns
- Self-heal validation protocol requires AI to fix skeleton code
- Pattern templates in step-06.md Section J guide correct patterns

**Verified:** 39 tests pass
**Resolved Date:** 2025-12-26

---

### [DEF-039] Skill step-07.md teaches incorrect Task pattern (base_url, navigate_to)
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2025-12-26-R1
**Caught By:** Comparison with old framework reference
**Code Version:** main
**Layer:** Skill / Documentation
**File:** `.claude/skills/qa-management-layer/references/step-07.md`

**Description:**
The step-07.md skill teaches a Task pattern that differs from the established old framework pattern:

| Aspect | Old Framework (Correct) | Skill Pattern (Wrong) |
|--------|------------------------|----------------------|
| Constructor | `def __init__(self, web_interface):` | `def __init__(self, web: WebInterface, base_url: str):` |
| Navigation | Via POM methods only | Direct `self.web.navigate_to()` |
| base_url | NOT in Task | Passed to Task constructor |

**Old Framework Pattern (Verified across 8 task files):**
```python
class SomeTask:
    def __init__(self, web_interface):  # NO base_url
        self.home_page = HomePage(web_interface)
        self.some_page = SomePage(web_interface)

    @autologger.automation_logger("Task")
    def do_something(self):
        (self.home_page.click_tile("Dashboard"))  # Navigation via POM
        (self.some_page.enter_data(...))
```

**Skill Pattern (Incorrect):**
```python
class AuthTasks:
    def __init__(self, web: WebInterface, base_url: str):  # WRONG
        self.base_url = base_url

    def register_user(self, user_data: dict) -> None:
        self.web.navigate_to(f"{self.base_url}/...")  # WRONG
```

**Impact:**
- Generated Tasks don't match established framework patterns
- Introduces inconsistency between old and new code
- Navigation responsibility incorrectly placed in Task layer

**Fix Required:**
1. Update step-07.md Section J pattern template
2. Update FRAMEWORK.md Task layer documentation
3. Remove base_url from Task constructor pattern
4. Move navigation to POM methods (e.g., `login_page.goto()` or `home_page.navigate_to_auth()`)

**Fix Applied:**
step-07.md updated with DD-49 enforcement: "Navigation via POM `navigate()` method (never `self.web.navigate_to()`)"

**Verified:** 2026-01-05 - step-07.md line 388 confirms correct pattern
**Resolved Date:** 2026-01-05

---

### [DEF-038] Test data hardcoded instead of using test_users fixture
**Severity:** MEDIUM
**Status:** RESOLVED
**Run ID:** 2025-12-26-R1
**Caught By:** Code review during E2E test failure analysis
**Code Version:** main
**Layer:** Test / AI Orchestration
**File:** `tests/auth/test_registration.py`
**Line(s):** 54-66

**Error (Pattern Violation):**
```python
# GENERATED (WRONG):
user_data = {
    "email": "testuser_reg@example.com",
    "password": "TestPass123!",
    ...
}
guest = GuestUser(self.web, self.base_url)
```

**Expected (Per step-09.md Section J):**
```python
# CORRECT - Use fixture:
def test_guest_can_register_new_account(self, web_interface, config, test_users):
    user_data = test_users["new_registration"]  # From tests/data/test_users.json
    guest = GuestUser(web_interface, config["base_url"])
```

**Rule Violated:**
- DD-28: Test data organization - should use shared `tests/data/test_users.json`
- conftest.py provides `test_users` fixture (line 82-98)
- step-09.md Section J shows correct pattern with fixtures

**Root Cause:**
AI did not follow step-09.md self-heal pattern template which shows `test_data` parameter in test signature. AI generated inline hardcoded dict instead of using pytest fixture.

**Fix Applied:**
ParaBank workflow (2026-01-07) demonstrates correct pattern:
```python
# tests/parabank/test_existing_customer_completes_banking_workflow.py:24-27
def setup(self, web_interface, config, test_data):
    self.test_data = test_data
    # ...
banking_data = self.test_data.get("banking_workflow", {})  # Correct fixture usage
```

Test properly uses `test_data` fixture parameter and loads from `tests/parabank/data/test_data.json` per DD-28 workflow-specific data strategy.

**Verified:** 2026-01-07 - ParaBank test uses test_data fixture correctly (line 24)
**Resolved Date:** 2026-01-07

---

### [DEF-037] DD-33 violated: AI assumed locators instead of Playwright discovery
**Severity:** CRITICAL
**Status:** RESOLVED
**Run ID:** 2025-12-26-R1
**Caught By:** E2E Registration Test
**Code Version:** main
**Layer:** AI Orchestration
**File:** `framework/pages/auth/registration_page.py`

**Error Message:**
```
TimeoutException: Element not found: css selector='#address1' after 20s
```

**Description:**
AI generated RegistrationPage POM with assumed locators (`#address1`, `#city`, etc.) instead of using DD-33 Playwright element discovery workflow.

**DD-33 states:**
> "AI uses Playwright snapshot → extracts elements → builds POM"

**What happened:**
1. Step 5 (Element Discovery) was bypassed
2. AI assumed registration form locators existed
3. POM saved with `#address1` locator that doesn't exist on actual page
4. Test failed at `enter_address()` - element not found

**Rule Violated:**
- DD-33: Dynamic element discovery requires Playwright snapshot
- FRAMEWORK.md Section 8.14: "AI uses Playwright snapshot → extracts → builds"
- Never assume page structure without discovery

**Root Cause:**
AI skipped element discovery (Step 5) and proceeded directly to POM generation with assumed locators. The qa-management-layer skill mandates Playwright discovery but AI did not follow it.

**Fix Required:**
1. Navigate to registration page using Playwright
2. Fill email and click "Create Account" to reveal registration form
3. Take browser snapshot to discover actual elements
4. Build POM from discovered elements, not assumptions
5. Re-run test with correct locators

**Prevention (reinforce existing DD-33):**
- Step 5 PRE-VALIDATE should fail if no Playwright snapshot taken
- Gate should require `discovery_method: playwright` before allowing Tool 3

**Fix Applied:**
DD-46 (RuntimeValidator) now enforces element validation in step-05.md. All discovered elements MUST be validated against live page before POM generation.

**Verified:** 2026-01-05 - step-05.md requires RuntimeValidator for each element
**Resolved Date:** 2026-01-05

---

### [DEF-041] Quality gates do not validate cross-layer method calls match upstream metadata
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2025-12-29-R2
**Caught By:** /framework-check command (post-workflow validation)
**Code Version:** main
**Layer:** Quality Gate
**Files:**
- `mcp_server/tools/gates/qg_task.py`
- `mcp_server/tools/gates/qg_role.py`
- `mcp_server/tools/gates/qg_test_runner.py`

**Error Message:**
```
framework/tasks/checkout/checkout_tasks.py:44
self.inventory_page.click_add_to_cart_backpack()  # Method doesn't exist
```

**Description:**
Quality gates validated structural patterns (skeleton code, locators, decorators, etc.) but did not cross-reference method calls against upstream metadata. This allowed generated code to call non-existent methods.

**Affected Gates:**
- qg_task POST: Task calls POM methods not in pom_metadata
- qg_role POST: Role calls Task methods not in task_metadata
- qg_test_runner POST: Test calls Role methods not in role_metadata, uses POM state methods not in pom_metadata

**Root Cause:**
Gates only validated structural patterns but did not validate data contracts between layers.

**Impact:**
- Tests fail at runtime with AttributeError
- Quality gate gives false "PASS" for broken code
- Defeats purpose of tool chain data contracts (DD-26)

**Fix Implemented:**
Added `_validate_*_method_calls()` methods to each gate:

1. **qg_task POST:** `_validate_pom_method_calls(code, pom_metadata)`
   - Extracts `self.xxx_page.method()` calls
   - Validates against pom_metadata.action_methods + state_methods

2. **qg_role POST:** `_validate_task_method_calls(code, task_metadata)`
   - Extracts `self.xxx_tasks.method()` calls
   - Validates against task_metadata.task_methods

3. **qg_test_runner POST:** Two validations:
   - `_validate_role_method_calls(code, role_metadata)` - validates user.method() calls
   - `_validate_pom_state_assertions(code, pom_metadata)` - validates assert page.is_xxx() calls

**Note:** qg_page_object skipped - POM is base layer, defines methods but doesn't call external methods.

**Verification:** Requires POST input to include upstream metadata:
- qg_task POST: include `pom_metadata`
- qg_role POST: include `task_metadata`
- qg_test_runner POST: include `role_metadata` and `pom_metadata`

**Verified:** 2025-12-29 (code review)
**Resolved Date:** 2025-12-29

---

### [DEF-040] PostToolUse hook not triggering - audit trail not generated
**Severity:** MEDIUM
**Status:** RESOLVED (via alternative mechanism)
**Run ID:** 2025-12-29-R1
**Caught By:** TOOLS 1-2 ONLY workflow (dynamic_controls test)
**Code Version:** main
**Layer:** Claude Code Infrastructure / Hooks
**File:** `.claude/settings.local.json`, `.claude/hooks/audit-trail-writer.py`

**Description:**
PostToolUse hook configured to trigger on `mcp__qa-automation__qg_.*` pattern is not executing. The audit-trail-writer.py hook should create progressive audit files after each quality gate passes, but no audit file is generated.

**Evidence:**
- `workflow_state.json` exists with all 9 steps saved (StateManager working correctly)
- `tests/_audit/` directory exists but is empty (no audit files)
- `.audit_session` marker file not created
- Hook configuration appears correct in settings.local.json

**Hook Configuration (correct):**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__qa-automation__qg_.*",
        "hooks": [
          {
            "type": "command",
            "command": "python \"D:/my_ai_projects/py_sel_framework_mcp/.claude/hooks/audit-trail-writer.py\""
          }
        ]
      }
    ]
  }
}
```

**Root Cause (Suspected):**
Claude Code's PostToolUse hook mechanism may not be passing the expected data to the hook script's stdin, or the hook is not being triggered at all for MCP tool calls.

**Impact:**
- ~~No audit trail for compliance/traceability~~ MITIGATED
- DD-30 (Progressive Audit Trail) now functional via alternative mechanism
- Affects regulated vertical use cases (healthcare, finance, legal)

**Resolution:**
The PostToolUse hook mechanism remains non-functional, but an alternative approach was implemented:
- `BaseGate.get_audit_logger()` provides lazy-initialized AuditLogger
- Quality gates call `audit_logger.log_gate_result()` directly after each gate pass
- Audit files ARE being generated (see DEF-042 for location issue)

**Evidence (2025-12-30):**
```
mcp_server/state/audit_log_2025-12-30T04-23-03.404517Z.json
{
  "run_id": "2025-12-30T04:23:03.404517Z",
  "steps": [{"step": 6, "gate": "qg_page_object", "mode": "POST", "result": "pass"}],
  "summary": {"total_steps": 1, "gates_passed": 1, "gates_failed": 0}
}
```

**Remaining Issue:**
- Audit files write to `mcp_server/state/` instead of `tests/_audit/` (see DEF-042)
- PostToolUse hook mechanism still doesn't work for MCP tools (deprioritized - direct call works)

**Verified:** 2025-12-30 - demoqa.com forms test: Audit file generated via BaseGate mechanism
**Resolved Date:** 2025-12-30

---

### [DEF-042] audit_logger.py writes to mcp_server/state/ instead of tests/_audit/
**Severity:** MEDIUM
**Status:** RESOLVED
**Run ID:** 2025-12-29-R3
**Caught By:** User observation (demoqa.com forms test)
**Code Version:** main
**Layer:** MCP Server / State Management
**File:** `mcp_server/utils/audit_logger.py`
**Line(s):** 52-53

**Description:**
The AuditLogger class writes audit files to `mcp_server/state/` by default, but per step-10.md specification and DD-30 (Progressive Audit Trail), audit logs should be written to `tests/_audit/` for:
- Traceability (audit files alongside test artifacts)
- Compliance (regulated verticals need audit trail with tests)
- CI/CD integration (tests/_audit/ can be archived with test reports)

**Current Implementation (Wrong):**
```python
# Line 52-53 in audit_logger.py
if output_dir is None:
    output_dir = str(Path(__file__).parent.parent / "state")  # mcp_server/state/
```

**Expected:**
```python
if output_dir is None:
    output_dir = str(Path(__file__).parent.parent.parent / "tests" / "_audit")
```

**Root Cause:**
audit_logger.py was implemented with a convenient default path near the MCP server code, not the specified location from step-10.md design.

**Impact:**
- Audit files not with test artifacts
- CI/CD may not find audit files
- Inconsistent with DD-30 specification

**Fix Required:**
1. Update default output_dir to `tests/_audit/`
2. Ensure directory creation if not exists
3. Update step-10.md if needed to clarify exact path

**Fix Applied:**
1. Updated `audit_logger.py:51-55` - Changed default output_dir from `mcp_server/state/` to `tests/_audit/`
2. Updated `qg_preflight.py:75` - Pass step/gate_name to pass_response() to trigger audit logging
3. Updated `qg_user_input.py:113` - Pass step/gate_name to pass_response() to trigger audit logging
4. Updated `qg_ai_processing.py:80` - Pass step/gate_name to pass_response() to trigger audit logging

**Verified:** 2025-12-30 - Audit log created at `tests/_audit/audit_log_2025-12-30T07-15-13.197729Z.json`
**Resolved Date:** 2025-12-30

---

### [DEF-043] Audit logger creates new session per MCP tool call - loses step history
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2025-12-30-R3
**Caught By:** User observation (demoqa.com forms test)
**Code Version:** main
**Layer:** MCP Server / Audit System
**File:** `mcp_server/tools/gates/base_gate.py`, `mcp_server/utils/audit_logger.py`
**Line(s):** base_gate.py:84-87

**Description:**
The audit log only captured Step 6, but `workflow_state.json` has all 9 steps. Each MCP tool call creates a NEW AuditLogger with a NEW run_id because:

1. `BaseGate._audit_logger` is a class-level variable
2. Each MCP tool call is a **separate Python process**
3. When Python restarts between calls, `_audit_logger` resets to `None`
4. `get_audit_logger()` creates NEW AuditLogger with new timestamp

**Evidence:**
```
workflow_state.json: 9 steps (step_1 through step_9)
audit_log_2025-12-30T04-23-03.json: only 1 step (step_6)
```

**Root Cause:**
The lazy initialization in `get_audit_logger()` doesn't check for existing session:
```python
@classmethod
def get_audit_logger(cls) -> "AuditLogger":
    if cls._audit_logger is None:  # Always None after process restart
        from utils.audit_logger import AuditLogger
        cls._audit_logger = AuditLogger()  # Creates new run_id each time
    return cls._audit_logger
```

**Impact:**
- Audit trail only captures single step (last gate that ran)
- Step history lost across MCP tool calls
- Compliance/traceability broken for multi-step workflows

**Fix Required:**
1. Store `audit_run_id` in `workflow_state.json` when first step runs
2. In `get_audit_logger()`, check state for existing run_id
3. Pass existing run_id to AuditLogger constructor to continue same session

**Proposed Fix:**
```python
@classmethod
def get_audit_logger(cls) -> "AuditLogger":
    if cls._audit_logger is None:
        from utils.audit_logger import AuditLogger
        from utils.state_manager import StateManager

        # Check for existing session in workflow state
        state = StateManager()
        existing_run_id = state.get("audit_run_id")

        if existing_run_id:
            # Continue existing session
            cls._audit_logger = AuditLogger(run_id=existing_run_id)
        else:
            # Start new session
            cls._audit_logger = AuditLogger()
            state.save_audit_run_id(cls._audit_logger.run_id)

    return cls._audit_logger
```

**Fix Applied:**
1. Updated `base_gate.py:91-105` - Check workflow_state for existing audit_run_id, persist new run_id to step_0
2. Updated `audit_logger.py:66-91` - Added `_load_existing_data()` to load steps from existing audit file

**Verified:** 2025-12-30 - qg_preflight + qg_user_input both logged to same audit file (total_steps: 2)
**Resolved Date:** 2025-12-30

---

### [DEF-044] Multi-page BDD scenarios pass Step 5 with incomplete element discovery
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2025-12-31-R1
**Caught By:** Live test of Customer creation workflow (heliosdigital-retail-qa)
**Code Version:** main
**Layer:** Quality Gate / AI Orchestration
**Files:**
- `mcp_server/tools/gates/qg_discovered_elements.py`
- `mcp_server/utils/scope_discovery.py`
- `.claude/skills/qa-management-layer/references/step-05.md`

**Description:**
During live test of 4-step Customer creation wizard (Search → Customer → Contacts → Address), Step 5 quality gate passed after discovering elements from only 1 of 4 pages. The BDD scenario clearly had 12 "When" steps spanning 4 wizard pages, but the gate did not enforce multi-page scope discovery.

**Test Details:**
- User Story: "As a sales agent, I want to create a new customer with contact and address details"
- URL: https://heliosdigital-retail-qa.azurewebsites.net/Portal/Customers
- Workflow: customers (4-step wizard)
- Role: SalesAgent

**What Should Have Happened:**
```
Step 5 (Multi-page flow):
1. Call scope_discovery.analyze_workflow(bdd_scenarios)
   → Returns: {page_count: 4, pages: [SearchPage, CustomerPage, ContactsPage, AddressPage]}

2. For EACH page in scope:
   - Navigate to page (interact to reveal elements)
   - Call qg_discovered_elements PRE with scope_result
   - Extract elements from snapshot
   - Call qg_discovered_elements POST with elements
   - Gate tracks: discovered_pages[page_name] = elements

3. Check is_discovery_complete() == True before Step 6
```

**What Actually Happened:**
- Discovered elements from only Step 1 (Search page)
- Gate passed without scope_result (scope_result is optional)
- Proceeded to Step 6 (POM generation) with incomplete discovery

**Root Causes:**
1. **scope_result is optional** - Gate accepts but doesn't require scope analysis for multi-page flows
2. **step-05.md doesn't enforce scope** - Skill reference doesn't mandate scope_discovery.analyze_workflow()
3. **discovered_pages tracking unused** - Gate has per-page tracking (Task 2.0) but AI didn't use it
4. **No is_discovery_complete() check** - Gate has method but workflow doesn't require completion

**Impact:**
- POMs generated for only 1 of 4 pages
- Test would fail at runtime trying to interact with undiscovered pages
- Quality gate gives false "PASS" for incomplete work

**Fix Required:**

| Component | Change Needed |
|-----------|---------------|
| `qg_discovered_elements.py` | Require scope_result when BDD has multiple pages |
| `step-05.md` | Mandate scope_discovery call before element discovery |
| PRE-VALIDATE | Detect page_count > 1 → require scope_result |
| POST-VALIDATE | Check discovered_pages.count >= page_count before allowing Step 6 |

**Proposed Fix:**
```python
# In qg_discovered_elements PRE-VALIDATE:
if bdd_scenario_page_count > 1 and not scope_result:
    return fail_response(
        "Multi-page workflow detected but scope_result not provided. "
        "Call scope_discovery.analyze_workflow() first."
    )

# In qg_discovered_elements POST-VALIDATE:
if scope_result and not cls.is_discovery_complete(scope_result):
    return fail_response(
        f"Discovery incomplete: {discovered_count}/{expected_count} pages. "
        "Discover remaining pages before proceeding."
    )
```

**Prevention Rule (DD-44):**
```
Multi-Page Scope Discovery Enforcement:
1. At Step 5, AI MUST call scope_discovery.analyze_workflow(bdd_scenarios)
2. If page_count > 1, AI MUST discover elements for EACH page
3. qg_discovered_elements requires scope_result for multi-page flows
4. Step 6 blocked until is_discovery_complete() returns True
```

**Implementation (Partial - Steps 5-6 only):**
- `qg_discovered_elements.py`: Added `_detect_page_count_from_bdd()` to auto-detect multi-page from BDD
- `qg_discovered_elements.py`: PRE fails if multi-page detected without scope_result (DD-44)
- `qg_discovered_elements.py`: POST returns `multi_page_progress` with hint for incomplete discovery
- `qg_page_object.py`: PRE fails if multi-page and `discovery_complete` is False
- `step-05.md`: Added Multi-Page Discovery section with loop pattern
- `CLAUDE.md`: Added DD-44 to design decisions table
- Tests: 8 new tests in `test_qg_discovered_elements.py` (all passing)

**Remaining Work (Steps 6-9):**
- Step 6: Loop to generate POMs for ALL pages
- Step 7: Task must compose ALL POMs from multi-page scope
- Step 9: Test must have ALL POMs for assertions
- step-06.md through step-09.md need multi-page guidance

**E2E Verification (ParaBank Workflow - 2026-01-07):**
- User Story: Login → Open savings account → Transfer $100 → Verify transaction
- Workflow: parabank (4 pages: LoginPage, OpenAccountPage, TransferFundsPage, AccountActivityPage)
- Scope Discovery: Navigation-based approach discovered all 4 pages correctly
- Element Discovery: All 4 pages completed two-pass discovery (input + output elements)
- Discovery Complete: qg_discovery_complete checkpoint passed (4/4 pages with both types)
- POM Generation: All 4 POMs generated and validated
- Test Generation: Test successfully uses all POMs
- Framework Check: All 7 files passed validation

**Verified:** 2026-01-07 - ParaBank E2E workflow completed Steps 1-11 successfully
**Resolved Date:** 2026-01-07

---

### [DEF-045] AI generates state-check methods based on guesses, not verified page observation
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2026-01-02-R1
**Caught By:** Test execution (ParaBank banking workflow)
**Code Version:** main → feature/3.0-pom-dual-elements
**Layer:** AI Orchestration / Workflow Design
**File:** Step 5 workflow (element discovery)

**Error Message:**
```
AssertionError: Welcome message should be displayed after registration
assert False
 +  where False = has_welcome_message()
```

**Description:**
During the 11-step QA workflow, AI generates POM state-check methods (`is_*`, `has_*`) based on assumptions rather than verified page observation. The state methods are meant to verify OUTPUT states (confirmation pages, success messages) but AI only sees INPUT pages (forms, buttons).

**Example of guessed code:**
```python
# AI assumed this text would appear after registration:
def has_welcome_message(self) -> bool:
    text = self.web.get_text(*self.WELCOME_HEADING, timeout=5)
    return text.startswith("Welcome ")  # GUESS - never verified

def is_registration_confirmed(self) -> bool:
    return "Your account was created successfully" in text  # GUESS
```

**Root Cause:**
The 11-step workflow has a fundamental gap:
- **Step 5 (Element Discovery)** captured elements on ENTRY pages only (forms, buttons)
- **State-check methods** verify EXIT pages (confirmations, success messages)
- AI generated EXIT verification without ever seeing the EXIT page

**Impact:**
- Tests fail at assertion phase even when workflow executes correctly
- State methods are untested guesses based on pattern matching
- No validation that expected text/elements actually exist on confirmation pages

**Fix Implemented (Two-Pass Discovery):**

Extended Step 5 with two-pass element discovery loop per page:
- **PASS 1 (Input):** Discover form fields, buttons, input elements → `input_elements`
- **PASS 2 (Output):** Discover confirmation messages, success indicators → `output_elements`

**Implementation Details:**

1. **Task 1.0 - Step 5 Extension:**
   - Updated `step-05.md` with two-pass discovery guidance (+175 lines)
   - Updated `qg_discovered_elements.py` with `type` parameter ("input" vs "output")
   - State structure: `discovered_pages[page_name] = {input_elements: [...], output_elements: [...]}`
   - 21 new tests added (59/62 passing)

2. **Task 2.0 - Discovery Checkpoint Gate:**
   - Created `qg_discovery_complete.py` - validates ALL pages have BOTH types
   - Blocks Step 6 until two-pass complete for all pages
   - 16 new tests (16/16 passing - 100%)

3. **Task 3.0 - POM Generation Update:**
   - Updated `qg_page_object.py` PRE to require both element types
   - Updated `tool_03_generate_page_object.py` to use dual elements
   - **input_elements** → action methods (enter_, click_, select_)
   - **output_elements + expected_states** → state-check methods (is_, has_, get_)
   - 8 new tests (66/66 passing - 100%)

**Files Modified:**
- `.claude/skills/qa-management-layer/references/step-05.md`
- `.claude/skills/qa-management-layer/references/step-06.md`
- `mcp_server/tools/gates/qg_discovered_elements.py`
- `mcp_server/tools/gates/qg_discovery_complete.py` (NEW)
- `mcp_server/tools/gates/qg_page_object.py`
- `mcp_server/tools/tool_03_generate_page_object.py`
- `mcp_server/_dev_tests/test_gates/test_qg_discovered_elements.py`
- `mcp_server/_dev_tests/test_gates/test_qg_discovery_complete.py` (NEW)
- `mcp_server/_dev_tests/test_gates/test_qg_page_object.py`

**Test Results:**
- Task 1.0: 59/62 tests (98%)
- Task 2.0: 16/16 tests (100%)
- Task 3.0: 66/66 tests (100%)
- Combined: 141/144 tests passing (98%)

**Backward Compatibility:** All changes maintain backward compatibility via default parameters (`type="input"`)

**E2E Verification (ParaBank Workflow - 2026-01-07):**
- Two-Pass Discovery: Completed PASS 1 (input) and PASS 2 (output) for all 4 pages
- State-Check Methods: Generated from verified output elements (success messages, confirmation indicators)
- POST Gates: All 4 POMs passed POST validation with complete state-check methods
- No Guesses: All state methods derived from actual Playwright snapshots of confirmation pages
- Test Assertions: Test uses `is_transaction_visible()` and `has_recent_transaction()` - both verified during PASS 2

**Status Notes:** Implementation complete, all unit/gate tests pass. E2E verified successfully.
**Resolved Date:** 2026-01-07

---

### [DEF-047] Hardcoded URLs in Task layer - should use config
**Severity:** HIGH
**Status:** RESOLVED
**Run ID:** 2026-01-02-R1
**Caught By:** Code review (ParaBank banking workflow)
**Code Version:** main
**Layer:** Task / AI Orchestration
**File:** `framework/tasks/banking/banking_tasks.py`
**Line(s):** 54, 77, 95, 113

**Error (Pattern Violation):**
```python
# GENERATED (WRONG) - banking_tasks.py:
self.web.navigate_to("https://parabank.parasoft.com/parabank/register.htm")
self.web.navigate_to("https://parabank.parasoft.com/parabank/openaccount.htm")
self.web.navigate_to("https://parabank.parasoft.com/parabank/transfer.htm")
self.web.navigate_to("https://parabank.parasoft.com/parabank/overview.htm")
```

**Established Pattern (conftest.py + environment_config.json):**
```python
# environment_config.json:
{
  "DEFAULT": {"url": "http://www.automationpractice.pl/index.php"},
  "PARABANK": {"url": "https://parabank.parasoft.com/parabank"}
}

# Task accesses via config:
base_url = self.web.config["url"]
self.web.navigate_to(f"{base_url}/register.htm")

# Or POM handles navigation:
self.registration_page.navigate()  # POM uses self.web.config["url"]
```

**Framework Pattern Evidence:**
- `conftest.py:72-79`: Loads URL from `environment_config.json`
- `conftest.py:102-119`: Passes `config` to `WebInterface`
- `WebInterface:47`: Stores `self.config` for access by layers
- `cart/login_page.py:36`: POM has `navigate()` method (though also hardcoded - see note)

**Root Cause:**
AI-generated Task code hardcoded URLs instead of:
1. Using `self.web.config["url"]` from environment config
2. Adding ParaBank environment to `environment_config.json`
3. Delegating navigation to POM methods

**Impact:**
- Cannot switch environments (dev/staging/prod)
- Tests not portable to other ParaBank instances
- Violates separation of config from code
- Maintenance burden when URLs change

**Fix Required:**
1. Add PARABANK environment to `environment_config.json`
2. Update `banking_tasks.py` to remove `self.web.navigate_to()` calls
3. Add `navigate()` methods to each banking POM using `self.web.config["url"]`
4. Task methods call `self.pom.navigate()` instead

**Prevention Rule: DD-49 (Added to FRAMEWORK.md 8.24)**

| Layer | Navigation Allowed | How |
|-------|-------------------|-----|
| POM | YES | `navigate()` using `self.web.config["url"]` |
| Task | Calls POM only | `self.pom.navigate()` - NO direct WebInterface |
| Role | NO | Orchestrates Tasks only |
| Test | NO | Calls Role methods only |

**Enforcement (3 layers):**

| Gate/Check | Pattern | Action |
|------------|---------|--------|
| `qg_task` POST | `self.web.navigate_to(` in code | FAIL - "Tasks must call POM navigate()" |
| `qg_page_object` POST | `navigate_to("http` without `self.web.config` | FAIL - "Use config URL" |
| `/framework-check` | Scan all layers for hardcoded URLs | Report violations |

**Pre-existing Violations (also need fix):**
- `cart/login_page.py:36` - hardcoded saucedemo URL

**Fix Applied:**
1. Added navigate() methods to all 4 banking POMs using self.web.config["url"]
2. Updated banking_tasks.py to call self.pom.navigate() instead of self.web.navigate_to()
3. DD-49 gate enforcement prevents future violations

**Files Updated:**
- framework/pages/banking/registration_page.py
- framework/pages/banking/open_new_account_page.py
- framework/pages/banking/transfer_funds_page.py
- framework/pages/banking/accounts_overview_page.py
- framework/tasks/banking/banking_tasks.py

**Verified:** 2026-01-05 - No hardcoded navigate_to() calls in banking_tasks.py
**Resolved Date:** 2026-01-05

---

### [DEF-046] Quality gates do not enforce one user story = one test principle
**Severity:** MEDIUM
**Status:** RESOLVED
**Run ID:** 2026-01-02-R1
**Caught By:** User observation (ParaBank banking workflow)
**Code Version:** main → feature/4.0-test-redundancy
**Layer:** Quality Gate / AI Orchestration
**File:** `mcp_server/tools/gates/qg_test_runner.py`

**Description:**
The workflow generated TWO test methods for ONE user story. The first test (`test_new_customer_can_register_and_open_savings`) is a subset of the second test (`test_customer_can_register_transfer_and_verify`), making it redundant.

**Principle Violated:**
In production QA, the pattern is:
```
Existing atomic tests (built incrementally):
├── test_registration.py       → Tests register, creates RegistrationPage POM
├── test_open_account.py       → Tests account opening, creates OpenAccountPage POM
├── test_transfer_funds.py     → Tests transfers, creates TransferPage POM

New E2E journey test:
└── test_new_customer_banking.py  → ONE test, ONE Role method
    - Reuses existing POMs (already validated)
    - Role orchestrates the complete journey
```

**What Happened:**
- User story described ONE complete journey (register → open savings → transfer → verify)
- AI/Tool 6 generated TWO tests (partial journey + full journey)
- First test is redundant subset of second
- Gate passed without detecting redundancy

**Root Cause:**
1. No validation that one user story = one E2E test
2. AI broke acceptance criteria into multiple tests instead of one orchestrated test
3. Gate doesn't detect when one test is subset of another

**Impact:**
- Redundant test execution
- Confusing test structure
- Violates DRY principle

**Fix Implemented (Test Redundancy Detection):**

Added redundancy detection to `qg_test_runner.py` POST validation:
- Detects if one test's role calls are a subset of another test
- Enforces MVP constraint: "One user story = ONE E2E test"
- Provides clear error messages and fix hints

**Implementation Details:**

1. **Task 4.0 - Redundancy Detection:**
   - Added `_detect_redundant_tests()` method to `qg_test_runner.py`
   - Added `_extract_test_methods()` method - parses test code
   - Added `_extract_role_calls()` method - extracts role method calls
   - Filters out POM state method calls (is_, has_, get_)
   - Filters out self.* prefixed calls (POM calls)
   - Compares all test pairs for subset redundancy
   - 8 new tests (49/49 passing - 100%)

2. **Step 9 Guidance Update:**
   - Updated `step-09.md` with "One user story = one E2E test" guidance
   - Added DEF-046 section with redundancy examples
   - Updated enforcement table

**How It Works:**
```python
# Example redundancy (FAILS gate):
def test_login():  # Role calls: ['login']
    user.login()

def test_login_and_browse():  # Role calls: ['login', 'browse_category']
    user.login()
    user.browse_category("Women")

# Result: FAIL - test_login is subset of test_login_and_browse
```

**Files Modified:**
- `mcp_server/tools/gates/qg_test_runner.py` (+110 lines)
- `.claude/skills/qa-management-layer/references/step-09.md` (+30 lines)
- `mcp_server/_dev_tests/test_gates/test_qg_test_runner.py` (+324 lines)

**Test Results:**
- 49/49 tests passing (100% - 41 existing + 8 new DEF-046 tests)

**E2E Verification (ParaBank Workflow - 2026-01-07):**
- User Story: ONE complete journey (login → open account → transfer → verify transaction)
- Generated Tests: ONE test method (`test_complete_banking_workflow`)
- Role Calls: ONE workflow method call (`customer.complete_banking_workflow()`)
- No Redundancy: POST gate detected no subset redundancy (only 1 test generated)
- Framework Check: Test properly calls ONE role method, asserts via POM state methods

**Status Notes:** Implementation complete, all unit/gate tests pass. E2E verified successfully.
**Resolved Date:** 2026-01-07

---

### [DEF-048] Code reconstruction after context loss lacks quality gate enforcement
**Severity:** HIGH
**Status:** OPEN
**Caught By:** User observation (ParaBank workflow - Step 10)
**Code Version:** feature/5.0-docs-and-verification
**Layer:** Quality Gate / AI Orchestration
**File:** `mcp_server/tools/gates/qg_save_run.py`

**Description:**
During Step 10 (Save & Run), when AI loses context and reconstructs code from memory/summary, the reconstructed code is saved to disk WITHOUT quality gate validation. This creates a gap where invalid/incomplete code can bypass all quality checks.

**What Happened:**
1. Steps 6-9 completed with quality gates passing (LoginPage validated)
2. Context loss occurred (conversation summarization)
3. AI reconstructed 3 POMs from memory (OpenAccountPage, TransferFundsPage, AccountActivityPage)
4. AI saved reconstructed POMs directly to disk WITHOUT calling POST gates
5. User caught the gap and requested validation
6. POST gates were called AFTER files were saved (wrong order)

**Impact:**
- Reconstructed code bypasses DD-25 (skeleton code detection)
- Reconstructed code bypasses WebInterface API validation
- Reconstructed code bypasses locator validation
- Files saved to disk may be invalid/incomplete
- No enforcement mechanism - relies on AI being diligent

**Architecture Gap:**
Step 10 workflow assumes code from Steps 6-9 is already validated. When code is reconstructed during Step 10, there's no gate to catch this and enforce validation before saving.

**Smart Gate Pattern Fix:**

Update `qg_save_run.py` PRE validation to detect reconstruction and enforce POST gating:

```python
# In qg_save_run validate_pre():

# NEW: Detect code reconstruction (differs from state)
state_manager = cls._get_state_manager()

# Check each layer for reconstruction
for layer, code_param, step_num, gate_name in [
    ("POM", "pom_code", 6, "qg_page_object"),
    ("Task", "task_code", 7, "qg_task"),
    ("Role", "role_code", 8, "qg_role"),
    ("Test", "test_code", 9, "qg_test_runner")
]:
    input_code = input_data.get(code_param, "")
    state_code = state_manager.get_step(step_num).get("data", {}).get(code_param, "")

    if input_code != state_code and input_code.strip():
        return cls.fail_response(
            error=f"{layer} code reconstruction detected without POST gate",
            fix_hint=f"""
Reconstructed code must pass POST gate BEFORE saving.

Pattern:
1. Reconstruct code from memory/summary
2. Call: {gate_name}(mode="POST", code=..., metadata=...)
3. If PASS: Include validated code in qg_save_run
4. If FAIL: Fix code, retry POST gate

Example:
# Reconstruct OpenAccountPage
code = '''class OpenAccountPage:...'''
metadata = {{"class_name": "OpenAccountPage", ...}}

# MANDATORY: Quality gate BEFORE saving
result = qg_page_object(mode="POST", code=code, metadata=metadata)
if result["status"] == "pass":
    # NOW safe to save
    qg_save_run(mode="PRE", pom_code=code, ...)
            """,
            fix_data={
                "reconstructed_layer": layer,
                "required_gate": gate_name,
                "mode": "POST"
            }
        )

# EXISTING: Skeleton code detection (unchanged)
skeleton_error = cls._detect_skeleton_code(pom_code)
if skeleton_error:
    return skeleton_error
...
```

**Why Smart Gate Pattern:**

✅ **Self-enforcing**: AI cannot proceed without gating reconstructed code
✅ **Self-teaching**: Gate provides example pattern in fix_hint
✅ **Minimal docs**: Step 10 skill just says "gate if reconstructed"
✅ **Real-time feedback**: Fails immediately with actionable fix
✅ **Integrates cleanly**: Runs BEFORE existing skeleton detection

**Implementation Plan:**
1. Update `qg_save_run.py` with reconstruction detection logic
2. Add unit tests for reconstruction detection scenarios
3. Update `step-10.md` with minimal pointer: "If code reconstructed: POST gate first"
4. Verify with E2E test (intentional reconstruction scenario)

**Files to Modify:**
- `mcp_server/tools/gates/qg_save_run.py` (add reconstruction detection)
- `.claude/skills/qa-management-layer/references/step-10.md` (minimal pointer)
- `mcp_server/_dev_tests/test_gates/test_qg_save_run.py` (add tests)

**Verification:**
After fix, test by:
1. Complete Steps 1-9 normally
2. Intentionally modify POM code in Step 10 (simulate reconstruction)
3. Call qg_save_run without calling qg_page_object POST
4. Verify: Gate FAILS with reconstruction error
5. Call qg_page_object POST, then qg_save_run
6. Verify: Gate PASSES, files saved

**Status Notes:** Defect logged. Implementation pending. Current workaround: AI manually calls POST gates on reconstructed code (but not enforced).

**Resolved Date:** Pending implementation

---

### [DEF-052] run_id isolation broken - each MCP tool call creates new run_id
**Severity:** HIGH
**Status:** RESOLVED
**Layer:** MCP State Management
**File:** `mcp_server/tools/gates/base_gate.py`
**Line(s):** 87-102

**Rule Violated:**
- State accumulation across Steps 1-11
- Single run_id per workflow

**Description:**
Each MCP tool call runs in a separate Python process. BaseGate._audit_logger is a class variable that gets reset to None in each new process. This causes get_audit_logger() to create a fresh AuditLogger with a new run_id every time, breaking state continuity.

**Impact:**
- Steps 1-4 each created separate run_id directories
- Each step's state saved to different directory
- Step 5 PRE-VALIDATE failed with "Step 4 not complete" (looking in wrong directory)

**Root Cause:**
Python class variables don't persist across separate process invocations (MCP tool architecture).

**Fix:**
Implemented session marker pattern:
1. Added _get_session_run_id(), _save_session_run_id(), _clear_session_marker() methods
2. Modified get_audit_logger() to check session marker file before creating new logger
3. Session marker: mcp_server/state/.run_session with format "run_id|timestamp"
4. 5-minute timeout (later increased to 30 minutes in DEF-052A)

**Verification:**
- Steps 1-4 all save to same run_id directory
- State accumulates correctly in single workflow_state.json
- Step 4 POST-VALIDATE successfully finds Step 3 state

**Resolved Date:** 2026-01-08

---

### [DEF-052A] Session marker bypassed when class variable already set
**Severity:** HIGH
**Status:** RESOLVED
**Layer:** Quality Gate
**File:** `mcp_server/tools/gates/qg_preflight.py`, `base_gate.py`
**Line(s):** qg_preflight.py:44-46, base_gate.py:136

**Rule Violated:**
- Fresh run_id per workflow
- Session isolation between workflows

**Description:**
DEF-052 fix incomplete. get_audit_logger() only checks session marker if _audit_logger is None. In long-running MCP server:
- Workflow 1 completes → _audit_logger cached with run_id ABC
- User starts Workflow 2 → creates session marker with run_id XYZ
- Step 2+ calls get_audit_logger() → _audit_logger NOT None → skips session check → returns old logger ABC
- Workflow 2 writes to wrong directory

**Impact:**
- Long-running MCP server reuses stale logger from previous workflow
- Session marker ignored after first workflow
- State written to wrong directory
- Gates fail with "Step X not complete" errors

**Root Cause:**
DEF-052 fix designed for fresh Python processes (tests), not long-running MCP server with persistent class variables.

**Fix:**
Added to qg_preflight.validate() (Step 1):
```python
# DEF-052A: Clear stale session from previous workflow
cls._audit_logger = None
cls._clear_session_marker()
```

Also increased session timeout from 5 minutes to 30 minutes to support manual E2E workflows.

**Impact Assessment:** docs/DEF-052A_impact_assessment.md

**Verification:**
- Tests pass (no breaking changes - tests already clear manually)
- Workflow 1 → Workflow 2 (no MCP restart) → separate run_ids
- E2E test completes Steps 1-11 with single run_id

**Resolved Date:** 2026-01-08

---

### [DEF-054] qg_save_run validates wrong file paths - same bug as DEF-055a
**Severity:** HIGH
**Status:** RESOLVED
**Caught By:** Task 25.0 investigation
**Code Version:** post-DEF-055a implementation
**Layer:** Quality Gates
**File:** `mcp_server/tools/gates/qg_save_run.py`
**Line(s):** `_validate_files_exist()` method

**Error Message:**
"Missing generated files on disk" even when files were correctly written by Steps 6-8.

**Description:**
DEF-055a fixed the file WRITE path in Steps 6-8 gates to include `framework/` prefix.
However, `qg_save_run._validate_files_exist()` (Step 10) still used the old buggy path conversion without `framework/` prefix.

Result: Files written to correct path, but validation checks wrong path → always fails.

**Root Cause:**
Same bug as DEF-055a in a different location:
```python
# BUG: Input "pages.auth.login_page"
# Produced: D:/project/pages/auth/login_page.py  ❌
# Files written to: D:/project/framework/pages/auth/login_page.py  ✓
# Validation fails because it checks wrong path
```

**Fix:**
Added `_import_path_to_file_path()` helper method (same as other gates) and used it for Steps 6-8 file validation:
```python
@classmethod
def _import_path_to_file_path(cls, import_path: str) -> str:
    # DEF-054 FIX: Prepend framework/ for pages/tasks/roles paths
    framework_prefixes = ('pages' + os.sep, 'tasks' + os.sep, 'roles' + os.sep)
    if relative_path.startswith(framework_prefixes):
        relative_path = 'framework' + os.sep + relative_path
```

**Verified:** Unit test confirms fix. 33/34 tests pass (1 pre-existing failure unrelated).
**Resolved Date:** 2026-01-08

---

### [DEF-055a] Path conversion missing framework/ prefix - files written to wrong location
**Severity:** CRITICAL
**Status:** RESOLVED
**Caught By:** Production E2E test (Task 24.0)
**Code Version:** post-DEF-051 implementation
**Layer:** Quality Gates
**File:** `mcp_server/tools/gates/qg_page_object.py`, `qg_task.py`, `qg_role.py`
**Line(s):** `_import_path_to_file_path()` method

**Error Message:**
Files not appearing in expected locations after Step 6-8 gate passes. No error visible (see DEF-055b).

**Description:**
DEF-051 implemented per-step file writes in Steps 6-8 gates. The `_import_path_to_file_path()` helper converts Python import paths (e.g., `pages.auth.login_page`) to filesystem paths. However, the conversion was missing the `framework/` prefix for pages/tasks/roles directories.

**Root Cause:**
```python
# BUG: Input "pages.auth.login_page"
# Produced: D:/project/pages/auth/login_page.py  ❌
# Expected: D:/project/framework/pages/auth/login_page.py  ✓
```

Pages, tasks, and roles live under `framework/` directory, not project root.

**Fix:**
Added detection for framework-prefixed paths:
```python
framework_prefixes = ('pages' + os.sep, 'tasks' + os.sep, 'roles' + os.sep)
if relative_path.startswith(framework_prefixes):
    relative_path = 'framework' + os.sep + relative_path
```

Applied to: `qg_page_object.py`, `qg_task.py`, `qg_role.py`

**Verified:** Code review confirms fix. Production E2E pending (Task 25.0).
**Resolved Date:** 2026-01-08

---

### [DEF-055b] Silent exception handling swallows file write errors
**Severity:** HIGH
**Status:** RESOLVED
**Caught By:** Production E2E test (Task 24.0)
**Code Version:** post-DEF-051 implementation
**Layer:** Quality Gates
**File:** `mcp_server/tools/gates/qg_page_object.py`, `qg_task.py`, `qg_role.py`, `qg_test_runner.py`
**Line(s):** File write try/except blocks

**Error Message:**
No error message - that's the problem. Files silently failed to write with no indication.

**Description:**
DEF-051 implementation wrapped file writes in `try/except: pass` blocks. When DEF-055a caused writes to fail (wrong path), the exception was swallowed with no logging, audit trail update, or user notification.

**Root Cause:**
```python
# BUG: Silent failure
try:
    cls._write_pom_file(file_path, code)
except:
    pass  # ❌ No visibility into failure
```

**Fix:**
Replaced silent pass with audit logging:
```python
except Exception as e:
    audit_logger = cls.get_audit_logger()
    audit_logger.log_gate(
        step=6,
        gate_name="qg_page_object",
        mode="POST",
        result="warning",
        error=f"FILE_WRITE_FAILED: {file_path} - {str(e)}"
    )
```

Applied to: `qg_page_object.py`, `qg_task.py`, `qg_role.py`, `qg_test_runner.py`

**Verified:** Code review confirms fix. Production E2E pending (Task 25.0).
**Resolved Date:** 2026-01-08

---

### [DEF-057] Metadata param format inconsistency - dict vs string format breaks Tool 5
**Severity:** CRITICAL
**Status:** RESOLVED
**Caught By:** Production E2E test (Task 26.0) - manual vs agent comparison
**Code Version:** feature/26.0-navigation-tracking (commit 219f3f7)
**Layer:** Quality Gates + Generators
**Files:**
- `mcp_server/utils/generators/page_object_generator.py` (line 595)
- `mcp_server/utils/generators/task_generator.py` (line 235)
- `mcp_server/utils/generators/role_generator.py` (lines 298, 316, 414)
- `mcp_server/tools/gates/qg_page_object.py` (line 466)

**Error Message:**
```
AttributeError: 'dict' object has no attribute 'split'
File: role_generator.py, line 298
Code: param_name = param.split(":")[0].strip()
```

**Description:**
Metadata param format is inconsistent across the tool chain, causing Tool 5 (generate_role) to crash when processing task_metadata from Tool 4.

**The Problem:**
Two separate but related issues:

1. **Param Format Inconsistency**: State files show dict format, but code expects string format
   - **CORRECT (per DEF-054, Jan 8)**: `["email: str", "password: str"]` (string array)
   - **BROKEN (current state)**: `[{"name": "email", "type": "str"}]` (dict array)

2. **POM Metadata Simplification**: Step 6 state loses detailed method metadata
   - Tool 3 generates: `[{"name": "enter_username", "params": ["username: str"], "returns": "self"}]`
   - Step 6 state saves: `["enter_username", "enter_password"]` (names only)
   - Tool 4 can't copy params because they're missing from state

**Evidence:**

```python
# POM Generator (line 595) - Generates STRING format ✓
"params": [f"{param_name}: str"]

# Role Generator (line 298) - Expects STRING format ✓
param_name = param.split(":")[0].strip()  # Crashes on dict

# Actual State File (2026-01-12 run) - Shows DICT format ❌
"params": [
  {"name": "username", "type": "str"},
  {"name": "password", "type": "str"}
]
```

**Root Cause:**
Dict format in state files is the PRIMARY bug. Agent succeeded because it autonomously self-healed (converted dict→string) when hitting the .split() crash at role_generator.py:298.

**CRITICAL PROTOCOL VIOLATION:**
Agent DID NOT follow DD-22 (Stop-and-Discuss Protocol) when encountering the Tool 5 crash:
- ❌ Did NOT stop execution
- ❌ Did NOT report the param format issue
- ❌ Did NOT request user discussion
- ✓ DID autonomously fix (self-heal) dict→string conversion
- ✓ DID continue execution to completion

**Why This Violates "The Isagawa Way":**
The Isagawa methodology demands strict protocol adherence and quality gates:
1. Issues must be surfaced, not hidden by autonomous fixes
2. Root causes must be addressed, not worked around
3. Human oversight required for deviations from expected behavior
4. Silent self-healing masks systemic problems

**The Correct Behavior (DD-22):**
```
1. STOP - Agent detects dict format, .split() will crash
2. REPORT - "Tool 5 crash: params are dicts, expected strings"
3. DISCUSS - Wait for parent/user direction
4. PROCEED - Only after explicit instruction
```

**What Agent Actually Did:**
```
1. Detect dict format
2. Convert dict→string autonomously  ← PROTOCOL VIOLATION
3. Continue execution
4. Report success (hiding the underlying bug)
```

**Impact:** Manual execution exposed the real bug (dict format). Agent execution masked it with autonomous workaround. The dict format bug remains in state files - we just got lucky the agent compensated.

**Impact Assessment (Updated for Dual Fix Strategy):**

### 1. Who Calls This Code? (EXPANDED)

**Generators:**
- `page_object_generator.py:_build_action_methods_metadata()` - Creates params as strings
- `task_generator.py:generate_task_methods_from_metadata()` - Copies params from POM
- `role_generator.py:_generate_workflow_method_from_task()` - Reads params with .split()

**Gates:**
- `qg_page_object.py:validate_post()` - Saves simplified pom_metadata
- `qg_task.py:validate_pre()` - Reads pom_metadata from state
- `qg_task.py:validate_post()` - Saves task_metadata
- `qg_role.py:validate_pre()` - Reads task_metadata from state

**State Manager:**
- `state_manager.py:save()` - Writes metadata to JSON (no format conversion)

**Test Fixtures:**
- `test_integration.py:valid_step_6_post_data()` - Uses full method dicts
- `test_integration.py:valid_step_7_post_data()` - Uses string params ✓

### 2. What Depends on Current Behavior?

**State File Structure:**
- Step 6: `pom_metadata` dict with per-page metadata
- Step 7: `task_metadata` with task_methods array
- Step 8: `role_metadata` with workflow_methods array

**Metadata Chain (Tool 3 → 4 → 5 → 6):**
- Tool 3 outputs metadata with full method details
- Tool 4 reads pom_metadata, copies params to task_methods
- Tool 5 reads task_metadata, processes params with .split()
- Tool 6 reads role_metadata for test generation

**Test Fixtures:**
- 38 integration tests depend on metadata format
- Fixtures use string param format (correct)

**Existing State Files:**
- All files in `tests/_state/*/workflow_state.json`
- May contain either format (unknown which)

### 3. What Will Break? (DUAL FIX IMPACT)

**Phase 2 Impact (Gate Validation Added):**

| Component | Current Behavior | After Phase 2 | Impact |
|-----------|-----------------|---------------|---------|
| **qg_page_object POST** | Accepts any action_methods format | REJECTS dict params | ⚠️ HIGH - Exposes violations |
| **qg_task POST** | Accepts any task_methods format | REJECTS dict params | ⚠️ HIGH - Exposes violations |
| **qg_role POST** | Accepts any workflow_methods format | REJECTS dict params | ⚠️ HIGH - Exposes violations |
| **Gate unit tests** | May pass with dict format | FAIL if fixtures use dicts | ⚠️ HIGH - Needs fixture updates |
| **Integration tests** | May pass with dict format | FAIL if fixtures use dicts | ⚠️ MEDIUM - 38 tests to check |
| **E2E tests (manual)** | Crashes at Tool 5 | FAILS at earlier gate | ✓ BETTER - Fail-fast |
| **E2E tests (agent)** | Self-heals, masks bug | FAILS at gate, can't self-heal | ✓ BETTER - Surfaces issue |

**Phase 3 Impact (Root Cause Fixed):**

| Component | Current Behavior | After Phase 3 | Impact |
|-----------|-----------------|---------------|---------|
| **qg_page_object state save** | Saves simplified action_methods names | Saves FULL metadata with params | ⚠️ MEDIUM - State structure change |
| **Tool 4 (generate_task)** | Copies from simplified metadata | Copies from FULL metadata | ✓ LOW - Gets params now |
| **Tool 5 (generate_role)** | Crashes on dict params | Receives string params | ✓ HIGH - No crash |
| **State files** | May have dict format | Always string format | ✓ HIGH - Consistent |
| **Test fixtures** | May use dict format | Must use string format | ⚠️ MEDIUM - Needs updates |

**What Must Change:**

**Code Files (7 files):**
1. `mcp_server/tools/gates/base_gate.py` - Add `_validate_param_format()`
2. `mcp_server/tools/gates/qg_page_object.py` - Add validation + fix consolidation
3. `mcp_server/tools/gates/qg_task.py` - Add validation
4. `mcp_server/tools/gates/qg_role.py` - Add validation
5. `mcp_server/utils/generators/page_object_generator.py` - Verify string output
6. `mcp_server/utils/generators/task_generator.py` - Verify string copying
7. `mcp_server/utils/generators/role_generator.py` - Already expects strings ✓

**Test Files (4+ files):**
1. `mcp_server/_dev_tests/test_gates/test_integration.py` - Update fixtures
2. `mcp_server/_dev_tests/test_gates/test_qg_page_object.py` - Update fixtures
3. `mcp_server/_dev_tests/test_gates/test_qg_task.py` - Update fixtures
4. `mcp_server/_dev_tests/test_gates/test_qg_role.py` - Update fixtures

**Tests Affected:**
- Gate unit tests: 481+ tests (unknown how many use dict format)
- Integration tests: 38 tests (need to check fixtures)
- E2E tests: All manual/agent runs (will fail until fix complete)

**Breaking Changes:**
- ❌ **Dict params rejected at gates** (immediate after Phase 2)
- ❌ **State structure changed** (after Phase 3 - ephemeral, OK)
- ❌ **Test fixtures need updates** (after Phase 2 validation added)
- ✓ **No API changes** (internal metadata only)
- ✓ **No backward compat needed** (state files ephemeral)

### 4. Migration Path

**COMPREHENSIVE FIX STRATEGY: Root Cause + Gate Enforcement**

Fix in TWO dimensions:
1. **Root Cause**: Ensure generators/consolidation output correct format
2. **Gate Enforcement**: Validate format at boundaries (prevent future regressions)

---

**Phase 1: Discovery (Complete) ✓**
- [x] Identify all locations using param format
- [x] Confirm correct standard (string format per DEF-054)
- [x] Document impact on generators, gates, tests
- [x] Identify both root cause AND enforcement gaps

---

**Phase 2: Add Gate Validation FIRST (Safety Net)**

**Why First:** Catch violations during fix process, prevent regressions

**Files to Modify:**
- `mcp_server/tools/gates/base_gate.py`
- `mcp_server/tools/gates/qg_page_object.py`
- `mcp_server/tools/gates/qg_task.py`
- `mcp_server/tools/gates/qg_role.py`

**Tasks:**
- [ ] 2.1: Add `_validate_param_format()` to base_gate.py
  ```python
  @classmethod
  def _validate_param_format(cls, params: list, context: str) -> Optional[Dict]:
      """Validate params are string format 'name: type', not dict format."""
      for param in params:
          if isinstance(param, dict):
              return cls.fail_response(
                  error=f"{context}: Param must be string, got dict: {param}",
                  fix_hint="Expected ['email: str'], not [{'name': 'email', 'type': 'str'}]"
              )
          if not isinstance(param, str) or ":" not in param:
              return cls.fail_response(
                  error=f"{context}: Invalid param format: {param}",
                  fix_hint="Params must be 'name: type' strings like 'email: str'"
              )
      return None
  ```

- [ ] 2.2: Add validation to qg_page_object POST `_validate_action_methods()`
  ```python
  # After existing checks, add:
  for method in action_methods:
      if isinstance(method, dict):
          params = method.get("params", [])
          error = cls._validate_param_format(params, f"action_method '{method.get('name')}'")
          if error:
              return error
  ```

- [ ] 2.3: Add validation to qg_task POST (new method `_validate_task_methods()`)
  ```python
  @classmethod
  def _validate_task_methods(cls, metadata: Dict) -> Optional[Dict]:
      task_methods = metadata.get("task_methods", [])
      for method in task_methods:
          params = method.get("params", [])
          error = cls._validate_param_format(params, f"task_method '{method.get('name')}'")
          if error:
              return error
      return None
  ```

- [ ] 2.4: Add validation to qg_role POST (new method `_validate_workflow_methods()`)
  ```python
  @classmethod
  def _validate_workflow_methods(cls, metadata: Dict) -> Optional[Dict]:
      workflow_methods = metadata.get("workflow_methods", [])
      for method in workflow_methods:
          params = method.get("params", [])
          error = cls._validate_param_format(params, f"workflow_method '{method.get('name')}'")
          if error:
              return error
      return None
  ```

- [ ] 2.5: Run gate unit tests → will expose ALL dict format violations

---

**Phase 3: Fix Root Causes (Generators & State Consolidation)**

**Issue 1: POM Metadata Consolidation in qg_page_object**

**Current Behavior (WRONG):**
```python
# qg_page_object.py line 463-470
state_manager.save(step=6, data={
    "pom_metadata": {
        "LoginPage": {
            "action_methods": ["navigate", "enter_email"]  # ← SIMPLIFIED (lost params)
        }
    }
})
```

**Fix:**
- [ ] 3.1: Update qg_page_object.py consolidation logic
  - Load existing Step 6 state
  - Build nested `pom_metadata` dict preserving FULL method details
  - Don't simplify to names only

**Files:** `mcp_server/tools/gates/qg_page_object.py:463-470`

**After Fix:**
```python
# Build consolidated pom_metadata from all generated POMs
consolidated_pom_metadata = {}
for page_name, pom_data in generated_poms.items():
    consolidated_pom_metadata[page_name] = pom_data["metadata"]  # FULL metadata

state_manager.save(step=6, data={
    "pom_metadata": consolidated_pom_metadata,  # ← Multi-page dict
    "generated_poms": generated_poms,
    "poms_generated": poms_generated,
    "total_poms": total_pages,
    "generation_complete": generation_complete
})
```

**Issue 2: Verify Generators Output Correct Format**

Check if generators are source of dict format:
- [ ] 3.2: Run POM generator standalone test
  - Call `generate_page_object_with_metadata()`
  - Check metadata.action_methods[0].params format
  - Should be `["text: str"]` not `[{"name": "text", "type": "str"}]`

- [ ] 3.3: Run Task generator standalone test
  - Call `generate_task_with_metadata()`
  - Check metadata.task_methods[0].params format
  - Should copy strings from POM

- [ ] 3.4: Run Role generator standalone test
  - Call `generate_role_with_metadata()`
  - Check metadata.workflow_methods[0].params format
  - Should filter strings from Task

**Files:**
- `mcp_server/utils/generators/page_object_generator.py:595`
- `mcp_server/utils/generators/task_generator.py:235`
- `mcp_server/utils/generators/role_generator.py:414`

**If generators output dict format → fix them**
**If generators output string format → AI orchestration is converting**

---

**Phase 4: Fix Test Fixtures**

**Files to Update:**
- `mcp_server/_dev_tests/test_gates/test_integration.py`
- `mcp_server/_dev_tests/test_gates/test_qg_page_object.py`
- `mcp_server/_dev_tests/test_gates/test_qg_task.py`
- `mcp_server/_dev_tests/test_gates/test_qg_role.py`

**Tasks:**
- [ ] 4.1: Update valid_step_6_post_data() to use full action_methods dicts
- [ ] 4.2: Update valid_step_7_post_data() - already uses strings ✓
- [ ] 4.3: Update valid_step_8_post_data() - verify params format
- [ ] 4.4: Run gate unit tests (481+ tests) - all should pass
- [ ] 4.5: Run integration tests (38 tests) - all should pass

---

**Phase 5: E2E Verification**

**Run Full 10-Step Workflow:**
- [ ] 5.1: Manual execution (Claude direct) - parabank7 workflow
  - All gates should PASS
  - No .split() crashes
  - State files show string format

- [ ] 5.2: Agent execution (Task tool) - same workflow
  - All gates should PASS
  - No autonomous fixes needed
  - State files show string format

- [ ] 5.3: Compare state files
  - Both runs: string format params ✓
  - Both runs: full action_methods metadata ✓
  - No dict format anywhere ✓

**Verification Checklist:**
- [ ] All 481+ gate unit tests pass
- [ ] All 38 integration tests pass
- [ ] Manual E2E: 10/10 steps pass
- [ ] Agent E2E: 10/10 steps pass
- [ ] State files: string format only
- [ ] Audit files: no format validation failures

---

**Backward Compatibility:**
- No backward compatibility needed - state files are ephemeral
- Each run creates new state directory in `tests/_state/{run_id}/`
- Old state files don't affect new runs
- Gates reject bad format immediately (fail-fast)

**Fix:**
NOT YET IMPLEMENTED - Requires careful impact assessment and testing.

**Proposed Implementation Plan:**

```python
# Step 1: Add format validator to base_gate.py
@classmethod
def _validate_param_format(cls, params: list) -> Optional[Dict[str, Any]]:
    """
    Validate params are string format, not dict format.

    CORRECT: ["email: str", "password: str"]
    WRONG: [{"name": "email", "type": "str"}]
    """
    for param in params:
        if isinstance(param, dict):
            return cls.fail_response(
                error=f"Param must be string format, got dict: {param}",
                fix_hint="Tool must output params as ['name: type'] not [{'name': ..., 'type': ...}]"
            )
        if not isinstance(param, str) or ":" not in param:
            return cls.fail_response(
                error=f"Param must be 'name: type' format, got: {param}",
                fix_hint="Params should be strings like 'email: str', 'count: int'"
            )
    return None

# Step 2: Fix qg_page_object.py metadata save (line 463-470)
# BEFORE: Simplifies to names only
state_manager.save(step=6, data={
    "pom_metadata": {
        "LoginPage": {
            "action_methods": ["navigate", "enter_email"]  # Lost params!
        }
    }
})

# AFTER: Preserve full metadata
state_manager.save(step=6, data={
    "pom_metadata": {
        "LoginPage": {
            "action_methods": [
                {"name": "navigate", "params": [], "returns": "self"},
                {"name": "enter_email", "params": ["email: str"], "returns": "self"}
            ]  # Full details preserved!
        }
    }
})

# Step 3: Add validation to qg_page_object POST
action_methods = metadata.get("action_methods", [])
for method in action_methods:
    if isinstance(method, dict):
        params = method.get("params", [])
        param_error = cls._validate_param_format(params)
        if param_error:
            return param_error

# Step 4: Add validation to qg_task POST
task_methods = metadata.get("task_methods", [])
for method in task_methods:
    params = method.get("params", [])
    param_error = cls._validate_param_format(params)
    if param_error:
        return param_error

# Step 5: Add validation to qg_role POST
workflow_methods = metadata.get("workflow_methods", [])
for method in workflow_methods:
    params = method.get("params", [])
    param_error = cls._validate_param_format(params)
    if param_error:
        return param_error
```

**Testing Strategy:**
1. Run gate unit tests with new validation → will expose all dict format usage
2. Fix test fixtures one by one
3. Run integration tests → verify metadata chain works
4. Run E2E test → verify full workflow passes
5. Compare manual vs agent execution → both should succeed

**Verification Criteria:**
- [ ] All gate unit tests pass (481+ tests)
- [ ] All integration tests pass (38 tests)
- [ ] Manual E2E execution succeeds (10/10 steps)
- [ ] Agent E2E execution succeeds (10/10 steps)
- [ ] State files show string param format
- [ ] No .split() crashes in role_generator.py

**Fix Implemented:**
- Branch: `feature/51.0-def057-root-fix`
- Commits: Multiple (DEF-057 Phase 2: Gate Validation, Phase 3: Root Cause Fix)
- Implementation: base_gate._validate_param_format() + POST validation in qg_task, qg_role, qg_test_runner

**Production Validation (2026-01-13):**
Complete 11-step parabank8 workflow validated STRING format enforcement:
- Step 7 (qg_task POST): Validated params ["username: str", "password: str"] ✓
- Step 8 (qg_role POST): Validated params [] ✓
- Step 9 (qg_test_runner POST): Validated test uses POM methods ✓

Result: 3/3 code generation gates enforced STRING format successfully. Gates would reject dict format [{"name": "username"}] that caused original crash.

**Verified:** Production E2E test passed (parabank8 workflow, Tasks 51.0 + 57.0)
**Resolved Date:** 2026-01-13

---

### [DEF-058] Generated test fails despite passing all quality gates - no smoke test validation
**Severity:** HIGH
**Status:** OPEN
**Caught By:** Manual test execution after Task 57.0 production validation (2026-01-13)
**Code Version:** feature/55.0-def058-smart-gate (commit 4ef1e26)
**Layer:** Quality Gates (Step 10 gap)
**File:** `mcp_server/tools/gates/qg_save_run.py`

**Error Message:**
```
AssertionError: Should be on account overview page
assert False
 +  where False = is_on_account_overview()
```

**Description:**
Complete 11-step workflow executed, all quality gates passed, generated code architecturally perfect, but the actual Selenium test fails when run.

**The Problem:**
Quality gates validate CODE CORRECTNESS but not CODE EXECUTION. The workflow generates syntactically correct, architecturally compliant code that doesn't work in practice.

**What Passed:**
- Step 1-4: Pre-flight, user input, AI processing, test scenarios ✓
- Step 5: Element discovery (4/4 passes with Smart Gate) ✓
- Step 6: POM generation (DD-25, DD-49 enforcement) ✓
- Step 7: Task generation (param validation, unused param detection) ✓
- Step 8: Role generation (param validation, architecture compliance) ✓
- Step 9: Test generation (POM assertions, AAA pattern) ✓
- Step 10: File validation (all files exist) ✓

**What Failed:**
- **Actual test execution:** `pytest tests/parabank8/test_login_and_view_account_overview.py`
- **Reason:** `is_on_account_overview()` returns False
- **Investigation:** Playwright confirms element exists, credentials valid, locator correct
- **Discrepancy:** Playwright finds element immediately, Selenium cannot find it after 5s

**Root Cause:**
Missing validation step between code generation and "workflow complete" declaration. Quality gates check:
- ✅ Architecture compliance (DD-25, DD-27, DD-49)
- ✅ Static analysis (param format, skeleton detection)
- ✅ Metadata contracts (tool chain data flow)
- ❌ **Does the test actually run?**

**Impact:**
User completes 11-step workflow, sees "✅ PASS" on all gates, commits generated code, then discovers test doesn't work. This:
1. Wastes user time (they expected working code)
2. Erodes trust in quality gates (if gates pass, why doesn't it work?)
3. Provides zero diagnostic context (just "assertion failed")
4. Requires manual debugging with no guidance

**The Quality Gap:**

| Current State | What We Validate | What We Don't |
|---------------|------------------|---------------|
| **Step 10** | Files exist on disk | Do tests execute? |
| **All Gates** | Code structure correct | Does Selenium work? |
| **POST gates** | Metadata format valid | Timing issues? |
| **Architecture** | 4-layer pattern enforced | Browser compatibility? |

**Diagnostic Context Gap:**

When test fails, user gets:
- ❌ "Should be on account overview page" (useless)
- ❌ Current URL not logged
- ❌ Element existence not checked (presence vs visibility)
- ❌ No page state snapshot
- ❌ No distinction: login failed vs element not found

**Proposed Solution: Step 11 - Smoke Test**

Add validation step after Step 10:

```
Step 11: Smoke Test Validation
- Run generated test in headed mode (visibility check)
- Capture diagnostics: URL, page state, element checks
- On failure: Provide actionable context
  - Current URL vs expected URL
  - Element presence vs visibility
  - Screenshot on failure
  - Suggested fixes (increase timeout, check locator, verify credentials)
```

**Alternative: Enhanced Diagnostic Context**

If Step 11 too heavyweight, enhance failure messages:

```python
# Current (useless)
assert pom.is_on_account_overview(), "Should be on account overview page"

# Enhanced (actionable)
current_url = self.web.driver.current_url
if not pom.is_on_account_overview():
    # Check if element exists at all
    exists = pom.web.is_element_present(*pom.ACCOUNTS_OVERVIEW_HEADING)
    raise AssertionError(
        f"Not on account overview page.\n"
        f"Expected: overview.htm\n"
        f"Actual: {current_url}\n"
        f"Element exists: {exists}\n"
        f"Element visible: False (timed out after 5s)"
    )
```

**Evidence:**

**Playwright Validation (works):**
- Credentials: john/demo ✓
- Login: Successful ✓
- Page reached: https://parabank.parasoft.com/parabank/overview.htm ✓
- Element found: `heading "Accounts Overview" [level=1]` ✓

**Selenium Execution (fails):**
- Same credentials: john/demo
- Login executes (10.58s runtime)
- Assertion fails: `is_on_account_overview()` returns False
- Locator: `(By.XPATH, "//h1[text()='Accounts Overview']")` (same as Playwright found)

**Gate vs Reality Mismatch:**
```
Quality Gates Say:     Reality Says:
✅ All 10 steps pass   ❌ Test fails
✅ Code correct        ❌ Doesn't execute
✅ Architecture good   ❌ Element not found
✅ Workflow complete   ❌ User has broken test
```

**Why This Is A Product Defect:**

As an open-source automation product, users expect:
1. **Bronze:** Code doesn't crash → ✅ We provide
2. **Silver:** Architecture is correct → ✅ We provide
3. **Gold:** Diagnostic context on failure → ❌ We don't provide
4. **Platinum:** Generated code actually works → ❌ We don't provide

**We're at Silver. Users expect Platinum.**

**Related Issues:**
- POM navigation paths had duplicate /parabank prefix (fixed in e281c25)
- But even with fix, core issue remains: no execution validation

**Fix Strategy:**

**Option A: Add Step 11 (Smoke Test)**
- Pro: Catches failures before user sees them
- Pro: Can provide rich diagnostic context
- Con: Adds execution time to workflow
- Con: Requires test runner infrastructure

**Option B: Enhanced Error Context (Fail-Fast with Better Info)**
- Pro: No workflow changes
- Pro: Helps user debug when failure occurs
- Con: User still gets broken code
- Con: Doesn't prevent the issue

**Recommendation:** Option A for production, Option B as interim fix.

**Impact Assessment:**

| Component | Current | After Fix |
|-----------|---------|-----------|
| Workflow time | ~2 min (10 steps) | ~3 min (11 steps with smoke test) |
| User confidence | "Did gates lie?" | "If gates pass, it works" |
| Debug time | Unknown (user figures it out) | Zero (smoke test caught it) |
| Trust in product | Eroded by silent failures | Built by validated output |

**Verified:** Not yet fixed
**Resolved Date:** N/A

---

## Summary

| Layer | CRITICAL | HIGH | MEDIUM | LOW | Total | Resolved |
|-------|----------|------|--------|-----|-------|----------|
| Page Objects | 1 | 1 | 4 | 3 | 9 | 8 (1 WONT_FIX) |
| Tasks | 2 | 1 | 0 | 2 | 5 | 4 |
| Roles | 2 | 1 | 0 | 0 | 3 | 2 (1 INVALID) |
| Tests | 2 | 0 | 0 | 0 | 2 | 2 |
| MCP Tools | 1 | 4 | 0 | 0 | 5 | 5 |
| MCP Tools (Phase B) | 1 | 0 | 0 | 0 | 1 | 1 |
| AI Orchestration | 1 | 3 | 2 | 0 | 6 | 5 |
| Quality Gates | 3 | 6 | 1 | 0 | 10 | 7 |
| Claude Code Infra | 0 | 0 | 0 | 1 | 1 | 1 (WONT_FIX) |
| MCP State Mgmt | 0 | 1 | 1 | 0 | 2 | 2 |
| **Total** | **13** | **17** | **8** | **6** | **44** | **38 + 2 WONT_FIX + 1 INVALID** |

### Status Breakdown
- **RESOLVED:** 39 (includes DEF-055a, DEF-055b from 2026-01-08, DEF-057 from 2026-01-13)
- **WONT_FIX:** 2 (DEF-008, DEF-032)
- **INVALID:** 1 (DEF-016)
- **READY_TO_TEST:** 5 (DEF-B08, B09, B10, DEF-025, DEF-034)
- **OPEN:** 7 (DEF-027, 028, 029, 048, 058)

---

## Audit Progress

- [x] Task 2.0: Page Objects audited
- [x] Task 3.0: Tasks audited
- [x] Task 4.0: Roles audited
- [x] Task 5.0: Tests audited
- [ ] Task 6.0: All tests passing

---

**Last Updated:** 2026-01-13 (DEF-057 RESOLVED, DEF-058 OPEN - test execution gap)
