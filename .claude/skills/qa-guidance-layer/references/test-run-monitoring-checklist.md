# Test Run Monitoring Checklist

**Purpose:** Systematic validation checklist for every 10-step workflow test run
**Audience:** Test observers, QA validators, protocol improvement team
**Version:** 1.0
**Last Updated:** 2026-01-11

---

## Pre-Run Verification

**Before starting test run, verify:**

```
□ MCP servers running (qa-automation, playwright)
□ Working directory correct (D:\my_ai_projects\py_sel_framework_mcp)
□ Target site accessible
□ Previous test artifacts archived (if needed)
□ Protocol version noted: [v1.0 | v1.1 | v1.X]
□ Test parameters documented (workflow_name, target_site, etc.)
```

---

## Session Management Monitoring

### Run ID Tracking

```
□ Step 1: Note initial run_id from qg_preflight: [_____________]
□ Step 2-4: Verify same run_id used
□ Step 5-9: Verify same run_id used
□ Step 10: Verify same run_id used
□ If agent resumed: Note new run_id (if created): [_____________]
□ Final: How many audit files created? [1 | 2 | 3+]
```

**Expected:** 1 audit file if no resume, 2+ if resumed
**Issue if:** Run_id changes mid-workflow without resume

### State File Verification

```
□ Check: mcp_server/state/.run_session exists? [Y/N]
□ Contents: [paste run_id from file]
□ Updated when: [timestamp of last modification]
```

---

## File Write Timing (CRITICAL - Observed Behavior)

### Step 6: POM Generation

```
□ Tool 3 generates code for POM 1: [Y/N]
□ File written to disk immediately after generation: [Y/N]
  - Path: framework/pages/{workflow}/[filename]
  - Timestamp: [HH:MM:SS]
□ Tool 3 generates code for POM 2 (if multi-page): [Y/N]
□ File written to disk immediately: [Y/N]
  - Path: framework/pages/{workflow}/[filename]
  - Timestamp: [HH:MM:SS]
```

### Step 7: Task Generation

```
□ Tool 4 generates Task code: [Y/N]
□ File written to disk immediately: [Y/N]
  - Path: framework/tasks/{workflow}/[filename]
  - Timestamp: [HH:MM:SS]
```

### Step 8: Role Generation

```
□ Tool 5 generates Role code: [Y/N]
□ File written to disk immediately: [Y/N]
  - Path: framework/roles/[filename]
  - Timestamp: [HH:MM:SS]
```

### Step 9: Test Generation

```
□ Tool 6 generates Test code: [Y/N]
□ File written to disk immediately: [Y/N]
  - Path: tests/{workflow}/[filename]
  - Timestamp: [HH:MM:SS]
```

### Step 10: File Handling

```
□ Does Step 10 re-save files? [Y/N]
□ Or just validates existing files? [Y/N]
□ Are all files present before test execution? [Y/N]
```

**Analysis:** Files written [incrementally after each tool | all at once in Step 10 | mixed]

---

## Quality Gate Execution (All 20 Gates)

### Step 1: Pre-flight
```
□ qg_preflight (POST) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

### Step 2: User Input
```
□ qg_user_input (POST) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

### Step 3: AI Processing
```
□ qg_ai_processing (POST) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

### Step 4: Test Scenarios
```
□ qg_test_scenarios (PRE) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]

□ qg_test_scenarios (POST) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

### Step 5: Element Discovery
```
□ qg_discovered_elements (PRE) called: [Y/N]
□ Status: [pass | fail | self-heal]
□ If multi-page: scope_result provided: [Y/N]
□ Timestamp: [HH:MM:SS]

□ qg_discovered_elements (POST) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

### Step 6: POM Generation
```
□ qg_page_object (PRE) for POM 1 called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]

□ qg_page_object (POST) for POM 1 called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]

□ qg_page_object (PRE) for POM 2 called (if multi-page): [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]

□ qg_page_object (POST) for POM 2 called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

### Step 7: Task Generation
```
□ qg_task (PRE) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]

□ qg_task (POST) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

### Step 8: Role Generation
```
□ qg_role (PRE) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]

□ qg_role (POST) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

### Step 9: Test Generation
```
□ qg_test_runner (PRE) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]

□ qg_test_runner (POST) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

### Step 10: Save & Run
```
□ qg_save_run (PRE) called: [Y/N]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]

