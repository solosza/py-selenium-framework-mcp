# Tasks: MCP Tool Refactor (Phase B)

**PRD:** `1-prd-mcp-tool-refactor.md`
**Created:** 2025-12-01
**Status:** Ready for Implementation

---

## Relevant Files

### Files to Create
- `mcp_server/utils/generators/__init__.py` - Package init, exports all generators
- `mcp_server/utils/generators/page_object_generator.py` - POM generation (NO decorators, returns self)
- `mcp_server/utils/generators/task_generator.py` - Task generation (@autologger, returns None)
- `mcp_server/utils/generators/role_generator.py` - Role generation (@autologger, returns None)
- `mcp_server/utils/generators/test_generator.py` - Test generation (asserts via POM)
- `mcp_server/_dev_tests/test_generators.py` - Unit tests for generators
- `mcp_server/_dev_tests/test_validation.py` - Automated validation script

### Files to Update
- `mcp_server/tools/tool_03_generate_page_object.py` - Use page_object_generator
- `mcp_server/tools/tool_04_generate_task.py` - Use task_generator
- `mcp_server/tools/tool_05_generate_role.py` - Use role_generator
- `mcp_server/tools/tool_06_generate_test_template.py` - Use test_generator

### Files to Deprecate
- `mcp_server/utils/code_generator.py` - Delete after migration complete

### Test Artifacts (Generated During E2E)
- `framework/pages/test1/` - Simple test POMs
- `framework/tasks/test1/` - Simple test Tasks
- `framework/roles/test1/` - Simple test Roles
- `tests/test1/` - Simple test (catalog browse)
- `framework/pages/test2/` - Medium test POMs
- `framework/tasks/test2/` - Medium test Tasks
- `framework/roles/test2/` - Medium test Roles
- `tests/test2/` - Medium test (auth + catalog)

### Notes
- Run generator tests: `python -m pytest mcp_server/_dev_tests/test_generators.py -v`
- Run E2E tests visible: `pytest tests/test1/ -v --headless=False`
- Generate HTML report: `--html=reports/test1_report.html --self-contained-html`

---

## Tasks

- [ ] B.1 Setup - Create generators directory structure & cleanup [GLUE]
  - [ ] B.1.1 Create branch `feature/B.1-generators-setup`
  - [ ] B.1.2 Create `mcp_server/utils/generators/` directory
  - [ ] B.1.3 Create `mcp_server/utils/generators/__init__.py` with placeholder exports
  - [ ] B.1.4 Clean up existing dev test artifacts in `mcp_server/_dev_tests/` (keep structure)
  - [ ] B.1.5 Create `framework/pages/test1/`, `framework/tasks/test1/`, `framework/roles/test1/`, `tests/test1/` directories
  - [ ] B.1.6 Create `framework/pages/test2/`, `framework/tasks/test2/`, `framework/roles/test2/`, `tests/test2/` directories
  - [ ] B.1.7 Verify directory structure created correctly
  - [ ] B.1.8 Commit: `chore: setup generators directory structure (Task B.1)`

- [ ] B.2 Tool 3 - Create page_object_generator and update tool [CORE]
  - [ ] B.2.1 Create branch `feature/B.2-page-object-generator`
  - [ ] B.2.2 Analyze existing `code_generator.py` POM generation logic
  - [ ] B.2.3 Create `page_object_generator.py` with embedded patterns:
    - NO decorators on methods
    - Locators as class-level UPPER_SNAKE constants
    - Action methods return `self` for chaining
    - State-check methods (`is_*`, `has_*`, `get_*`) for assertions
    - Docstrings and inline comments
  - [ ] B.2.4 Write unit tests in `mcp_server/_dev_tests/test_generators.py` for POM generator
  - [ ] B.2.5 Run tests: `python -m pytest mcp_server/_dev_tests/test_generators.py -v -k page_object`
  - [ ] B.2.6 Update `tool_03_generate_page_object.py` to use new generator
  - [ ] B.2.7 Test tool via MCP - generate a sample POM to `test1/`
  - [ ] B.2.8 Manually verify generated code matches framework patterns
  - [ ] B.2.9 Record test results
  - [ ] B.2.10 Commit: `feat: add page_object_generator with correct patterns (Task B.2)`

