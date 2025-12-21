# PRD: QA Execution Engine

**Version:** 1.0
**Created:** 2025-12-20
**Status:** Draft

---

## 1. Introduction/Overview

Implement the QA Execution Engine - quality gates and state management that enforce design decisions during the 10-step test automation workflow.

**Terminology:**
- **QA Guidance Layer** = Skill that guides AI (already exists)
- **QA Execution Engine** = Implementation (quality gates, state manager) - THIS PROJECT

**Problem:** Current MCP tools generate code but lack enforcement. AI can skip steps, pass incomplete data, and ignore design decisions. This results in skeleton code, missing assertions, and broken imports.

**Solution:** Add quality gates (qg_* tools) that validate at each step boundary, block progression on failure, and persist state for auditability.

---

## 2. Goals

| Goal | Measure |
|------|---------|
| Enforce all 28 DDs | Each DD appears in at least one step's validation |
| Block incomplete data | Zero skeleton code reaches Step 10 |
| Enable workflow resume | State persisted after each step |
| Sequential validation | Cannot proceed to Step N+1 until Step N passes |

---

## 3. User Stories

**US-1:** As an AI assistant, I need quality gates to validate my work so that incomplete code doesn't propagate through the tool chain.

**US-2:** As a user, I want the workflow to block on errors so that I'm consulted before bad code is generated.

**US-3:** As a developer, I want workflow state persisted so that I can resume after interruption and audit what happened.

**US-4:** As a user, I want clear error messages when gates fail so that I know exactly what's wrong and how to fix it.

---

## 4. Functional Requirements

### 4.1 Quality Gate Tools (qg_*)

| FR | Requirement |
|----|-------------|
| FR-01 | Implement `qg_preflight` - validates credential_strategy and test_data_location |
| FR-02 | Implement `qg_user_input` - validates persona, URL, role_name, domain |
| FR-03 | Implement `qg_ai_processing` - validates bdd_scenarios, expected_states, intent |
| FR-04 | Implement `qg_test_scenarios` - PRE validates input, POST validates Tool 1 output |
| FR-05 | Implement `qg_discovered_elements` - PRE validates page ready, POST validates elements found |
| FR-06 | Implement `qg_page_object` - PRE validates elements, POST validates no skeleton (DD-25) |
| FR-07 | Implement `qg_task` - PRE validates pom_metadata, POST validates no skeleton/locators (DD-25, DD-27) |
| FR-08 | Implement `qg_role` - PRE validates task_metadata, POST validates no skeleton (DD-25) |
| FR-09 | Implement `qg_test_runner` - PRE validates role/pom metadata, POST validates assertions use POM state methods (DD-15) |
| FR-10 | Implement `qg_save_run` - PRE validates all code present, no skeleton anywhere |

### 4.2 State Manager

| FR | Requirement |
|----|-------------|
| FR-11 | Implement `StateManager` class with save(), load(), get_step(), is_step_complete() |
| FR-12 | State file location: `mcp_server/state/workflow_state.json` |
| FR-13 | State schema per step as defined in step-*.md files |
| FR-14 | Quality gates (Steps 1-3) call state_manager.save() on PASS |
| FR-15 | Operation tools (Steps 4-9) call state_manager.save() on SUCCESS |
| FR-16 | AI never calls state_manager directly |

### 4.3 Gate Behavior

| FR | Requirement |
|----|-------------|
| FR-17 | Gates return `{"status": "pass"}` or `{"status": "fail", "error": "...", "fix_hint": "..."}` |
| FR-18 | On FAIL, gate provides specific error message and fix hint |
| FR-19 | Gate enforcement: Cannot proceed to Step N+1 until Step N gate passes |
| FR-20 | Retry policy: AI retries up to 3 times, then STOP → REPORT → USER DECIDES |

### 4.4 DD Enforcement

