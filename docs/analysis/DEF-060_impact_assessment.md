# DEF-060 Impact Assessment

**Defect:** Test data infrastructure not auto-created based on Step 1 config
**Fix Approach:** Two-phase scaffolding via Protocols + Smart Gates (NEEDS_RETRY pattern)
**Date:** 2026-01-15

---

## Changes Being Made

### File 1: `mcp_server/tools/gates/qg_preflight.py`
**Change:** Add Phase 1 scaffolding - create shared test data infrastructure (Step 1 POST)

**New Logic:**
```python
def _check_test_data_infrastructure(cls, credential_strategy: str, test_data_location: str) -> Optional[Dict[str, Any]]:
    """
    Phase 1: Check/create shared test data files (no workflow name needed).

    Returns:
        None if infrastructure exists
        NEEDS_RETRY dict with scaffolding instructions if missing
    """
    missing = []

    # Check tests/data/ directory exists
    if not Path("tests/data").exists():
        missing.append({
            "type": "directory",
            "path": "tests/data",
            "reason": "Root directory for shared test data"
        })

    # Check credential file based on strategy
    if credential_strategy in ["static", "dynamic"]:
        cred_file = Path("tests/data/test_users.json")
        if not cred_file.exists():
            missing.append({
                "type": "file",
                "path": "tests/data/test_users.json",
                "template": '{\\n  "default_user": {\\n    "username": "",\\n    "password": "",\\n    "email": ""\\n  }\\n}',
                "reason": "Credential storage for static/dynamic strategies"
            })

    if missing:
        return {
            "status": "NEEDS_RETRY",
            "fix_applied": "test_data_infrastructure_scaffolded",
            "error": "Missing test data infrastructure",
            "message": "Create the following files/directories based on Step 1 config:",
            "scaffolding_needed": missing
        }

    return None
```

**Integration Point (in validate() method):**
```python
# After validating credential_strategy and test_data_location
infrastructure_check = cls._check_test_data_infrastructure(
    credential_strategy=input_data.get("credential_strategy"),
    test_data_location=input_data.get("test_data_location")
)

if infrastructure_check:
    return infrastructure_check  # NEEDS_RETRY - AI creates files, retries

# Continue with state save if infrastructure valid
```

### File 2: `mcp_server/tools/gates/qg_save_run.py`
**Change:** Add Phase 2 scaffolding - create workflow-specific directories (Step 10 PRE)

**New Logic:**
```python
def _check_workflow_test_data_directories(cls, workflow: str, test_data_location: str) -> Optional[Dict[str, Any]]:
    """
    Phase 2: Check/create workflow-specific test data directories.
    Requires workflow name from Step 2 state.

    Args:
        workflow: Workflow name from Step 2 (e.g., "auth", "parabank9")
        test_data_location: Strategy from Step 1 ("shared", "workflow", "both")

    Returns:
        None if directories exist
        NEEDS_RETRY dict with scaffolding instructions if missing
    """
    missing = []

    if test_data_location in ["workflow", "both"]:
        workflow_data_dir = Path(f"tests/{workflow}/data")
        if not workflow_data_dir.exists():
            missing.append({
                "type": "directory",
                "path": f"tests/{workflow}/data",
                "reason": f"Workflow-specific test data for {workflow}"
            })

    if missing:
        return {
            "status": "NEEDS_RETRY",
            "fix_applied": "workflow_directories_scaffolded",
            "error": "Missing workflow-specific test data directories",
            "message": f"Create test data directories for workflow '{workflow}':",
            "scaffolding_needed": missing
        }

    return None
```

**Integration Point (PRE validation before file save):**
```python
# Read Step 1 and Step 2 state
step1_data = state_manager.get_step(1)
step2_data = state_manager.get_step(2)

workflow = step2_data.get("workflow")
test_data_location = step1_data.get("test_data_location")

# Check workflow directories
directory_check = cls._check_workflow_test_data_directories(
    workflow=workflow,
    test_data_location=test_data_location
)

if directory_check:
    return directory_check  # NEEDS_RETRY - AI creates directories, retries

# Continue with file save if directories valid
```

