# Step 11: HITL Execution Gate - Design Discussion

**Project:** step-11-hitl-execution-gate
**Phase:** Design (4D Framework - Phase 1)
**Date:** 2026-01-13
**Status:** ✅ COMPLETE - All 6 design questions answered, impact assessment complete, ready for PRD

---

## Context

**Where We Are:**
- 11-step workflow generates architecturally correct code (Steps 1-11)
- All quality gates enforce code structure (DD-25, DD-27, DD-49, etc.)
- Production validation shows: code passes all gates BUT may fail execution (DEF-058)

**The Gap:**
```
Quality Gates Say:     Reality Says:
✅ All 10 steps pass   ❌ Test fails
✅ Code correct        ❌ Doesn't execute
✅ Architecture good   ❌ Element not found
✅ Workflow complete   ❌ User has broken test
```

**The Problem (DEF-058):**
User completes workflow, sees "all gates passed", commits code, then discovers test doesn't run. This violates the core Isagawa thesis: "enforces execution, not just structure."

---

## What We're Building

**Step 11: Execution Validation Gate with HITL**

A new quality gate that enables proper QA triage workflow:

1. **Validates execution** - Test must pass before workflow completes
2. **Captures diagnostic data** - Provides context for triage (not pre-classified)
3. **Enables QA triage** - Human determines: app bug vs test issue
4. **Supports test fixes** - When test is wrong, AI helps fix it
5. **Re-validates code quality** - Fixed code must pass relevant gates (qg_page_object, qg_task, etc.)
6. **Re-runs test** - After fixes applied and gates passed
7. **Completes workflow** - Only when test passes AND code quality maintained

**Critical Principle:** Test failures are NOT always code issues. Test engineers find bugs. HITL is mandatory to distinguish:
- **Application defect** (test correct, app broken) → Log defect, STOP workflow
- **Test code issue** (app correct, test wrong) → Fix test, re-validate, retry

---

## Why Now

**Two Goals Achieved Simultaneously:**

### Goal 1: Prove AI Management Layer Thesis
From `isagawa_corp_thesis_v3.1.md`:
> "The AI Management Layer enforces how AI executes work, not just what it produces."

Without Step 11, we only enforce structure. With Step 11, we enforce execution.

### Goal 2: Complete QA Execution Platform
From `competitive_intel_qa_engine_2026-01-07.md`:
> "40% of QA time spent fixing broken tests"

Step 11 catches execution failures before user sees them, solving the maintenance trap.

---

## Design Principles (From Isagawa Architecture)

### Pattern 1: Assembly Line (Sequential Pipeline)
Step 11 fits naturally as the final stage in the 11-step assembly line:
```
Step 1-9: Generate code (gates validate STRUCTURE)
          ↓
Step 10:  Save files
          ↓
Step 11:  Execution Validation Gate (validates RUNTIME)
          ↓
      ✅ DONE (only if test passes)
```

### Pattern 3: Smart Gates (Provide Fix, Don't Just Block)
From `execution_patterns.md`:
> "Gates PROVIDE the fix, not just report the error"

```
Instead of:
  Gate: "Test failed. Element not found." ❌

We do:
  Gate: "Element not found. I tested 3 alternatives:
         1. CSS: .account-header (found in 0.2s)
         2. XPath: //h1[@id='title'] (found in 0.1s)
         3. Text: 'Accounts' (found in 0.3s)
         Recommend #2. Your call?" ✅
```

---

## HITL Integration

**Why HITL at Step 11:**
- AI detects failure and proposes fixes (90% of work)
- Human validates AI's judgment (critical 10%)
- Human brings context AI lacks (API delays, deployment changes, business rules)

**Tiered Approach:**
```
TIER 1: Auto-Apply (High Confidence)
  - Obvious fixes (timeout increase)
  - Action: Apply + notify

TIER 2: Quick Approval (Medium Confidence)
  - Single clear fix with tradeoffs
  - Action: Show recommendation + 1-click approve

TIER 3: Full HITL (Low Confidence / Complex)
  - Multiple options with pros/cons
  - Action: Present options + user picks
```

---

## Design Questions (Architectural - QA Triage Workflow)

**Key Insight:** Step 11 is NOT a Smart Gate. It's a Quality Gate that enables QA triage workflow.

**Pattern for Step 11:**
```python
# qg_execution validates execution, provides diagnostic data for triage
return cls.fail_response(
    error="Test failed: {test_name}",
    fix_hint="Triage required: Determine if application defect or test issue.",
    metadata={
        "diagnostic_data": {...},  # Raw data for analysis
        "triage_questions": [...],  # Questions to help human decide
    }
)
```

**Distinction:**

| Smart Gate (qg_page_object) | Execution Gate (qg_execution) |
|----------------------------|------------------------------|
| Deterministic rules | Context-dependent judgment |
| Gate knows the fix | Human decides cause |
| "Use PascalCase format" | "Is this expected behavior?" |
| Auto-fixable | Requires triage |

---

### 1. Diagnostic Data Capture

**Question:** What diagnostic data must qg_execution capture to enable QA triage?

**Data Requirements (MVP):**

| Data Type | What to Capture | Purpose |
|-----------|----------------|---------|
| **Test Execution** | Pytest output, exit code, failed assertion, stack trace | Understand what failed |
| **Page State** | Playwright snapshot (current page elements, their states) | See what's actually on page |
| **Browser Context** | Current URL, page title, console errors, network errors | Validate navigation/state |
| **Expected vs Actual** | What test expected, what it found | Core triage question |
| **Test Context** | Test file, POM file, method that failed, line number | Know where to fix |
| **Test Data Used** | Credentials, input values, test data source | Reproducibility - know what data caused failure |
| **Execution Flow** | Steps completed before failure (login ✓ → navigate ✓ → assert ✗) | Know how far test got, which step broke |

