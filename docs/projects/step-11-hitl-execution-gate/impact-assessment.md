# Step 11 Impact Assessment

**Project:** step-11-hitl-execution-gate
**Date:** 2026-01-13
**Purpose:** Assess impact of adding Step 11 (Execution Validation Gate with HITL) to the existing 11-step workflow

---

## Executive Summary

**Scope:** Adding Step 11 extends the existing 11-step QA workflow to include test execution validation with human-in-the-loop (HITL) triage.

**Impact Level:** MODERATE
- 1 breaking change (StateManager VALID_STEPS)
- 5 files require updates
- 0 backward compatibility issues (additive extension)
- Clear migration path

---

## 1. Who Calls This Code?

### Current Workflow Entry Points

| Component | Current State | Step 11 Impact |
|-----------|---------------|----------------|
| **Slash Command** | `/qa-workflow` and `/qa-workflow-dev` invoke 11-step workflow | ✅ No change - remains entry point |
| **QA Guidance Layer Skill** | `.claude/skills/qa-guidance-layer/SKILL.md` references Steps 1-11 | ⚠️ UPDATE: Add Step 11 reference |
| **Step References** | `.claude/skills/qa-guidance-layer/references/step-01.md` through `step-10.md` | ➕ ADD: Create `step-11.md` |
| **MCP Server** | `mcp_server/server.py` registers tools for Steps 1-11 gates | ➕ ADD: Register Step 11 tools (`run_test`, `qg_execution`, `qg_workflow_complete`) |
| **StateManager** | `mcp_server/utils/state_manager.py` validates steps 1-10 | ⚠️ BREAKING: Extend `VALID_STEPS` to include 11 |
| **AuditLogger** | `mcp_server/utils/audit_logger.py` logs gate results | ✅ No change - extensible by design |

### Current Step 10 Behavior

**File:** `mcp_server/tools/gates/qg_save_run.py`

**What it does:**
1. Validates Step 9 complete
2. Validates all 4 code blocks present (POM, Task, Role, Test)
3. Validates no skeleton code (DD-25 final sweep)
4. Validates all generated files exist on disk (Task 19.0)
5. Validates test data files exist (FR-14.4)
6. Clears session marker (workflow complete)
7. Returns PASS (workflow ends)

**What it does NOT do:**
- Does NOT run tests (current Step 10 just validates code is ready)
- Does NOT provide test execution feedback
- Does NOT enable HITL triage

**Current documentation:**
- `.claude/skills/qa-guidance-layer/references/step-10.md` describes ASK user "Ready to run?" then RUN pytest
- Documentation implies test execution happens, but gate doesn't enforce it
- **GAP:** Test execution is optional and unvalidated (DEF-058 root cause)

---

## 2. What Depends on Current Behavior?

### Components That Assume 10-Step Workflow

| Component | Assumption | Step 11 Impact |
|-----------|------------|----------------|
| **StateManager** | `VALID_STEPS = range(1, 11)` (steps 1-10 only) | ⚠️ BREAKING: Must extend to `range(1, 12)` |
| **Skill Documentation** | References "11-step workflow" in multiple places | ⚠️ UPDATE: Change to "11-step workflow" |
| **Audit Trail** | Progressive audit ends at Step 10 | ✅ Extends naturally (hook-based) |
| **Quality Gates** | 10 gates registered (qg_preflight through qg_save_run) | ➕ ADD: 2 new gates (`qg_execution`, `qg_workflow_complete`) |
| **Test References** | Tests reference 11-step workflow | ⚠️ UPDATE: Test assertions for step count |

### Current Test Execution Flow

**Today:**
```
Step 10: qg_save_run (PRE) validates code ready
→ Gate PASSES
→ Workflow COMPLETE
→ User manually runs test (optional)
```

**Problem:** Test execution not enforced, failures not captured (DEF-058)

**After Step 11:**
```
Step 10: qg_save_run (PRE) validates code ready
→ Gate PASSES
→ Step 11: run_test executes pytest
→ qg_execution validates test passed
→ IF FAIL: HITL triage (app bug vs test issue)
→ qg_workflow_complete validates cross-step consistency
→ Workflow COMPLETE
```

---

## 3. What Will Break?

### Breaking Changes

| Component | File | Line | Change Required | Risk |
|-----------|------|------|----------------|------|
| **StateManager** | `mcp_server/utils/state_manager.py` | 26 | `VALID_STEPS = range(1, 11)` → `range(1, 12)` | LOW - Simple change, test coverage exists |

