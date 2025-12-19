# QA Validation Agents - Defect Log

**Project:** QA Validation Agents
**Location:** `agents/`

---

## DEF-VA-001: Missing AI Orchestrator Integration

**Date:** 2024-12-17
**Severity:** CRITICAL
**Status:** RESOLVED
**Found In:** Task 7.0 - Real Validation Run
**Resolved:** 2024-12-17

### Description

The Supervisor agent has no mechanism to invoke the AI Orchestrator (Claude Code + MCP tools). The `_run_scenario()` function in `supervisor.py` lines 195-204 only simulates artifact generation - it never actually triggers the 9-step MCP workflow.

### Expected Behavior

```
Supervisor → SQA Agent → AI Orchestrator → Reviewer → Report
                              │
                              └─→ Invokes MCP Tools 1-6
                                  Passes metadata
                                  Generates artifacts
```

### Actual Behavior

```
Supervisor → (simulated) → Reviewer → Report
                │
                └─→ No actual artifact generation
                    Just returns "Simulated review"
```

### Root Cause

1. Architecture had 3 components but needed 4:
   - Supervisor (triggers agents)
   - SQA Agent (simulates SDET user)
   - **AI Orchestrator (Claude Code + MCP)** ← MISSING
   - Reviewer (validates artifacts)

2. SQA Agent was only providing requirements, not invoking the skill

3. The "Orchestrator" was marked as "(Simulated)" in code comments but never implemented

### Evidence

`supervisor.py` lines 195-204:
```python
if content_map:
    # Testing mode: validate provided content
    review_result = await _test_validate_artifacts({...})
else:
    # SIMULATION MODE - JUST SKIPS EVERYTHING!
    review_result = {
        "status": "APPROVE",
        "summary": "Simulated review - no artifacts provided",
    }
```

### Impact

- Task 7.0 validation run could not execute properly
- Integration tests passed because they provided mock `content_map`, hiding the gap
- Real validation flow was broken

### Fix Required

1. Add AI Orchestrator as explicit component in architecture
2. SQA Agent must invoke `/skill execute-from-step1` to trigger AI Orchestrator
3. Add visual workflow logger to track flow and catch failures early
4. Add new DDs to prevent recurrence

### Related DDs

- New DD-VA-23: Agent hierarchy must include AI Orchestrator
- New DD-VA-24: Visual workflow logging required
- New DD-VA-25: SQA Agent must invoke skill (not just provide requirements)

### Resolution

**Fix implemented:**
1. Updated `supervisor.py` to return `ORCHESTRATOR_PENDING` status when no `content_map` provided
2. Updated `sr_qa_engineer.py` to include `next_action` with skill invocation instruction
3. Built `workflow_logger.py` for visual feedback
4. Integrated visual logger into Supervisor flow

**Verified by:**
- E2E validation run showing all 4 steps completing:
  - [1/4] SUPERVISOR -> SQA_AGENT ✅
  - [2/4] SQA_AGENT -> AI_ORCHESTRATOR ✅
  - [3/4] AI_ORCHESTRATOR -> REVIEWER ✅
  - [4/4] REVIEWER -> SUPERVISOR ✅

---

## DEF-VA-002: No Visual Feedback During Validation Flow

**Date:** 2024-12-17
**Severity:** HIGH
**Status:** RESOLVED
**Found In:** Task 7.0 - Real Validation Run
**Resolved:** 2024-12-17

### Description

During validation run, there was no visual indication of:
- Which step was executing
- Which agent was active
- Where the flow failed
- What the handoff status was

This made debugging extremely difficult.

### Expected Behavior

Real-time visual log showing:
```
[1/5] SUPERVISOR → SQA AGENT          ✅ SUCCESS
[2/5] SQA → AI ORCHESTRATOR           🔄 RUNNING
      Step 3: Tool 1 invoked...
      Step 4: Tool 2 invoked...
[2/5] SQA → AI ORCHESTRATOR           ❌ FAILED
      Error: Element not found
```

### Actual Behavior

No visual feedback. Had to manually trace through conversation to find failure point.

### Root Cause

Visual workflow logger was never built. No logging infrastructure for agent handoffs.

### Fix Required

1. Build `agents/tools/workflow_logger.py`
2. Integrate into Supervisor flow
3. Show real-time status at each step

### Resolution

**Fix implemented:**
1. Built `agents/tools/workflow_logger.py` with `VisualWorkflowLogger` class
2. Integrated into `supervisor.py` `_run_scenario()` function
3. Visual output shows:
   - Step number and total (e.g., [1/4])
   - Agent handoffs (FROM -> TO)
   - Action being performed
   - Input/Output metadata
   - Sub-step status (OK/FAILED)
   - Final result with root cause on failure

**Example output:**
```
+----------------------------------------------------------------------------+
| [1/4] SUPERVISOR -> SQA_AGENT                                     [>>] RUNNING |
+----------------------------------------------------------------------------+
| Action: Get test scenario from SQA Agent                                   |
      Input:  scenario_id='QA-EASY-001'
      Output: scenario='Create new account with valid data', has_next_action=True
+-------------------------------------------------------------------- [OK] SUCCESS +
```

---

## DEF-VA-003: MCP Tools Accept Wrong Element Format Silently

**Date:** 2024-12-17
**Severity:** HIGH
**Status:** OPEN
**Found In:** Task 7.0 - Real Validation Run

### Description

Tool 3 (generate_page_object) silently ignores elements when field names don't match expected format. No error is raised - just generates skeleton code with empty locators.