**Future Enhancements (v2):**

| Data Type | What to Capture | Purpose |
|-----------|----------------|---------|
| **Environment Context** | Browser/version, OS, viewport size, CI vs local | Cross-environment debugging |
| **Timing Breakdown** | Per-step duration, slow operations | Performance vs functional issue detection |
| **Network Activity** | API calls, response times, status codes | Backend issue detection |
| **Application Logs** | Server-side logs (if accessible) | See what app was doing internally |

**Extensible Metadata Structure:**
```python
metadata = {
    "diagnostic_data": {
        "v1": {
            # MVP data types
            "test_execution": {...},
            "page_state": {...},
            "browser_context": {...},
            "test_data": {...},        # NEW
            "execution_flow": {...}    # NEW
        },
        "v2": {
            # Future enhancements (not captured in MVP)
            "environment": None,       # Placeholder
            "timing": None,            # Placeholder
            "network": None,           # Placeholder
            "app_logs": None           # Placeholder
        }
    }
}
```

This structure allows adding v2 fields without breaking existing tooling.

**Example (DEF-058 case with MVP data):**
```python
metadata={
    "diagnostic_data": {
        "v1": {
            "test_execution": {
                "exit_code": 1,
                "failed_assertion": "assert overview_page.is_on_account_overview()",
                "error": "AssertionError: Should be on account overview page",
                "file": "tests/parabank8/test_login_and_view_account_overview.py",
                "line": 48,
                "duration_seconds": 10.2
            },
            "page_state": {
                "playwright_snapshot": {
                    "heading": [
                        {"level": 1, "text": "Accounts Overview", "visible": True}
                    ],
                    "forms": [],
                    "buttons": [...]
                }
            },
            "browser_context": {
                "url": "https://parabank.parasoft.com/parabank/overview.htm",
                "title": "ParaBank | Accounts Overview",
                "console_errors": [],
                "network_errors": []
            },
            "expected_vs_actual": {
                "expected": "Element visible with locator: //h1[text()='Accounts Overview']",
                "actual": "Element not found by Selenium after 5s timeout",
                "playwright_result": "Element found immediately"
            },
            "test_context": {
                "pom_file": "framework/pages/parabank8/account_overview_page.py",
                "failed_method": "is_on_account_overview()",
                "failed_locator": "ACCOUNTS_OVERVIEW_HEADING = (By.XPATH, \"//h1[text()='Accounts Overview']\")",
                "line": 55
            },
            "test_data": {
                "credentials": {
                    "username": "john",
                    "password": "demo",
                    "source": "tests/data/test_users.json",
                    "workflow": "parabank8"
                },
                "input_values": {},  # No additional inputs for this test
                "fixtures_used": ["web_interface", "config", "test_users"]
            },
            "execution_flow": {
                "steps": [
                    {"step": 1, "action": "Navigate to login page", "status": "passed", "duration": 1.2},
                    {"step": 2, "action": "Enter username", "status": "passed", "duration": 0.3},
                    {"step": 3, "action": "Enter password", "status": "passed", "duration": 0.2},
                    {"step": 4, "action": "Click login", "status": "passed", "duration": 2.5},
                    {"step": 5, "action": "Assert on account overview", "status": "FAILED", "duration": 5.0}
                ],
                "failed_at_step": 5,
                "steps_before_failure": 4
            }
        },
        "v2": {
            "environment": None,
            "timing": None,
            "network": None,
            "app_logs": None
        }
    },
    "triage_questions": [
        "Is this element supposed to exist on /parabank/overview.htm?",
        "Is the h1 text exactly 'Accounts Overview' per requirements?",
        "Should login automatically navigate to overview page?"
    ]
}
```

**DECISION - Question 1:**
- ✅ MVP includes 7 data types (added Test Data, Execution Flow)
- ✅ v2 enhancements documented but not implemented in MVP
- ✅ Extensible metadata structure with versioning (v1/v2)
- ✅ Playwright snapshot runs automatically on failure (captures complete page state)
- ✅ Test data captures credentials + source for reproducibility
- ✅ Execution flow shows step-by-step progress before failure

**Ready for implementation:** Yes - data structure is complete and extensible.

---

### 2. QA Triage Workflow (HITL)

**Question:** How does AI present diagnostic data to enable human triage decision?

**Triage Decision Tree:**

```
Test Failed
  ↓
AI analyzes diagnostic data
  ↓
AI presents to human:
  "Test failed. Is this expected behavior?"

  [Show diagnostic data formatted for human]
  - What test expected
  - What actually happened
  - Current page state (Playwright snapshot)
  - URL, console errors

  Options:
  1. Application defect (test correct, app broken)
  2. Test issue (app correct, test wrong)
  3. Need more investigation

Human decides → AI acts accordingly
```

**Option 1: Application Defect**
```
Human: "This is an app bug. Element should be there."

AI action:
- Create defect entry in DEFECT_LOG.md
- Mark workflow as BLOCKED (don't force test to pass)
- Stop Step 11 (don't retry)
- User must fix application, then re-run workflow
```

**Option 2: Test Issue**
```
Human: "Test is wrong. Element uses different locator."

AI action:
- Ask human for guidance: "What should change?"
- Human provides direction (e.g., "try CSS selector", "add wait")
- AI modifies test code (POM/Task/Test)
- Re-run relevant quality gates (qg_page_object, qg_task, etc.)
- Gates pass? → Re-run test
- Test passes? → Step 11 complete
```

