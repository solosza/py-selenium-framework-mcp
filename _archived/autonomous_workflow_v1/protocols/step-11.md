<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 11: Execution & Validation

**Purpose:** Execute test, validate results with HITL triage for failures, and perform final workflow integrity checks.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 11 - Execution & Validation |
| **Dependencies** | Step 10 complete (all files saved to disk) |
| **Input** | Test files from Step 10, workflow state |
| **Output** | Test execution result, HITL triage decisions (if failure), workflow integrity report |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | Reviews test results, makes triage decisions on failures (app bug vs test issue) |
| **AI** | Executes test, captures diagnostic data, presents triage options, validates workflow integrity |
| **Tools** | `run_test` (execute pytest), `qg_execution` (validate results + HITL triage), `qg_workflow_complete` (8 consistency checks) |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 10 complete (all files saved)
- Verify test file path exists
- Verify workflow state has all metadata

ACTION (3-TOOL SEQUENCE):
1. CALL run_test with test_path
   - Executes pytest subprocess
   - **Browser ALWAYS visible (non-headless) for HITL observation**
   - Parameters: test_path (required), marker (optional)
   - Captures: status, exit_code, output, duration, failure_data
   - Returns test_result object

2. CALL qg_execution with test_result
   - IF test passed → return pass_response
   - IF test failed → HITL triage workflow:
     a. Capture 7 diagnostic data types
     b. Generate AI analysis (likely cause, confidence, evidence)
     c. Present triage options to user
     d. Wait for user decision
   - Returns pass (test passed) or fail (blocking until HITL decision)

3. CALL qg_workflow_complete with workflow_id, test_path, test_result
   - Runs 8 cross-step consistency checks
   - Validates 11-step workflow integrity
   - Returns pass (workflow complete) or fail (with escalation options)

VALIDATE:
- POST-only gates (no PRE validation for Step 11)
- qg_execution: Test result structure valid, triage workflow enforced on failure
- qg_workflow_complete: All 8 checks pass

HITL TRIAGE OPTIONS (on test failure):
User selects one of:
1. Application Defect - Log defect, block workflow (user fixes app)
2. Test Issue - AI investigates + fixes test code
3. Investigate - Show full diagnostic data, user analyzes

RETRY POLICY:
- Error signature tracking (MD5 hash of error location + message)
- Max 3 retries per unique error signature
- Flaky test detection (passes after retry)

COMPLETION CRITERIA:
- ✓ ONLY mark Step 11 complete if BOTH gates return pass_response:
  - qg_execution returns pass (test status = "passed")
  - qg_workflow_complete returns pass (all 8 checks pass)
- ✗ DO NOT mark complete if test fails, even after presenting triage options
- ✗ DO NOT mark complete if consistency checks fail
- Workflow status remains "IN PROGRESS" or "AWAITING TRIAGE" until test passes

IF TEST FAILS:
- Present triage options (Section G)
- STOP - do not mark Step 11 complete
- Wait for user decision
- Resume from Step 11 after fix (do not restart from Step 1)

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, test result, HITL triage (if triggered), workflow integrity checks, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
- CLOSE transcript with workflow summary (total duration, final status)
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | `run_test` (pytest subprocess execution) |
| **Quality Gates** | `qg_execution` (POST-only), `qg_workflow_complete` (POST-only meta-gate) |
| **Gate Modes** | POST-only (validates execution results, not inputs) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `test_result`, `triage_decision`, `workflow_integrity`, `retry_count` |
| **Who Saves** | AI (after test execution and gate validation) |
| **When Saved** | After qg_execution and qg_workflow_complete both pass |
| **State Schema** | See below |

```json
{
  "step": 11,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "test_result": {
      "status": "passed",
      "exit_code": 0,
      "output": "test_login.py::test_valid_login PASSED",
      "duration": 2.3,
      "report_path": "tests/_reports/report.html"
    },
    "triage_decision": null,
    "workflow_integrity": {
      "checks_passed": 8,
      "checks_failed": 0,
      "test_path_consistent": true,
      "files_exist": true,
      "imports_valid": true,
      "workflow_id_consistent": true,
      "audit_trail_complete": true,
      "state_complete": true,
      "modifications_tracked": true,
      "no_orphaned_state": true
    },
    "retry_count": 0,
    "error_signature": null
  }
}
```

