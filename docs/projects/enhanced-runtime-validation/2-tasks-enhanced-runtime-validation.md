# Task List: Enhanced Runtime Validation Gates

**PRD:** `1-prd-enhanced-runtime-validation.md`
**Generated:** 2025-12-30
**Version:** 1.5 (Tasks 1-8 complete, URL-based scope discovery implemented)

---

## Design Principles

### Single Responsibility Principle (SRP)

Each module has ONE responsibility:

| Module | Single Responsibility | Returns |
|--------|----------------------|---------|
| `scope_discovery.py` | "Track pages via URL changes during navigation" | ScopeResult (page_count, pages list) |
| `runtime_validator.py` | "Is element usable? What's wrong?" | Validation result with error category |
| `fix_suggester.py` | "Given error, what fix to try?" | `Optional[dict]` - None if no known fix |
| `knowledge_base.py` | "Read/write patterns from KB file" | Pattern data |
| `webinterface_checker.py` | "Does WebInterface have this method?" | Boolean + method info |

### No-Fix Handling

When `fix_suggester.py` returns `None` (no known fix):
- **AI Orchestration** (not code) handles this case
- AI stops, reports to user: "No known fix. What should we try?"
- If user provides fix, AI saves pattern to KB via `knowledge_base.py` (FR-59)
- This aligns with DD-22 (Stop-and-Discuss Protocol)

### Dependency Flow

```
runtime_validator.py → returns error_category
         ↓
fix_suggester.py → queries knowledge_base.py → returns Optional[fix]
         ↓
   ┌─────┴─────┐
   │           │
 Some fix    None (no fix)
   │           │
   ↓           ↓
Propose to   STOP, ask user
user         (AI orchestration)
```

---

## Existing Codebase Assessment

### Files That EXIST (Extend/Modify)

| File | Current State | Action Required |
|------|---------------|-----------------|
| `mcp_server/utils/audit_logger.py` | Full audit logging with log_gate(), log_self_heal(), incremental persist | **EXTEND** - Add log_runtime_validation(), log_fix_attempt() |
| `mcp_server/utils/state_manager.py` | Step data persistence, attempt tracking, execution mode | **EXTEND** - Add checkpoint resume logic |
| `mcp_server/utils/element_discovery.py` | Selenium-based element discovery | **KEEP** - Runtime validation uses Playwright (separate concern) |
| `mcp_server/tools/gates/base_gate.py` | pass_response(), fail_response(), blocked_response(), skeleton detection | **KEEP** - No changes needed |
| `mcp_server/tools/gates/qg_discovered_elements.py` | Step 5 gate | **EXTEND** - Add scope discovery validation |
| `mcp_server/tools/gates/qg_page_object.py` | Step 6 gate | **EXTEND** - Add runtime validation call |
| `mcp_server/tools/gates/qg_task.py` | Step 7 gate | **EXTEND** - Add runtime validation call |
| `mcp_server/tools/gates/qg_role.py` | Step 8 gate | **EXTEND** - Add runtime validation call |
| `mcp_server/tools/gates/qg_test_runner.py` | Step 9 gate | **EXTEND** - Add runtime validation call |
| `mcp_server/tools/gates/qg_save_run.py` | Step 10 gate | **EXTEND** - Make final validation mandatory |
| `framework/interfaces/web_interface.py` | Full WebInterface class | **REFERENCE ONLY** - Used for method existence check |
| `docs/KNOWLEDGE_BASE.md` | Patterns for workflow discovery | **EXTEND** - Add runtime validation patterns section |

### Files To CREATE (New)

| File | Responsibility |
|------|----------------|
| `mcp_server/utils/scope_discovery.py` | Analyze workflow scope (page count) |
| `mcp_server/utils/runtime_validator.py` | Validate elements, return error category |
| `mcp_server/utils/fix_suggester.py` | Suggest fixes based on error category |
| `mcp_server/utils/knowledge_base.py` | Read/write patterns to KNOWLEDGE_BASE.md |
| `mcp_server/utils/webinterface_checker.py` | Check WebInterface method existence |

### Test Files To CREATE

| File | Tests For |
|------|-----------|
| `mcp_server/_dev_tests/test_scope_discovery.py` | scope_discovery.py |
| `mcp_server/_dev_tests/test_runtime_validator.py` | runtime_validator.py |
| `mcp_server/_dev_tests/test_fix_suggester.py` | fix_suggester.py |
| `mcp_server/_dev_tests/test_knowledge_base.py` | knowledge_base.py |
| `mcp_server/_dev_tests/test_webinterface_checker.py` | webinterface_checker.py |
| `mcp_server/_dev_tests/test_enhanced_gates.py` | Gate integration tests |