**Option 3: Need Investigation**
```
Human: "Not sure, need to investigate."

AI action:
- Provide additional diagnostic tools
- Offer to run test with different configurations
- Human can pause workflow, investigate manually
- Resume when ready
```

**Example (DEF-058 triage):**
```
AI presents:
────────────────────────────────────────────
Test Failed: test_login_and_view_account_overview

Expected:
  Element visible: //h1[text()='Accounts Overview']

Actual:
  Element not found after 5s timeout

Page State (Playwright):
  ✓ URL correct: /parabank/overview.htm
  ✓ Page title: "ParaBank | Accounts Overview"
  ✓ Element EXISTS: h1 with text "Accounts Overview"
  ✗ Selenium cannot find it (timeout)

Console: No errors

Is this expected behavior?
1. App bug - Element should be findable by Selenium
2. Test issue - Need different locator/wait strategy
3. Investigate further
────────────────────────────────────────────

---

Human responds: "Option 2 - Test issue"
  ↓
AI: "What should change?"
Human: "Try CSS selector instead"
  ↓
AI modifies account_overview_page.py
  ↓
[SMART GATES APPLY HERE]
qg_page_object validates modification
  - Still class constant? ✓
  - No skeleton code? ✓
  - DD-49 compliant? ✓
  ↓
Gate passes → Re-run test → Passes → Done
```

**DECISION - Question 2:**

**2.1 AI Presentation: SUGGESTIVE**
- AI analyzes diagnostic data and suggests likely cause
- Example: "Looks like a locator issue - Playwright finds element, Selenium doesn't"
- AI provides reasoning but human makes final decision
- Format: "Analysis: {likely cause} | Confidence: {high/medium/low}"

**2.2 Human Input: HYBRID (Options + Free Text)**
- AI presents structured options based on analysis
- User can pick an option OR provide free text guidance
- Example:
  ```
  AI suggests:
  1. Try CSS selector instead (RECOMMENDED)
  2. Increase timeout to 10s
  3. Add explicit wait for visibility
  4. Other (provide your own guidance)
  ```
- If user picks "Other", AI asks: "What should I try?"
- User can respond with free text: "Use contains() instead of exact match"

**Why Hybrid:**
- Options speed up common cases
- Free text handles edge cases AI didn't anticipate
- Flexibility without sacrificing structure

**Updated Triage Presentation (DEF-058):**
```
AI presents:
────────────────────────────────────────────
Test Failed: test_login_and_view_account_overview

Analysis: LOCATOR ISSUE (Confidence: HIGH)
Reasoning: Playwright finds element immediately, Selenium times out.
          This indicates Selenium-specific selector problem.

Expected:
  Element visible: //h1[text()='Accounts Overview']

Actual:
  Element not found after 5s timeout

Page State (Playwright):
  ✓ URL correct: /parabank/overview.htm
  ✓ Page title: "ParaBank | Accounts Overview"
  ✓ Element EXISTS: h1 with text "Accounts Overview"
  ✗ Selenium cannot find it (XPath issue)

Credentials: john/demo (from tests/data/test_users.json)
Steps before failure: 4/5 passed (login succeeded, assertion failed)

Is this expected behavior?
1. App bug - Element should be findable by Selenium
2. Test issue - Need different locator (LIKELY)
3. Test issue - Need timing adjustment
4. Investigate further
────────────────────────────────────────────

[If user picks option 2 "Test issue - Need different locator"]

AI: "What locator strategy should I try?"
Options:
1. CSS selector (h1.page-title) - RECOMMENDED
2. More flexible XPath (contains text)
3. ID-based locator
4. Other (tell me what to try)
```

---

### 3. Code Fix Validation (Smart Gates Apply)

**Question:** How do existing smart gates re-validate code fixes during Step 11?

**Key Principle:** When AI modifies test code after triage, ALL relevant quality gates MUST re-run.

**Re-Validation Flow:**

```
Human triages: "Test issue - fix code"
  ↓
AI modifies file(s)
  ↓
Determine which files changed
  ↓
Re-run corresponding gates:
  - POM modified? → qg_page_object (PRE + POST)
  - Task modified? → qg_task (PRE + POST)
  - Role modified? → qg_role (PRE + POST)
  - Test modified? → qg_test_runner (PRE + POST)
  ↓
ANY gate fails? → Smart gate provides fix_hint
  ↓
AI applies fix_hint
  ↓
Re-run gates until ALL pass
  ↓
ALL gates pass? → Re-run test
```

**Smart Gates Enforce Patterns (Examples):**

| Gate | Validates | Example fix_hint |
|------|-----------|------------------|
| **qg_page_object** | Locators as class constants, no skeleton, atomic methods | "Locator must be class constant. Move to top of class." |
| **qg_task** | NO locators in Tasks, delegates to POM | "Locator detected in Task. Remove it. Use POM method instead." |
| **qg_role** | Orchestrates Tasks, no direct page access | "Direct POM access in Role. Use Task method instead." |
| **qg_test_runner** | Uses POM state-check methods for assertions | "Assertion not using POM state method. Use pom.is_*() instead." |

**Example (DEF-058 fix):**

```
1. Human: "Test issue - try different locator"
2. AI modifies account_overview_page.py:
   - Changes ACCOUNTS_OVERVIEW_HEADING locator
3. Re-run qg_page_object:
   - Validates: Still class constant? ✓
   - Validates: No skeleton code? ✓
   - Validates: Proper format? ✓
   - Result: PASS
4. Re-run test → Passes → Step 11 complete
```

