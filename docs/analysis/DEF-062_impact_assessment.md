# DEF-062 Impact Assessment

**Defect:** Environment flag not auto-detected - test uses wrong URL
**Fix Approach:** Auto-detect environment from URL in Step 2, save to state, use in Step 10
**Date:** 2026-01-14

---

## Changes Being Made

### File 1: `mcp_server/tools/gates/qg_user_input.py`
**Change:** Add environment detection from URL, save `detected_env_id` to state

**New Logic:**
```python
def _detect_environment_from_url(url: str) -> str:
    """Match URL domain against environment_config.json entries."""
    config_path = Path("framework/resources/config/environment_config.json")
    with open(config_path, 'r') as f:
        environments = json.load(f)

    # Check each environment's URL against provided URL
    for env_id, config in environments.items():
        env_url = config.get('url', '')
        if extract_domain(url) == extract_domain(env_url):
            return env_id

    return "DEFAULT"  # Fallback

# In validate() method:
detected_env_id = cls._detect_environment_from_url(url)
state_manager.save(step=2, data={
    # ... existing fields ...
    "detected_env_id": detected_env_id  # NEW
})
```

### File 2: `mcp_server/tools/operations/run_test.py`
**Change:** Read `detected_env_id` from state instead of defaulting to "dev"

**Modified Logic:**
```python
async def run_test_async(arguments: dict) -> str:
    test_path = arguments.get("test_path")
    env = arguments.get("env")  # Changed: no default here

    # NEW: If env not provided, read from state
    if env is None:
        try:
            audit_logger = AuditLogger()
            state_manager = StateManager(run_id=audit_logger.run_id)
            step2_data = state_manager.load(step=2)
            env = step2_data.get("detected_env_id", "DEFAULT")
        except Exception:
            env = "DEFAULT"  # Fallback if state read fails

    # Rest unchanged
    result = execute_test(test_path=test_path, env=env, ...)
```

---

## 1. Who Calls This Code?

### `qg_user_input` (Step 2 Gate)

**Direct Callers:**
- `mcp_server/server.py` - MCP tool registration (line 100)
  - Called by AI via MCP protocol when executing Step 2

**Indirect Dependencies:**
- All downstream steps (Steps 3-11) depend on Step 2 state
- Step 3 (AI Processing) reads persona, URL, role_name, workflow
- Step 10 (Test Execution) will now read detected_env_id

**Test Files:**
- `mcp_server/_dev_tests/test_gates/test_qg_user_input.py` (20 unit tests)
- `mcp_server/_dev_tests/test_gates/test_integration.py` (integration tests)

### `run_test` (Test Execution Operation)

**Direct Callers:**
- `mcp_server/server.py` - MCP tool registration (line 79)
  - Called by AI via MCP protocol when executing Step 10
- `mcp_server/tools/gates/qg_execution.py` - Receives test_result from run_test
- `mcp_server/tools/gates/qg_workflow_complete.py` - Receives test_result from run_test

**Test Files:**
- `mcp_server/_dev_tests/test_operations/test_run_test.py` (8 unit tests)
- `mcp_server/_dev_tests/test_gates/test_step11_integration.py` (integration tests)

---

## 2. What Depends on Current Behavior?

### Step 2 State Schema

**Current Schema (from `.claude/skills/qa-management-layer/references/step-02.md`):**
```json
{
  "step": 2,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "persona": "registered user",
    "URL": "http://automationpractice.pl/index.php",
    "role_name": "RegisteredUser",
    "workflow": "auth",
    "raw_requirement": "..."
  }
}
```

**New Schema (after fix):**
```json
{
  "step": 2,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "persona": "registered user",
    "URL": "http://automationpractice.pl/index.php",
    "role_name": "RegisteredUser",
    "workflow": "auth",
    "raw_requirement": "...",
    "detected_env_id": "DEFAULT"  ← NEW FIELD
  }
}
```

**Impact:** ADDITIVE - no breaking changes
- Existing code reading Step 2 state won't break (new field is optional)
- New code (run_test) will benefit from new field

### run_test Default Parameter

**Current Behavior:**
- `execute_test(env="dev")` - function default
- `run_test_async(arguments.get("env", "dev"))` - MCP entry point default
- Result: Tests use "dev" environment when env not specified
- **PROBLEM:** "dev" doesn't exist in environment_config.json!

**Dependencies on "dev" Default:**
- **None found** - all production workflows call run_test without env parameter
- No tests explicitly depend on "dev" value
- Actual behavior: conftest.py raises ValueError when env="dev" not found

**New Behavior:**
- Read `detected_env_id` from Step 2 state
- Fallback to "DEFAULT" if state read fails or field missing
- Result: Tests use correct environment based on URL provided in Step 2

---

## 3. What Will Break?

### Tests

**Unit Tests (`test_qg_user_input.py`):**
- ❌ **WILL BREAK** - State schema changed
- 20 tests verify state save structure
- Need to update assertions to expect `detected_env_id` field

**Unit Tests (`test_run_test.py`):**
- ✅ **NO BREAK** - Tests mock subprocess, don't read state
- Tests provide explicit env parameter or use default
- Default change from "dev" → state-read won't affect mocked tests

**Integration Tests:**
- ⚠️ **POSSIBLE BREAK** - If integration tests check Step 2 state structure
- Need to verify `test_integration.py` and `test_step11_integration.py`

