# PRD: Pair Programming Workflow Formalization

**Project:** Workflow Refactor - Formalize Pair Programming Pattern
**Date:** 2026-01-21
**Status:** Phase 2 (Define) - Ready for Task Generation

---

## 1. Introduction/Overview

**Problem:**
The current autonomous test generation workflow (Steps 1-10) generates code optimistically, requiring manual fixes 96% of the time during Step 11 execution. The helios7 test demonstrated that pair programming (human guides, AI builds incrementally, gates validate in real-time) produces working code without rework.

**Solution:**
Formalize the pair programming pattern as the PRIMARY workflow. This isn't rebuilding - it's documenting what already works (helios7 evidence) so it's reproducible, teachable, and scalable across the 6-component AI Management Layer architecture.

**Goal:**
Create sufficient protocols, configure 6-layer defense-in-depth enforcement, and validate that pair programming produces framework-compliant tests that pass on first attempt without Step 11 manual fixes.

---

## 2. Goals

**Primary Goals:**
1. Formalize pair programming as the default workflow (replace autonomous generation)
2. Document sufficient protocols (Layer 1 defense) working with Smart Gates (Layer 2)
3. Configure all 6 defense layers to enforce stop-when-blocked behavior
4. Enable full audit trail for session reconstruction and compliance
5. Validate with one working test generated via pair programming

**Success Metrics:**
- **Test passes on first attempt** - No Step 11 manual fixes required
- **HITL triggers reliably** - AI stops when blocked (no rambling/looping)
- **Full session audit** - Complete reconstruction capability from logs

---

## 3. User Stories

**As a QA engineer,**
I want AI to build test code incrementally with my guidance,
So that I don't waste time fixing AI-generated code that doesn't match reality.

**As a QA engineer,**
I want AI to STOP immediately when blocked (not loop through fixes),
So that I can redirect AI quickly instead of watching it fail repeatedly.

**As a QA engineer,**
I want to see the browser at all times (never headless),
So that I can verify AI is clicking the right elements and interrupt if wrong.

**As a QA engineer,**
I want configurable timeout monitoring (default 30s),
So that AI doesn't silently wait while I stare at the screen.

**As a platform architect,**
I want the 6-component defense-in-depth to enforce quality,
So that pair programming is reliable and reproducible, not ad-hoc collaboration.

**As a compliance officer,**
I want full audit trail of every HITL interaction and construction decision,
So that I can reconstruct what happened and verify human oversight.

---

## 4. Functional Requirements

### FR-1: Sufficient Protocols (Layer 1 Defense)

**FR-1.1:** Protocol SHALL document stop-when-blocked patterns (DD-22)
- When to stop: test fails, timeout exceeds threshold, element not found, DD violation
- How to report: error message, context, hypothesis (not just "failed")
- How to wait: do NOT proceed until human provides guidance

**FR-1.2:** Protocol SHALL document build-as-you-go patterns
- When to save files: immediately after each piece created (POM method added → save)
- Build-test-discover cycle: create → save → test → discover gap → create more
- Incremental validation points: after each file save, after each test run

**FR-1.3:** Protocol SHALL document HITL trigger patterns
- What triggers HITL: test fail, timeout threshold exceeded, DD violation, element not found, 3+ sequential failures, same fix attempted twice
- How to signal user: "AI blocked at [X], awaiting guidance"
- User interrupt mechanism: "stop" command → immediate HITL trigger

**FR-1.4:** Protocol SHALL document configuration requirements
- Browser visible: headless=false (never override, non-negotiable)
- Timeout monitoring: configurable threshold (default 30s), enable/disable toggle
- Tool usage: Tools 1-2 core (BDD scenarios, element discovery), Tools 3-6 optional (on-demand)

**FR-1.5:** Protocol SHALL document collaboration patterns
- AI builds: knows framework from FRAMEWORK.md + 28 DDs, uses Edit/Write tools
- Human navigates/discovers: guides at blockers, provides direction
- Gates validate: after each piece (work with Protocols Layer 1)

### FR-2: Smart Gates (Layer 2 Defense)

**FR-2.1:** Smart Gates SHALL validate AND teach (not just block)
- On violation detected: provide fix data (how to correct, not just "violation found")
- Example: DD-27 violation → "Move locators to POM as class constants: `self.pom.LOCATOR`"