### Non-Breaking Updates Required

| Component | File | Change Type | Risk |
|-----------|------|-------------|------|
| **Skill Documentation** | `.claude/skills/qa-guidance-layer/SKILL.md` | Add Step 11 reference | LOW - Documentation only |
| **Step Reference** | `.claude/skills/qa-guidance-layer/references/step-11.md` | Create new file | LOW - New file, no dependencies |
| **MCP Server** | `mcp_server/server.py` | Register 3 new tools | LOW - Additive, existing tools unchanged |
| **Gate Module** | `mcp_server/tools/gates/__init__.py` | Export 2 new gates | LOW - Additive import |
| **Dev Tests** | `mcp_server/_dev_tests/test_gates/` | Create test files | LOW - New tests, existing tests unchanged |

### Existing Tests That Reference Step Count

**Search Pattern:** "Step 10", "11-step", "steps 1-10"

**Files To Update:**
- Documentation files referencing "11-step workflow"
- Test assertions checking step range (1-10)
- Audit trail tests expecting Step 10 as final step

**Migration Strategy:**
1. Search for hardcoded "10" references: `grep -r "11-step\|Step 10\|steps 1-10" .`
2. Update references to "11-step workflow"
3. Update assertions expecting final step = 10 to final step = 11
4. Run full test suite to catch missed references

---

## 4. Migration Path

### Phase 1: Core Implementation (No Breaking Changes)

**Goal:** Implement Step 11 tools without modifying existing workflow

**Files To Create:**
```
mcp_server/tools/operations/run_test.py              (Operation tool)
mcp_server/tools/gates/qg_execution.py               (Step 11 gate)
mcp_server/tools/gates/qg_workflow_complete.py       (Meta-gate)
.claude/skills/qa-guidance-layer/references/step-11.md
mcp_server/_dev_tests/test_gates/test_qg_execution.py
mcp_server/_dev_tests/test_gates/test_qg_workflow_complete.py
```

**Files To Update:**
```
mcp_server/tools/gates/__init__.py                   (Export new gates)
mcp_server/server.py                                 (Register new tools)
```

**Validation:** New tools callable, but workflow still ends at Step 10 (backward compatible)

### Phase 2: Extend StateManager (Breaking Change)

**File:** `mcp_server/utils/state_manager.py:26`

**Change:**
```python
# BEFORE
VALID_STEPS = range(1, 11)  # 1-10 inclusive

# AFTER
VALID_STEPS = range(1, 12)  # 1-11 inclusive
```

**Impact:** Existing workflows unaffected (all write to steps 1-10, which are still valid)

**Validation:**
- Existing tests still pass (steps 1-10 remain valid)
- New Step 11 tests pass (step 11 now accepted)

### Phase 3: Update Documentation

**Files:**
```
.claude/skills/qa-guidance-layer/SKILL.md            (Add Step 11 overview)
FRAMEWORK.md                                         (Update Section 9 workflow diagram)
docs/projects/release-readiness/                     (Update release checklist)
```

**Search & Replace:**
- "11-step workflow" → "11-step workflow"
- "Steps 1-11" → "Steps 1-11"
- "Step 10 (Save & Run) completes workflow" → "Step 10 validates code, Step 11 validates execution"

### Phase 4: Integration Testing

**Test Scenarios:**
1. **Happy Path:** Run full 11-step workflow, test passes → workflow completes
2. **Test Failure - App Bug:** Test fails, HITL triages as app defect → defect logged, workflow stops
3. **Test Failure - Test Issue:** Test fails, HITL triages as test bug → AI fixes code, gates re-validate, test re-runs
4. **Gate Failure:** qg_workflow_complete detects inconsistency → workflow escalates to human
5. **Backward Compatibility:** Old 11-step workflow data still readable by StateManager

---

## 5. Detailed Component Analysis

### 5.1 StateManager (BREAKING CHANGE)

**File:** `mcp_server/utils/state_manager.py`

**Current Implementation:**
```python
VALID_STEPS = range(1, 11)  # 1-10 inclusive

def get_step(self, step: int) -> Optional[dict]:
    """Get step data by number."""
    if step not in VALID_STEPS:
        return None
    # Read from state
```

**Required Change:**
```python
VALID_STEPS = range(1, 12)  # 1-11 inclusive
```

**Who Calls This:**
- All quality gates (qg_preflight through qg_save_run)
- Step 11 tools (qg_execution, qg_workflow_complete)

