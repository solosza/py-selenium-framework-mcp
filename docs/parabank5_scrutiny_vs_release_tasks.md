# Parabank5 Scrutiny Results vs Release-Readiness Task List

**Date:** 2026-01-09
**Purpose:** Map parabank5 scrutiny findings to existing tasks, identify gaps, propose consolidated v0.2 MVP plan

---

## Executive Summary

**Total Issues Found:** 34 (4 CRITICAL, 5 HIGH, 8 MEDIUM, 9 LOW, 4 GATE FAILURES, 4 ARCHITECTURAL)

**Already Covered by Existing Tasks:** 8 issues (24%)
**Partially Covered (Skeleton-Only):** 6 issues (18%)
**NEW WORK REQUIRED:** 20 issues (58%)

**Key Finding:** Skeleton-only architecture (Tasks 28-35) addresses structural issues, but **business logic validation gaps** are the bigger problem.

---

## Issue Mapping: What's Already Covered

### ✅ Fully Covered by Completed Tasks

| Issue # | Scrutiny Finding | Covered By | Status |
|---------|------------------|------------|--------|
| #28 | Audit Trail Incomplete | Task 1.0 (Audit Trail System) | ✅ DONE |
| #2 partial | Self-heal cap needed | Task 2.0 (Self-Heal Cap) | ✅ DONE |
| #6 partial | Missing required fields | Tasks 9-18 (Gate refactors) | ✅ DONE |

**Analysis:** Foundation tasks (1.0-3.0, 7.0-25.0) addressed infrastructure issues but not business logic validation.

---

### 🔶 Partially Covered by Planned Work

| Issue # | Scrutiny Finding | Will Be Addressed By | Notes |
|---------|------------------|---------------------|-------|
| **#5** | LoginPage generation failure | **Task 26.0 (Navigation Tracking)** | ✅ DIRECTLY FIXES multi-page detection! |
| #8 | Wrong WebInterface method used | Task 30.0 (POM generator refactor) | Skeleton + pattern provision |
| #9 | Wrong expected states assignment | Task 30.0 + Task 28.0 (Protocol updates) | Gates will provide correct patterns |
| #13 | Duplicate unused locator | Task 30.0 (Skeleton-only POM) | Only generates used locators |
| #14 | Unused navigate() method | Task 30.0 (Skeleton-only POM) | AI fills only needed methods |
| #26 | Self-heal masking tool issues | Tasks 30-34 (Skeleton-only generators) | Reduces tool complexity |

**Analysis:** Skeleton-only architecture (Tasks 28-35) will reduce **structural/code quality issues** but won't fix **business logic validation**.

---

## Critical Gaps: NEW WORK REQUIRED

### 🔴 CRITICAL PRIORITY (Blocks v0.2 MVP)

#### Gap 1: Business Logic Validation Gates (Issues #1, #2, #3, #4)

**Problem:**
- Test transfers from same account to same account (passes but meaningless)
- Credential strategy "self-contained" selected but test uses hardcoded discovery credentials
- Test data location "workflow" selected but no data files created
- Account IDs hardcoded from discovery session (not portable)

**Root Cause:** Gates validate **structure** (syntax, imports, patterns) but not **semantics** (business logic, strategy adherence).

**Current Behavior:**
```python
# Test generates this (WRONG):
user.transfer_funds_between_accounts(
    amount="100",
    from_account="15564",  # Same account!
    to_account="15564"     # Same account!
)

# qg_test_runner POST validates:
✓ Has AAA pattern
✓ Uses POM state methods for assertions
✓ Imports correct
# ❌ Does NOT validate: from_account != to_account
```

**What's Missing:**
- `qg_test_runner` needs **semantic validation**
- `qg_role` needs to enforce credential strategy from Step 1
- `qg_test_runner` needs to enforce test data strategy from Step 1
- `qg_test_runner` needs to validate parameter values make business sense

**Proposed Solution:** **NEW Task 36.0: Smart Gate Semantic Validation**

---

#### Gap 2: Step 1 Strategy Enforcement (Issues #2, #3)

**Problem:**
- Step 1 (qg_preflight) CAPTURES strategies (credential_strategy, test_data_location)
- But Steps 6-9 gates DON'T ENFORCE them

**Current State Check:**
```python
# Step 1 saves:
state.save(1, {
    "credential_strategy": "self-contained",  # User selected
    "test_data_location": "workflow"          # User selected
})

# Step 9 validation:
# ❌ Doesn't check if test honors self-contained
# ❌ Doesn't check if data files created in tests/parabank5/data/
```

