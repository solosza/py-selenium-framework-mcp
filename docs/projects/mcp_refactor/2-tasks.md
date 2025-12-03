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
- `framework/pages/e2e_simple/` - Simple E2E POMs (catalog)
- `framework/tasks/e2e_simple/` - Simple E2E Tasks
- `framework/roles/e2e_simple/` - Simple E2E Roles
- `tests/e2e_simple/` - Simple E2E test (catalog browse)
- `framework/pages/e2e_medium/` - Medium E2E POMs (auth + catalog)
- `framework/tasks/e2e_medium/` - Medium E2E Tasks
- `framework/roles/e2e_medium/` - Medium E2E Roles
- `tests/e2e_medium/` - Medium E2E test (auth + catalog)
- `reports/e2e_simple_report.html` - Simple E2E HTML report
- `reports/e2e_medium_report.html` - Medium E2E HTML report

### Notes
- Run E2E tests visible: `pytest tests/e2e_simple/ -v --headless=False`
- Generate HTML report: `--html=reports/e2e_simple_report.html --self-contained-html`
- AI enforcement rules are in CLAUDE.md → FRAMEWORK.md Section 8 (no code needed)

---

## Tasks

- [ ] B.1 Tool 1-2 Metadata Output [CORE]
  - [ ] B.1.1 Create branch `feature/B.1-tool-1-2-metadata`
  - [ ] B.1.2 Update Tool 1 to output `test_scenarios[]` in metadata format:
    - Each scenario: {name, given, when, then, workflow}
    - Add `metadata` key to JSON response
  - [ ] B.1.3 Update Tool 2 to output `discovered_elements[]` in metadata format:
    - Each element: {name, type, locator}
    - Ensure consistent with what Tool 3 expects
  - [ ] B.1.4 Test Tool 1 standalone: `python mcp_server/tools/tool_01_generate_tests_from_user_story.py`
  - [ ] B.1.5 Test Tool 2 standalone: `python mcp_server/tools/tool_02_discover_page_elements.py`
  - [ ] B.1.6 Verify metadata output format matches PRD Section 6.2
  - [ ] B.1.7 Record results
  - [ ] B.1.8 Commit: `feat: add metadata output to Tools 1-2 (Task B.1)`

- [ ] B.2 Tool 3 expected_states [CORE]
  - [ ] B.2.1 Create branch `feature/B.2-tool-3-expected-states`
  - [ ] B.2.2 Update `page_object_generator.py` to accept `expected_states` parameter
  - [ ] B.2.3 Generate state-check methods from expected_states:
    - `is_*` methods return bool
    - `has_*` methods return bool
    - `get_*` methods return str/int
  - [ ] B.2.4 Update Tool 3 to pass expected_states to generator
  - [ ] B.2.5 Ensure pom_metadata.state_methods includes generated state methods
  - [ ] B.2.6 Test Tool 3 with sample expected_states input
  - [ ] B.2.7 Verify generated POM has correct state-check methods
  - [ ] B.2.8 Record results
  - [ ] B.2.9 Commit: `feat: add expected_states support to Tool 3 (Task B.2)`

- [ ] B.3 Tool 4 Refactor [CORE]
  - [ ] B.3.1 Create branch `feature/B.3-tool-4-refactor`
  - [ ] B.3.2 Implement check-existing pattern in Tool 4:
    - Scan `framework/tasks/` for existing Task classes
    - Return `existing_found` status if task already handles intent
    - Include existing_class, existing_methods in response
  - [ ] B.3.3 Update `task_generator.py` to use POM metadata:
    - Read action_methods from pom_metadata
    - Generate Task methods that call actual POM methods
    - No hardcoded method names
  - [ ] B.3.4 Ensure task_metadata output includes:
    - class_name, import_path, composed_pages[], task_methods[]
  - [ ] B.3.5 Test Tool 4 with check_existing=True (should find CommonTasks)
  - [ ] B.3.6 Test Tool 4 with pom_metadata input
  - [ ] B.3.7 Verify generated Task calls actual POM methods from metadata
  - [ ] B.3.8 Record results
  - [ ] B.3.9 Commit: `feat: add check-existing and POM metadata to Tool 4 (Task B.3)`

- [ ] B.4 Tool 5 Refactor [CORE]
  - [ ] B.4.1 Create branch `feature/B.4-tool-5-refactor`
  - [ ] B.4.2 Implement check-existing pattern in Tool 5:
    - Scan `framework/roles/` for existing Role classes
    - Return `existing_found` status if role matches persona
    - Include existing_class, existing_methods in response
  - [ ] B.4.3 Update `role_generator.py` to use Task metadata:
    - Read task_methods from task_metadata
    - Generate Role methods that call actual Task methods
    - No hardcoded method names
  - [ ] B.4.4 Ensure role_metadata output includes:
    - class_name, import_path, composed_tasks[], workflow_methods[]
  - [ ] B.4.5 Test Tool 5 with check_existing=True (should find RegisteredUser if exists)
  - [ ] B.4.6 Test Tool 5 with task_metadata input
  - [ ] B.4.7 Verify generated Role calls actual Task methods from metadata
  - [ ] B.4.8 Record results
  - [ ] B.4.9 Commit: `feat: add check-existing and Task metadata to Tool 5 (Task B.4)`

