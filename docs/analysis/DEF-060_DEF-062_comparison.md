# DEF-060 vs DEF-062: Protocols + Smart Gates Pattern Comparison

**Date:** 2026-01-15
**Status:** Both implemented with NEEDS_RETRY pattern

---

## Pattern Overview

Both defects use the **Protocols + Smart Gates** pattern:
1. Gate validates and detects missing infrastructure/config
2. Gate returns **NEEDS_RETRY** with scaffolding instructions
3. AI implements fix based on instructions
4. AI retries gate
5. Gate validates again and returns PASS

---

## Key Difference: Human Approval

| Aspect | DEF-060 (Test Data) | DEF-062 (Environment Config) |
|--------|---------------------|------------------------------|
| **Scaffolding Type** | Boilerplate files | Configuration decision |
| **Risk Level** | Low (empty templates) | Medium (affects test execution) |
| **Human Approval** | ❌ **NO** - Auto-scaffold | ✅ **YES** - Require approval |
| **Reasoning** | User can edit files after creation | Config decisions need user input |
| **Pattern** | NEEDS_RETRY → AI scaffolds → Retry | NEEDS_RETRY → **AI asks user** → User approves → AI scaffolds → Retry |

---

## DEF-060: Test Data Auto-Creation (NO Human Approval)

**What's Scaffolded:**
- `tests/data/` directory
- `tests/data/test_users.json` (empty template for static/dynamic strategies)

**Flow:**
```
Step 1 POST: qg_preflight validates config
    ↓
Missing test data detected
    ↓
Gate returns NEEDS_RETRY with template
    ↓
AI reads template
    ↓
AI creates directory + file (no approval needed)
    ↓
AI retries gate
    ↓
Gate returns PASS
```

**Why No Approval:**
- Boilerplate files with empty/default values
- User can edit files after creation
- Low risk - doesn't affect test execution
- Common convention (`tests/data/test_users.json`)

**Example Template:**
```json
{
  "default_user": {
    "username": "",
    "password": "",
    "email": ""
  }
}
```

---

## DEF-062: Environment Auto-Detection (YES Human Approval)

**What's Scaffolded:**
- Entry in `framework/resources/config/environment_config.json`
- Environment name derived from workflow
- Base URL from user-provided URL

**Flow:**
```
Step 2 POST: qg_user_input validates input
    ↓
Unknown environment detected
    ↓
Gate returns NEEDS_RETRY with proposed config
    ↓
AI reads proposed config
    ↓
🚨 AI USES AskUserQuestion to show proposed config
    ↓
USER APPROVES or MODIFIES
    ↓
AI adds approved config to environment_config.json
    ↓
AI retries gate
    ↓
Gate returns PASS with detected_env_id
```

**Why Human Approval:**
- Configuration decision, not boilerplate
- Affects which test environment is used
- User may want different environment name
- User may want to add additional config (timeouts, etc.)
- Higher impact on test execution

**Example Proposed Config:**
```json
{
  "auth": {
    "url": "https://new-app.example.com"
  }
}
```

**User Decision Point:**
```
"I detected a new environment that's not in the config.

Proposed environment config:
{
  "auth": {
    "url": "https://new-app.example.com"
  }
}

Add this environment to environment_config.json?"

Options:
1. Yes, add as shown (Recommended)
2. Modify environment name or URL
```

---

## Implementation Comparison

### DEF-060: Direct Scaffolding

**Step 1 Protocol (step-01.md):**
```markdown
When gate returns NEEDS_RETRY:
1. Read scaffolding_needed array
2. For each item:
   - If type: "directory" → Create with mkdir -p
   - If type: "file" → Create with template using Write tool
3. Retry gate call
4. Verify gate returns pass
```

**No human intervention - AI executes directly**

### DEF-062: Human Approval Required

**Step 2 Protocol (step-02.md):**
```markdown
When gate returns NEEDS_RETRY:
1. Read scaffolding_needed[0].template
2. Parse template to extract proposed config
3. **USE AskUserQuestion to request approval** ⚠️
4. **If user approves:**
   - Add environment to config
   - Retry gate
5. **If user wants to modify:**
   - Ask for modifications
   - Add modified config
   - Retry gate

CRITICAL: Never auto-scaffold environment config without user approval.
```