**FR-2.2:** Smart Gates SHALL signal HITL when validation fails
- Test failure → Return blocker signal → Trigger HITL (Component 6)
- DD violation → Return blocker signal → Trigger HITL with fix data

**FR-2.3:** Smart Gates SHALL validate after each save/test
- After file save: framework compliance check
- After test run: functional correctness check
- After tool call: output quality check

### FR-3: Hooks (Layer 3 Defense)

**Note:** Hooks are Claude Code lifecycle hooks (PostToolUse pattern) implemented in `.claude/hooks/`, not MCP server hooks.

**FR-3.1:** Hooks SHALL monitor timeout thresholds
- Hook type: PostToolUse (monitors tool execution duration)
- Default threshold: 30 seconds (configurable via `environment_config.json`)
- Enable/disable toggle: user can turn off for long-running operations
- Actions monitored: browser_navigate, element_wait, ajax_call (configurable)

**FR-3.2:** Hooks SHALL force HITL trigger on timeout
- If AI waiting > threshold → Hook interrupts → Force HITL trigger immediately
- User prompted: "Element not found, timeout at 30s. Continue waiting or change approach?"

**FR-3.3:** Hooks SHALL detect rambling patterns
- Hook type: PostToolUse (tracks consecutive failures)
- 3+ sequential failures → Interrupt, force HITL
- Same fix attempted twice → Force HITL
- Prevent AI from looping through multiple fix attempts

### FR-4: Checkpointing (Layer 4 Defense)

**FR-4.1:** Checkpointing SHALL auto-save at each blocker
- When HITL triggered → Save state automatically
- State includes: files created, last action, blocker type, context

**FR-4.2:** Checkpointing SHALL enable resume from exact blocker
- User can close session, resume later from checkpoint
- No loss of progress, continues from exact stop point

### FR-5: Audit System (Layer 5 Defense)

**FR-5.1:** Audit System SHALL log full session for reconstruction

**Data Model (Finalized 2026-01-22):**

**File Structure:**
```
tests/_audit/audit_log_<run_id>.json         ← Event stream (gates, tools, HITL, violations)
tests/_state/<run_id>/workflow_state.json    ← Accumulated state (steps, construction journal, metrics)
tests/_reports/<run_id>/screenshot_*.png     ← Test execution artifacts
```

**Audit Log (`tests/_audit/audit_log_<run_id>.json`):**
- **HITL interactions:** `{"type": "hitl_interaction", "timestamp": "...", "trigger_reason": "...", "user_input": "...", "ai_response": "...", "context": {...}}`
- **Timeout events:** `{"type": "hook_intervention", "pattern": "timeout_exceeded", "threshold": 30, "actual": 45, "action": "force_hitl"}`
- **Gate validations:** `{"type": "gate_validation", "gate": "qg_task", "result": "pass/fail", "violations": [...], "fix_data": {...}}`
- **Hook interventions:** `{"type": "hook_intervention", "pattern": "loop_detected", "action": "force_hitl"}`
- **Tool calls:** `{"type": "tool_call", "tool": "generate_tests_from_user_story", "input": {...}, "output": {...}}`

**Workflow State (`tests/_state/<run_id>/workflow_state.json`):**
- **Steps accumulation:** `{"steps": {"step_1": {...}, "step_2": {...}, "step_3": {...}}}`
- **Construction journal:** `{"iterations": [{"iteration": 1, "files_created": ["path1"], "files_modified": []}]}`
- **Test execution history:** `{"test_runs": [{"run": 1, "command": "pytest ...", "result": "failed", "screenshot": "tests/_reports/<run_id>/screenshot_001.png"}]}`
- **Count-based metrics:** `{"metrics": {"iterations": 5, "hitl_triggers": 3, "gate_violations": 2, "test_runs": 8, "final_result": "passed"}}`

**Design Decisions:**
1. **Separation of concerns:** Event stream (audit) vs accumulated state (workflow state)
2. **File paths only:** No code snapshots in construction journal (use git diffs)
3. **Screenshot references:** Paths to `_reports/` directory (not embedded in JSON)
4. **Count-based metrics:** Focus on correctness (iteration count, HITL count, violations) not timing
5. **HITL interactions:** Full conversation logged for compliance and session reconstruction

