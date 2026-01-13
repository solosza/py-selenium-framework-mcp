# 10-Step End-to-End Workflow Testing Protocol (Universal) v1.1

**Version:** 1.1
**Purpose:** Generalized testing protocol for validating complete 11-step workflow for ANY site/workflow
**Audience:** Testing sub-agents, QA validation agents
**Last Updated:** 2026-01-11
**Changes from v1.0:** Added sub-agent execution rules based on production test run

---

## Protocol Overview

This protocol defines the STRUCTURE and PROCESS for testing the complete 11-step QA workflow end-to-end. This protocol is **site-agnostic** and **workflow-agnostic**.

**Critical Rules:**
1. **Execute ALL 10 steps** - No shortcuts, no stopping early
2. **Use REAL tools** - No synthetic data, no manual audit log manipulation
3. **Validate at each checkpoint** - Report results after EVERY step
4. **Stop on failure** - If any step fails, STOP and report
5. **Save ALL artifacts** - Keep generated code, test results, screenshots

---

## Input Parameters

Before starting, the user MUST provide:

```yaml
# Required Parameters
test_requirement: "[User story describing what to test]"
target_site: "[Base URL of application under test]"
workflow_name: "[Workflow identifier, e.g., 'auth', 'checkout', 'admin']"
credential_strategy: "[static | dynamic | self-contained | none]"
test_data_location: "[shared | workflow-specific | both | none]"

# Optional Parameters
expected_pages: "[Number of pages expected in workflow, or 'auto-detect']"
page_urls: "[List of URLs if known, or empty for auto-discovery]"
browser: "[chrome | firefox | edge]"
headless: "[true | false]"
```

**Example:**
```yaml
test_requirement: "As a registered user, I want to login and view my dashboard"
target_site: "https://example.com"
workflow_name: "auth"
credential_strategy: "static"
test_data_location: "shared"
expected_pages: "auto-detect"
page_urls: []
browser: "chrome"
headless: false
```

---

## Pre-Test Checklist

Before starting, verify:

```
□ Target site accessible (check [target_site])
□ Playwright MCP server running (if using browser tools)
□ Python environment has all dependencies
□ Working directory: D:\my_ai_projects\py_sel_framework_mcp
□ Review testing skill protocol: .claude/skills/testing/SKILL.md
□ Workflow name is unique (or intentionally reusing)
```

---

## Sub-Agent Execution Rules (v1.1)

### Rule 1: Unique Workflow Names (RECOMMENDED)

**Purpose:** Prevent accidental file overwrites from previous test runs

**Implementation:**
- Before starting, check if `framework/pages/{workflow_name}/` exists
- If exists AND you don't want to overwrite, use incremented name:
  - First test: `workflow_name: "parabank"`
  - Subsequent: `workflow_name: "parabank2"`, `"parabank3"`, etc.
- If intentionally reusing (e.g., updating existing tests), document this

**User typically specifies workflow name** - respect their choice, but warn if overwriting.

**For MVP:** README documentation is sufficient. See project README for naming conventions.

---

### Rule 3: Complete Audit Trail

**Purpose:** Ensure comprehensive audit logging for compliance and debugging

**Requirements:**
- Log ALL 20 gate calls (PRE/POST for Steps 1-11 where applicable)
- Log browser_navigate calls for navigation tracking validation
- Log Step 10 test execution: command, duration, result (PASS/FAIL), errors
- Include pytest output in audit metadata

**Audit entries must include:**
- All quality gate results (qg_preflight, qg_user_input, etc.)
- All tool executions (Tool 1-6)
- Test execution result (Step 10)
- Files generated (complete list with timestamps)

**Post-Commercial:** Will include browser_navigate tool calls in audit trail

---

### Rule 4: Checkpoint Validation

**Purpose:** Validate each step completion before proceeding to next

**Implementation:**

After each step, agent MUST verify:
- ✓ Step N: All gates passed (check status="pass")
- ✓ Step N: Required files generated (if applicable)
- ✓ Step N: Audit trail updated
- ✓ Step N: No errors in output

**If ANY check fails:**
1. STOP immediately
2. Report exact failure
3. Wait for user direction (do NOT auto-continue)

**Example checkpoint (Step 6):**
```
✓ PRE gate passed for both POMs
✓ Tool 3 generated code for both POMs
✓ POST gate passed for both POMs
✓ Files exist on disk
✓ No skeleton code detected
→ Proceed to Step 7
```

**Checkpoint Report Format:**
```
**CHECKPOINT [N]: [PASSED/FAILED]**
- [Check 1]: [status]
- [Check 2]: [status]
- [Check 3]: [status]

**STEP [N] COMPLETE** (if all checks pass)
```

