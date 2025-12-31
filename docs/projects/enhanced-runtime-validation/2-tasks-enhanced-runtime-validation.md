# Task List: Enhanced Runtime Validation Gates

**PRD:** `1-prd-enhanced-runtime-validation.md`
**Generated:** 2025-12-30
**Version:** 1.1 (SRP-compliant design)

---

## Design Principles

### Single Responsibility Principle (SRP)

Each module has ONE responsibility:

| Module | Single Responsibility | Returns |
|--------|----------------------|---------|
| `scope_discovery.py` | "How many pages in this workflow?" | Scope analysis result |
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
    - `analyze_workflow(bdd_scenarios: list) -> ScopeResult` - Analyze BDD scenarios for page count
    - `get_page_list() -> List[PageInfo]` - Return list of page identifiers
    - `is_single_page() -> bool` - Convenience check
    - `is_multi_page() -> bool` - Convenience check
  - [x] 1.5 **CREATE:** Unit tests `mcp_server/_dev_tests/test_scope_discovery.py`
  - [x] 1.6 Run checks (lint, type, tests) following testing skill
  - [x] 1.7 **Audit:** Verify testing skill conventions followed
  - [x] 1.8 Record results in this file
  - [x] 1.9 Commit: `feat: add scope discovery for two-pass element discovery (Task 1.0)`

**Done When:**
- [x] ScopeDiscovery class detects single vs multi-page workflows
- [x] Unit tests pass with happy path, edge cases
- [x] Testing skill failure protocol followed if any failures