**What's Missing:**
- `qg_role` POST needs to validate credentials match strategy
- `qg_test_runner` POST needs to validate test data location matches strategy
- `qg_save_run` PRE needs to validate expected data files exist

**Proposed Solution:** **Enhance Tasks 17.0 (qg_role), 18.0 (qg_test_runner), 19.0 (qg_save_run)** with strategy enforcement

---

### 🟠 HIGH PRIORITY (Stability Issues)

#### Gap 3: Discovery Session Isolation (Issues #7, #11)

**Problem:**
- Step 5 discovery creates REAL user accounts in target application
- Step 5 Playwright conflicts (browser already in use)
- Discovery pollutes application state

**Current Behavior:**
```
Step 5: AI uses Playwright to discover elements
    ↓
AI navigates to registration page
    ↓
AI fills form with testuser20260108 / Test123!
    ↓
✅ User CREATED in ParaBank (SIDE EFFECT!)
    ↓
Step 9: Test hardcodes these credentials
```

**What's Missing:**
- Discovery should use **mock/snapshot** approach, not live interaction
- Playwright browser lifecycle management (cleanup)
- Discovery session should be **read-only**

**Proposed Solution:** **NEW Task 37.0: Discovery Session Isolation**

---

#### Gap 4: Comprehensive Gate Pre-Validation (Issue #6)

**Problem:**
- Gates validate POST (after tool executes) but not PRE comprehensively
- AI has to retry multiple times for missing fields

**Examples from Transcript:**
```
Step 7: Missing workflow → Retry
Step 7: Missing task_name → Retry
Step 8: Missing role_name → Retry
Step 9: Missing test_scenarios → Retry
Step 9: Missing class_name → Retry
```

**What's Missing:**
- PRE gates should validate **all required context** upfront
- Gates should provide **fix data** on first failure, not after retries

**Proposed Solution:** **Enhance all PRE gates** (covered by Smart Gate pattern in Tasks 22-23, extend to all gates)

---

### 🟡 MEDIUM PRIORITY (Quality Issues)

#### Gap 5: Step 2 URL Path Validation (Issue #10)

**Problem:**
- User provided URL: `https://parabank.parasoft.com`
- Test failed because correct URL is: `https://parabank.parasoft.com/parabank`
- qg_user_input didn't validate path

**What's Missing:**
- URL validation should check for missing paths
- Should suggest adding base path if root domain provided

**Proposed Solution:** **Enhance Task 10.0 (qg_user_input)** with URL path validation

---

#### Gap 6: Business Logic Assertions (Issue #12)

**Problem:**
- Test checks UI (is_transfer_confirmed) but not business logic (balance changed)
- Gates don't enforce "verify actual system state change"

**Example:**
```python
# Test does:
assert confirmation_page.is_transfer_confirmed()  # ✓ UI check
assert confirmation_page.get_transfer_amount() == "$100.00"  # ✓ UI check

# Test SHOULD do:
assert source_account.get_balance() == initial_balance - 100  # ❌ Missing
assert dest_account.get_balance() == initial_balance + 100    # ❌ Missing
```

**What's Missing:**
- `qg_test_runner` should detect "state change" tests and require balance/data verification
- Step 9 protocol should guide AI to add business logic assertions

**Proposed Solution:** **Enhance Task 18.0 (qg_test_runner)** + **Task 29.0 (step-09.md protocol)**

---

### 🔵 ARCHITECTURAL (Technical Debt)

#### Gap 7: Rollback on Partial Failure (Issue #27)

**Problem:**
- If Step 7 fails after Steps 6 POMs generated, what happens to orphaned files?
- No cleanup mechanism shown

**What's Missing:**
- Atomic workflow execution (all-or-nothing)
- Rollback mechanism to delete partial artifacts
- State tracking for "dirty" runs

**Proposed Solution:** **NEW Task 38.0: Workflow Rollback Mechanism**

---

## Proposed Consolidated Task Plan for v0.2 MVP

### Phase 1: Fix Critical Blockers (Tasks 36-37)

**Task 36.0: Smart Gate Semantic Validation** [CORE]
- Subtask 36.1: Add business logic validation to qg_test_runner
  - Detect transfer scenarios → validate from_account != to_account
  - Detect balance checks → ensure before/after assertions
  - Detect workflow operations → validate parameters realistic
- Subtask 36.2: Add credential strategy enforcement to qg_role
  - If "self-contained" → test must register user within test
  - If "static" → test must use test_users fixture
  - If "dynamic" → test must register, save to config, use in subsequent tests