□ qg_save_run (POST) called: [Y/N] [Expected: may not exist]
□ Status: [pass | fail]
□ Timestamp: [HH:MM:SS]
```

**Gate Summary:**
- Total gates called: [___/20]
- Total passed: [___]
- Total failed: [___]
- Self-heals triggered: [___]

---

## Audit Trail Completeness

### Audit File Structure

```
□ Audit file(s) created: [list paths]
□ Primary run_id: [_____________]
□ Secondary run_id (if resumed): [_____________]

□ Each audit file has:
  - run_id field: [Y/N]
  - execution_mode field: [Y/N]
  - steps array: [Y/N]
  - files_generated array: [Y/N]
  - summary object: [Y/N]
```

### Audit Entries Per Step

```
□ Step 1: Gate result logged: [Y/N]
□ Step 2: Gate result logged: [Y/N]
□ Step 3: Gate result logged: [Y/N]
□ Step 4: PRE + POST gates logged: [Y/N]
□ Step 5: PRE + POST gates logged: [Y/N]
□ Step 5: Browser navigate calls logged: [Y/N] [Expected: NO for MVP]
□ Step 6: All POM gates logged: [Y/N]
□ Step 7: PRE + POST gates logged: [Y/N]
□ Step 8: PRE + POST gates logged: [Y/N]
□ Step 9: PRE + POST gates logged: [Y/N]
□ Step 10: PRE gate logged: [Y/N]
□ Step 10: Test execution result logged: [Y/N] [CRITICAL]
```

### Audit Metadata Accuracy

**Step 5 POST gate metadata:**
```
□ pages_discovered: [value from audit]
□ total_pages: [value from audit]
□ discovery_complete: [value from audit]
□ Does this match actual pages discovered? [Y/N]
```

**Step 6-9 POST gate metadata:**
```
□ Step 6: Method counts accurate? [Y/N]
□ Step 7: Task methods count accurate? [Y/N]
□ Step 8: Role methods count accurate? [Y/N]
□ Step 9: Test file path correct? [Y/N]
```

**Audit Summary:**
```
□ total_steps: [value] (Expected: 10 if complete)
□ gates_passed: [value]
□ gates_failed: [value]
□ final_result: [pass | fail]
```

---

## Navigation Tracking Validation (Task 26.0)

**Only applicable for multi-page workflows**

### Browser Navigation

```
□ Step 5: Real browser_navigate calls made: [Y/N]
□ URLs navigated to: [list]
□ Number of pages: [___]
```

### PRE Gate Detection

```
□ PRE gate detected multi-page: [Y/N]
□ PRE gate returned scope_result: [Y/N]
□ scope_result.page_count: [___]
□ All pages have "reason": "navigation detected": [Y/N]
□ Page names inferred from URLs: [Y/N]
□ Page name format: [PascalCase | other]
```

### Self-Healing

```
□ Self-healing provided scope_result automatically: [Y/N]
□ No explicit scope_discovery call needed: [Y/N]
```

**Navigation Tracking Status:** [✓ VALIDATED | ✗ FAILED | N/A (single-page)]

---

## Code Quality Validation

### Skeleton Code Detection (DD-25)

```
□ Any POM has NotImplementedError: [Y/N]
□ Any POM has "pass" only methods: [Y/N]
□ Any POM has "# TODO" comments: [Y/N]

