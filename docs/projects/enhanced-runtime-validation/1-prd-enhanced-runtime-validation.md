# PRD: Enhanced Runtime Validation Gates

**Version:** 1.7 (Living Document)
**Created:** 2025-12-30
**Last Updated:** 2025-12-31
**Status:** Ready for Task Generation

**Changelog:**
- v1.7: Updated scope discovery to use URL-based detection (FR-04 clarified); Removed pattern-matching approach; Added navigation tracker API
- v1.6: Added Visual Feedback feature (Section 4.13, FR-81 to FR-88, AT-12); Updated Section 6.4 with `visual_feedback.py`
- v1.5: SRP-compliant module design - Added `scope_discovery.py`, `fix_suggester.py`; Updated Sections 6.4, 9.1, 18.3 with SRP responsibilities
- v1.4: Split Section 9.0 into 9.0a (Runtime Checkpoints) and 9.0b (Development Testing); Added Sections 14-19 (NFRs, Observability, Security, Rollout, Repo Steps, Definition of Ready)
- v1.3: Added Testing Skill reference in Section 9.0 and Section 11; mandatory testing process per phase
- v1.2: Added Section 9.0 (Test-At-Every-Checkpoint Philosophy) with 10 checkpoints and per-checkpoint test requirements
- v1.1: Added FR-77 to FR-80 (WebInterface Method Verification), AT-11

---

## 1. Introduction/Overview

**Problem:** Current quality gates validate code structure ("does it follow patterns") but not runtime viability ("will it work against the real app"). This results in code that passes all gates but fails at Step 10 (run test), requiring iterative debugging.

**Solution:** Enhance Steps 5-9 with runtime validation that catches issues at source. Before generating any code, discover workflow scope (how many pages/states). Then for each page, validate elements exist AND are interactable against the real application via Playwright.

**Entry Point:** Existing `/qa-workflow` command (no new slash commands).

**Category Claim:** Strengthens "AI Management Layer" thesis - enforcement at every step, not just guidance. Enforceable AND auditable.

---

## 2. Goals

| Goal | Measure |
|------|---------|
| First-run pass rate | 100% (tests pass on first execution) |
| Time to first passing test | Reduced (catch issues early, not at Step 10) |
| Fix iterations | Minimal (fix at source, not after generation) |
| Audit completeness | 100% (every action logged with timestamp) |
| Workflow scope accuracy | Correctly identify all pages/states before code generation |

---

## 3. User Stories

**US-1:** As an AI assistant, I need to discover workflow scope upfront so that I generate the correct number of POMs (one per page/state).

**US-2:** As an AI assistant, I need runtime validation so that generated locators actually find elements on the real page.

**US-3:** As a user, I want interactive fix loops so that I'm consulted when validation fails and can guide the fix.

**US-4:** As a user, I want a complete audit trail so that I can see exactly what was discovered, validated, fixed, and saved.

**US-5:** As a developer, I want checkpoint saves so that I can resume from any step after interruption.

**US-6:** As a user, I want the system to learn from discovered patterns so that future runs benefit from past fixes (Knowledge Base).

**US-7:** As a user, I want file change detection so that manual edits trigger re-validation of affected artifacts.

---

## 4. Functional Requirements

### 4.1 Workflow Scope Discovery (Step 5a - NEW)

| FR | Requirement |
|----|-------------|
| FR-01 | After Step 4 (test scenarios), AI initiates scope discovery before element discovery |
| FR-02 | AI navigates to starting URL and takes Playwright snapshot |
| FR-03 | AI prompts user: "What action advances this workflow?" |
| FR-04 | User performs action; AI detects page change via **URL comparison** (primary method - works universally). URL change = new page. No pattern matching required. |
| FR-05 | AI logs each new page/state with URL and derived page name (e.g., `/cart.html` → `CartPage`) |
| FR-06 | Repeat until user indicates workflow complete |
| FR-07 | AI presents scope summary: "Found N pages: [list]" for confirmation |
| FR-08 | Capture cross-POM dependencies (e.g., InquiryPage requires LoginPage) |
| FR-09 | Save checkpoint: `workflow_scope.json` |

**Implementation Notes (v1.7):**
- URL-based detection is universal - works on any site regardless of UI patterns
- Page names derived from URL path: `/checkout-step-one.html` → `CheckoutStepOnePage`
- No dependency on numbered steppers, tabs, or breadcrumbs (pattern matching removed)
- API: `tracker = create_navigation_tracker()`, `tracker.is_new_page(url, prev)`, `tracker.register_page(url)`

### 4.2 Per-Page Element Discovery (Step 5b - ENHANCED)

| FR | Requirement |
|----|-------------|
| FR-10 | For each confirmed page, navigate to that state |
| FR-11 | Take Playwright snapshot |
| FR-12 | Extract interactive elements (buttons, inputs, links, etc.) |
| FR-13 | Check Knowledge Base for known patterns (e.g., "wizard buttons need click_js") |
| FR-14 | Present page summary to user for confirmation |
| FR-15 | Save checkpoint per page: `page_{name}_elements.json` |

### 4.3 Per-Page Element Validation (Step 5c - NEW)