**Impact:**
- ✅ Existing workflows: No change (steps 1-10 still valid)
- ✅ New workflows: Can save Step 11 data
- ✅ Tests: Existing tests unaffected (all use steps 1-10)

**Risk:** LOW - Single constant change, backward compatible

---

### 5.2 MCP Server Tool Registration

**File:** `mcp_server/server.py`

**Current Registered Tools:**
```python
# Steps 1-11 quality gates
qg_preflight, qg_user_input, qg_ai_processing, qg_test_scenarios,
qg_discovered_elements, qg_page_object, qg_task, qg_role,
qg_test_runner, qg_save_run

# Operation tools (placeholders)
run_test (not implemented)
analyze_failure (not implemented)
```

**Required Additions:**
```python
# Step 11 operation tool
async def run_test(arguments: dict) -> str:
    """Execute pytest with consistent parameters."""
    from tools.operations.run_test import execute_test
    result = execute_test(arguments)
    return json.dumps(result, indent=2)

# Step 11 quality gates
async def qg_execution(arguments: dict) -> str:
    """Step 11: Execution validation gate."""
    result = QGExecution.validate(arguments)
    return json.dumps(result, indent=2)

async def qg_workflow_complete(arguments: dict) -> str:
    """Meta-gate: Validates 11-step workflow integrity."""
    result = QGWorkflowComplete.validate(arguments)
    return json.dumps(result, indent=2)
```

**Impact:**
- ✅ Existing tools unchanged
- ➕ 3 new tools added
- ✅ Backward compatible (new tools optional until Step 11 invoked)

**Risk:** LOW - Additive change, no modification to existing tools

---

### 5.3 Audit Trail System

**File:** `mcp_server/utils/audit_logger.py`

**Current Implementation:**
```python
def log_gate(self, step: int, gate_name: str, mode: str, result: str):
    """Log gate execution."""
    # Appends to audit file progressively
```

**Step 11 Impact:**
- ✅ No code changes needed (extensible by design)
- ➕ Step 11 gates will automatically log to audit trail
- ➕ New detail file: `tests/_audit/step11/{run_id}_diagnostic.json`

