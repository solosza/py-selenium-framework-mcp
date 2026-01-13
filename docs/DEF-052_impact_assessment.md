# DEF-052 Impact Assessment Report

**Date:** 2026-01-08
**Defect:** run_id isolation broken - each gate creates new run_id
**Status:** IN ASSESSMENT

---

## 1. Who calls this code?

### Callers of `BaseGate.get_audit_logger()`:
- All 10 quality gates (qg_preflight through qg_save_run)
- Each gate calls it to get audit logger, then extracts run_id for StateManager
- Pattern: `audit_logger = cls.get_audit_logger()` → `StateManager(run_id=audit_logger.run_id)`

### Files affected:
- `mcp_server/tools/gates/base_gate.py` (Lines 74-94)
- `mcp_server/tools/gates/qg_preflight.py` (Line 70-71)
- `mcp_server/tools/gates/qg_user_input.py` (Line 105-106)
- `mcp_server/tools/gates/qg_ai_processing.py` (Line 78-79)
- `mcp_server/tools/gates/qg_test_scenarios.py` (Line 47-48)
- `mcp_server/tools/gates/qg_discovered_elements.py`
- `mcp_server/tools/gates/qg_page_object.py`
- `mcp_server/tools/gates/qg_task.py`
- `mcp_server/tools/gates/qg_role.py`
- `mcp_server/tools/gates/qg_test_runner.py`
- `mcp_server/tools/gates/qg_save_run.py`

---

## 2. What depends on current behavior?

### Test Dependencies:
- `test_production_fixes.py::TestBaseGateAuditRunID::test_fresh_run_id_each_workflow()`
  - **Tests that each workflow gets fresh run_id**
  - Manually sets `BaseGate._audit_logger = None` to "simulate new workflow"
  - **This test PASSES in single Python process** (class variable persists)
  - **This test FAILS in production** (each MCP call is separate process, class variable always None)

- `test_production_fixes.py::TestBaseGateAuditRunID::test_no_run_id_reuse_from_state()`
  - Tests that run_id is NEVER reused from StateManager
  - **This is CORRECT** - we should NOT reuse from state, but from SESSION MARKER

### Current Behavior (Broken):
Each MCP tool call runs in separate Python process:
1. Process 1: qg_preflight → new AuditLogger → run_id A → saves to `_state/A/`
2. Process 2: qg_user_input → new AuditLogger → run_id B → saves to `_state/B/`
3. Process 3: qg_ai_processing → new AuditLogger → run_id C → saves to `_state/C/`

Result: 3 separate state directories, gates can't see each other's state

---

## 3. What will break?

### Tests that will NEED UPDATE:
- `test_fresh_run_id_each_workflow()`
  - Currently: Manually sets `BaseGate._audit_logger = None` between workflows
  - **FIX NEEDED**: Clear `.run_session` marker file between workflows instead

- `test_no_run_id_reuse_from_state()`
  - This test is correct - we should NOT reuse from state
  - **NO CHANGE NEEDED** - session marker is different from state

### Code that will IMPROVE (currently broken):
- All quality gates will now share same run_id within a workflow session
- StateManager will find previous steps' state (currently failing)
- Audit trail will accumulate correctly (currently splitting into multiple files)

---

## 4. Migration path

### Backward Compatibility:
✅ **No breaking changes to old data**
- Existing state directories remain untouched
- Old audit files remain readable
- No migration of existing files needed

### New Behavior:
1. **Session Marker**: Store current run_id in `mcp_server/state/.run_session`
   - Format: Plain text file containing run_id + timestamp
   - Example: `2026-01-08T03:52:14.892869Z|2026-01-08T03:52:14`

2. **Session Reuse Logic** (in `BaseGate.get_audit_logger()`):
   ```python
   if .run_session exists and is recent (< 5 minutes):
       run_id = read from .run_session
       audit_logger = AuditLogger(run_id=run_id)
   else:
       audit_logger = AuditLogger()  # Fresh run_id
       save run_id to .run_session
   ```

3. **Session Cleanup**: Clear `.run_session` when:
   - Step 10 completes (workflow done)
   - 5 minutes elapse (session timeout)
   - User starts new workflow explicitly

### Pattern Reuse:
This is IDENTICAL to the existing pattern in `audit-trail-writer.py`:
- `.audit_session` marker tracks current audit filename
- Reused across MCP tool calls in same workflow
- Cleared after Step 10

---

## 5. Implementation Plan

### Phase 1: Add Session Marker Support (New Methods)
**File**: `mcp_server/tools/gates/base_gate.py`