**What This Enables:**
- Session reconstruction from audit log
- HITL decision documentation (compliance)
- Construction progress tracking (workflow state)
- Test execution history (build→test→discover cycles)
- Framework compliance audit trail

**FR-5.2:** Audit trail SHALL enable full session replay
- Given audit log → Reconstruct entire session timeline
- Show: what AI built, when HITL triggered, what user said, how AI responded
- Use case: Debugging failed tests, compliance verification, training examples

**FR-5.3:** Audit trail SHALL support compliance requirements
- Demonstrate human oversight (HITL triggers logged)
- Document construction decisions (why this approach chosen)
- Prove quality enforcement (gate validations, hook interventions)

**FR-5.4:** Complete JSON Schema Examples

**Audit Log Example (`tests/_audit/audit_log_2026-01-22T10-30-45.123456Z.json`):**
```json
{
  "workflow_id": "2026-01-22T10-30-45.123456Z",
  "events": [
    {
      "type": "gate_validation",
      "timestamp": "2026-01-22T10:30:46.123Z",
      "gate": "qg_user_input",
      "result": "pass",
      "input": {"persona": "sales representative", "url": "...", "role_name": "SalesRepresentative", "workflow": "helios8"}
    },
    {
      "type": "tool_call",
      "timestamp": "2026-01-22T10:30:50.456Z",
      "tool": "generate_tests_from_user_story",
      "input": {"user_story": "...", "workflow": "helios8"},
      "output": {"scenarios": [...], "test_name": "test_submit_inquiry"}
    },
    {
      "type": "gate_validation",
      "timestamp": "2026-01-22T10:31:20.789Z",
      "gate": "qg_test_runner",
      "result": "fail",
      "violations": ["DD-27: locators found in Task layer"],
      "fix_data": {"suggestion": "Move locators to POM as class constants", "example": "self.pom.LOCATOR"}
    },
    {
      "type": "hitl_interaction",
      "timestamp": "2026-01-22T10:31:25.012Z",
      "trigger_reason": "test_failed",
      "user_input": "add wait method to POM",
      "ai_response": "Added wait_for_element(locator, timeout=10) to InquiriesPage",
      "context": {"file_modified": "framework/pages/helios8/inquiries_page.py", "method_added": "wait_for_element"}
    },
    {
      "type": "hook_intervention",
      "timestamp": "2026-01-22T10:32:15.345Z",
      "pattern": "timeout_exceeded",
      "threshold": 30,
      "actual": 45,
      "action": "force_hitl",
      "context": {"action": "browser_navigate", "url": "..."}
    }
  ]
}
```

**Workflow State Example (`tests/_state/2026-01-22T10-30-45.123456Z/workflow_state.json`):**
```json
{
  "workflow_id": "2026-01-22T10-30-45.123456Z",
  "steps": {
    "step_1": {
      "persona": "sales representative",
      "url": "https://example.com/inquiries",
      "role_name": "SalesRepresentative",
      "workflow": "helios8",
      "raw_requirement": "As a sales representative, I want to submit a service inquiry",
      "detected_env_id": "helios1"
    },
    "step_2": {
      "credential_strategy": "none",
      "test_data_location": "workflow-specific"
    },
    "step_3": {
      "bdd_scenarios": [
        {
          "given": "User is on inquiries page",
          "when": "User submits inquiry form",
          "then": "Inquiry is created and visible in list"
        }
      ],
      "expected_states": ["is_inquiry_created", "is_inquiry_in_list"],
      "intent": "create_inquiry"
    }
  },
  "construction_journal": {
    "iterations": [
      {
        "iteration": 1,
        "timestamp": "2026-01-22T10:30:55.000Z",
        "files_created": ["framework/pages/helios8/inquiries_page.py"],
        "files_modified": []
      },
      {
        "iteration": 2,
        "timestamp": "2026-01-22T10:31:10.000Z",
        "files_created": ["framework/tasks/helios8/inquiry_tasks.py"],
        "files_modified": ["framework/pages/helios8/inquiries_page.py"]
      },
      {
        "iteration": 3,
        "timestamp": "2026-01-22T10:31:30.000Z",
        "files_created": ["framework/roles/helios8/sales_representative.py"],
        "files_modified": []
      },
      {
        "iteration": 4,
        "timestamp": "2026-01-22T10:31:50.000Z",
        "files_created": ["tests/helios8/test_submit_inquiry.py"],
        "files_modified": []
      },
      {
        "iteration": 5,
        "timestamp": "2026-01-22T10:32:20.000Z",
        "files_created": [],
        "files_modified": ["framework/pages/helios8/inquiries_page.py"]
      }
    ]
  },
  "test_execution_history": {
    "test_runs": [
      {
        "run": 1,
        "timestamp": "2026-01-22T10:31:55.000Z",
        "command": "pytest tests/helios8/test_submit_inquiry.py",
        "result": "failed",
        "error": "ElementNotInteractableException: Element not visible",
        "screenshot": "tests/_reports/2026-01-22T10-30-45.123456Z/screenshot_001.png"
      },
      {
        "run": 2,
        "timestamp": "2026-01-22T10:32:25.000Z",
        "command": "pytest tests/helios8/test_submit_inquiry.py",
        "result": "passed",
        "duration": "12.3s",
        "screenshot": "tests/_reports/2026-01-22T10-30-45.123456Z/screenshot_002.png"
      }
    ]
  },
  "metrics": {
    "iterations": 5,
    "hitl_triggers": 3,
    "gate_violations": 2,
    "test_runs": 8,
    "final_result": "passed"
  }
}
```