□ Task has skeleton code: [Y/N]
□ Role has skeleton code: [Y/N]
□ Test has skeleton code: [Y/N]
```

**Expected:** NO skeleton code in any module

### Locator Placement (DD-27)

```
□ POMs have locators: [Y/N] (Expected: YES)
□ Task has locators: [Y/N] (Expected: NO)
□ Role has locators: [Y/N] (Expected: NO)
□ Test has locators: [Y/N] (Expected: NO)
```

**Violations found:** [list if any]

### Return Value Check (IC-07-02)

```
□ Task methods have return values: [Y/N] (Expected: NO)
□ Role methods have return values: [Y/N] (Expected: NO)
```

**Violations found:** [list if any]

### Decorator Check (IC-07-04)

```
□ Task methods have @autologger("Task"): [Y/N]
□ Role constructor has @autologger("Role Constructor"): [Y/N]
□ Role methods have @autologger("Role"): [Y/N]
□ Test has @autologger("Test"): [Y/N]
□ POMs have NO decorators: [Y/N]
```

**Violations found:** [list if any]

### Navigation Responsibility (DD-49)

```
□ POMs have navigate() method: [Y/N]
□ POMs use self.web.config['url']: [Y/N]
□ Tasks call pom.navigate(): [Y/N]
□ Tasks do NOT call self.web.navigate_to(): [Y/N]
□ Roles do NOT navigate directly: [Y/N]
```

**Violations found:** [list if any]

### Framework Pattern Check

```
□ /framework-check command executed: [Y/N]
□ When executed: [before test | after test | not at all]
□ Result: [X passed, Y failed]
□ Violations: [list if any]
```

---

## Environment Correctness (CRITICAL)

### Environment Configuration

```
□ Target site from parameters: [URL]
□ Workflow name from parameters: [workflow_name]
□ Credential strategy: [static | dynamic | self-contained | none]
□ Test data location: [shared | workflow-specific | both | none]
```

### Config File Detection

```
□ Config file expected: framework/resources/config/[workflow_name]_config.json
□ Config file exists: [Y/N]
□ If not, DEFAULT config used: [Y/N]
□ DEFAULT config file: [path]
```

### Environment Flag Validation

```
□ Pytest command includes --env flag: [Y/N]
□ Flag value: [--env=X | not provided]
□ Flag matches workflow_name: [Y/N]
□ If no flag, DEFAULT environment loaded: [Y/N]
```

**Expected:** `pytest --env={workflow_name}` should load `{workflow_name}_config.json`

### Base URL Correctness

```
□ Config base URL: [URL from loaded config]
□ Target site (from parameters): [URL from test parameters]
□ URLs match: [Y/N]
□ Test navigated to correct site: [Y/N]
□ If mismatch, test navigated to: [actual URL]
```

**Example Issue:**
```
Target: https://parabank.parasoft.com/parabank
Config loaded: DEFAULT (automationpractice.pl)
Test navigated to: http://www.automationpractice.pl ← WRONG
```

### Credential Configuration

```
□ Credential strategy from parameters: [static | dynamic | self-contained | none]
□ If static, credential file expected: tests/data/test_users.json
□ Credential file exists: [Y/N]
□ Test used credentials from correct file: [Y/N]
□ Credentials field names match app: [Y/N] (e.g., username vs email)
```

### Test Data Location Correctness

```
□ Test data location from parameters: [shared | workflow-specific | both | none]
□ If shared: tests/data/ files loaded: [Y/N]
□ If workflow-specific: tests/{workflow}/data/ files loaded: [Y/N]
□ Test loaded data from correct location: [Y/N]
```

### Browser Configuration

```
□ Browser from parameters: [chrome | firefox | edge]
□ Browser config loaded: [browser name]
□ Browsers match: [Y/N]
□ Headless from parameters: [true | false]
□ Headless config loaded: [true | false]
□ Settings match: [Y/N]
```

### Environment Mismatch Detection

**Common mismatches to check:**

```
□ Test navigates to wrong site (URL mismatch): [Y/N]
□ Test uses wrong credentials (file not found): [Y/N]
□ Test loads wrong data (folder mismatch): [Y/N]
□ Browser setting mismatch (headless vs headed): [Y/N]
```

**If ANY mismatch detected:**
- Root cause: [--env flag missing | config file missing | wrong flag value | other]
- Impact: [test failed | test passed on wrong site | wrong data used]
- Fix: [add --env flag | create config | fix flag value]

### Environment Debug Commands

**To verify environment correctness, run:**

```bash
# Check what config exists
ls framework/resources/config/

# Check DEFAULT config
cat framework/resources/config/environment_config.json

# Check workflow-specific config
cat framework/resources/config/{workflow_name}_config.json

# Verify credential files
ls tests/data/
cat tests/data/test_users.json

