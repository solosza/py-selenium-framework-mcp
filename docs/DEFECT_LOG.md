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
**Status:** OPEN
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

---

### [DEF-020] Role data retrieval methods return values - violates "Roles return None" rule
**Severity:** HIGH
**Status:** OPEN
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
**Status:** IN_PROGRESS
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

| Option | Description |
|--------|-------------|
| **Quality gate MCP tools** | Create validation tools that enforce checks before each step proceeds |
| **SDK orchestration** | Code enforces step order and validations programmatically |
| **Pre-tool checkpoint in skill** | Add explicit "STOP: Is this static or dynamic?" before Tool 2 |

**Recommended Fix:** Quality gate MCP tools - enforce DD compliance at each step transition.

**Verified:** TBD - requires E2E rerun with enforcement in place
**Resolved Date:** TBD

---

### [DEF-B04] AI called wrong function for Tool 2 - utility vs tool wrapper
**Severity:** MEDIUM
**Status:** IN_PROGRESS
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

**Remaining Gap:** AI enforcement. Same pattern as DEF-B05 - DD exists but AI didn't follow it.

**Recommended Fix:** Quality gate MCP tools to validate imports before tool execution.

**Verified:** TBD - after adding DD-19 and rerunning E2E from start
**Resolved Date:** TBD

---

### [DEF-B06] AI did not format user story in explicit BDD before Tool 1
**Severity:** MEDIUM
**Status:** OPEN
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

**Verified:** TBD
**Resolved Date:** TBD

---

### [DEF-B07] Tool 6 ignores scenario parameter and generates generic template
**Severity:** HIGH
**Status:** OPEN
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

**Verified:** TBD
**Resolved Date:** TBD

---

### [DEF-B08] AI passed wrong element format to Tool 3 (not Tool 2 output format)
**Severity:** HIGH
**Status:** OPEN
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

**Verified:** TBD
**Resolved Date:** TBD

---

### [DEF-B09] Tool 4 generates skeleton Task code when POM metadata not passed
**Severity:** HIGH
**Status:** OPEN
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

**Verified:** TBD
**Resolved Date:** TBD

---

### [DEF-B10] AI manual Task code included locators (architecture violation)
**Severity:** CRITICAL
**Status:** OPEN
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

**Verified:** TBD
**Resolved Date:** TBD

---

## Summary

| Layer | CRITICAL | HIGH | MEDIUM | LOW | Total | Resolved |
|-------|----------|------|--------|-----|-------|----------|
| Page Objects | 1 | 1 | 4 | 3 | 9 | 8 (1 WONT_FIX) |
| Tasks | 2 | 1 | 0 | 2 | 5 | 4 |
| Roles | 2 | 1 | 0 | 0 | 3 | 2 (1 INVALID) |
| Tests | 2 | 0 | 0 | 0 | 2 | 2 |
| MCP Tools | 1 | 5 | 0 | 0 | 6 | 0 (4 IN_PROGRESS + 2 OPEN) |
| MCP Tools (Phase B) | 1 | 0 | 0 | 0 | 1 | 1 |
| AI Orchestration | 1 | 1 | 3 | 0 | 5 | 2 |
| **Total** | **10** | **9** | **7** | **5** | **31** | **18 + 1 WONT_FIX + 1 INVALID + 4 IN_PROGRESS + 5 OPEN** |

---

## Audit Progress

- [x] Task 2.0: Page Objects audited
- [x] Task 3.0: Tasks audited
- [x] Task 4.0: Roles audited
- [x] Task 5.0: Tests audited
- [ ] Task 6.0: All tests passing

---

**Last Updated:** 2025-12-01