**Rejected Components (Not Implemented):**
- **Discovery Gaps Log:** Redundant with construction journal (gaps show as new files in next iteration)
- **Decision Log:** Redundant with HITL interaction log (user input captures rationale)
- **Rollback/Resume with Snapshots:** Fix forward with HITL instead of rollback to previous iteration

### FR-6: HITL System (Layer 6 Defense)

**FR-6.1:** HITL SHALL trigger reliably (ultimate safety mechanism)
- When Gate signals blocker → HITL MUST trigger
- When Hook detects loop/timeout → HITL MUST trigger
- When user types "stop" → HITL MUST trigger immediately

**FR-6.2:** HITL SHALL provide clear user signals
- Signal format: "AI blocked at [action]: [reason]. Awaiting guidance."
- Example: "AI blocked at element_wait: Timeout 30s. Continue waiting or change approach?"
- User clearly knows: AI is stopped, why it stopped, what options exist

**FR-6.3:** HITL SHALL support user interrupt anytime
- User command: "stop" (or equivalent)
- Effect: Immediate HITL trigger, workflow pauses, AI waits for guidance
- This is the escape valve if all other layers fail

### FR-7: Tool Usage (Hybrid Model)

**FR-7.1:** Tools 1-2 SHALL be core workflow
- Tool 1 (generate_tests_from_user_story): Generate BDD scenarios for structure
- Tool 2 (discover_page_elements): Bulk element discovery from Playwright snapshot

**FR-7.2:** Tools 3-6 SHALL be optional (on-demand)
- Available if user requests: "Generate scaffold for CustomerSearchPage"
- AI defaults to manual construction with Edit/Write tools
- User (developer) knows they're optional, public-facing treats as available

**FR-7.3:** Quality Gates SHALL always be active
- Regardless of how code was built (manual or tool-generated)
- Gates are Component 2, non-negotiable defense layer

### FR-8: Configuration

**FR-8.1:** System SHALL enforce headless=false (visual browser)
- Browser MUST be visible at all times
- User MUST see what AI is doing in real-time
- No override allowed (non-negotiable for pair programming)

**FR-8.2:** System SHALL provide configurable timeout monitoring
```json
{
  "timeout_monitoring": {
    "enabled": true,
    "threshold_seconds": 30,
    "actions": ["browser_navigate", "element_wait", "ajax_call"]
  }
}
```
- Default: 30 seconds
- User can increase for slow applications
- User can disable for specific long-running operations

**FR-8.3:** System SHALL default to pair programming mode
- No feature flag, no user choice at start
- Pair programming IS the workflow
- Tools 1-6 available (only developer knows 3-6 are optional)

### FR-9: Workflow Structure