# Verify workflow-specific data
ls tests/{workflow_name}/data/
```

### Environment Validation Checklist

**Before test execution, verify:**

```
□ Config file for workflow exists OR test uses DEFAULT intentionally
□ --env flag matches workflow_name
□ Base URL in config matches target_site
□ Credential file exists (if static strategy)
□ Test data files exist in expected location
□ Browser config matches parameters
```

**Expected behavior:**
- If `workflow_name="parabank"` → pytest should use `--env=parabank` → loads `parabank_config.json`
- Base URL from config should match `target_site` parameter
- Test should navigate to correct site

**Common failure modes:**
1. **No --env flag** → DEFAULT config loaded → wrong site
2. **Wrong --env value** → Wrong config loaded → wrong site
3. **Config file missing** → DEFAULT fallback → wrong site
4. **Credential field mismatch** → Test fails (username vs email)
5. **Test data in wrong location** → FileNotFoundError

---

## Test Execution Monitoring

### Test Run Details

```
□ Pytest command: [paste exact command]
□ Environment flag used: [--env=X | none]
□ Browser: [chrome | firefox | edge]
□ Headless: [true | false]
□ Start time: [HH:MM:SS]
□ End time: [HH:MM:SS]
□ Duration: [XX.XXs]
```

### Test Results

```
□ Test status: [PASSED | FAILED | ERROR | SKIPPED]
□ Tests run: [___]
□ Passed: [___]
□ Failed: [___]
□ Errors: [___]

□ HTML report generated: [Y/N]
□ Report path: [path]
□ Screenshots captured (if failure): [Y/N]
```

### Test Output Analysis

```
□ Import errors: [Y/N] - [list if any]
□ Fixture errors: [Y/N] - [list if any]
□ Assertion errors: [Y/N] - [list if any]
□ Element not found errors: [Y/N] - [list if any]
□ Timeout errors: [Y/N] - [list if any]
```

### Test Execution in Audit

```
□ Step 10 audit entry includes test result: [Y/N]
□ Test status in audit: [pass | fail | not recorded]
□ Test duration in audit: [Y/N]
□ Pytest output in audit metadata: [Y/N]
```

**Expected:** Step 10 should log test execution result in audit trail

---

## Agent Behavior Monitoring

### Completion Criteria

```
□ Agent reported "All 10 steps complete": [Y/N]
□ Agent stopped prematurely: [Y/N]
□ If stopped, at which step: [___]
□ Reason for stopping: [token limit | completion criteria | error | other]
```

### Checkpoint Validation

```
□ Agent reported checkpoint after Step 1: [Y/N]
□ Agent reported checkpoint after Step 2: [Y/N]
□ Agent reported checkpoint after Step 3: [Y/N]
□ Agent reported checkpoint after Step 4: [Y/N]
□ Agent reported checkpoint after Step 5: [Y/N]
□ Agent reported checkpoint after Step 6: [Y/N]
□ Agent reported checkpoint after Step 7: [Y/N]
□ Agent reported checkpoint after Step 8: [Y/N]
□ Agent reported checkpoint after Step 9: [Y/N]
□ Agent reported checkpoint after Step 10: [Y/N]
```

**Expected:** Agent reports after EVERY step

### Error Handling

```
□ Any gate failures encountered: [Y/N]
□ If yes, agent stopped: [Y/N]
□ Agent reported error clearly: [Y/N]
□ Agent waited for user direction: [Y/N]
□ Agent attempted auto-fix: [Y/N] (Expected: NO)
```

### Protocol Adherence

```
□ Agent confirmed protocol read at start: [Y/N]
□ Agent listed 10 steps before starting: [Y/N]
□ Agent stated critical requirements: [Y/N]
□ Agent acknowledged error handling: [Y/N]
```

**Expected:** Agent confirms understanding before execution (Rule 10)

---

## Resume Behavior (If Applicable)

**If agent was resumed:**

```
□ Resume agent ID: [_____________]
□ Resumed from step: [___]
□ New run_id created: [Y/N]
□ If yes, new run_id: [_____________]
□ State preserved from previous run: [Y/N]
□ Metadata context preserved: [Y/N]
□ Files from previous steps still present: [Y/N]
```

---

## Performance Metrics

```
□ Total workflow duration: [___] minutes
□ Step 1 duration: [___]s
□ Step 2 duration: [___]s
□ Step 3 duration: [___]s
□ Step 4 duration: [___]s
□ Step 5 duration: [___]s (usually longest - element discovery)
□ Step 6 duration: [___]s
□ Step 7 duration: [___]s
□ Step 8 duration: [___]s
□ Step 9 duration: [___]s
□ Step 10 duration: [___]s

