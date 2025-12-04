# Tasks: MCP Tool Chain Refactor (Phase B)

**PRD:** `1-prd-mcp-tool-refactor.md` (v2.0)
**Created:** 2025-12-02
**Status:** Ready for Implementation

---

## Relevant Files

### Files to Update
- `mcp_server/tools/tool_01_generate_tests_from_user_story.py` - Add metadata output format
- `mcp_server/tools/tool_02_discover_page_elements.py` - Add metadata output format
- `mcp_server/tools/tool_03_generate_page_object.py` - Accept expected_states parameter
- `mcp_server/tools/tool_04_generate_task.py` - Check existing, accept POM metadata
- `mcp_server/tools/tool_05_generate_role.py` - Check existing, accept Task metadata
- `mcp_server/tools/tool_06_generate_test_runner.py` - Accept Role + POM metadata
- `mcp_server/utils/generators/page_object_generator.py` - Generate state methods from expected_states
- `mcp_server/utils/generators/task_generator.py` - Use POM metadata for method calls
- `mcp_server/utils/generators/role_generator.py` - Use Task metadata for method calls
- `mcp_server/utils/generators/test_generator.py` - Use Role + POM metadata for assertions

### Test Artifacts (Generated During E2E)

**File Placement Rules:**
1. **Test files** always go in `tests/test1/`, `tests/test2/`
2. **NEW classes** (if needed) go in `framework/*/test1/`, `framework/*/test2/`
3. **AI dynamically discovers** existing classes via Tools 4-5 check-existing pattern (DD-12)

**Directory Structure:**
```
tests/
  test1/                    # B.6 Simple E2E test
  test2/                    # B.7 Medium E2E test

framework/
  pages/test1/              # NEW POMs only if check-existing finds no match
  tasks/test1/              # NEW Tasks only if check-existing finds no match
  roles/test1/              # NEW Roles only if check-existing finds no match
```

**Reports:**
- `reports/test1_report.html` - Simple E2E HTML report
- `reports/test2_report.html` - Medium E2E HTML report

### Notes
- Run E2E tests visible: `pytest tests/test1/ -v --headless=False`
- Generate HTML report: `--html=reports/test1_report.html --self-contained-html`
- AI dynamically scans framework/ via Tools 4-5 to find reusable classes
- No hardcoded "reuse list" - AI discovers at runtime

---

## Tasks

- [x] B.1 Tool 1-2 Metadata Output [CORE]
  - [x] B.1.1 Create branch `feature/B.1-tool-1-2-metadata`
  - [x] B.1.2 Update Tool 1 to output `test_scenarios[]` in metadata format:
    - Each scenario: {title, given, when, then, workflow}
    - Add `metadata` key to JSON response
  - [x] B.1.3 Update Tool 2 to output `discovered_elements[]` in metadata format:
    - Each element: {name, type, locator}
    - Ensure consistent with what Tool 3 expects
  - [x] B.1.4 Test Tool 1 standalone: `python mcp_server/tools/tool_01_generate_tests_from_user_story.py`
  - [x] B.1.5 Test Tool 2 standalone: `python mcp_server/tools/tool_02_discover_page_elements.py`
  - [x] B.1.6 Verify metadata output format matches PRD Section 6.2
  - [x] B.1.7 Record results
  - [x] B.1.8 Commit: `feat: add metadata output to Tools 1-2 (Task B.1)`

- [x] B.2 Tool 3 expected_states [CORE]
  - [x] B.2.1 Create branch `feature/B.2-tool-3-expected-states`
  - [x] B.2.2 Update `page_object_generator.py` to accept `expected_states` parameter
  - [x] B.2.3 Generate state-check methods from expected_states:
    - `is_*` methods return bool
    - `has_*` methods return bool
    - `get_*` methods return str/int
  - [x] B.2.4 Update Tool 3 to pass expected_states to generator
  - [x] B.2.5 Ensure pom_metadata.state_methods includes generated state methods
  - [x] B.2.6 Test Tool 3 with sample expected_states input
  - [x] B.2.7 Verify generated POM has correct state-check methods
  - [x] B.2.8 Record results
  - [x] B.2.9 Commit: `feat: add expected_states support to Tool 3 (Task B.2)`