**FR-9.1:** Workflow SHALL follow collaborative construction pattern
```
Step 1: User Input (Entry Point)
        - AI asks: "What test do you want to create?" (persona, action, URL)
        - AI asks: "Workflow identifier?" with explanation:
          "This creates folders at framework/pages/{workflow}/ and tests/{workflow}/
           Use to organize tests by: test run (helios7), feature (checkout-v2), sprint (auth-sprint-2)"
        - AI extracts: persona, URL, role_name from requirement
        - AI auto-detects environment (asks for approval if unknown)
        - Gate: qg_user_input validates all fields
        - Output: persona, URL, role_name, workflow, raw_requirement, detected_env_id

Step 2: Pre-flight Configuration
        - AI asks: Credential strategy? (static/dynamic/self-contained/none)
        - AI asks: Test data location? (shared/workflow/both/none)
        - AI asks: Browser visibility? (headless=false, non-negotiable)
        - AI asks: Timeout monitoring? (default 30s, enable/disable)
        - Gate: qg_preflight validates and scaffolds infrastructure
        - Output: credential_strategy, test_data_location, browser_config, timeout_config

Step 3: AI Processing (Intent Extraction)
        - AI creates: BDD scenarios (Given/When/Then)
        - AI extracts: expected_states from "Then" clauses
        - AI determines: intent (action verb)
        - Gate: qg_ai_processing validates metadata
        - Output: bdd_scenarios, expected_states, intent

Step 4: Collaborative Construction (HITL loop)
        ↓
        Tool 1: Generate BDD scenarios (structure)
        Tool 2: Discover elements (bulk extraction)
        ---
        AI builds POMs/Tasks/Roles manually with Edit/Write
        (Tools 3-6 available if user requests)
        ---
        Gates validate each piece
        HITL triggers at blockers
        Human guides at each blocker
        Repeat: build → save → test → discover gap → build more
        ↓
Step 5: Done (test passes or HITL triage)
```

**Note:** Steps 1-3 validated incrementally via HITL. Steps 4-5 pending validation.

**FR-9.2:** AI SHALL build and save incrementally
- Create CustomerSearchPage.py → Save immediately → Test
- Discover gap (need click_new_inquiry method) → Add method → Save → Test
- NOT: Plan everything → Discuss → Then generate all files

**FR-9.3:** AI SHALL stop when blocked (DD-22)
- Stop immediately (do NOT attempt multiple fixes)
- Report clearly (error, context, hypothesis)
- Wait for user guidance (do NOT proceed)

---

## 5. Non-Goals (Out of Scope)

**NG-1:** Autonomous test generation (replaced by pair programming)
- The old workflow (Steps 1-10 generate, Step 11 fix) is OUT OF SCOPE
- This PRD formalizes pair programming as replacement

**NG-2:** Headless browser mode
- Never supported in pair programming (user must see browser)
- No feature flag, no configuration option

**NG-3:** Multiple workflow modes (autonomous vs pair programming)
- Only pair programming supported
- Tools 3-6 exist but are optional (not a "mode")

**NG-4:** Modular platform architecture (not in MVP)
- Ship QA monolith first (all 6 components integrated)
- Extract components later (after customer validation)

**NG-5:** Community-contributed test regeneration
- Existing helios1-7 tests archived (not regenerated)
- Focus on one new test to validate pair programming

---

## 6. Design Considerations

### Protocol Files (Layer 1)
- **Location:** `.claude/skills/qa-management-layer/`
- **Update:** `SKILL.md` with pair programming workflow
- **Create/Update:** Collaboration guidance replacing sequential step files
- **Document:** Stop-when-blocked, build-as-you-go, HITL triggers, configuration

### Hooks (Layer 3)
- **Location:** `.claude/hooks/` (Claude Code hooks, not MCP server)
- **Hook type:** PostToolUse (monitors tool execution duration, tracks failures)
- **Configuration:** Read from `framework/resources/config/environment_config.json`

### Configuration Files
- **Location:** `framework/resources/config/`
- **Update:** `environment_config.json` with timeout monitoring, headless=false enforcement
- **Create:** `pair_programming_config.json` (if needed for modular config)

### Test Structure
- **E2E tests:** Follow production structure (helios8 or target site)
  - `framework/pages/helios8/` - Page objects
  - `framework/tasks/helios8/` - Task workflows
  - `framework/roles/helios8/` - Role orchestration
  - `tests/helios8/test_submit_inquiry.py` - Test runner
- **NO dedicated pair_programming_validation/ directory** - use production pattern