**If gate fails during re-validation:**
```
AI modifies code incorrectly (adds locator to Task)
  ↓
qg_task validates
  ↓
Gate fails: "Locator detected in Task at line 25"
fix_hint: "Remove locator. Use POM method cart_page.click_checkout() instead."
  ↓
AI applies fix_hint
  ↓
qg_task re-validates → Passes
  ↓
Re-run test
```

**DECISION - Question 3:**

**3.1 Dependency-Aware Re-Validation (MVP)**
- ✅ Re-run gates for ALL downstream dependencies (follow 4-layer chain)
- Not just modified file - validate entire dependency chain

**Re-Validation Matrix:**

| File Modified | Gates to Re-run | Why |
|---------------|----------------|-----|
| **POM** | qg_page_object + qg_task + qg_role + qg_test_runner | Full chain - POM changes affect everything downstream |
| **Task** | qg_task + qg_role + qg_test_runner | Task changes affect Roles and Tests |
| **Role** | qg_role + qg_test_runner | Role changes affect Tests |
| **Test** | qg_test_runner | Only affects itself |

**3.2 Validation Mode: POST Only**
- ✅ POST validation only (no PRE needed)
- Why: Prerequisites already validated in Steps 1-11, we're just modifying existing code
- PRE checks ("Does state exist?") are redundant in Step 11 context

**3.3 Gate Failure Threshold: 3 Attempts**
- ✅ Same as test failures: 3 attempts → escalate to human
- If AI can't generate compliant code after 3 attempts, human intervention required
- Consistent policy across test failures and gate failures

**3.4 Interface Contract Validation: NOT in MVP**
- ❌ Skip method call/signature validation in MVP
- Why: Tools moving to skeleton generation + AI fill (future architecture)
- Step 11 catches interface breaks via test execution failure
- HITL triage handles wrong method calls: Test crashes → Human guides → AI fixes with correct method from metadata
- Don't over-invest in parsing current full-code generation

**What This Means:**
- Gates validate patterns (locators, returns, structure) - what they do now
- Interface breaks (wrong method calls) caught by test execution, not gates
- Skeleton approach (future) solves this architecturally

**3.5 Metadata Handling During Re-Validation (CRITICAL)**

**Problem:** When Step 11 modifies code, metadata from earlier steps may be stale.

**Metadata Dependencies:**

| Gate | Requires Metadata | Source Step | Stale After Modification? |
|------|------------------|-------------|---------------------------|
| **qg_page_object** | discovered_elements, expected_states, page_name | Step 5, Step 3, Step 5 | NO - elements don't change, just locators |
| **qg_task** | pom_metadata | Step 6 | YES if POM modified - method list may have changed |
| **qg_role** | task_metadata | Step 7 | YES if Task modified - method list may have changed |
| **qg_test_runner** | pom_metadata, task_metadata, role_metadata, test_scenarios | Steps 4,6,7,8 | YES if any layer modified |

**Metadata Regeneration Strategy:**

```
Step 11 modifies file(s)
  ↓
Determine which metadata is now stale
  ↓
Regenerate stale metadata from modified code:
  - POM modified? → Extract methods, regenerate pom_metadata
  - Task modified? → Extract methods, regenerate task_metadata
  - Role modified? → Extract methods, regenerate role_metadata
  ↓
Pass updated metadata to gates for re-validation
```

**Metadata Extraction (Step 11):**

```python
# If POM modified, regenerate pom_metadata
pom_metadata = {
    "class_name": "AccountOverviewPage",
    "import_path": "framework.pages.parabank8.account_overview_page",
    "locators": extract_locators_from_code(modified_pom_code),
    "action_methods": extract_methods_by_pattern(modified_pom_code, returns_self=True),
    "state_methods": extract_methods_by_pattern(modified_pom_code, returns_bool=True)
}

# Pass to qg_page_object
qg_page_object(code=modified_pom_code, page_name=page_name, pom_metadata=pom_metadata)
```

**State Management (Read Earlier Metadata):**

Step 11 must read metadata from workflow state:
- `state.get("discovered_elements")` from Step 5
- `state.get("pom_metadata")` from Step 6 (or regenerate if modified)
- `state.get("task_metadata")` from Step 7 (or regenerate if modified)

**Schema Consistency:**

All metadata must follow established schemas (from DD-26: Tool chain data contracts):
- pom_metadata schema: `{class_name, import_path, locators, action_methods, state_methods}`
- task_metadata schema: `{class_name, import_path, workflow_methods}`
- role_metadata schema: `{class_name, import_path, workflow_methods, capabilities}`

**Key Decision:**
- ✅ Regenerate metadata from modified code before re-running gates
- ✅ Use same extraction logic as original steps (consistency)
- ✅ Validate regenerated metadata matches expected schema
- ✅ Update workflow state with regenerated metadata

---

### 4. Retry Policy and Loop Prevention

**Question:** What prevents infinite retry loops during Step 11?

**Retry Scenarios:**

| Scenario | Max Attempts | Action After Limit |
|----------|-------------|-------------------|
| **Test fails, same error** | 3 attempts | Ask human: Continue or abort? |
| **Gate fails, same error** | 3 attempts | Present error to human: "AI cannot fix this" |
| **Test fails, different errors** | 5 total attempts | Each new error gets fresh analysis |
| **Human requested retry** | Unlimited | Human controls when to stop |

**Loop Prevention Logic:**

```
Attempt counter = 0
Last error signature = None

RETRY_LOOP:
  Run test
  ↓
  Test passes? → Done ✅
  ↓
  Test fails → Capture error signature
  ↓
  Same as last error? → Increment attempt counter
  Different error? → Reset attempt counter, update signature
  ↓
  Attempt counter > 3? → ASK HUMAN
    - "Test failing 3 times with same error: {error}"
    - "Continue fixing or abort workflow?"
    - Human decides: Continue (reset counter) or Abort
  ↓
  Total attempts > 5? → FORCE ABORT
    - "Step 11 exceeded max attempts"
    - Workflow incomplete
  ↓
  HITL triage → Fix code → Re-validate gates → RETRY_LOOP
```

