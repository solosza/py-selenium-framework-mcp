# Task List: Release Readiness

**Version:** 1.0
**Created:** 2025-12-27
**PRD:** `1-prd-release-readiness.md`
**Branch:** `feature/release-readiness`

---

## Relevant Files

### Audit Trail (Task 1.0)
- `mcp_server/utils/audit_logger.py` - NEW: Audit log writer class
- `tests/_audit/` - Directory for `audit_log_{timestamp}.json` files (was mcp_server/state)
- `mcp_server/tools/gates/base_gate.py` - Add audit logging hook
- `mcp_server/_dev_tests/test_audit_logger.py` - NEW: Unit tests for AuditLogger

### Self-Heal Cap (Task 2.0)
- `mcp_server/utils/state_manager.py` - Add attempt tracking methods
- `mcp_server/tools/gates/base_gate.py` - Add `blocked_response()` method
- `mcp_server/tools/gates/qg_page_object.py` - Update POST to check attempts
- `mcp_server/tools/gates/qg_task.py` - Update POST to check attempts
- `mcp_server/tools/gates/qg_role.py` - Update POST to check attempts
- `mcp_server/tools/gates/qg_test_runner.py` - Update POST to check attempts
- `mcp_server/_dev_tests/test_self_heal_cap.py` - NEW: Unit tests for cap enforcement

### Execution Mode Flag (Task 2.5)
- `mcp_server/utils/state_manager.py` - Add execution_mode get/set methods
- `mcp_server/utils/audit_logger.py` - Add source parameter to log_gate(), execution summary
- `mcp_server/tools/gates/qg_page_object.py` - Accept source parameter in POST
- `mcp_server/tools/gates/qg_task.py` - Accept source parameter in POST
- `mcp_server/tools/gates/qg_role.py` - Accept source parameter in POST
- `mcp_server/tools/gates/qg_test_runner.py` - Accept source parameter in POST
- `mcp_server/_dev_tests/test_execution_mode.py` - NEW: Unit tests for execution mode

### License & Documentation (Task 3.0)
- `.claude/skills/qa-guidance-layer/SKILL.md` - Add license header
- `.claude/skills/qa-guidance-layer/references/*.md` - Add license headers
- `.claude/skills/*/SKILL.md` - Add license headers to all skills
- `LICENSE.md` - NEW: Skills license terms
- `README.md` - Add installation guide section

### Validation (Tasks 4.0, 5.0)
- `SESSION.md` - Document smoke test results
- `docs/DEFECT_LOG.md` - Track any issues found

### Production Fixes (Task 7.0)
- `mcp_server/utils/state_manager.py` - Refactor to per-run directories
- `mcp_server/tools/gates/base_gate.py` - Fix audit run_id reuse
- `mcp_server/tools/gates/qg_page_object.py` - Add immediate file write
- `mcp_server/tools/gates/qg_task.py` - Add immediate file write
- `mcp_server/tools/gates/qg_role.py` - Add immediate file write
- `mcp_server/tools/gates/qg_test_runner.py` - Add immediate file write
- `mcp_server/tools/gates/qg_save_run.py` - Add file existence validation
- `.claude/skills/qa-guidance-layer/references/step-06.md` - Update docs
- `.claude/skills/qa-guidance-layer/references/step-07.md` - Update docs
- `.claude/skills/qa-guidance-layer/references/step-08.md` - Update docs
- `.claude/skills/qa-guidance-layer/references/step-09.md` - Update docs
- `.claude/skills/qa-guidance-layer/references/step-10.md` - Update docs
- `tests/_state/{run_id}/` - NEW: Per-run state directories
- `mcp_server/_dev_tests/test_production_fixes.py` - NEW: Unit tests for fixes

---

## Notes

- Tests for CORE tasks use pytest: `python -m pytest mcp_server/_dev_tests/`
- VALIDATION tasks don't produce code, they produce documentation
- Each parent task gets its own branch: `feature/<task-id>-short-name`

---

## Tasks

