# Tasks: Step 1 - User Input (7-Step Workflow v4.0)

**PRD:** `2-prd-v4.md` (Step 1 section)
**Test Plan:** `4-test-plan-step1-v4.md` (6 component test pyramids, 155 tests total)
**Status:** Ready for implementation
**Approach:** TDD for Core (gates, transcript, state, audit), Test-After for Glue (protocol, hook)
**Date:** 2026-01-23

---

## Test Plan Integration

All tasks reference specific test pyramid layers from `4-test-plan-step1-v4.md`:

| Component | Pyramid Layers | Total Tests | Task |
|-----------|----------------|-------------|------|
| Protocol | 3 layers (17 tests) | 80% coverage | Task 5.1 (Layer 3) |
| Gate | 4 layers (53 tests) | 95% coverage | Task 3.0 (all layers) |
| State | 4 layers (33 tests) | 90% coverage | Task 5.2 (Layer 3) |
| Audit | 4 layers (33 tests) | 90% coverage | Task 5.3 (Layer 3) |
| Hook | 3 layers (18 tests) | 85% coverage | Task 5.4 (Layer 2) |
| Transcript | 4 layers (33 tests) | 90% coverage | Task 2.0 (all layers) |

**Total Step 1 Tests:** ~155 tests across all pyramid layers

**Test Execution Speed:**
- P0 (Layers 1-2): <10 seconds (run on every commit)
- P1 (Layers 3-4): <60 seconds (run before merge)

---

## Relevant Files

### Existing Files (Reuse)
- `.claude/skills/qa-management-layer/references/step-01.md` - Protocol specification (update needed for transcript)
- `mcp_server/tools/gates/qg_user_input.py` - Step 1 gate (POST validation - already implemented)
- `mcp_server/tools/gates/base_gate.py` - Base gate class (validate_and_pass method)
- `mcp_server/utils/state_manager.py` - State checkpoint manager (save_step method)
- `mcp_server/utils/audit_logger.py` - Audit logging (log_gate method - v1.0)
- `.claude/hooks/audit-trail-writer.py` - PostToolUse hook (already logs gate calls)

### New Files (Create)
- `mcp_server/utils/transcript_writer.py` - Workflow transcript writer (markdown append logic)
- `mcp_server/_dev_tests/test_utils/test_transcript_writer.py` - Unit tests for transcript writer

### Test Files (Create/Update)
- `mcp_server/_dev_tests/test_gates/test_qg_user_input.py` - Unit tests for gate validation logic (may exist, verify)
- `mcp_server/_dev_tests/test_integration/test_step1_e2e.py` - Integration test for full Step 1 flow

---

## Tasks

### Phase 0: Pre-Implementation Setup

- [x] 0.0 Create feature branch and verify existing components [GLUE]
  - [x] 0.1 Create branch `feature/step1-user-input-v4` ✓
  - [x] 0.2 Verify `qg_user_input.py` gate exists and implements POST validation ✓
  - [x] 0.3 Verify `AuditLogger` (v1.0) exists and implements atomic persist (DEF-040) ✓
  - [x] 0.4 Verify `StateManager` exists and implements per-run isolation ✓
  - [x] 0.5 Verify PostToolUse hook exists and logs gate calls ✓
  - [x] 0.6 Document findings: what exists, what needs creation, what needs updates ✓
  - [x] 0.7 Commit: `docs: Verify Step 1 existing components (Task 0.0)` ✓

**ASSESSMENT FINDINGS (Task 0.0):**

| Component | Status | Location | Tests Exist? | Test Status | Action Needed |
|-----------|--------|----------|--------------|-------------|---------------|
| **qg_user_input.py** | ✅ EXISTS | `mcp_server/tools/gates/qg_user_input.py` | ✅ YES | ⚠️ 29 tests, 16 FAILING | **FIX TESTS** - Tests out of sync with implementation |
| **AuditLogger** | ✅ EXISTS | `mcp_server/utils/audit_logger.py` | ✅ YES | ❓ Not run yet | **VERIFY TESTS** - Check coverage, gap-fill |
| **StateManager** | ✅ EXISTS | `mcp_server/utils/state_manager.py` | ✅ YES | ❓ Not run yet | **VERIFY TESTS** - Check coverage, gap-fill |
| **PostToolUse hook** | ✅ EXISTS | `.claude/hooks/audit-trail-writer.py` | ❌ NO | N/A | **CREATE TESTS** - Task 5.4 (Hook Layer 2) |
| **TranscriptWriter** | ✅ EXISTS | `mcp_server/utils/transcript_writer.py` | ❌ NO | N/A | **CREATE TESTS** - Task 2.0 (all 4 layers) |
| **step-01.md protocol** | ✅ EXISTS | `.claude/skills/qa-management-layer/references/step-01.md` | N/A | N/A | **UPDATE** - Add transcript write step |