**Example (DEF-058 scenario):**

```
Attempt 1: Element not found → Human: "Try CSS" → Fix → Test still fails (same error)
Attempt 2: Element not found → Human: "Increase timeout" → Fix → Test still fails (same error)
Attempt 3: Element not found → Human: "Try contains()" → Fix → Test still fails (same error)

AI: "Test has failed 3 times with same error after different fixes.
     Should I:
     1. Continue trying new approaches
     2. Mark as application defect
     3. Abort workflow (investigate manually)"

Human picks option → AI proceeds accordingly
```

**DECISION - Question 4:**

**4.1 Same-Error Retry Limit: 2 Attempts**
- ✅ After 2 attempts with same error → Ask human for guidance
- Why 2 not 3: Faster feedback loop, less frustration
- If same fix fails twice, AI likely can't solve it autonomously

**4.2 Total Attempt Limit: 5 with Human Confirmation**
- ✅ After 5 total attempts → Confirm with human before continuing
- NOT a hard abort - human decides whether to continue, investigate, or abort
- Different errors each time = progress, may be solvable with more attempts

**Confirmation Dialog (at 5 attempts):**
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
```

**4.3 No Time Limits**
- ✅ No timeout for Step 11
- Why: HITL is involved - human controls pacing
- Human can abort anytime via triage decision
- Time limits would interrupt human mid-investigation

**Loop Prevention Logic:**

```python
same_error_count = 0
total_attempts = 0
last_error_signature = None

while True:
    run_test()
    total_attempts += 1

    if test_passed:
        break  # Done!

    # Check error signature
    current_error = get_error_signature()

    if current_error == last_error_signature:
        same_error_count += 1
    else:
        same_error_count = 1  # Reset
        last_error_signature = current_error

    # Same error limit
    if same_error_count >= 2:
        ask_human("Same error 2x. What should I try?")
        same_error_count = 0  # Reset after human input

    # Total attempt soft limit
    if total_attempts >= 5:
        response = ask_human("5 attempts made. Continue, mark defect, or abort?")
        if response == "abort":
            break
        # If continue, keep going (no hard limit)
```

**Why This Works:**
- 2 same-error attempts: Quick escalation when stuck
- 5 total attempts: Checkpoi nt, not hard stop
- No time limits: Human controls pacing via HITL
- Human can abort anytime: Full control

---

### 5. State Persistence and Audit Trail

**Question:** What state must Step 11 persist for audit trail and learning?

**Audit Data to Capture:**

```python
{
    "step": 11,
    "workflow_id": "parabank8_login_test",
    "timestamp": "2026-01-13T10:30:00Z",

    "initial_test_result": {
        "status": "failed",
        "error": "AssertionError: Should be on account overview page",
        "test_file": "tests/parabank8/test_login_and_view_account_overview.py",
        "failed_line": 48
    },

    "diagnostic_data": {
        "pytest_output": "...",
        "playwright_snapshot": {...},
        "browser_state": {...}
    },

    "triage_decision": {
        "decision": "test_issue",  # or "app_defect" or "investigate"
        "human_notes": "Element exists, Selenium can't find it",
        "timestamp": "2026-01-13T10:32:00Z"
    },

    "fixes_attempted": [
        {
            "attempt": 1,
            "files_modified": ["framework/pages/parabank8/account_overview_page.py"],
            "change_description": "Changed locator to CSS selector",
            "gates_run": ["qg_page_object"],
            "gates_passed": true,
            "test_result": "still_failed",
            "same_error": true
        },
        {
            "attempt": 2,
            "files_modified": ["framework/pages/parabank8/account_overview_page.py"],
            "change_description": "Increased timeout from 5s to 10s",
            "gates_run": ["qg_page_object"],
            "gates_passed": true,
            "test_result": "passed",
            "same_error": false
        }
    ],

    "final_state": {
        "status": "completed",  # or "blocked_app_defect" or "aborted"
        "attempts_count": 2,
        "total_duration_seconds": 180,
        "test_passed": true
    }
}
```

**Audit Trail Location:** `tests/_audit/step11_execution_{workflow_id}_{timestamp}.json`

**Why Capture This:**
- Debug failures in Step 11 itself
- Track common failure patterns (inform future improvements)
- Provide evidence for QA reports (what was tried, what worked)
- Learning data (if failure pattern repeats, AI can suggest known fix)

**DECISION - Question 5:**

**5.1 Data Capture: Full Diagnostic Data**
- ✅ Capture complete diagnostic data for each attempt
- JSON compresses well, storage is cheap
- Full context helps debugging Step 11 issues
- Can filter/summarize in UI layer if needed

**5.2 Audit File Strategy: HYBRID (Summary + Detail)**
- ✅ Both workflow audit AND separate Step 11 detail file

**Workflow Audit (Timeline Summary):**
```json
{
  "step": 11,
  "gate": "qg_execution",
  "result": "pass",
  "timestamp": "2026-01-13T10:35:00Z",
  "summary": {
    "attempts": 2,
    "triage_decision": "test_issue",
    "files_modified": ["framework/pages/parabank8/account_overview_page.py"],
    "final_status": "completed",
    "duration_seconds": 180
  },
  "step11_detail_file": "tests/_audit/step11/step11_parabank8_login_2026-01-13T10-30-00.json"
}
```

**Step 11 Detail File (Full Investigation Trail):**
- Location: `tests/_audit/step11/step11_{workflow_id}_{timestamp}.json`
- Contains: Full diagnostic data (7 types), triage decision, all fix attempts with before/after, final state
- Purpose: Complete record for debugging, pattern analysis, QA reporting

**Directory Structure:**
```
tests/_audit/
├── audit_log_2026-01-13T10-00-00.json  (workflow audit - all 11 steps)
└── step11/
    ├── step11_parabank8_login_2026-01-13T10-30-00.json
    ├── step11_checkout_flow_2026-01-13T11-15-00.json
    └── step11_cart_add_item_2026-01-13T12-00-00.json
