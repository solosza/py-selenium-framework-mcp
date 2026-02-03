<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 5: Test Execution & HITL Iteration

**Purpose:** Execute test, validate results with HITL triage for failures, and iterate through pair programming loop.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 5 - Test Execution & HITL Iteration |
| **Dependencies** | Step 4 complete (all modules generated and saved) |
| **Input** | Test files from Step 4, workflow state |
| **Output** | Test execution result, HITL triage decisions (if failure) |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | Reviews test results, makes triage decisions on failures (app bug vs test issue) |
| **AI** | Executes test via Bash, constructs test_result, captures diagnostic data, presents triage options, applies fixes |
| **Tools** | `Bash` (execute pytest), `qg_execution` (validate results + HITL triage) |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 4 complete (all files saved)
- Verify test file path exists
- Verify workflow state has all metadata

ACTION (2-STEP SEQUENCE):
1. EXECUTE pytest via Bash tool (NOT run_test MCP tool):
   - Command: python -m pytest {test_path} -v --env={env} --headless=False
   - Parameters:
     - test_path (required): Path to test file
     - env (required): Environment config key from Step 1 detected_env_id
       Example: If URL was parabank.parasoft.com, detected_env_id = "parabank"
   - Browser ALWAYS visible (non-headless) for HITL observation
   - Capture exit code and output from Bash result
   - AI constructs test_result structure from Bash output:
     {
       "status": "passed" | "failed" | "crashed",
       "exit_code": <exit_code from Bash>,
       "output": <stdout + stderr from Bash>,
       "duration": <execution time if available>,
       "failure_data": <parse from output if status=failed>
     }
   - For failure_data extraction (when status=failed):
     - failed_assertion: Look for "E       assert" lines
     - error_location: Look for "file.py:line:" patterns
     - stack_trace: Content between failure markers

2. CALL qg_execution with test_result
   - IF test passed -> return pass_response -> WORKFLOW COMPLETE
   - IF test failed -> HITL triage workflow:
     a. Capture 7 diagnostic data types
     b. Generate AI analysis (likely cause, confidence, evidence)
     c. Return NEEDS_RETRY with hitl_required
     d. AI presents triage options to user
     e. Wait for user decision
   - Returns pass (test passed) or NEEDS_RETRY (HITL required)

VALIDATE:
- POST-only gate (no PRE validation for Step 5)
- qg_execution: Test result structure valid, HITL triggers on failure

HITL TRIAGE OPTIONS (on test failure):
User selects one of:
1. Application Defect - Log defect, block workflow (user fixes app)
2. Test Issue - AI investigates + fixes test code, retry
3. Investigate - Show full diagnostic data, user analyzes
4. Other - User describes what they want to do, AI follows instructions

RETRY POLICY:
- Error signature tracking (MD5 hash of error location + message)
- Max 2 retries per unique error signature before escalation
- Flaky test detection (passes after retry)

COMPLETION CRITERIA:
- ONLY mark Step 5 complete if qg_execution returns pass_response
- Test status must be "passed"
- DO NOT mark complete if test fails, even after presenting triage options
- Workflow status remains "IN PROGRESS" or "AWAITING TRIAGE" until test passes

IF TEST FAILS:
- Present triage options (Section G)
- STOP - do not mark Step 5 complete
- Wait for user decision
- Apply fix based on decision
- Retry from run_test (do not restart from Step 1)

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, test result, HITL triage (if triggered), timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
- CLOSE transcript with workflow summary (total duration, final status)
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | `Bash` (pytest via command line) |
| **Quality Gate** | `qg_execution` (POST-only) |
| **Gate Mode** | POST-only (validates execution results, not inputs) |

**Why Bash instead of run_test MCP tool:**
The run_test MCP tool uses synchronous subprocess.run() which blocks the MCP server event loop, causing timeouts. Bash tool handles subprocess execution correctly without blocking.

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `test_result`, `triage_decision`, `retry_count` |
| **Who Saves** | AI (after test execution and gate validation) |
| **When Saved** | After qg_execution passes |
| **State Schema** | See below |

```json
{
  "step": 5,
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
    "retry_count": 0,
    "error_signature": null
  }
}
```

**Failure State Example (HITL triage):**