---

### Rule 5: Explicit Completion Criteria

**Purpose:** Agent completes workflow ONLY when ALL criteria met

**Required for completion:**
```
□ All 10 steps executed (not partial)
□ All 20 gates passed (or applicable PRE/POST gates)
□ All files generated (POMs, Task, Role, Test)
□ Test executed via pytest
□ Test result: PASSED (not FAILED, not SKIPPED)
□ Audit trail created (one or more files if resumed)
□ HTML report generated
□ Navigation tracking validated (if multi-page)
```

**Agent MUST report:**
- Steps completed: X/10
- Gates passed: X/20
- Test result: PASSED/FAILED
- Audit files: [list with run_ids]
- Generated files: [list with sizes]

**Partial completion is NOT success.** All criteria must be met.

---

### Rule 6: Error Handling Protocol (Testing Skill)

**Purpose:** Standardized error handling across all test runs

**CRITICAL:** Before executing any test run, agent MUST review:
- `.claude/skills/testing/SKILL.md` - Core testing protocol
- `.claude/skills/testing/references/failure-handling.md` - Detailed failure protocol

**Failure Protocol (9-Step Process):**

| Step | Action |
|------|--------|
| 1. STOP | Halt work, do not auto-fix |
| 2. REPORT | Show: test name, error, location |
| 3. ANALYZE | Explain: expected vs actual, likely cause |
| 4. DISCUSS DEFECT | Ask user: "Create defect entry?" |
| 5. FIX OPTIONS | Present 2-3 fix approaches with tradeoffs |
| 6. DISCUSS FIX | Ask user: "Which fix approach? Proceed?" |
| 7. FIX | Implement approved fix only |
| 8. RE-TEST | Run same tests again |
| 9. RESOLVE | Update defect status if tracked |

**Failures include:**
- Gate returns status="fail"
- Tool throws exception
- File write fails
- Import error
- Test fails (FAILED or ERROR)
- Skeleton code detected
- Locator in Task/Role

**On failure:**
1. STOP immediately (do not proceed to next step)
2. Capture context:
   - Which step/phase failed
   - Exact error message
   - Input parameters
   - Expected vs Actual
3. Report to user using error template from protocol
4. WAIT for user direction
5. Do NOT attempt auto-fixes

**Never say:** "Continuing despite error..."
**Always say:** "Step X failed. Stopping. Awaiting direction."

**Reference:** See `.claude/skills/testing/SKILL.md` lines 240-269 for complete protocol

---

### Rule 10: Protocol Adherence Validation

**Purpose:** Agent confirms protocol compliance before starting

**Before executing workflow, agent MUST:**

1. **Confirm protocol read**
   - State: "I have read testing-protocol-11-step-e2e-v1.1.md"
   - List: "I will execute steps 1-10 as defined"

2. **List the 10 steps**
   ```
   Step 1: Pre-flight Configuration
   Step 2: User Input
   Step 3: AI Processing
   Step 4: Generate Test Scenarios (Tool 1)
   Step 5: Discover Page Elements (Tool 2)
   Step 6: Generate Page Objects (Tool 3)
   Step 7: Generate Task (Tool 4)
   Step 8: Generate Role (Tool 5)
   Step 9: Generate Test Runner (Tool 6)
   Step 10: Save & Run Test
   ```

3. **State critical requirements**
   - ✓ ALL 10 steps (not partial)
   - ✓ REAL tools (no synthetic data)
   - ✓ Audit trail logging
   - ✓ Complete checkpoint validation
   - ✓ Test execution (actual pytest)

4. **Acknowledge error handling**
   - ✓ STOP on failure (do not continue)
   - ✓ Report to user
   - ✓ Wait for direction
   - ✓ Follow testing skill protocol

**This prevents premature completion or partial execution.**

---

## Universal Test Execution Flow

### STEP 1: Pre-flight Configuration

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-01.md`

**Input:**
```python
{
    "credential_strategy": [credential_strategy parameter],
    "test_data_location": [test_data_location parameter]
}
```

**Action:**
```python
from tools.gates.qg_preflight import QGPreflight

result = QGPreflight.validate({
    "credential_strategy": credential_strategy,
    "test_data_location": test_data_location
})
```

**Expected Result:**
```json
{
  "status": "pass"
}
```

**Checkpoint Validation:**
- [ ] qg_preflight called successfully
- [ ] Result status = "pass"
- [ ] No errors in output

**If Failed:**
```
STOP. Report:
- Error message: [exact error]
- Input provided: [show input]
- Expected: status="pass"
- Actual: status="[actual]"
```

---

### STEP 2: User Input

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-02.md`