```

**Why Hybrid:**
- Workflow audit stays readable (summary only)
- Step 11 detail file has complete investigation context
- Easy correlation via reference link
- Can analyze Step 11 patterns across workflows (all in one directory)
- Supports future learning without bloating main audit

**5.3 Learning from Patterns: v2 Enhancement**
- ❌ NOT in MVP - capture data structure to support it later
- Data structure includes: error type, fix applied, success/failure
- Future: Mine historical audits to suggest fixes ("Last time this error occurred, CSS selector worked")
- Can build ML/pattern matching on top of audit data in v2

---

### 6. Tool Architecture - Gate vs Operation

**Question:** How should Step 11 split gate (validation) from operation (test execution)?

**Architectural Decision:** Split into TWO tools to maintain "gates don't do operations" principle.

**Option C (Recommended): Two Separate Tools**

**Tool 1: `run_test` (Operation)**
```python
def run_test(test_path: str, env: str = None) -> dict:
    """
    Operation: Execute pytest for specified test.

    Returns:
        {
            "status": "passed" | "failed",
            "exit_code": int,
            "output": str,
            "duration": float,
            "failed_assertion": str (if failed),
            "stack_trace": str (if failed)
        }
    """
    # Execute pytest
    # Capture all output
    # Return structured results
```

**Tool 2: `qg_execution` (Quality Gate)**
```python
def qg_execution(test_results: dict, test_path: str, workflow_id: str) -> dict:
    """
    Quality Gate: Validates test execution results.

    Enforces: Test must pass before workflow completes.
    Provides: Diagnostic data for triage when test fails.
    """
    if test_results["status"] == "passed":
        return cls.pass_response()

    # Test FAILED - Capture diagnostic data
    playwright_snapshot = capture_playwright_snapshot()
    browser_state = get_browser_state()

    return cls.fail_response(
        error=f"Test failed: {test_results['failed_assertion']}",
        fix_hint="Triage required: Determine if application defect or test issue.",
        metadata={
            "test_execution": test_results,
            "diagnostic_data": {
                "playwright_snapshot": playwright_snapshot,
                "browser_state": browser_state,
                "test_context": extract_test_context(test_path)
            },
            "triage_questions": [
                "Is this element supposed to exist?",
                "Is the expected behavior correct?",
                "Should navigation reach this state?"
            ]
        }
    )
```

**AI Orchestration (Step 11 flow):**

```
AI calls: run_test(test_path, env)
  ↓
AI calls: qg_execution(test_results, test_path, workflow_id)
  ↓
Gate returns: PASS or FAIL
  ↓
If FAIL:
  - AI presents diagnostic data to human
  - HITL triage workflow
  - If test issue: Fix code → Re-validate gates → RETRY
  - If app defect: Log defect → BLOCK workflow
```

**Pattern Consistency:**

| Principle | Compliance |
|-----------|-----------|
| **Gates don't do operations** | ✅ run_test does execution, qg_execution only validates |
| **Gates enforce quality** | ✅ qg_execution blocks workflow if test fails |
| **Gates provide context** | ✅ Returns diagnostic data for triage |
| **fail_response structure** | ✅ Uses standard fail_response(error, fix_hint, metadata) |

**Why NOT the other options:**

| Option | Problem |
|--------|---------|
| **A: AI runs test manually** | AI must know exact pytest command, flags, env config → error-prone |
| **B: Gate runs test** | Violates "gates don't do operations" → breaks architectural pattern |

**DECISION - Question 6:**

**6.1 Three-Tool Architecture**
- ✅ `run_test` (MCP tool) - Operation: Execute pytest
- ✅ `qg_execution` (Quality Gate) - Validates test passed, enables HITL retry
- ✅ `qg_workflow_complete` (Meta-Gate) - Validates entire 11-step workflow integrity

**6.2 run_test as MCP Tool (Not Bash)**
- ✅ MCP tool ensures consistent pytest execution
- Guarantees required params every time:
  - `-v` (verbose output)
  - `--html={report_path}` (HTML report generation)
  - `--self-contained-html` (single-file report)
  - `--env {env}` (environment config)
- AI using Bash might forget params → inconsistent execution
- Tool encapsulates pytest complexity

**Tool Signature:**
```python
def run_test(test_path: str, env: str = "DEFAULT") -> dict:
    """
    Execute pytest with consistent parameters.

    Returns:
        {
            "status": "passed" | "failed",
            "exit_code": int,
            "output": str,
            "duration": float,
            "report_path": str,
            "failed_assertion": str (if failed),
            "stack_trace": str (if failed)
        }
    """