| FR | Requirement |
|----|-------------|
| FR-21 | DD-25 (skeleton code): Gates check for `pass`, `# Add...`, empty bodies |
| FR-22 | DD-27 (no locators in Task): qg_task checks for `By.` imports |
| FR-23 | DD-15 (POM state assertions): qg_test_runner validates assertions use state methods |
| FR-24 | DD-19 (tool imports): All tools import from `tools/`, never `utils/` |
| FR-25 | DD-26 (data contracts): Gates validate metadata format matches Section H specs |

---

## 5. Non-Goals (Out of Scope)

| Non-Goal | Reason |
|----------|--------|
| CI/CD integration | Focus on local execution first |
| IDE plugins | Future roadmap item |
| pip packaging | Future roadmap item |
| Multi-workflow support | Single workflow at a time for v1 |
| Parallel step execution | Sequential only for v1 |

---

## 6. Design Considerations

### Architecture (4-Layer)

All four layers together form the **QA Execution Engine**:

```
┌─────────────────────────────────────────────────────────────────────┐
│                      QA EXECUTION ENGINE                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│   SKILL (qa-guidance-layer)        ← Guides AI through workflow     │
│       │                                                             │
│       ▼                                                             │
│   QUALITY GATES (qg_*)             ← Validates at step boundaries   │
│       │                                                             │
│       ▼                                                             │
│   OPERATION TOOLS (Tool 1-6)       ← Generates code artifacts       │
│       │                                                             │
│       ▼                                                             │
│   STATE MANAGER                    ← Persists workflow state        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

**Component Responsibilities:**

| Component | Purpose | Who Calls |
|-----------|---------|-----------|
| Skill | Step-by-step workflow guidance | AI reads, follows instructions |
| Quality Gates | Validate before/after operations | AI calls qg_* tools |
| Operation Tools | Generate code (POM, Task, Role, Test) | AI calls Tool 1-6 |
| State Manager | Persist state, enable resume | Gates/Operations call internally |

### File Structure

```
mcp_server/
├── tools/
│   ├── gates/                    ← NEW: Quality gate tools
│   │   ├── __init__.py
│   │   ├── qg_preflight.py
│   │   ├── qg_user_input.py
│   │   ├── qg_ai_processing.py
│   │   ├── qg_test_scenarios.py
│   │   ├── qg_discovered_elements.py
│   │   ├── qg_page_object.py
│   │   ├── qg_task.py
│   │   ├── qg_role.py
│   │   ├── qg_test_runner.py
│   │   └── qg_save_run.py
│   │
│   └── (existing operation tools)
│
├── state/                        ← NEW: Workflow state
│   └── workflow_state.json
│
└── utils/
    └── state_manager.py          ← NEW: State persistence