**Input Extraction:**

From `test_requirement`, extract:
- **Persona**: The "As a [role]" part
- **Role Name**: Convert persona to PascalCase (e.g., "registered user" → "RegisteredUser")
- **URL**: Use first page URL from `page_urls` if provided, else `target_site`

**Action:**
```python
from tools.gates.qg_user_input import QGUserInput

result = QGUserInput.validate({
    "persona": [extracted persona],
    "URL": [target URL],
    "role_name": [derived role name],
    "workflow": [workflow_name parameter],
    "raw_requirement": [test_requirement parameter]
})
```

**Example:**
```python
# If test_requirement = "As a registered user, I want to login"
# Then:
persona = "As a registered user"
role_name = "RegisteredUser"
URL = target_site  # or page_urls[0]
workflow = workflow_name
```

**Expected Result:**
```json
{
  "status": "pass"
}
```

**Checkpoint Validation:**
- [ ] Persona extracted correctly from requirement
- [ ] Role name derived (PascalCase conversion)
- [ ] URL validated (accessible)
- [ ] Workflow set correctly
- [ ] qg_user_input returned "pass"

**If Failed:**
```
STOP. Report:
- Which field failed validation
- Extracted values: persona="[X]", role_name="[Y]", URL="[Z]"
- Validation error: [exact message]
```

---

### STEP 3: AI Processing

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-03.md`

**Input Construction:**

From `test_requirement`, generate:
- **BDD Scenarios**: Convert requirement to Given/When/Then format
- **Expected States**: Extract state-check methods from "Then" clauses
- **Intent**: Summarize workflow intent

**Action:**
```python
from tools.gates.qg_ai_processing import QGAIProcessing

# Generate BDD scenarios from requirement
bdd_scenarios = [
    {
        "given": "[Initial state from requirement]",
        "when": ["[Action 1]", "[Action 2]", ...],
        "then": ["[Expected outcome 1]", "[Expected outcome 2]", ...]
    }
]

# Derive expected states from "Then" clauses
# Pattern: "I should [state]" → "is_[state]" or "has_[state]"
expected_states = [
    "[derived state method names]"
]

# Summarize intent
intent = "[verb]_[object]"  # e.g., "login_and_view_dashboard"

result = QGAIProcessing.validate({
    "bdd_scenarios": bdd_scenarios,
    "expected_states": expected_states,
    "intent": intent
})

metadata_context = result.get("metadata_context")
```

**Example:**
```python
# Requirement: "As a registered user, I want to login and view my dashboard"
bdd_scenarios = [{
    "given": "I am a registered user on the login page",
    "when": ["I enter my credentials", "I click login"],
    "then": ["I should be logged in", "I should see the dashboard"]
}]

expected_states = ["is_logged_in", "is_dashboard_visible"]
intent = "login_and_view_dashboard"
```

**Expected Result:**
```json
{
  "status": "pass",
  "metadata_context": {
    "bdd_scenarios": [...],
    "expected_states": [...],
    "intent": "..."
  }
}
```

**Checkpoint Validation:**
- [ ] BDD scenarios generated (Given/When/Then structure)
- [ ] Expected states derived (is_*/has_* pattern)
- [ ] Intent summarized
- [ ] metadata_context extracted
- [ ] qg_ai_processing returned "pass"

**If Failed:**
```
STOP. Report:
- Which field failed: bdd_scenarios | expected_states | intent
- Generated values: [show what was generated]
- Validation error: [exact message]
```

---

### STEP 4: Generate Test Scenarios (Tool 1)

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-04.md`

**Input Construction:**

Format user story from requirement:
```
As a [role]
I want to [action]
So that [benefit]

Scenario: [Title]
Given [initial state]
When [action 1]
And [action 2]
...
Then [expected outcome 1]
And [expected outcome 2]
...
```

**Action (PRE Gate):**
```python
from tools.gates.qg_test_scenarios import QGTestScenarios

pre_result = QGTestScenarios.validate_pre({
    "metadata_context": metadata_context,
    "workflow": workflow_name
})
```

**Action (Tool 1):**
```python
from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story
import asyncio
import json

user_story = """[formatted user story from requirement]"""

tool1_result = await generate_tests_from_user_story({
    "user_story": user_story,
    "workflow": workflow_name
})

# Parse if string
if isinstance(tool1_result, str):
    tool1_result = json.loads(tool1_result)

test_scenarios = tool1_result.get("metadata", {}).get("test_scenarios", [])
```