### Expected Behavior

Tool 3 should:
1. Accept multiple field name variants (`name` OR `suggested_name`, `locator` OR `locator_id`/`locator_css`)
2. Return error if no valid elements found after transformation
3. Warn if elements are being skipped

### Actual Behavior

Tool 3 transformation (line 119-133):
```python
locator = elem.get("locator_id") or elem.get("locator_css") or elem.get("locator_xpath", "")
name = elem.get("suggested_name", "")  # Ignores "name" field!
```

When passed `{"name": "X", "locator": "Y"}`, both become empty strings, element is skipped, no error.

### Root Cause

Rigid field name matching without fallbacks or validation.

### Fix Required

1. Tool 3: Accept `name` OR `suggested_name`, `locator` OR `locator_*` variants
2. Tool 3: Error if `elements_count == 0` after transformation
3. All tools: Validate required inputs and return clear errors

---

## DEF-VA-004: MCP Tool Chain Metadata Not Passed Between Tools

**Date:** 2024-12-17
**Severity:** CRITICAL
**Status:** OPEN
**Found In:** Task 7.0 - Real Validation Run

### Description

The 9-step MCP tool chain is metadata-driven, but the AI Orchestrator didn't pass metadata between tools. Each tool generated skeleton code because it had no context.

### Expected Behavior

```
Tool 2 → elements[] → Tool 3 → pom_metadata → Tool 4 → task_metadata → Tool 5 → role_metadata → Tool 6
```

Tool 3 returns `metadata` in output. Tool 4 expects `pom_metadata` parameter. This must be passed.

### Actual Behavior

AI Orchestrator called each tool independently without passing metadata:
- Tool 3 output had `metadata` but not used
- Tool 4 called without `pom_metadata` → generated skeleton
- Tool 5 called without `task_metadata` → generated skeleton
- Tool 6 called without context → generated wrong test method name

### Root Cause

1. AI Orchestrator (me) didn't understand metadata passing requirement
2. DDs don't explicitly state "MUST pass Tool N metadata to Tool N+1"
3. No validation that required metadata was provided

### Fix Required

1. Add DD: "AI Orchestrator MUST pass Tool N output metadata to Tool N+1"
2. Tools should error if expected metadata is missing
3. Skill documentation should show exact parameter passing
4. Consider: Tool output should show "PASS THIS TO NEXT TOOL: {...}"

---

## DEF-VA-005: Reviewer Does Not Check Implementation Completeness

**Date:** 2024-12-17
**Severity:** HIGH
**Status:** OPEN
**Found In:** Task 7.0 - Real Validation Run

### Description

Reviewer approved artifacts with skeleton code (`pass` statements, empty methods, missing locators). It only checks for specific DD pattern violations, not implementation completeness.

### Expected Behavior

Reviewer should REJECT if:
- POM has no locators (just `pass`)
- POM has no action methods
- Task methods are empty (`pass`)
- Role methods are empty (`pass`)
- Test calls methods that don't exist

### Actual Behavior

Reviewer only checks:
- DD-03: Locators in wrong layer
- DD-15: Bad assertion patterns
- DD-09: Task/Role returning values
- DD-11: State method naming
- DD-18/19: Import issues

Skeleton code passes all these checks because it doesn't HAVE the bad patterns.

### Root Cause

Reviewer validates "what is there" but not "what should be there".

### Fix Required

1. Add checks for:
   - `check_pom_has_locators()` - Must have locator constants
   - `check_pom_has_action_methods()` - Must have action methods
   - `check_task_methods_implemented()` - Methods can't be just `pass`
   - `check_role_methods_implemented()` - Methods can't be just `pass`
   - `check_test_calls_exist()` - Methods called must exist

2. Add DD: "Generated code must have complete implementation"

---

## DEF-VA-006: Reviewer Output Not Shown in Visual Logger

**Date:** 2024-12-17
**Severity:** MEDIUM
**Status:** OPEN
**Found In:** Task 7.0 - Real Validation Run

### Description

Visual workflow logger shows Reviewer step but not the detailed audit results. User cannot see what was checked or why it was approved/rejected.

### Expected Behavior

```
[3/4] AI_ORCHESTRATOR -> REVIEWER
      Files Audited:
      - framework/pages/auth/authentication_page.py
        [OK] DD-03: No locators in wrong layer
        [OK] DD-15: Assertions use POM methods
        [WARN] DD-NEW: Only 0 locators found (expected > 0)
      - framework/tasks/auth/auth_tasks.py
        [FAIL] DD-NEW: Method create_account() is empty (just pass)

      Result: REJECT - 1 blocking violation
```

### Actual Behavior

```
[3/4] AI_ORCHESTRATOR -> REVIEWER
      [OK] DD-03 Check (Locators)
      [OK] DD-15 Check (Assertions)
      Output: status=APPROVE, violations=0
```

No file-level detail, no per-DD breakdown.

### Fix Required

1. Reviewer returns detailed per-file, per-DD results
2. Visual logger displays full audit breakdown
3. Show warnings even when approved

---

## Defect Template

```markdown
## DEF-VA-XXX: [Brief Description]

**Date:** YYYY-MM-DD
**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Status:** OPEN | IN_PROGRESS | RESOLVED
**Found In:** [Task/Context]

### Description
[What went wrong]

### Expected Behavior
[What should happen]

### Actual Behavior
[What actually happened]

### Root Cause
[Why it happened]

### Fix Required
[What needs to be done]

### Related DDs
[Any new or existing DDs]
```