### Visual Design
- **HITL Signal Format:** Clear, actionable prompts
  - ❌ Bad: "Error occurred"
  - ✅ Good: "AI blocked at element_wait: Timeout 30s. Continue waiting or change approach?"

### User Experience
- **Transparency:** User sees browser at all times, knows when AI is blocked
- **Control:** User can interrupt anytime ("stop" command)
- **Trust:** Full audit trail shows what happened, why decisions were made

---

## 7. Technical Considerations

### Dependencies
- **FRAMEWORK.md + 28 DDs:** AI knowledge base (already exists, unchanged)
- **4-layer architecture:** Page → Task → Role → Test (unchanged)
- **MCP tools:** Tools 1-6 (1-2 core, 3-6 optional), Quality Gates (always active)
- **Playwright MCP:** Browser control, element discovery (used via Tool 2)

### Integration Points
- **Protocol files:** Read by AI at workflow start (`.claude/skills/qa-management-layer/`)
- **Quality Gates:** Called after each file save, test run (`mcp_server/tools/gates/`)
- **Hooks:** Monitor during execution (`.claude/hooks/` - PostToolUse pattern for timeout/loop detection)
- **Audit System:** Write to `tests/_audit/audit_log_[timestamp].json`

### Technical Constraints
- **Timeout monitoring:** Requires Claude Code hook infrastructure (`.claude/hooks/` PostToolUse pattern)
- **HITL triggering:** Requires clear signal mechanism from Gates/Hooks to HITL System
- **Full audit trail:** High I/O (every action logged) - acceptable for quality/compliance
- **Hook limitations:** PostToolUse hooks can only monitor after tool completes (not during execution)

### Backward Compatibility
- **Existing tests (helios1-7):** Archive to `tests/archive/`
- **Protocol files:** Old step-*.md replaced with collaboration guidance
- **Tool chain:** Tools 1-6 remain in codebase (no breaking API changes)

---

## 8. Success Metrics

### Primary Metrics (MVP)
1. **Test passes on first attempt**
   - Measure: Test execution result (pass/fail)
   - Target: 100% pass rate (no Step 11 fixes)
   - Validation: One test generated via pair programming passes

2. **HITL triggers reliably**
   - Measure: Count of blockers where HITL triggered vs AI rambled
   - Target: 100% HITL trigger rate (no missed blockers)
   - Validation: Audit log shows HITL triggered at every blocker

3. **Full session audit**
   - Measure: Can session be reconstructed from audit log?
   - Target: 100% reconstruction (every action logged)
   - Validation: Given audit log → Replay entire session timeline

### Secondary Metrics (Post-MVP)
- Time to complete test (pair programming vs autonomous)
- User satisfaction (survey: "Did you feel in control?")
- Compliance validation (audit log meets regulatory requirements)

---

## 9. Test Strategy

