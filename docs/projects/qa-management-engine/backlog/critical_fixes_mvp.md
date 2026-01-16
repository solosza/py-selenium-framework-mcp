# Critical Fixes (MVP v1.0)

**Status:** Backlog
**Target Version:** v1.0 (MVP)
**Total Effort:** <2 hours
**Priority:** High (blockers for release)

---

## Overview

Two remaining critical fixes needed before MVP v1.0 release. Both are quick fixes (<1 hour each) that prevent production issues.

---

## DEF-060: Test Data Auto-Creation

**Priority:** Medium
**Effort:** <1 hour
**Status:** Open

### Problem

When test requires test data, AI must manually create directory structure. No automated creation based on Step 1 config.

### Impact

- Manual directory creation required
- Error-prone (user forgets to create directory)
- Inconsistent structure across workflows

### Proposed Fix

Step 1 (qg_preflight) POST validation creates directory structure based on test_data_location config.

**Implementation:**
```python
# mcp_server/tools/gates/qg_preflight.py
def _create_test_data_directories(self, config: dict):
    """Create test data directories based on config."""
    if config["test_data_location"] == "shared":
        os.makedirs("tests/data", exist_ok=True)

    elif config["test_data_location"] == "workflow":
        workflow = config["workflow"]
        os.makedirs(f"tests/{workflow}/data", exist_ok=True)

    elif config["test_data_location"] == "both":
        os.makedirs("tests/data", exist_ok=True)
        workflow = config["workflow"]
        os.makedirs(f"tests/{workflow}/data", exist_ok=True)
```

### Acceptance Criteria

- ✅ Step 1 POST validation creates data directories
- ✅ Supports all 3 strategies (shared, workflow, both)
- ✅ Uses os.makedirs with exist_ok=True (idempotent)
- ✅ No errors if directories already exist

---

## DEF-062: Environment Flag Auto-Detection

**Priority:** High
**Effort:** <1 hour
**Status:** Open

### Problem

When URL domain doesn't match environment config, test times out after 5 minutes. No proactive detection or warning.

**Example:**
- User provides URL: `https://parabank.parasoft.com/parabank`
- Environment config has `local` and `staging`, but not `parabank`
- Test runs without `--env` flag → defaults to `local` → timeout

### Impact

- 5-minute timeout wastes user time
- Confusing error (timeout, not environment mismatch)
- Requires manual config editing

### Proposed Fix

Add URL domain → environment mapping in Step 2 (qg_user_input). If domain not in config, suggest adding it via HITL confirmation.

**Implementation:**
```python
# mcp_server/tools/gates/qg_user_input.py
def _check_environment_config(self, url: str) -> dict:
    """Check if URL domain exists in environment_config.json."""
    domain = self._extract_domain(url)
    env_config = load_json("tests/config/environment_config.json")

    # Check if domain exists in any environment
    for env_id, env_data in env_config.items():
        if domain in env_data.get("base_url", ""):
            return {"status": "PASS", "env_id": env_id}

    # Domain not found → suggest adding
    return {
        "status": "NEEDS_CONFIRMATION",
        "message": f"Domain '{domain}' not found in environment_config.json",
        "suggested_env_id": self._suggest_env_id(domain),
        "proposed_config": {
            "base_url": url,
            "timeout": 30
        }
    }
```

**HITL Confirmation:**
```
Domain 'parabank.parasoft.com' not found in environment_config.json.

Would you like to add it?

1. Yes, add as 'parabank' environment
2. Let me edit the name first
3. No, I'll add it manually

Proposed config:
{
  "parabank": {
    "base_url": "https://parabank.parasoft.com/parabank",
    "timeout": 30
  }
}
```

### Acceptance Criteria

- ✅ Step 2 PRE validation checks URL against environment config
- ✅ If domain not found, suggests adding via HITL
- ✅ HITL allows: approve, modify name, reject
- ✅ If approved, writes to environment_config.json
- ✅ Provides clear error if user rejects (not timeout)

### Dependencies

- Requires Modular HITL System (`.business/roadmap/backlog/modular_hitl_system.md`)
- OR temporary HITL implementation in qg_user_input for MVP

---

## Implementation Plan

### Option 1: Quick Fix (MVP v1.0)

**DEF-060:**
1. Add directory creation logic to qg_preflight POST validation
2. Test with all 3 strategies
3. Verify idempotent (no errors if dirs exist)

**DEF-062:**
1. Add temporary HITL to qg_user_input (Step 2)
2. Check domain, prompt user, write to config
3. Refactor to modular HITL in v1.2

**Effort:** 2 hours total
**Target:** MVP v1.0 release

---

### Option 2: Wait for Modular HITL (v1.2)

**DEF-060:**
- Implement now (no HITL needed)

**DEF-062:**
- Wait for modular HITL system (v1.2)
- Implement using standard HITL interface

**Effort:** DEF-060: 1 hour now, DEF-062: 2 hours in v1.2
**Target:** DEF-060 in v1.0, DEF-062 in v1.2

---

## Recommendation

**Fix DEF-060 now** (1 hour, no dependencies)
**Fix DEF-062 now with temp HITL** (1 hour, refactor in v1.2)

**Rationale:**
- DEF-062 causes 5-minute timeouts (bad UX)
- Temporary HITL is 20 lines of code
- Can refactor to modular HITL in v1.2 without breaking changes

---

## Next Steps

1. Implement DEF-060 (test data auto-creation)
2. Implement DEF-062 (environment detection + temp HITL)
3. Test with parabank URL (verify no timeout)
4. Mark both defects RESOLVED
5. Update DEFECT_LOG.md with resolution details