- [x] **1.0 Audit Trail System** [CORE] ✓ COMMITTED (a90a5d7)
  - [x] 1.1 Create branch `feature/1.0-audit-trail`
  - [x] 1.2 **Invoke `testing` skill** - Follow TDD for CORE logic (Red-Green-Refactor)
  - [x] 1.3 Write failing tests first for AuditLogger (31 tests)
  - [x] 1.4 Create `mcp_server/utils/audit_logger.py` with AuditLogger class
    - `__init__(run_id)` - Initialize with timestamp-based run ID
    - `log_gate(step, gate_name, mode, result, error=None, source=None)` - Record gate call
    - `log_self_heal(step, attempt, error)` - Record self-heal attempt
    - `log_file_generated(path, step)` - Record file output
    - `get_summary()` - Return summary dict (total_steps, gates_passed, etc.)
    - `finalize()` - Write JSON file to `mcp_server/state/`
  - [x] 1.5 Define audit log JSON schema matching PRD spec
  - [x] 1.6 Add `_audit_logger` class variable to BaseGate
  - [x] 1.7 Add `set_audit_logger(logger)` class method to BaseGate
  - [x] 1.8 Update `pass_response()` to log gate pass if logger set
  - [x] 1.9 Update `fail_response()` to log gate fail if logger set
  - [x] 1.10 Run checks: 50 tests passed
  - [x] 1.11 **Audit: Verify testing skill conventions followed** ✓ TDD
  - [x] 1.12 Record results: 31 audit + 19 base_gate tests
  - [x] 1.13 Commit: `feat: add audit trail system (Task 1.0)`

---

- [x] **2.0 Self-Heal Cap Enforcement** [CORE] ✓ COMMITTED (84d9d31)
  - [x] 2.1 Create branch `feature/2.0-self-heal-cap`
  - [x] 2.2 **Invoke `testing` skill** - Follow TDD for CORE logic (Red-Green-Refactor)
  - [x] 2.3 Write failing tests first for attempt tracking and blocked status (24 tests)
  - [x] 2.4 Add to StateManager:
    - `_attempt_counts: dict` - Per-step attempt tracking (stored in state file under `_attempts` key)
    - `increment_attempt(step) -> int` - Increment and return count
    - `get_attempt_count(step) -> int` - Get current count
    - `reset_attempts(step)` - Reset on success
  - [x] 2.5 Add to BaseGate:
    - `MAX_ATTEMPTS = 3` - Class constant
    - `blocked_response(step, attempts, errors)` - Return blocked status
    - `set_state_manager(manager)` - Inject state manager for testing
  - [x] 2.6 Update `qg_page_object.validate_post()`:
    - Check attempt count before validation
    - If >= MAX_ATTEMPTS, return blocked response
    - On fail, increment attempt and include in audit
    - On pass, reset attempts
  - [x] 2.7 Update `qg_task.validate_post()` with same pattern
  - [x] 2.8 Update `qg_role.validate_post()` with same pattern
  - [x] 2.9 Update `qg_test_runner.validate_post()` with same pattern
  - [x] 2.10 Integrate attempt logging with AuditLogger
  - [x] 2.11 Run checks: 24 self-heal cap tests passed, 461 total passed
  - [x] 2.12 **Audit: Verify testing skill conventions followed** ✓ TDD
  - [x] 2.13 Record results: 24 new tests, all passing
  - [x] 2.14 Commit: `feat: add self-heal cap enforcement (Task 2.0)`

---

