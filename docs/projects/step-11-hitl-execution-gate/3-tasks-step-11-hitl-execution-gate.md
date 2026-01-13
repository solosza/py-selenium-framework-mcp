# Task List: Step 11 - HITL Execution Gate

**Project:** step-11-hitl-execution-gate
**Phase:** Divide (4D Framework - Phase 3)
**Date:** 2026-01-13
**PRD Reference:** `2-prd-step-11-hitl-execution-gate.md`
**Status:** Parent tasks generated, awaiting sub-task breakdown

---

## Relevant Files

### Implementation Files

**Operation Tool:**
- `mcp_server/tools/operations/run_test.py` - Test execution operation (pytest subprocess, output capture)
- `mcp_server/tools/operations/__init__.py` - Export run_test function

**Quality Gates:**
- `mcp_server/tools/gates/qg_execution.py` - Step 11 execution validation gate (HITL triage workflow)
- `mcp_server/tools/gates/qg_workflow_complete.py` - Meta-gate for 11-step workflow integrity
- `mcp_server/tools/gates/__init__.py` - Export new gates (QGExecution, QGWorkflowComplete)

**State Management:**
- `mcp_server/utils/state_manager.py` - VALID_STEPS extension (line 26: range(1, 11) → range(1, 12))

**MCP Server:**
- `mcp_server/server.py` - Register 3 new tools (run_test, qg_execution, qg_workflow_complete)

**Documentation:**
- `.claude/skills/qa-management-layer/references/step-11.md` - Step 11 protocol reference (NEW)
- `.claude/skills/qa-management-layer/SKILL.md` - Add Step 11 to workflow overview
- `FRAMEWORK.md` - Update Section 9 workflow diagram (11-step → 11-step)

### Test Files

**Unit Tests:**
- `mcp_server/_dev_tests/test_operations/test_run_test.py` - Test run_test operation
- `mcp_server/_dev_tests/test_gates/test_qg_execution.py` - Test qg_execution gate
- `mcp_server/_dev_tests/test_gates/test_qg_workflow_complete.py` - Test qg_workflow_complete gate
- `mcp_server/_dev_tests/test_utils/test_state_manager_step11.py` - Test StateManager step 11 support

**Integration Tests:**
- `mcp_server/_dev_tests/test_gates/test_step11_integration.py` - Step 11 tool chain integration

**E2E Tests:**
- `mcp_server/_dev_tests/test_step11_e2e.py` - Full 11-step workflow scenarios

**Test Fixtures:**
- `mcp_server/_dev_tests/fixtures/step11_fixtures.json` - Test data for Step 11 tests

### Notes