- [x] B.3 Tool 4 Refactor [CORE]
  - [x] B.3.1 Create branch `feature/B.3-tool-4-refactor`
  - [x] B.3.2 Implement check-existing pattern in Tool 4:
    - Scan `framework/tasks/` for existing Task classes
    - Return `existing_found` status if task already handles intent
    - Include existing_class, existing_methods in response
  - [x] B.3.3 Update `task_generator.py` to use POM metadata:
    - Read action_methods from pom_metadata
    - Generate Task methods that call actual POM methods
    - No hardcoded method names
  - [x] B.3.4 Ensure task_metadata output includes:
    - class_name, import_path, composed_pages[], task_methods[]
  - [x] B.3.5 Test Tool 4 with check_existing=True (should find CommonTasks)
  - [x] B.3.6 Test Tool 4 with pom_metadata input
  - [x] B.3.7 Verify generated Task calls actual POM methods from metadata
  - [x] B.3.8 Record results
  - [x] B.3.9 Commit: `feat: add check-existing and POM metadata to Tool 4 (Task B.3)`

- [x] B.4 Tool 5 Refactor [CORE]
  - [x] B.4.1 Create branch `feature/B.4-tool-5-refactor`
  - [x] B.4.2 Implement check-existing pattern in Tool 5:
    - Scan `framework/roles/` for existing Role classes
    - Return `existing_found` status if role matches persona
    - Include existing_class, existing_methods in response
  - [x] B.4.3 Update `role_generator.py` to use Task metadata:
    - Read task_methods from task_metadata
    - Generate Role methods that call actual Task methods
    - No hardcoded method names
  - [x] B.4.4 Ensure role_metadata output includes:
    - class_name, import_path, composed_tasks[], workflow_methods[]
  - [x] B.4.5 Test Tool 5 with check_existing=True (should find RegisteredUser if exists)
  - [x] B.4.6 Test Tool 5 with task_metadata input
  - [x] B.4.7 Verify generated Role calls actual Task methods from metadata
  - [x] B.4.8 Record results
  - [x] B.4.9 Commit: `feat: add check-existing and Task metadata to Tool 5 (Task B.4)`

- [x] B.5 Tool 6 Refactor [CORE]
  - [x] B.5.1 Create branch `feature/B.5-tool-6-refactor`
  - [x] B.5.2 Update `test_generator.py` to accept Role + POM metadata:
    - Read workflow_methods from role_metadata
    - Read state_methods from pom_metadata
  - [x] B.5.3 Generate test assertions using actual POM state methods:
    - `assert page.is_logged_in()` not `assert result == True`
    - Use method names from pom_metadata.state_methods
  - [x] B.5.4 Ensure AAA pattern in generated tests:
    - Arrange: Create Role and POM instances
    - Act: ONE Role workflow method call
    - Assert: Via POM state-check methods
  - [x] B.5.5 Test Tool 6 with role_metadata + pom_metadata input
  - [x] B.5.6 Verify generated test uses actual method names from metadata
  - [x] B.5.7 Verify no hardcoded method names in generated test
  - [x] B.5.8 Record results
  - [x] B.5.9 Commit: `feat: add Role + POM metadata to Tool 6 (Task B.5)`

- [x] B.6 Simple E2E Test [GLUE]
  - [x] B.6.1 Create branch `feature/B.6-simple-e2e`
  - [x] B.6.2 Define test requirement:
    - "As a guest, I want to browse products in the Women category"
    - URL: http://automationpractice.pl/index.php
    - Expected: Products displayed in Women category
  - [x] B.6.3 Execute Step 1-2 (AI Processing):
    - Extract role_name: GuestUser
    - Extract domain: catalog
    - Extract expected_states: [{name: "has_products", ...}]
    - Initialize metadata context
  - [x] B.6.4 Execute Step 3 (Tool 1): Parse BDD, get test_scenarios
  - [x] B.6.5 Execute Step 4 (Tool 2): Skipped - reusing existing ProductListPage
  - [x] B.6.6 Execute Step 5 (Tool 3): Skipped - reusing existing ProductListPage
  - [x] B.6.7 Execute Step 6 (Tool 4): Check-existing found CatalogTasks - REUSED
  - [x] B.6.8 Execute Step 7 (Tool 5): Check-existing found GuestUser - REUSED
  - [x] B.6.9 Execute Step 8 (Tool 6): Generate Test with metadata
  - [x] B.6.10 Execute Step 9: Save test to `tests/test1/`
  - [x] B.6.11 Add `__init__.py` files to new directories
  - [x] B.6.12 Run test with visible browser: `pytest tests/test1/ -v --headless=False`
  - [x] B.6.13 Generate HTML report: `--html=reports/test1_report.html --self-contained-html`
  - [x] B.6.14 User validates: browser visible, test passes, report generated
  - [x] B.6.15 Record results
  - [x] B.6.16 Commit: `feat: simple E2E test - catalog browse (Task B.6)`