### Unit Tests
- **Timeout monitoring:** Hook detects >threshold, triggers HITL
- **Stop-when-blocked:** AI stops on blocker (doesn't loop)
- **Audit logging:** Each action writes to audit trail
- **Gate teaching:** Gates provide fix data on violations

**Location:** `mcp_server/_dev_tests/test_gates/` (add new gate teaching tests here)
**Tools:** pytest
**Mocking:** Mock browser actions, mock HITL responses

### Integration Tests
- **6-layer defense:** Protocol guides → Gate validates → Hook monitors → HITL triggers
- **Build-save-test cycle:** Create file → Save → Test → Validate
- **Tool chain:** Tool 1-2 called, Tools 3-6 optional

**Location:** `mcp_server/_dev_tests/test_workflow_integration/`
**Tools:** pytest with real MCP server, mock browser

### E2E/Smoke Tests
- **One complete test:** User navigates, AI builds, test passes
- **HITL trigger:** AI blocks, user guides, AI resumes
- **Audit reconstruction:** Replay session from log

**Location:** `tests/helios8/` (or target site) - follows production structure
- `framework/pages/helios8/` - Page objects
- `framework/tasks/helios8/` - Task workflows
- `framework/roles/helios8/` - Role orchestration
- `tests/helios8/test_submit_inquiry.py` - Test runner

**Tools:** Real workflow execution, real browser (visible)

### Acceptance Tests (GIVEN/WHEN/THEN)

**AT-1: Test passes on first attempt**
```gherkin
GIVEN AI and user start pair programming workflow
WHEN user guides AI to build test for "Submit inquiry"
AND AI builds incrementally (POM → Task → Role → Test)
AND gates validate each piece
AND test runs
THEN test PASSES without manual fixes
AND no Step 11 remediation required
```

**AT-2: HITL triggers on timeout**
```gherkin
GIVEN timeout monitoring enabled (30s threshold)
WHEN AI waits for element >30 seconds
THEN Hook forces HITL trigger
AND user sees: "Timeout at 30s. Continue or change?"
AND user provides guidance
AND AI resumes with new approach
```

**AT-3: HITL triggers on test failure**
```gherkin
GIVEN AI runs test
WHEN test fails (ElementNotInteractableException)
THEN Gate signals blocker
AND HITL triggers immediately
AND user sees: "Test failed at [line X]. Awaiting guidance."
AND AI does NOT attempt autonomous fixes
```

**AT-4: User interrupt works**
```gherkin
GIVEN AI is building code
WHEN user types "stop" command
THEN HITL triggers immediately
AND AI stops current action
AND AI waits for user guidance
```

**AT-5: Full audit trail logged**
```gherkin
GIVEN pair programming session completes
WHEN reviewing audit log
THEN ALL actions logged (HITL triggers, timeout events, build-save-test cycles, gate validations, hook interventions)
AND session can be reconstructed from log
AND timeline shows: what AI built, when HITL triggered, what user said
```

**AT-6: Visual browser enforced**
```gherkin
GIVEN pair programming workflow starts
WHEN browser launches
THEN headless=false enforced
AND user can see browser window
AND user can see AI clicking elements
AND user can interrupt if AI doing wrong thing
```

**AT-7: Stop-when-blocked (no rambling)**
```gherkin
GIVEN AI encounters blocker (element not found)
WHEN blocker detected
THEN AI stops immediately
AND AI reports: error message + context + hypothesis
AND AI does NOT attempt fix #1, fix #2, fix #3
AND HITL triggers once (not multiple times)
```

**AT-8: Build-save-test cycle**
```gherkin
GIVEN AI builds CustomerSearchPage
WHEN AI creates file
THEN file saved immediately (not batched)
AND test runs
AND blocker discovered (need click_new_inquiry method)
AND AI adds method → saves → tests again
```

**AT-9: Smart Gates teach fixes**
```gherkin
GIVEN AI creates Task with inline locators (DD-27 violation)
WHEN Gate validates
THEN Gate catches violation
AND Gate provides fix data: "Move locators to POM: self.pom.LOCATOR"
AND HITL triggered with fix guidance
```

**AT-10: 6-layer defense works together**
```gherkin
GIVEN AI building test
WHEN Protocol guides (Layer 1)
AND Gate validates (Layer 2)
AND Hook monitors (Layer 3)
AND Checkpoint saves (Layer 4)
AND Audit logs (Layer 5)
AND HITL provides escape (Layer 6)
THEN all 6 layers coordinate
AND if Layer 1 fails → Layer 2 catches
AND if Layer 2 fails → Layer 3 catches
AND if Layer 3 fails → Layer 6 catches (user interrupt)
```

---

## 10. Non-Functional Requirements

### Performance SLAs
- **Timeout threshold:** Default 30s (configurable 10s-120s)
- **HITL trigger latency:** <1 second from blocker detection to user prompt
- **Audit write latency:** <100ms per log entry (non-blocking)
- **File save latency:** <500ms (incremental saves acceptable)

### Retry/Backoff
- **No automatic retries** - AI does NOT retry on failure
- **HITL instead of retry** - Blocker → HITL trigger → User decides

### Error Handling
- **Blocker detection:** Gate validation failure → HITL trigger
- **Timeout exceeded:** Hook detects → HITL trigger
- **User interrupt:** "stop" command → HITL trigger
- **System failure:** Checkpoint preserves state, Audit documents failure

### Observability/Telemetry

**Events to emit (all logged to `tests/_audit/audit_log_<run_id>.json`):**

**Audit Log Events (Event Stream):**
- `{"type": "gate_validation", "timestamp": "...", "gate": "qg_user_input", "result": "pass/fail", "violations": [...], "fix_data": {...}}`
- `{"type": "tool_call", "timestamp": "...", "tool": "generate_tests_from_user_story", "input": {...}, "output": {...}}`
- `{"type": "hitl_interaction", "timestamp": "...", "trigger_reason": "test_failed", "user_input": "...", "ai_response": "...", "context": {...}}`
- `{"type": "hook_intervention", "timestamp": "...", "pattern": "timeout_exceeded", "threshold": 30, "actual": 45, "action": "force_hitl"}`
- `{"type": "hook_intervention", "timestamp": "...", "pattern": "loop_detected", "consecutive_failures": 3, "action": "force_hitl"}`

**Workflow State Events (Accumulated State in `tests/_state/<run_id>/workflow_state.json`):**
- **Steps:** `{"steps": {"step_1": {"persona": "...", "url": "...", ...}, "step_2": {...}, "step_3": {...}}}`
- **Construction journal:** `{"iterations": [{"iteration": 1, "timestamp": "...", "files_created": ["path1"], "files_modified": []}]}`
- **Test execution history:** `{"test_runs": [{"run": 1, "timestamp": "...", "command": "pytest ...", "result": "failed", "error": "...", "screenshot": "tests/_reports/<run_id>/screenshot_001.png"}]}`
- **Metrics:** `{"metrics": {"iterations": 5, "hitl_triggers": 3, "gate_violations": 2, "test_runs": 8, "final_result": "passed"}}`

**Audit Format:** JSON (enables tooling, session reconstruction)

**Tests SHALL assert:**
- Audit log contains expected event types (gate_validation, tool_call, hitl_interaction, hook_intervention)
- Workflow state contains construction_journal, test_execution_history, metrics
- Event timestamps in correct order
- Full reconstruction possible from audit log
- AuditReconstructor can parse and replay timeline
- Workflow state metrics match actual workflow (iteration count = construction_journal length)
- Screenshot references in test_execution_history are valid paths

### Security & Privacy
- **No secrets in audit log** - Credentials masked/redacted
- **Audit log access control** - Only developer/compliance access
- **Data retention** - Audit logs kept for compliance period (90 days minimum)

### Rollout & Rollback

**Rollout Plan:**
- **Phase 1:** Feature branch `feature/pair-programming-pair-programming`
- **Phase 2:** Implement PRD, commit after each task
- **Phase 3:** Validate with one test (acceptance tests pass)
- **Phase 4:** Merge to main (replace autonomous workflow)

**Feature Flag:**
- **None** - Hard switch to pair programming
- Public-facing: Pair programming IS the workflow
- Developer knows Tools 3-6 optional (not advertised)

**Rollback Plan:**
- **If pair programming fails:** Revert merge commit
- **Smoke test:** One test generation via autonomous workflow (archived helios1-7 as reference)
- **Success criteria:** Autonomous workflow still functional after revert

---

## 11. Open Questions

**OQ-1:** Should we provide migration guide for existing tests?
- Context: helios1-7 archived, but future users might have autonomous-generated tests
- Decision needed: Document how to convert autonomous tests to pair programming?

**OQ-2:** Should timeout threshold be per-action or global?
- Context: Some actions legitimately take longer (page load vs element click)
- Current: Global 30s threshold configurable
- Alternative: Per-action thresholds (e.g., navigate=60s, click=10s)

**OQ-3:** Should audit logs be human-readable or JSON-only? ✅ RESOLVED
- Context: JSON enables tooling, human-readable helps debugging
- **Decision:** JSON-only format (enables AuditReconstructor tooling for session replay)
- Human-readable output generated by AuditReconstructor on-demand

**OQ-4:** How to handle multi-session pair programming?
- Context: Long workflows might span multiple sessions
- Current: Checkpointing enables resume
- Question: Should Protocol document session boundaries explicitly?

---

## 12. Definition of Ready

**PRD is ready for task generation when:**
- ✅ Test Strategy included (unit, integration, e2e)
- ✅ 10 Acceptance Tests defined (GIVEN/WHEN/THEN)
- ✅ Non-Functional SLAs specified (performance, retry, error handling)
- ✅ Observability/Telemetry defined (events to log, test assertions)
- ✅ Security & Privacy noted (no secrets, access control, retention)
- ✅ Rollout & Rollback outlined (feature branch, merge plan, smoke test)

**Status:** ✅ READY - Proceed to Phase 3 (Divide - Task Generation)

---

**Next Phase:** Generate task breakdown using 4D Divide template