**KEY FINDINGS:**

1. **TranscriptWriter ALREADY EXISTS** (created in previous session)
   - Has full implementation (reads audit log, generates markdown)
   - NO tests exist
   - **Action:** Task 2.0 becomes "Create tests for existing implementation" (not TDD from scratch)

2. **qg_user_input TESTS ARE FAILING** (16 out of 29 tests failing)
   - Tests exist but out of sync with current implementation
   - Common failure: Tests expect "pass" but getting "NEEDS_RETRY" (environment detection changed?)
   - **Action:** Task 3.0 becomes "Fix broken tests + gap-fill to reach 95% coverage"

3. **AuditLogger & StateManager have tests** (need verification)
   - `test_audit_logger.py` exists
   - `test_state_manager.py` exists
   - **Action:** Run tests, verify coverage, gap-fill if needed

4. **Hook has NO tests** (expected)
   - **Action:** Create tests per Layer 2 pyramid (3-5 tests)

5. **Protocol exists** (expected)
   - **Action:** Update with transcript write step

**DECISION IMPACT:**

| Original Plan | Revised Plan |
|---------------|--------------|
| Task 2.0: TDD TranscriptWriter from scratch | Task 2.0: Test-After for existing TranscriptWriter (create 4-layer pyramid) |
| Task 3.0: TDD gate tests | Task 3.0: Fix 16 failing tests + gap-fill to 95% coverage |
| Task 5.2-5.3: Create State/Audit Layer 3 tests | Task 5.2-5.3: Verify existing tests + gap-fill if needed |

**ESTIMATED EFFORT ADJUSTMENT:**
- Original: 19 hours (full TDD)
- Revised: 12-15 hours (fix existing + gap-fill)
  - Task 2.0: 3 hours (test-after, not TDD) - REDUCED
  - Task 3.0: 4 hours (fix 16 failing tests + gap-fill) - INCREASED
  - Task 5.0: 2 hours (verify existing tests) - REDUCED

---

### Phase 1: Test Infrastructure (TDD Setup)

- [x] 1.0 Create test infrastructure for Step 1 components [GLUE] ✓
  - [x] 1.1 Create `mcp_server/_dev_tests/test_integration/` directory if not exists ✓
  - [x] 1.2 Create `mcp_server/_dev_tests/test_utils/` directory if not exists ✓
  - [x] 1.3 Create test fixtures for Step 1 (valid/invalid personas, URLs, workflows) ✓
  - [x] 1.4 Create test data files: `test_data/step1_valid_inputs.json`, `test_data/step1_invalid_inputs.json` ✓
  - [x] 1.5 Create mock environment_config.json for testing (known/unknown domains) ✓
  - [x] 1.6 Run checks (no actual tests yet, just infrastructure) ✓
  - [x] 1.7 **Audit: Verify testing skill conventions followed** ✓
  - [x] 1.8 Record results ✓
  - [x] 1.9 Commit: `test: Create test infrastructure for Step 1 (Task 1.0)` ✓

**VERIFICATION RESULTS (Task 1.0):**

**Directories Created:**
- `mcp_server/_dev_tests/test_integration/` - Integration test location (with `__init__.py`)
- `mcp_server/_dev_tests/test_utils/` - Test utilities and fixtures (with `__init__.py`)

**Test Data Files Created:**
- `test_data/step1_valid_inputs.json` - 8 valid test cases (auth, catalog, checkout, admin, registration, premium, social workflows)
- `test_data/step1_invalid_inputs.json` - 16 invalid/edge case scenarios (missing fields, malformed URLs, invalid formats, long values)
- `test_data/mock_environment_config.json` - 5 known environments (automationpractice, helios1, parabank_test, test_env_1, test_env_2)

**Test Fixtures Created:**
- `test_utils/test_fixtures.py` - Comprehensive fixture module with:
  - Data loaders: `load_valid_inputs()`, `load_invalid_inputs()`, `load_mock_environment_config()`
  - Lookup helpers: `get_valid_input_by_id()`, `get_invalid_input_by_id()`, `get_known_environment_url()`
  - Builders: `build_valid_input()`, `build_invalid_input()`
  - Environment checker: `is_known_environment()`