```json
{
  "step": 5,
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
| **Rules That Apply** | DD-22 (HITL triage), DD-50 (Smart Gate Pattern) |
| **Gate Enforcement** | **BLOCKED: Workflow cannot complete until qg_execution passes** |

**qg_execution POST-Validation Checks:**

| Check | Rule |
|-------|------|
| `test_result.status` | Must be "passed", "failed", or "crashed" |
| `test_result.exit_code` | Required (0 = pass, non-zero = fail) |
| Test failure | Returns NEEDS_RETRY with hitl_required (user decision required) |
| Diagnostic data | 7 types captured on failure |
| AI analysis | Generated with confidence level |
| Retry policy | Max 2 retries per error signature |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| Test execution error | Capture failure_data, trigger HITL triage |
| Assertion failure | AI analysis + 3 triage options |
| Timeout | High-confidence AI analysis (timeout issue) |
| Element not found | High-confidence AI analysis (locator issue) |

**HITL Triage Workflow (on test failure):**

When qg_execution returns `NEEDS_RETRY` with `fix_applied: "hitl_required"`:

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
- Test execution (output, exit code, stack trace)
- Page state (current URL, page source)
- Browser context (console errors, network failures)
- Expected vs Actual (assertion comparison)
- Test context (fixtures, test data)
- Test data (credentials used)
- Execution flow (step-by-step log)

HOW SHOULD WE PROCEED?

1. Application Defect
   -> Log defect to DEFECT_LOG.md
   -> Block workflow (you fix the application)
   -> Status: BLOCKED until app fixed

2. Test Issue
   -> AI investigates root cause
   -> AI proposes test fix
   -> Re-run test after fix

3. Investigate
   -> Show full diagnostic data
   -> You analyze with AI assistance
   -> Decide next action after investigation

4. Other
   -> Describe what you want to do
   -> AI follows your instructions

Select option (1-4):"
```

**Triage Decision Actions:**

| Option | Action | Blocking? |
|--------|--------|-----------|
| **1. Application Defect** | Log to DEFECT_LOG.md, stop workflow | YES - User fixes app |
| **2. Test Issue** | AI fixes test code, re-runs test | NO - AI attempts fix |
| **3. Investigate** | Show full diagnostic data, user analyzes | YES - Awaits user decision |
| **4. Other** | User describes custom action, AI follows | YES - Awaits user input |

**Retry Policy:**

| Scenario | Behavior |
|----------|----------|
| First failure | Full HITL triage |
| Same error signature (2nd occurrence) | Retry with warning |
| Same error signature (3rd occurrence) | Mandatory HITL triage, escalate |
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

## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

### qg_execution

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-05-01 | POST-only mode (validates test execution results) | Test must run before validation | `validate()` |
| IC-05-02 | 7 diagnostic data types captured on failure | Comprehensive failure analysis for HITL | `_capture_diagnostic_data()` |
| IC-05-03 | AI analysis includes confidence level (0-100%) | User needs to know analysis reliability | `_generate_ai_analysis()` |
| IC-05-04 | 3 triage options presented to user (app bug, test issue, investigate) | Structured HITL workflow | `_format_triage_presentation()` |
| IC-05-05 | Error signature tracking (MD5 hash) | Retry policy enforcement, flaky test detection | `_check_retry_policy()` |
| IC-05-06 | Returns NEEDS_RETRY with hitl_required on failure | Triggers HITL loop, not hard fail | `validate()` |
| IC-05-07 | Max 2 retries per unique error signature | Prevent infinite retry loops | `_check_retry_policy()` |

---

## J. Flow Diagram