```

### Reference Documents

| Document | Location |
|----------|----------|
| Step definitions | `.claude/skills/qa-guidance-layer/references/step-*.md` |
| Design decisions | `CLAUDE.md` (DD-01 through DD-28) |
| Architecture | `FRAMEWORK.md` Section 9 |
| Meta-template | `.claude/skills/design-execution-engine/SKILL.md` |

---

## 7. Technical Considerations

### Dependencies

- Existing MCP server infrastructure
- Existing operation tools (Tool 1-6)
- Python 3.x, JSON for state

### Integration Points

- Quality gates called by AI before/after operation tools
- State manager called internally by gates/operations
- Skill files guide AI orchestration (no code changes needed)

### Constraints

- Gates must be fast (<100ms validation)
- State file must be atomic writes (no corruption)
- Error messages must be actionable

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| DD enforcement | 100% of DDs validated by at least one gate |
| Skeleton code blocked | 0 skeleton code reaches Step 10 |
| Workflow completion | 90%+ workflows complete without manual intervention |
| Resume capability | Can resume from any step after interruption |

---

## 9. Test Strategy

**Reference:** Uses `.claude/skills/testing/` framework for comprehensive coverage.

### 9.1 Test Pyramid (Domain-Specific)

```
┌─────────────────────────────────────────────────────────────────────┐
│                    QA EXECUTION ENGINE TEST PYRAMID                  │
├─────────────────────────────────────────────────────────────────────┤
│  1. DATA STRUCTURE    - Does state schema work?                      │
│  2. VALIDATION LOGIC  - Does gate validation work?                   │
│  3. STATE OPERATIONS  - Does persistence work?                       │
│  4. EDGE CASES        - Does it handle weird input?                  │
│  5. ERROR HANDLING    - Does it fail gracefully with fix_hint?       │
│  6. INTEGRATION       - Do gates block correctly?                    │
│  7. E2E               - Does full workflow complete?                 │
└─────────────────────────────────────────────────────────────────────┘
```

### 9.2 Test Matrix by Component

#### State Manager Tests

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | save/load works | invalid path | empty state | P0 |
| Unit | get_step returns data | step not found | step 0 | P0 |
| Unit | is_step_complete | incomplete step | boundary step | P0 |
| Unit | atomic write | write failure | concurrent writes | P1 |
| Integration | gate saves state | - | resume after interrupt | P0 |

**Test File:** `mcp_server/_dev_tests/test_state_manager.py`

#### Step 1 Gate (qg_preflight)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | valid credential_strategy | invalid value | empty string | P0 |
| Unit | valid test_data_location | missing field | null value | P0 |
| Unit | both fields valid | both invalid | one valid/one invalid | P0 |
| Unit | state saved on pass | no save on fail | - | P0 |
| Integration | blocks Step 2 on fail | - | - | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_preflight.py`

#### Step 2 Gate (qg_user_input)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | valid persona | missing "As a" | empty persona | P0 |
| Unit | valid URL | invalid URL format | localhost URL | P0 |
| Unit | role_name extracted | cannot extract role | multiple roles | P1 |
| Unit | domain detected | unknown domain | - | P1 |
| Integration | blocks Step 3 on fail | - | - | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_user_input.py`

#### Step 3 Gate (qg_ai_processing)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | valid bdd_scenarios | missing given/when/then | empty scenarios | P0 |
| Unit | valid expected_states | empty array | single state | P0 |
| Unit | valid intent | empty intent | very long intent | P1 |
| Unit | metadata_context built | - | - | P0 |
| Integration | blocks Step 4 on fail | - | - | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_ai_processing.py`

#### Step 4 Gate (qg_test_scenarios)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | PRE: Step 3 complete | Step 3 incomplete | - | P0 |
| Unit | POST: valid scenarios | skeleton scenarios | single scenario | P0 |
| Unit | POST: BDD format (DD-23) | missing then | - | P0 |
| Unit | POST: tool import (DD-19) | wrong import path | - | P1 |
| Integration | blocks Step 5 on fail | - | - | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_test_scenarios.py`

#### Step 5 Gate (qg_discovered_elements)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | PRE: Step 4 complete | Step 4 incomplete | - | P0 |
| Unit | PRE: credential_strategy applied | - | strategy=none | P1 |
| Unit | POST: elements not empty | empty elements | single element | P0 |
| Unit | POST: element structure | missing locator | multiple locator types | P0 |
| Unit | POST: page_name PascalCase | lowercase name | - | P1 |
| Integration | blocks Step 6 on fail | - | - | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_discovered_elements.py`

#### Step 6 Gate (qg_page_object)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | PRE: Step 5 complete | Step 5 incomplete | - | P0 |
| Unit | PRE: elements present | no elements | - | P0 |
| Unit | POST: no skeleton (DD-25) | pass in body | # Add comment | P0 |
| Unit | POST: locators present | missing locator | - | P0 |
| Unit | POST: state methods match expected_states | missing state method | - | P0 |
| Unit | POST: metadata structure (DD-26) | missing action_methods | - | P0 |
| Integration | blocks Step 7 on fail | - | skeleton triggers retry | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_page_object.py`

#### Step 7 Gate (qg_task)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | PRE: Step 6 complete | Step 6 incomplete | - | P0 |
| Unit | PRE: pom_metadata present | no metadata | - | P0 |
| Unit | POST: no skeleton (DD-25) | empty body | placeholder | P0 |
| Unit | POST: no locators (DD-27) | By. import | By.CSS_SELECTOR | P0 |
| Unit | POST: check-existing (DD-12) | - | existing task found | P1 |
| Unit | POST: metadata structure (DD-26) | missing task_methods | - | P0 |
| Integration | blocks Step 8 on fail | - | - | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_task.py`