- Subtask 36.3: Add test data strategy enforcement to qg_test_runner
  - If "workflow" → validate tests/{workflow}/data/ files created
  - If "shared" → validate tests/data/ files used
  - If "both" → validate both locations have appropriate data
- Subtask 36.4: Add semantic validation to qg_save_run PRE
  - Verify credential files exist based on strategy
  - Verify test data files exist based on strategy

**Done When:**
- parabank5 re-run catches same-account transfer (FAIL)
- parabank5 re-run catches hardcoded credentials violation (FAIL)
- parabank5 re-run catches missing workflow data files (FAIL)
- AI must fix all 3 to pass gates

**Dependency:** None (can start immediately)

---

**Task 37.0: Discovery Session Isolation** [CORE]
- Subtask 37.1: Add read-only discovery mode to Step 5
  - Playwright runs in snapshot mode (capture DOM, no interaction)
  - OR use existing accounts from test data for discovery
  - No writes to target application during discovery
- Subtask 37.2: Fix Playwright browser lifecycle
  - Ensure browser closes after Step 5
  - Add cleanup to handle "browser already in use" errors
  - Add timeout/retry logic
- Subtask 37.3: Update step-05.md protocol
  - Document read-only discovery requirement
  - Guide AI to use existing accounts, not create new ones

**Done When:**
- Step 5 discovery doesn't create accounts in target application
- Playwright browser conflicts resolved
- parabank5 re-run uses existing test account for discovery

**Dependency:** Task 26.0 (navigation tracking) - can run in parallel

---

### Phase 2: Strengthen Existing Work (Enhance Released Tasks)

**Task 39.0: Comprehensive PRE Gate Validation** [CORE]
- Subtask 39.1: Audit all PRE gates for missing field checks
- Subtask 39.2: Add fix data provision on first failure (no retry loops)
- Subtask 39.3: Update PRE gates: qg_task, qg_role, qg_test_runner
- Subtask 39.4: Add unit tests for all missing field scenarios

**Done When:**
- No retry loops for missing fields
- Gates provide fix data on first validation failure

**Dependency:** Builds on Tasks 22-23 pattern

---

**Task 40.0: URL Path Validation** [GLUE]
- Subtask 40.1: Enhance qg_user_input to validate URL paths
- Subtask 40.2: Suggest base path if root domain provided
- Subtask 40.3: Add unit tests for URL validation

**Done When:**
- qg_user_input rejects `https://parabank.parasoft.com` without path
- Suggests adding `/parabank` if missing

**Dependency:** None

---

**Task 41.0: Business Logic Assertion Enforcement** [CORE]
- Subtask 41.1: Detect state-change operations in test scenarios
- Subtask 41.2: Require before/after assertions for balance/data changes
- Subtask 41.3: Update step-09.md protocol with business logic guidance
- Subtask 41.4: Enhance qg_test_runner POST to validate assertions

**Done When:**
- Transfer tests require balance assertions
- Gates block tests that only check UI, not business state

**Dependency:** Task 36.0 (semantic validation)

---

### Phase 3: Technical Debt (Tasks 42+)

**Task 42.0: Workflow Rollback Mechanism** [ARCHITECTURAL]
- Subtask 42.1: Add transaction-like state tracking
- Subtask 42.2: Implement rollback on gate failure
- Subtask 42.3: Clean up orphaned files
- Subtask 42.4: Add rollback unit tests

**Done When:**
- If Step 7 fails, Step 6 POMs are deleted
- Workflow state rolled back to last successful step

**Dependency:** Can defer to post-v0.2

---

## Updated Release-Readiness Task List Structure

### Recommendation: Insert New Tasks BEFORE Skeleton-Only

**Rationale:**
- Skeleton-only (Tasks 28-35) addresses **structural issues**
- New Tasks 36-42 address **business logic issues**
- Business logic validation is **higher priority** for MVP
- Skeleton-only is **architectural improvement**, not blocker

**Proposed Order:**
```
Tasks 1-25: ✅ DONE (Foundation + Production Fixes)
Task 26: 🟡 IN PLANNING (Navigation Tracking)
Task 27: ⬜ PENDING (Shift-Left Testing)

NEW MVP BLOCKERS:
Task 36: 🔴 CRITICAL (Smart Gate Semantic Validation)
Task 37: 🔴 CRITICAL (Discovery Session Isolation)
Task 39: 🟠 HIGH (Comprehensive PRE Gate Validation)
Task 40: 🟡 MEDIUM (URL Path Validation)
Task 41: 🟡 MEDIUM (Business Logic Assertion Enforcement)

ARCHITECTURAL IMPROVEMENTS (Post-MVP):
Task 28-35: ⬜ PENDING (Skeleton-Only Architecture) - renumber to 42-49
Task 42: ⬜ PENDING (Workflow Rollback) - renumber to 50
```

