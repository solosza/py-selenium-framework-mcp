# Pre-Execution Validation

**Status:** Idea
**Created:** 2026-01-14
**Target Version:** v1.1 (Post-MVP)
**Effort:** 2-3 hours
**Impact:** High (prevents timeouts, wrong environments)

---

## Context

Extracted from HITL function enhancements during Parabank10 validation. Currently, validation happens during execution (Step 11), causing timeouts and wasted time.

---

## Problem

**Current State:**
- Environment validation happens at execution time (Step 11)
- Test data validation happens when test runs
- Credential validation happens when test accesses data
- Mismatches cause timeouts (5 minutes) or runtime failures

**Example Issues:**
- URL `https://parabank.parasoft.com` without `--env parabank` → 5-minute timeout
- Missing `test_users.json` → test fails at login step
- Missing credential keys → KeyError at runtime

### Impact

- 5-minute timeouts waste user time
- Runtime failures require re-running entire workflow
- Poor user experience (fail fast would be better)

---

## Proposed Solution

**Vision:** Validate BEFORE execution (Steps 2 and 10), fail fast with clear errors

### Features

1. **Environment validation (Step 2):**
   - Check URL domain matches selected environment
   - Warn if no `--env` flag provided
   - Suggest correct environment based on URL

2. **Test data validation (Step 10):**
   - Verify required files exist BEFORE execution
   - Check file format (valid JSON, required keys)
   - Provide clear error if missing

3. **Credential validation (Step 10):**
   - Confirm test_users.json has required keys
   - Validate credential structure (email, password)
   - Warn if using static credentials without data

---

## Implementation

### Step 2 (qg_user_input) PRE Validation

```python
# mcp_server/tools/gates/qg_user_input.py
def _validate_environment(self, url: str, env_flag: str) -> dict:
    """Validate URL matches environment config."""
    domain = self._extract_domain(url)
    env_config = load_json("tests/config/environment_config.json")

    # No --env flag provided
    if not env_flag:
        return {
            "status": "WARNING",
            "message": f"No --env flag provided. URL domain: {domain}",
            "suggested_env": self._suggest_env_from_domain(domain, env_config),
            "recommendation": "Add --env flag to prevent timeout"
        }

    # Check if env_flag matches URL domain
    env_base_url = env_config.get(env_flag, {}).get("base_url", "")
    if domain not in env_base_url:
        return {
            "status": "MISMATCH",
            "message": f"URL domain '{domain}' does not match --env {env_flag}",
            "expected_url": env_base_url,
            "recommendation": f"Use --env with correct environment"
        }

    return {"status": "PASS"}
```

### Step 10 (qg_save_run) PRE Validation

```python
# mcp_server/tools/gates/qg_save_run.py
def _validate_test_data(self, test_code: str, workflow: str) -> dict:
    """Validate test data files exist."""
    # Extract required data files from test code
    required_files = self._extract_data_files(test_code)

    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)

    if missing_files:
        return {
            "status": "FAIL",
            "message": f"Missing test data files: {missing_files}",
            "recommendation": "Create files or adjust test code"
        }

    return {"status": "PASS"}

def _validate_credentials(self, credential_strategy: str) -> dict:
    """Validate credential files exist and are valid."""
    if credential_strategy == "static":
        if not os.path.exists("tests/data/test_users.json"):
            return {
                "status": "FAIL",
                "message": "test_users.json not found",
                "recommendation": "Create file or use dynamic/self-contained strategy"
            }

        # Validate JSON structure
        users = load_json("tests/data/test_users.json")
        for user_id, user_data in users.items():
            if "email" not in user_data or "password" not in user_data:
                return {
                    "status": "FAIL",
                    "message": f"User '{user_id}' missing email or password",
                    "recommendation": "Add required keys to test_users.json"
                }

    return {"status": "PASS"}
```

---

## Value

**Benefits:**
- ✅ Fail fast (catch issues before 5-minute timeout)
- ✅ Clear errors (specific, actionable messages)
- ✅ Better UX (no wasted time on preventable failures)
- ✅ Reduced debugging (issues caught early)

**Success Metric:** Zero timeouts due to wrong environment

---

## User Experience

**Before:**
```
Step 11: Running test...
[5 minutes pass]
Error: Timeout (300s)
```

**After:**
```
Step 2: Validating environment...
⚠️  WARNING: URL domain 'parabank.parasoft.com' does not match environment 'local'

Suggested fix: Add --env parabank
Or update environment_config.json

Continue anyway? (y/n)
```

---

## Implementation Plan

1. Add environment validation to qg_user_input (Step 2 PRE)
2. Add test data validation to qg_save_run (Step 10 PRE)
3. Add credential validation to qg_save_run (Step 10 PRE)
4. Test with mismatched environment (verify early warning)
5. Test with missing test data (verify early failure)
6. Update step-02.md and step-10.md protocols

**Effort:** 2-3 hours

---

## Configuration

**Environment Variables:**
```bash
# Validation strictness
VALIDATE_ENVIRONMENT=true     # Enforce environment matching
VALIDATE_TEST_DATA=true       # Enforce test data existence
VALIDATE_CREDENTIALS=true     # Enforce credential structure

# Fail vs Warn
VALIDATION_MODE=strict        # strict (fail), warn (warning only)
```

---

## Next Steps

1. Move to backlog when ready to implement
2. Implement in v1.1 (post-MVP quick win)
3. Test with real-world URL mismatches
4. Update protocol documentation