#### Step 8 Gate (qg_role)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | PRE: Step 7 complete | Step 7 incomplete | - | P0 |
| Unit | PRE: task_metadata present | no metadata | - | P0 |
| Unit | POST: no skeleton (DD-25) | pass in body | - | P0 |
| Unit | POST: check-existing (DD-12) | - | existing role found | P1 |
| Unit | POST: metadata structure (DD-26) | missing workflow_methods | - | P0 |
| Integration | blocks Step 9 on fail | - | - | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_role.py`

#### Step 9 Gate (qg_test_runner)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | PRE: Step 8 complete | Step 8 incomplete | - | P0 |
| Unit | PRE: role + pom metadata | missing pom_metadata | - | P0 |
| Unit | POST: no skeleton (DD-25) | pass in test | - | P0 |
| Unit | POST: POM state assertions (DD-15) | assert result==True | - | P0 |
| Unit | POST: import paths (DD-18) | wrong import | - | P0 |
| Unit | POST: parameter values (DD-17) | placeholder values | - | P1 |
| Integration | blocks Step 10 on fail | - | - | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_test_runner.py`

#### Step 10 Gate (qg_save_run)

| Type | Happy | Negative | Edge | Priority |
|------|-------|----------|------|----------|
| Unit | PRE: Step 9 complete | Step 9 incomplete | - | P0 |
| Unit | PRE: all code present | missing POM | missing Role | P0 |
| Unit | PRE: no skeleton anywhere | skeleton in any layer | - | P0 |
| Unit | PRE: DD-22 documented | - | - | P1 |
| Integration | final sweep catches skeleton | - | - | P0 |

**Test File:** `mcp_server/_dev_tests/test_gates/test_qg_save_run.py`

### 9.3 Integration Tests

| Test | Purpose | Priority |
|------|---------|----------|
| `test_step_blocking.py` | Step N blocks Step N+1 until pass | P0 |
| `test_skeleton_blocked.py` | Skeleton code at any step blocks progression | P0 |
| `test_state_persistence.py` | State persists across gate calls | P0 |
| `test_workflow_resume.py` | Resume from any step after interruption | P0 |
| `test_retry_policy.py` | 3 retries then STOP → REPORT → USER DECIDES | P1 |
| `test_full_workflow.py` | End-to-end with all gates | P0 |

**Test Directory:** `mcp_server/_dev_tests/test_integration/`

### 9.4 E2E Tests

| Test | Purpose | Priority |
|------|---------|----------|
| `test_e2e_auth_workflow.py` | Full auth workflow (login) with all gates | P0 |
| `test_e2e_catalog_workflow.py` | Full catalog workflow with all gates | P1 |
| `test_e2e_skeleton_rejection.py` | Intentionally bad tool output blocked | P0 |

**Test Directory:** `mcp_server/_dev_tests/test_e2e/`

### 9.5 Manual Validation

- [ ] Run actual workflow with live MCP tools
- [ ] Verify gates block on intentionally bad input
- [ ] Verify state persists and resumes correctly
- [ ] Verify error messages include actionable fix_hint

### 9.6 Test Commands

```bash
# Run all unit tests
pytest mcp_server/_dev_tests/test_*.py -v

# Run gate tests only
pytest mcp_server/_dev_tests/test_gates/ -v

# Run integration tests
pytest mcp_server/_dev_tests/test_integration/ -v

# Run with coverage
pytest mcp_server/_dev_tests/ --cov=mcp_server --cov-report=term-missing

# Run specific gate test
pytest mcp_server/_dev_tests/test_gates/test_qg_preflight.py -v
```