**Action (POST Gate):**
```python
post_result = QGTestScenarios.validate_post({
    "test_scenarios": test_scenarios
})
```

**Expected Results:**
- PRE: `{"status": "pass"}`
- POST: `{"status": "pass"}`
- test_scenarios: List of scenarios with given/when/then

**Checkpoint Validation:**
- [ ] PRE gate passed
- [ ] Tool 1 executed successfully
- [ ] test_scenarios extracted (list of dicts)
- [ ] Each scenario has: name, given, when (list), then (list), workflow
- [ ] POST gate passed

**If Failed:**
```
STOP. Report:
- Which phase failed: PRE | Tool | POST
- Input: user_story="[...]", workflow="[...]"
- Output: [show tool1_result]
- Error: [exact message]
```

---

### STEP 5: Discover Page Elements (Tool 2)

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-05.md`

**CRITICAL: This step validates navigation tracking (Task 26.0)**

**Part A: Navigate to Pages (REAL BROWSER)**

**Strategy:**
- If `page_urls` provided → Navigate to each URL
- If `page_urls` empty → Use first URL from test requirement, let navigation tracking detect others

**Action:**
```python
# MUST use REAL Playwright MCP tools, not synthetic audit log entries
from mcp_tools import mcp__playwright__browser_navigate, mcp__playwright__browser_snapshot

# Navigate to initial page
initial_url = page_urls[0] if page_urls else target_site

nav_result = mcp__playwright__browser_navigate({"url": initial_url})
snapshot = mcp__playwright__browser_snapshot()

# If additional pages known, navigate to them
for page_url in page_urls[1:]:
    nav_result = mcp__playwright__browser_navigate({"url": page_url})
    snapshot = mcp__playwright__browser_snapshot()

# Note: PostToolUse hook automatically logs navigation to audit trail
```

**Part B: PRE Gate Validation (Navigation Tracking)**

**Action:**
```python
from tools.gates.qg_discovered_elements import QGDiscoveredElements

pre_result = QGDiscoveredElements.validate_pre({
    "mode": "PRE",
    "url": initial_url,
    "page_name": "[InferredPageName]",  # Inferred from URL
    "credential_strategy": credential_strategy,
    "discovery_method": "playwright",
    "type": "input"
})
```

**Expected PRE Result (Multi-Page with Navigation Tracking):**
```json
{
  "status": "fail",
  "error": "Multi-page workflow detected (N pages) but scope_result not provided (DD-44)",
  "fix_hint": "Retry with the provided scope_result included in your next call.",
  "scope_result": {
    "page_count": N,
    "pages": [
      {
        "name": "[PageName]",
        "page_name": "[PageName]",
        "order": 1,
        "url": "[URL]",
        "depends_on": [],
        "reason": "navigation detected"  // ← CRITICAL: Must be "navigation detected" if Task 26.0 active
      },
      ...
    ]
  }
}
```

**Expected PRE Result (Single-Page):**
```json
{
  "status": "pass"
}
```

**Part C: Element Discovery**

**Action:**
```python
from tools.tool_02_discover_page_elements import discover_page_elements

# Extract pages from PRE gate result
scope_result = pre_result.get("scope_result")
if scope_result:
    pages = scope_result.get("pages", [])
else:
    # Single page workflow
    pages = [{
        "page_name": "[InferredFromURL]",
        "url": initial_url,
        "order": 1
    }]

discovered_elements_list = []

for page in pages:
    page_name = page["page_name"]
    page_url = page["url"]

    print(f"Discovering elements for {page_name} at {page_url}...")

    # Navigate to page
    mcp__playwright__browser_navigate({"url": page_url})

    # Get snapshot
    snapshot = mcp__playwright__browser_snapshot()

    # Discover elements
    elements_result = await discover_page_elements({
        "page_name": page_name,
        "url": page_url,
        "workflow": workflow_name
    })

    discovered_elements_list.append({
        "page_name": page_name,
        "elements": elements_result.get("elements", [])
    })