---

## Tasks

### Phase 1: Scope Discovery Infrastructure

- [x] 1.0 Implement Scope Discovery (Step 5a) [CORE]
  - [x] 1.1 Create branch `feature/1.0-scope-discovery`
  - [x] 1.2 **ASSESS:** Read `mcp_server/utils/element_discovery.py` for existing patterns
  - [x] 1.3 **ASSESS:** Read `mcp_server/tools/gates/qg_discovered_elements.py` for Step 5 gate
  - [x] 1.4 **CREATE:** `mcp_server/utils/scope_discovery.py` with:
    - `ScopeDiscovery` class
    - `analyze_workflow(bdd_scenarios: list) -> ScopeResult` - Analyze BDD scenarios for page count (fallback)
    - `register_page(url) -> PageInfo` - Register page via URL (primary method)
    - `is_new_page(current_url, previous_url) -> bool` - Detect page change via URL comparison
    - `get_scope_result() -> ScopeResult` - Get final scope from navigation tracking
    - `create_navigation_tracker()` - Convenience function
  - [x] 1.5 **CREATE:** Unit tests `mcp_server/_dev_tests/test_scope_discovery.py`
  - [x] 1.6 Run checks (lint, type, tests) following testing skill
  - [x] 1.7 **Audit:** Verify testing skill conventions followed
  - [x] 1.8 Record results in this file
  - [x] 1.9 Commit: `feat: add scope discovery for two-pass element discovery (Task 1.0)`
  - [x] 1.10 **UPDATE (2025-12-31):** Replaced pattern-matching with URL-based detection per PRD FR-04

**Done When:**
- [x] ScopeDiscovery class detects single vs multi-page workflows
- [x] Unit tests pass with happy path, edge cases
- [x] Testing skill failure protocol followed if any failures
- [x] **URL-based detection works universally** (validated on SauceDemo)

**Results (2025-12-30):**
```bash
pytest mcp_server/_dev_tests/test_scope_discovery.py -v
# 14 passed, 14 warnings (custom marks) in 0.10s
```

**Results (2025-12-31 - URL-based update):**
```bash
# Tested on SauceDemo checkout flow - 5 pages detected via URL changes
# /inventory.html -> InventoryPage
# /cart.html -> CartPage
# /checkout-step-one.html -> CheckoutStepOnePage
# /checkout-step-two.html -> CheckoutStepTwoPage
# /checkout-complete.html -> CheckoutCompletePage
```

---

### Phase 2: Per-Page Element Discovery

- [x] 2.0 Extend Step 5 Gate for Per-Page Discovery [CORE]
  - [x] 2.1 Create branch `feature/2.0-per-page-discovery`
  - [x] 2.2 **ASSESS:** Read current `qg_discovered_elements.py` implementation
  - [x] 2.3 **EXTEND:** `mcp_server/tools/gates/qg_discovered_elements.py`:
    - Add PRE mode check for scope_result validation (page_name in scope)
    - Add per-page element tracking in POST mode (discovered_pages dict)
    - Add discovery progress tracking (pages_discovered, total_pages, discovery_complete)
    - Add helper methods: get_discovery_progress(), is_discovery_complete()
  - [x] 2.4 **EXTEND:** Unit tests `mcp_server/_dev_tests/test_qg_discovered_elements.py`
  - [x] 2.5 Run checks following testing skill
  - [x] 2.6 **Audit:** Verify testing skill conventions followed
  - [x] 2.7 Record results
  - [x] 2.8 Commit: `feat: extend Step 5 gate for per-page element discovery (Task 2.0)`

**Done When:**
- [x] Gate validates scope discovery (if provided) before element discovery
- [x] Per-page elements tracked separately in discovered_pages
- [x] Discovery progress tracked (pages_discovered/total_pages)
- [x] Tests pass

**Results (2025-12-30):**
```bash
pytest mcp_server/_dev_tests/test_qg_discovered_elements.py -v
# 25 passed, 36 warnings (custom marks) in 0.34s

pytest mcp_server/_dev_tests/test_scope_discovery.py -v
# 14 passed, 14 warnings (custom marks) in 0.09s
```

---

### Phase 3: Runtime Validator (Validation + Categorization)