**Import Verification:**
```bash
$ python -c "from test_utils import load_valid_inputs, load_invalid_inputs, load_mock_environment_config; ..."
Valid cases: 8
Invalid cases: 16
Mock environments: 5
Import test PASSED
```

**Testing Skill Conventions:**
- ✅ Centralized reports pattern (Pattern A)
- ✅ Test data in `test_data/` subdirectory
- ✅ Test utilities in dedicated package
- ✅ Follows JSON data format for fixtures
- ✅ Coverage targets defined in test plan (95% gates, 90% transcript/state/audit, 85% hook, 80% protocol)

---

### Phase 2: Transcript Writer (Test-After - Core Logic)

**Reference:** `4-test-plan-step1-v4.md` - Component 6: Transcript pyramid (4 layers, 33 tests)
**Note:** TranscriptWriter already exists from previous session - using test-after approach instead of TDD

- [x] 2.0 Create tests for existing TranscriptWriter (4-layer pyramid) [CORE] ✓
  - [x] 2.1 Created comprehensive test file `test_transcript_writer.py` with 24 tests ✓
  - [x] 2.2 Layer 1: 10 tests (constructor, generate, persist, path handling) ✓
  - [x] 2.3 Layer 2: 7 tests (gate, self-heal, tool, HITL, hook, unknown event formatters) ✓
  - [x] 2.4 Layer 3: 4 tests (event grouping, step sections, multi-event flows) ✓
  - [x] 2.5 Layer 4: 3 tests (missing file, malformed JSON, missing workflow_id) ✓
  - [x] 2.6 Run all transcript tests - ALL 24 PASSED ✓
  - [x] 2.7 Check coverage - 100% (exceeds 90% target) ✓
  - [x] 2.8 Updated conftest.py with transcript/layer markers ✓
  - [x] 2.9 Record results ✓
  - [x] 2.10 Commit: `test: Create comprehensive tests for TranscriptWriter (Task 2.0)` ✓

**TEST RESULTS (Task 2.0):**

**Test File:** `mcp_server/_dev_tests/test_transcript_writer.py`

**Test Breakdown by Layer:**
- **Layer 1 (Basic Operations):** 10 tests
  - Constructor (default/custom paths, Windows colon replacement)
  - generate() creates file and returns path
  - persist() creates directories
  - Empty events, workflow_id, timestamp, UTF-8 encoding
- **Layer 2 (Markdown Formatting):** 7 tests
  - Gate events (pass ✅ and fail ❌)
  - Self-heal events (🔧)
  - Tool call events (🔨)
  - HITL interaction events (👤)
  - Hook intervention events (⚠️)
  - Unknown event types (❓)
- **Layer 3 (Event Flow & Grouping):** 4 tests
  - Events grouped by step number
  - Multiple events within same step
  - Step sections separated by dividers
  - Events without step number ignored
- **Layer 4 (Error Handling):** 3 tests
  - Missing audit file raises FileNotFoundError
  - Malformed JSON raises JSONDecodeError
  - Missing workflow_id uses run_id fallback

**Test Execution:**
```bash
$ pytest test_transcript_writer.py -v
24 passed in 0.25s

$ pytest test_transcript_writer.py --cov=utils.transcript_writer --cov-report=term-missing
24 passed in 0.37s
Coverage: 100% (166/166 statements)
```

**Coverage Achievement:**
- Target: 90%
- Actual: 100%
- Statements: 166/166 covered
- Missing: 0

**Markers Registered:**
- `@pytest.mark.transcript` - All TranscriptWriter tests
- `@pytest.mark.layer1` - Basic operations (10 tests)
- `@pytest.mark.layer2` - Formatting (7 tests)
- `@pytest.mark.layer3` - Event flow (4 tests)
- `@pytest.mark.layer4` - Error handling (3 tests)

**Selective Test Execution:**
```bash
pytest -m "layer1 and transcript"  # Run only Layer 1 tests
pytest -m "transcript"              # Run all transcript tests
```

**Done When:**
- Layer 1: 10-15 tests (basic write operations)
- Layer 2: 5-10 tests (markdown formatting, edge cases)
- Layer 3: 3-5 tests (append behavior, integration)
- Layer 4: 2-3 tests (production failures)
- Total: ~33 tests, 90%+ coverage
- Markdown format matches PRD specification
- Transcript is human-readable