- [x] B.6.5 Tool 2 Dynamic Discovery Enhancement [CORE]
  - [x] B.6.5.1 Create branch `feature/B.6.5-tool2-dynamic-discovery`
  - [x] B.6.5.2 Update Tool 2 to accept `driver_session` parameter (existing WebDriver instance)
  - [x] B.6.5.3 Update Tool 2 to accept `scope` parameter (CSS selector to limit discovery)
  - [x] B.6.5.4 When `driver_session` provided: skip creating new driver, use existing
  - [x] B.6.5.5 When `driver_session` provided: do NOT close driver (AI owns lifecycle)
  - [x] B.6.5.6 Test static flow: Tool 2 with URL only (existing behavior)
  - [x] B.6.5.7 Test dynamic flow: Tool 2 with driver_session + scope
  - [x] B.6.5.8 Run checks (syntax OK) + Add DD-21 documentation
  - [x] B.6.5.9 Record results
  - [x] B.6.5.10 Commit: `feat: add dynamic element discovery to Tool 2 (DD-20, DD-21)`

- [ ] B.7 Medium E2E Test - Add to Cart [GLUE]
  - [ ] B.7.1 Create branch `feature/B.7-medium-e2e`
  - [ ] B.7.2 Define test requirement:
    - "As a guest, I want to add a product to my cart so I can purchase it later"
    - URL: http://www.automationpractice.pl/index.php
    - Expected: Product added, cart confirmation modal displayed with correct product
  - [ ] B.7.3 Execute Step 1-2 (AI Processing):
    - Extract role_name: GuestUser
    - Extract domain: cart
    - Extract expected_states: [{name: "is_modal_displayed"}, {name: "has_product_in_cart"}]
    - Identify DYNAMIC elements: cart confirmation modal (requires Add to Cart click)
    - Initialize metadata context
  - [ ] B.7.4 Execute Step 3 (Tool 1): Parse BDD, get test_scenarios
  - [ ] B.7.5 Execute Step 4 (Tool 2) - DYNAMIC FLOW (DD-20):
    - AI creates WebDriver instance
    - AI navigates to product page
    - AI hovers over product, clicks "Add to Cart"
    - AI waits for modal to appear
    - AI calls Tool 2 with driver_session + scope="#layer_cart"
    - Tool 2 discovers modal elements
  - [ ] B.7.6 Execute Step 5 (Tool 3): Generate CartConfirmationModal POM (NEW)
  - [ ] B.7.7 Execute Step 6 (Tool 4): Generate CartTasks (NEW)
  - [ ] B.7.8 Execute Step 7 (Tool 5): Extend GuestUser with add_to_cart workflow
  - [ ] B.7.9 Execute Step 8 (Tool 6): Generate Test with metadata
  - [ ] B.7.10 Execute Step 9: Save test to `tests/test2/`, new classes to appropriate dirs
  - [ ] B.7.11 Add `__init__.py` files to new directories
  - [ ] B.7.12 Run test with visible browser: `pytest tests/test2/ -v --headless=False`
  - [ ] B.7.13 Generate HTML report: `--html=reports/test2_report.html --self-contained-html`
  - [ ] B.7.14 User validates: browser visible, modal appears, test passes, report generated
  - [ ] B.7.15 Record results
  - [ ] B.7.16 Commit: `feat: medium E2E test - add to cart with dynamic discovery (Task B.7)`

- [ ] B.8 Cleanup [GLUE]
  - [ ] B.8.1 Create branch `feature/B.8-cleanup`
  - [ ] B.8.2 Verify all tools (1-6) output correct metadata format
  - [ ] B.8.3 Verify no hardcoded method names remain in generators
  - [ ] B.8.4 Run both E2E tests: `pytest tests/test1/ tests/test2/ -v`
  - [ ] B.8.5 Clean up old test artifacts (devtest1/, devtest2/ if exist)
  - [ ] B.8.6 Update PRD status to "Complete"
  - [ ] B.8.7 Update SESSION.md with Phase B completion
  - [ ] B.8.8 Record final results
  - [ ] B.8.9 Commit: `feat: complete Phase B - MCP tool chain refactor (Task B.8)`
  - [ ] B.8.10 Merge feature branch to main

