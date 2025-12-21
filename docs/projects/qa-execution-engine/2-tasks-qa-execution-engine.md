# Tasks: QA Execution Engine

**Generated:** 2025-12-20
**Source PRD:** 1-prd-qa-execution-engine.md
**Testing Reference:** `.claude/skills/testing/`

---

## Relevant Files

### New Files (to be created)

| File | Description |
|------|-------------|
| `mcp_server/utils/state_manager.py` | StateManager class for workflow state persistence |
| `mcp_server/state/workflow_state.json` | Workflow state file (gitignored) |
| `mcp_server/tools/gates/__init__.py` | Gate module initialization |
| `mcp_server/tools/gates/base_gate.py` | Base gate class with shared validation |
| `mcp_server/tools/gates/qg_preflight.py` | Step 1 quality gate |
| `mcp_server/tools/gates/qg_user_input.py` | Step 2 quality gate |
| `mcp_server/tools/gates/qg_ai_processing.py` | Step 3 quality gate |
| `mcp_server/tools/gates/qg_test_scenarios.py` | Step 4 quality gate |
| `mcp_server/tools/gates/qg_discovered_elements.py` | Step 5 quality gate |
| `mcp_server/tools/gates/qg_page_object.py` | Step 6 quality gate |
| `mcp_server/tools/gates/qg_task.py` | Step 7 quality gate |
| `mcp_server/tools/gates/qg_role.py` | Step 8 quality gate |
| `mcp_server/tools/gates/qg_test_runner.py` | Step 9 quality gate |
| `mcp_server/tools/gates/qg_save_run.py` | Step 10 quality gate |

### Test Files (to be created)

| File | Description |
|------|-------------|
| `mcp_server/_dev_tests/test_state_manager.py` | State manager unit tests |
| `mcp_server/_dev_tests/test_gates/test_base_gate.py` | Base gate unit tests |
| `mcp_server/_dev_tests/test_gates/test_qg_preflight.py` | Step 1 gate tests |
| `mcp_server/_dev_tests/test_gates/test_qg_user_input.py` | Step 2 gate tests |
| `mcp_server/_dev_tests/test_gates/test_qg_ai_processing.py` | Step 3 gate tests |
| `mcp_server/_dev_tests/test_gates/test_qg_test_scenarios.py` | Step 4 gate tests |
| `mcp_server/_dev_tests/test_gates/test_qg_discovered_elements.py` | Step 5 gate tests |
| `mcp_server/_dev_tests/test_gates/test_qg_page_object.py` | Step 6 gate tests |
| `mcp_server/_dev_tests/test_gates/test_qg_task.py` | Step 7 gate tests |
| `mcp_server/_dev_tests/test_gates/test_qg_role.py` | Step 8 gate tests |
| `mcp_server/_dev_tests/test_gates/test_qg_test_runner.py` | Step 9 gate tests |
| `mcp_server/_dev_tests/test_gates/test_qg_save_run.py` | Step 10 gate tests |
| `mcp_server/_dev_tests/test_integration/test_step_blocking.py` | Step blocking tests |
| `mcp_server/_dev_tests/test_integration/test_workflow_resume.py` | Resume tests |
| `mcp_server/_dev_tests/test_e2e/test_full_workflow.py` | E2E workflow tests |

### Existing Files (to be modified)

| File | Description |
|------|-------------|
| `mcp_server/server.py` | Register gate tools as MCP endpoints |
| `.claude/skills/qa-guidance-layer/SKILL.md` | Update to reference gates |
| `.gitignore` | Add state file exclusion |

---

## Test Commands

```bash
# Run all tests
pytest mcp_server/_dev_tests/ -v

# Run with coverage
pytest mcp_server/_dev_tests/ --cov=mcp_server --cov-report=term-missing

# Run specific component
pytest mcp_server/_dev_tests/test_state_manager.py -v
pytest mcp_server/_dev_tests/test_gates/test_qg_preflight.py -v
```

---

## Tasks

### Phase 1: Foundation

---

#### 1.0 Step Definition Validation [GLUE] ✅ COMPLETE

- [x] 1.1 Read all 10 step definition files (step-01.md through step-10.md)
- [x] 1.2 Verify each has sections A through G (A-H for tool steps 4-9)
- [x] 1.3 Verify DD coverage matches design doc (20/20 DDs)
- [x] 1.4 Verify state schema defined for each step
- [x] 1.5 Verify gate mode documented (POST-only, PRE+POST, PRE-only)
- [x] 1.6 Create validation checklist document
- [x] 1.7 Record results

**Done When:**
- All 10 step files validated ✅
- All sections present ✅
- DD coverage confirmed at 20/20 ✅

**Results:** See `validation-step-definitions.md`

---

#### 2.0 State Manager [CORE] ✅ COMPLETE

- [x] 2.1 Create branch `feature/2.0-state-manager`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| Happy | `test_save_creates_state_file` | [x] |
| Happy | `test_load_returns_state` | [x] |
| Happy | `test_get_step_returns_data` | [x] |
| Happy | `test_is_step_complete_returns_true` | [x] |
| Negative | `test_load_missing_file_returns_empty` | [x] |
| Negative | `test_get_step_not_found_returns_none` | [x] |
| Negative | `test_is_step_complete_returns_false` | [x] |
| Edge | `test_save_empty_data` | [x] |
| Edge | `test_get_step_zero` | [x] |
| Edge | `test_get_step_boundary_ten` | [x] |
| Error | `test_atomic_write_no_corruption` | [x] |
| Error | `test_invalid_json_handled` | [x] |
| Clear | `test_clear_removes_state` | [x] |
| Default | `test_default_state_file_path` | [x] |
| WriteErr | `test_save_to_readonly_location_raises` | [x] |
| WriteErr | `test_save_cleans_up_temp_file_on_rename_failure` | [x] |