```

**6.3 qg_workflow_complete Validations**

**Cross-Step Consistency Checks (8 validations):**

| Validation | What It Catches | Example Failure |
|------------|----------------|----------------|
| **Test path consistency** | Step 9 generated test A, Step 11 ran test B | Generated test_login.py, ran test_checkout.py |
| **File existence** | Files saved in Step 10 actually exist on disk | Save reported success but file missing |
| **Import path validity** | Generated import paths actually work | Role imports Task from wrong path |
| **Workflow ID consistency** | Same workflow_id used across all 11 steps | Step 5 used "parabank7", Step 11 used "parabank8" |
| **Audit trail complete** | All 11 steps logged with gate results | Step 7 missing from audit log |
| **State completeness** | All required metadata in final state | pom_metadata missing after Step 11 modifications |
| **Code modifications tracked** | Step 11 changes recorded in audit | Modified POM but no record in Step 11 audit |
| **No orphaned state** | Clean state, no partial failures | Previous workflow artifacts still in state |

**6.4 qg_workflow_complete Failure Handling**

**If qg_workflow_complete fails → Escalate to Human (NOT auto-restart)**

**Example Failure Presentation:**
```
────────────────────────────────────────────
Workflow Consistency Check Failed

Issue: Test path mismatch
  Generated (Step 9): tests/auth/test_login.py
  Executed (Step 11): tests/checkout/test_purchase.py

This suggests Step 11 ran the wrong test file.

What would you like to do?
1. Re-run Step 11 with correct test path (quick fix)
2. Restart entire workflow from Step 1 (clean slate)
3. Accept as-is (test_purchase.py IS what you wanted)
4. Abort workflow (investigate manually)
────────────────────────────────────────────
```

**Why Escalate (Not Auto-Fix):**
- Human has context (maybe they WANTED different test)
- Most failures are Step 11 issues (fixable without full restart)
- Don't assume user intent
- Restarting all 11 steps is extreme for consistency check

**Final Step 11 Flow:**
```
Steps 1-11: Complete ✅
  ↓
AI calls: run_test(test_path, env)
  ↓
AI calls: qg_execution(test_results, test_path, workflow_id)
  ↓
Test failed? → HITL triage → Fix code → Re-validate gates → RETRY run_test
  ↓
Test passed? → Continue
  ↓
AI calls: qg_workflow_complete(workflow_state)
  ↓
Consistency checks pass? → Workflow complete ✅
Consistency checks fail? → Escalate to human with options
```

---

## Success Criteria

**MVP is successful when:**

1. **Catches DEF-058 before user sees it**
   - Test fails → AI diagnoses → Fix applied → Test passes
   - User never sees "all gates passed" with broken test

2. **Demonstrates Smart Gate pattern**
   - AI provides fix data, not just errors
   - Human validates when needed
   - Clear progression: detect → diagnose → fix → verify

3. **Completes both goals**
   - ✅ Proves AI Management Layer thesis (execution enforcement)
   - ✅ Completes QA Execution Platform (tests that work)

4. **Ready for first users**
   - Workflow: user input → 11 steps → working test
   - Documentation: clear, complete
   - Distribution: pip install ready

---

## Non-Goals (Out of Scope for MVP)

- ❌ Complex failure diagnosis (ML-based pattern recognition)
- ❌ Historical learning (track fixes across workflows)
- ❌ Performance optimization (parallel test execution)
- ❌ Multi-test orchestration (test suites)
- ❌ CI/CD integration (that's later)
- ❌ Visual regression testing
- ❌ Advanced reporting/dashboards

Keep it simple: detect, diagnose, fix, verify.

---

## Technical Constraints

**Must work with:**
- Existing MCP architecture
- Current quality gate pattern (qg_*)
- State management system
- Pytest test runner
- Both Selenium and Playwright

**Cannot:**
- Break existing Steps 1-11
- Require new dependencies (use existing stack)
- Change established patterns (DD-25, DD-27, DD-49)
- Add significant latency (< 2 min for full Step 11)

---

## Design Decisions Summary

**Phase 1 (Design) is complete. All 6 questions answered:**

### Question 1: Diagnostic Data Capture
- ✅ 7 MVP data types (Test Execution, Page State, Browser Context, Expected vs Actual, Test Context, Test Data, Execution Flow)
- ✅ v2 enhancements documented (Environment, Timing, Network, App Logs)
- ✅ Extensible metadata structure with versioning (v1/v2)
- ✅ Playwright snapshot runs automatically on failure

### Question 2: QA Triage Workflow (HITL)
- ✅ AI presentation: SUGGESTIVE (analyzes data, suggests likely cause with confidence)
- ✅ Human input: HYBRID (AI provides options + user can give free text guidance)
- ✅ 3-option triage: App bug, Test issue, Investigate further
- ✅ AI presents diagnostic data formatted for decision-making

### Question 3: Code Fix Validation
- ✅ Dependency-aware re-validation (follow 4-layer chain: POM → Task → Role → Test)
- ✅ POST validation only (no PRE needed in Step 11)
- ✅ Gate failure threshold: 3 attempts → escalate
- ✅ Interface contract validation: NOT in MVP (skeleton approach handles this in future)
- ✅ Metadata regeneration: Extract from modified code, update workflow state

### Question 4: Retry Policy
- ✅ Same-error limit: 2 attempts → ask human
- ✅ Total attempt limit: 5 → confirm with human (not hard abort)
- ✅ No time limits (HITL controls pacing)
- ✅ Error signature tracking to detect same vs different errors

### Question 5: State Persistence
- ✅ Full diagnostic data capture (JSON size not an issue)
- ✅ Hybrid audit: Summary in workflow audit, detail in `tests/_audit/step11/` directory
- ✅ Learning patterns: v2 enhancement (data structure supports it)

### Question 6: Tool Architecture
- ✅ Three-tool architecture: `run_test` (operation) + `qg_execution` (step gate) + `qg_workflow_complete` (meta-gate)
- ✅ run_test as MCP tool (ensures consistent pytest params)
- ✅ qg_workflow_complete validates 8 cross-step consistency checks
- ✅ qg_workflow_complete failure: Escalate to human (not auto-restart)

---

## Impact Assessment ✅

**Completed:** 2026-01-13
**Document:** See `impact-assessment.md` for full 500+ line analysis

### Executive Summary

**Impact Level:** MODERATE (1 breaking change, 5 file updates)
**Risk Level:** LOW (additive design, fully backward compatible)
**Migration Path:** Clear 4-phase plan documented

### Breaking Change

**File:** `mcp_server/utils/state_manager.py:26`

```python
# BEFORE
VALID_STEPS = range(1, 11)  # 1-10 inclusive