---

## Done When Criteria

### Per Task
- All subtasks completed
- Tool tests pass (standalone execution)
- Generated code matches framework patterns
- Commands + results documented

### Phase B Complete
- All 6 tools output/accept correct metadata
- Check-existing pattern works (Tools 4-5)
- expected_states generates correct POM state methods
- Simple E2E test passes with visible browser + HTML report
- Medium E2E test passes with visible browser + HTML report
- User validates both E2E tests visually
- All commits merged to main

---

## Commands Run

```bash
# Task B.1 - Tool 1-2 Metadata Output
git checkout -b feature/B.1-tool-1-2-metadata
python mcp_server/tools/tool_01_generate_tests_from_user_story.py
python mcp_server/tools/tool_02_discover_page_elements.py
```

## Results

### Task B.1 Results (2025-12-03)

**Tool 1 Output:**
- Status: SUCCESS
- `metadata.test_scenarios[]` contains: `{title, given, when, then, workflow}`
- Changed field name from `name` to `title` for clarity

**Tool 2 Output:**
- Status: SUCCESS
- `metadata.discovered_elements[]` contains: `{name, type, locator}`
- Discovered 23 elements on auth page (4 buttons, 12 links, 5 inputs, 2 images)

**Live Test (Login Flow):**
- Step 1-2: AI extracted role=RegisteredUser, domain=auth, expected_states=[is_logged_in]
- Step 3 (Tool 1): Generated test scenario `test_valid_login_with_email_and_password`
- Step 4 (Tool 2): Discovered EMAIL, PASSWD, SUBMITLOGIN elements with correct locators

**Documentation Updated:**
- PRD FR-09: Changed `name` to `title`
- FRAMEWORK.md Section 8.4: Changed `name` to `title`
- Task list: Updated to reflect `title` field

### Task B.2 Results (2025-12-03)

**Defect Found & Fixed:**
- DEF-B01: `generators/__init__.py` imported non-existent `get_available_workflows` - RESOLVED

**Implementation:**
- Added `expected_states` parameter to `generate_page_object()` and `generate_page_object_with_metadata()`
- Added `_generate_expected_state_methods()` function to create state-check methods from expected_states
- Updated `generate_state_check_methods_block()` to accept expected_states (priority over workflow defaults)
- Updated `_build_state_methods_metadata()` to build metadata from expected_states
- Updated Tool 3 to pass expected_states to generator

**Cumulative Live Test (Steps 1-5, Tools 1-3):**
- Step 1: User input - "As a registered user, I want to login with email and password"
- Step 2: AI extracted role=RegisteredUser, domain=auth, expected_states=[is_logged_in, is_account_page_displayed]
- Step 3 (Tool 1): Generated test scenario `test_valid_login_with_email_and_password` - SUCCESS
- Step 4 (Tool 2): Discovered 23 elements, filtered 3 for login (EMAIL, PASSWD, SUBMITLOGIN) - SUCCESS
- Step 5 (Tool 3): Generated LoginPage with expected_states methods - SUCCESS
  - `is_logged_in()` found in generated code ✓
  - `is_account_page_displayed()` found in generated code ✓
  - `metadata.state_methods` contains both methods ✓

### Task B.3 Results (2025-12-03)

**Implementation Verified:**
- Tool 4 and task_generator.py already implemented correctly from prior work
- No code changes needed - verification only

**Check-Existing Pattern:**
- Status: SUCCESS
- Found existing: `['CommonTasks']` for auth workflow
- Existing methods: `['navigate_to_login_page', 'log_in', 'log_out', 'register_new_user', ...]`

**Metadata-Driven Generation:**
- Input: `pom_metadata` with action_methods + state_methods
- Generated: `AuthTasks` with `log_in(email, password)` calling `[enter_email, enter_passwd, click_submitlogin]`
- task_metadata output: class_name, import_path, composed_pages[], task_methods[] ✓