- [x] **2.5 Execution Mode Flag** [CORE] ✓ COMMITTED
  - [x] 2.5.1 Create branch `feature/2.5-execution-mode`
  - [x] 2.5.2 **Invoke `testing` skill** - Follow TDD for CORE logic (Red-Green-Refactor)
  - [x] 2.5.3 Write failing tests first for execution mode infrastructure (21 tests)
  - [x] 2.5.4 Add to StateManager:
    - `get_execution_mode() -> str` - Return current mode ("mixed" or "skills_only")
    - `set_execution_mode(mode: str)` - Set mode (validated)
    - Default from env var `ISAGAWA_EXECUTION_MODE` or "mixed"
  - [x] 2.5.5 Add to workflow state schema:
    - `execution_mode` field (default: "mixed")
  - [x] 2.5.6 Update AuditLogger:
    - `log_gate()` now accepts `source` parameter (tool/ai/self-heal)
    - Store source per step in audit log
  - [x] 2.5.7 Update code-generating gates (Steps 6-9) to accept `source` parameter:
    - `qg_page_object` POST: Add `source` to input_data, pass to audit
    - `qg_task` POST: Same pattern
    - `qg_role` POST: Same pattern
    - `qg_test_runner` POST: Same pattern
  - [x] 2.5.8 Add "Execution Summary" section to audit log:
    - Count of tool-generated vs ai-generated vs self-healed steps
    - Execution mode used
  - [x] 2.5.9 Run checks: 21 tests pass (466 total, 3 pre-existing failures)
  - [x] 2.5.10 **Audit: Verify testing skill conventions followed** ✓ TDD
  - [x] 2.5.11 Commit: `feat: add execution mode flag infrastructure (Task 2.5)`

  **Done When:**
  - `execution_mode` stored in workflow state
  - `source` tracked per step in audit log
  - Execution summary in audit report
  - All tests pass

---

- [x] **3.0 License & Documentation** [GLUE] ✓ COMMITTED (798dfcd)
  - [x] 3.1 Create branch `feature/3.0-license-docs`
  - [x] 3.2 **Invoke `documentation` skill** - Follow doc conventions
  - [x] 3.3 Create license header template:
    ```
    <!-- LICENSE: Proprietary - Isagawa Corp -->
    <!-- You may USE this skill with Claude Code. -->
    <!-- You may NOT redistribute, modify, or create derivative works. -->
    <!-- See LICENSE.md for full terms. -->
    ```
  - [x] 3.4 Add header to `.claude/skills/qa-guidance-layer/SKILL.md`
  - [x] 3.5 Add header to all files in `.claude/skills/qa-guidance-layer/references/`
  - [x] 3.6 Add header to all other skill directories (`dialogue-engine`, `testing`, etc.)
  - [x] 3.7 Create `LICENSE.md` with full terms:
    - Grant: Use with Claude Code
    - Restrictions: No redistribution, no modification, no derivatives
    - Attribution: Isagawa Corp
  - [x] 3.8 Update README.md with Installation Guide section:
    - Prerequisites (Python 3.x, pip)
    - Clone repository
    - Install dependencies
    - Copy skills to project
    - Configure MCP server
    - Quick start example
  - [x] 3.9 **Audit: Verify all skill files have headers** ✓ 35 files
  - [x] 3.10 Commit: `docs: add license headers and installation guide (Task 3.0)`

---

- [ ] **4.0 Smoke Test Validation** [VALIDATION]
  - [ ] 4.1 Select 2 additional test sites (criteria: public, stable, different UI)
    - Candidate 1: saucedemo.com (Swag Labs - React-based)
    - Candidate 2: demoqa.com (more complex forms)
  - [ ] 4.2 **Invoke `qa-guidance-layer` skill** - Follow 10-step workflow for each test
  - [ ] 4.3 Site 1 - Simple workflow: Login test
    - Run 10-step workflow
    - Document: all gates pass? any self-heals?
  - [ ] 4.4 Site 1 - Medium workflow: Add to cart
    - Run 10-step workflow
    - Document results
  - [ ] 4.5 Site 2 - Simple workflow: Form submission
    - Run 10-step workflow
    - Document results
  - [ ] 4.6 Site 2 - Medium workflow: Multi-step form
    - Run 10-step workflow
    - Document results
  - [ ] 4.7 Complex workflow (either site): Multi-page checkout or registration flow
    - Run 10-step workflow
    - Document results
  - [ ] 4.8 Update SESSION.md with validation matrix results
  - [ ] 4.9 Log any defects to DEFECT_LOG.md

  **Done When:**
  - 2+ sites tested
  - At least 1 complex workflow passes
  - Results documented in SESSION.md

