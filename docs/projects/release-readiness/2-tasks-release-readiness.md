# Task List: Release Readiness

**Version:** 1.0
**Created:** 2025-12-27
**PRD:** `1-prd-release-readiness.md`
**Branch:** `feature/release-readiness`

---

## Relevant Files

### Audit Trail (Task 1.0)
- `mcp_server/utils/audit_logger.py` - NEW: Audit log writer class
- `mcp_server/state/` - Directory for `audit_log_{timestamp}.json` files
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

### License & Documentation (Task 3.0)
- `.claude/skills/qa-guidance-layer/SKILL.md` - Add license header
- `.claude/skills/qa-guidance-layer/references/*.md` - Add license headers
- `.claude/skills/*/SKILL.md` - Add license headers to all skills
- `LICENSE.md` - NEW: Skills license terms
- `README.md` - Add installation guide section

### Validation (Tasks 4.0, 5.0)
- `SESSION.md` - Document smoke test results
- `docs/DEFECT_LOG.md` - Track any issues found

---

## Notes

- Tests for CORE tasks use pytest: `python -m pytest mcp_server/_dev_tests/`
- VALIDATION tasks don't produce code, they produce documentation
- Each parent task gets its own branch: `feature/<task-id>-short-name`

---

## Tasks

- [ ] **1.0 Audit Trail System** [CORE]
  - [ ] 1.1 Create branch `feature/1.0-audit-trail`
  - [ ] 1.2 **Invoke `testing` skill** - Follow TDD for CORE logic (Red-Green-Refactor)
  - [ ] 1.3 Write failing tests first for AuditLogger
  - [ ] 1.4 Create `mcp_server/utils/audit_logger.py` with AuditLogger class
    - `__init__(run_id)` - Initialize with timestamp-based run ID
    - `log_gate(step, gate_name, mode, result, error=None, source=None)` - Record gate call
    - `log_self_heal(step, attempt, error)` - Record self-heal attempt
    - `log_file_generated(path, step)` - Record file output
    - `get_summary()` - Return summary dict (total_steps, gates_passed, etc.)
    - `finalize()` - Write JSON file to `mcp_server/state/`
  - [ ] 1.5 Define audit log JSON schema matching PRD spec
  - [ ] 1.6 Add `_audit_logger` class variable to BaseGate
  - [ ] 1.7 Add `set_audit_logger(logger)` class method to BaseGate
  - [ ] 1.8 Update `pass_response()` to log gate pass if logger set
  - [ ] 1.9 Update `fail_response()` to log gate fail if logger set
  - [ ] 1.10 Run checks: `python -m pytest mcp_server/_dev_tests/test_audit_logger.py -v`
  - [ ] 1.11 **Audit: Verify testing skill conventions followed**
  - [ ] 1.12 Record results
  - [ ] 1.13 Commit: `feat: add audit trail system (Task 1.0)`

---

- [ ] **2.0 Self-Heal Cap Enforcement** [CORE]
  - [ ] 2.1 Create branch `feature/2.0-self-heal-cap`
  - [ ] 2.2 **Invoke `testing` skill** - Follow TDD for CORE logic (Red-Green-Refactor)
  - [ ] 2.3 Write failing tests first for attempt tracking and blocked status
  - [ ] 2.4 Add to StateManager:
    - `_attempt_counts: dict` - Per-step attempt tracking
    - `increment_attempt(step) -> int` - Increment and return count
    - `get_attempt_count(step) -> int` - Get current count
    - `reset_attempts(step)` - Reset on success
  - [ ] 2.5 Add to BaseGate:
    - `MAX_ATTEMPTS = 3` - Class constant
    - `blocked_response(step, attempts, errors)` - Return blocked status
  - [ ] 2.6 Update `qg_page_object.validate_post()`:
    - Check attempt count before validation
    - If >= MAX_ATTEMPTS, return blocked response
    - On fail, increment attempt and include in audit
    - On pass, reset attempts
  - [ ] 2.7 Update `qg_task.validate_post()` with same pattern
  - [ ] 2.8 Update `qg_role.validate_post()` with same pattern
  - [ ] 2.9 Update `qg_test_runner.validate_post()` with same pattern
  - [ ] 2.10 Integrate attempt logging with AuditLogger
  - [ ] 2.11 Run checks: `python -m pytest mcp_server/_dev_tests/test_self_heal_cap.py -v`
  - [ ] 2.12 **Audit: Verify testing skill conventions followed**
  - [ ] 2.13 Record results
  - [ ] 2.14 Commit: `feat: add self-heal cap enforcement (Task 2.0)`

---

- [ ] **3.0 License & Documentation** [GLUE]
  - [ ] 3.1 Create branch `feature/3.0-license-docs`
  - [ ] 3.2 **Invoke `documentation` skill** - Follow doc conventions
  - [ ] 3.3 Create license header template:
    ```
    <!-- LICENSE: Proprietary - Isagawa Corp -->
    <!-- You may USE this skill with Claude Code. -->
    <!-- You may NOT redistribute, modify, or create derivative works. -->
    <!-- See LICENSE.md for full terms. -->
    ```
  - [ ] 3.4 Add header to `.claude/skills/qa-guidance-layer/SKILL.md`
  - [ ] 3.5 Add header to all files in `.claude/skills/qa-guidance-layer/references/`
  - [ ] 3.6 Add header to all other skill directories (`dialogue-engine`, `testing`, etc.)
  - [ ] 3.7 Create `LICENSE.md` with full terms:
    - Grant: Use with Claude Code
    - Restrictions: No redistribution, no modification, no derivatives
    - Attribution: Isagawa Corp
  - [ ] 3.8 Update README.md with Installation Guide section:
    - Prerequisites (Python 3.x, pip)
    - Clone repository
    - Install dependencies
    - Copy skills to project
    - Configure MCP server
    - Quick start example
  - [ ] 3.9 **Audit: Verify all skill files have headers**
  - [ ] 3.10 Commit: `docs: add license headers and installation guide (Task 3.0)`

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

## Task Dependencies

```
1.0 Audit Trail ──────┐
                      ├──► 6.0 E2E Verification
2.0 Self-Heal Cap ────┤
                      │
3.0 License/Docs ─────┘

4.0 Smoke Test ─────────► Independent (parallel OK)

5.0 Adversarial ────────► Independent (parallel OK)
```

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