**Cumulative Live Test (Steps 1-6, Tools 1-4):**
- Step 1: User input - login requirement + URL
- Step 2: AI extracted role=RegisteredUser, domain=auth, expected_states
- Step 3 (Tool 1): Generated test scenario `test_valid_login_with_email_and_password` - SUCCESS
- Step 4 (Tool 2): Discovered 23 elements, filtered 3 for login - SUCCESS
- Step 5 (Tool 3): Generated LoginPage with expected_states methods - SUCCESS
- Step 6 (Tool 4): Check-existing found CommonTasks, force-generated AuthTasks - SUCCESS
  - `log_in()` calls actual POM methods from metadata ✓
  - task_metadata.task_methods contains both methods ✓

### Task B.4 Results (2025-12-03)

**Check-Existing Pattern:**
- Status: SUCCESS
- Found existing: `RegisteredUser` in auth domain, `GuestUser` in guest domain
- Existing methods: `['login', 'logout', 'register']` for RegisteredUser

**Metadata-Driven Generation:**
- Input: `task_metadata` with class_name, import_path, task_methods[]
- Generated: `RegisteredUser` with `login()` calling `self.auth_tasks.log_in(self.email, self.password)`
- role_metadata output: class_name, import_path, composed_tasks[], workflow_methods[] ✓

**Bug Fixed:**
- Check-existing was not flattening roles across domains
- Roles are stored as `{"auth": ["RegisteredUser"], "guest": ["GuestUser"]}`
- Fixed to iterate all domains and flatten before matching

**Cumulative Live Test (Steps 1-7, Tools 1-5):**
- Step 1: User input - login requirement + URL
- Step 2: AI extracted role=RegisteredUser, domain=auth, expected_states
- Step 3 (Tool 1): Generated test scenario - SUCCESS
- Step 4 (Tool 2): Discovered 3 elements (mock) - SUCCESS
- Step 5 (Tool 3): Generated LoginPage with 3 action, 2 state methods - SUCCESS
- Step 6 (Tool 4): Check-existing found CommonTasks, force-generated AuthTasks - SUCCESS
- Step 7 (Tool 5): Check-existing found RegisteredUser, force-generated with metadata - SUCCESS
  - `login()` calls `auth_tasks.log_in(self.email, self.password)` ✓
  - role_metadata.workflow_methods contains login ✓

### Task B.5 Results (2025-12-03)

**Implementation:**
- Updated `test_generator.py`:
  - Added `_generate_test_method_from_metadata()` function
  - Added `generate_test_methods_from_metadata()` function
  - Added `generate_test_with_metadata()` function
  - Returns code + metadata for downstream validation
- Updated `tool_06_generate_test_runner.py`:
  - Accepts `role_metadata` and `pom_metadata` parameters
  - Prefers metadata over legacy `role` parameter
  - Returns test_metadata with methods and assertions used
- Updated `generators/__init__.py`:
  - Exported `generate_test_with_metadata`

**PRD Requirements Implemented:**
- FR-34: Tool 6 accepts role_metadata + pom_metadata ✓
- FR-35: Generate tests calling actual Role methods from metadata ✓
- FR-36: Generate assertions using POM state methods from metadata ✓
- FR-37: AAA pattern (Arrange, Act ONE call, Assert via POM) ✓
- FR-38: @autologger("Test"), @pytest.mark.<domain> ✓

**Cumulative Live Test (Steps 1-8, Tools 1-6):**
- Step 1: User input - login requirement + URL
- Step 2: AI extracted role=RegisteredUser, domain=auth, expected_states
- Step 3 (Tool 1): Generated test scenario - SUCCESS
- Step 4 (Tool 2): Discovered 3 elements (mock) - SUCCESS
- Step 5 (Tool 3): Generated LoginPage with 3 action, 2 state methods - SUCCESS
- Step 6 (Tool 4): Check-existing found CommonTasks, force-generated AuthTasks - SUCCESS
- Step 7 (Tool 5): Check-existing found RegisteredUser, force-generated with metadata - SUCCESS
- Step 8 (Tool 6): Generated TestLogin using role_metadata + pom_metadata - SUCCESS
  - Test class: `TestLogin` ✓
  - Role used: `RegisteredUser` ✓
  - Page used: `LoginPage` ✓
  - Test methods: `['test_login']` ✓
  - Assertions: `['is_logged_in', 'is_account_page_displayed']` ✓

**Generated Test Code (key portion):**
```python
def test_login(self):
    # Arrange
    user_data = {"email": "testuser@example.com", "password": "TestPass123"}
    user = RegisteredUser(self.web, user_data, self.base_url)

    # Act - ONE workflow call, NO return value
    user.login()

    # Assert - Via Page Object state-check methods (NOT return value)
    assert self.login_page.is_logged_in(), "Is Logged In"
    assert self.login_page.is_account_page_displayed(), "Is Account Page Displayed"
```