---

- [ ] **5.0 Adversarial Input Validation** [VALIDATION]
  - [ ] 5.1 **Invoke `qa-guidance-layer` skill** - Follow 10-step workflow for each test case
  - [ ] 5.2 Test Case 1: Ambiguous requirement
    - Input: "register user" (no details)
    - Expected: Gate asks for missing details or fails with helpful message
    - Document actual behavior
  - [ ] 5.3 Test Case 2: Missing URL
    - Input: Persona only, no page specified
    - Expected: `qg_user_input` rejects with fix_hint
    - Document actual behavior
  - [ ] 5.4 Test Case 3: Contradictory requirement
    - Input: "login without credentials"
    - Expected: Gate catches logical impossibility
    - Document actual behavior
  - [ ] 5.5 Test Case 4: Multi-step in one prompt
    - Input: "login, browse products, add to cart, checkout"
    - Expected: System handles or requests breakdown
    - Document actual behavior
  - [ ] 5.6 Test Case 5: Malformed BDD
    - Input: Requirement with no clear Given/When/Then structure
    - Expected: `qg_test_scenarios` rejects with fix_hint
    - Document actual behavior
  - [ ] 5.7 Update SESSION.md with adversarial test results
  - [ ] 5.8 Log any defects or improvements needed to DEFECT_LOG.md

  **Done When:**
  - 5 adversarial cases tested
  - Gates block with helpful error messages
  - Any defects logged

---

- [ ] **6.0 E2E Integration Verification** [INTEGRATION]
  - [ ] 6.1 Create branch `feature/6.0-e2e-verification`
  - [ ] 6.2 **Invoke `qa-guidance-layer` skill** - Follow 10-step workflow
  - [ ] 6.3 **Invoke `testing` skill** - For verification assertions
  - [ ] 6.4 Clear workflow state: `mcp_server/state/workflow_state.json`
  - [ ] 6.5 Run full 10-step workflow on automationpractice.pl (new test)
  - [ ] 6.6 Verify audit log created: `audit_log_{timestamp}.json`
    - Contains all 10 steps
    - Shows execution source per step
    - Summary section populated
  - [ ] 6.7 Simulate failure to test self-heal cap:
    - Intentionally fail Step 6 POM 3 times
    - Verify gate returns `blocked` status
    - Verify DD-22 user decision triggered
  - [ ] 6.8 Verify attempt count resets on success
  - [ ] 6.9 Final review: all tests passing
  - [ ] 6.10 Merge all feature branches to main
  - [ ] 6.11 Commit: `feat: release readiness complete (Task 6.0)`

  **Done When:**
  - E2E workflow passes with audit trail
  - Self-heal cap verified working
  - All feature branches merged
  - Clean main branch

---