- [x] 3.0 Implement Runtime Validator [CORE]
  - [x] 3.1 Create branch `feature/3.0-runtime-validator`
  - [x] 3.2 **ASSESS:** Read Playwright MCP tools available (browser_snapshot, browser_click, etc.)
  - [x] 3.3 **CREATE:** `mcp_server/utils/runtime_validator.py` with:
    - `RuntimeValidator` class
    - `validate_element(locator: str) -> ValidationResult` - Check element usability
    - `ValidationResult` dataclass with:
      - `is_valid: bool`
      - `error_category: Optional[str]` - LOCATOR_NOT_FOUND, NOT_VISIBLE, NOT_INTERACTABLE, STALE_REFERENCE, METHOD_NOT_FOUND
      - `details: dict` - Additional context
    - **NO fix suggestion logic** - that's fix_suggester's job
  - [x] 3.4 **CREATE:** Unit tests `mcp_server/_dev_tests/test_runtime_validator.py`
  - [x] 3.5 Run checks following testing skill
  - [x] 3.6 **Audit:** Verify testing skill conventions followed
  - [x] 3.7 Record results
  - [x] 3.8 Commit: `feat: add runtime validator with error categorization (Task 3.0)`

**Done When:**
- [x] RuntimeValidator validates elements exist, visible, interactable
- [x] Returns error category (not fix suggestion)
- [x] Tests cover all error categories
- [x] Tests pass

**Results (2025-12-30):**
```bash
pytest mcp_server/_dev_tests/test_runtime_validator.py -v
# 23 passed, 23 warnings (custom marks) in 0.10s

# Regression check
pytest mcp_server/_dev_tests/test_scope_discovery.py mcp_server/_dev_tests/test_qg_discovered_elements.py -v
# 39 passed, 50 warnings in 0.28s
```

---

### Phase 4: Knowledge Base Module

- [x] 4.0 Implement Knowledge Base Read/Write [CORE]
  - [x] 4.1 Create branch `feature/4.0-knowledge-base`
  - [x] 4.2 **ASSESS:** Read current `docs/KNOWLEDGE_BASE.md` structure
  - [x] 4.3 **CREATE:** `mcp_server/utils/knowledge_base.py` with:
    - `KnowledgeBase` class
    - `find_pattern(error_category: str, context: dict) -> Optional[Pattern]` - Find matching pattern
    - `save_pattern(pattern: Pattern) -> None` - Save new pattern to KB
    - `Pattern` dataclass with:
      - `error_category: str`
      - `context_match: dict` - What context this applies to
      - `fix: str` - The fix to apply
      - `confidence: float` - How confident (0-1)
  - [x] 4.4 **CREATE:** Unit tests `mcp_server/_dev_tests/test_knowledge_base.py`
  - [x] 4.5 Run checks following testing skill
  - [x] 4.6 **Audit:** Verify testing skill conventions followed
  - [x] 4.7 Record results
  - [x] 4.8 Commit: `feat: add knowledge base read/write module (Task 4.0)`

**Done When:**
- [x] KnowledgeBase can read patterns from KNOWLEDGE_BASE.md
- [x] KnowledgeBase can write new patterns
- [x] Tests cover find (exists/not exists) and save
- [x] Tests pass

**Results (2025-12-30):**
```bash
pytest mcp_server/_dev_tests/test_knowledge_base.py -v
# 20 passed, 20 warnings (custom marks) in 0.15s

# Regression check
pytest mcp_server/_dev_tests/test_runtime_validator.py mcp_server/_dev_tests/test_scope_discovery.py mcp_server/_dev_tests/test_qg_discovered_elements.py -v
# 62 passed, 73 warnings in 0.37s
```

---

### Phase 5: Fix Suggester

- [x] 5.0 Implement Fix Suggester [CORE]
  - [x] 5.1 Create branch `feature/5.0-fix-suggester`
  - [x] 5.2 **ASSESS:** Read runtime_validator.py for error categories
  - [x] 5.3 **ASSESS:** Read knowledge_base.py for pattern interface
  - [x] 5.4 **CREATE:** `mcp_server/utils/fix_suggester.py` with:
    - `FixSuggester` class
    - `__init__(self, kb: KnowledgeBase)` - Inject KB dependency
    - `suggest_fix(error_category: str, context: dict) -> Optional[FixRecommendation]`
      - Returns `FixRecommendation` if pattern found
      - Returns `None` if no known fix (caller handles this)
    - `FixRecommendation` dataclass with:
      - `fix_action: str` - What to do
      - `fix_details: dict` - Parameters/specifics
      - `confidence: float` - From KB pattern
  - [x] 5.5 **CREATE:** Unit tests `mcp_server/_dev_tests/test_fix_suggester.py`
    - Test: Known pattern returns recommendation
    - Test: Unknown pattern returns None
    - Test: Correct KB integration
  - [x] 5.6 Run checks following testing skill
  - [x] 5.7 **Audit:** Verify testing skill conventions followed
  - [x] 5.8 Record results
  - [x] 5.9 Commit: `feat: add fix suggester with KB integration (Task 5.0)`