---

## 1. Who Calls This Code?

### `qg_preflight` (Step 1 Gate)

**Direct Callers:**
- `mcp_server/server.py` - MCP tool registration (line ~90)
- Called by AI via MCP protocol when executing Step 1

**Indirect Dependencies:**
- All downstream steps (Steps 2-11) depend on Step 1 passing
- Tests that read credentials from `tests/data/test_users.json`
- conftest.py `test_users` fixture

**Test Files:**
- `mcp_server/_dev_tests/test_gates/test_qg_preflight.py` (existing unit tests)
- Will need new tests for scaffolding logic

### `qg_save_run` (Step 10 Gate)

**Direct Callers:**
- AI orchestration (not a registered MCP tool - internal gate)
- Called during Step 9 before saving generated files

**Indirect Dependencies:**
- Tests that read workflow-specific data from `tests/{workflow}/data/`
- Test execution (Step 10) needs directories to exist

**Test Files:**
- No existing test file for qg_save_run
- Will need new test file: `test_qg_save_run.py`

---

## 2. What Depends on Current Behavior?

### Current Behavior (Manual Scaffolding)

**User Manual Workflow:**
1. Answer Step 1 questions (credential_strategy, test_data_location)
2. System does NOT create files/directories
3. Test generation completes (Steps 2-9)
4. Test execution fails with "file not found"
5. User manually creates:
   ```bash
   mkdir -p tests/data
   mkdir -p tests/{workflow}/data
   echo '{"default_user": {"username": "", "password": ""}}' > tests/data/test_users.json
   ```
6. Re-run test