```

**Part D: POST Gate Validation**

**Action:**
```python
post_result = QGDiscoveredElements.validate_post({
    "mode": "POST",
    "elements": discovered_elements_list,
    "scope_result": scope_result
})
```

**Expected POST Result:**
```json
{
  "status": "pass"
}
```

**Checkpoint Validation:**
- [ ] Real browser navigation performed (NOT synthetic audit log)
- [ ] PostToolUse hook logged navigation to audit trail
- [ ] PRE gate detected pages (count matches expected_pages if specified)
- [ ] If multi-page: scope_result contains "reason": "navigation detected" for all pages
- [ ] Elements discovered for ALL pages
- [ ] POST gate passed

**Navigation Tracking Validation (Task 26.0):**
- [ ] Pages detected from audit log browser_navigate calls
- [ ] Page names inferred from URLs (PascalCase format)
- [ ] Self-healing provided scope_result without explicit scope_discovery
- [ ] "reason" field = "navigation detected" (confirms navigation-first detection, not BDD fallback)

**If Failed:**
```
STOP. Report:
- Which part failed: navigation | PRE | discovery | POST
- Exact error: [message]
- Pages detected: [count]
- Detection method: navigation-first | BDD fallback | none
- Browser navigations: [list URLs]
- Elements discovered: [count per page]
```

---

### STEP 6: Generate Page Objects (Tool 3)

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-06.md`

**Action:**

```python
from tools.gates.qg_page_object import QGPageObject
from tools.tool_03_generate_page_object import generate_page_object

pom_metadata_list = []

for page_data in discovered_elements_list:
    page_name = page_data["page_name"]
    elements = page_data["elements"]

    # Extract expected_states relevant to this page
    # (Match state names to page context)
    page_expected_states = [
        state for state in expected_states
        if should_belong_to_page(state, page_name)
    ]

    print(f"Generating POM for {page_name}...")

    # PRE validation
    pre_result = QGPageObject.validate_pre({
        "page_name": page_name,
        "discovered_elements": elements,
        "expected_states": page_expected_states
    })

    if pre_result["status"] != "pass":
        print(f"PRE gate failed for {page_name}: {pre_result}")
        break

    # Generate POM
    pom_result = await generate_page_object({
        "page_name": page_name,
        "elements": elements,
        "expected_states": page_expected_states,
        "workflow": workflow_name,
        "base_url": target_site
    })

    # POST validation
    post_result = QGPageObject.validate_post({
        "code": pom_result.get("code"),
        "metadata": pom_result.get("metadata")
    })

    if post_result["status"] != "pass":
        print(f"POST gate failed for {page_name}: {post_result}")
        break

    pom_metadata_list.append(pom_result.get("metadata"))
```

**Checkpoint Validation:**
- [ ] PRE gate passed for ALL pages
- [ ] POM code generated for ALL pages
- [ ] POST gate passed for ALL pages
- [ ] No skeleton code detected (qg_page_object validates)
- [ ] Locators present as class constants
- [ ] Atomic methods return self
- [ ] State-check methods present

**If Failed:**
```
STOP. Report:
- Which page failed: [page_name]
- Which phase: PRE | Tool | POST
- Error: [exact message]
- Generated code: [show if available]
```

---

### STEP 7: Generate Task Workflow (Tool 4)

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-07.md`

**Action:**

```python
from tools.gates.qg_task import QGTask
from tools.tool_04_generate_task import generate_task

# Derive task name from workflow
# Pattern: [Workflow]Tasks (e.g., "auth" → "AuthTasks")
task_name = f"{workflow_name.capitalize()}Tasks"

# PRE validation
pre_result = QGTask.validate_pre({
    "task_name": task_name,
    "pom_metadata": pom_metadata_list
})

if pre_result["status"] != "pass":
    print(f"PRE gate failed: {pre_result}")
    # STOP

# Generate Task
task_result = await generate_task({
    "task_name": task_name,
    "workflow": workflow_name,
    "pom_metadata": pom_metadata_list,
    "workflow_description": test_requirement  # Use original requirement
})

# POST validation
post_result = QGTask.validate_post({
    "code": task_result.get("code"),
    "metadata": task_result.get("metadata")
})

if post_result["status"] != "pass":
    print(f"POST gate failed: {post_result}")
    # STOP

task_metadata = task_result.get("metadata")
```

**Checkpoint Validation:**
- [ ] PRE gate passed
- [ ] Task code generated
- [ ] POST gate passed
- [ ] No skeleton code
- [ ] NO LOCATORS in Task code (DD-27 - critical!)
- [ ] Methods use @autologger decorator
- [ ] Methods have NO return values
- [ ] POM methods called correctly

**If Failed:**
```
STOP. Report:
- Which phase: PRE | Tool | POST
- Error: [exact message]
- Task name: [task_name]
- Generated code: [show if available]
- Locator violation: [if DD-27 violated]
```

---

### STEP 8: Generate Role (Tool 5)

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-08.md`

**Action:**