- [ ] B.3 Tool 4 - Create task_generator and update tool [CORE]
  - [ ] B.3.1 Create branch `feature/B.3-task-generator`
  - [ ] B.3.2 Analyze existing `code_generator.py` Task generation logic
  - [ ] B.3.3 Create `task_generator.py` with embedded patterns:
    - `@autologger.automation_logger("Task")` decorator on methods
    - Methods return `None` (no return statements)
    - NO locators (delegate to page objects)
    - Compose page objects in `__init__`
    - Docstrings and inline comments
  - [ ] B.3.4 Write unit tests for Task generator
  - [ ] B.3.5 Run tests: `python -m pytest mcp_server/_dev_tests/test_generators.py -v -k task`
  - [ ] B.3.6 Update `tool_04_generate_task.py` to use new generator
  - [ ] B.3.7 Test tool via MCP - generate a sample Task to `test1/`
  - [ ] B.3.8 Manually verify generated code matches framework patterns
  - [ ] B.3.9 Record test results
  - [ ] B.3.10 Commit: `feat: add task_generator with correct patterns (Task B.3)`

- [ ] B.4 Tool 5 - Create role_generator and update tool [CORE]
  - [ ] B.4.1 Create branch `feature/B.4-role-generator`
  - [ ] B.4.2 Analyze existing `code_generator.py` Role generation logic
  - [ ] B.4.3 Create `role_generator.py` with embedded patterns:
    - `@autologger.automation_logger("Role")` decorator on workflow methods
    - `@autologger.automation_logger("Role Constructor")` on `__init__`
    - Methods return `None` (no return statements)
    - Compose Tasks in `__init__` (not page objects directly)
    - Workflow methods orchestrate MULTIPLE task calls
    - Docstrings and inline comments
  - [ ] B.4.4 Write unit tests for Role generator
  - [ ] B.4.5 Run tests: `python -m pytest mcp_server/_dev_tests/test_generators.py -v -k role`
  - [ ] B.4.6 Update `tool_05_generate_role.py` to use new generator
  - [ ] B.4.7 Test tool via MCP - generate a sample Role to `test1/`
  - [ ] B.4.8 Manually verify generated code matches framework patterns
  - [ ] B.4.9 Record test results
  - [ ] B.4.10 Commit: `feat: add role_generator with correct patterns (Task B.4)`

- [ ] B.5 Tool 6 - Create test_generator and update tool [CORE]
  - [ ] B.5.1 Create branch `feature/B.5-test-generator`
  - [ ] B.5.2 Analyze existing `code_generator.py` Test generation logic
  - [ ] B.5.3 Create `test_generator.py` with embedded patterns:
    - `@autologger.automation_logger("Test")` decorator
    - `@pytest.mark.<category>` marker
    - Arrange: Create role and POM instances
    - Act: ONE role workflow method call (no return capture)
    - Assert: Via POM state-check methods (`assert page.has_products()`)
    - NOT asserting on return values
    - Docstrings and inline comments
  - [ ] B.5.4 Write unit tests for Test generator
  - [ ] B.5.5 Run tests: `python -m pytest mcp_server/_dev_tests/test_generators.py -v -k test_gen`
  - [ ] B.5.6 Update `tool_06_generate_test_template.py` to use new generator
  - [ ] B.5.7 Test tool via MCP - generate a sample test to `test1/`
  - [ ] B.5.8 Manually verify generated code matches framework patterns
  - [ ] B.5.9 Record test results
  - [ ] B.5.10 Commit: `feat: add test_generator with correct patterns (Task B.5)`

- [ ] B.6 Validation - Create automated validation script [CORE]
  - [ ] B.6.1 Create branch `feature/B.6-validation-script`
  - [ ] B.6.2 Create `mcp_server/_dev_tests/test_validation.py` with validation rules:
    - POM: no decorators, returns self, locators as constants, has state-checks
    - Task: has @autologger("Task"), returns None, no locators
    - Role: has @autologger("Role"), returns None, composes tasks
    - Test: has @autologger("Test"), asserts via POM, single role call
  - [ ] B.6.3 Write functions to parse and validate generated Python code
  - [ ] B.6.4 Test validation script against generated code in `test1/`
  - [ ] B.6.5 Run validation: `python mcp_server/_dev_tests/test_validation.py`
  - [ ] B.6.6 Fix any validation failures in generators
  - [ ] B.6.7 Record validation results
  - [ ] B.6.8 Commit: `feat: add automated validation script (Task B.6)`