### Production Workflows

**Existing Workflows (parabank9, parabank10):**
- ✅ **NO BREAK** - State files are per-run, old runs won't be re-read
- New runs will have new state schema
- Backward compatible: if `detected_env_id` missing, fallback to "DEFAULT"

**Manual --env Flag:**
- ✅ **NO BREAK** - Explicit `--env` parameter still takes precedence
- User can override auto-detection: `run_test(test_path="...", env="parabank")`

### Environment Config

**No Changes to `environment_config.json`:**
- ✅ **NO BREAK** - Only reading existing config, not modifying
- Detection logic matches domain strings
- Fallback to "DEFAULT" if no match found

---

## 4. Migration Path

### State Files

**Old State Files (before fix):**
- Location: `tests/_state/<run_id>/step_02.json`
- Schema: Missing `detected_env_id` field
- **Action:** NO MIGRATION NEEDED
  - Old state files are historical, won't be re-read
  - New runs create new state files with new schema

**New State Files (after fix):**
- Same location, new schema includes `detected_env_id`
- Backward compatible read: `state.get("detected_env_id", "DEFAULT")`

### Tests

**Migration Required:**
- `test_qg_user_input.py` - Update 20 unit tests
  - Add `detected_env_id` to expected state data
  - Verify environment detection logic with new tests

**New Tests Required:**
- Test environment detection from various URLs
- Test fallback to "DEFAULT" for unknown domains
- Test state read fallback in run_test when field missing

### Documentation

**Files to Update:**
- `.claude/skills/qa-management-layer/references/step-02.md` - Update state schema example
- `FRAMEWORK.md` - Document environment auto-detection behavior
- `docs/reference/DEFECT_LOG.md` - Mark DEF-062 as RESOLVED with implementation details

---

## 5. Backward Compatibility

### ✅ Compatible Changes

1. **State Schema Change:** Additive field, old code won't break
2. **run_test Parameter:** Explicit env parameter still works
3. **Environment Config:** Read-only, no modifications
4. **Fallback Logic:** Graceful degradation to "DEFAULT"

### ⚠️ Breaking Changes (Controlled)

1. **Default Parameter Change:**
   - Old: `env="dev"` (invalid, would cause error)
   - New: `env=None` → read from state → fallback to "DEFAULT"
   - Impact: Actually FIXES existing broken behavior

2. **Test Assertions:**
   - Old: Tests expect 5 fields in Step 2 state
   - New: Tests expect 6 fields (added `detected_env_id`)
   - Impact: Requires test updates, but caught by CI

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Unit tests fail due to state schema change | **HIGH** | Low | Update tests in same commit |
| Integration tests fail | **MEDIUM** | Medium | Run full test suite before merge |
| Old workflows break | **LOW** | Low | Backward compatible read with fallback |
| Environment detection incorrect | **MEDIUM** | High | Add comprehensive detection tests |
| State read fails at runtime | **LOW** | Low | Graceful fallback to "DEFAULT" |

---

## 7. Testing Strategy

### Pre-Implementation Tests (TDD)

1. **Environment Detection Logic:**
   ```python
   def test_detect_environment_parabank():
       url = "https://parabank.parasoft.com/parabank/index.htm"
       env_id = QGUserInput._detect_environment_from_url(url)
       assert env_id == "parabank"

   def test_detect_environment_default():
       url = "http://www.automationpractice.pl/index.php"
       env_id = QGUserInput._detect_environment_from_url(url)
       assert env_id == "DEFAULT"

   def test_detect_environment_unknown_fallback():
       url = "https://unknown-domain.com/page"
       env_id = QGUserInput._detect_environment_from_url(url)
       assert env_id == "DEFAULT"
   ```

2. **State Save Validation:**
   - Update existing `test_qg_user_input.py` tests
   - Verify `detected_env_id` in saved state

3. **State Read in run_test:**
   - Mock StateManager in run_test tests
   - Verify env read from state when not provided
   - Verify fallback to "DEFAULT" on read failure

### Post-Implementation Tests

1. **E2E Test (ParaBank):**
   - User provides ParaBank URL
   - Step 2 detects env_id = "parabank"
   - Step 10 uses parabank environment
   - Test runs without timeout

2. **E2E Test (Default):**
   - User provides automationpractice.pl URL
   - Step 2 detects env_id = "DEFAULT"
   - Step 10 uses DEFAULT environment
   - Test runs successfully

3. **Manual Override Test:**
   - User provides ParaBank URL (detected as "parabank")
   - User manually calls run_test with env="DEFAULT"
   - Explicit parameter takes precedence
   - Test uses DEFAULT environment

---

## 8. Rollback Plan

**If Fix Causes Issues:**

1. **Immediate Rollback:**
   ```bash
   git revert <commit-hash>
   ```

2. **Fallback Behavior:**
   - run_test will use explicit env parameter if provided
   - User can manually specify `--env` flag as workaround

3. **State Cleanup:**
   - No cleanup needed - old state files remain valid
   - New runs create fresh state files

---

## 9. Approval Checklist

- [ ] Impact assessment reviewed
- [ ] Test strategy approved
- [ ] Backward compatibility verified
- [ ] Rollback plan documented
- [ ] Ready for implementation

---

**Assessment Completed:** 2026-01-14
**Next Step:** Implement DEF-062 fix with TDD approach