| FR | Requirement |
|----|-------------|
| FR-16 | For each extracted element, validate: exists in DOM |
| FR-17 | For each extracted element, validate: is visible |
| FR-18 | For each extracted element, validate: is interactable (not blocked by overlay, pointer-events, etc.) |
| FR-19 | Categorize validation failures (see Section 4.8) |
| FR-20 | On failure: STOP, report to user, propose fix, await confirmation |
| FR-21 | Re-validate after fix applied |
| FR-22 | Only proceed when all elements validated |

#### 4.3.1 WebInterface Method Verification (During Step 5c)

| FR | Requirement |
|----|-------------|
| FR-77 | When fix requires specific interaction method (e.g., `click_js`, `scroll_into_view`), check if WebInterface has that method |
| FR-78 | If method missing: STOP, report "Required method `{method}` not found in WebInterface", propose implementation with signature and body |
| FR-79 | After user approves proposed method, AI adds method to `framework/interfaces/web_interface.py` |
| FR-80 | Re-validate element with newly added method before proceeding |

**Flow:**
```
Element validation fails (NOT_INTERACTABLE)
    ↓
Determine fix: needs click_js
    ↓
Check: WebInterface.has_method("click_js")?
    ├─ YES → Record "use click_js" for POM generation → Continue
    └─ NO → STOP
            ├─ Report: "click_js not found in WebInterface"
            ├─ Propose: def click_js(self, locator): ...
            ├─ User approves
            ├─ AI adds method to web_interface.py
            └─ Re-validate element → Continue
```

### 4.4 POM Generation with Runtime Validation (Step 6 - ENHANCED)

| FR | Requirement |
|----|-------------|
| FR-23 | Generate POM for each validated page |
| FR-24 | Run existing structural gate (qg_page_object) |
| FR-25 | NEW: Runtime validation - each locator finds element on real page |
| FR-26 | NEW: Runtime validation - each action method executes without error |
| FR-27 | NEW: Runtime validation - each state-check method returns expected type |
| FR-28 | On failure: categorize error, propose fix, user confirms, re-validate |
| FR-29 | Update Knowledge Base if new pattern discovered |
| FR-30 | Save checkpoint: validated POM code |

### 4.5 Downstream Steps (Steps 7-9 - ENHANCED)

| FR | Requirement |
|----|-------------|
| FR-31 | Step 7 (Task): Validate Task methods call POM methods correctly |
| FR-32 | Step 7 (Task): Confirm no locators in Task code (DD-27) |
| FR-33 | Step 8 (Role): Validate Role orchestrates Tasks correctly |
| FR-34 | Step 9 (Test): Validate assertions use POM state methods (DD-15) |
| FR-35 | Each step follows same pattern: Generate → Validate → Fix → Confirm → Proceed |

### 4.6 Mandatory Final Gate (Step 10 - ENHANCED)

| FR | Requirement |
|----|-------------|
| FR-36 | Regardless of path (tool chain OR manual edit), must pass final gate |
| FR-37 | Final gate validates: all POMs pass structural + runtime |
| FR-38 | Final gate validates: all Tasks pass (no locators, no skeleton) |
| FR-39 | Final gate validates: all Roles pass (no skeleton) |
| FR-40 | Final gate validates: Test code passes (POM assertions) |
| FR-41 | Final gate validates: Import paths correct |
| FR-42 | PASS → Save files → Run test |
| FR-43 | FAIL → Block, report issues, user fixes |

### 4.7 Audit Trail

| FR | Requirement |
|----|-------------|
| FR-44 | Log every action with timestamp: `[ISO_TIMESTAMP] EVENT: details` |
| FR-45 | Log categories: SCOPE_*, DISCOVERY_*, VALIDATION_*, FIX_*, GATE_*, KB_*, FILE_* |
| FR-46 | Capture: what was found, what failed, what was fixed, final state |
| FR-47 | Save audit log: `audit/{workflow_name}_{timestamp}.log` |
| FR-48 | Diff detection: track hash at generation vs. final save |
| FR-49 | Log diff summary: "Generated X, User modified Y, Final state Z" |

### 4.8 Error Categorization

| FR | Requirement |
|----|-------------|
| FR-50 | Category: `LOCATOR_NOT_FOUND` - element doesn't exist in DOM |
| FR-51 | Category: `NOT_VISIBLE` - element exists but hidden |
| FR-52 | Category: `NOT_INTERACTABLE` - pointer events blocked, needs click_js |
| FR-53 | Category: `STALE_REFERENCE` - DOM changed after capture |
| FR-54 | Category: `METHOD_NOT_FOUND` - called method doesn't exist |
| FR-55 | Each category has specific fix approach in fix proposal |

### 4.9 Knowledge Base Integration

| FR | Requirement |
|----|-------------|
| FR-56 | Before generating code, check KB for known patterns |
| FR-57 | Pattern example: "wizard buttons need click_js" |
| FR-58 | Pattern example: "dropdowns need select_dropdown_by_visible_text" |
| FR-59 | When new pattern discovered during fix, save to KB |
| FR-60 | KB location: `docs/KNOWLEDGE_BASE.md` |

### 4.10 Re-entry Points (Checkpoints)

| FR | Requirement |
|----|-------------|
| FR-61 | Checkpoint after scope discovery: `workflow_scope.json` |
| FR-62 | Checkpoint after each page discovery: `page_{name}_elements.json` |
| FR-63 | Checkpoint after each POM validated: `page_{name}_pom.py` |
| FR-64 | Checkpoint after each downstream step |
| FR-65 | On resume, detect last checkpoint and offer to continue from there |