**Done When:**
- [x] FixSuggester returns Optional[FixRecommendation]
- [x] Returns None when no pattern (not fallback - caller decides)
- [x] Properly queries KnowledgeBase
- [x] Tests pass

**Results (2025-12-31):**
```bash
pytest mcp_server/_dev_tests/test_fix_suggester.py -v
# 28 passed, 28 warnings (custom marks) in 0.16s

# Regression check
pytest mcp_server/_dev_tests/test_knowledge_base.py mcp_server/_dev_tests/test_runtime_validator.py mcp_server/_dev_tests/test_scope_discovery.py mcp_server/_dev_tests/test_qg_discovered_elements.py -v
# 82 passed, 93 warnings in 0.37s
```

---

### Phase 6: Visual Feedback During Validation

- [x] 6.0 Implement Visual Feedback Module [GLUE]
  - [x] 6.1 Create branch `feature/6.0-visual-feedback`
  - [x] 6.2 **ASSESS:** Read RuntimeValidator for integration points
  - [x] 6.3 **ASSESS:** Read Playwright MCP browser_evaluate capabilities
  - [x] 6.4 **CREATE:** `mcp_server/utils/visual_feedback.py` with:
    - `VisualFeedback` class
    - `highlight_element(ref: str, status: str) -> None` - Inject CSS for element
    - `highlight_valid(ref: str) -> None` - Green outline for valid elements
    - `highlight_invalid(ref: str, error_category: str) -> None` - Red outline for errors
    - `show_pipeline_header(scope_result, validation_results, kb_status) -> None` - Display 3-step pipeline:
      ```
      RUNTIME VALIDATION PIPELINE - LIVE DEMO
      Step 1: ScopeDiscovery ......... [OK] Single Page (LoginPage)
      Step 2: RuntimeValidator ....... [OK] 4 Valid, 0 Errors
      Step 3: KnowledgeBase .......... [OK] Patterns Ready
      ```
    - `update_step_status(step: int, status: str, details: str) -> None` - Update individual step
    - `show_results_panel(results: List[ValidationResult]) -> None` - Show element-by-element results
    - `cleanup() -> None` - Remove injected elements (optional)
    - CSS classes: `.qa-validation-ok`, `.qa-validation-fail`, `.qa-pipeline-header`, `.qa-pipeline-step`, `.qa-results-panel`
  - [x] 6.5 **CREATE:** Unit tests `mcp_server/_dev_tests/test_visual_feedback.py`
    - Test: highlight_valid injects correct CSS class
    - Test: highlight_invalid injects correct CSS class with label
    - Test: show_pipeline_header displays 3-step status
    - Test: update_step_status updates individual step
    - Test: show_results_panel displays element list
    - Test: cleanup removes injected elements
    - Test: headless mode skips visual injection
  - [x] 6.6 **INTEGRATE:** Add visual feedback calls to RuntimeValidator (via constructor injection)
  - [x] 6.7 Run checks following testing skill
  - [x] 6.8 **Audit:** Verify testing skill conventions followed
  - [x] 6.9 Record results
  - [x] 6.10 Commit: `feat: add visual feedback during validation (Task 6.0)`

**Done When:**
- [x] Valid elements highlighted with green outline
- [x] Invalid elements highlighted with red outline + error label
- [x] 3-step pipeline header displays:
  - Step 1: ScopeDiscovery status (Single/Multi Page + page names)
  - Step 2: RuntimeValidator status (X Valid, Y Errors)
  - Step 3: KnowledgeBase status (Patterns Ready/Loading)
- [x] Results panel displays element-by-element validation
- [x] Headless mode gracefully skips visuals
- [x] Tests pass

**Results (2025-12-31):**
```bash
pytest mcp_server/_dev_tests/test_visual_feedback.py -v
# 47 passed, 47 warnings (custom marks) in 0.14s

# Regression check (Tasks 1-5)
pytest mcp_server/_dev_tests/test_fix_suggester.py mcp_server/_dev_tests/test_knowledge_base.py mcp_server/_dev_tests/test_runtime_validator.py mcp_server/_dev_tests/test_scope_discovery.py -v
# 85 passed, 85 warnings in 0.22s
```