### Task B.6 Results (2025-12-03)

**Test Requirement:**
- "As a guest, I want to browse products in the Women category"
- URL: http://www.automationpractice.pl/index.php

**Reused Existing Classes (DD-12 check-existing):**
- `GuestUser` - Role with `browse_category()` method
- `CatalogTasks` - Task with `browse_category()` method
- `ProductListPage` - POM with `has_products()` and `is_page_loaded()` state methods

**Generated Files:**
- `tests/test1/test_browse_women_category.py` - Test file
- `tests/test1/__init__.py` - Package init

**No New Framework Classes Generated** - All needed classes already existed

**Test Execution:**
```
pytest tests/test1/ -v --headless=False --html=reports/test1_report.html --self-contained-html
============================= 1 passed in 10.74s ==============================
```

**Validation:**
- Browser opened and was visible
- Navigated to Women category
- Products displayed (7 products)
- Assertions passed
- HTML report generated at `reports/test1_report.html`

**Defects Found & Fixed:**
- DEF-B02: AI did not apply file path override (DD-16) - RESOLVED
  - Tool 6 suggested `tests/catalog/`, fixed to `tests/test1/`
- DEF-B03: AI did not inject actual parameter values (DD-17) - RESOLVED
  - Tool 6 generated `"category_name_value"`, fixed to `"Women"`

**Design Decisions Added:**
- DD-16: File path override - AI saves to `tests/test1/`, `tests/test2/`
- DD-17: Parameter value injection - AI replaces placeholders with actual values
- DD-18: Import path validation - AI verifies imports match file locations

### Task B.6.5 Results (PASSED)

**Tool 2 Dynamic Discovery Enhancement - DD-20, DD-21**

**Files Modified:**
- `mcp_server/tools/tool_02_discover_page_elements.py` - Added `driver_session` and `scope` parameters
- `mcp_server/utils/element_discovery.py` - Added `scope` support to `discover_elements()` method
- `FRAMEWORK.md` - Added DD-21 visual flow diagram to Section 8.5

**Test Results:**
1. **Static Flow (URL only)**: PASSED - 23 elements discovered on login page
2. **Dynamic Flow (driver_session + scope)**: PASSED - 16 elements discovered in Quick View modal
   - Navigate to category page
   - Hover product → click Quick View
   - Switch to iframe
   - Call Tool 2 with `driver_session` + `scope="body"`
   - Found: 4 buttons, 6 links, 6 images

**Pain Points Encountered (documented in DD-21):**
- Homepage vs category page structure differences
- Products out of stock don't show modal
- Quick View modal content is in iframe (requires context switch)
- ElementNotInteractableException - needed JavaScript clicks

**Design Decisions Added:**
- DD-20: Dynamic element discovery - AI prepares page state before Tool 2 (already existed)
- DD-21: AI-SDET collaboration pattern when AI gets stuck during dynamic discovery
  - Primary: AI tries → asks SDET specific questions when stuck
  - Alternate: Playwright MCP for visual reconnaissance (future testing)

**Syntax Check:** PASSED (all Python files compile)

### Task B.7 Results (In Progress)

**Test Requirement (Updated):**
- "As a guest, I want to add a product to my cart so I can purchase it later"
- URL: http://www.automationpractice.pl/index.php
- Requires DYNAMIC element discovery (cart modal)

**Defects Found During B.7:**
- DEF-B04: AI called wrong function for Tool 2 - utility vs tool wrapper
  - AI imported `discover_page_elements` from `utils/` instead of `discover_elements` from `tools/`
  - Fix: DD-19 added - always import from `tools/`, never `utils/`
  - Status: IN_PROGRESS (awaiting clean E2E rerun)

- DEF-B05: Tool 2 cannot discover dynamic/modal elements
  - Tool 2 only discovers elements present on page load
  - Cannot discover modals, hover elements, AJAX content
  - Fix: DD-20 added - AI prepares page state, passes driver_session to Tool 2
  - Status: IN_PROGRESS (awaiting Tool 2 enhancement)

**Design Decisions Added:**
- DD-19: Tool invocation - always import from `tools/`, never `utils/`
- DD-20: Dynamic element discovery - AI prepares page state before Tool 2