```python
@classmethod
def _get_session_run_id(cls) -> Optional[str]:
    """Get run_id from session marker if active."""
    session_file = Path(__file__).parent.parent.parent.parent / "mcp_server" / "state" / ".run_session"
    if not session_file.exists():
        return None

    try:
        content = session_file.read_text().strip()
        run_id, timestamp_str = content.split('|')

        # Check if session is recent (< 5 minutes)
        from datetime import datetime, timezone, timedelta
        timestamp = datetime.fromisoformat(timestamp_str)
        now = datetime.now(timezone.utc)
        if (now - timestamp) > timedelta(minutes=5):
            # Session expired
            session_file.unlink()
            return None

        return run_id
    except Exception:
        return None

@classmethod
def _save_session_run_id(cls, run_id: str) -> None:
    """Save run_id to session marker."""
    from datetime import datetime, timezone
    session_file = Path(__file__).parent.parent.parent.parent / "mcp_server" / "state" / ".run_session"
    session_file.parent.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).isoformat()
    session_file.write_text(f"{run_id}|{timestamp}")

@classmethod
def _clear_session_marker(cls) -> None:
    """Clear session marker (called after Step 10)."""
    session_file = Path(__file__).parent.parent.parent.parent / "mcp_server" / "state" / ".run_session"
    if session_file.exists():
        session_file.unlink()
```

**Impact**: ✅ No breaking changes - these are NEW methods

### Phase 2: Update get_audit_logger() to Use Session
**File**: `mcp_server/tools/gates/base_gate.py` (Lines 74-94)

```python
@classmethod
def get_audit_logger(cls) -> "AuditLogger":
    """Get the audit logger, reusing run_id from session if active."""
    if cls._audit_logger is None:
        from utils.audit_logger import AuditLogger

        # DEF-052 FIX: Reuse run_id from session if active
        session_run_id = cls._get_session_run_id()
        if session_run_id:
            cls._audit_logger = AuditLogger(run_id=session_run_id)
        else:
            cls._audit_logger = AuditLogger()  # Fresh run_id
            cls._save_session_run_id(cls._audit_logger.run_id)

    return cls._audit_logger
```

**Impact**: ⚠️ Behavior change - same workflow now shares run_id

### Phase 3: Update qg_save_run to Clear Session (Step 10)
**File**: `mcp_server/tools/gates/qg_save_run.py`

After successful POST validation, add:
```python
# DEF-052: Clear session marker (workflow complete)
cls._clear_session_marker()
```

**Impact**: ✅ No breaking changes - cleans up session after workflow

### Phase 4: Update Tests
**File**: `mcp_server/_dev_tests/test_production_fixes.py`

1. `test_fresh_run_id_each_workflow()`:
   ```python
   # OLD:
   BaseGate._audit_logger = None  # Simulate new workflow

   # NEW:
   BaseGate._clear_session_marker()  # Simulate new workflow
   BaseGate._audit_logger = None
   ```

2. Add new test: `test_session_marker_reuses_run_id()`:
   ```python
   def test_session_marker_reuses_run_id(self):
       """Verify same workflow session reuses run_id across MCP calls."""
       # Simulate first MCP call (Step 1)
       logger_1 = BaseGate.get_audit_logger()
       run_id_1 = logger_1.run_id

       # Simulate second MCP call (Step 2) - new Python process
       BaseGate._audit_logger = None  # Class variable reset
       logger_2 = BaseGate.get_audit_logger()
       run_id_2 = logger_2.run_id

       # Should reuse same run_id from session
       assert run_id_1 == run_id_2, "Same workflow should reuse run_id"
   ```

**Impact**: ⚠️ Test updates required

---

## 6. Risk Assessment

### Low Risk ✅:
- New methods don't affect existing code
- Session marker pattern already proven in audit-trail-writer.py
- Old state files remain untouched
- No database migrations needed

### Medium Risk ⚠️:
- Tests need updates (but clear fix path)
- 5-minute timeout might be too short/long (can adjust)

### Mitigations:
- Implement in Task 22.2 (already in E2E test phase)
- Run full E2E test after fix
- Verify all gates share same run_id
- Check that separate workflows get different run_ids

---

## 7. Verification Checklist

After implementing fix:
- [ ] qg_preflight, qg_user_input, qg_ai_processing share same run_id
- [ ] All 3 steps save to SAME state directory
- [ ] Single audit file accumulates all steps
- [ ] qg_test_scenarios PRE validation finds Step 3 state
- [ ] Tests pass with updated session marker logic
- [ ] Manual test: Start new workflow → different run_id
- [ ] .run_session cleared after Step 10

---

## 8. Decision

**Recommendation**: ✅ PROCEED WITH FIX

**Rationale**:
1. Current behavior is BROKEN (gates can't find previous state)
2. Fix follows proven pattern (audit-trail-writer session marker)
3. No data migration needed
4. Test updates are straightforward
5. Low risk of breaking existing functionality

**Next Step**: Implement DEF-052 fix following Phase 1-4 plan above