---

## Test-in-Production Strategy (Per User Request)

**Approach:** Complete one task → Test with parabank5 workflow → Verify fix → Move to next task

### Task 36.0 Testing Plan:
1. Implement semantic validation gates
2. Re-run parabank5 workflow
3. **Expected:** Gates FAIL on:
   - Same account transfer
   - Hardcoded credentials
   - Missing workflow data
4. AI must fix all 3
5. **Success:** Test passes with:
   - Different from/to accounts
   - Self-contained user registration
   - Workflow data files created

### Task 37.0 Testing Plan:
1. Implement read-only discovery
2. Check ParaBank before/after Step 5
3. **Expected:** No new user accounts created
4. **Expected:** Playwright browser cleanup works
5. **Success:** Discovery uses existing test account

### Task 39.0 Testing Plan:
1. Enhance PRE gates
2. Re-run parabank5
3. **Expected:** No retry loops for missing fields
4. **Expected:** Gates provide fix data on first failure
5. **Success:** Workflow completes without repeated validation errors

---

## Gap Summary Table

| Gap # | Issue | Severity | Covered By Existing? | New Task Needed? |
|-------|-------|----------|---------------------|------------------|
| 1 | Business logic validation | CRITICAL | ❌ No | ✅ Task 36.0 |
| 2 | Strategy enforcement | CRITICAL | ❌ No | ✅ Task 36.0 |
| 3 | Discovery isolation | HIGH | ❌ No | ✅ Task 37.0 |
| 4 | PRE gate validation | HIGH | 🔶 Partial (22-23) | ✅ Task 39.0 |
| 5 | URL path validation | MEDIUM | ❌ No | ✅ Task 40.0 |
| 6 | Business assertions | MEDIUM | ❌ No | ✅ Task 41.0 |
| 7 | Rollback mechanism | ARCHITECTURAL | ❌ No | ✅ Task 42.0 (defer) |

---

## v0.2 MVP Scope Recommendation

**MUST HAVE (Blocks v0.2):**
- ✅ Task 26.0: Navigation Tracking (fixes LoginPage issue #5)
- ✅ Task 36.0: Semantic Validation (fixes issues #1-4)
- ✅ Task 37.0: Discovery Isolation (fixes issues #7, #11)

**SHOULD HAVE (Quality):**
- ✅ Task 39.0: PRE Gate Validation (reduces retry loops)
- ✅ Task 40.0: URL Validation (better UX)

**NICE TO HAVE (Polish):**
- ⬜ Task 41.0: Business Logic Assertions (defer to v0.3)

**DEFER TO POST-MVP:**
- ⬜ Tasks 28-35: Skeleton-Only Architecture (v0.3+)
- ⬜ Task 42.0: Rollback Mechanism (v0.3+)

---

## Estimated Effort

| Task | Complexity | Estimated Hours | Test Time |
|------|-----------|-----------------|-----------|
| 26.0 | LOW | 3 hours | 1 hour |
| 36.0 | HIGH | 8 hours | 2 hours |
| 37.0 | MEDIUM | 5 hours | 1 hour |
| 39.0 | MEDIUM | 4 hours | 1 hour |
| 40.0 | LOW | 2 hours | 30 min |
| **Total** | | **22 hours** | **5.5 hours** |

**Total v0.2 MVP Effort:** ~27.5 hours (3-4 days with testing)

---

## Verdict: Can We Consolidate?

**YES** - High consolidation opportunity:

1. **Task 26.0 (already planned)** directly fixes Issue #5 ✅
2. **Skeleton-only tasks (28-35)** address 6 structural issues ✅
3. **NEW Task 36-37** address 9 critical/high issues ✅
4. **Enhancement Tasks 39-41** address 5 medium issues ✅

**What You Get:**
- Fix 20/34 scrutiny issues with 5 new tasks
- Leverage existing skeleton-only work for 6 more issues
- Defer 8 low-severity polish issues to post-MVP

**Ship Strategy:**
1. Complete Tasks 26, 36, 37 → Test parabank5 → Ship v0.2 MVP
2. Complete Tasks 39-40 → Test parabank5 → Ship v0.2.1
3. Complete Tasks 28-35 → Test parabank5 → Ship v0.3 (Architecture Upgrade)

This is **absolutely shippable as v0.2 MVP** after Tasks 26, 36, 37.
