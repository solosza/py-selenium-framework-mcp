# PRD: Step 11 - HITL Execution Gate

**Project:** step-11-hitl-execution-gate
**Phase:** Define (4D Framework - Phase 2)
**Date:** 2026-01-13
**Status:** DRAFT
**Version:** 1.0

---

## 1. Introduction/Overview

### Problem Statement

The current 11-step QA workflow generates architecturally correct code (all quality gates pass) but does NOT validate that generated tests actually execute successfully. This creates a critical gap: users complete the workflow, see "all gates passed," commit code, then discover their test fails at runtime (DEF-058).

**Real-world example:**
- User generates test for ParaBank login
- Steps 1-11 pass (code structure perfect)
- User commits code
- User runs test → FAILS (`AssertionError: Should be on account overview page`)
- Playwright finds element immediately, Selenium times out
- User spent time debugging what should have been caught automatically

### The Gap

```
Current State (Steps 1-11):
✅ Code structure validated (locators, patterns, methods)
✅ Architecture enforced (4-layer, composition, no inheritance)
✅ Quality gates passed (DD-25, DD-27, DD-49 all enforced)
❌ Test execution NOT validated
❌ Runtime failures NOT caught
❌ User discovers broken test AFTER workflow complete

Gap: Structure ≠ Execution
```

### Solution: Step 11 - Execution Validation Gate

Step 11 extends the workflow to validate test execution and enables human-in-the-loop (HITL) triage when tests fail:

1. **Mandatory test execution** - Test must pass before workflow completes
2. **Diagnostic data capture** - Provides context for failure analysis
3. **QA triage workflow** - Human determines: application defect vs test code issue
4. **AI-assisted fixes** - When test is wrong, AI fixes code with human guidance
5. **Quality re-validation** - Fixed code must pass relevant gates
6. **Test retry** - Re-run test after fixes applied
7. **Cross-step consistency** - Meta-gate validates entire 11-step workflow integrity

**Critical principle:** Test failures require human judgment. Only a test engineer can determine if a failure indicates an application bug (test is correct) or a test code issue (test is wrong).

---

## 2. Goals

### Primary Goals

1. **Close DEF-058 Gap** - Catch test execution failures before user sees them
2. **Prove AI Management Layer Thesis** - Demonstrate execution enforcement (not just structure)
3. **Enable QA Triage Workflow** - Distinguish app bugs from test issues systematically
4. **Maintain Code Quality** - Ensure fixes maintain framework patterns (4-layer architecture)

### Success Metrics

**Functional:**
- ✅ 100% of test failures caught before workflow completion
- ✅ 0 "all gates passed" scenarios with broken tests
- ✅ HITL triage workflow completes in < 5 minutes for simple failures
- ✅ Code fixes pass all relevant quality gates before re-run

**Quality:**
- ✅ Backward compatible (existing 11-step workflows unaffected)
- ✅ Audit trail captures Step 11 data (test results, triage decisions, fixes)
- ✅ Cross-step consistency validated (no orphaned state, correct test run)

**Performance:**
- ✅ Step 11 execution < 2 minutes (test run + triage presentation)
- ✅ Gate validation < 5 seconds per gate
- ✅ Total workflow time increase: < 10% over current 11-step flow

---

## 3. User Stories

### US-1: QA Engineer - Test Execution Validation
**As a** QA engineer using the QA Execution Engine
**I want** the workflow to automatically run my generated test before completion
**So that** I don't commit broken tests and waste time debugging later

**Acceptance Criteria:**
- Test executes automatically after Step 10 completes
- Test results captured in audit trail
- Workflow only completes if test passes
- Clear feedback on test success/failure

### US-2: QA Engineer - Application Bug Detection
**As a** QA engineer
**I want** to triage test failures to determine if they're application bugs
**So that** I can log legitimate defects without fixing correct tests