- [ ] B.7 Simple E2E - Generate + run catalog browse test [GLUE]
  - [ ] B.7.1 Create branch `feature/B.7-simple-e2e`
  - [ ] B.7.2 Define simple test case: Guest browses Women category, verifies products displayed
  - [ ] B.7.3 Generate POM via Tool 3 → `framework/pages/test1/product_list_page.py`
  - [ ] B.7.4 Generate Task via Tool 4 → `framework/tasks/test1/catalog_tasks.py`
  - [ ] B.7.5 Generate Role via Tool 5 → `framework/roles/test1/guest_user.py`
  - [ ] B.7.6 Generate Test via Tool 6 → `tests/test1/test_browse_category.py`
  - [ ] B.7.7 Add `__init__.py` files to test1 directories
  - [ ] B.7.8 Run validation script on all generated code
  - [ ] B.7.9 Run test with visible browser: `pytest tests/test1/ -v --headless=False`
  - [ ] B.7.10 Generate HTML report: `pytest tests/test1/ -v --html=reports/test1_report.html --self-contained-html`
  - [ ] B.7.11 Verify test passes and report generated
  - [ ] B.7.12 Record results
  - [ ] B.7.13 Commit: `feat: simple E2E test - catalog browse (Task B.7)`

- [ ] B.8 Medium E2E - Generate + run auth + catalog test [GLUE]
  - [ ] B.8.1 Create branch `feature/B.8-medium-e2e`
  - [ ] B.8.2 Define medium test case: User logs in → browses category → verifies products → logs out
  - [ ] B.8.3 Generate POMs via Tool 3:
    - `framework/pages/test2/login_page.py`
    - `framework/pages/test2/product_list_page.py`
    - `framework/pages/test2/account_page.py`
  - [ ] B.8.4 Generate Tasks via Tool 4:
    - `framework/tasks/test2/auth_tasks.py`
    - `framework/tasks/test2/catalog_tasks.py`
  - [ ] B.8.5 Generate Role via Tool 5 → `framework/roles/test2/authenticated_user.py`
  - [ ] B.8.6 Generate Test via Tool 6 → `tests/test2/test_auth_catalog_workflow.py`
  - [ ] B.8.7 Add `__init__.py` files to test2 directories
  - [ ] B.8.8 Run validation script on all generated code
  - [ ] B.8.9 Run test with visible browser: `pytest tests/test2/ -v --headless=False`
  - [ ] B.8.10 Generate HTML report: `pytest tests/test2/ -v --html=reports/test2_report.html --self-contained-html`
  - [ ] B.8.11 Verify test passes and report generated
  - [ ] B.8.12 Record results
  - [ ] B.8.13 Commit: `feat: medium E2E test - auth + catalog workflow (Task B.8)`

- [ ] B.9 Cleanup - Deprecate code_generator.py, final docs [GLUE]
  - [ ] B.9.1 Create branch `feature/B.9-cleanup`
  - [ ] B.9.2 Verify all tools (3-6) use new generators (no imports from code_generator.py)
  - [ ] B.9.3 Run all generator tests: `python -m pytest mcp_server/_dev_tests/ -v`
  - [ ] B.9.4 Run all E2E tests: `pytest tests/test1/ tests/test2/ -v`
  - [ ] B.9.5 Delete `mcp_server/utils/code_generator.py`
  - [ ] B.9.6 Update `mcp_server/utils/generators/__init__.py` with final exports
  - [ ] B.9.7 Update SESSION.md with Phase B completion
  - [ ] B.9.8 Record final results
  - [ ] B.9.9 Commit: `refactor: deprecate code_generator.py, complete Phase B (Task B.9)`
  - [ ] B.9.10 Merge feature branch to main

---

## Done When Criteria

### Per Task
- All subtasks completed
- Tests pass
- Validation passes (for B.2-B.6)
- Manual review confirms pattern match
- Commands + results documented

### Phase B Complete
- All 4 generators created and tested
- All 4 tools updated to use new generators
- Automated validation passes on all generated code
- Simple E2E test runs with visible browser + HTML report
- Medium E2E test runs with visible browser + HTML report
- `code_generator.py` deleted
- All commits merged to main

---

## Commands Run

```bash
# To be filled during execution
```

## Results

- To be recorded during execution