**Failure State Example (HITL triage):**

```json
{
  "step": 11,
  "status": "awaiting_triage",
  "timestamp": "ISO-8601",
  "data": {
    "test_result": {
      "status": "failed",
      "exit_code": 1,
      "output": "test_login.py::test_valid_login FAILED\nE   assert False",
      "duration": 0.5,
      "failure_data": {
        "failed_assertion": "assert False",
        "error_location": "tests/auth/test_login.py:15",
        "stack_trace": "..."
      }
    },
    "diagnostic_data": {
      "version": "v1",
      "data_types": {
        "test_execution": {...},
        "page_state": {...},
        "browser_context": {...},
        "expected_vs_actual": {...},
        "test_context": {...},
        "test_data": {...},
        "execution_flow": {...}
      }
    },
    "ai_analysis": {
      "likely_cause": "Assertion failure in login validation",
      "confidence": 75,
      "evidence": ["Assertion: assert False at line 15"],
      "suggested_fix": "Review POM state-check method logic"
    },
    "retry_count": 0,
    "error_signature": "a1b2c3d4e5f6g7h8"
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-22 (HITL triage), FR-11.1-11.5 (execution gate features) |
| **Gate Enforcement** | **BLOCKED: Workflow cannot complete until qg_execution AND qg_workflow_complete pass** |

**qg_execution POST-Validation Checks:**

| Check | Rule |
|-------|------|
| `test_result.status` | Must be "passed", "failed", or "error" |
| `test_result.exit_code` | Required (0 = pass, non-zero = fail) |
| Test failure | Triggers HITL triage (user decision required) |
| Diagnostic data | 7 types captured on failure |
| AI analysis | Generated with confidence level |
| Retry policy | Max 3 retries per error signature |

**qg_workflow_complete POST-Validation Checks (8 consistency checks):**

| Check | Rule |
|-------|------|
| Test path consistency | Step 9 test path matches Step 11 execution path |
| File existence | All generated files (POM, Task, Role, Test) exist on disk |
| Import path validity | All import paths resolve correctly |
| Workflow ID consistency | Workflow ID matches across all state entries |
| Audit trail complete | All 11 steps logged to audit trail |
| State completeness | All required metadata present in state |
| Code modifications tracked | Any code changes after generation are logged |
| No orphaned state | No state fragments from incomplete workflows |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| Test execution error | Capture failure_data, trigger HITL triage |
| Assertion failure | AI analysis + 3 triage options |
| Timeout | High-confidence AI analysis (timeout issue) |
| Element not found | High-confidence AI analysis (locator issue) |
| Consistency check fails | Escalation options, HITL investigation |

**HITL Triage Workflow (on test failure):**

```
"TEST EXECUTION FAILED

Test: tests/auth/test_valid_login.py::test_valid_login
Duration: 0.5s
Exit Code: 1

Error:
AssertionError: assert False
  File "tests/auth/test_login.py", line 15, in test_valid_login
    assert login_page.is_logged_in(), "User should be logged in"

AI Analysis (Confidence: 75%):
Likely cause: Assertion failure in login validation
Evidence:
- Assertion failed at line 15
- POM state-check returned False

Suggested fix: Review is_logged_in() method logic

Diagnostic Data Available:
✓ Test execution (output, exit code, stack trace)
✓ Page state (current URL, page source)
✓ Browser context (console errors, network failures)
✓ Expected vs Actual (assertion comparison)
✓ Test context (fixtures, test data)
✓ Test data (credentials used)
✓ Execution flow (step-by-step log)

HOW SHOULD WE PROCEED?

1. Application Defect
   → Log defect to DEFECT_LOG.md
   → Block workflow (you fix the application)
   → Status: BLOCKED until app fixed

2. Test Issue
   → AI investigates root cause
   → AI proposes test fix
   → Re-run test after fix

3. Investigate
   → Show full diagnostic data
   → You analyze with AI assistance
   → Decide next action after investigation