---

### Phase 3: Gate Validation Tests (Fix & Verify with Pyramid)

**Reference:** `4-test-plan-step1-v4.md` - Component 2: Gate pyramid (4 layers, 53 tests)

- [x] 3.0 Fix qg_user_input gate tests and verify coverage [CORE] ✓
  - [x] 3.1 Read existing `qg_user_input.py` - verified POST validation implemented ✓
  - [x] 3.2 Found existing tests: `test_gates/test_qg_user_input.py` (29 tests, 16 failing) ✓
  - [x] 3.3 Root cause analysis: BaseGate v4.0 requires transcript validation ✓
  - [x] 3.4 Fixed tests: Added transcript check mock + StateManager mock path fix ✓
  - [x] 3.5 All 29 tests PASSING ✓
  - [x] 3.6 Coverage: 95% (128/135 statements) - meets target ✓
  - [x] 3.7 Updated environment_config.json (added DEFAULT and parabank entries) ✓
  - [x] 3.8 Record results and commit ✓

**TEST RESULTS (Task 3.0):**

**Problem Identified:**
- 16 out of 29 tests failing with `"status": "NEEDS_RETRY"` instead of `"pass"`
- Root cause: BaseGate.validate_and_pass() (v4.0) requires transcript to exist before returning pass
- Tests written before v4.0 didn't account for transcript validation

**Solution Applied (Option 1 - Mock transcript check):**
1. Added autouse fixture to mock `BaseGate._check_transcript_written` → returns None
2. Fixed StateManager mock path from `tools.gates.qg_user_input.StateManager` to `utils.state_manager.StateManager`
3. Updated environment_config.json to add missing environments:
   - `DEFAULT`: http://www.automationpractice.pl/index.php
   - `parabank`: https://parabank.parasoft.com

**Changes Made:**
```python
# Added fixture to skip transcript validation in unit tests
@pytest.fixture(autouse=True)
def mock_transcript_check():
    """Mock BaseGate._check_transcript_written to skip transcript validation."""
    with patch('tools.gates.base_gate.BaseGate._check_transcript_written', return_value=None):
        yield
```

**Test Results:**
```bash
$ pytest test_gates/test_qg_user_input.py -v
29 passed in 0.22s

$ pytest test_gates/test_qg_user_input.py --cov=tools.gates.qg_user_input --cov-report=term-missing
Coverage: 95% (128/135 statements)
```

**Coverage Achievement:**
- Target: 95%
- Actual: 95%
- Statements: 128/135 covered
- Missing lines: 142, 144, 154-155, 163, 205-207 (edge cases in validation helpers)

**Test Breakdown:**
- Happy path: 8 tests ✓
- Negative cases: 5 tests ✓
- Edge cases: 4 tests ✓
- Error handling: 2 tests ✓
- Integration: 1 test ✓
- Environment detection: 5 tests ✓
- State management: 1 test ✓
- Workflow validation: 1 test ✓
- Role name validation: 1 test ✓
- Raw requirement: 1 test ✓