□ Token usage: [___]K / 200K ([___]% used)
□ Agent stopped due to token limit: [Y/N]
```

**Performance Assessment:** [fast <5 min | normal 5-15 min | slow >15 min]

---

## Workflow Name Management

```
□ Workflow name used: [_____________]
□ Workflow name unique: [Y/N]
□ If not unique, files overwritten: [Y/N]
□ Existing folders detected:
  - framework/pages/{workflow}: [existed | new]
  - framework/tasks/{workflow}: [existed | new]
  - framework/roles/{workflow}: [existed | new]
  - tests/{workflow}: [existed | new]
```

---

## Post-Run Verification

### File Existence

```
□ All POMs exist on disk: [Y/N]
□ Task file exists: [Y/N]
□ Role file exists: [Y/N]
□ Test file exists: [Y/N]
□ HTML report exists: [Y/N]
□ Audit log(s) exist: [Y/N]
```

### File Sizes

```
□ POM 1 size: [___] bytes (Expected: >1KB)
□ POM 2 size: [___] bytes (if applicable)
□ Task size: [___] bytes (Expected: >1KB)
□ Role size: [___] bytes (Expected: >1KB)
□ Test size: [___] bytes (Expected: >1KB)
```

**Red flag:** Any file <500 bytes likely skeleton/incomplete

### Import Path Validation

```
□ Manually verify imports resolve:
  - Test imports Role: [Y/N]
  - Test imports POM: [Y/N]
  - Role imports Task: [Y/N]
  - Task imports POMs: [Y/N]
```

---

## Issues Discovered

### Critical Issues (Blocks MVP)

```
Issue ID: [_____________]
Description: [_____________]
Step: [___]
Impact: [_____________]
Status: [OPEN | RESOLVED]
```

### High Priority Issues (Pre-Commercial)

```
Issue ID: [_____________]
Description: [_____________]
Step: [___]
Impact: [_____________]
Status: [OPEN | RESOLVED]
```

### Medium/Low Priority Issues

```
Issue ID: [_____________]
Description: [_____________]
Step: [___]
Impact: [_____________]
Status: [OPEN | RESOLVED]
```

---

## Overall Assessment

### Success Criteria (All Must Pass)

```
□ All 10 steps completed
□ All gates passed (or applicable gates)
□ No skeleton code
□ No pattern violations
□ Test executed
□ Test PASSED
□ Audit trail complete
□ Navigation tracking validated (if multi-page)
```

**Overall Status:** [✓ COMPLETE SUCCESS | ⊗ PARTIAL SUCCESS | ✗ FAILED]

**MVP Readiness Score:** [___/10]

**Recommendation:** [READY FOR MVP | NEEDS FIXES | BLOCKED]

---

## Improvements Identified

### Protocol Updates Needed

```
1. [_____________]
2. [_____________]
3. [_____________]
```

### Tool/Gate Improvements

```
1. [_____________]
2. [_____________]
3. [_____________]
```

### Agent Prompt Improvements

```
1. [_____________]
2. [_____________]
3. [_____________]
```

---

## Reviewer Sign-Off

```
Reviewer: [_____________]
Date: [_____________]
Protocol Version Tested: [v1.0 | v1.1 | v1.X]
Test Run ID: [_____________]
Approved: [Y/N]
Notes: [_____________]
```

---

## Appendix: Quick Reference

### Critical Checks (Must Monitor Every Run)

1. ✓ File write timing (Steps 6-9)
2. ✓ All 20 gates executed
3. ✓ No skeleton code
4. ✓ Test execution result
5. ✓ Audit trail completeness
6. ✓ Navigation tracking (if multi-page)
7. ✓ Pattern violations (framework-check)
8. ✓ Session continuity (run_id)
9. ✓ Environment correctness (--env flag, base URL)

### Common Issues to Watch For

| Issue | Where to Check | Expected |
|-------|----------------|----------|
| Session fragmentation | Audit files count | 1 file (or 2 if resumed) |
| Skeleton code | POST gates, code review | BLOCKED by gates |
| Locators in Task | framework-check | NONE |
| Missing test result | Audit Step 10 | Logged |
| Navigation not logged | Audit Step 5 | Not in MVP (future) |
| Workflow overwrite | File timestamps | Intentional or unique name |
| Wrong site (env mismatch) | Test navigation, pytest command | --env flag matches workflow |
| Config file missing | framework/resources/config/ | Workflow config exists OR DEFAULT used intentionally |
| Credential field mismatch | Test errors, credential strategy | username vs email fields correct |

---

**End of Checklist**
