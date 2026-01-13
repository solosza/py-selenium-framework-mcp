# DEF-052A Impact Assessment

**Fix:** Clear `_audit_logger` class variable in `qg_preflight` (Step 1)
**Date:** 2026-01-08
**Severity:** HIGH (blocks E2E workflows)

---

## 1. Who Calls This Code?

### Direct Callers of `QGPreflight.validate()`

| Caller | Location | Purpose |
|--------|----------|---------|
| **MCP Tool** | `mcp_server/server.py:90` | Primary production entry point |
| **Unit Tests** | `test_qg_preflight.py` | 21 test calls - validation logic |
| **Integration Tests** | `test_integration.py:391, 887, 951` | 3 calls - workflow orchestration |
| **Context Reconstruction** | `test_context_reconstruction.py:42` | 1 call - resume testing |

**Total:** 1 production caller + 25 test callers

---

## 2. What Depends on Current Behavior?

### Current Behavior

`QGPreflight.validate()`:
1. Validates `credential_strategy` and `test_data_location`
2. Calls `BaseGate.get_audit_logger()` → may get STALE logger from previous workflow
3. Saves state to `StateManager(run_id=logger.run_id)`

### Dependencies

| Component | Dependency | Impact of Change |
|-----------|------------|------------------|
| **StateManager** | Uses run_id from audit logger | No impact - will use fresh run_id |
| **MCP Server** | Calls `validate()` via tool wrapper | No impact - wrapper doesn't check logger |
| **Tests** | Call `validate()` directly | No impact - tests already clear state manually |
| **Audit Trail** | Uses run_id for file naming | No impact - new workflow = new run_id (expected) |

---

## 3. What Will Break?

### Breaking Changes: **NONE**

#### Tests That Manually Clear `_audit_logger`

`test_production_fixes.py:244`:
```python
# DEF-052: Clear session marker (simulates new workflow)
BaseGate._clear_session_marker()
BaseGate._audit_logger = None  # ← Tests already do this manually
```

**Impact:** Our fix makes this **automatic** in production code. Tests will still work.

#### Integration Tests

`test_integration.py` tests call `QGPreflight.validate()` and check `result["status"]`. They don't:
- Access `_audit_logger` directly
- Depend on logger persisting across calls
- Check run_id values

**Impact:** No breaking changes.

---

## 4. Migration Path

### Old Behavior (Buggy)

```python
# Workflow 1
QGPreflight.validate(...)  # Creates _audit_logger with run_id ABC

# ... MCP server keeps running ...

# Workflow 2
QGPreflight.validate(...)  # ❌ REUSES old _audit_logger with run_id ABC
                           # ❌ Session marker ignored
                           # ❌ State written to wrong directory
```

### New Behavior (Fixed)

```python
# Workflow 1
QGPreflight.validate(...)
  ↓
  cls._audit_logger = None          # ← NEW: Clear stale logger
  cls._clear_session_marker()       # ← NEW: Clear stale session
  # ... creates fresh logger with run_id ABC

# ... MCP server keeps running ...

# Workflow 2
QGPreflight.validate(...)
  ↓
  cls._audit_logger = None          # ← NEW: Clear old logger from Workflow 1
  cls._clear_session_marker()       # ← NEW: Clear old session
  # ... creates fresh logger with run_id XYZ  ✅ Correct behavior
```

### Data Migration

**No data migration needed.**

- Old state files remain in their directories
- New workflows create new run_id directories
- No backward compatibility issues

### Rollback Plan

If fix causes issues:
1. Revert `qg_preflight.py` changes
2. Restart MCP server between workflows (manual workaround)

---

## 5. Implementation Plan

### Phase 1: Add Clear Logic

```python
# qg_preflight.py validate() method
@classmethod
def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate pre-flight configuration.

    DEF-052A FIX: Clear stale class variable from previous workflow
    to ensure fresh run_id for each new workflow.
    """
    # Clear stale session from previous workflow
    cls._audit_logger = None
    cls._clear_session_marker()

    # ... rest of validation logic (unchanged)
```

### Phase 2: Verify Tests Pass

Run existing tests:
```bash
pytest mcp_server/_dev_tests/test_gates/test_qg_preflight.py -v
pytest mcp_server/_dev_tests/test_gates/test_integration.py -v
pytest mcp_server/_dev_tests/test_production_fixes.py -v
```

Expected: All tests pass (no breaking changes)

### Phase 3: Manual E2E Test

1. Start MCP server
2. Run Workflow 1 → verify fresh run_id
3. Run Workflow 2 (without restarting MCP) → verify NEW run_id
4. Verify both workflows have separate state directories

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Tests break due to assumption about logger persistence | Low | Medium | Tests already manually clear `_audit_logger` |
| Production workflows get unexpected run_id | Low | Low | Fresh run_id per workflow is EXPECTED behavior |
| Performance impact from clearing logger | Very Low | Very Low | Clearing class variable is O(1) operation |
| Rollback needed | Very Low | Low | Simple revert, no data migration |

**Overall Risk:** **LOW**

---

## 7. Verification Checklist

After implementing fix:

- [ ] All unit tests pass (`test_qg_preflight.py`)
- [ ] All integration tests pass (`test_integration.py`)
- [ ] All production fix tests pass (`test_production_fixes.py`)
- [ ] Manual E2E test: Workflow 1 → Workflow 2 (no MCP restart) → separate run_ids
- [ ] Session marker timeout increased to 30 minutes
- [ ] Documentation updated (DEFECT_LOG.md, SESSION.md)

---

## 8. Recommendation

**PROCEED WITH FIX**

**Rationale:**
1. **No breaking changes** - Tests already clear `_audit_logger` manually
2. **Fixes critical bug** - Long-running MCP server reuses stale logger
3. **Low risk** - Simple change, easy rollback
4. **No data migration** - Each workflow gets fresh directory
5. **Aligns with design** - Step 1 is "start of workflow", clearing state is correct

**Next Steps:**
1. Implement fix in `qg_preflight.py`
2. Run test suite
3. Restart MCP server
4. Run full E2E test from Step 1