### 4.11 Re-Validation Triggers

| FR | Requirement |
|----|-------------|
| FR-66 | Detect file changes in tracked artifacts |
| FR-67 | `pages/**/*.py` change → trigger POM gate re-run |
| FR-68 | `tasks/**/*.py` change → trigger Task gate re-run |
| FR-69 | `roles/**/*.py` change → trigger Role gate re-run |
| FR-70 | `tests/**/*.py` change → trigger Test gate re-run |
| FR-71 | Log re-validation trigger in audit |

### 4.12 Expected Catch List (What Enhanced Gates Must Detect)

| FR | Requirement |
|----|-------------|
| FR-72 | Conditional paths (2-step vs 5-step wizard based on data) |
| FR-73 | Element interactability (pointer events interception → need click_js) |
| FR-74 | Assertion accuracy (success alert vs Notes section) |
| FR-75 | Form validation rules (no numbers in name fields) |
| FR-76 | Method availability (select_option vs select_dropdown_by_visible_text) |

### 4.13 Visual Feedback During Validation (NEW)

| FR | Requirement |
|----|-------------|
| FR-81 | During element validation, inject visual highlighting into browser for validated elements |
| FR-82 | Valid elements: green outline (3px solid #00ff00) with label |
| FR-83 | Invalid elements: red outline (3px solid #ff0000) with error category label |
| FR-84 | Display pipeline status header showing current step and progress |
| FR-85 | Show validation results panel with element-by-element status |
| FR-86 | Visual feedback uses JavaScript injection via Playwright `browser_evaluate` |
| FR-87 | Clean up visual overlays after validation step completes (optional, user preference) |
| FR-88 | Support for both headed (visible) and headless modes (skip visual in headless) |

**Visual Feedback Flow:**
```
Element Validation Starts
    |
    v
For each element:
    +-- Find element in DOM
    +-- Validate (exists, visible, interactable)
    +-- Inject CSS class:
    |       Valid   -> .validation-ok (green outline)
    |       Invalid -> .validation-fail (red outline)
    +-- Update results panel
    |
    v
Show summary header:
    "Step 2: RuntimeValidator -> X Valid, Y Errors"
    |
    v
User sees visual state of all elements on page
```

**CSS Injection Example:**
```css
.validation-ok {
    outline: 3px solid #00ff00 !important;
    outline-offset: 2px;
}
.validation-fail {
    outline: 3px solid #ff0000 !important;
    outline-offset: 2px;
}
```

**Benefits:**
- User immediately sees which elements passed/failed validation
- Reduces cognitive load during fix loops
- Makes debugging faster (can correlate element visually with error message)
- Provides confidence that validation is working correctly

---

## 5. Non-Goals (Out of Scope)

| Non-Goal | Reason |
|----------|--------|
| Modify existing MCP tool generators (Tools 1-6) | Keep generators as-is; gates catch their issues |
| Add new slash commands | Use existing `/qa-workflow` entry point |
| Handle parallel workflows | Single workflow at a time for v1 |
| Change existing gate detection logic | Current structural detection works; add runtime on top |
| CI/CD integration | Focus on local execution first |
| Automated fix application | User must confirm all fixes |

---

## 6. Design Considerations

### 6.1 Integration with Existing 10-Step Flow

```
/qa-workflow
     │
Step 1-4: (existing - unchanged)
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 5: ENHANCED Element Discovery                          │
│   5a: Workflow Scope Discovery (NEW) ← How many pages?      │
│   5b: Per-page element discovery (iterate)                  │
│   5c: Per-page element validation (NEW) ← Exists + interact │
│   Checkpoint: workflow_scope.json, page_*_elements.json     │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 6: ENHANCED POM Generation (per page)                  │
│   6a: Generate POM                                          │
│   6b: Structural gate (existing qg_page_object)             │
│   6c: Runtime gate (NEW) ← Locators work, methods execute   │
│   6d: Fix loop with user                                    │
│   6e: KB update if new pattern                              │
│   Checkpoint: page_{name}_pom.py (validated)                │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
Steps 7-9: (same enhanced pattern - generate, validate, fix, proceed)
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│ Step 10: MANDATORY FINAL GATE                               │
│   - All artifacts validated                                 │
│   - Diff detection logged                                   │
│   - PASS → Save → Run                                       │
│   - FAIL → Block → Report → User fixes                      │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
AUDIT LOG: Complete trail from Step 1 to completion
```

### 6.2 Two-Pass Approach

**Pass 1 (Scope Discovery):**
- Walk through entire workflow with user
- Count pages/states
- Capture dependencies
- User confirms scope before any code generation

**Pass 2 (Detailed Discovery):**
- For each confirmed page, discover elements
- Validate each element against real page
- Generate and validate POM
- Proceed only when 100% validated

### 6.3 Cross-POM Dependencies

```json
{
  "workflow": "create_inquiry",
  "pages": [
    {"name": "LoginPage", "order": 1, "entry_url": "/login"},
    {"name": "InquiryFormPage", "order": 2, "requires": ["LoginPage"]},
    {"name": "ConfirmationPage", "order": 3, "requires": ["InquiryFormPage"]}
  ],
  "dependencies": {
    "InquiryFormPage": "must be logged in",
    "ConfirmationPage": "must have submitted form"
  }
}
```

### 6.4 File Structure (New/Modified)

```
mcp_server/
├── tools/
│   └── gates/
│       ├── qg_discovered_elements.py  ← ENHANCED (runtime validation)
│       ├── qg_page_object.py          ← ENHANCED (runtime validation)
│       ├── qg_task.py                 ← ENHANCED (runtime validation)
│       ├── qg_role.py                 ← ENHANCED (runtime validation)
│       ├── qg_test_runner.py          ← ENHANCED (runtime validation)
│       └── qg_save_run.py             ← ENHANCED (mandatory final gate)
│
├── state/
│   ├── workflow_state.json            ← Existing
│   ├── workflow_scope.json            ← NEW: Scope discovery output
│   └── page_*_elements.json           ← NEW: Per-page checkpoints
│
├── audit/                             ← NEW: Audit logs
│   └── {workflow}_{timestamp}.log
│
└── utils/
    ├── scope_discovery.py            ← NEW: Two-pass scope discovery
    ├── runtime_validator.py          ← NEW: Playwright-based validation + error categorization
    ├── fix_suggester.py              ← NEW: Fix suggestions (returns Optional, None if no known fix)
    ├── knowledge_base.py             ← NEW: KB read/write utilities
    ├── webinterface_checker.py       ← NEW: WebInterface method existence check
    └── visual_feedback.py            ← NEW: Browser visual highlighting during validation
```

### 6.5 Design Clarifications

| ID | Clarification | Date |
|----|---------------|------|
| DC-01 | Multi-page loop tracking only applies to Step 6 (POMs). POMs are 1:1 with pages. Tasks are per-domain (shared), Roles are per-persona, Tests are per-scenario - none require loop tracking. | 2025-12-31 |

---

## 7. Technical Considerations

### 7.1 Dependencies

- Existing MCP server infrastructure
- Existing quality gates (structural validation)
- Playwright MCP integration (for runtime validation)
- Python 3.x, JSON for state/checkpoints

### 7.2 Integration Points

- `/qa-workflow` slash command triggers enhanced flow
- Playwright `browser_snapshot` for element discovery
- Playwright `browser_click`, `browser_type` for interactability testing
- Existing gates enhanced with runtime validation layer

### 7.3 Constraints

- Runtime validation requires live browser session (Playwright)
- User must be present for fix confirmations (not fully autonomous)
- Single workflow at a time (no parallel execution)
- Gates must remain fast (<5s for structural, <30s for runtime)

---

## 8. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| First-run pass rate | 100% | Tests pass on first `run_test` execution |
| Time to first passing test | < 50% of current | Compare before/after enhancement |
| Fix iterations per workflow | < 3 | Count fix loops in audit log |
| Audit log completeness | 100% | Every action has timestamp + details |
| Scope discovery accuracy | 100% | All pages/states identified before code gen |
| KB pattern reuse | > 50% | Second run of similar workflow uses KB patterns |

---

## 9. Test Strategy

### 9.0a Runtime Checkpoints (What the SYSTEM Validates)

**These checkpoints describe what the ENHANCED SYSTEM will validate during `/qa-workflow` execution. This is the core functionality we are building.**

#### Checkpoint Matrix

| Checkpoint | When | What to Test | Block If Fail |
|------------|------|--------------|---------------|
| CP-01 | After Step 5a (Scope Discovery) | All pages identified? Dependencies captured? | Cannot proceed to 5b |
| CP-02 | After Step 5b (Element Discovery) per page | Elements extracted? KB consulted? | Cannot proceed to 5c for this page |
| CP-03 | After Step 5c (Element Validation) per element | Exists? Visible? Interactable? | Cannot proceed until fixed |
| CP-04 | After WebInterface method check | Method exists? If not, proposed and added? | Cannot proceed until method available |
| CP-05 | After Step 6 (POM Generation) per page | Structural gate pass? Runtime gate pass? | Cannot proceed to Step 7 |
| CP-06 | After Step 7 (Task Generation) | No locators? Calls POM methods correctly? | Cannot proceed to Step 8 |
| CP-07 | After Step 8 (Role Generation) | Orchestrates Tasks correctly? No skeleton? | Cannot proceed to Step 9 |
| CP-08 | After Step 9 (Test Generation) | Uses POM state assertions? Imports correct? | Cannot proceed to Step 10 |
| CP-09 | After Step 10 (Final Gate) | All artifacts pass? Diff logged? | Cannot save/run |
| CP-10 | After test execution | Test passes? If not, audit trail complete? | Workflow complete or restart |

#### Per-Checkpoint Test Requirements

**CP-01 (Scope Discovery):**
```
□ Correct number of pages identified
□ Page names are valid (PascalCase)
□ Entry URLs captured
□ Dependencies mapped (if multi-page)
□ User confirmed scope
□ workflow_scope.json saved
□ Audit log entry created
```

**CP-02 (Element Discovery):**
```
□ Elements extracted from Playwright snapshot
□ Element types identified (button, input, link, etc.)
□ KB checked for known patterns
□ User confirmed element list
□ page_{name}_elements.json saved
□ Audit log entry created
```

**CP-03 (Element Validation):**
```
□ Each element: exists in DOM
□ Each element: is visible
□ Each element: is interactable
□ Failures categorized correctly
□ Fix proposed for each failure
□ User confirmed each fix
□ Re-validation passed after fix
□ Audit log entry for each validation
```

**CP-04 (WebInterface Method Check):**
```
□ Required method identified
□ WebInterface scanned for method
□ If missing: STOP triggered
□ Implementation proposed
□ User approved implementation
□ Method added to web_interface.py
□ Re-validation passed with new method
□ Audit log entry created
```

**CP-05 (POM Generation):**
```
□ POM generated for page
□ Structural gate: no skeleton code
□ Structural gate: locators present
□ Structural gate: state methods match expected_states
□ Runtime gate: each locator finds element
□ Runtime gate: each method executes
□ KB updated if new pattern
□ Checkpoint saved
□ Audit log entry created
```

**CP-06 through CP-08 (Task/Role/Test):**
```
□ Code generated
□ Structural gate passed
□ Runtime validation passed (methods exist, calls valid)
□ No skeleton code
□ Checkpoint saved
□ Audit log entry created
```

**CP-09 (Final Gate):**
```
□ All POMs validated
□ All Tasks validated
□ All Roles validated
□ Test code validated
□ Import paths verified
□ Diff detection logged
□ Ready for save
```

**CP-10 (Execution):**
```
□ Files saved correctly
□ Test executed
□ Result captured (pass/fail)
□ If fail: full audit trail available for debugging
□ Workflow complete
```

---

### 9.0b Development Testing (How WE Test as We BUILD)

**This section describes how we test OUR CODE as we implement each phase. Follow `.claude/skills/testing/SKILL.md`.**

**Principle:** Test at every development phase. Do NOT proceed to next phase until current phase tests pass.

**MANDATORY: Follow Testing Skill Process**

Before testing ANY implementation phase:

1. **Define Test Pyramid** for the component (see skill Section "Testing Strategy Framework")
2. **Apply Test Coverage Matrix** — happy path, negative, edge cases, boundary
3. **Run Tests** with visual feedback (`-v`, `--html`)
4. **On Failure** — Follow failure protocol:
   - STOP (do not auto-fix)
   - REPORT (test name, error, location)
   - ANALYZE (expected vs actual)
   - DISCUSS DEFECT (ask user: create defect entry?)
   - FIX OPTIONS (present 2-3 approaches with tradeoffs)
   - DISCUSS FIX (ask user: which approach?)
   - FIX (implement approved fix only)
   - RE-TEST (run same tests again)
   - RESOLVE (update defect status)

**Key Rules from Testing Skill:**
- Never auto-fix without user discussion
- Always present fix options before implementing
- Generate HTML report every run
- Track defects systematically

**Development Testing vs Runtime Checkpoints:**

| Aspect | Development Testing (9.0b) | Runtime Checkpoints (9.0a) |
|--------|---------------------------|---------------------------|
| When | As we BUILD this feature | When USER runs `/qa-workflow` |
| Who | Developer/AI | The enhanced system |
| What | Tests our implementation code | Validates user's workflow artifacts |
| How | pytest, testing skill | Playwright, gates |

---

### 9.1 Unit Tests

| Component | Test Focus |
|-----------|------------|
| `scope_discovery.py` | Scope analysis, page counting, dependency detection |
| `runtime_validator.py` | Element exists, visible, interactable checks, error categorization |
| `fix_suggester.py` | Fix suggestions for each error category, Optional return (None when no fix) |
| `knowledge_base.py` | Pattern read/write, pattern matching |
| `webinterface_checker.py` | Method existence check, method addition |
| Enhanced gates | Runtime validation logic added to existing tests |

### 9.2 Integration Tests

| Test | Purpose | Checkpoint |
|------|---------|------------|
| `test_scope_discovery.py` | Multi-page workflow correctly identified | CP-01 |
| `test_element_discovery.py` | Elements extracted per page | CP-02 |
| `test_element_validation.py` | Validation catches issues, categorizes correctly | CP-03 |
| `test_webinterface_method_check.py` | Missing methods detected, proposed, added | CP-04 |
| `test_runtime_validation.py` | Failed elements caught and categorized | CP-03, CP-05 |
| `test_fix_loop.py` | Fix proposed, user confirms, re-validation works | CP-03, CP-04 |
| `test_checkpoint_resume.py` | Resume from any checkpoint | All CPs |
| `test_file_change_trigger.py` | Manual edit triggers re-validation | CP-05 to CP-08 |
| `test_checkpoint_blocking.py` | Cannot proceed if checkpoint fails | All CPs |

### 9.3 E2E Tests

| Test | Purpose |
|------|---------|
| `test_e2e_simple_workflow.py` | Single-page workflow with runtime validation |
| `test_e2e_multi_page_workflow.py` | Multi-page workflow with scope discovery |
| `test_e2e_audit_completeness.py` | Full audit trail generated |

### 9.4 Test Commands

```bash
# Run all enhanced gate tests
pytest mcp_server/_dev_tests/test_gates/ -v -k "runtime"

# Run integration tests
pytest mcp_server/_dev_tests/test_integration/ -v

# Run E2E tests
pytest mcp_server/_dev_tests/test_e2e/ -v
```

---

## 10. Acceptance Tests (GIVEN/WHEN/THEN)

**AT-01: Scope Discovery Identifies Multiple Pages**
```
GIVEN a workflow that spans Login → Inquiry → Confirmation
WHEN I run scope discovery via /qa-workflow
THEN AI identifies 3 distinct pages
AND prompts me to confirm before proceeding
AND saves workflow_scope.json with all 3 pages
```

**AT-02: Runtime Validation Catches Non-Interactable Element**
```
GIVEN a page with a button blocked by overlay (pointer-events: none)
WHEN element validation runs
THEN validation fails with category NOT_INTERACTABLE
AND AI proposes fix: use click_js instead of click
AND awaits my confirmation before applying
```

**AT-03: Fix Loop Re-Validates After Fix**
```
GIVEN a locator that fails validation
WHEN I confirm the proposed fix
THEN AI applies the fix
AND re-runs validation on that element
AND only proceeds when validation passes
```

**AT-04: Audit Trail Captures Full History**
```
GIVEN I complete a workflow via /qa-workflow
WHEN I check the audit log
THEN every action has ISO timestamp
AND I can see: scope discovery, element validation, fixes applied, final state
AND diff detection shows what was generated vs. modified
```

**AT-05: Checkpoint Resume Works**
```
GIVEN I completed Step 5 (scope + element discovery)
AND workflow was interrupted
WHEN I restart /qa-workflow
THEN system detects existing checkpoints
AND offers to resume from Step 6
AND I don't have to redo Step 5
```

**AT-06: Knowledge Base Reused**
```
GIVEN I previously discovered "wizard buttons need click_js"
AND KB was updated with this pattern
WHEN I run a new workflow with similar wizard buttons
THEN AI checks KB before generating
AND applies click_js pattern automatically
```

**AT-07: File Change Triggers Re-Validation**
```
GIVEN I have a validated LoginPage POM
WHEN I manually edit login_page.py
THEN system detects file change
AND triggers POM gate re-validation
AND logs the re-validation in audit
```

**AT-08: Mandatory Final Gate Blocks Bad Code**
```
GIVEN code was generated (or manually edited) with a broken locator
WHEN Step 10 final gate runs
THEN gate fails with specific error
AND blocks save/run
AND reports which artifact failed and why
```

**AT-09: Cross-POM Dependencies Tracked**
```
GIVEN a workflow where InquiryPage requires logged-in state
WHEN scope discovery completes
THEN dependency map shows InquiryPage requires LoginPage
AND this is saved in workflow_scope.json
```

**AT-10: Conditional Paths Detected**
```
GIVEN a wizard that has 2 steps for some data, 5 steps for other data
WHEN I walk through scope discovery
THEN AI detects the branching point
AND logs both paths in scope summary
AND asks which path to generate code for
```

**AT-11: WebInterface Method Verification**
```
GIVEN an element requires click_js to interact (pointer-events blocked)
AND WebInterface does not have a click_js method
WHEN Step 5c element validation runs
THEN AI detects method is missing
AND STOPS with message "Required method click_js not found in WebInterface"
AND proposes implementation: def click_js(self, locator): ...
AND waits for user approval
WHEN user approves
THEN AI adds click_js method to framework/interfaces/web_interface.py
AND re-validates the element with the new method
AND proceeds only after validation passes
```

**AT-12: Visual Feedback During Validation**
```
GIVEN element validation is running in headed browser mode
WHEN RuntimeValidator validates elements on the page
THEN valid elements are highlighted with green outline (3px solid #00ff00)
AND invalid elements are highlighted with red outline (3px solid #ff0000)
AND a status header shows current pipeline step and progress
AND a results panel displays element-by-element validation status
AND user can visually correlate highlighted elements with validation results
```

---

## 11. Implementation Order (Step-by-Step Rollout)

**Approach:** Implement one step at a time, test thoroughly before moving to next.

| Phase | Step | Deliverable | Test Before Proceed |
|-------|------|-------------|---------------------|
| 1 | Step 5a | Scope Discovery | Multi-page workflow correctly identified |
| 2 | Step 5b | Per-page Element Discovery | Elements extracted from each page |
| 3 | Step 5c | Element Validation | Runtime validation catches issues |
| 4 | Step 6 | POM Runtime Validation | Generated POM validated against real page |
| 5 | Step 7 | Task Runtime Validation | Task methods validated |
| 6 | Step 8 | Role Runtime Validation | Role orchestration validated |
| 7 | Step 9 | Test Runtime Validation | Assertions validated |
| 8 | Step 10 | Mandatory Final Gate | Full sweep blocks bad code |
| 9 | Audit | Complete Audit Trail | Every action logged |
| 10 | KB | Knowledge Base Integration | Patterns saved and reused |
| 11 | Triggers | Re-Validation Triggers | File changes trigger gates |
| 12 | Resume | Checkpoint Resume | Can resume from any step |

**Process per phase (MANDATORY):**

```
1. IMPLEMENT
   └─ Implement feature code

2. TEST (Follow Testing Skill)
   ├─ 2a. Define test pyramid for this component
   ├─ 2b. Create test matrix (happy, negative, edge, boundary)
   ├─ 2c. Write unit tests
   ├─ 2d. Write integration tests
   ├─ 2e. Run tests with visual feedback (-v --html)
   └─ 2f. Generate HTML report

3. ON FAILURE (Follow Testing Skill Failure Protocol)
   ├─ STOP — do not auto-fix
   ├─ REPORT — show test name, error, location
   ├─ ANALYZE — expected vs actual
   ├─ DISCUSS DEFECT — ask user: create defect entry?
   ├─ FIX OPTIONS — present 2-3 approaches
   ├─ DISCUSS FIX — ask user: which approach?
   ├─ FIX — implement approved fix only
   ├─ RE-TEST — run same tests again
   └─ RESOLVE — update defect status

4. VALIDATE
   └─ Manual validation with real workflow

5. DOCUMENT
   └─ Update documentation

6. GATE
   └─ All tests pass? → Proceed to next phase
   └─ Any test fails? → Back to step 3
```

**Task Generation Note:** When generating tasks for Phase 2, include explicit testing subtasks that reference `.claude/skills/testing/SKILL.md` for each implementation phase.

---

## 12. Open Questions

| Question | Status | Notes |
|----------|--------|-------|
| How to handle auth-required pages in scope discovery? | Open | May need credential strategy from Step 1 |
| Should runtime validation run in headless or headed mode? | Open | Headed useful for debugging |
| How to handle dynamic content (loading spinners, AJAX)? | Open | May need configurable waits |
| Should KB patterns be workflow-specific or global? | Open | Global preferred for reuse |

---

## 13. Rollout Plan

1. **Phase 1:** Implement Step 5a (Scope Discovery) - test thoroughly
2. **Phase 2:** Implement Step 5b-5c (Element Discovery + Validation) - test thoroughly
3. **Phase 3:** Implement Step 6 enhancement (POM Runtime) - test thoroughly
4. **Phase 4-7:** Implement Steps 7-10 enhancements - test each
5. **Phase 8-11:** Implement Audit, KB, Triggers, Resume - test each
6. **Final:** Full E2E validation with real workflow

**Rollback:** If enhanced gates cause issues, existing structural gates still function. Runtime validation is additive, not replacement.

---

## 14. Non-Functional Requirements

### 14.1 Performance SLAs

| Operation | Target | Verification |
|-----------|--------|--------------|
| Structural gate validation | < 5 seconds | Timer in gate code |
| Runtime validation per element | < 10 seconds | Timer in validator |
| Full checkpoint validation | < 30 seconds | Timer in checkpoint code |
| Audit log write | < 100ms | Timer in audit module |
| KB pattern lookup | < 500ms | Timer in KB module |

### 14.2 Retry & Error Handling

| Scenario | Retry Policy | Fallback |
|----------|--------------|----------|
| Playwright connection lost | 3 retries, 2s backoff | STOP, report to user |
| Element not found | 1 retry after 2s wait | Categorize as LOCATOR_NOT_FOUND |
| Gate timeout | No retry | STOP, report timeout |
| File write failure | 2 retries | STOP, report to user |

---

## 15. Observability & Telemetry

### 15.1 Audit Log Events

| Event | Format | When |
|-------|--------|------|
| `SCOPE_START` | `[ts] SCOPE_START: url={url}` | Scope discovery begins |
| `SCOPE_PAGE_FOUND` | `[ts] SCOPE_PAGE_FOUND: page={name}, url={url}` | New page detected |
| `SCOPE_COMPLETE` | `[ts] SCOPE_COMPLETE: pages={count}` | Scope confirmed |
| `DISCOVERY_START` | `[ts] DISCOVERY_START: page={name}` | Element discovery begins |
| `DISCOVERY_ELEMENT` | `[ts] DISCOVERY_ELEMENT: name={name}, type={type}` | Element found |
| `VALIDATION_START` | `[ts] VALIDATION_START: element={name}` | Validation begins |
| `VALIDATION_PASS` | `[ts] VALIDATION_PASS: element={name}` | Element validated |
| `VALIDATION_FAIL` | `[ts] VALIDATION_FAIL: element={name}, category={cat}` | Validation failed |
| `FIX_PROPOSED` | `[ts] FIX_PROPOSED: element={name}, fix={desc}` | Fix suggested |
| `FIX_APPROVED` | `[ts] FIX_APPROVED: element={name}` | User approved fix |
| `FIX_APPLIED` | `[ts] FIX_APPLIED: element={name}` | Fix implemented |
| `GATE_PASS` | `[ts] GATE_PASS: step={step}` | Gate passed |
| `GATE_FAIL` | `[ts] GATE_FAIL: step={step}, reason={reason}` | Gate failed |
| `KB_PATTERN_FOUND` | `[ts] KB_PATTERN_FOUND: pattern={name}` | KB pattern matched |
| `KB_PATTERN_SAVED` | `[ts] KB_PATTERN_SAVED: pattern={name}` | New pattern saved |
| `CHECKPOINT_SAVED` | `[ts] CHECKPOINT_SAVED: file={path}` | Checkpoint created |
| `FILE_CHANGED` | `[ts] FILE_CHANGED: path={path}` | File change detected |
| `REVALIDATION_TRIGGERED` | `[ts] REVALIDATION_TRIGGERED: artifact={name}` | Re-validation started |

### 15.2 Testing Observability

Tests should assert:
- Correct audit events emitted in correct order
- Timestamps are valid ISO format
- All required fields present
- No orphan events (every START has corresponding COMPLETE/PASS/FAIL)

---

## 16. Security & Privacy

### 16.1 Secrets Policy

| Rule | Implementation |
|------|----------------|
| No secrets in repo | `.gitignore` includes `**/secrets/**`, `**/*.env` |
| Credentials from config | `test_users.json` for test credentials (not committed) |
| No hardcoded passwords | Gates check for hardcoded credential patterns |

### 16.2 Data Handling

| Data Type | Handling |
|-----------|----------|
| Audit logs | Local only, not committed |
| Checkpoints | Local only, `.gitignore` `mcp_server/state/*.json` |
| KB patterns | Committed (no sensitive data) |
| Screenshots | Local only if captured |

### 16.3 Threats & Mitigations

| Threat | Mitigation |
|--------|------------|
| Malicious locator injection | Validate locator format before use |
| Code injection via generated code | Structural gate checks for suspicious patterns |
| Sensitive data in audit logs | Mask credentials in log output |

---

## 17. Rollout & Rollback

### 17.1 Feature Flag

| Flag | Default | Description |
|------|---------|-------------|
| `ENHANCED_RUNTIME_VALIDATION` | `false` | Enable enhanced gates |
| `SCOPE_DISCOVERY_ENABLED` | `false` | Enable Step 5a scope discovery |
| `KB_INTEGRATION_ENABLED` | `false` | Enable KB pattern matching |

### 17.2 Rollout Plan

| Phase | What | Flag State |
|-------|------|------------|
| Phase 1 | Step 5a (Scope Discovery) | `SCOPE_DISCOVERY_ENABLED=true` |
| Phase 2 | Step 5b-5c (Element Discovery + Validation) | `ENHANCED_RUNTIME_VALIDATION=true` |
| Phase 3 | Step 6 (POM Runtime) | (same flag) |
| Phase 4-7 | Steps 7-10 | (same flag) |
| Phase 8+ | KB, Triggers, Resume | `KB_INTEGRATION_ENABLED=true` |

### 17.3 Rollback

| Scenario | Action |
|----------|--------|
| Enhanced gates cause issues | Set `ENHANCED_RUNTIME_VALIDATION=false` |
| Scope discovery breaks flow | Set `SCOPE_DISCOVERY_ENABLED=false` |
| Full rollback | All flags `false`, existing structural gates still function |

### 17.4 Smoke Test (Rollback Verification)

```
GIVEN all enhanced flags are set to false
WHEN I run /qa-workflow
THEN existing 11-step flow works as before
AND no enhanced validation runs
AND structural gates still function
```

---

## 18. Repo Steps

### 18.1 PRD Location

- Save as: `docs/projects/enhanced-runtime-validation/1-prd-enhanced-runtime-validation.md` ✓

### 18.2 Task List Location

- Save as: `docs/projects/enhanced-runtime-validation/2-tasks-enhanced-runtime-validation.md`

### 18.3 Implementation Files

| New File | Location | Responsibility (SRP) |
|----------|----------|---------------------|
| `scope_discovery.py` | `mcp_server/utils/` | Track pages via URL changes during navigation. API: `create_navigation_tracker()`, `is_new_page()`, `register_page()`, `get_scope_result()` |
| `runtime_validator.py` | `mcp_server/utils/` | Is element usable? What's wrong? (categorization) |
| `fix_suggester.py` | `mcp_server/utils/` | Given error, what fix to try? (returns Optional) |
| `knowledge_base.py` | `mcp_server/utils/` | Read/write patterns from KB file |
| `webinterface_checker.py` | `mcp_server/utils/` | Does WebInterface have this method? |
| `visual_feedback.py` | `mcp_server/utils/` | Inject visual highlighting into browser during validation |
| Audit logs | `mcp_server/audit/` (gitignored) | - |
| Checkpoints | `mcp_server/state/` (gitignored) | - |

### 18.4 Test Files

| Test File | Location |
|-----------|----------|
| Unit tests | `mcp_server/_dev_tests/test_runtime_validator.py` |
| Gate tests | `mcp_server/_dev_tests/test_gates/test_enhanced_*.py` |
| Integration tests | `mcp_server/_dev_tests/test_integration/` |
| E2E tests | `mcp_server/_dev_tests/test_e2e/` |

### 18.5 Git Workflow

```bash
# Branch naming
git checkout -b feature/enhanced-runtime-validation

# Commit per phase
git commit -m "feat: implement Step 5a scope discovery"
git commit -m "feat: implement Step 5b-5c element validation"
# etc.
```

---

## 19. Definition of Ready (Gate Before Task Generation)

**PRD is ready for task generation when all checkboxes are complete:**

- [x] Test Strategy defined (Section 9)
- [x] At least 5 Acceptance Tests (Section 10 - 11 ATs defined)
- [x] Non-Functional SLAs defined (Section 14)
- [x] Observability/Telemetry defined (Section 15)
- [x] Security & Privacy notes (Section 16)
- [x] Rollout & Rollback plan (Section 17)
- [x] Repo Steps defined (Section 18)
- [x] All SESSION.md items captured (items 4-13)
- [x] Testing Skill referenced (Section 9.0b, Section 11)

**Status: READY FOR TASK GENERATION**

---

## 20. References

| Document | Location |
|----------|----------|
| Existing QA Execution Engine PRD | `docs/projects/qa-execution-engine/1-prd-qa-execution-engine.md` |
| Step definitions | `.claude/skills/qa-management-layer/references/step-*.md` |
| Design decisions | `CLAUDE.md` (DD-01 through DD-33) |
| Knowledge Base | `docs/KNOWLEDGE_BASE.md` |
| Testing Skill | `.claude/skills/testing/SKILL.md` |
| Session context | `SESSION.md` (design discussion items 4-13) |

---

*PRD v1.4 - Living document. Update as implementation proceeds.*