**CSS Classes:**
```css
.validation-ok {
    outline: 3px solid #00ff00 !important;
    outline-offset: 2px;
}
.validation-fail {
    outline: 3px solid #ff0000 !important;
    outline-offset: 2px;
}
.pipeline-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #1a1a2e;
    color: #00ff00;
    padding: 10px;
    z-index: 99999;
    font-family: monospace;
}
.results-panel {
    position: fixed;
    top: 60px;
    right: 10px;
    background: rgba(0, 0, 0, 0.9);
    color: #fff;
    padding: 15px;
    border-radius: 5px;
    z-index: 99998;
    font-family: monospace;
}
```

---

### Phase 7: WebInterface Checker

- [x] 7.0 Implement WebInterface Checker [CORE]
  - [x] 7.1 Create branch `feature/7.0-webinterface-checker`
  - [x] 7.2 **ASSESS:** Read `framework/interfaces/web_interface.py` to understand structure
  - [x] 7.3 **CREATE:** `mcp_server/utils/webinterface_checker.py` with:
    - `WebInterfaceChecker` class
    - `get_available_methods() -> List[MethodInfo]` - Parse WebInterface for public methods
    - `method_exists(method_name: str) -> bool` - Check if method exists
    - `get_method_signature(method_name: str) -> Optional[MethodSignature]` - Get parameters
  - [x] 7.4 **CREATE:** Unit tests `mcp_server/_dev_tests/test_webinterface_checker.py`
  - [x] 7.5 Run checks following testing skill
  - [x] 7.6 **Audit:** Verify testing skill conventions followed
  - [x] 7.7 Record results
  - [x] 7.8 Commit: `feat: add WebInterface method checker (Task 7.0)`

**Done When:**
- [x] WebInterfaceChecker parses WebInterface class
- [x] method_exists() works correctly
- [x] Tests cover existing and non-existing methods
- [x] Tests pass

**Results (2025-12-31):**
```bash
pytest mcp_server/_dev_tests/test_webinterface_checker.py -v
# 49 passed in 0.15s
```

---

### Phase 8: POM Runtime Validation (Step 6)

- [x] 8.0 Extend Step 6 Gate with Runtime Validation [CORE]
  - [x] 8.1 Create branch `feature/8.0-gate-extensions`
  - [x] 8.2 **ASSESS:** Read current `qg_page_object.py` implementation
  - [x] 8.3 **EXTEND:** `mcp_server/tools/gates/qg_page_object.py`:
    - Import WebInterfaceChecker
    - Add `_validate_webinterface_methods()` in POST mode
    - Regex pattern extracts `self.web.<method>()` calls
    - Validates each method exists via WebInterfaceChecker
    - Reports invalid methods with suggestions for typos
  - [x] 8.4 **EXTEND:** Gate tests for new validation (8 new tests)
  - [x] 8.5 Run checks following testing skill
  - [x] 8.6 **Audit:** Verify testing skill conventions followed
  - [x] 8.7 Record results
  - [x] 8.8 Commit: `feat: integrate WebInterfaceChecker into qg_page_object (Task 8.0)`

**Done When:**
- [x] POM WebInterface method calls validated
- [x] WebInterface method existence verified
- [x] Gate returns error with suggestions for typos
- [x] Tests pass

**Results (2025-12-31):**
```bash
pytest mcp_server/_dev_tests/test_gates/test_qg_page_object.py -v
# 47 passed in 0.25s

pytest mcp_server/_dev_tests/test_gates/ -v
# 402 passed in 1.5s
```

---

### Phase 8.5: Multi-Page Workflow Support (DD-44)

**Context:** DEF-044 discovered that multi-page BDD workflows (e.g., 4-step wizard) need enforcement across ALL code generation steps, not just Steps 5-6.

**Multi-Page Data Flow:**
```
Step 5: Discover elements for ALL pages (loop)
    ↓ discovered_pages: {Page1: [...], Page2: [...], Page3: [...], Page4: [...]}
Step 6: Generate POMs for ALL pages (loop)
    ↓ pom_metadata: {Page1: {class, import, methods}, Page2: {...}, ...}
Step 7: Task must compose ALL POMs from scope
    ↓ task_metadata: {pom_dependencies: [Page1, Page2, Page3, Page4]}
Step 8: Role uses Task (single)
    ↓ role_metadata: {task_dependency: TaskClass}
Step 9: Test needs ALL POMs for assertions
    ↓ test assertions use POM state methods from all pages
```