**Results (2025-12-30):**
```bash
pytest mcp_server/_dev_tests/test_scope_discovery.py -v
# 14 passed, 14 warnings (custom marks) in 0.10s
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

- [ ] 3.0 Implement Runtime Validator [CORE]
  - [ ] 3.1 Create branch `feature/3.0-runtime-validator`
  - [ ] 3.2 **ASSESS:** Read Playwright MCP tools available (browser_snapshot, browser_click, etc.)
  - [ ] 3.3 **CREATE:** `mcp_server/utils/runtime_validator.py` with:
    - `RuntimeValidator` class
    - `validate_element(locator: str) -> ValidationResult` - Check element usability
    - `ValidationResult` dataclass with:
      - `is_valid: bool`
      - `error_category: Optional[str]` - LOCATOR_NOT_FOUND, NOT_VISIBLE, NOT_INTERACTABLE, STALE_REFERENCE, METHOD_NOT_FOUND
      - `details: dict` - Additional context
    - **NO fix suggestion logic** - that's fix_suggester's job
  - [ ] 3.4 **CREATE:** Unit tests `mcp_server/_dev_tests/test_runtime_validator.py`
  - [ ] 3.5 Run checks following testing skill
  - [ ] 3.6 **Audit:** Verify testing skill conventions followed
  - [ ] 3.7 Record results
  - [ ] 3.8 Commit: `feat: add runtime validator with error categorization (Task 3.0)`

**Done When:**
- RuntimeValidator validates elements exist, visible, interactable
- Returns error category (not fix suggestion)
- Tests cover all error categories
- Tests pass

---

### Phase 4: Knowledge Base Module

- [ ] 4.0 Implement Knowledge Base Read/Write [CORE]
  - [ ] 4.1 Create branch `feature/4.0-knowledge-base`
  - [ ] 4.2 **ASSESS:** Read current `docs/KNOWLEDGE_BASE.md` structure
  - [ ] 4.3 **CREATE:** `mcp_server/utils/knowledge_base.py` with:
    - `KnowledgeBase` class
    - `find_pattern(error_category: str, context: dict) -> Optional[Pattern]` - Find matching pattern
    - `save_pattern(pattern: Pattern) -> None` - Save new pattern to KB
    - `Pattern` dataclass with:
      - `error_category: str`
      - `context_match: dict` - What context this applies to
      - `fix: str` - The fix to apply
      - `confidence: float` - How confident (0-1)
  - [ ] 4.4 **CREATE:** Unit tests `mcp_server/_dev_tests/test_knowledge_base.py`
  - [ ] 4.5 Run checks following testing skill
  - [ ] 4.6 **Audit:** Verify testing skill conventions followed
  - [ ] 4.7 Record results
  - [ ] 4.8 Commit: `feat: add knowledge base read/write module (Task 4.0)`

**Done When:**
- KnowledgeBase can read patterns from KNOWLEDGE_BASE.md
- KnowledgeBase can write new patterns
- Tests cover find (exists/not exists) and save
- Tests pass

---

### Phase 5: Fix Suggester

- [ ] 5.0 Implement Fix Suggester [CORE]
  - [ ] 5.1 Create branch `feature/5.0-fix-suggester`
  - [ ] 5.2 **ASSESS:** Read runtime_validator.py for error categories
  - [ ] 5.3 **ASSESS:** Read knowledge_base.py for pattern interface
  - [ ] 5.4 **CREATE:** `mcp_server/utils/fix_suggester.py` with:
    - `FixSuggester` class
    - `__init__(self, kb: KnowledgeBase)` - Inject KB dependency
    - `suggest_fix(error_category: str, context: dict) -> Optional[FixRecommendation]`
      - Returns `FixRecommendation` if pattern found
      - Returns `None` if no known fix (caller handles this)
    - `FixRecommendation` dataclass with:
      - `fix_action: str` - What to do
      - `fix_details: dict` - Parameters/specifics
      - `confidence: float` - From KB pattern
  - [ ] 5.5 **CREATE:** Unit tests `mcp_server/_dev_tests/test_fix_suggester.py`
    - Test: Known pattern returns recommendation
    - Test: Unknown pattern returns None
    - Test: Correct KB integration
  - [ ] 5.6 Run checks following testing skill
  - [ ] 5.7 **Audit:** Verify testing skill conventions followed
  - [ ] 5.8 Record results
  - [ ] 5.9 Commit: `feat: add fix suggester with KB integration (Task 5.0)`

**Done When:**
- FixSuggester returns Optional[FixRecommendation]
- Returns None when no pattern (not fallback - caller decides)
- Properly queries KnowledgeBase
- Tests pass

---

### Phase 6: WebInterface Checker

- [ ] 6.0 Implement WebInterface Checker [CORE]
  - [ ] 6.1 Create branch `feature/6.0-webinterface-checker`
  - [ ] 6.2 **ASSESS:** Read `framework/interfaces/web_interface.py` to understand structure
  - [ ] 6.3 **CREATE:** `mcp_server/utils/webinterface_checker.py` with:
    - `WebInterfaceChecker` class
    - `get_available_methods() -> List[MethodInfo]` - Parse WebInterface for public methods
    - `method_exists(method_name: str) -> bool` - Check if method exists
    - `get_method_signature(method_name: str) -> Optional[MethodSignature]` - Get parameters
  - [ ] 6.4 **CREATE:** Unit tests `mcp_server/_dev_tests/test_webinterface_checker.py`
  - [ ] 6.5 Run checks following testing skill
  - [ ] 6.6 **Audit:** Verify testing skill conventions followed
  - [ ] 6.7 Record results
  - [ ] 6.8 Commit: `feat: add WebInterface method checker (Task 6.0)`

**Done When:**
- WebInterfaceChecker parses WebInterface class
- method_exists() works correctly
- Tests cover existing and non-existing methods
- Tests pass

---

### Phase 7: POM Runtime Validation (Step 6)

- [ ] 7.0 Extend Step 6 Gate with Runtime Validation [CORE]
  - [ ] 7.1 Create branch `feature/7.0-pom-runtime-validation`
  - [ ] 7.2 **ASSESS:** Read current `qg_page_object.py` implementation
  - [ ] 7.3 **EXTEND:** `mcp_server/tools/gates/qg_page_object.py`:
    - Import RuntimeValidator, FixSuggester, WebInterfaceChecker
    - Add runtime validation in POST mode (call RuntimeValidator)
    - Add WebInterface method check (call WebInterfaceChecker)
    - Return validation result with error category
    - **Do NOT implement fix loop** - that's AI orchestration
  - [ ] 7.4 **EXTEND:** Gate tests for new validation
  - [ ] 7.5 Run checks following testing skill
  - [ ] 7.6 **Audit:** Verify testing skill conventions followed
  - [ ] 7.7 Record results
  - [ ] 7.8 Commit: `feat: add runtime validation to Step 6 gate (Task 7.0)`

**Done When:**
- POM locators validated at runtime
- WebInterface method existence verified
- Gate returns error category (not fix)
- Tests pass

---

### Phase 8: Task Runtime Validation (Step 7)

- [ ] 8.0 Extend Step 7 Gate with Runtime Validation [CORE]
  - [ ] 8.1 Create branch `feature/8.0-task-runtime-validation`
  - [ ] 8.2 **ASSESS:** Read current `qg_task.py` implementation
  - [ ] 8.3 **EXTEND:** `mcp_server/tools/gates/qg_task.py`:
    - Add runtime validation for POM method calls
    - Validate workflow sequence feasibility
  - [ ] 8.4 **EXTEND:** Gate tests for new validation
  - [ ] 8.5 Run checks following testing skill
  - [ ] 8.6 **Audit:** Verify testing skill conventions followed
  - [ ] 8.7 Record results
  - [ ] 8.8 Commit: `feat: add runtime validation to Step 7 gate (Task 8.0)`

**Done When:**
- Task POM method calls validated
- Workflow sequence feasibility checked
- Tests pass

---

### Phase 9: Role Runtime Validation (Step 8)

- [ ] 9.0 Extend Step 8 Gate with Runtime Validation [CORE]
  - [ ] 9.1 Create branch `feature/9.0-role-runtime-validation`
  - [ ] 9.2 **ASSESS:** Read current `qg_role.py` implementation
  - [ ] 9.3 **EXTEND:** `mcp_server/tools/gates/qg_role.py`:
    - Add runtime validation for Task method calls
    - Validate complete workflow feasibility
  - [ ] 9.4 **EXTEND:** Gate tests for new validation
  - [ ] 9.5 Run checks following testing skill
  - [ ] 9.6 **Audit:** Verify testing skill conventions followed
  - [ ] 9.7 Record results
  - [ ] 9.8 Commit: `feat: add runtime validation to Step 8 gate (Task 9.0)`

**Done When:**
- Role Task method calls validated
- Complete workflow feasibility checked
- Tests pass

---

### Phase 10: Test Runtime Validation (Step 9)

- [ ] 10.0 Extend Step 9 Gate with Runtime Validation [CORE]
  - [ ] 10.1 Create branch `feature/10.0-test-runtime-validation`
  - [ ] 10.2 **ASSESS:** Read current `qg_test_runner.py` implementation
  - [ ] 10.3 **EXTEND:** `mcp_server/tools/gates/qg_test_runner.py`:
    - Add full workflow simulation
    - Validate all assertions reachable
  - [ ] 10.4 **EXTEND:** Gate tests for new validation
  - [ ] 10.5 Run checks following testing skill
  - [ ] 10.6 **Audit:** Verify testing skill conventions followed
  - [ ] 10.7 Record results
  - [ ] 10.8 Commit: `feat: add runtime validation to Step 9 gate (Task 10.0)`

**Done When:**
- Full workflow simulation works
- Assertion reachability validated
- Tests pass

---

### Phase 11: Mandatory Final Gate (Step 10)

- [ ] 11.0 Enforce Mandatory Final Validation [CORE]
  - [ ] 11.1 Create branch `feature/11.0-mandatory-final-gate`
  - [ ] 11.2 **ASSESS:** Read current `qg_save_run.py` implementation
  - [ ] 11.3 **EXTEND:** `mcp_server/tools/gates/qg_save_run.py`:
    - Make final gate mandatory (cannot be bypassed)
    - Aggregate all previous validations
    - Require all steps complete before save
  - [ ] 11.4 **EXTEND:** Gate tests for mandatory enforcement
  - [ ] 11.5 Run checks following testing skill
  - [ ] 11.6 **Audit:** Verify testing skill conventions followed
  - [ ] 11.7 Record results
  - [ ] 11.8 Commit: `feat: make Step 10 final gate mandatory (Task 11.0)`

**Done When:**
- Final gate cannot be bypassed
- All previous step validations aggregated
- Tests pass

---

### Phase 12: Audit Trail Enhancement

- [ ] 12.0 Extend Audit Logger for Runtime Validation [GLUE]
  - [ ] 12.1 Create branch `feature/12.0-audit-enhancement`
  - [ ] 12.2 **ASSESS:** Read current `mcp_server/utils/audit_logger.py` implementation
  - [ ] 12.3 **EXTEND:** `mcp_server/utils/audit_logger.py`:
    - Add `log_runtime_validation(element, result, category)` method
    - Add `log_fix_attempt(element, fix, outcome)` method
    - Preserve existing functionality
  - [ ] 12.4 **EXTEND:** Unit tests for new logging methods
  - [ ] 12.5 Run checks following testing skill
  - [ ] 12.6 **Audit:** Verify testing skill conventions followed
  - [ ] 12.7 Record results
  - [ ] 12.8 Commit: `feat: extend audit logger for runtime validation (Task 12.0)`

**Done When:**
- Runtime validation logged with categories
- Fix attempts logged
- Existing functionality preserved
- Tests pass

---

### Phase 13: Knowledge Base Patterns

- [ ] 13.0 Extend Knowledge Base with Runtime Patterns [GLUE]
  - [ ] 13.1 Create branch `feature/13.0-kb-patterns`
  - [ ] 13.2 **EXTEND:** `docs/KNOWLEDGE_BASE.md`:
    - Add "Runtime Validation Patterns" section
    - Add initial error category → fix mappings:
      - LOCATOR_NOT_FOUND → check selector, try different strategy
      - NOT_VISIBLE → add wait, scroll into view
      - NOT_INTERACTABLE → use click_js
      - STALE_REFERENCE → re-find element
      - METHOD_NOT_FOUND → check WebInterface, propose addition
  - [ ] 13.3 Verify knowledge_base.py can parse new section
  - [ ] 13.4 **Audit:** Verify documentation quality
  - [ ] 13.5 Record results
  - [ ] 13.6 Commit: `feat: add runtime validation patterns to KB (Task 13.0)`

**Done When:**
- KB has runtime validation patterns section
- Error → fix mappings documented
- knowledge_base.py can read patterns
- Patterns are actionable

---

### Phase 14: Re-Validation Triggers

- [ ] 14.0 Implement Re-Validation on User Changes [GLUE]
  - [ ] 14.1 Create branch `feature/14.0-revalidation-triggers`
  - [ ] 14.2 **ASSESS:** Read existing gate implementations for trigger points
  - [ ] 14.3 **EXTEND:** Base gate or individual gates:
    - Add change detection logic
    - Add re-validation trigger on user modification
    - Add cascade re-validation for downstream steps
  - [ ] 14.4 **EXTEND:** Tests for re-validation triggers
  - [ ] 14.5 Run checks following testing skill
  - [ ] 14.6 **Audit:** Verify testing skill conventions followed
  - [ ] 14.7 Record results
  - [ ] 14.8 Commit: `feat: add re-validation triggers on user changes (Task 14.0)`

**Done When:**
- User changes trigger re-validation
- Downstream steps cascade correctly
- Tests pass

---

### Phase 15: Checkpoint Resume

- [ ] 15.0 Extend State Manager for Checkpoint Resume [GLUE]
  - [ ] 15.1 Create branch `feature/15.0-checkpoint-resume`
  - [ ] 15.2 **ASSESS:** Read current `mcp_server/utils/state_manager.py` implementation
  - [ ] 15.3 **EXTEND:** `mcp_server/utils/state_manager.py`:
    - Add `save_checkpoint(step, data)` method
    - Add `restore_checkpoint(step)` method
    - Add `list_checkpoints()` method
    - Add `get_resume_step()` method
  - [ ] 15.4 **EXTEND:** Unit tests for checkpoint functionality
  - [ ] 15.5 Run checks following testing skill
  - [ ] 15.6 **Audit:** Verify testing skill conventions followed
  - [ ] 15.7 Record results
  - [ ] 15.8 Commit: `feat: add checkpoint resume to state manager (Task 15.0)`

**Done When:**
- Checkpoints can be saved and restored
- Resume from last successful step works
- Tests pass

---

## Relevant Files Summary

### Files To CREATE (SRP-Compliant)

| File | Single Responsibility |
|------|----------------------|
| `mcp_server/utils/scope_discovery.py` | Analyze workflow scope |
| `mcp_server/utils/runtime_validator.py` | Validate elements, return error category |
| `mcp_server/utils/fix_suggester.py` | Suggest fixes (returns None if unknown) |
| `mcp_server/utils/knowledge_base.py` | Read/write KB patterns |
| `mcp_server/utils/webinterface_checker.py` | Check WebInterface methods |

### Test Files To CREATE

| File | Tests For |
|------|-----------|
| `mcp_server/_dev_tests/test_scope_discovery.py` | scope_discovery.py |
| `mcp_server/_dev_tests/test_runtime_validator.py` | runtime_validator.py |
| `mcp_server/_dev_tests/test_fix_suggester.py` | fix_suggester.py |
| `mcp_server/_dev_tests/test_knowledge_base.py` | knowledge_base.py |
| `mcp_server/_dev_tests/test_webinterface_checker.py` | webinterface_checker.py |
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

**Last Updated:** 2025-12-30
**Version:** 1.1 (SRP-compliant design)