```python
from tools.gates.qg_role import QGRole
from tools.tool_05_generate_role import generate_role

# Use role_name from Step 2
role_name = [role_name from Step 2]

# Derive capabilities from requirement
# Pattern: "I want to [action]" → "can_[action]"
capabilities = [
    # Extract from test_requirement
]

# PRE validation
pre_result = QGRole.validate_pre({
    "role_name": role_name,
    "task_metadata": task_metadata
})

if pre_result["status"] != "pass":
    print(f"PRE gate failed: {pre_result}")
    # STOP

# Generate Role
role_result = await generate_role({
    "role_name": role_name,
    "workflow": workflow_name,
    "capabilities": capabilities,
    "task_metadata": task_metadata,
    "credentials": None if credential_strategy == "static" else {}
})

# POST validation
post_result = QGRole.validate_post({
    "code": role_result.get("code"),
    "metadata": role_result.get("metadata")
})

if post_result["status"] != "pass":
    print(f"POST gate failed: {post_result}")
    # STOP

role_metadata = role_result.get("metadata")
```

**Checkpoint Validation:**
- [ ] PRE gate passed
- [ ] Role code generated
- [ ] POST gate passed
- [ ] No skeleton code
- [ ] Role orchestrates MULTIPLE task methods (not single operation)
- [ ] Methods use @autologger decorator
- [ ] NO return values
- [ ] Workflow method present

**If Failed:**
```
STOP. Report:
- Which phase: PRE | Tool | POST
- Error: [exact message]
- Role name: [role_name]
- Generated code: [show if available]
```

---

### STEP 9: Generate Test Runner (Tool 6)

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-09.md`

**Action:**

```python
from tools.gates.qg_test_runner import QGTestRunner
from tools.tool_06_generate_test_runner import generate_test_runner

# Derive test name from intent
# Pattern: test_[intent] (e.g., "login_and_view_dashboard" → "test_login_and_view_dashboard")
test_name = f"test_{intent}"

# Use first scenario from Step 4
scenario = test_scenarios[0]

# PRE validation
pre_result = QGTestRunner.validate_pre({
    "test_name": test_name,
    "pom_metadata": pom_metadata_list,
    "role_metadata": role_metadata
})

if pre_result["status"] != "pass":
    print(f"PRE gate failed: {pre_result}")
    # STOP

# Generate Test
test_result = await generate_test_runner({
    "test_name": test_name,
    "workflow": workflow_name,
    "role": role_name,
    "scenario": scenario,
    "pom_metadata": pom_metadata_list,
    "role_metadata": role_metadata,
    "task_metadata": task_metadata
})

# POST validation
post_result = QGTestRunner.validate_post({
    "code": test_result.get("code"),
    "metadata": test_result.get("metadata")
})

if post_result["status"] != "pass":
    print(f"POST gate failed: {post_result}")
    # STOP

test_metadata = test_result.get("metadata")
test_code = test_result.get("code")
```

**Checkpoint Validation:**
- [ ] PRE gate passed
- [ ] Test code generated
- [ ] POST gate passed
- [ ] Test calls ONE role workflow method (not multiple)
- [ ] Assertions use POM state-check methods (NOT return values)
- [ ] AAA pattern (Arrange/Act/Assert)
- [ ] Proper fixtures used
- [ ] Import paths correct

**If Failed:**
```
STOP. Report:
- Which phase: PRE | Tool | POST
- Error: [exact message]
- Test name: [test_name]
- Generated code: [show if available]
- Assertion violation: [if using return values instead of POM]
```

---

### STEP 10: Save & Run Test

**Protocol Reference:** `.claude/skills/qa-guidance-layer/references/step-10.md`

**Part A: PRE-Save Validation**

```python
from tools.gates.qg_save_run import QGSaveRun

pre_result = QGSaveRun.validate_pre({
    "pom_code": [pom["code"] for pom in pom_metadata_list],
    "task_code": task_result.get("code"),
    "role_code": role_result.get("code"),
    "test_code": test_code
})

if pre_result["status"] != "pass":
    print(f"PRE-save gate failed: {pre_result}")
    # STOP
```

**Part B: Save Files**

```python
from pathlib import Path

# Save POMs
for pom_data in pom_metadata_list:
    class_name = pom_data["class_name"]
    file_name = class_name.lower().replace("page", "_page") + ".py"
    pom_path = Path(f"framework/pages/{workflow_name}/{file_name}")
    pom_path.parent.mkdir(parents=True, exist_ok=True)
    pom_path.write_text(pom_data["code"])
    print(f"Saved POM: {pom_path}")

# Save Task
task_file_name = f"{workflow_name}_tasks.py"
task_path = Path(f"framework/tasks/{workflow_name}/{task_file_name}")
task_path.parent.mkdir(parents=True, exist_ok=True)
task_path.write_text(task_result["code"])
print(f"Saved Task: {task_path}")