- All tests use pytest framework
- Mock subprocess calls for unit tests (don't run actual tests)
- Integration tests use real StateManager, mock subprocess
- E2E tests run actual pytest executions
- Test fixtures provide sample diagnostic data structures

---

## Tasks

### Phase 1: Core Infrastructure & Breaking Changes

- [ ] **58.0 StateManager Extension** [CORE]
  - [ ] 58.1 Create branch `feature/58.0-statemanager-step11`
  - [ ] 58.2 Update VALID_STEPS constant in `state_manager.py:26` (range(1, 11) → range(1, 12))
  - [ ] 58.3 Create unit test file `test_state_manager_step11.py`
  - [ ] 58.4 Write test: step 11 save succeeds
  - [ ] 58.5 Write test: step 11 get_step returns data
  - [ ] 58.6 Write test: is_step_complete(11) works
  - [ ] 58.7 Write test: backward compatibility (old 11-step state files readable)
  - [ ] 58.8 Run existing StateManager tests (verify no regressions)
  - [ ] 58.9 Run checks (formatter, linter, tests)
  - [ ] 58.10 **Audit: Verify testing skill conventions followed**
  - [ ] 58.11 Record results (commands + output)
  - [ ] 58.12 Commit: `feat: Extend StateManager to support Step 11 (Task 58.0)`

**Done When:**
- VALID_STEPS includes step 11
- Unit tests pass (step 11 save/get/complete)
- All existing StateManager tests pass (backward compatibility confirmed)
- Old 11-step state files remain readable

**Relevant Files:**
- `mcp_server/utils/state_manager.py` (line 26)
- `mcp_server/_dev_tests/test_utils/test_state_manager_step11.py` (new)

---

### Phase 2: Operation Tool Implementation

- [ ] **59.0 Test Execution Operation (run_test)** [CORE]
  - [ ] 59.1 Create branch `feature/59.0-run-test-operation`
  - [ ] 59.2 Create directory `mcp_server/tools/operations/` (if not exists)
  - [ ] 59.3 Create file `mcp_server/tools/operations/run_test.py`
  - [ ] 59.4 Implement pytest subprocess execution with flags (-v, --html, --self-contained-html, --env)
  - [ ] 59.5 Implement output capture (stdout + stderr via subprocess.run)
  - [ ] 59.6 Implement result structure (status, exit_code, output, duration, report_path)
  - [ ] 59.7 Implement failure data extraction (failed_assertion, stack_trace from pytest output)
  - [ ] 59.8 Handle crashes gracefully (non-zero exit codes, subprocess errors)
  - [ ] 59.9 Validate test_path parameter (within tests/ directory, prevent traversal)
  - [ ] 59.10 Create `mcp_server/tools/operations/__init__.py` (export execute_test function)
  - [ ] 59.11 Create unit test file `test_operations/test_run_test.py`
  - [ ] 59.12 Write test: successful test execution (exit code 0)
  - [ ] 59.13 Write test: failed test execution (exit code 1, assertion captured)
  - [ ] 59.14 Write test: pytest crash handling (non-zero exit, stderr captured)
  - [ ] 59.15 Write test: test path validation (reject paths outside tests/)
  - [ ] 59.16 Mock subprocess calls (don't run actual tests in unit tests)
  - [ ] 59.17 Run checks (formatter, linter, tests)
  - [ ] 59.18 **Audit: Verify testing skill conventions followed**
  - [ ] 59.19 Record results
  - [ ] 59.20 Commit: `feat: Implement run_test operation tool (Task 59.0)`

**Done When:**
- run_test executes pytest with correct flags
- Output captured (stdout/stderr)
- Returns structured results with all required fields
- Crashes handled gracefully
- Unit tests pass (≥90% coverage)

**Relevant Files:**
- `mcp_server/tools/operations/run_test.py` (new)
- `mcp_server/tools/operations/__init__.py` (new)
- `mcp_server/_dev_tests/test_operations/test_run_test.py` (new)

---

### Phase 3: Quality Gate Implementation

- [ ] **60.0 Execution Validation Gate (qg_execution)** [CORE]
  - [ ] 60.1 Create branch `feature/60.0-qg-execution-gate`
  - [ ] 60.2 Create file `mcp_server/tools/gates/qg_execution.py`
  - [ ] 60.3 Inherit from BaseGate, implement validate() method
  - [ ] 60.4 Implement test passed validation (status == "passed" → pass_response)
  - [ ] 60.5 Implement test failed handling (status == "failed" → capture diagnostic data)
  - [ ] 60.6 Implement diagnostic data capture - Test Execution (pytest output, exit code, duration)
  - [ ] 60.7 Implement diagnostic data capture - Page State (Playwright snapshot on failure)
  - [ ] 60.8 Implement diagnostic data capture - Browser Context (URL, cookies, storage)
  - [ ] 60.9 Implement diagnostic data capture - Expected vs Actual (assertion parsing)
  - [ ] 60.10 Implement diagnostic data capture - Test Context (file, function, line, fixtures)
  - [ ] 60.11 Implement diagnostic data capture - Test Data (credentials redacted, parameters)
  - [ ] 60.12 Implement diagnostic data capture - Execution Flow (stack trace, navigation)
  - [ ] 60.13 Implement AI analysis (suggestive - analyze data, suggest cause with confidence 0-100%)
  - [ ] 60.14 Implement triage presentation format (error, analysis, evidence, 3 options)
  - [ ] 60.15 Implement triage option 1: Application defect (log to DEFECT_LOG.md, stop workflow)
  - [ ] 60.16 Implement triage option 2: Test issue (proceed to fix workflow)
  - [ ] 60.17 Implement triage option 3: Investigate (show full diagnostic data)
  - [ ] 60.18 Implement error signature tracking (hash error message + location)
  - [ ] 60.19 Implement same-error retry limit (2 attempts → ask human)
  - [ ] 60.20 Implement total attempt limit (5 attempts → confirm with human)
  - [ ] 60.21 Implement retry history tracking (attempt number, error, result)
  - [ ] 60.22 Implement state persistence (save Step 11 data with triage history)
  - [ ] 60.23 Implement audit trail (hybrid - summary in main, detail in tests/_audit/step11/)
  - [ ] 60.24 Create unit test file `test_gates/test_qg_execution.py`
  - [ ] 60.25 Write test: test passed → PASS response
  - [ ] 60.26 Write test: test failed → FAIL response with diagnostic data
  - [ ] 60.27 Write test: diagnostic data structure validation (all 7 types present)
  - [ ] 60.28 Write test: triage option 1 (app defect) - logs defect, stops workflow
  - [ ] 60.29 Write test: triage option 2 (test issue) - returns fix workflow data
  - [ ] 60.30 Write test: triage option 3 (investigate) - returns full diagnostic data
  - [ ] 60.31 Write test: same-error limit (2 attempts → escalate)
  - [ ] 60.32 Write test: total attempt limit (5 attempts → confirm)
  - [ ] 60.33 Write test: error signature tracking (same vs different errors)
  - [ ] 60.34 Write test: state persistence (Step 11 data saved correctly)
  - [ ] 60.35 Mock Playwright snapshot calls
  - [ ] 60.36 Create test fixtures (sample diagnostic data in `fixtures/step11_fixtures.json`)
  - [ ] 60.37 Run checks (formatter, linter, tests)
  - [ ] 60.38 **Audit: Verify testing skill conventions followed**
  - [ ] 60.39 Record results
  - [ ] 60.40 Commit: `feat: Implement qg_execution gate with HITL triage (Task 60.0)`

**Done When:**
- Gate validates test passed/failed correctly
- All 7 diagnostic data types captured
- HITL triage workflow works (3 options)
- Retry policy enforced (2 same-error, 5 total)
- State persisted with triage history
- Unit tests pass (≥90% coverage, all scenarios covered)

**Relevant Files:**
- `mcp_server/tools/gates/qg_execution.py` (new, ~500+ lines)
- `mcp_server/_dev_tests/test_gates/test_qg_execution.py` (new, ~300+ lines)
- `mcp_server/_dev_tests/fixtures/step11_fixtures.json` (new)
- `docs/DEFECT_LOG.md` (modified - defect logging integration)

---

- [ ] **61.0 Meta-Gate (qg_workflow_complete)** [CORE]
  - [ ] 61.1 Create branch `feature/61.0-qg-workflow-complete`
  - [ ] 61.2 Create file `mcp_server/tools/gates/qg_workflow_complete.py`
  - [ ] 61.3 Inherit from BaseGate, implement validate() method
  - [ ] 61.4 Implement consistency check 1: Test path (Step 9 test == Step 11 test)
  - [ ] 61.5 Implement consistency check 2: File existence (all generated files on disk)
  - [ ] 61.6 Implement consistency check 3: Import path validity (all imports work)
  - [ ] 61.7 Implement consistency check 4: Workflow ID consistency (same across steps)
  - [ ] 61.8 Implement consistency check 5: Audit trail complete (all 11 steps logged)
  - [ ] 61.9 Implement consistency check 6: State completeness (metadata present)
  - [ ] 61.10 Implement consistency check 7: Code modifications tracked (Step 11 changes logged)
  - [ ] 61.11 Implement consistency check 8: No orphaned state (clean state)
  - [ ] 61.12 Implement escalation logic (failure → human decision, not auto-restart)
  - [ ] 61.13 Implement failure context presentation (which check failed, what's wrong, suggested fix)
  - [ ] 61.14 Implement escalation options (re-run Step 11, restart workflow, accept, abort)
  - [ ] 61.15 Create unit test file `test_gates/test_qg_workflow_complete.py`
  - [ ] 61.16 Write test: all checks pass → PASS response
  - [ ] 61.17 Write test: check 1 fails (test path mismatch) → FAIL with context
  - [ ] 61.18 Write test: check 2 fails (file missing) → FAIL with file path
  - [ ] 61.19 Write test: check 3 fails (invalid import) → FAIL with import path
  - [ ] 61.20 Write test: check 4 fails (workflow ID mismatch) → FAIL with IDs
  - [ ] 61.21 Write test: check 5 fails (audit incomplete) → FAIL with missing step
  - [ ] 61.22 Write test: check 6 fails (metadata missing) → FAIL with required field
  - [ ] 61.23 Write test: check 7 fails (changes not tracked) → FAIL with modified file
  - [ ] 61.24 Write test: check 8 fails (orphaned state) → FAIL with artifact path
  - [ ] 61.25 Write test: escalation options presented correctly
  - [ ] 61.26 Mock StateManager for test isolation
  - [ ] 61.27 Run checks (formatter, linter, tests)
  - [ ] 61.28 **Audit: Verify testing skill conventions followed**
  - [ ] 61.29 Record results
  - [ ] 61.30 Commit: `feat: Implement qg_workflow_complete meta-gate (Task 61.0)`

**Done When:**
- All 8 consistency checks implemented
- Each check returns specific failure context
- Escalation logic works (human decides)
- Unit tests pass (all 8 checks + escalation scenarios, ≥90% coverage)

**Relevant Files:**
- `mcp_server/tools/gates/qg_workflow_complete.py` (new, ~400+ lines)
- `mcp_server/_dev_tests/test_gates/test_qg_workflow_complete.py` (new, ~250+ lines)

---

### Phase 4: MCP Server Integration

- [ ] **62.0 MCP Server Registration** [GLUE]
  - [ ] 62.1 Create branch `feature/62.0-mcp-registration`
  - [ ] 62.2 Open `mcp_server/server.py`
  - [ ] 62.3 Import run_test from `tools.operations.run_test`
  - [ ] 62.4 Import QGExecution from `tools.gates.qg_execution`
  - [ ] 62.5 Import QGWorkflowComplete from `tools.gates.qg_workflow_complete`
  - [ ] 62.6 Add async function `run_test(arguments: dict) -> str` (calls execute_test, returns JSON)
  - [ ] 62.7 Add async function `qg_execution(arguments: dict) -> str` (calls QGExecution.validate, returns JSON)
  - [ ] 62.8 Add async function `qg_workflow_complete(arguments: dict) -> str` (calls QGWorkflowComplete.validate, returns JSON)
  - [ ] 62.9 Register tools in MCP server tool list
  - [ ] 62.10 Update `mcp_server/tools/gates/__init__.py` (export QGExecution, QGWorkflowComplete)
  - [ ] 62.11 Update `mcp_server/tools/operations/__init__.py` (export execute_test)
  - [ ] 62.12 Verify tool registration (manual test - call tools via MCP)
  - [ ] 62.13 Run checks (formatter, linter, import validation)
  - [ ] 62.14 **Audit: Verify MCP tool registration pattern followed**
  - [ ] 62.15 Record results
  - [ ] 62.16 Commit: `feat: Register Step 11 tools in MCP server (Task 62.0)`

**Done When:**
- All 3 tools registered in server.py
- __init__.py exports updated
- Manual test confirms tools callable via MCP
- No import errors

**Relevant Files:**
- `mcp_server/server.py` (modified, ~30 lines added)
- `mcp_server/tools/gates/__init__.py` (modified, 2 exports added)
- `mcp_server/tools/operations/__init__.py` (modified, 1 export added)

---

### Phase 5: Documentation & Protocol

- [ ] **63.0 Documentation Updates** [GLUE]
  - [ ] 63.1 Create branch `feature/63.0-step11-documentation`
  - [ ] 63.2 Create file `.claude/skills/qa-management-layer/references/step-11.md`
  - [ ] 63.3 Write Step 11 protocol sections: Identity & Flow, Persona Map, Skill Instruction
  - [ ] 63.4 Document run_test operation tool usage
  - [ ] 63.5 Document qg_execution gate validation rules
  - [ ] 63.6 Document HITL triage workflow (3 options, user decisions)
  - [ ] 63.7 Document qg_workflow_complete validation (8 checks)
  - [ ] 63.8 Document state management (Step 11 data structure)
  - [ ] 63.9 Document enforcement rules (retry limits, error handling)
  - [ ] 63.10 Open `.claude/skills/qa-management-layer/SKILL.md`
  - [ ] 63.11 Update workflow overview (add Step 11 summary)
  - [ ] 63.12 Update step list (Steps 1-11 → Steps 1-11)
  - [ ] 63.13 Open `FRAMEWORK.md`
  - [ ] 63.14 Update Section 9 workflow diagram (add Step 11)
  - [ ] 63.15 Update section title "10-Step Workflow" → "11-Step Workflow"
  - [ ] 63.16 Search for "11-step" across all docs (grep -r "11-step" docs/)
  - [ ] 63.17 Replace "11-step" → "11-step" in all found instances
  - [ ] 63.18 Search for "Steps 1-11" across all docs
  - [ ] 63.19 Replace "Steps 1-11" → "Steps 1-11" in all found instances
  - [ ] 63.20 Run markdown linter (if available)
  - [ ] 63.21 **Audit: Verify documentation completeness**
  - [ ] 63.22 Record results (files updated, search/replace count)
  - [ ] 63.23 Commit: `docs: Add Step 11 protocol and update workflow docs (Task 63.0)`

**Done When:**
- step-11.md protocol reference complete (all sections)
- SKILL.md updated with Step 11 overview
- FRAMEWORK.md Section 9 updated (workflow diagram + references)
- All "11-step" references changed to "11-step"
- Documentation follows existing format/style

**Relevant Files:**
- `.claude/skills/qa-management-layer/references/step-11.md` (new, ~400+ lines)
- `.claude/skills/qa-management-layer/SKILL.md` (modified, Step 11 added)
- `FRAMEWORK.md` (modified, Section 9 updated)
- Multiple doc files (search/replace "11-step" → "11-step")

---

### Phase 6: Integration & E2E Testing

- [ ] **64.0 Integration Testing** [CORE]
  - [ ] 64.1 Create branch `feature/64.0-step11-integration-tests`
  - [ ] 64.2 Create file `mcp_server/_dev_tests/test_gates/test_step11_integration.py`
  - [ ] 64.3 Write test: Full tool chain (run_test → qg_execution → qg_workflow_complete)
  - [ ] 64.4 Write test: Triage workflow - app bug path (test fails, user selects "app defect", workflow stops)
  - [ ] 64.5 Write test: Triage workflow - test issue path (test fails, user selects "test issue", AI fixes, test re-runs)
  - [ ] 64.6 Write test: Dependency-aware re-validation - POM fix (POM modified → 4 gates re-run)
  - [ ] 64.7 Write test: Dependency-aware re-validation - Task fix (Task modified → 3 gates re-run)
  - [ ] 64.8 Write test: Dependency-aware re-validation - Role fix (Role modified → 2 gates re-run)
  - [ ] 64.9 Write test: Dependency-aware re-validation - Test fix (Test modified → 1 gate re-run)
  - [ ] 64.10 Write test: Same-error retry limit (2 attempts with same error → human intervention)
  - [ ] 64.11 Write test: Total attempt retry limit (5 attempts → human confirmation)
  - [ ] 64.12 Write test: Audit trail capture (PostToolUse hook integration)
  - [ ] 64.13 Write test: State persistence (Step 11 data saved correctly with triage history)
  - [ ] 64.14 Use real StateManager (not mocked)
  - [ ] 64.15 Mock subprocess calls (don't run actual pytest in integration tests)
  - [ ] 64.16 Mock Playwright snapshot calls
  - [ ] 64.17 Run checks (formatter, linter, tests)
  - [ ] 64.18 **Audit: Verify testing skill conventions followed**
  - [ ] 64.19 Record results
  - [ ] 64.20 Commit: `test: Add Step 11 integration tests (Task 64.0)`

**Done When:**
- Full tool chain tested (run_test → gates)
- Both triage paths tested (app bug, test issue)
- Dependency-aware re-validation tested (all 4 scenarios)
- Retry limits tested (same-error, total)
- Integration tests pass (≥85% coverage)

**Relevant Files:**
- `mcp_server/_dev_tests/test_gates/test_step11_integration.py` (new, ~400+ lines)

---

- [ ] **65.0 E2E Testing & Validation** [CORE]
  - [ ] 65.1 Create branch `feature/65.0-step11-e2e-tests`
  - [ ] 65.2 Create file `mcp_server/_dev_tests/test_step11_e2e.py`
  - [ ] 65.3 Write test: Happy path (11-step workflow, test passes on first run)
  - [ ] 65.4 Write test: Test failure - app bug (test fails, user selects "app defect", defect logged, workflow stops)
  - [ ] 65.5 Write test: Test failure - test issue (test fails, user selects "test issue", AI fixes POM, test passes)
  - [ ] 65.6 Write test: qg_workflow_complete failure - test path mismatch (escalates to human)
  - [ ] 65.7 Write test: qg_workflow_complete failure - file missing (escalates to human)
  - [ ] 65.8 Write test: qg_workflow_complete failure - workflow ID mismatch (escalates to human)
  - [ ] 65.9 Write test: Backward compatibility (old 11-step state file readable by Step 11 system)
  - [ ] 65.10 Write test: Migration validation (11-step workflow data + Step 11 data coexist)
  - [ ] 65.11 Write test: Audit trail completeness (all 11 steps logged, Step 11 detail file created)
  - [ ] 65.12 Write test: Performance validation (Step 11 completes < 2 minutes)
  - [ ] 65.13 Use real MCP server (integration test with actual tool registration)
  - [ ] 65.14 Use real Playwright for snapshot testing (in E2E only)
  - [ ] 65.15 Create sample test that PASSES (for happy path)
  - [ ] 65.16 Create sample test that FAILS (for failure scenarios)
  - [ ] 65.17 Run checks (formatter, linter, tests)
  - [ ] 65.18 **Audit: Verify testing skill conventions followed**
  - [ ] 65.19 Record results (test execution times, coverage)
  - [ ] 65.20 Commit: `test: Add Step 11 E2E tests and validation (Task 65.0)`

**Done When:**
- Happy path E2E test passes (full 11-step workflow)
- Failure scenarios tested (app bug, test issue, gate failures)
- Backward compatibility confirmed (old state files work)
- Performance validated (Step 11 < 2 min)
- All E2E tests pass

**Relevant Files:**
- `mcp_server/_dev_tests/test_step11_e2e.py` (new, ~500+ lines)
- `mcp_server/_dev_tests/fixtures/sample_passing_test.py` (new, test fixture)
- `mcp_server/_dev_tests/fixtures/sample_failing_test.py` (new, test fixture)

---

## Parent Task Breakdown

**Total Parent Tasks:** 8
- **CORE:** 6 tasks (58.0, 59.0, 60.0, 61.0, 64.0, 65.0)
- **GLUE:** 2 tasks (62.0, 63.0)

**Implementation Order:**
1. Task 58.0 (StateManager) - Foundation (breaking change)
2. Task 59.0 (run_test) - Operation tool
3. Task 60.0 (qg_execution) - Main gate
4. Task 61.0 (qg_workflow_complete) - Meta-gate
5. Task 62.0 (MCP registration) - Integration
6. Task 63.0 (Documentation) - Protocol updates
7. Task 64.0 (Integration tests) - Validation
8. Task 65.0 (E2E tests) - Final validation

**Estimated Complexity:**
- Task 58.0: LOW (single constant change)
- Task 59.0: MEDIUM (subprocess handling, output parsing)
- Task 60.0: HIGH (7 data types, HITL workflow, retry logic)
- Task 61.0: MEDIUM (8 checks, escalation logic)
- Task 62.0: LOW (registration boilerplate)
- Task 63.0: LOW (documentation updates)
- Task 64.0: MEDIUM (multiple integration scenarios)
- Task 65.0: MEDIUM (E2E scenarios, backward compatibility)

---

## Migration Strategy Alignment

Tasks align with 4-phase migration strategy from impact assessment:

**Phase 1: Core Implementation** → Tasks 59.0, 60.0, 61.0
- Create 3 new tools (run_test, qg_execution, qg_workflow_complete)
- No breaking changes yet (tools available but not required)

**Phase 2: StateManager Extension** → Task 58.0
- Update VALID_STEPS constant (breaking change)
- Run existing test suite (verify backward compatibility)

**Phase 3: Documentation** → Task 63.0
- Create step-11.md reference
- Update SKILL.md, FRAMEWORK.md
- Search & replace "11-step" → "11-step"

**Phase 4: Integration Testing** → Tasks 62.0, 64.0, 65.0
- Register tools in MCP server
- Integration tests (tool chain, triage workflows)
- E2E tests (happy path, failures, backward compatibility)

---

## Success Criteria

**Task completion is successful when:**

1. ✅ All existing tests pass (backward compatibility confirmed)
2. ✅ New Step 11 tests pass (functionality validated)
3. ✅ 11-step E2E workflow completes successfully
4. ✅ HITL triage workflow works (app bug vs test issue)
5. ✅ qg_workflow_complete catches consistency issues
6. ✅ Audit trail includes Step 11 data
7. ✅ Old 11-step state files still readable
8. ✅ Documentation updated ("11-step" → "11-step")
9. ✅ StateManager accepts step 11 data

**Quality Gates:**
- Formatter check passes
- Linter passes (no warnings)
- Type checker passes (if applicable)
- Unit tests pass (≥90% coverage for new code)
- Integration tests pass
- E2E tests pass
- All skill conventions followed (testing skill protocol)

---

## Task Execution Summary

**Total Tasks:** 8 parent tasks, 197 sub-tasks
**Estimated Lines of Code:** ~3,000+ lines (implementation + tests)
**Test Coverage Target:** ≥90% for CORE tasks, ≥85% for integration

**Sub-Task Breakdown:**
- Task 58.0: 12 sub-tasks (StateManager extension)
- Task 59.0: 20 sub-tasks (run_test operation)
- Task 60.0: 40 sub-tasks (qg_execution gate - most complex)
- Task 61.0: 30 sub-tasks (qg_workflow_complete meta-gate)
- Task 62.0: 16 sub-tasks (MCP server registration)
- Task 63.0: 23 sub-tasks (documentation updates)
- Task 64.0: 20 sub-tasks (integration testing)
- Task 65.0: 20 sub-tasks (E2E testing)

**Implementation Approach:**
- Use TDD for CORE tasks (write tests first, then implement)
- Follow testing skill conventions (AAA pattern, fixtures, mocking)
- Run checks after each task (formatter, linter, tests)
- Commit with conventional commit format
- Feature branches per parent task

**Next Phase:** Phase 4 (Deliver) - Execute tasks sequentially, starting with Task 58.0