**Current Dependencies:**
- No code currently depends on automatic scaffolding (doesn't exist)
- Manual intervention is expected workaround
- Tests fail gracefully with clear error messages

### New Behavior (Auto-Scaffolding)

**Automated Workflow:**
1. Answer Step 1 questions → Gate scaffolds shared infrastructure immediately
2. Steps 2-9 execute normally
3. Step 10 PRE → Gate scaffolds workflow-specific directories
4. Test execution succeeds without manual intervention

**New Dependencies:**
- AI must handle NEEDS_RETRY responses and create files/directories
- State management must be available (already is)
- File system permissions (already handled by Write tool)

---

## 3. What Will Break?

### Tests

**Unit Tests (`test_qg_preflight.py`):**
- ⚠️ **POSSIBLE BREAK** - Existing tests don't expect NEEDS_RETRY response
- Need to add new test cases for scaffolding logic
- Existing tests verify state save structure (should still pass)

**New Tests Required:**
```python
# test_qg_preflight.py
def test_returns_needs_retry_when_test_data_missing():
    """Verify NEEDS_RETRY returned when tests/data/ doesn't exist."""

def test_creates_credential_file_for_static_strategy():
    """Verify credential file scaffolding for static strategy."""

def test_no_credential_file_for_self_contained():
    """Verify no file created for self-contained strategy."""

# test_qg_save_run.py (NEW FILE)
def test_returns_needs_retry_when_workflow_directory_missing():
    """Verify NEEDS_RETRY when tests/{workflow}/data/ doesn't exist."""

def test_creates_workflow_directory_for_workflow_strategy():
    """Verify directory scaffolding for workflow-specific data."""
```

### Production Workflows

**Existing Workflows (parabank9, parabank10):**
- ✅ **NO BREAK** - Directories already exist manually
- New workflows will benefit from auto-scaffolding
- Backward compatible: if directories exist, no action taken

**AI Orchestration:**
- ⚠️ **AI MUST HANDLE NEEDS_RETRY** - New response pattern
- AI must create files/directories when instructed
- AI must retry gate after scaffolding

---

## 4. Migration Path

### Existing State Files

**Old State Files (before fix):**
- Location: `tests/_state/<run_id>/step_01.json`
- Schema: Already has `credential_strategy` and `test_data_location`
- **Action:** NO MIGRATION NEEDED
  - Old state files already have required fields
  - New logic reads same fields

### Existing Test Data Files

**Manual Files (already created by users):**
- `tests/data/test_users.json` (if exists)
- `tests/{workflow}/data/` (if exists)
- **Action:** NO MIGRATION NEEDED
  - Scaffolding logic checks if files exist first
  - If exists, returns None (no NEEDS_RETRY)
  - Only creates missing files/directories

### AI Protocol Update

**Required Change:**
- Update Step 1 protocol (`.claude/skills/qa-management-layer/references/step-01.md`)
- Add instructions for handling NEEDS_RETRY response
- Document scaffolding template format

**Example Protocol Update:**
```markdown
## Handling NEEDS_RETRY Response

If qg_preflight returns `status: "NEEDS_RETRY"`:

1. Read `scaffolding_needed` array
2. For each item:
   - If `type: "directory"` → Create directory with `mkdir -p`
   - If `type: "file"` → Create file with `template` content using Write tool
3. Retry gate call after scaffolding complete

**Example:**
```json
{
  "status": "NEEDS_RETRY",
  "scaffolding_needed": [
    {
      "type": "directory",
      "path": "tests/data",
      "reason": "Root directory for shared test data"
    },
    {
      "type": "file",
      "path": "tests/data/test_users.json",
      "template": "{\n  \"default_user\": {...}\n}",
      "reason": "Credential storage"
    }
  ]
}
```
```

---

## 5. Backward Compatibility

### ✅ Compatible Changes

1. **Idempotent Scaffolding:** Checks if files/directories exist before creating
2. **State Schema:** No changes to Step 1 or Step 2 state structure
3. **Existing Files:** Manual files preserved, not overwritten
4. **Graceful Degradation:** If scaffolding fails, existing error messages still work

### ⚠️ Breaking Changes (Controlled)

1. **New Response Pattern:**
   - Old: Gate returns PASS or FAIL
   - New: Gate can return NEEDS_RETRY (AI must handle)
   - Impact: AI protocol must be updated

2. **Test Assertions:**
   - Old: Tests don't expect NEEDS_RETRY
   - New: Tests must verify NEEDS_RETRY logic
   - Impact: Requires new test cases

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| AI doesn't handle NEEDS_RETRY | **HIGH** | High | Update Step 1 protocol with explicit instructions |
| Scaffolding creates wrong paths | **MEDIUM** | Medium | Add path validation tests |
| File system permissions error | **LOW** | Medium | Graceful error handling + clear error message |
| Existing workflows break | **LOW** | Low | Idempotent checks (no-op if files exist) |
| Template JSON malformed | **LOW** | Medium | Validate JSON templates in tests |

---

## 7. Testing Strategy

### Pre-Implementation Tests (TDD)

1. **Scaffolding Logic (qg_preflight):**
   ```python
   def test_returns_needs_retry_when_tests_data_missing():
       """P0: Verify NEEDS_RETRY when tests/data/ doesn't exist."""
       input_data = {
           "credential_strategy": "static",
           "test_data_location": "shared"
       }
       # Mock Path.exists() to return False
       result = QGPreflight.validate(input_data)
       assert result["status"] == "NEEDS_RETRY"
       assert "tests/data" in result["scaffolding_needed"][0]["path"]

   def test_creates_credential_file_template():
       """P0: Verify credential file template for static strategy."""
       # Verify template JSON is valid
       # Verify template has expected fields (username, password, email)

   def test_no_scaffolding_for_self_contained():
       """P1: Verify no credential file for self-contained strategy."""
       input_data = {
           "credential_strategy": "self-contained",
           "test_data_location": "shared"
       }
       # Mock Path.exists() to return False for tests/data/
       result = QGPreflight.validate(input_data)
       # Should only scaffold directory, NOT credential file
       assert all("test_users.json" not in item["path"]
                  for item in result.get("scaffolding_needed", []))

   def test_no_needs_retry_when_files_exist():
       """P0: Verify no NEEDS_RETRY when infrastructure already exists."""
       input_data = {
           "credential_strategy": "static",
           "test_data_location": "shared"
       }
       # Mock Path.exists() to return True
       result = QGPreflight.validate(input_data)
       assert result["status"] == "pass"
   ```

2. **Workflow Directory Scaffolding (qg_save_run):**
   ```python
   def test_returns_needs_retry_when_workflow_directory_missing():
       """P0: Verify NEEDS_RETRY when tests/{workflow}/data/ doesn't exist."""
       # Mock state with workflow="parabank9", test_data_location="workflow"
       # Mock Path.exists() to return False
       result = QGSaveRun._check_workflow_test_data_directories("parabank9", "workflow")
       assert result["status"] == "NEEDS_RETRY"
       assert "tests/parabank9/data" in result["scaffolding_needed"][0]["path"]

   def test_no_scaffolding_for_shared_only():
       """P1: Verify no workflow directories for test_data_location='shared'."""
       result = QGSaveRun._check_workflow_test_data_directories("auth", "shared")
       assert result is None  # No scaffolding needed

   def test_creates_both_for_both_strategy():
       """P1: Verify workflow directory created for test_data_location='both'."""
       # Verify workflow directory scaffolded when strategy is "both"
   ```

### Post-Implementation Tests

1. **E2E Test (Fresh Project):**
   - Start with empty `tests/` directory
   - Answer Step 1: credential_strategy="static", test_data_location="both"
   - Verify `tests/data/test_users.json` created automatically
   - Continue through Step 9
   - Verify `tests/{workflow}/data/` created automatically at Step 10
   - Test executes without manual intervention

2. **E2E Test (Existing Files):**
   - Start with existing `tests/data/test_users.json`
   - Answer Step 1: credential_strategy="static"
   - Verify existing file NOT overwritten
   - Verify no errors

3. **AI Protocol Test:**
   - Mock NEEDS_RETRY response
   - Verify AI creates files as instructed
   - Verify AI retries gate after scaffolding
   - Verify gate passes on retry

---

## 8. Rollback Plan

**If Fix Causes Issues:**

1. **Immediate Rollback:**
   ```bash
   git revert <commit-hash>
   ```

2. **Fallback Behavior:**
   - System reverts to manual scaffolding
   - User creates files/directories manually (existing workaround)
   - Tests continue to work with manual intervention

3. **File Cleanup:**
   - No cleanup needed - scaffolded files are valid test data
   - User can delete auto-created files if needed

---

## 9. Two-Phase Design Rationale

### Why Two Phases?

**Phase 1 (Step 1)**: Scaffold shared infrastructure
- **Can execute:** Tests directory structure known (`tests/data/`)
- **Cannot execute:** Workflow-specific directories (don't know workflow name yet)
- **Blocking:** Must succeed before Step 2 (credentials needed for tests)

**Phase 2 (Step 10)**: Scaffold workflow-specific directories
- **Can execute:** Workflow name available from Step 2 state
- **Cannot execute:** Cannot happen earlier (workflow name doesn't exist until Step 2)
- **Blocking:** Must succeed before test execution (tests read workflow-specific data)

### Alternative Considered: Single-Phase at Step 10

**Why Rejected:**
- Step 10 is too late for shared credential file
- Tests in Steps 2-9 may reference credential data
- Better to fail fast at Step 1 if infrastructure can't be created

---

## 10. Approval Checklist

- [ ] Impact assessment reviewed
- [ ] Test strategy approved
- [ ] Backward compatibility verified
- [ ] Rollback plan documented
- [ ] Two-phase design rationale clear
- [ ] Protocol update requirements identified
- [ ] Ready for implementation

---

**Assessment Completed:** 2026-01-15
**Next Step:** Implement DEF-060 fix with TDD approach (two phases)