# Save Role
role_file_name = role_name.lower().replace("user", "_user") + ".py"
role_path = Path(f"framework/roles/{workflow_name}/{role_file_name}")
role_path.parent.mkdir(parents=True, exist_ok=True)
role_path.write_text(role_result["code"])
print(f"Saved Role: {role_path}")

# Save Test
test_file_name = f"{test_name}.py"
test_path = Path(f"tests/{workflow_name}/{test_file_name}")
test_path.parent.mkdir(parents=True, exist_ok=True)
test_path.write_text(test_code)
print(f"Saved Test: {test_path}")
```

**Part C: Run Test**

```python
from tools.run_test import run_test

test_run_result = run_test({
    "test_path": f"tests/{workflow_name}/{test_file_name}",
    "browser": browser,
    "headless": headless
})

print(f"Test Result: {test_run_result}")
```

**Expected Test Result:**
```json
{
  "status": "passed",
  "tests_run": 1,
  "passed": 1,
  "failed": 0,
  "errors": [],
  "duration": "XX.XXs",
  "report_path": "tests/_reports/report_TIMESTAMP.html"
}
```

**Checkpoint Validation:**
- [ ] PRE-save gate passed
- [ ] All files saved to correct locations
- [ ] No file write errors
- [ ] Test executed with pytest
- [ ] Test PASSED (status="passed")
- [ ] HTML report generated
- [ ] No import errors
- [ ] Browser interactions successful

**If Failed:**
```
STOP. Report:
- Which part: PRE-save | save | run
- File errors: [list files that failed to save]
- Test result: [show full pytest output]
- Error messages: [exact errors]
- Screenshots: [if browser test failed]
```

---

## Universal Validation Report Template

After completing all 10 steps, generate this report:

```markdown
# 10-Step Workflow Test Report

**Date:** [timestamp]
**Test Requirement:** [test_requirement]
**Target Site:** [target_site]
**Workflow:** [workflow_name]
**Run ID:** [audit log run_id(s)]

## Input Parameters

- **Credential Strategy:** [credential_strategy]
- **Test Data Location:** [test_data_location]
- **Expected Pages:** [expected_pages]
- **Browser:** [browser]
- **Headless:** [headless]

## Results Summary

| Step | Name | Status | Duration | Notes |
|------|------|--------|----------|-------|
| 1 | Pre-flight | ✓/✗ | Xs | |
| 2 | User Input | ✓/✗ | Xs | Persona: [persona], Role: [role_name] |
| 3 | AI Processing | ✓/✗ | Xs | Intent: [intent] |
| 4 | Test Scenarios | ✓/✗ | Xs | Scenarios: [count] |
| 5 | Element Discovery | ✓/✗ | Xs | Pages: [count], Navigation: ✓/✗ |
| 6 | POM Generation | ✓/✗ | Xs | POMs: [count] |
| 7 | Task Generation | ✓/✗ | Xs | Task: [task_name] |
| 8 | Role Generation | ✓/✗ | Xs | Role: [role_name] |
| 9 | Test Generation | ✓/✗ | Xs | Test: [test_name] |
| 10 | Save & Run | ✓/✗ | Xs | Test: PASS/FAIL |

**Overall Status:** PASS / FAIL
**Total Duration:** XXs

## Navigation Tracking Validation (Task 26.0)

- **Pages detected:** [count]
- **Detection method:** navigation-first / BDD fallback / none
- **Page names inferred:** [list]
- **Reason field:** "navigation detected" / other / N/A
- **Self-healing active:** YES / NO / N/A

**Navigation Tracking Status:** ✓ VALIDATED / ✗ FAILED / N/A (single-page)

## Files Generated

```
framework/pages/[workflow_name]/
├── [page1_file].py
├── [page2_file].py
└── ...

framework/tasks/[workflow_name]/
└── [workflow_name]_tasks.py

framework/roles/[workflow_name]/
└── [role_file].py

tests/[workflow_name]/
└── [test_name].py
```

## Test Execution Details

**Test Path:** tests/[workflow_name]/[test_name].py
**Result:** PASSED / FAILED
**Duration:** XXs
**Report:** tests/_reports/report_TIMESTAMP.html

**Test Output:**
```
[paste pytest output]
```

## Errors / Issues

[If any step failed, list exact errors here]

## Conclusion

[PASS: All 10 steps completed, test passed, navigation tracking validated (if multi-page)]
[FAIL: Step X failed with error Y]