- [x] 2.2 Write failing tests (TDD)
  - [x] 2.2.1 Happy path tests (4 tests)
  - [x] 2.2.2 Negative tests (3 tests)
  - [x] 2.2.3 Edge case tests (3 tests)
  - [x] 2.2.4 Error handling tests (2 tests)
  - [x] 2.2.5 Additional tests (4 tests - clear, default path, write errors)
- [x] 2.3 Implement StateManager class
  - [x] 2.3.1 Create `mcp_server/utils/state_manager.py`
  - [x] 2.3.2 Implement save(step: int, data: dict)
  - [x] 2.3.3 Implement load() -> dict
  - [x] 2.3.4 Implement get_step(step: int) -> dict | None
  - [x] 2.3.5 Implement is_step_complete(step: int) -> bool
  - [x] 2.3.6 Implement clear() for testing
- [x] 2.4 Create state directory and gitignore entry
- [x] 2.5 Run tests, verify all pass (16/16)
- [x] 2.6 Verify coverage = 100%
- [x] 2.7 Record results
- [x] 2.8 Commit: `feat: implement StateManager (Task 2.0)`

**Done When:**
- ~~12~~ 16 unit tests pass ✅
- Coverage ~~>= 95%~~ = 100% ✅
- Atomic writes verified ✅

**Results:**
- Tests: 16 passed, 0 warnings
- Coverage: 100%
- All tests follow testing skill conventions (AAA, markers, assertions)
- conftest.py created with marker registration

---

#### 3.0 Gate Infrastructure [CORE] ✅ COMPLETE

- [x] 3.1 Create branch `feature/3.0-gate-infrastructure`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| Happy | `test_pass_response_format` | [x] |
| Happy | `test_fail_response_format` | [x] |
| Happy | `test_detect_skeleton_finds_pass` | [x] |
| Happy | `test_detect_skeleton_finds_add_comment` | [x] |
| Happy | `test_validate_required_fields_all_present` | [x] |
| Negative | `test_detect_skeleton_clean_code_returns_empty` | [x] |
| Negative | `test_validate_required_fields_missing` | [x] |
| Edge | `test_detect_skeleton_empty_string` | [x] |
| Edge | `test_detect_skeleton_multiline` | [x] |
| Edge | `test_validate_fields_empty_list` | [x] |
| DD-25 | `test_skeleton_pattern_empty_body` | [x] |
| DD-27 | `test_locator_detection_empty_code` | [x] |
| DD-27 | `test_locator_detection_clean_code` | [x] |
| DD-27 | `test_locator_detection_by_import` | [x] |
| DD-27 | `test_locator_detection_by_css_selector` | [x] |
| DD-15 | `test_pom_assertion_empty_code` | [x] |
| DD-15 | `test_pom_assertion_no_assertions` | [x] |
| DD-15 | `test_pom_assertion_pattern_valid` | [x] |
| DD-15 | `test_pom_assertion_pattern_invalid` | [x] |
| TestGate | `test_validates_aaa_pattern` | [x] |
| TestGate | `test_validates_pytest_markers` | [x] |
| TestGate | `test_validates_assertion_messages` | [x] |
| TestGate | `test_validates_docstring_priority` | [x] |
| TestGate | `test_rejects_missing_aaa_comments` | [x] |
| TestGate | `test_rejects_missing_markers` | [x] |

- [x] 3.2 Write failing tests (TDD)
  - [x] 3.2.1 Happy path tests (5 tests)
  - [x] 3.2.2 Negative tests (2 tests)
  - [x] 3.2.3 Edge case tests (3 tests)
  - [x] 3.2.4 DD-25 skeleton pattern tests (1 test)
  - [x] 3.2.5 DD-27 locator detection tests (4 tests)
  - [x] 3.2.6 DD-15 assertion pattern tests (4 tests)
  - [x] 3.2.7 Test structure validation tests (6 tests)