**Hook Registration:**
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__qa-automation__qg_.*",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/audit-trail-writer.py\""
          }
        ]
      }
    ]
  }
}
```

**Impact:**
- ✅ Existing hook matches new gates (pattern: `qg_.*`)
- ✅ Step 11 automatically captured in audit trail
- ➕ Additional detail logging for Step 11 diagnostics

**Risk:** NONE - System designed for extension

---

### 5.4 Documentation Updates

**Files Requiring "11-step" → "11-step" Updates:**

| File | Line(s) | Reference | Update |
|------|---------|-----------|--------|
| `.claude/skills/qa-guidance-layer/SKILL.md` | Multiple | "11-step workflow" | Change to "11-step workflow" |
| `FRAMEWORK.md` | Section 9 | Workflow diagram shows Steps 1-11 | Add Step 11 to diagram |
| `README.md` | Overview | "11-step QA workflow" | Change to "11-step workflow" |
| `docs/projects/release-readiness/1-prd-release-readiness.md` | Multiple | References 10 steps | Add Step 11 |

**New Documentation Required:**
```
.claude/skills/qa-guidance-layer/references/step-11.md
docs/projects/step-11-hitl-execution-gate/2-prd-step-11-hitl-execution-gate.md
docs/projects/step-11-hitl-execution-gate/3-tasks-step-11-hitl-execution-gate.md
```

**Risk:** LOW - Documentation-only changes

---

### 5.5 Test Impact

**Existing Tests:**
- `mcp_server/_dev_tests/test_gates/` - Tests for gates 1-10
- `mcp_server/_dev_tests/test_production_fixes.py` - E2E workflow tests
- `mcp_server/_dev_tests/test_audit_logger.py` - Audit trail tests

**Required Test Updates:**
```
✅ NO CHANGES - Existing tests validate steps 1-10 (still valid)
➕ NEW TESTS - Add test_qg_execution.py, test_qg_workflow_complete.py
➕ NEW E2E - Add 11-step workflow test
```

**Test Strategy:**
1. Run existing test suite → Verify all pass (backward compatibility)
2. Add Step 11 tests → Verify new gates work
3. Run E2E 11-step test → Verify full workflow

**Risk:** LOW - Additive tests, existing tests unchanged

---

## 6. Backward Compatibility Analysis

### Existing Workflow Data

**State Files:** `mcp_server/state/{run_id}/workflow_state.json`

**Structure:**
```json
{
  "step_1": { "timestamp": "...", "data": {...} },
  "step_2": { "timestamp": "...", "data": {...} },
  ...
  "step_10": { "timestamp": "...", "data": {...} }
}
```

**Step 11 Impact:**
- ✅ Existing state files remain valid (steps 1-10 unchanged)
- ➕ New workflows add `"step_11"` key
- ✅ StateManager reads both old and new formats

**Conclusion:** FULLY BACKWARD COMPATIBLE

---

### Audit Files

**Location:** `tests/_audit/YYYY-MM-DD_HHMMSS_{workflow}_{intent}.json`

**Current Structure:**
```json
{
  "audit_metadata": {...},
  "step_1": {...},
  ...
  "step_10": {...}
}
```

**Step 11 Impact:**
- ✅ Old audit files remain valid (10 steps)
- ➕ New workflows include `"step_11"` key
- ➕ Additional detail file: `tests/_audit/step11/{run_id}_diagnostic.json`

**Conclusion:** FULLY BACKWARD COMPATIBLE (progressive design)

---

## 7. Risk Assessment

| Risk Category | Level | Mitigation |
|--------------|-------|------------|
| **Breaking Changes** | LOW | Single constant change (VALID_STEPS), simple update |
| **Existing Tests** | LOW | All existing tests use steps 1-10 (unchanged) |
| **Backward Compatibility** | NONE | Additive design, old workflows still work |
| **Documentation Drift** | MEDIUM | Must update all "11-step" references |
| **Integration** | LOW | Hook-based audit trail extends naturally |

---

## 8. Implementation Checklist

### Pre-Implementation

- [x] Impact assessment complete
- [ ] PRD created (Phase 2)
- [ ] Task breakdown complete (Phase 3)
- [ ] Design approved by user

### Phase 1: Core Implementation

- [ ] Create `run_test.py` operation tool
- [ ] Create `qg_execution.py` gate
- [ ] Create `qg_workflow_complete.py` meta-gate
- [ ] Register tools in `server.py`
- [ ] Update `__init__.py` exports

### Phase 2: StateManager Extension

- [ ] Update `VALID_STEPS` to include 11
- [ ] Run existing test suite (verify backward compatibility)
- [ ] Add Step 11 tests

### Phase 3: Documentation

- [ ] Create `step-11.md` reference
- [ ] Update SKILL.md with Step 11 overview
- [ ] Update FRAMEWORK.md Section 9
- [ ] Search & replace "11-step" → "11-step"

### Phase 4: Integration Testing

- [ ] Happy path E2E test (test passes)
- [ ] Test failure - app bug triage
- [ ] Test failure - test issue triage
- [ ] qg_workflow_complete validation
- [ ] Backward compatibility test (old state files)

---

## 9. Success Criteria

**Step 11 is successfully implemented when:**

1. ✅ All existing tests pass (backward compatibility confirmed)
2. ✅ New Step 11 tests pass (functionality validated)
3. ✅ 11-step E2E workflow completes successfully
4. ✅ HITL triage workflow works (app bug vs test issue)
5. ✅ qg_workflow_complete catches consistency issues
6. ✅ Audit trail includes Step 11 data
7. ✅ Old 11-step state files still readable
8. ✅ Documentation updated ("11-step" → "11-step")
9. ✅ StateManager accepts step 11 data

---

## 10. Timeline Estimate

**Complexity:** MODERATE (breaking change + new functionality)

**Phases:**
- Phase 1 (Core Implementation): 3 new tools + tests
- Phase 2 (StateManager): 1 constant change + validation
- Phase 3 (Documentation): Search & update references
- Phase 4 (Integration): E2E testing + validation

**Note:** Following project instructions - no time estimates provided. User decides scheduling.

---

## Conclusion

**Impact Level:** MODERATE
- 1 breaking change (easily mitigated)
- 5 file updates (non-breaking)
- Fully backward compatible
- Clear migration path

**Risk:** LOW
- Single constant change for breaking change
- Additive design (no modification to existing behavior)
- Strong test coverage ensures safety
- Progressive audit trail extends naturally

**Recommendation:** PROCEED with implementation following 4D framework (Define → PRD next)

---

**Document Status:** ✅ COMPLETE
**Next Step:** Create PRD (Phase 2 - Define)
**Blocking Issues:** None