## Artifacts Saved

- Audit log: tests/_audit/audit_log_[run_id].json (or multiple files if resumed)
- Test report: tests/_reports/report_[timestamp].html
- Screenshots (if any): [list]
- Generated code: [list all files]
```

---

## Error Handling Protocol

**If ANY step fails:**

1. **STOP immediately** - Do not proceed to next step
2. **Capture context:**
   - Exact error message
   - Step that failed (1-10)
   - Phase that failed (PRE/Tool/POST)
   - Input parameters provided
   - Output received
   - Expected vs Actual
3. **Report to user:**
   ```
   ❌ STEP [N] FAILED: [Step Name]

   Phase: [PRE/Tool/POST]
   Error: [exact error message]

   Input Parameters:
   [list input data]

   Expected:
   [what should have happened]

   Actual:
   [what actually happened]

   Context:
   - Workflow: [workflow_name]
   - Site: [target_site]
   - Step completed: [N-1]
   ```
4. **Reference testing skill:**
   - Follow `.claude/skills/testing/SKILL.md` failure protocol (lines 240-269)
   - Present 2-3 fix options with tradeoffs
   - Do NOT implement first solution that comes to mind
5. **WAIT for user direction** - Do not auto-fix

---

## Success Criteria

Test is considered SUCCESSFUL only if ALL criteria met:

- [x] All 10 steps completed without errors
- [x] All PRE gates passed
- [x] All POST gates passed
- [x] All code generated (no skeleton code)
- [x] All files saved to correct locations
- [x] Pytest test executed
- [x] Test PASSED (status="passed")
- [x] HTML report generated
- [x] If multi-page: Navigation tracking detected pages from browser_navigate
- [x] If multi-page: scope_result has "reason": "navigation detected"

**Partial success is NOT success.** All criteria must be met.

---

## Appendix A: Parameter Derivation Rules

**From test_requirement to parameters:**

| Derive | From | Pattern |
|--------|------|---------|
| Persona | Requirement start | "As a [role]" → "[role]" |
| Role Name | Persona | Convert to PascalCase: "registered user" → "RegisteredUser" |
| Intent | Requirement action | "I want to [X]" → "[X]" (verb_object format) |
| Expected States | BDD "Then" clauses | "I should [state]" → "is_[state]" or "has_[state]" |
| Capabilities | Intent | "I want to [action]" → "can_[action]" |
| Test Name | Intent | "test_" + intent |
| Task Name | Workflow | Capitalize(workflow) + "Tasks" |

**Example:**
```
Requirement: "As a registered user, I want to login and view my dashboard"

Derived:
- persona: "As a registered user"
- role_name: "RegisteredUser"
- intent: "login_and_view_dashboard"
- expected_states: ["is_logged_in", "is_dashboard_visible"]
- capabilities: ["can_login", "can_view_dashboard"]
- test_name: "test_login_and_view_dashboard"
- task_name: "AuthTasks" (if workflow="auth")
```

---

## Appendix B: File Naming Conventions

**POMs:**
- Pattern: `[workflow_name]/[page_name_lowercase].py`
- Example: `framework/pages/auth/login_page.py`

**Tasks:**
- Pattern: `[workflow_name]/[workflow_name]_tasks.py`
- Example: `framework/tasks/auth/auth_tasks.py`

**Roles:**
- Pattern: `[workflow_name]/[role_name_lowercase].py`
- Example: `framework/roles/auth/registered_user.py`

**Tests:**
- Pattern: `[workflow_name]/test_[intent].py`
- Example: `tests/auth/test_login_and_view_dashboard.py`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-11 | Initial generalized protocol (site-agnostic, workflow-agnostic) |
| 1.1 | 2026-01-11 | Added sub-agent execution rules 1, 3-6, 10 based on production test findings |

---

## Notes

**Session Fragmentation (Expected):**
- If agent stops mid-workflow and is resumed, a new audit file will be created
- This is EXPECTED behavior, not a bug
- Use run_ids to link audit file segments
- For continuous execution (no stops), one audit file is created

**Workflow Naming:**
- Users typically specify unique workflow names to differentiate test runs
- Reusing workflow names will overwrite existing files
- See project README for naming conventions
- For MVP: README documentation sufficient
- Post-MVP: Consider adding validation logic

**Audit Trail (Competitive Differentiator):**
- Comprehensive audit logging is a key competitive advantage
- Pre-commercial improvements planned:
  - Include browser_navigate tool calls in audit
  - Fix Step 5 POST gate metadata accuracy
  - Log Step 10 test execution results
- Not MVP blocking but high priority for commercial release