**Acceptance Criteria:**
- When test fails, I see diagnostic data (error, page state, expected vs actual)
- I can choose "Application defect" option
- System logs defect entry
- Workflow stops (doesn't attempt to fix test)
- I retain control over defect management

### US-3: QA Engineer - Test Issue Resolution
**As a** QA engineer
**I want** AI to help fix test code issues when I determine test is wrong
**So that** I can quickly correct tests without manual debugging

**Acceptance Criteria:**
- When test fails, I see AI's suggested cause with confidence level
- I can choose "Test issue" option
- AI presents fix options with tradeoffs
- I can provide free-text guidance for fixes
- Fixed code passes all quality gates before re-run
- Test re-runs automatically after fixes validated

### US-4: QA Engineer - Investigation Support
**As a** QA engineer
**I want** to investigate complex failures before deciding
**So that** I make informed triage decisions

**Acceptance Criteria:**
- I can choose "Investigate further" option
- System provides full diagnostic data:
  - Test execution output
  - Page state snapshot
  - Browser context
  - Expected vs actual values
  - Test data used
  - Execution flow trace
- I can return to triage after investigation
- Workflow pauses during investigation (no timeout)

### US-5: Developer - Backward Compatibility
**As a** developer maintaining existing workflows
**I want** Step 11 to not break existing 11-step workflows
**So that** I don't have to update working code

**Acceptance Criteria:**
- Old state files (steps 1-10) remain readable
- Old audit files (steps 1-10) remain valid
- StateManager accepts both 11-step and 11-step data
- Existing tests pass without modification

---

## 4. Functional Requirements

### FR-11.1: Test Execution (Operation Tool)

**Tool:** `run_test`
**Type:** MCP Operation Tool
**Purpose:** Execute pytest with consistent parameters

**FR-11.1.1** - The system MUST provide a `run_test` MCP tool that executes pytest
**FR-11.1.2** - The tool MUST accept `test_path` parameter (required)
**FR-11.1.3** - The tool MUST accept `env` parameter (optional, defaults to "DEFAULT")
**FR-11.1.4** - The tool MUST execute pytest with required flags:
- `-v` (verbose output)
- `--html={report_path}` (HTML report)
- `--self-contained-html` (single-file report)
- `--env={env}` (environment config)

**FR-11.1.5** - The tool MUST return structured results:
```python
{
    "status": "passed" | "failed",
    "exit_code": int,
    "output": str,  # Full pytest output
    "duration": float,  # Seconds
    "report_path": str,  # HTML report location
    "failed_assertion": str,  # If failed
    "stack_trace": str  # If failed
}
```

**FR-11.1.6** - The tool MUST capture both stdout and stderr
**FR-11.1.7** - The tool MUST handle pytest crashes gracefully (non-zero exit codes)
**FR-11.1.8** - The tool MUST NOT auto-fix failures (operation only, no validation logic)

### FR-11.2: Execution Validation (Quality Gate)

**Tool:** `qg_execution`
**Type:** MCP Quality Gate
**Purpose:** Validate test execution results and enable HITL triage

**FR-11.2.1** - The gate MUST validate test execution completed (not skipped)
**FR-11.2.2** - The gate MUST validate test status is "passed"
**FR-11.2.3** - If test passed, gate returns PASS response with metadata
**FR-11.2.4** - If test failed, gate returns FAIL response with diagnostic data

**FR-11.2.5** - Diagnostic data MUST include (7 MVP data types):
1. **Test Execution** - pytest output, exit code, duration, report path
2. **Page State** - Playwright snapshot of page at failure point
3. **Browser Context** - URL, cookies, localStorage, sessionStorage
4. **Expected vs Actual** - Assertion values (expected, actual, comparison)
5. **Test Context** - Test file, test function, line number, fixtures used
6. **Test Data** - Credentials used, workflow parameters, test inputs
7. **Execution Flow** - Stack trace, framework method calls, navigation history

**FR-11.2.6** - Playwright snapshot MUST run automatically on test failure
**FR-11.2.7** - Diagnostic data MUST be versioned (v1 MVP, v2 future enhancements)

**FR-11.2.8** - AI presentation MUST be SUGGESTIVE:
- Analyze diagnostic data
- Suggest likely cause with confidence level (0-100%)
- Present as hypothesis, not classification
- Show supporting evidence from diagnostic data

**FR-11.2.9** - Human input MUST be HYBRID:
- AI provides 3 triage options:
  1. Application defect (log defect, stop workflow)
  2. Test issue (AI fixes test code)
  3. Investigate further (show full diagnostic data)
- User can select option OR provide free-text guidance

**FR-11.2.10** - Triage presentation format:
```
Test Failed: test_login_and_view_account_overview

Error: AssertionError: Should be on account overview page
Line: tests/parabank8/test_login_and_view_account_overview.py:48

AI Analysis (Confidence: 75%):
Likely cause: Element locator timing issue
- Selenium times out after 5s waiting for element
- Playwright finds element immediately (0.1s)
- Element exists but may require explicit wait

Evidence:
- Locator: //h1[text()='Accounts Overview']
- Playwright snapshot shows element present
- Selenium wait timeout: 5s (may be insufficient)

Suggested fix: Increase timeout or add explicit wait condition

How should we proceed?
1. Application defect - Test is correct, app behavior unexpected
2. Test issue - Fix test code (locator/timing/logic)
3. Investigate - Show full diagnostic data before deciding
> _
```

**FR-11.2.11** - If user selects "Application defect":
- Log defect entry to DEFECT_LOG.md
- Stop workflow (do not attempt fixes)
- Save Step 11 state with triage decision
- Return FAIL response (blocking gate)

**FR-11.2.12** - If user selects "Test issue":
- Proceed to fix workflow (FR-11.3)
- AI generates fix based on triage decision
- Fixed code validated through dependency-aware gates
- Test re-runs after validation

**FR-11.2.13** - If user selects "Investigate":
- Display full diagnostic data (all 7 types)
- User reviews data
- User returns to triage options
- No timeout during investigation

### FR-11.3: Code Fix Validation (Dependency-Aware)

**FR-11.3.1** - When code is modified, system MUST determine dependency chain:
- POM modified → Re-validate: qg_page_object → qg_task → qg_role → qg_test_runner
- Task modified → Re-validate: qg_task → qg_role → qg_test_runner
- Role modified → Re-validate: qg_role → qg_test_runner
- Test modified → Re-validate: qg_test_runner

**FR-11.3.2** - All gates in chain MUST use POST mode validation
**FR-11.3.3** - Gates MUST validate code against smart gate patterns:
- No skeleton code (DD-25)
- No locators in Tasks (DD-27)
- Navigation only in POMs (DD-49)
- Correct orchestration calls
- Interface contracts maintained

**FR-11.3.4** - If any gate fails ≥3 times, escalate to human:
- Show gate failure history
- Present options: retry, modify approach, abort
- User decides next step

**FR-11.3.5** - Metadata MUST be regenerated from modified code:
- Extract class names, method names, import paths
- Update workflow state with new metadata
- Ensure metadata matches actual code

### FR-11.4: Retry Policy (Loop Prevention)

**FR-11.4.1** - System MUST track error signatures across attempts
**FR-11.4.2** - Same error 2x in a row → Ask human for guidance
**FR-11.4.3** - Total 5 attempts reached → Confirm with human before continuing
**FR-11.4.4** - Different errors each attempt → Continue (indicates progress)
**FR-11.4.5** - No time limits (HITL controls pacing)
**FR-11.4.6** - Human can abort anytime via triage options

**Confirmation dialog (at 5 attempts):**
```
Step 11 has attempted 5 fixes with different errors each time.

Attempts so far:
1. Changed locator to CSS → Still failed (timing issue)
2. Increased timeout → Still failed (wrong page)
3. Added navigation step → Still failed (state issue)
4. Fixed preconditions → Still failed (different locator)
5. Tried alternative locator → Still failed (visibility)

Continue trying or abort workflow?
1. Continue (try more approaches)
2. Mark as application defect
3. Abort workflow (manual investigation needed)
> _
```

### FR-11.5: Workflow Completion Validation (Meta-Gate)

**Tool:** `qg_workflow_complete`
**Type:** MCP Meta-Gate
**Purpose:** Validate 11-step workflow integrity

**FR-11.5.1** - Gate MUST validate 8 cross-step consistency checks:

| Check | Validation | Failure Scenario |
|-------|------------|------------------|
| Test path consistency | Step 9 test == Step 11 test | Generated test_login.py, ran test_checkout.py |
| File existence | All files from Steps 6-9 exist | POM file missing on disk |
| Import path validity | All import paths work | Role imports Task from wrong path |
| Workflow ID consistency | Same workflow_id across all steps | Step 5 used "parabank7", Step 11 used "parabank8" |
| Audit trail complete | All 11 steps logged | Step 7 missing from audit log |
| State completeness | All required metadata present | pom_metadata missing after fixes |
| Code modifications tracked | Step 11 changes recorded | Modified POM but no audit record |
| No orphaned state | Clean state, no partial failures | Previous workflow artifacts in state |

**FR-11.5.2** - Gate runs AFTER test passes (final validation)
**FR-11.5.3** - Gate failure → Escalate to human (NOT auto-restart)
**FR-11.5.4** - Escalation options:
1. Re-run Step 11 (specific test issue)
2. Restart workflow (fundamental inconsistency)
3. Accept as-is (known issue, proceed anyway)
4. Abort (manual investigation needed)

**FR-11.5.5** - Gate MUST provide specific failure context:
- Which check failed
- What inconsistency detected
- Where to look (file paths, line numbers)
- Suggested fix approach

### FR-11.6: State Persistence and Audit Trail

**FR-11.6.1** - Step 11 state MUST be saved to workflow state:
```json
{
  "step": 11,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "test_result": {
      "status": "passed",
      "duration": 2.3,
      "attempts": 1
    },
    "triage_history": [
      {
        "attempt": 1,
        "failure": "AssertionError: Should be on account overview page",
        "triage_decision": "test_issue",
        "fix_applied": "Increased timeout from 5s to 10s",
        "result": "passed"
      }
    ]
  }
}
```

**FR-11.6.2** - Audit trail MUST use hybrid strategy:
- **Summary:** In main workflow audit file (tests/_audit/{timestamp}_{workflow}.json)
- **Detail:** In separate Step 11 audit file (tests/_audit/step11/{run_id}_diagnostic.json)

**FR-11.6.3** - Detailed audit MUST include:
- Full diagnostic data (all 7 types)
- Triage decisions with timestamps
- Fix attempts with code diffs
- Gate re-validation results
- Final test execution result

**FR-11.6.4** - Audit data MUST be compressed (strip code, keep metadata only)
**FR-11.6.5** - Learning patterns (v2 future enhancement - data structure supports)

### FR-11.7: StateManager Extension

**FR-11.7.1** - StateManager MUST extend VALID_STEPS:
```python
# BEFORE
VALID_STEPS = range(1, 11)  # 1-10 inclusive

# AFTER
VALID_STEPS = range(1, 12)  # 1-11 inclusive
```

**FR-11.7.2** - StateManager MUST accept step 11 data in save()
**FR-11.7.3** - StateManager MUST return step 11 data in get_step(11)
**FR-11.7.4** - StateManager MUST maintain backward compatibility (old 11-step files readable)

### FR-11.8: MCP Server Registration

**FR-11.8.1** - MCP server MUST register 3 new tools:
```python
# Operation tool
async def run_test(arguments: dict) -> str

# Quality gates
async def qg_execution(arguments: dict) -> str
async def qg_workflow_complete(arguments: dict) -> str
```

**FR-11.8.2** - Tools MUST be exported from `mcp_server/tools/gates/__init__.py`
**FR-11.8.3** - Tool registration MUST follow existing pattern (async, JSON serialization)

---

## 5. Non-Goals (Out of Scope)

### MVP Exclusions

❌ **Auto-fix without HITL** - All fixes require human triage decision
❌ **ML-based failure classification** - Use rule-based analysis (v1)
❌ **Historical learning** - Track patterns across workflows (v2)
❌ **Performance optimization** - Parallel test execution (v2)
❌ **Multi-test orchestration** - Single test only (v1)
❌ **CI/CD integration** - Local execution only (v1)
❌ **Visual regression testing** - Functional tests only (v1)
❌ **Advanced reporting** - Basic audit trail (v1)
❌ **Self-healing locators** - Human decides fixes (v1)
❌ **Test data generation** - Use existing test data strategies (v1)

### Explicit Boundaries

- Step 11 does NOT replace Step 10 (both are necessary)
- Step 11 does NOT modify test execution (uses pytest as-is)
- Step 11 does NOT enforce test writing patterns (that's Step 9's job)
- Step 11 does NOT auto-classify failures (human triages)

---

## 6. Technical Considerations

### Architecture

**Pattern:** Smart Gate + HITL Integration
- Smart gates provide fix data (not just errors)
- HITL enables human judgment at critical decision points
- Dependency-aware validation maintains code quality

**Integration Points:**
- **StateManager** - Extends to support step 11 data
- **AuditLogger** - Automatically logs Step 11 via PostToolUse hook
- **Quality Gates** - Re-validates code after fixes (qg_page_object, qg_task, qg_role, qg_test_runner)
- **Pytest** - Executes tests via subprocess, captures output
- **Playwright** - Captures page snapshots on failure

### Dependencies

**Existing:**
- Python 3.x
- Selenium WebDriver
- Pytest + pytest-html
- Playwright (for snapshots)
- MCP server infrastructure
- Quality gate framework

**New:**
- None (uses existing stack)

### Technical Constraints

**MUST work with:**
- Existing 11-step workflow (backward compatible)
- Current quality gate pattern (qg_* naming)
- State management system (StateManager)
- Pytest test runner (no custom runner)
- Both Selenium and Playwright

**CANNOT:**
- Break existing Steps 1-11
- Require new dependencies
- Change established patterns (DD-25, DD-27, DD-49)
- Add significant latency (< 2 min for Step 11)

### Implementation Notes

**Critical Decisions:**
1. **Step 11 is NOT a Smart Gate** - It's a QA triage workflow requiring human judgment
2. **Dependency-aware re-validation** - Follow full 4-layer chain when code modified
3. **Metadata regeneration** - Extract from modified code, update workflow state
4. **Hybrid audit** - Summary in workflow audit, detail in separate file
5. **Error signature tracking** - Detect same vs different errors for retry logic

---

## 7. Design Considerations

### UI/UX Elements

**Triage Presentation (Console Output):**
```
╔══════════════════════════════════════════════════════════════════════╗
║                      TEST EXECUTION FAILED                            ║
╚══════════════════════════════════════════════════════════════════════╝

Test: test_login_and_view_account_overview
File: tests/parabank8/test_login_and_view_account_overview.py:48

Error: AssertionError: Should be on account overview page

────────────────────────────────────────────────────────────────────────
AI ANALYSIS (Confidence: 75%)
────────────────────────────────────────────────────────────────────────

Likely Cause: Element locator timing issue

Evidence:
  • Locator: //h1[text()='Accounts Overview']
  • Playwright finds element immediately (0.1s)
  • Selenium timeout after 5s
  • Element exists on page (verified via snapshot)

Suggested Fix: Increase explicit wait timeout or add wait condition

────────────────────────────────────────────────────────────────────────
TRIAGE OPTIONS
────────────────────────────────────────────────────────────────────────

1. Application Defect
   → Test is correct, application behavior unexpected
   → Logs defect to DEFECT_LOG.md
   → Stops workflow (no fix attempt)

2. Test Issue
   → Fix test code (locator/timing/logic)
   → AI suggests fixes, you guide
   → Re-validates code quality before retry

3. Investigate Further
   → View full diagnostic data (7 types)
   → Analyze before deciding
   → Return to triage after review

Enter your choice (1/2/3) or provide custom guidance:
> _
```

**Progress Feedback:**
```
[Step 11] Running test...
[Step 11] Test execution complete (2.3s)
[Step 11] ✅ Test PASSED
[Step 11] Validating workflow integrity...
[Step 11] ✅ All consistency checks passed
[Step 11] Workflow COMPLETE
```

**Fix Workflow Feedback:**
```
[Step 11] Applying fix: Increase timeout to 10s
[Step 11] Validating modified POM...
[Step 11] ✅ qg_page_object PASSED
[Step 11] ✅ qg_task PASSED
[Step 11] ✅ qg_role PASSED
[Step 11] ✅ qg_test_runner PASSED
[Step 11] Re-running test...
[Step 11] ✅ Test PASSED
[Step 11] Workflow COMPLETE
```

### Error Messages

**Gate Failure Example:**
```
❌ qg_workflow_complete FAILED

Check Failed: Test path consistency
Expected: tests/parabank8/test_login_and_view_account_overview.py
Actual:   tests/parabank7/test_login.py

This indicates Step 11 ran the wrong test.

Fix: Verify workflow_id consistency across all steps.
Check state data for steps 9 and 11.

Options:
1. Re-run Step 11 with correct test
2. Restart workflow from Step 1
3. Accept as-is (if intentional)
4. Abort workflow

Enter your choice (1/2/3/4):
> _
```

---

## 8. Test Strategy

### Unit Tests

**Location:** `mcp_server/_dev_tests/test_gates/`

**Coverage:**
- `test_qg_execution.py` - Test execution gate validation logic
  - Test passed scenario → PASS response
  - Test failed scenario → FAIL response with diagnostic data
  - Diagnostic data structure validation
  - Triage option handling
  - Error signature tracking
- `test_qg_workflow_complete.py` - Meta-gate validation logic
  - All 8 consistency checks (pass/fail scenarios)
  - Cross-step data validation
  - Escalation option handling
- `test_run_test.py` - Test execution operation
  - Pytest execution with correct flags
  - Output capture (stdout/stderr)
  - Exit code handling
  - Report path generation

**Tools:** pytest, mocking (unittest.mock)

**Mocking Policy:**
- Mock pytest subprocess calls (don't run actual tests)
- Mock Playwright snapshot capture
- Mock StateManager for isolation
- Use fixtures for test data

### Integration Tests

**Location:** `mcp_server/_dev_tests/test_gates/test_integration.py`

**Scenarios:**
- Full Step 11 workflow (run_test → qg_execution → qg_workflow_complete)
- Test failure → triage → fix → re-validate → re-run
- Dependency-aware re-validation (POM fix triggers full chain)
- Audit trail capture (PostToolUse hook integration)
- StateManager step 11 data persistence

**Tools:** pytest with real StateManager, mock subprocess

### End-to-End Tests

**Location:** `mcp_server/_dev_tests/test_step11_e2e.py`

**Scenarios:**
- **Happy path:** 11-step workflow, test passes on first run
- **Test failure - app bug:** Test fails, user selects "Application defect", workflow stops
- **Test failure - test issue:** Test fails, user selects "Test issue", AI fixes, test passes
- **Gate failure:** qg_workflow_complete detects inconsistency, escalates to user
- **Backward compatibility:** Old 11-step state files still readable

**Tools:** pytest, real MCP server, Playwright (for actual test execution)

### Test Data

**Fixtures:**
```python
# tests/data/step11_test_fixtures.json
{
  "test_passed": {
    "status": "passed",
    "exit_code": 0,
    "output": "1 passed in 2.3s",
    "duration": 2.3
  },
  "test_failed": {
    "status": "failed",
    "exit_code": 1,
    "output": "AssertionError: Should be on account overview page",
    "duration": 2.1,
    "failed_assertion": "Should be on account overview page",
    "stack_trace": "..."
  }
}
```

---

## 9. Acceptance Tests (GIVEN/WHEN/THEN)

### AT-1: Test Execution Success

**GIVEN** the 11-step workflow completed successfully
**AND** all generated files exist
**WHEN** Step 11 executes the test
**AND** the test passes on first attempt
**THEN** qg_execution returns PASS
**AND** qg_workflow_complete validates consistency
**AND** workflow completes with status "complete"
**AND** audit trail includes Step 11 data

### AT-2: Test Execution Failure - Application Defect

**GIVEN** Step 11 executes the test
**AND** the test fails with assertion error
**WHEN** AI presents triage options
**AND** user selects "Application defect"
**THEN** system logs defect to DEFECT_LOG.md
**AND** qg_execution returns FAIL (blocking)
**AND** workflow stops (no fix attempt)
**AND** Step 11 state saved with triage decision

### AT-3: Test Execution Failure - Test Issue with Fix

**GIVEN** Step 11 executes the test
**AND** the test fails with locator timeout
**WHEN** user selects "Test issue"
**AND** AI suggests increasing timeout
**AND** user confirms fix
**THEN** AI modifies POM code (increase timeout)
**AND** system re-validates via qg_page_object (POST)
**AND** system re-validates via qg_task, qg_role, qg_test_runner (POST)
**AND** all gates pass
**AND** test re-runs and passes
**AND** qg_execution returns PASS
**AND** workflow completes

### AT-4: Dependency-Aware Re-Validation (POM Fix)

**GIVEN** test failed due to POM locator issue
**AND** user selected "Test issue"
**WHEN** AI modifies POM locator
**THEN** system determines dependency chain: POM → Task → Role → Test
**AND** system re-runs qg_page_object POST validation
**AND** system re-runs qg_task POST validation
**AND** system re-runs qg_role POST validation
**AND** system re-runs qg_test_runner POST validation
**AND** all gates pass
**AND** metadata regenerated from modified code

### AT-5: Same Error Retry Limit

**GIVEN** test fails with error "Element not found"
**AND** AI attempts fix (increase timeout)
**AND** test re-runs and fails with SAME error
**WHEN** retry count = 2 for same error
**THEN** system asks human for guidance
**AND** presents options: try different approach, mark as app defect, abort
**AND** waits for human decision (no auto-retry)

### AT-6: Total Attempt Limit

**GIVEN** test has been retried 5 times
**AND** each attempt had DIFFERENT error
**WHEN** attempt count reaches 5
**THEN** system confirms with human before continuing
**AND** presents attempt history
**AND** offers options: continue, mark as app defect, abort
**AND** human decides whether to proceed

### AT-7: qg_workflow_complete - Test Path Consistency

**GIVEN** Step 9 generated test: `tests/parabank8/test_login.py`
**AND** Step 11 is about to run
**WHEN** qg_workflow_complete validates workflow
**AND** Step 11 ran test: `tests/parabank7/test_checkout.py` (wrong test)
**THEN** qg_workflow_complete returns FAIL
**AND** error: "Test path consistency check failed"
**AND** shows expected vs actual test paths
**AND** escalates to human for decision

### AT-8: qg_workflow_complete - File Existence

**GIVEN** Step 6 generated POM: `framework/pages/auth/login_page.py`
**AND** Step 10 reported file saved
**WHEN** qg_workflow_complete validates workflow
**AND** file does NOT exist on disk
**THEN** qg_workflow_complete returns FAIL
**AND** error: "File existence check failed"
**AND** shows missing file path
**AND** suggests checking Step 6 POST validation

### AT-9: Backward Compatibility - Old State Files

**GIVEN** existing workflow state file with steps 1-10
**AND** StateManager with VALID_STEPS = range(1, 12)
**WHEN** system reads old state file
**THEN** StateManager successfully loads steps 1-10
**AND** get_step(1) through get_step(10) return data
**AND** get_step(11) returns None (not present)
**AND** no errors or crashes

### AT-10: Audit Trail Capture

**GIVEN** Step 11 executes and completes
**WHEN** qg_execution returns PASS
**THEN** PostToolUse hook captures gate result
**AND** main audit file updated with Step 11 summary
**AND** detailed audit file created: `tests/_audit/step11/{run_id}_diagnostic.json`
**AND** detailed audit contains all 7 diagnostic data types
**AND** code stripped from audit (metadata only)

---

## 10. Non-Functional Requirements (SLAs)

### Performance

**P-1: Test Execution Time**
- Target: < 30 seconds per test execution (depends on test)
- Measurement: Time from run_test invocation to result return
- Verification: E2E tests measure duration, assert < 30s for simple tests

**P-2: Gate Validation Time**
- Target: < 5 seconds per gate validation
- Measurement: Time from gate invocation to pass/fail response
- Verification: Unit tests measure gate.validate() duration

**P-3: Total Step 11 Overhead**
- Target: < 2 minutes for complete Step 11 (test + triage + validation)
- Measurement: Time from Step 10 complete to Step 11 complete
- Verification: E2E tests measure full Step 11 duration

**P-4: Workflow Time Impact**
- Target: < 10% increase over current 11-step workflow
- Baseline: Current workflow ~5 minutes (Steps 1-11)
- With Step 11: ~5.5 minutes total
- Verification: Compare E2E test times (11-step vs 11-step)

### Retry/Backoff

**R-1: No Automatic Backoff**
- HITL controls retry timing (human decides when to retry)
- No exponential backoff or automatic delays
- System waits for human input before each retry

**R-2: Retry Limits**
- Same error: 2 attempts max before human intervention
- Total attempts: 5 attempts max before human confirmation
- No time limits (human can take as long as needed)

### Error Handling

**E-1: Pytest Crashes**
- Handle non-zero exit codes gracefully
- Capture stderr for diagnostic data
- Present to user as test infrastructure failure
- Do not auto-retry (human decides)

**E-2: Gate Validation Failures**
- After 3 gate failures, escalate to human
- Present gate failure history
- Offer: retry, modify approach, abort
- Do not loop indefinitely

**E-3: StateManager Failures**
- If state write fails, log error and abort
- Do not proceed with incomplete state
- Preserve previous state (atomic writes)

**E-4: Audit Logger Failures**
- If audit write fails, log warning but continue
- Audit failures should not block workflow
- Attempt retry once, then proceed

### Observability/Telemetry

**O-1: Gate Execution Events**
- Log: Gate name, mode, result, duration
- Format: `[Step 11] qg_execution POST: PASS (1.2s)`
- Destination: Console output + audit trail

**O-2: Triage Decisions**
- Log: Decision type, timestamp, user input
- Format: `[Step 11] Triage decision: test_issue (timeout fix)`
- Destination: Step 11 detail audit file

**O-3: Code Fix Applications**
- Log: Modified file, change description, result
- Format: `[Step 11] Modified: login_page.py (timeout 5s → 10s)`
- Destination: Step 11 detail audit file

**O-4: Test Execution Results**
- Log: Test path, status, duration, attempt number
- Format: `[Step 11] Test: test_login.py, Status: PASSED, Duration: 2.3s, Attempt: 2`
- Destination: Main audit file + Step 11 detail

**Verification:**
- E2E tests assert log entries exist
- Audit trail validation checks required fields
- No hardcoded log format (use structured logging)

### Security & Privacy

**S-1: No Secrets in Logs**
- Strip credentials from diagnostic data
- Replace with placeholders: `[REDACTED]`
- Apply to: test_users.json data, environment variables

**S-2: No Secrets in Audit Files**
- Audit files stored in tests/_audit/ (gitignored)
- Code stripped from audit (metadata only)
- Credentials replaced with `[REDACTED]`

**S-3: Subprocess Security**
- pytest executed via subprocess.run() with explicit args
- No shell=True (prevents injection)
- Test path validated before execution

**S-4: File Path Validation**
- Validate test_path parameter against project root
- Reject paths outside tests/ directory
- Prevent directory traversal attacks

**Verification:**
- Unit tests attempt injection attacks (assert blocked)
- Audit trail inspection confirms no secrets present
- Security review of subprocess calls

### Rollout & Rollback

**Feature Flag:** `STEP_11_ENABLED` (environment variable)
- Default: `false` (opt-in for MVP)
- Set to `true` to enable Step 11
- If false, workflow ends at Step 10 (current behavior)

**Rollout Plan:**
1. **Phase 1 (Week 1):** Internal testing only (developers)
2. **Phase 2 (Week 2):** Alpha users (3-5 friendly QA engineers)
3. **Phase 3 (Week 3):** Beta users (10-15 QA engineers)
4. **Phase 4 (Week 4):** General availability (default enabled)

**Rollback Procedure:**
1. Set `STEP_11_ENABLED=false` in environment
2. Restart MCP server
3. Workflow reverts to 11-step behavior
4. Old state files remain valid (backward compatible)

**Smoke Test (Rollback Validation):**
```python
def test_step_11_disabled():
    """Verify workflow ends at Step 10 when feature disabled."""
    os.environ["STEP_11_ENABLED"] = "false"

    # Run workflow
    result = run_11_step_workflow(...)

    # Assert ends at Step 10
    assert result["last_step"] == 10
    assert "step_11" not in result["state"]

    # Cleanup
    del os.environ["STEP_11_ENABLED"]
```

---

## 11. Success Metrics

### Functional Success

**FS-1:** 100% of test failures caught before workflow completion
- Measurement: E2E tests with intentionally failing tests
- Success: All failures trigger Step 11 triage

**FS-2:** 0 "all gates passed" scenarios with broken tests
- Measurement: Manual testing + user reports
- Success: No user commits broken test after workflow completes

**FS-3:** HITL triage workflow completes < 5 minutes (simple failures)
- Measurement: Time from test failure to triage decision
- Success: 90% of simple failures triaged within 5 minutes

**FS-4:** Code fixes pass all gates before re-run
- Measurement: E2E tests with test_issue triage path
- Success: 100% of fixes pass relevant gates

### Quality Success

**QS-1:** Backward compatible (existing workflows unaffected)
- Measurement: Run existing test suite with Step 11 enabled
- Success: All existing tests pass without modification

**QS-2:** Audit trail captures Step 11 data
- Measurement: Inspect audit files after Step 11 execution
- Success: Step 11 summary in main audit, detail in separate file

**QS-3:** Cross-step consistency validated
- Measurement: qg_workflow_complete tests
- Success: All 8 consistency checks enforce correctness

### Performance Success

**PS-1:** Step 11 execution < 2 minutes
- Measurement: E2E test duration (Step 10 → Step 11 complete)
- Success: 95th percentile < 2 minutes

**PS-2:** Gate validation < 5 seconds
- Measurement: Unit test duration (gate.validate() calls)
- Success: 99th percentile < 5 seconds

**PS-3:** Total workflow increase < 10%
- Measurement: 11-step workflow vs 11-step workflow duration
- Success: Average increase < 10% (5 min → 5.5 min)

---

## 12. Open Questions

### Resolved During Design Phase

✅ **Q1:** How much diagnostic data to capture?
**A:** 7 MVP data types (v1), 4 additional for v2 (extensible structure)

✅ **Q2:** Should AI auto-classify failures?
**A:** No. AI suggests (SUGGESTIVE), human decides (HITL)

✅ **Q3:** How to validate fixed code?
**A:** Dependency-aware re-validation (follow 4-layer chain)

✅ **Q4:** When to stop retrying?
**A:** 2 same-error attempts OR 5 total attempts (confirm with human)

✅ **Q5:** Where to store detailed audit data?
**A:** Hybrid (summary in main audit, detail in tests/_audit/step11/)

✅ **Q6:** Should Step 11 be a single gate or multiple tools?
**A:** Three-tool architecture (run_test, qg_execution, qg_workflow_complete)

### Remaining Questions

❓ **Q7:** Should Playwright snapshots be compressed or stored as-is?
**Impact:** Disk space usage, audit file size
**Decision needed:** Before implementation starts

❓ **Q8:** Should retry limit be configurable or hardcoded?
**Impact:** User flexibility vs complexity
**Decision needed:** During Phase 3 (task breakdown)

❓ **Q9:** Should qg_workflow_complete run before or after test passes?
**Impact:** When consistency checks happen
**Tentative:** After test passes (validate complete workflow)

---

## 13. Definition of Ready

Step 11 PRD is ready for Phase 3 (Task Generation) when:

- ✅ All functional requirements documented (FR-11.1 through FR-11.8)
- ✅ Test strategy defined (unit, integration, E2E)
- ✅ At least 10 acceptance tests specified (AT-1 through AT-10)
- ✅ Non-functional SLAs documented (performance, error handling, security)
- ✅ Rollout/rollback plan defined with smoke test
- ✅ Impact assessment complete (see impact-assessment.md)
- ✅ Design decisions documented (see 1-design-step-11-hitl-execution-gate.md)
- ✅ Open questions reviewed (2 resolved, 3 remain for implementation)

**Status:** ✅ READY FOR PHASE 3 (Task Generation)

---

**Document Status:** DRAFT v1.0
**Next Phase:** Generate task breakdown (Phase 3)
**Blocking Issues:** None (all critical decisions made)