**Files Modified:**
- `test_gates/test_qg_user_input.py` (added transcript mock fixture, fixed StateManager mock path)
- `framework/resources/config/environment_config.json` (added DEFAULT and parabank)
  - [x] 3.4 **Layer 1: Regex Pattern Tests (51 tests, TDD)** ✓
    - [x] 3.4.1 Write tests: URL_PATTERN matches valid HTTP/HTTPS (9 tests) ✓
    - [x] 3.4.2 Write tests: PASCAL_CASE_PATTERN matches valid names (9 tests) ✓
    - [x] 3.4.3 Write tests: _is_valid_persona() with various inputs (6 tests) ✓
    - [x] 3.4.4 Write tests: _is_valid_url() with edge cases (9 tests) ✓
    - [x] 3.4.5 Write tests: _is_valid_role_name() with edge cases (7 tests) ✓
    - [x] 3.4.6 Write tests: _is_valid_workflow() validation (6 tests) ✓
    - [x] 3.4.7 Write tests: _is_valid_raw_requirement() validation (5 tests) ✓
    - [x] 3.4.8 Run Layer 1 tests - ALL PASSED ✓
  - [x] 3.5 **Layer 2: Edge Case Validation (10 tests)** ✓
    - [x] 3.5.1 test_url_with_special_chars ✓
    - [x] 3.5.2 test_unicode_in_persona ✓
    - [x] 3.5.3 test_very_long_persona (>1000 chars) ✓
    - [x] 3.5.4 test_very_long_url ✓
    - [x] 3.5.5 test_url_with_fragment ✓
    - [x] 3.5.6 test_url_with_basic_auth ✓
    - [x] 3.5.7 test_workflow_with_numbers ✓
    - [x] 3.5.8 test_role_name_all_caps ✓
    - [x] 3.5.9 test_minimal_valid_input ✓
    - [x] 3.5.10 Run Layer 2 tests - ALL PASSED ✓
  - [x] 3.6 **Layer 3: Integration with State (covered by existing tests)** ✓
    - [x] 3.6.1 test_state_saved_on_pass (existing) ✓
    - [x] 3.6.2 test_no_state_saved_on_fail (existing) ✓
    - [x] 3.6.3 test_blocks_step_3_on_fail (existing) ✓
    - [x] 3.6.4 test_detects_parabank_environment (existing) ✓
  - [x] 3.7 **Layer 4: Production Failure Scenarios (3 tests)** ✓
    - [x] 3.7.1 test_environment_config_read_fails - selective mock for config path ✓
    - [x] 3.7.2 test_state_manager_raises_exception - verifies graceful handling ✓
    - [x] 3.7.3 test_malformed_environment_config_json - selective mock + fallback ✓
    - [x] 3.7.4 Run Layer 4 tests - ALL PASSED ✓
  - [x] 3.8 Run all gate tests: 95 passed in 0.38s ✓
  - [x] 3.9 Coverage: 98% (135 stmts, 3 missing - urlparse edge cases) ✓
  - [x] 3.10 **Audit: All 4 pyramid layers implemented (95 tests > 53 target)** ✓
  - [x] 3.11 Acceptance test mapping verified ✓
  - [x] 3.12 Results recorded (see below) ✓
  - [ ] 3.13 Commit: `test: Implement qg_user_input gate 4-layer test pyramid (Task 3.0)`

**TEST RESULTS (Task 3.4-3.7 Completion):**

**Final Test Breakdown:**
| Layer | Target | Actual | Status |
|-------|--------|--------|--------|
| Layer 1 (Regex/Helpers) | 20-30 | 51 | ✅ Exceeds |
| Layer 2 (Edge Cases) | 10-15 | 10 | ✅ Meets |
| Layer 3 (Integration) | 3-5 | 4 (existing) | ✅ Meets |
| Layer 4 (Fault Injection) | 2-3 | 3 | ✅ Meets |
| **Total** | **53** | **95** | **✅ 179%** |

**Coverage:**
- Target: 95%
- Actual: 98%
- Missing lines: 167-168, 176 (urlparse exception handling - extremely rare edge cases)

**Key Implementation Notes:**
- Layer 4 tests required selective mocking (only fail for environment_config.json path)
- Global `builtins.open` mocks broke StateManager/AuditLogger file operations
- Fixed with custom `selective_fail_open()` side_effect functions

**Done When:**
- Layer 1: 20-30 tests (regex patterns, validation methods)
- Layer 2: 10-15 tests (edge cases, fix hints)
- Layer 3: 3-5 tests (integration with state)
- Layer 4: 2-3 tests (production failures)
- Total: ~53 tests, 95%+ coverage
- All validation rules from PRD covered
- All fix hints verified

---

### Phase 4: Protocol Update (Test-After - Glue)

- [x] 4.0 Update Step 1 protocol to include transcript writing [GLUE] ✓
  - [x] 4.1 Read existing `.claude/skills/qa-management-layer/references/step-01.md` ✓
  - [x] 4.2 Updated POST-ACTION to reflect v4.0 architecture (tests/_state/ path, hook-based) ✓
  - [x] 4.3 Specified transcript entry format (step name, inputs, fields, result, timestamp) ✓
  - [x] 4.4 Updated transcript write logic in POST-ACTION section ✓
  - [x] 4.5 Verified protocol follows qa-management-layer skill conventions ✓
  - [x] 4.6 Recorded changes in commit message ✓
  - [x] 4.7 Commit: `docs: Update step-01.md protocol - add transcript write (Task 4.0)` ✓

**COMPLETION RESULTS (Task 4.0):**

**Changes Made to step-01.md:**

Updated POST-ACTION section (lines 71-76) to reflect v4.0 architecture:

**Before:**
```markdown
POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, user inputs, extracted fields, gate result, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
```

**After:**
```markdown
POST-ACTION (on gate PASS only):
- Transcript automatically generated by PostToolUse hook after gate returns PASS
- Hook writes to tests/_state/<run_id>/workflow_transcript.md
- Transcript includes: step name, user inputs, extracted fields, gate result, timestamp
- Uses TranscriptWriter utility to generate markdown from audit log
- Append mode (preserves existing step entries from same run)
- No manual AI action required - hook executes automatically after qg_user_input PASS
```

**Key Improvements:**
1. ✅ Clarifies transcript write occurs AFTER gate PASS only (not on FAIL/NEEDS_RETRY)
2. ✅ Specifies PostToolUse hook handles this automatically (defense-in-depth architecture)
3. ✅ Corrects path from `tests/_reports/` to `tests/_state/<run_id>/` (matches v4.0)
4. ✅ References TranscriptWriter utility (links protocol to implementation)
5. ✅ Makes clear no manual AI action required (reduces cognitive load)

**Verification:**
- Protocol follows qa-management-layer skill conventions ✅
- POST-ACTION section aligns with defense-in-depth architecture (Hook component) ✅
- Path matches StateManager and TranscriptWriter implementation ✅
- Clear enough for AI to understand automated behavior ✅

**Done When:**
- Protocol includes transcript writing step ✅
- Transcript format specified in protocol ✅
- Protocol is clear enough for AI to follow ✅

---

### Phase 5: Integration Tests (E2E Step 1 Flow + Component Layer 3s)

**Reference:** `4-test-plan-step1-v4.md` - Layer 3 tests for all 6 components

- [ ] 5.0 Implement Layer 3 integration tests for all components [CORE]
  - [ ] 5.1 **Protocol Layer 3: E2E Protocol Adherence (1-2 tests)**
    - [ ] 5.1.1 Write test: `test_step1_full_flow_valid_inputs()` (AT-1.1)
      - AI asks for persona, URL, workflow
      - User provides valid inputs
      - AI extracts role_name, auto-detects environment
      - AI calls qg_user_input (POST)
      - Gate validates and passes
      - State saved with all fields
      - Audit log contains gate_validation event
      - Transcript contains Step 1 entry
      - Verify test passes
    - [ ] 5.1.2 Write test: `test_step1_full_flow_with_retry()` (AT-1.9)
      - User provides invalid persona (empty)
      - Gate fails with fix hint
      - User corrects persona
      - Gate validates and passes
      - State saved with corrected persona
      - Verify test passes
    - [ ] 5.1.3 Run Protocol Layer 3 tests
  - [ ] 5.2 **State Layer 3: Isolation & Concurrency (3-5 tests)**
    - [ ] 5.2.1 Write test: `test_multiple_runs_dont_overwrite()` (AT-1.10)
      - Run Step 1 with run_id_A
      - Run Step 1 with run_id_B
      - Verify both state files exist
      - Verify run_A state != run_B state
    - [ ] 5.2.2 Write test: `test_state_immutability_after_write()`
      - Save state
      - Attempt to modify state file directly
      - Load state
      - Verify modifications NOT reflected (if possible to enforce)
    - [ ] 5.2.3 Write test: `test_concurrent_writes_same_run()` (optional, rare scenario)
    - [ ] 5.2.4 Run State Layer 3 tests
  - [ ] 5.3 **Audit Layer 3: Append & Immutability (3-5 tests)**
    - [ ] 5.3.1 Write test: `test_multiple_events_appended_correctly()` (AT-1.8)
      - Log gate_validation event (Step 1)
      - Log another event (simulate Step 2)
      - Verify both events in audit log
      - Verify events array has correct order
    - [ ] 5.3.2 Write test: `test_existing_events_not_modified()`
      - Load existing audit log with events
      - Append new event
      - Verify existing events unchanged
    - [ ] 5.3.3 Write test: `test_workflow_restart_loads_existing_events()`
      - Create audit log with events
      - Initialize new AuditLogger with same run_id
      - Verify existing events loaded
    - [ ] 5.3.4 Run Audit Layer 3 tests
  - [ ] 5.4 **Hook Layer 2: Integration with MCP (3-5 tests)**
    - [ ] 5.4.1 Write test: `test_hook_triggers_after_gate_call()`
      - Call qg_user_input gate (mock MCP)
      - Verify hook triggered
      - Verify AuditLogger.log_gate() called
    - [ ] 5.4.2 Write test: `test_hook_calls_audit_logger()`
      - Trigger hook with gate result
      - Verify AuditLogger.log_gate() called with correct params
    - [ ] 5.4.3 Write test: `test_hook_ignores_non_gate_tools()`
      - Trigger hook with non-gate tool result
      - Verify AuditLogger NOT called
    - [ ] 5.4.4 Run Hook Layer 2 tests
  - [ ] 5.5 **E2E Acceptance Test Coverage Verification**
    - [ ] 5.5.1 Verify AT-1.1 (valid input) covered by Protocol Layer 3
    - [ ] 5.5.2 Verify AT-1.2 (invalid persona) covered by Gate Layer 2
    - [ ] 5.5.3 Verify AT-1.3 (invalid URL) covered by Gate Layer 2
    - [ ] 5.5.4 Verify AT-1.4 (environment detection) covered by Gate Layer 1+3
    - [ ] 5.5.5 Verify AT-1.5 (unknown environment) covered by Gate Layer 2
    - [ ] 5.5.6 Verify AT-1.6 (role name extraction) covered by Gate Layer 1
    - [ ] 5.5.7 Verify AT-1.7 (crash safety) covered by Audit/State Layer 4
    - [ ] 5.5.8 Verify AT-1.8 (transcript append) covered by Transcript/Audit Layer 3
    - [ ] 5.5.9 Verify AT-1.9 (gate retry) covered by Protocol Layer 3
    - [ ] 5.5.10 Verify AT-1.10 (state isolation) covered by State Layer 3
  - [ ] 5.6 Run all integration tests (pytest -m "layer3" -v)
  - [ ] 5.7 Check coverage (target: 80%+ for integration tests)
  - [ ] 5.8 **Audit: Verify all Layer 3 tests implemented across all components**
  - [ ] 5.9 **Audit: Verify all 10 acceptance tests covered**
  - [ ] 5.10 Record results (test count per component, acceptance test mapping)
  - [ ] 5.11 Commit: `test: Implement Layer 3 integration tests for all Step 1 components (Task 5.0)`