- [ ] B.5 Tool 6 Refactor [CORE]
  - [ ] B.5.1 Create branch `feature/B.5-tool-6-refactor`
  - [ ] B.5.2 Update `test_generator.py` to accept Role + POM metadata:
    - Read workflow_methods from role_metadata
    - Read state_methods from pom_metadata
  - [ ] B.5.3 Generate test assertions using actual POM state methods:
    - `assert page.is_logged_in()` not `assert result == True`
    - Use method names from pom_metadata.state_methods
  - [ ] B.5.4 Ensure AAA pattern in generated tests:
    - Arrange: Create Role and POM instances
    - Act: ONE Role workflow method call
    - Assert: Via POM state-check methods
  - [ ] B.5.5 Test Tool 6 with role_metadata + pom_metadata input
  - [ ] B.5.6 Verify generated test uses actual method names from metadata
  - [ ] B.5.7 Verify no hardcoded method names in generated test
  - [ ] B.5.8 Record results
  - [ ] B.5.9 Commit: `feat: add Role + POM metadata to Tool 6 (Task B.5)`

- [ ] B.6 Simple E2E Test [GLUE]
  - [ ] B.6.1 Create branch `feature/B.6-simple-e2e`
  - [ ] B.6.2 Define test requirement:
    - "As a guest, I want to browse products in the Women category"
    - URL: http://automationpractice.pl/index.php
    - Expected: Products displayed in Women category
  - [ ] B.6.3 Execute Step 1-2 (AI Processing):
    - Extract role_name: GuestUser
    - Extract domain: catalog
    - Extract expected_states: [{name: "has_products", ...}]
    - Initialize metadata context
  - [ ] B.6.4 Execute Step 3 (Tool 1): Parse BDD, get test_scenarios
  - [ ] B.6.5 Execute Step 4 (Tool 2): Discover elements on catalog page
  - [ ] B.6.6 Execute Step 5 (Tool 3): Generate POM with expected_states
  - [ ] B.6.7 Execute Step 6 (Tool 4): Generate Task (or use existing)
  - [ ] B.6.8 Execute Step 7 (Tool 5): Generate Role (or use existing)
  - [ ] B.6.9 Execute Step 8 (Tool 6): Generate Test with metadata
  - [ ] B.6.10 Execute Step 9: Save files to `e2e_simple/` directories
  - [ ] B.6.11 Add `__init__.py` files to e2e_simple directories
  - [ ] B.6.12 Run test with visible browser: `pytest tests/e2e_simple/ -v --headless=False`
  - [ ] B.6.13 Generate HTML report: `--html=reports/e2e_simple_report.html --self-contained-html`
  - [ ] B.6.14 User validates: browser visible, test passes, report generated
  - [ ] B.6.15 Record results
  - [ ] B.6.16 Commit: `feat: simple E2E test - catalog browse (Task B.6)`

- [ ] B.7 Medium E2E Test [GLUE]
  - [ ] B.7.1 Create branch `feature/B.7-medium-e2e`
  - [ ] B.7.2 Define test requirement:
    - "As a registered user, I want to login and browse products"
    - URL: http://automationpractice.pl/index.php?controller=authentication
    - Expected: Login successful, products displayed
  - [ ] B.7.3 Execute Step 1-2 (AI Processing):
    - Extract role_name: RegisteredUser
    - Extract domain: auth (primary), catalog (secondary)
    - Extract expected_states: [{name: "is_logged_in"}, {name: "has_products"}]
    - Initialize metadata context
  - [ ] B.7.4 Execute Step 3 (Tool 1): Parse BDD, get test_scenarios
  - [ ] B.7.5 Execute Step 4 (Tool 2): Discover elements on login page
  - [ ] B.7.6 Execute Step 5 (Tool 3): Generate LoginPage POM with expected_states
  - [ ] B.7.7 Execute Step 4 again (Tool 2): Discover elements on catalog page
  - [ ] B.7.8 Execute Step 5 again (Tool 3): Generate ProductListPage POM
  - [ ] B.7.9 Execute Step 6 (Tool 4): Generate Tasks (check existing first)
  - [ ] B.7.10 Execute Step 7 (Tool 5): Generate Role (check existing first)
  - [ ] B.7.11 Execute Step 8 (Tool 6): Generate Test with metadata
  - [ ] B.7.12 Execute Step 9: Save files to `e2e_medium/` directories
  - [ ] B.7.13 Add `__init__.py` files to e2e_medium directories
  - [ ] B.7.14 Run test with visible browser: `pytest tests/e2e_medium/ -v --headless=False`
  - [ ] B.7.15 Generate HTML report: `--html=reports/e2e_medium_report.html --self-contained-html`
  - [ ] B.7.16 User validates: browser visible, login works, test passes, report generated
  - [ ] B.7.17 Record results
  - [ ] B.7.18 Commit: `feat: medium E2E test - auth + catalog (Task B.7)`

- [ ] B.8 Cleanup [GLUE]
  - [ ] B.8.1 Create branch `feature/B.8-cleanup`
  - [ ] B.8.2 Verify all tools (1-6) output correct metadata format
  - [ ] B.8.3 Verify no hardcoded method names remain in generators
  - [ ] B.8.4 Run both E2E tests: `pytest tests/e2e_simple/ tests/e2e_medium/ -v`
  - [ ] B.8.5 Clean up old test artifacts (devtest1/, devtest2/, test1/, test2/ if exist)
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
# To be filled during execution
```

## Results

- To be recorded during execution