### 9.7 Coverage Targets

| Component | Target | Rationale |
|-----------|--------|-----------|
| State Manager | 95% | Core infrastructure, must be reliable |
| Gate Base | 90% | Shared logic, high reuse |
| Individual Gates | 90% | Enforcement logic, critical |
| Integration | 85% | Component interactions |
| E2E | 80% | Full workflows |

---

## 10. Acceptance Tests (GIVEN/WHEN/THEN)

**AT-01: Preflight Gate Blocks Invalid Input**
```
GIVEN the workflow has not started
WHEN I call qg_preflight with credential_strategy="invalid"
THEN the gate returns status="fail" with error message
AND I cannot proceed to Step 2
```

**AT-02: Skeleton Code Blocked at POM**
```
GIVEN Step 5 is complete with discovered_elements
WHEN Tool 3 generates POM with "pass" in method body
THEN qg_page_object returns status="fail"
AND error mentions "skeleton code detected"
AND I cannot proceed to Step 7
```

**AT-03: State Persists After Gate Pass**
```
GIVEN Step 1 gate passes
WHEN I check workflow_state.json
THEN step 1 status="complete"
AND data contains credential_strategy and test_data_location
```

**AT-04: Workflow Resume**
```
GIVEN workflow completed Step 3
AND workflow was interrupted
WHEN I restart the workflow
THEN state_manager.is_step_complete(3) returns True
AND I can continue from Step 4
```

**AT-05: DD-15 Enforced**
```
GIVEN Tool 6 generates test with "assert result == True"
WHEN qg_test_runner validates
THEN gate returns status="fail"
AND error mentions "use POM state methods, not return values"
```

**AT-06: Data Contract Validated**
```
GIVEN Tool 3 outputs metadata with missing action_methods
WHEN qg_task validates pom_metadata
THEN gate returns status="fail"
AND error mentions "pom_metadata missing action_methods"
```

---

## 11. Implementation Order (Sequential)

| Phase | Steps | Deliverables |
|-------|-------|--------------|
| Phase 1 | State Manager | `state_manager.py`, tests |
| Phase 2 | Step 1 Gate | `qg_preflight.py`, tests |
| Phase 3 | Step 2 Gate | `qg_user_input.py`, tests |
| Phase 4 | Step 3 Gate | `qg_ai_processing.py`, tests |
| Phase 5 | Step 4 Gate | `qg_test_scenarios.py`, tests |
| Phase 6 | Step 5 Gate | `qg_discovered_elements.py`, tests |
| Phase 7 | Step 6 Gate | `qg_page_object.py`, tests |
| Phase 8 | Step 7 Gate | `qg_task.py`, tests |
| Phase 9 | Step 8 Gate | `qg_role.py`, tests |
| Phase 10 | Step 9 Gate | `qg_test_runner.py`, tests |
| Phase 11 | Step 10 Gate | `qg_save_run.py`, tests |
| Phase 12 | Integration | Full workflow test |

**Process per phase:**
1. Implement gate
2. Write unit tests
3. Manual validation
4. Move to next phase

---

## 12. Open Questions

| Question | Status |
|----------|--------|
| Should gates be registered as MCP tools or internal functions? | MCP tools (for AI to call) |
| How to handle gate timeout? | 30s default, configurable |
| Should state file be gitignored? | Yes (workflow-specific) |

---

## 13. Rollout Plan

1. **Local dev:** Implement and test locally
2. **Skill update:** Update qa-guidance-layer skill to reference gates
3. **Documentation:** Update FRAMEWORK.md with gate usage
4. **Validation:** Run full E2E workflow with gates enabled

**Rollback:** If gates cause issues, AI can bypass by not calling them (skill guidance only).

---

*PRD complete. Ready for task generation.*