**Done When:**
- Protocol Layer 3: 2 tests (E2E flows)
- State Layer 3: 3-5 tests (isolation, concurrency)
- Audit Layer 3: 3-5 tests (append, immutability)
- Hook Layer 2: 3-5 tests (integration with MCP)
- Transcript Layer 3: Already implemented in Task 2.3
- Total: ~15-20 integration tests
- All 10 acceptance tests (AT-1.1 through AT-1.10) mapped to tests
- Coverage: 80%+ for integration layer

---

### Phase 6: Manual Testing & Validation

- [ ] 6.0 Manual testing and validation [GLUE]
  - [ ] 6.1 Run Step 1 manually with valid inputs
  - [ ] 6.2 Verify state saved correctly: `cat tests/_state/{run_id}/workflow_state.json`
  - [ ] 6.3 Verify audit log: `cat tests/_audit/audit_log_{run_id}.json`
  - [ ] 6.4 Verify transcript: `cat tests/_reports/{run_id}/workflow_transcript.md`
  - [ ] 6.5 Test gate retry: Provide invalid input, verify fix hint, correct input, verify retry works
  - [ ] 6.6 Test environment detection: Use unknown URL, verify NEEDS_RETRY behavior
  - [ ] 6.7 Verify transcript is readable (open in text editor, check formatting)
  - [ ] 6.8 Verify transcript emoji indicators work (✓ ⏳ ❌)
  - [ ] 6.9 **Audit: Verify manual testing covers all user-facing scenarios**
  - [ ] 6.10 Record results (screenshots, findings, any issues)
  - [ ] 6.11 Commit: `docs: Add manual testing results for Step 1 (Task 6.0)`

**Done When:**
- All manual tests pass
- State, audit log, transcript verified manually
- No user confusion (transcript is clear and readable)

---

### Phase 7: Documentation & Cleanup