Select option (1, 2, or 3):"
```

**Triage Decision Actions:**

| Option | Action | Blocking? |
|--------|--------|-----------|
| **1. Application Defect** | Log to DEFECT_LOG.md, stop workflow | YES - User fixes app |
| **2. Test Issue** | AI fixes test code, re-runs test | NO - AI attempts fix |
| **3. Investigate** | Show full diagnostic data, user analyzes | YES - Awaits user decision |

**Retry Policy:**

| Scenario | Behavior |
|----------|----------|
| First failure | Full HITL triage |
| Same error signature (2nd occurrence) | Retry with warning |
| Same error signature (3rd occurrence) | Mandatory HITL triage |
| Same error signature (4th+) | Block workflow, require user action |
| Different error signature | Treat as new failure |

---

## H. Diagnostic Data Types (7 Types Captured)

**Purpose:** Comprehensive failure analysis for HITL triage.

| Data Type | Contents | Source |
|-----------|----------|--------|
| **1. Test Execution** | pytest output, exit code, stack trace, failure_data | run_test output |
| **2. Page State** | Current URL, page title, page source (last 500 chars) | Browser context |
| **3. Browser Context** | Console errors, network failures, JavaScript errors | Browser logs |
| **4. Expected vs Actual** | Assertion comparison, POM state-check result | Test code analysis |
| **5. Test Context** | Fixtures used, conftest state, test setup | Pytest context |
| **6. Test Data** | Credentials, test inputs (sanitized), test configuration | Test data files |
| **7. Execution Flow** | Step-by-step log of POM/Task/Role method calls | @autologger output |

**AI Analysis Components:**

| Component | Description | Example |
|-----------|-------------|---------|
| **Likely Cause** | Root cause hypothesis | "Assertion failure in login validation" |
| **Confidence** | 0-100% (based on pattern matching) | 75% |
| **Evidence** | Data supporting hypothesis | ["Assertion at line 15", "POM returned False"] |
| **Suggested Fix** | Actionable fix guidance | "Review is_logged_in() method logic" |

**Confidence Levels:**

| Confidence | Pattern | Example |
|------------|---------|---------|
| **90-100%** | Explicit error (timeout, element not found) | TimeoutException, NoSuchElementException |
| **75-89%** | Strong assertion pattern | assert False, AssertionError with clear context |
| **50-74%** | Generic failure with context | Generic exception with stack trace |
| **< 50%** | Unclear failure | Test hung, unknown error |

---

## I. Workflow Complete Meta-Gate (8 Checks)

**Purpose:** Validate 11-step workflow integrity before marking complete.

| Check | Purpose | Failure Impact |
|-------|---------|----------------|
| **1. Test path consistency** | Step 9 path matches Step 11 execution | Medium - Path mismatch, wrong test ran |
| **2. File existence** | All generated files exist on disk | High - Missing file = incomplete workflow |
| **3. Import path validity** | All imports resolve correctly | High - Import error = broken code |
| **4. Workflow ID consistency** | Same workflow ID across all steps | Medium - State fragmentation |
| **5. Audit trail complete** | All 11 steps logged | Low - Audit gap, compliance issue |
| **6. State completeness** | All required metadata present | Medium - Missing data for debugging |
| **7. Code modifications tracked** | Post-generation changes logged | Low - Audit trail gap |
| **8. No orphaned state** | No state fragments from old workflows | Low - State pollution |

**Escalation Options (on check failure):**

```
"WORKFLOW INTEGRITY CHECK FAILED

Check failed: File existence
Reason: framework/tasks/auth/auth_tasks.py not found

Impact: HIGH - Generated Task file missing from disk

Possible causes:
1. File write failed in Step 7
2. File deleted manually after generation
3. Incorrect file path in metadata

HOW SHOULD WE PROCEED?

1. Regenerate Missing File
   → Go back to Step 7 (Task generation)
   → Re-generate auth_tasks.py
   → Continue from Step 7

2. Investigate State
   → Show full workflow state
   → Check metadata for path issues
   → Manual resolution

3. Restart Workflow
   → Restart from Step 1
   → Fresh generation
   → Clean state