- [x] 8.5.0 Multi-Page Scope Detection (Step 5) - DONE
  - [x] 8.5.1 Auto-detect page count from BDD via _detect_page_count_from_bdd()
  - [x] 8.5.2 Require scope_result when page_count > 1 (DD-44 enforcement)
  - [x] 8.5.3 Return multi_page_progress with hint for incomplete discovery
  - [x] 8.5.4 Add 8 unit tests for DD-44 detection
  - [x] 8.5.5 Update step-05.md with Multi-Page Discovery section

- [x] 8.5.6 Multi-Page Discovery Blocking (Step 6 PRE) - DONE
  - [x] 8.5.7 Block Step 6 PRE if discovery_complete is False
  - [x] 8.5.8 Add DD-44 to qg_page_object.py docstring

- [x] 8.5.9 Multi-Page POM Generation Loop (Step 6) [CORE] ✅ COMPLETE
  - [x] 8.5.10 Update step-06.md with multi-page POM generation loop
  - [x] 8.5.11 Add generated_poms dict for per-page tracking
  - [x] 8.5.12 Track pom_generation_progress (poms_generated, total_poms, generation_complete)
  - [x] 8.5.13 Add 11 tests for multi-page POM tracking

**DC-01: Multi-Page Loop Scope Clarification (2025-12-31)**

Multi-page loop tracking ONLY applies to Step 6 (POM generation):

| Step | Layer | Loop? | Rationale |
|------|-------|-------|-----------|
| Step 6 | POMs | YES | One POM per page (1:1 mapping) |
| Step 7 | Tasks | NO | Tasks are per-domain, not per-page |
| Step 8 | Roles | NO | One Role per persona |
| Step 9 | Tests | NO | One test per scenario |

The following tasks were scoped out per DC-01:
- ~~8.5.14-8.5.18 Multi-Page Task Composition~~ - NOT APPLICABLE (Tasks are per-domain)
- ~~8.5.19-8.5.22 Multi-Page Test Assertions~~ - NOT APPLICABLE (Tests are per-scenario)

- [ ] 8.5.14 Production Validation [GLUE]
  - [ ] 8.5.15 Re-run SauceDemo checkout workflow with multi-page POM generation
  - [ ] 8.5.16 Verify all pages discovered → all POMs generated
  - [ ] 8.5.17 Mark DEF-044 as RESOLVED after successful production test

**Done When:**
- Multi-page BDD workflows enforce scope discovery at Step 5 ✅
- Step 6 generates POMs for ALL pages in scope ✅
- Step 6 tracks generation progress with completion flag ✅
- Production validation passes
- DEF-044 marked RESOLVED

**Current Status:**
- 8.5.0-8.5.8: COMPLETE (Steps 5-6 enforcement)
- 8.5.9-8.5.13: COMPLETE (Multi-page POM generation loop)
- 8.5.14-8.5.17: PENDING (Production validation)

---

### Phase 9: Task Runtime Validation (Step 7)

- [ ] 9.0 Extend Step 7 Gate with Runtime Validation [CORE]
  - [ ] 9.1 Create branch `feature/9.0-task-runtime-validation`
  - [ ] 9.2 **ASSESS:** Read current `qg_task.py` implementation
  - [ ] 9.3 **EXTEND:** `mcp_server/tools/gates/qg_task.py`:
    - Add runtime validation for POM method calls
    - Validate workflow sequence feasibility
  - [ ] 9.4 **EXTEND:** Gate tests for new validation
  - [ ] 9.5 Run checks following testing skill
  - [ ] 9.6 **Audit:** Verify testing skill conventions followed
  - [ ] 9.7 Record results
  - [ ] 9.8 Commit: `feat: add runtime validation to Step 7 gate (Task 9.0)`

**Done When:**
- Task POM method calls validated
- Workflow sequence feasibility checked
- Tests pass

---

### Phase 10: Role Runtime Validation (Step 8)

- [ ] 10.0 Extend Step 8 Gate with Runtime Validation [CORE]
  - [ ] 10.1 Create branch `feature/10.0-role-runtime-validation`
  - [ ] 10.2 **ASSESS:** Read current `qg_role.py` implementation
  - [ ] 10.3 **EXTEND:** `mcp_server/tools/gates/qg_role.py`:
    - Add runtime validation for Task method calls
    - Validate complete workflow feasibility
  - [ ] 10.4 **EXTEND:** Gate tests for new validation
  - [ ] 10.5 Run checks following testing skill
  - [ ] 10.6 **Audit:** Verify testing skill conventions followed
  - [ ] 10.7 Record results
  - [ ] 10.8 Commit: `feat: add runtime validation to Step 8 gate (Task 10.0)`

**Done When:**
- Role Task method calls validated
- Complete workflow feasibility checked
- Tests pass

---

### Phase 11: Test Runtime Validation (Step 9)