- [ ] 7.0 Update documentation and finalize Step 1 [GLUE]
  - [ ] 7.1 Update design doc (`1-design-discussion-v4.md`): Mark Step 1 as ✅ IMPLEMENTED
  - [ ] 7.2 Update PRD (`2-prd-v4.md`): Add implementation notes section for Step 1
  - [ ] 7.3 Update SESSION.md: Record Step 1 completion, move to Step 2 design phase
  - [ ] 7.4 Update SKILL.md if protocol changes affect skill interface
  - [ ] 7.5 Run all tests one final time (unit + integration)
  - [ ] 7.6 Check overall coverage (target: >85% for Step 1 components)
  - [ ] 7.7 Create summary report: tests written, coverage achieved, manual testing results
  - [ ] 7.8 **Audit: Verify all Step 1 requirements from PRD implemented**
  - [ ] 7.9 Record final results
  - [ ] 7.10 Commit: `docs: Finalize Step 1 documentation (Task 7.0)`

**Done When:**
- All documentation updated
- All tests pass (unit + integration)
- Coverage >85% for Step 1 components
- Ready to move to Step 2 design

---

## Test Execution Commands

### Unit Tests
```bash
# Transcript writer tests
pytest mcp_server/_dev_tests/test_utils/test_transcript_writer.py -v

# Gate validation tests
pytest mcp_server/_dev_tests/test_gates/test_qg_user_input.py -v

# All unit tests
pytest mcp_server/_dev_tests/test_utils/ mcp_server/_dev_tests/test_gates/ -v
```

### Integration Tests
```bash
# Step 1 E2E tests
pytest mcp_server/_dev_tests/test_integration/test_step1_e2e.py -v

# All integration tests
pytest mcp_server/_dev_tests/test_integration/ -v
```

### Coverage
```bash
# Coverage for all Step 1 components
pytest mcp_server/_dev_tests/ --cov=mcp_server/utils/transcript_writer --cov=mcp_server/tools/gates/qg_user_input --cov-report=html --cov-report=term

# Open coverage report
# Windows: start htmlcov/index.html
# Linux/Mac: open htmlcov/index.html
```

---

## Implementation Notes

### TDD Pattern (Core Tasks)
- **Red:** Write failing test first
- **Green:** Implement minimal code to pass test
- **Refactor:** Clean up code, extract common logic
- Repeat for each test case

### Test-After Pattern (Glue Tasks)
- Implement functionality first
- Write tests to verify behavior
- Ensure adequate coverage (80%+)

### Coverage Targets
- Gates: 95%+ (critical validation logic)
- State/Audit: 90%+ (data integrity)
- Transcript: 90%+ (new component)
- Integration: 80%+ (E2E flow)

### Definition of Done (Per Task)
- All subtasks completed
- Tests pass (unit + integration)
- Coverage meets target
- Audit step verified
- Results recorded
- Committed with conventional commit message

---

**Next Phase:** Execute tasks 0.0 through 7.0, then move to Step 2 design

**Estimated Effort (Updated with Test Pyramids):**
- Phase 0-1: 1 hour (setup + test infrastructure)
- Phase 2: 5 hours (TDD for TranscriptWriter - 4 layers, 33 tests)
  - Layer 1: 2 hours (10-15 basic write operation tests)
  - Layer 2: 1.5 hours (5-10 markdown formatting tests)
  - Layer 3: 1 hour (3-5 append behavior tests)
  - Layer 4: 0.5 hour (2-3 production failure tests)
- Phase 3: 6 hours (TDD for Gate - 4 layers, 53 tests)
  - Layer 1: 2.5 hours (20-30 regex pattern tests)
  - Layer 2: 2 hours (10-15 edge case tests)
  - Layer 3: 1 hour (3-5 integration with state tests)
  - Layer 4: 0.5 hour (2-3 production failure tests)
- Phase 4: 1 hour (protocol update)
- Phase 5: 4 hours (Layer 3 integration tests for all components)
  - Protocol Layer 3: 1 hour (2 tests)
  - State Layer 3: 1 hour (3-5 tests)
  - Audit Layer 3: 1 hour (3-5 tests)
  - Hook Layer 2: 1 hour (3-5 tests)
- Phase 6: 1 hour (manual testing)
- Phase 7: 1 hour (documentation)
- **Total:** ~19 hours for Step 1 complete implementation with full test pyramids

**Test Breakdown:**
- Layer 1 tests: ~45 tests (basic building blocks - 3-4 hours)
- Layer 2 tests: ~35 tests (edge cases - 3-4 hours)
- Layer 3 tests: ~25 tests (integration - 4 hours)
- Layer 4 tests: ~10 tests (production failures - 1 hour)
- **Total:** 155 tests across all layers

**Confidence Level:** High - TDD approach with clear pyramid structure ensures quality