- [x] 3.3 Create gates directory structure
- [x] 3.4 Implement BaseGate class
- [x] 3.5 Create shared validation utilities
- [x] 3.6 Implement TestStructureValidator (validation utilities - ready for pytest plugin)
  - [x] 3.6.1 Created TestStructureValidator class with validation methods
  - [x] 3.6.2 Validate AAA pattern (# Arrange, # Act, # Assert comments)
  - [x] 3.6.3 Validate pytest markers (@pytest.mark.unit, etc.)
  - [x] 3.6.4 Validate assertion messages (assert x, "message")
  - [x] 3.6.5 Validate docstring format (P0/P1/P2 priority)
  - [ ] 3.6.6 Integrate as pytest collection hook (future task)
- [x] 3.7 Run tests, verify all pass (25/25)
- [x] 3.8 Verify coverage >= 90% (91%)
- [x] 3.9 Record results
- [x] 3.10 Commit: `feat: implement gate infrastructure (Task 3.0)`

**Done When:**
- ~~23~~ 25 unit tests pass ✅
- Coverage >= 90% (91%) ✅
- DD validation utilities working ✅
- Test structure validation utilities ready ✅

**Results:**
- Tests: 25 passed
- Coverage: 91%
- BaseGate: pass/fail responses, skeleton detection (DD-25), locator detection (DD-27), POM assertion validation (DD-15)
- TestStructureValidator: AAA pattern, markers, assertion messages, docstring priority

---

### Phase 2: Configuration Gates (Steps 1-3)

---

#### 4.0 Preflight Gate - Step 1 [CORE] ✅ COMPLETE

- [x] 4.1 Create branch `feature/4.0-qg-preflight`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| Happy | `test_valid_credential_strategy_static` | [x] |
| Happy | `test_valid_credential_strategy_dynamic` | [x] |
| Happy | `test_valid_credential_strategy_self_contained` | [x] |
| Happy | `test_valid_credential_strategy_none` | [x] |
| Happy | `test_valid_test_data_location_shared` | [x] |
| Happy | `test_valid_test_data_location_workflow` | [x] |
| Happy | `test_valid_test_data_location_both` | [x] |
| Happy | `test_valid_test_data_location_none` | [x] |
| Happy | `test_both_fields_valid_passes` | [x] |
| Happy | `test_state_saved_on_pass` | [x] |
| Negative | `test_invalid_credential_strategy_fails` | [x] |
| Negative | `test_invalid_test_data_location_fails` | [x] |
| Negative | `test_missing_credential_strategy_fails` | [x] |
| Negative | `test_missing_test_data_location_fails` | [x] |
| Negative | `test_both_invalid_fails` | [x] |
| Negative | `test_no_state_saved_on_fail` | [x] |
| Edge | `test_empty_string_credential_strategy` | [x] |
| Edge | `test_null_value_handled` | [x] |
| Edge | `test_case_sensitivity` | [x] |
| Error | `test_fix_hint_provided_on_fail` | [x] |

- [x] 4.2 Write failing tests (TDD)
  - [x] 4.2.1 Happy path tests (10 tests)
  - [x] 4.2.2 Negative tests (6 tests)
  - [x] 4.2.3 Edge case tests (3 tests)
  - [x] 4.2.4 Error handling tests (1 test)
- [x] 4.3 Implement qg_preflight gate
  - [x] 4.3.1 Create `mcp_server/tools/gates/qg_preflight.py`
  - [x] 4.3.2 Validate credential_strategy (DD-24)
  - [x] 4.3.3 Validate test_data_location (DD-28)
  - [x] 4.3.4 Call state_manager.save() on pass
  - [x] 4.3.5 Return error with fix_hint on fail
- [ ] 4.4 Register as MCP tool in server.py (deferred to integration phase)
- [x] 4.5 Run tests, verify all pass (20/20)
- [x] 4.6 Verify coverage >= 90% (98%)
- [x] 4.7 Record results
- [x] 4.8 Commit: `feat: implement qg_preflight gate (Task 4.0)`

**Done When:**
- 20 unit tests pass ✅
- DD-24 and DD-28 enforced ✅
- State saved on pass ✅
- Registered as MCP tool (deferred)

**Results:**
- Tests: 20 passed
- Coverage: 98%
- DD-24 (credential_strategy): static, dynamic, self-contained, none
- DD-28 (test_data_location): shared, workflow, both, none

---

#### 5.0 User Input Gate - Step 2 [CORE] ✅ COMPLETE

- [x] 5.1 Create branch `feature/5.0-qg-user-input`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| Happy | `test_valid_persona_passes` | [x] |
| Happy | `test_valid_url_http_passes` | [x] |
| Happy | `test_valid_url_https_passes` | [x] |
| Happy | `test_role_name_extracted_registered_user` | [x] |
| Happy | `test_role_name_extracted_guest` | [x] |
| Happy | `test_domain_detected_auth` | [x] |
| Happy | `test_domain_detected_catalog` | [x] |
| Happy | `test_state_saved_on_pass` | [x] |
| Negative | `test_missing_persona_fails` | [x] |
| Negative | `test_persona_without_as_a_fails` | [x] |
| Negative | `test_invalid_url_format_fails` | [x] |
| Negative | `test_missing_url_fails` | [x] |
| Negative | `test_no_state_saved_on_fail` | [x] |
| Edge | `test_empty_persona` | [x] |
| Edge | `test_localhost_url` | [x] |
| Edge | `test_url_with_port` | [x] |
| Edge | `test_multiple_roles_in_persona` | [x] |
| Error | `test_fix_hint_for_missing_persona` | [x] |
| Error | `test_fix_hint_for_invalid_url` | [x] |
| Integration | `test_blocks_step_3_on_fail` | [x] |
| Extra | `test_invalid_domain_fails` | [x] |
| Extra | `test_empty_role_name_fails` | [x] |
| Extra | `test_empty_raw_requirement_fails` | [x] |
| Extra | `test_missing_all_fields_shows_all_hints` | [x] |

- [x] 5.2 Write failing tests (TDD)
  - [x] 5.2.1 Happy path tests (8 tests)
  - [x] 5.2.2 Negative tests (5 tests)
  - [x] 5.2.3 Edge case tests (4 tests)
  - [x] 5.2.4 Error handling tests (2 tests)
  - [x] 5.2.5 Integration tests (1 test)
  - [x] 5.2.6 Extra tests (4 tests - domain, role_name, raw_requirement)
- [x] 5.3 Implement qg_user_input gate
  - [x] 5.3.1 Create `mcp_server/tools/gates/qg_user_input.py`
  - [x] 5.3.2 Validate persona (DD-01)
  - [x] 5.3.3 Validate URL (DD-02)
  - [x] 5.3.4 Extract role_name
  - [x] 5.3.5 Detect domain
  - [x] 5.3.6 Call state_manager.save() on pass
- [ ] 5.4 Register as MCP tool in server.py (deferred to integration phase)
- [x] 5.5 Run tests, verify all pass (24/24)
- [x] 5.6 Verify coverage >= 90% (95%)
- [x] 5.7 Record results
- [x] 5.8 Commit: `feat: implement qg_user_input gate (Task 5.0)`

**Done When:**
- ~~20~~ 24 unit tests pass ✅
- DD-01 and DD-02 enforced ✅
- Role name and domain validated ✅
- Registered as MCP tool (deferred)

**Results:**
- Tests: 24 passed
- Coverage: 95%
- DD-01 (persona): non-empty string required
- DD-02 (URL): valid http/https format required
- Domain: auth, catalog, cart, checkout

---

#### 6.0 AI Processing Gate - Step 3 [CORE]

- [ ] 6.1 Create branch `feature/6.0-qg-ai-processing`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| Happy | `test_valid_bdd_scenarios_passes` | [ ] |
| Happy | `test_valid_expected_states_passes` | [ ] |
| Happy | `test_valid_intent_passes` | [ ] |
| Happy | `test_metadata_context_built` | [ ] |
| Happy | `test_state_saved_on_pass` | [ ] |
| Negative | `test_missing_bdd_scenarios_fails` | [ ] |
| Negative | `test_bdd_missing_given_fails` | [ ] |
| Negative | `test_bdd_missing_when_fails` | [ ] |
| Negative | `test_bdd_missing_then_fails` | [ ] |
| Negative | `test_empty_expected_states_fails` | [ ] |
| Negative | `test_missing_intent_fails` | [ ] |
| Negative | `test_no_state_saved_on_fail` | [ ] |
| Edge | `test_single_expected_state` | [ ] |
| Edge | `test_very_long_intent` | [ ] |
| Edge | `test_multiple_scenarios` | [ ] |
| Error | `test_fix_hint_for_missing_bdd` | [ ] |
| Error | `test_fix_hint_for_empty_states` | [ ] |
| Integration | `test_blocks_step_4_on_fail` | [ ] |

- [ ] 6.2 Write failing tests (TDD)
  - [ ] 6.2.1 Happy path tests (5 tests)
  - [ ] 6.2.2 Negative tests (7 tests)
  - [ ] 6.2.3 Edge case tests (3 tests)
  - [ ] 6.2.4 Error handling tests (2 tests)
  - [ ] 6.2.5 Integration tests (1 test)
- [ ] 6.3 Implement qg_ai_processing gate
  - [ ] 6.3.1 Create `mcp_server/tools/gates/qg_ai_processing.py`
  - [ ] 6.3.2 Validate bdd_scenarios (DD-03)
  - [ ] 6.3.3 Validate expected_states (DD-09)
  - [ ] 6.3.4 Validate intent
  - [ ] 6.3.5 Build metadata_context
  - [ ] 6.3.6 Call state_manager.save() on pass
- [ ] 6.4 Register as MCP tool in server.py
- [ ] 6.5 Run tests, verify all pass (18/18)
- [ ] 6.6 Verify coverage >= 90%
- [ ] 6.7 Record results
- [ ] 6.8 Commit: `feat: implement qg_ai_processing gate (Task 6.0)`

**Done When:**
- 18 unit tests pass
- DD-03 and DD-09 enforced
- Metadata context built
- Registered as MCP tool

---

### Phase 3: Operation Gates (Steps 4-9)

---

#### 7.0 Test Scenarios Gate - Step 4 [CORE]

- [ ] 7.1 Create branch `feature/7.0-qg-test-scenarios`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| PRE-Happy | `test_pre_step_3_complete_passes` | [ ] |
| PRE-Happy | `test_pre_metadata_context_present` | [ ] |
| PRE-Negative | `test_pre_step_3_incomplete_fails` | [ ] |
| PRE-Negative | `test_pre_metadata_context_missing_fails` | [ ] |
| POST-Happy | `test_post_valid_scenarios_passes` | [ ] |
| POST-Happy | `test_post_bdd_format_valid` | [ ] |
| POST-Negative | `test_post_skeleton_scenarios_fails` | [ ] |
| POST-Negative | `test_post_missing_then_fails` | [ ] |
| POST-Negative | `test_post_wrong_import_path_fails` | [ ] |
| Edge | `test_single_scenario` | [ ] |
| Edge | `test_multiple_scenarios` | [ ] |
| Error | `test_fix_hint_for_skeleton` | [ ] |
| DD-19 | `test_tool_import_from_tools` | [ ] |
| DD-23 | `test_bdd_format_given_when_then` | [ ] |
| Integration | `test_blocks_step_5_on_fail` | [ ] |

- [ ] 7.2 Write failing tests (TDD)
  - [ ] 7.2.1 PRE validation tests (4 tests)
  - [ ] 7.2.2 POST validation tests (5 tests)
  - [ ] 7.2.3 Edge case tests (2 tests)
  - [ ] 7.2.4 Error handling tests (1 test)
  - [ ] 7.2.5 DD enforcement tests (2 tests)
  - [ ] 7.2.6 Integration tests (1 test)
- [ ] 7.3 Implement qg_test_scenarios gate
  - [ ] 7.3.1 Create `mcp_server/tools/gates/qg_test_scenarios.py`
  - [ ] 7.3.2 PRE: Check is_step_complete(3)
  - [ ] 7.3.3 PRE: Validate metadata_context
  - [ ] 7.3.4 POST: Validate test_scenarios structure
  - [ ] 7.3.5 POST: Validate BDD format (DD-23)
  - [ ] 7.3.6 POST: Validate tool import (DD-19)
- [ ] 7.4 Register as MCP tool in server.py
- [ ] 7.5 Run tests, verify all pass (15/15)
- [ ] 7.6 Verify coverage >= 90%
- [ ] 7.7 Record results
- [ ] 7.8 Commit: `feat: implement qg_test_scenarios gate (Task 7.0)`

**Done When:**
- 15 unit tests pass
- PRE+POST validation working
- DD-19 and DD-23 enforced
- Registered as MCP tool

---

#### 8.0 Discovered Elements Gate - Step 5 [CORE]

- [ ] 8.1 Create branch `feature/8.0-qg-discovered-elements`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| PRE-Happy | `test_pre_step_4_complete_passes` | [ ] |
| PRE-Happy | `test_pre_credential_strategy_applied` | [ ] |
| PRE-Negative | `test_pre_step_4_incomplete_fails` | [ ] |
| POST-Happy | `test_post_elements_not_empty_passes` | [ ] |
| POST-Happy | `test_post_element_structure_valid` | [ ] |
| POST-Happy | `test_post_page_name_pascalcase` | [ ] |
| POST-Negative | `test_post_empty_elements_fails` | [ ] |
| POST-Negative | `test_post_missing_locator_fails` | [ ] |
| POST-Negative | `test_post_lowercase_page_name_fails` | [ ] |
| Edge | `test_single_element` | [ ] |
| Edge | `test_multiple_locator_types` | [ ] |
| Edge | `test_credential_strategy_none` | [ ] |
| Error | `test_fix_hint_for_empty_elements` | [ ] |
| DD-20 | `test_dynamic_element_handling` | [ ] |
| DD-21 | `test_ai_sdet_collaboration` | [ ] |
| DD-24 | `test_credential_strategy_from_step_1` | [ ] |
| Integration | `test_blocks_step_6_on_fail` | [ ] |

- [ ] 8.2 Write failing tests (TDD)
  - [ ] 8.2.1 PRE validation tests (3 tests)
  - [ ] 8.2.2 POST validation tests (6 tests)
  - [ ] 8.2.3 Edge case tests (3 tests)
  - [ ] 8.2.4 Error handling tests (1 test)
  - [ ] 8.2.5 DD enforcement tests (3 tests)
  - [ ] 8.2.6 Integration tests (1 test)
- [ ] 8.3 Implement qg_discovered_elements gate
  - [ ] 8.3.1 Create `mcp_server/tools/gates/qg_discovered_elements.py`
  - [ ] 8.3.2 PRE: Check is_step_complete(4)
  - [ ] 8.3.3 PRE: Apply credential_strategy from Step 1
  - [ ] 8.3.4 POST: Validate elements array
  - [ ] 8.3.5 POST: Validate element structure
  - [ ] 8.3.6 POST: Validate page_name PascalCase
- [ ] 8.4 Register as MCP tool in server.py
- [ ] 8.5 Run tests, verify all pass (17/17)
- [ ] 8.6 Verify coverage >= 90%
- [ ] 8.7 Record results
- [ ] 8.8 Commit: `feat: implement qg_discovered_elements gate (Task 8.0)`

**Done When:**
- 17 unit tests pass
- PRE+POST validation working
- DD-20, DD-21, DD-24 enforced
- Registered as MCP tool

---

#### 9.0 Page Object Gate - Step 6 [CORE]

- [ ] 9.1 Create branch `feature/9.0-qg-page-object`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| PRE-Happy | `test_pre_step_5_complete_passes` | [ ] |
| PRE-Happy | `test_pre_elements_present` | [ ] |
| PRE-Happy | `test_pre_expected_states_present` | [ ] |
| PRE-Negative | `test_pre_step_5_incomplete_fails` | [ ] |
| PRE-Negative | `test_pre_no_elements_fails` | [ ] |
| POST-Happy | `test_post_no_skeleton_code_passes` | [ ] |
| POST-Happy | `test_post_locators_present` | [ ] |
| POST-Happy | `test_post_atomic_methods_present` | [ ] |
| POST-Happy | `test_post_state_methods_match_expected` | [ ] |
| POST-Happy | `test_post_metadata_structure_valid` | [ ] |
| POST-Negative | `test_post_skeleton_pass_in_body_fails` | [ ] |
| POST-Negative | `test_post_skeleton_add_comment_fails` | [ ] |
| POST-Negative | `test_post_missing_locator_fails` | [ ] |
| POST-Negative | `test_post_missing_state_method_fails` | [ ] |
| POST-Negative | `test_post_missing_action_methods_fails` | [ ] |
| Edge | `test_single_locator` | [ ] |
| Edge | `test_single_state_method` | [ ] |
| Error | `test_fix_hint_for_skeleton` | [ ] |
| DD-09 | `test_state_methods_from_expected_states` | [ ] |
| DD-25 | `test_skeleton_detection_comprehensive` | [ ] |
| DD-26 | `test_metadata_contract_valid` | [ ] |
| Integration | `test_blocks_step_7_on_fail` | [ ] |
| Integration | `test_skeleton_triggers_retry` | [ ] |

- [ ] 9.2 Write failing tests (TDD)
  - [ ] 9.2.1 PRE validation tests (5 tests)
  - [ ] 9.2.2 POST validation tests (10 tests)
  - [ ] 9.2.3 Edge case tests (2 tests)
  - [ ] 9.2.4 Error handling tests (1 test)
  - [ ] 9.2.5 DD enforcement tests (3 tests)
  - [ ] 9.2.6 Integration tests (2 tests)
- [ ] 9.3 Implement qg_page_object gate
  - [ ] 9.3.1 Create `mcp_server/tools/gates/qg_page_object.py`
  - [ ] 9.3.2 PRE: Check is_step_complete(5)
  - [ ] 9.3.3 PRE: Validate elements present
  - [ ] 9.3.4 POST: Run detect_skeleton_code (DD-25)
  - [ ] 9.3.5 POST: Validate locators and methods
  - [ ] 9.3.6 POST: Validate state methods match expected_states (DD-09)
  - [ ] 9.3.7 POST: Validate metadata structure (DD-26)
- [ ] 9.4 Register as MCP tool in server.py
- [ ] 9.5 Run tests, verify all pass (23/23)
- [ ] 9.6 Verify coverage >= 90%
- [ ] 9.7 Record results
- [ ] 9.8 Commit: `feat: implement qg_page_object gate (Task 9.0)`

**Done When:**
- 23 unit tests pass
- PRE+POST validation working
- DD-09, DD-25, DD-26 enforced
- Skeleton code blocked
- Registered as MCP tool

---

#### 10.0 Task Gate - Step 7 [CORE]

- [ ] 10.1 Create branch `feature/10.0-qg-task`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| PRE-Happy | `test_pre_step_6_complete_passes` | [ ] |
| PRE-Happy | `test_pre_pom_metadata_present` | [ ] |
| PRE-Negative | `test_pre_step_6_incomplete_fails` | [ ] |
| PRE-Negative | `test_pre_no_pom_metadata_fails` | [ ] |
| POST-Happy | `test_post_no_skeleton_code_passes` | [ ] |
| POST-Happy | `test_post_no_locators_passes` | [ ] |
| POST-Happy | `test_post_metadata_structure_valid` | [ ] |
| POST-Negative | `test_post_skeleton_empty_body_fails` | [ ] |
| POST-Negative | `test_post_skeleton_placeholder_fails` | [ ] |
| POST-Negative | `test_post_by_import_fails` | [ ] |
| POST-Negative | `test_post_by_css_selector_fails` | [ ] |
| POST-Negative | `test_post_missing_task_methods_fails` | [ ] |
| Edge | `test_check_existing_task_found` | [ ] |
| Edge | `test_single_task_method` | [ ] |
| Error | `test_fix_hint_for_locators` | [ ] |
| DD-12 | `test_check_existing_before_generate` | [ ] |
| DD-25 | `test_skeleton_detection_in_task` | [ ] |
| DD-26 | `test_metadata_contract_valid` | [ ] |
| DD-27 | `test_no_locators_in_task` | [ ] |
| Integration | `test_blocks_step_8_on_fail` | [ ] |

- [ ] 10.2 Write failing tests (TDD)
  - [ ] 10.2.1 PRE validation tests (4 tests)
  - [ ] 10.2.2 POST validation tests (8 tests)
  - [ ] 10.2.3 Edge case tests (2 tests)
  - [ ] 10.2.4 Error handling tests (1 test)
  - [ ] 10.2.5 DD enforcement tests (4 tests)
  - [ ] 10.2.6 Integration tests (1 test)
- [ ] 10.3 Implement qg_task gate
  - [ ] 10.3.1 Create `mcp_server/tools/gates/qg_task.py`
  - [ ] 10.3.2 PRE: Check is_step_complete(6)
  - [ ] 10.3.3 PRE: Validate pom_metadata present
  - [ ] 10.3.4 POST: Run detect_skeleton_code (DD-25)
  - [ ] 10.3.5 POST: Check for By. imports (DD-27)
  - [ ] 10.3.6 POST: Check existing (DD-12)
  - [ ] 10.3.7 POST: Validate metadata structure (DD-26)
- [ ] 10.4 Register as MCP tool in server.py
- [ ] 10.5 Run tests, verify all pass (20/20)
- [ ] 10.6 Verify coverage >= 90%
- [ ] 10.7 Record results
- [ ] 10.8 Commit: `feat: implement qg_task gate (Task 10.0)`

**Done When:**
- 20 unit tests pass
- PRE+POST validation working
- DD-12, DD-25, DD-26, DD-27 enforced
- Locators in Task blocked
- Registered as MCP tool

---

#### 11.0 Role Gate - Step 8 [CORE]

- [ ] 11.1 Create branch `feature/11.0-qg-role`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| PRE-Happy | `test_pre_step_7_complete_passes` | [ ] |
| PRE-Happy | `test_pre_task_metadata_present` | [ ] |
| PRE-Negative | `test_pre_step_7_incomplete_fails` | [ ] |
| PRE-Negative | `test_pre_no_task_metadata_fails` | [ ] |
| POST-Happy | `test_post_no_skeleton_code_passes` | [ ] |
| POST-Happy | `test_post_metadata_structure_valid` | [ ] |
| POST-Happy | `test_post_workflow_methods_present` | [ ] |
| POST-Negative | `test_post_skeleton_pass_in_body_fails` | [ ] |
| POST-Negative | `test_post_missing_workflow_methods_fails` | [ ] |
| Edge | `test_check_existing_role_found` | [ ] |
| Edge | `test_single_workflow_method` | [ ] |
| Error | `test_fix_hint_for_skeleton` | [ ] |
| DD-12 | `test_check_existing_before_generate` | [ ] |
| DD-25 | `test_skeleton_detection_in_role` | [ ] |
| DD-26 | `test_metadata_contract_valid` | [ ] |
| Integration | `test_blocks_step_9_on_fail` | [ ] |

- [ ] 11.2 Write failing tests (TDD)
  - [ ] 11.2.1 PRE validation tests (4 tests)
  - [ ] 11.2.2 POST validation tests (5 tests)
  - [ ] 11.2.3 Edge case tests (2 tests)
  - [ ] 11.2.4 Error handling tests (1 test)
  - [ ] 11.2.5 DD enforcement tests (3 tests)
  - [ ] 11.2.6 Integration tests (1 test)
- [ ] 11.3 Implement qg_role gate
  - [ ] 11.3.1 Create `mcp_server/tools/gates/qg_role.py`
  - [ ] 11.3.2 PRE: Check is_step_complete(7)
  - [ ] 11.3.3 PRE: Validate task_metadata present
  - [ ] 11.3.4 POST: Run detect_skeleton_code (DD-25)
  - [ ] 11.3.5 POST: Check existing (DD-12)
  - [ ] 11.3.6 POST: Validate metadata structure (DD-26)
- [ ] 11.4 Register as MCP tool in server.py
- [ ] 11.5 Run tests, verify all pass (16/16)
- [ ] 11.6 Verify coverage >= 90%
- [ ] 11.7 Record results
- [ ] 11.8 Commit: `feat: implement qg_role gate (Task 11.0)`

**Done When:**
- 16 unit tests pass
- PRE+POST validation working
- DD-12, DD-25, DD-26 enforced
- Registered as MCP tool

---

#### 12.0 Test Runner Gate - Step 9 [CORE]

- [ ] 12.1 Create branch `feature/12.0-qg-test-runner`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| PRE-Happy | `test_pre_step_8_complete_passes` | [ ] |
| PRE-Happy | `test_pre_role_metadata_present` | [ ] |
| PRE-Happy | `test_pre_pom_metadata_present` | [ ] |
| PRE-Negative | `test_pre_step_8_incomplete_fails` | [ ] |
| PRE-Negative | `test_pre_no_role_metadata_fails` | [ ] |
| PRE-Negative | `test_pre_no_pom_metadata_fails` | [ ] |
| POST-Happy | `test_post_no_skeleton_code_passes` | [ ] |
| POST-Happy | `test_post_pom_state_assertions_valid` | [ ] |
| POST-Happy | `test_post_import_paths_valid` | [ ] |
| POST-Happy | `test_post_parameter_values_injected` | [ ] |
| POST-Negative | `test_post_skeleton_pass_in_test_fails` | [ ] |
| POST-Negative | `test_post_assert_result_true_fails` | [ ] |
| POST-Negative | `test_post_wrong_import_fails` | [ ] |
| POST-Negative | `test_post_placeholder_values_fails` | [ ] |
| Edge | `test_multiple_assertions` | [ ] |
| Edge | `test_complex_import_paths` | [ ] |
| Error | `test_fix_hint_for_bad_assertion` | [ ] |
| DD-15 | `test_assertions_use_pom_state_methods` | [ ] |
| DD-16 | `test_file_paths_override` | [ ] |
| DD-17 | `test_parameter_values_from_requirement` | [ ] |
| DD-18 | `test_import_paths_validated` | [ ] |
| DD-25 | `test_skeleton_detection_in_test` | [ ] |
| DD-26 | `test_metadata_contract_valid` | [ ] |
| Integration | `test_blocks_step_10_on_fail` | [ ] |

- [ ] 12.2 Write failing tests (TDD)
  - [ ] 12.2.1 PRE validation tests (6 tests)
  - [ ] 12.2.2 POST validation tests (8 tests)
  - [ ] 12.2.3 Edge case tests (2 tests)
  - [ ] 12.2.4 Error handling tests (1 test)
  - [ ] 12.2.5 DD enforcement tests (6 tests)
  - [ ] 12.2.6 Integration tests (1 test)
- [ ] 12.3 Implement qg_test_runner gate
  - [ ] 12.3.1 Create `mcp_server/tools/gates/qg_test_runner.py`
  - [ ] 12.3.2 PRE: Check is_step_complete(8)
  - [ ] 12.3.3 PRE: Validate role_metadata and pom_metadata present
  - [ ] 12.3.4 POST: Run detect_skeleton_code (DD-25)
  - [ ] 12.3.5 POST: Validate assertions use state methods (DD-15)
  - [ ] 12.3.6 POST: Validate import paths (DD-18)
  - [ ] 12.3.7 POST: Validate parameter values (DD-17)
  - [ ] 12.3.8 POST: Validate file paths (DD-16)
- [ ] 12.4 Register as MCP tool in server.py
- [ ] 12.5 Run tests, verify all pass (24/24)
- [ ] 12.6 Verify coverage >= 90%
- [ ] 12.7 Record results
- [ ] 12.8 Commit: `feat: implement qg_test_runner gate (Task 12.0)`

**Done When:**
- 24 unit tests pass
- PRE+POST validation working
- DD-15, DD-16, DD-17, DD-18, DD-25, DD-26 enforced
- POM state assertions validated
- Registered as MCP tool

---

### Phase 4: Final Gate

---

#### 13.0 Save Run Gate - Step 10 [CORE]

- [ ] 13.1 Create branch `feature/13.0-qg-save-run`

**Unit Tests (TDD) - Test Matrix:**

| Category | Test | Status |
|----------|------|--------|
| PRE-Happy | `test_pre_step_9_complete_passes` | [ ] |
| PRE-Happy | `test_pre_all_code_present` | [ ] |
| PRE-Happy | `test_pre_pom_code_present` | [ ] |
| PRE-Happy | `test_pre_task_code_present` | [ ] |
| PRE-Happy | `test_pre_role_code_present` | [ ] |
| PRE-Happy | `test_pre_test_code_present` | [ ] |
| PRE-Negative | `test_pre_step_9_incomplete_fails` | [ ] |
| PRE-Negative | `test_pre_missing_pom_fails` | [ ] |
| PRE-Negative | `test_pre_missing_task_fails` | [ ] |
| PRE-Negative | `test_pre_missing_role_fails` | [ ] |
| PRE-Negative | `test_pre_missing_test_fails` | [ ] |
| PRE-Negative | `test_pre_skeleton_in_pom_fails` | [ ] |
| PRE-Negative | `test_pre_skeleton_in_task_fails` | [ ] |
| PRE-Negative | `test_pre_skeleton_in_role_fails` | [ ] |
| PRE-Negative | `test_pre_skeleton_in_test_fails` | [ ] |
| Edge | `test_minimal_code_set` | [ ] |
| Error | `test_fix_hint_for_missing_code` | [ ] |
| Error | `test_fix_hint_for_skeleton` | [ ] |
| DD-22 | `test_stop_and_discuss_documented` | [ ] |
| DD-25 | `test_final_skeleton_sweep_all_layers` | [ ] |
| Integration | `test_final_sweep_catches_skeleton` | [ ] |

- [ ] 13.2 Write failing tests (TDD)
  - [ ] 13.2.1 PRE validation happy tests (6 tests)
  - [ ] 13.2.2 PRE validation negative tests (9 tests)
  - [ ] 13.2.3 Edge case tests (1 test)
  - [ ] 13.2.4 Error handling tests (2 tests)
  - [ ] 13.2.5 DD enforcement tests (2 tests)
  - [ ] 13.2.6 Integration tests (1 test)
- [ ] 13.3 Implement qg_save_run gate
  - [ ] 13.3.1 Create `mcp_server/tools/gates/qg_save_run.py`
  - [ ] 13.3.2 PRE: Check is_step_complete(9)
  - [ ] 13.3.3 PRE: Validate all code present (POM, Task, Role, Test)
  - [ ] 13.3.4 PRE: Run detect_skeleton_code on ALL code (DD-25)
  - [ ] 13.3.5 Return pass/fail (PRE-only mode)
- [ ] 13.4 Register as MCP tool in server.py
- [ ] 13.5 Run tests, verify all pass (21/21)
- [ ] 13.6 Verify coverage >= 90%
- [ ] 13.7 Record results
- [ ] 13.8 Commit: `feat: implement qg_save_run gate (Task 13.0)`

**Done When:**
- 21 unit tests pass
- PRE-only validation working
- Final skeleton code sweep
- DD-22, DD-25 enforced
- Registered as MCP tool

---

### Phase 5: Integration

---

#### 14.0 Skill Update [GLUE]

- [ ] 14.1 Create branch `feature/14.0-skill-update`
- [ ] 14.2 Update `.claude/skills/qa-guidance-layer/SKILL.md`
  - [ ] 14.2.1 Add gate tool references for each step
  - [ ] 14.2.2 Update workflow to include gate calls
  - [ ] 14.2.3 Add gate return format documentation
- [ ] 14.3 Update step references if needed
  - [ ] 14.3.1 Ensure each step references its gate tool
  - [ ] 14.3.2 Verify gate mode documented correctly
- [ ] 14.4 Manual test: Read skill, verify gates are documented
- [ ] 14.5 Record results
- [ ] 14.6 Commit: `docs: update qa-guidance-layer skill with gates (Task 14.0)`

**Done When:**
- SKILL.md references all qg_* gates
- Each step file references its gate
- Gate modes documented

---

#### 15.0 Integration Testing [GLUE]

- [ ] 15.1 Create branch `feature/15.0-integration-testing`

**Integration Tests:**

| Test | Purpose | Priority |
|------|---------|----------|
| `test_step_1_blocks_step_2` | Step 1 gate must pass before Step 2 | P0 |
| `test_step_n_blocks_step_n_plus_1` | Sequential enforcement | P0 |
| `test_skeleton_at_step_6_blocks_step_7` | Skeleton code blocked | P0 |
| `test_state_persists_across_gates` | State manager integration | P0 |
| `test_workflow_resume_after_interrupt` | Resume capability | P0 |
| `test_retry_policy_3_attempts` | 3 retries then user decides | P1 |

**E2E Tests:**

| Test | Purpose | Priority |
|------|---------|----------|
| `test_e2e_auth_workflow_complete` | Full auth workflow | P0 |
| `test_e2e_skeleton_rejection` | Intentionally bad output blocked | P0 |

- [ ] 15.2 Write integration tests
  - [ ] 15.2.1 Step blocking tests (6 tests)
  - [ ] 15.2.2 State persistence tests (2 tests)
  - [ ] 15.2.3 Resume tests (2 tests)
- [ ] 15.3 Write E2E tests
  - [ ] 15.3.1 Full workflow test
  - [ ] 15.3.2 Skeleton rejection test
- [ ] 15.4 Run all tests
- [ ] 15.5 Manual E2E: Run actual workflow with live MCP tools
- [ ] 15.6 Record results
- [ ] 15.7 Commit: `test: add integration tests for QA Execution Engine (Task 15.0)`

**Done When:**
- All acceptance tests from PRD pass (AT-01 through AT-06)
- Full workflow completes without skeleton code
- State persists and resumes correctly
- Manual E2E validation complete

---

## Summary

| Task | Component | Unit Tests | Coverage Target |
|------|-----------|------------|-----------------|
| 2.0 | State Manager | 12 | 95% |
| 3.0 | Gate Infrastructure | 17 | 90% |
| 4.0 | qg_preflight | 20 | 90% |
| 5.0 | qg_user_input | 20 | 90% |
| 6.0 | qg_ai_processing | 18 | 90% |
| 7.0 | qg_test_scenarios | 15 | 90% |
| 8.0 | qg_discovered_elements | 17 | 90% |
| 9.0 | qg_page_object | 23 | 90% |
| 10.0 | qg_task | 20 | 90% |
| 11.0 | qg_role | 16 | 90% |
| 12.0 | qg_test_runner | 24 | 90% |
| 13.0 | qg_save_run | 21 | 90% |
| **Total** | | **223 unit tests** | |

---

## Acceptance Tests Coverage

| AT | Description | Covered By |
|----|-------------|------------|
| AT-01 | Preflight gate blocks invalid input | Task 4.0 |
| AT-02 | Skeleton code blocked at POM | Task 9.0 |
| AT-03 | State persists after gate pass | Task 2.0, 15.0 |
| AT-04 | Workflow resume | Task 15.0 |
| AT-05 | DD-15 enforced | Task 12.0 |
| AT-06 | Data contract validated | Tasks 7.0-12.0 |

---

*Task list complete. Ready for execution.*