```
+-----------------------------------------------------------------------------+
|                    STEP 5: TEST EXECUTION & HITL ITERATION                   |
+-----------------------------------------------------------------------------+
                                      |
                                      v
                         +------------------------+
                         |  PRE-CHECK:            |
                         |  Step 4 complete?      |
                         |  Test file exists?     |
                         +------------------------+
                                      |
                          +-----------+-----------+
                          v                       v
                    +----------+            +----------+
                    |  YES     |            |  NO      |
                    +----+-----+            +----+-----+
                         |                       |
                         v                       v
+---------------------------------+     +-----------------+
|  OPERATION: run_test            |     |  BLOCKED        |
|  - Execute pytest subprocess    |     |  Go back to     |
|  - Capture test_result          |     |  Step 4         |
+---------------------------------+     +-----------------+
                         |
                         v
+-------------------------------------------------------------+
|  QUALITY GATE: qg_execution                                  |
|  - Validate test_result structure                            |
|  - IF test passed -> return pass_response                    |
|  - IF test failed -> return NEEDS_RETRY + hitl_required      |
+-------------------------------------------------------------+
                         |
          +--------------+--------------+
          v                             v
    +----------+                  +----------------------+
    |  PASSED  |                  |  NEEDS_RETRY         |
    +----+-----+                  |  hitl_required       |
         |                        +----+-----------------+
         |                             |
         |                             v
         |              +--------------------------------+
         |              |  AI PRESENTS TRIAGE OPTIONS:   |
         |              |  1. Application Defect         |
         |              |  2. Test Issue                 |
         |              |  3. Investigate                |
         |              +--------------------------------+
         |                             |
         |              +--------------+---------------+
         |              v              v               v
         |         +--------+    +---------+   +--------------+
         |         | App Bug|    |Test Issue|   | Investigate  |
         |         +----+---+    +----+----+   +------+-------+
         |              |             |               |
         |              v             v               v
         |         +--------+    +---------+   +--------------+
         |         |Log     |    |AI fixes |   |Show full     |
         |         |defect, |    |code,    |   |diagnostic    |
         |         |BLOCK   |    |re-run   |   |data, AWAIT   |
         |         +--------+    +----+----+   +--------------+
         |                            |
         |                            v
         |                       (Re-run test)
         |                            |
         +----------------------------+
                         |
                         v
                +----------------+
                |  WORKFLOW      |
                |  COMPLETE      |
                |                |
                |  State saved   |
                |  Audit trail   |
                |  finalized     |
                +----------------+
```

---

## K. User Communication

**Purpose:** Define clean, concise output to user (not verbose MCP JSON).

**In Progress:**
```
Step 5: Executing Test...
  - Test: tests/helios_inquiry/test_create_inquiry.py
  - Environment: helios_inquiry
  - Browser: visible
  [Test execution in progress...]
```

**Complete (Passed):**
```
Step 5: Test Execution
  - Status: PASSED
  - Duration: 12.3s
  - Report: tests/_reports/2026-01-26T00-20-55.248039Z/

5-Step QA Workflow Complete!
```

**In Progress (Test Failed, Awaiting Triage):**
```
Step 5: Test Execution - FAILED (Awaiting Triage)
  - Test: tests/helios_inquiry/test_create_inquiry.py
  - Status: FAILED
  - Assertion: is_inquiry_created() returned False
  - Next: Choose fix strategy (1: App Defect, 2: Test Issue, 3: Investigate)
  - Workflow Status: INCOMPLETE
```

**What NOT to Show:**
- Full pytest output (unless investigating)
- Gate status JSON (unless debugging)
- Stack traces (unless part of triage diagnostic data)
- Verbose test logs
- "Step 5 Complete" when test failed
- "5-Step QA Workflow Complete!" when test failed

**Rule:** Follow user-communication-protocol.md - Signal, not noise.

---

## L. HITL Response Protocol

**When AI receives NEEDS_RETRY with fix_applied == "hitl_required":**

1. **Extract presentation from fix_data**
   ```python
   presentation = response["fix_data"]["presentation"]
   triage_options = response["fix_data"]["triage_options"]
   ai_analysis = response["fix_data"]["ai_analysis"]
   ```

2. **Present to user**
   - Show formatted triage message
   - Show numbered options (1, 2, 3, 4)
   - Wait for user input

3. **Handle user decision**
   - Option 1 (App Defect): Log to DEFECT_LOG.md, stop workflow
   - Option 2 (Test Issue): Analyze code, apply fix, retry run_test
   - Option 3 (Investigate): Show full diagnostic_data, return to options
   - Option 4 (Other): Ask user what they want to do, follow instructions

4. **Retry loop**
   - After fix applied, call run_test again
   - Call qg_execution with new test_result
   - Repeat until PASS or user blocks

**Key Rule:** AI must NOT proceed without user decision when hitl_required is returned.

---

*Step 5 completes the 5-Step QA Execution Engine workflow.*