- [ ] **7.0 Production Test Fixes** [CORE] - UNBLOCKS MULTI-PAGE WORKFLOWS
  - [ ] 7.1 Create branch `feature/7.0-production-fixes`
  - [ ] 7.2 **Invoke `testing` skill** - Follow TDD for CORE logic (Red-Green-Refactor)
  - [ ] 7.3 Write failing tests first for per-run state architecture (15 tests)
  - [ ] 7.4 **FIX #1: Audit run_id reuse (DEF-049)**
    - Update `BaseGate.get_audit_logger()`:
      - Remove check for `existing_run_id` from state
      - Always create fresh AuditLogger with new run_id
      - Document: "Each workflow run gets fresh audit file"
    - Test: Multiple workflow runs create separate audit files
  - [ ] 7.5 **FIX #2: Per-run state directories (DEF-050)**
    - Update `StateManager.__init__()`:
      - Accept `run_id` parameter (required)
      - Create `tests/_state/{run_id}/` directory
      - Set state file path to `tests/_state/{run_id}/workflow_state.json`
    - Update `StateManager.save()`:
      - Write to per-run state file (not monolithic)
    - Update `StateManager.load()`:
      - Load from per-run state file
    - Add `StateManager.get_run_id()` method
    - Test: Multiple runs create separate state directories
  - [ ] 7.6 **FIX #3: Immediate file writes (DEF-051)**
    - Update `qg_page_object.validate_post()`:
      - After validation passes, write POM file to disk IMMEDIATELY
      - Use metadata.file_path for target location
      - Multi-page: iterate ALL POMs in generated_poms, write each
      - Log file write to audit trail
    - Update `qg_task.validate_post()`:
      - After validation passes, write Task file to disk IMMEDIATELY
      - Log file write to audit trail
    - Update `qg_role.validate_post()`:
      - After validation passes, write Role file to disk IMMEDIATELY
      - Log file write to audit trail
    - Update `qg_test_runner.validate_post()`:
      - After validation passes, write Test file to disk IMMEDIATELY
      - Log file write to audit trail
    - Test: Files exist on disk after each gate passes
  - [ ] 7.7 **ENHANCEMENT: Step 10 validation**
    - Update `qg_save_run.validate_pre()`:
      - Load expected files list from state (steps 6-9 metadata)
      - Verify all files exist on disk
      - Return fail with missing file list if any missing
      - Include helpful error: "Expected files: [...], Missing: [...]"
    - Test: Missing files detected and reported
  - [ ] 7.8 Update step skill references (6-10):
    - `.claude/skills/qa-guidance-layer/references/step-06.md` - Document immediate write
    - `.claude/skills/qa-guidance-layer/references/step-07.md` - Document immediate write
    - `.claude/skills/qa-guidance-layer/references/step-08.md` - Document immediate write
    - `.claude/skills/qa-guidance-layer/references/step-09.md` - Document immediate write
    - `.claude/skills/qa-guidance-layer/references/step-10.md` - Document validation role
  - [ ] 7.9 Integration with BaseGate:
    - Update all gates to pass run_id to StateManager
    - Ensure StateManager initialized with run_id from audit logger
  - [ ] 7.10 Run checks: All tests pass (485+ tests)
  - [ ] 7.11 **Audit: Verify testing skill conventions followed** ✓ TDD
  - [ ] 7.12 Record results: 15+ new tests, all passing
  - [ ] 7.13 Commit: `fix: production test critical failures (Task 7.0)`

  **Done When:**
  - Each workflow run creates separate state directory
  - Each workflow run creates separate audit file
  - All files written immediately after gate passes
  - Step 10 validates all files exist
  - Multi-page workflows save ALL POMs
  - All tests pass

  **Defects Fixed:**
  - DEF-049: Audit run_id reuse causes audit history loss
  - DEF-050: State not persisted per-run (no context recovery)
  - DEF-051: Multi-POM workflows only save 1 file (Step 10 bug)

---

## Task Dependencies

```
1.0 Audit Trail ──────┐
                      │
2.0 Self-Heal Cap ────┤
                      ├──► 7.0 Production Fixes ──► 6.0 E2E Verification
2.5 Execution Mode ───┤
                      │
3.0 License/Docs ─────┘

4.0 Smoke Test ─────────► Independent (parallel OK, blocked by 7.0)

5.0 Adversarial ────────► Independent (parallel OK, blocked by 7.0)
```

**CRITICAL:** Task 7.0 MUST complete before Tasks 4.0, 5.0, 6.0 can succeed.
- Multi-page workflows are broken without Task 7.0 fixes
- Production test demonstrated all 3 bugs block real workflows

---

## Commands (to be filled during execution)

```bash
# Task 1.0 - Audit Trail
# python -m pytest mcp_server/_dev_tests/test_audit_logger.py -v
# Result:

# Task 2.0 - Self-Heal Cap
# python -m pytest mcp_server/_dev_tests/test_self_heal_cap.py -v
# Result:

# Task 6.0 - E2E
# Full workflow execution
# Result:
```

---

*Task list generated from PRD using 4D Framework Phase 2.*