Select option (1, 2, or 3):"
```

---

## J. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 11: EXECUTION & VALIDATION                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 10 complete?     │
                         │  Test file exists?     │
                         └────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  YES     │            │  NO      │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
┌─────────────────────────────────┐     ┌─────────────────┐
│  OPERATION: run_test            │     │  BLOCKED        │
│  - Execute pytest subprocess    │     │  Go back to     │
│  - Capture test_result          │     │  Step 10        │
└─────────────────────────────────┘     └─────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_execution                                  │
│  - Validate test_result structure                            │
│  - IF test passed → return pass_response                     │
│  - IF test failed → HITL triage workflow                     │
└─────────────────────────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
    ┌──────────┐                  ┌──────────────────────┐
    │  PASSED  │                  │  FAILED              │
    └────┬─────┘                  └────┬─────────────────┘
         │                             │
         │                             ▼
         │              ┌──────────────────────────────────┐
         │              │  HITL TRIAGE WORKFLOW:           │
         │              │  1. Capture 7 diagnostic types   │
         │              │  2. Generate AI analysis         │
         │              │  3. Present 3 options to user    │
         │              └──────────────────────────────────┘
         │                             │
         │              ┌──────────────┼──────────────┐
         │              ▼              ▼              ▼
         │         ┌────────┐    ┌─────────┐   ┌──────────────┐
         │         │ App Bug│    │Test Issue│   │ Investigate  │
         │         └────┬───┘    └────┬────┘   └──────┬───────┘
         │              │             │               │
         │              ▼             ▼               ▼
         │         ┌────────┐    ┌─────────┐   ┌──────────────┐
         │         │Log     │    │AI fixes │   │Show full     │
         │         │defect, │    │test,    │   │diagnostic    │
         │         │BLOCK   │    │re-run   │   │data, AWAIT   │
         │         └────────┘    └────┬────┘   └──────────────┘
         │                            │
         │                            ▼
         │                       (Re-run test)
         │                            │
         └────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│  META-GATE: qg_workflow_complete                             │
│  - Run 8 consistency checks                                  │
│  - Validate 11-step workflow integrity                       │
└─────────────────────────────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
    ┌──────────┐                  ┌──────────────────────┐
    │  PASS    │                  │  FAIL                │
    └────┬─────┘                  └────┬─────────────────┘
         │                             │
         ▼                             ▼
    ┌──────────────┐          ┌───────────────────────┐
    │  WORKFLOW    │          │  ESCALATION OPTIONS:  │
    │  COMPLETE    │          │  1. Regenerate        │
    │              │          │  2. Investigate       │
    │  State saved │          │  3. Restart           │
    │  Audit trail │          └───────────────────────┘
    │  finalized   │
    └──────────────┘
```

---

## K. Progressive Audit Trail (Step 11 Entry)

**Step 11 Audit Data:**

```json
{
  "step_11": {
    "timestamp": "2025-12-28T12:05:00Z",
    "gate_result": "pass",
    "data": {
      "test_execution": {
        "tool": "run_test",
        "test_path": "tests/auth/test_valid_login.py",
        "status": "passed",
        "exit_code": 0,
        "duration": 2.3,
        "report_path": "tests/_reports/report.html"
      },
      "execution_gate": {
        "tool": "qg_execution",
        "validation": "pass",
        "triage_required": false
      },
      "workflow_complete_gate": {
        "tool": "qg_workflow_complete",
        "validation": "pass",
        "checks_passed": 8,
        "checks_failed": 0,
        "consistency_summary": {
          "test_path_consistent": true,
          "files_exist": true,
          "imports_valid": true,
          "workflow_id_consistent": true,
          "audit_trail_complete": true,
          "state_complete": true,
          "modifications_tracked": true,
          "no_orphaned_state": true
        }
      }
    }
  }
}
```

**Failure Audit Example:**

```json
{
  "step_11": {
    "timestamp": "2025-12-28T12:05:00Z",
    "gate_result": "awaiting_triage",
    "data": {
      "test_execution": {
        "tool": "run_test",
        "test_path": "tests/auth/test_valid_login.py",
        "status": "failed",
        "exit_code": 1,
        "duration": 0.5,
        "failure_data": {
          "failed_assertion": "assert False",
          "error_location": "tests/auth/test_login.py:15"
        }
      },
      "execution_gate": {
        "tool": "qg_execution",
        "validation": "fail",
        "triage_required": true,
        "ai_analysis": {
          "likely_cause": "Assertion failure",
          "confidence": 75
        },
        "diagnostic_data_captured": true
      },
      "user_decision": "pending"
    }
  }
}
```

---

## L. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