- [ ] 11.0 Extend Step 9 Gate with Runtime Validation [CORE]
  - [ ] 11.1 Create branch `feature/11.0-test-runtime-validation`
  - [ ] 11.2 **ASSESS:** Read current `qg_test_runner.py` implementation
  - [ ] 11.3 **EXTEND:** `mcp_server/tools/gates/qg_test_runner.py`:
    - Add full workflow simulation
    - Validate all assertions reachable
  - [ ] 11.4 **EXTEND:** Gate tests for new validation
  - [ ] 11.5 Run checks following testing skill
  - [ ] 11.6 **Audit:** Verify testing skill conventions followed
  - [ ] 11.7 Record results
  - [ ] 11.8 Commit: `feat: add runtime validation to Step 9 gate (Task 11.0)`

**Done When:**
- Full workflow simulation works
- Assertion reachability validated
- Tests pass

---

### Phase 12: Mandatory Final Gate (Step 10)

- [ ] 12.0 Enforce Mandatory Final Validation [CORE]
  - [ ] 12.1 Create branch `feature/12.0-mandatory-final-gate`
  - [ ] 12.2 **ASSESS:** Read current `qg_save_run.py` implementation
  - [ ] 12.3 **EXTEND:** `mcp_server/tools/gates/qg_save_run.py`:
    - Make final gate mandatory (cannot be bypassed)
    - Aggregate all previous validations
    - Require all steps complete before save
  - [ ] 12.4 **EXTEND:** Gate tests for mandatory enforcement
  - [ ] 12.5 Run checks following testing skill
  - [ ] 12.6 **Audit:** Verify testing skill conventions followed
  - [ ] 12.7 Record results
  - [ ] 12.8 Commit: `feat: make Step 10 final gate mandatory (Task 12.0)`

**Done When:**
- Final gate cannot be bypassed
- All previous step validations aggregated
- Tests pass

---

### Phase 13: Audit Trail Enhancement

- [ ] 13.0 Extend Audit Logger for Runtime Validation [GLUE]
  - [ ] 13.1 Create branch `feature/13.0-audit-enhancement`
  - [ ] 13.2 **ASSESS:** Read current `mcp_server/utils/audit_logger.py` implementation
  - [ ] 13.3 **EXTEND:** `mcp_server/utils/audit_logger.py`:
    - Add `log_runtime_validation(element, result, category)` method
    - Add `log_fix_attempt(element, fix, outcome)` method
    - Preserve existing functionality
  - [ ] 13.4 **EXTEND:** Unit tests for new logging methods
  - [ ] 13.5 Run checks following testing skill
  - [ ] 13.6 **Audit:** Verify testing skill conventions followed
  - [ ] 13.7 Record results
  - [ ] 13.8 Commit: `feat: extend audit logger for runtime validation (Task 13.0)`

**Done When:**
- Runtime validation logged with categories
- Fix attempts logged
- Existing functionality preserved
- Tests pass

---

### Phase 14: Knowledge Base Patterns

- [ ] 14.0 Extend Knowledge Base with Runtime Patterns [GLUE]
  - [ ] 14.1 Create branch `feature/14.0-kb-patterns`
  - [ ] 14.2 **EXTEND:** `docs/KNOWLEDGE_BASE.md`:
    - Add "Runtime Validation Patterns" section
    - Add initial error category → fix mappings:
      - LOCATOR_NOT_FOUND → check selector, try different strategy
      - NOT_VISIBLE → add wait, scroll into view
      - NOT_INTERACTABLE → use click_js
      - STALE_REFERENCE → re-find element
      - METHOD_NOT_FOUND → check WebInterface, propose addition
  - [ ] 14.3 Verify knowledge_base.py can parse new section
  - [ ] 14.4 **Audit:** Verify documentation quality
  - [ ] 14.5 Record results
  - [ ] 14.6 Commit: `feat: add runtime validation patterns to KB (Task 14.0)`

**Done When:**
- KB has runtime validation patterns section
- Error → fix mappings documented
- knowledge_base.py can read patterns
- Patterns are actionable

---

### Phase 15: Re-Validation Triggers

- [ ] 15.0 Implement Re-Validation on User Changes [GLUE]
  - [ ] 15.1 Create branch `feature/15.0-revalidation-triggers`
  - [ ] 15.2 **ASSESS:** Read existing gate implementations for trigger points
  - [ ] 15.3 **EXTEND:** Base gate or individual gates:
    - Add change detection logic
    - Add re-validation trigger on user modification
    - Add cascade re-validation for downstream steps
  - [ ] 15.4 **EXTEND:** Tests for re-validation triggers
  - [ ] 15.5 Run checks following testing skill
  - [ ] 15.6 **Audit:** Verify testing skill conventions followed
  - [ ] 15.7 Record results
  - [ ] 15.8 Commit: `feat: add re-validation triggers on user changes (Task 15.0)`