**Human approval required before scaffolding**

---

## Code-Level Implementation

### DEF-060: qg_preflight.py

**Returns NEEDS_RETRY with file template:**
```python
if missing:
    return {
        "status": "NEEDS_RETRY",
        "fix_applied": "test_data_infrastructure_scaffolded",
        "error": "Missing test data infrastructure",
        "message": "Create the following files/directories based on Step 1 config:",
        "scaffolding_needed": [{
            "type": "file",
            "path": "tests/data/test_users.json",
            "template": '{\n  "default_user": {...}\n}',
            "reason": "Credential storage"
        }]
    }
```

**AI Action:** Read template → Create file → Retry (NO approval)

### DEF-062: qg_user_input.py

**Returns NEEDS_RETRY with config template:**
```python
return {
    "needs_retry": {
        "status": "NEEDS_RETRY",
        "fix_applied": "environment_added_to_config",
        "error": f"Unknown environment: {url_domain}",
        "message": f"Add environment for '{workflow}' workflow to environment_config.json:",
        "scaffolding_needed": [{
            "type": "config_entry",
            "path": "framework/resources/config/environment_config.json",
            "template": json.dumps({workflow: {"url": base_url}}, indent=2),
            "reason": f"Environment config for {workflow} workflow at {base_url}"
        }]
    }
}
```

**AI Action:** Read template → **AskUserQuestion** → Wait for approval → Add to config → Retry

---

## When to Use Each Pattern

### Auto-Scaffold (No Approval) - Like DEF-060

Use when:
- ✅ Scaffolding creates **boilerplate/template files**
- ✅ Default values are safe and conventional
- ✅ User can easily edit files after creation
- ✅ Low impact on system behavior
- ✅ Standard conventions (e.g., `tests/data/test_users.json`)

**Examples:**
- Test data files (with empty/placeholder values)
- Directory structures (`tests/data/`, `tests/{workflow}/data/`)
- Empty configuration placeholders

### Human Approval Required - Like DEF-062

Use when:
- ⚠️ Scaffolding creates **configuration affecting behavior**
- ⚠️ Decisions have execution impact (which environment to use)
- ⚠️ User may want to customize values before creation
- ⚠️ Medium-to-high risk if wrong
- ⚠️ Non-standard naming or values

**Examples:**
- Environment configuration (affects test execution)
- Database connection strings
- API endpoints
- Feature flags
- Service URLs

---

## Future: Full HITL System

**Current State:** Manual `AskUserQuestion` for DEF-062 (temporary stopgap)

**Future State:** Full HITL (Human-in-the-Loop) system
- Unified approval mechanism for all config decisions
- Approval history tracking
- Confidence scoring
- Learn from user preferences
- Batch approval for multiple decisions

**Migration Path:**
- DEF-060: No change needed (auto-scaffold is appropriate)
- DEF-062: Replace `AskUserQuestion` with HITL approval API
- Other config decisions: Use HITL pattern from DEF-062

---

## Testing Status

| Defect | Tests | Status |
|--------|-------|--------|
| DEF-060 | 26 tests (20 existing + 6 new) | ✅ ALL PASSING |
| DEF-062 | 29 tests (24 existing + 5 new) | ✅ ALL PASSING |

**Both defects implemented using TDD (Test-Driven Development)**

---

## Summary

**DEF-060 and DEF-062 both use Protocols + Smart Gates pattern, but differ in human involvement:**

| Feature | DEF-060 | DEF-062 |
|---------|---------|---------|
| Pattern | NEEDS_RETRY | NEEDS_RETRY |
| Scaffolds | Test data files | Environment config |
| Human Approval | NO | YES (temporary) |
| Rationale | Low-risk boilerplate | Config decision |
| Future | No change | Migrate to full HITL |

**Design Philosophy:**
- **Auto-scaffold** when safe and conventional (DEF-060)
- **Human approval** for configuration decisions (DEF-062)
- **Consistent pattern** across both (NEEDS_RETRY + scaffolding instructions)
- **Clear separation** between boilerplate vs configuration

---

**Comparison Created:** 2026-01-15
**Both Implementations:** Complete and ready for production testing
**Branch:** feature/def062-environment-auto-detection