### qg_execution

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-11-01 | POST-only mode (validates test execution results) | Test must run before validation | `validate()` |
| IC-11-02 | 7 diagnostic data types captured on failure | Comprehensive failure analysis for HITL | `_capture_diagnostic_data()` |
| IC-11-03 | AI analysis includes confidence level (0-100%) | User needs to know analysis reliability | `_generate_ai_analysis()` |
| IC-11-04 | 3 triage options presented to user (app bug, test issue, investigate) | Structured HITL workflow | `_format_triage_presentation()` |
| IC-11-05 | Error signature tracking (MD5 hash) | Retry policy enforcement, flaky test detection | `_check_retry_policy()` |
| IC-11-06 | Max 3 retries per unique error signature | Prevent infinite retry loops | `_check_retry_policy()` |
| IC-11-07 | Blocking on 4th+ occurrence of same error | Force HITL investigation of persistent failures | `validate()` |

### qg_workflow_complete

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-11-08 | 8 consistency checks run sequentially | Fail-fast with specific check that failed | `validate()` |
| IC-11-09 | Test path from Step 9 must match Step 11 execution | Ensure correct test was run | `_check_test_path_consistency()` |
| IC-11-10 | All generated files (POM, Task, Role, Test) must exist | Verify workflow generated actual files | `_check_file_existence()` |
| IC-11-11 | Import paths validated via importlib.util.find_spec() | Prevent import errors at runtime | `_check_import_paths()` |
| IC-11-12 | Workflow ID must match across all 11 steps | Prevent state fragmentation | `_check_workflow_id()` |
| IC-11-13 | Audit trail must have entries for all 11 steps | Complete audit trail for compliance | `_check_audit_trail()` |
| IC-11-14 | State must have metadata for all completed steps | State completeness for debugging | `_check_state_completeness()` |
| IC-11-15 | Post-generation code modifications logged to audit | Track manual changes after generation | `_check_modifications_tracked()` |
| IC-11-16 | No orphaned state from incomplete workflows | Clean state management | `_check_no_orphaned_state()` |

**Date Added:** 2026-01-13
**Task Reference:** Task 60.0 (qg_execution), Task 61.0 (qg_workflow_complete)

---

## M. Retry Policy Details

**Error Signature Generation:**

```python
# MD5 hash of: error_location + first line of error message
error_sig = hashlib.md5(f"{error_location}:{error_message}".encode()).hexdigest()[:16]
```

**Retry Logic:**

| Occurrence | Action |
|------------|--------|
| 1st (new signature) | Full HITL triage |
| 2nd (same signature) | Retry with warning: "Same error occurred again" |
| 3rd (same signature) | Mandatory HITL triage |
| 4th+ (same signature) | Block workflow, require user action |

**Flaky Test Detection:**

If test passes after retry:
```
"Test passed after retry (attempt 2).

This may indicate a flaky test. Consider:
1. Adding explicit waits
2. Checking for race conditions
3. Reviewing dynamic element handling

Error signature: a1b2c3d4e5f6g7h8"
```

---

## K. User Communication

**Purpose:** Define clean, concise output to user (not verbose MCP JSON).

**In Progress:**
```
⚙ Step 11: Executing Test...
  • Test: tests/helios1/test_create_service_inquiry.py
  • Environment: helios1
  • Browser: visible
  [Test execution in progress...]
```

**Complete (Passed):**
```
✓ Step 11: Test Execution
  • Status: PASSED
  • Duration: 12.3s
  • Report: tests/_reports/2026-01-19T00-20-55.248039Z/
```

**In Progress (Test Failed, Awaiting Triage):**
```
⚙ Step 11: Test Execution - FAILED (Awaiting Triage)
  • Test: tests/helios1/test_create_service_inquiry.py
  • Status: FAILED
  • Assertion: is_inquiry_created() returned False
  • Next: Choose fix strategy (1: Debug, 2: Regenerate, 3: Manual)
  • Workflow Status: INCOMPLETE
```

**What NOT to Show:**
- ❌ Full pytest output
- ❌ Gate status (unless showing triage options)
- ❌ Stack traces (unless part of triage diagnostic data)
- ❌ Verbose test logs
- ❌ "✓ Step 11 Complete" when test failed
- ❌ "✓ 11-Step QA Workflow Complete!" when test failed

**Rule:** Follow user-communication-protocol.md - Signal, not noise.

---

*Step 11 completes the 11-Step QA Execution Engine workflow.*