**Done When:**
- User changes trigger re-validation
- Downstream steps cascade correctly
- Tests pass

---

### Phase 16: Checkpoint Resume

- [ ] 16.0 Extend State Manager for Checkpoint Resume [GLUE]
  - [ ] 16.1 Create branch `feature/16.0-checkpoint-resume`
  - [ ] 16.2 **ASSESS:** Read current `mcp_server/utils/state_manager.py` implementation
  - [ ] 16.3 **EXTEND:** `mcp_server/utils/state_manager.py`:
    - Add `save_checkpoint(step, data)` method
    - Add `restore_checkpoint(step)` method
    - Add `list_checkpoints()` method
    - Add `get_resume_step()` method
  - [ ] 16.4 **EXTEND:** Unit tests for checkpoint functionality
  - [ ] 16.5 Run checks following testing skill
  - [ ] 16.6 **Audit:** Verify testing skill conventions followed
  - [ ] 16.7 Record results
  - [ ] 16.8 Commit: `feat: add checkpoint resume to state manager (Task 16.0)`

**Done When:**
- Checkpoints can be saved and restored
- Resume from last successful step works
- Tests pass

---

## Relevant Files Summary

### Files To CREATE (SRP-Compliant)

| File | Single Responsibility |
|------|----------------------|
| `mcp_server/utils/scope_discovery.py` | Track pages via URL changes during navigation |
| `mcp_server/utils/runtime_validator.py` | Validate elements, return error category |
| `mcp_server/utils/fix_suggester.py` | Suggest fixes (returns None if unknown) |
| `mcp_server/utils/knowledge_base.py` | Read/write KB patterns |
| `mcp_server/utils/webinterface_checker.py` | Check WebInterface methods |
| `mcp_server/utils/visual_feedback.py` | Inject visual highlighting during validation |

### Test Files To CREATE

| File | Tests For |
|------|-----------|
| `mcp_server/_dev_tests/test_scope_discovery.py` | scope_discovery.py |
| `mcp_server/_dev_tests/test_runtime_validator.py` | runtime_validator.py |
| `mcp_server/_dev_tests/test_fix_suggester.py` | fix_suggester.py |
| `mcp_server/_dev_tests/test_knowledge_base.py` | knowledge_base.py |
| `mcp_server/_dev_tests/test_webinterface_checker.py` | webinterface_checker.py |
| `mcp_server/_dev_tests/test_visual_feedback.py` | visual_feedback.py |
| `mcp_server/_dev_tests/test_enhanced_gates.py` | Gate integration |

### Files To EXTEND

| File | Extension |
|------|-----------|
| `mcp_server/utils/audit_logger.py` | log_runtime_validation(), log_fix_attempt() |
| `mcp_server/utils/state_manager.py` | Checkpoint resume methods |
| `mcp_server/tools/gates/qg_discovered_elements.py` | Scope discovery validation |
| `mcp_server/tools/gates/qg_page_object.py` | Runtime validation call |
| `mcp_server/tools/gates/qg_task.py` | Runtime validation call |
| `mcp_server/tools/gates/qg_role.py` | Runtime validation call |
| `mcp_server/tools/gates/qg_test_runner.py` | Runtime validation call |
| `mcp_server/tools/gates/qg_save_run.py` | Mandatory enforcement |
| `docs/KNOWLEDGE_BASE.md` | Runtime validation patterns |

### Files To REFERENCE (Read-Only)

| File | Used For |
|------|----------|
| `framework/interfaces/web_interface.py` | Method existence checking |
| `mcp_server/tools/gates/base_gate.py` | Shared utilities |

---

## Notes

### SRP Enforcement
- Each new module has ONE responsibility
- fix_suggester returns None, not fallback (caller decides)
- Gates call validators but don't implement fix loops
- AI orchestration handles "no fix" case (not code)

### Testing Protocol
- Each phase follows testing skill
- Happy path + negative + edge cases
- Failure protocol: STOP → REPORT → DISCUSS → FIX → RE-TEST

### Feature Branch Workflow
- One branch per parent task
- Commit after all subtasks complete
- Merge to main after tests pass

---

**Last Updated:** 2025-12-31
**Version:** 1.5 (Tasks 1-8 complete, URL-based scope discovery implemented)