# AFTER
VALID_STEPS = range(1, 12)  # 1-11 inclusive
```

**Risk:** LOW - Single constant change, backward compatible (existing workflows using steps 1-10 are unaffected)

### Files To Create (6 New Files)

**Implementation:**
```
mcp_server/tools/operations/run_test.py              (Execute pytest)
mcp_server/tools/gates/qg_execution.py               (Step 11 gate)
mcp_server/tools/gates/qg_workflow_complete.py       (Meta-gate)
```

**Testing:**
```
mcp_server/_dev_tests/test_gates/test_qg_execution.py
mcp_server/_dev_tests/test_gates/test_qg_workflow_complete.py
```

**Documentation:**
```
.claude/skills/qa-management-layer/references/step-11.md
```

### Files To Update (5 Files)

**Code (Non-Breaking):**
- `mcp_server/server.py` - Register 3 new tools
- `mcp_server/tools/gates/__init__.py` - Export 2 new gates

**Documentation:**
- `.claude/skills/qa-management-layer/SKILL.md` - Add Step 11 reference
- `FRAMEWORK.md` - Update Section 9 workflow diagram
- Multiple files - Change "11-step" to "11-step" references

### Backward Compatibility Analysis

| Component | Compatibility | Notes |
|-----------|---------------|-------|
| **State Files** | ✅ FULL | Old files (steps 1-10) remain valid |
| **Audit Files** | ✅ FULL | Progressive design extends naturally |
| **Existing Tests** | ✅ FULL | All tests use steps 1-10 (unchanged) |
| **Audit Logger** | ✅ NO CHANGE | Hook-based design (pattern: `qg_.*`) |
| **Step 10 Behavior** | ✅ NO CHANGE | Existing validation logic unchanged |

### What We Discovered About Current Step 10

**Current Gap (DEF-058 Root Cause):**
- Step 10 (`qg_save_run`) validates code is ready
- Test execution is OPTIONAL and UNVALIDATED
- User can complete workflow without running test
- Test failures not captured in quality gate system

**Step 11 Closes The Gap:**
- Makes test execution MANDATORY (blocking gate)
- Captures test results in audit trail
- Enables HITL triage (app bug vs test issue)
- Validates cross-step consistency (meta-gate)

### Migration Strategy: 4 Phases

**Phase 1: Core Implementation**
- Create 3 new tools (run_test, qg_execution, qg_workflow_complete)
- Register tools in server.py
- No breaking changes yet (tools available but not required)

**Phase 2: StateManager Extension**
- Update VALID_STEPS constant (breaking change)
- Run existing test suite (verify backward compatibility)
- Add Step 11 tests

**Phase 3: Documentation**
- Create step-11.md reference
- Update SKILL.md, FRAMEWORK.md
- Search & replace "11-step" → "11-step"

**Phase 4: Integration Testing**
- Happy path E2E (test passes)
- Test failure - app bug triage
- Test failure - test issue triage
- qg_workflow_complete validation
- Backward compatibility test

### Success Criteria

**Step 11 implementation is successful when:**

1. ✅ All existing tests pass (backward compatibility confirmed)
2. ✅ New Step 11 tests pass (functionality validated)
3. ✅ 11-step E2E workflow completes successfully
4. ✅ HITL triage workflow works (app bug vs test issue)
5. ✅ qg_workflow_complete catches consistency issues
6. ✅ Audit trail includes Step 11 data
7. ✅ Old 11-step state files still readable
8. ✅ Documentation updated ("11-step" → "11-step")
9. ✅ StateManager accepts step 11 data

### Key Insight: Current Step 10 Design

**What Step 10 Actually Does:**
1. Validates Step 9 complete
2. Validates all 4 code blocks present (POM, Task, Role, Test)
3. Validates no skeleton code
4. Validates all generated files exist on disk
5. Validates test data files exist
6. Clears session marker
7. Returns PASS → **Workflow ends**

**What Step 10 Does NOT Do:**
- ❌ Does NOT run tests
- ❌ Does NOT validate test execution
- ❌ Does NOT capture test results

**Documentation vs Reality Gap:**
- Documentation (step-10.md) says: "ASK user: Ready to run test? → RUN pytest"
- Implementation (qg_save_run.py) does: Validates code ready → PASS → Workflow ends
- **Result:** Test execution optional, failures undetected (DEF-058)

**Step 11 is NOT a replacement for Step 10:**
- Step 10: Validates CODE is ready (structure, patterns, files)
- Step 11: Validates EXECUTION works (test passes, app works)
- Both are necessary: Code correctness + Runtime correctness

---

## Next Phase: Define (PRD)

With design decisions AND impact assessment complete, Phase 2 will create the PRD (Product Requirements Document):

**PRD will specify:**
1. Tool signatures (run_test, qg_execution, qg_workflow_complete)
2. Metadata schemas (diagnostic_data structure, audit structure)
3. Gate validation logic (qg_execution rules, qg_workflow_complete checks)
4. HITL interaction flows (triage presentation, option selection)
5. State management (metadata regeneration, audit file structure)
6. Success criteria (functional, performance, UX)

**Ready to move to Phase 2?**

