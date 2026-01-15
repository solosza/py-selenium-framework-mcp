# DEF-063: Dynamic Credential Field Resolution

**Status:** Design Phase
**Pattern:** Protocols + Smart Gates (NEEDS_RETRY with scaffolding)
**Date:** 2026-01-15

---

## Problem

**Current Behavior:**
- Tool 5 (generate_role) hardcodes credential field names (`email`, `password`)
- Breaks for applications using different field names (e.g., ParaBank uses `username`)
- Role constructor fails when test_users.json has different fields

**Example Failure:**
```python
# Generated Role
class RegisteredUser:
    def __init__(self, web_interface, user_data, base_url):
        self.email = user_data.get('email')      # Hardcoded!
        self.password = user_data.get('password')

# test_users.json
{"john_demo": {"username": "john", "password": "demo"}}

# Result: self.email = None (field not found!)
```

---

## Root Cause

1. Tool 5 assumes all apps use `email`/`password`
2. No detection of actual field names during workflow
3. No validation in qg_role POST to catch field name mismatches

---

## Solution: Protocols + Smart Gates

### Detection Point: Step 8 POST (qg_role)

When validating generated Role code, gate should:

1. **Extract** hardcoded credential field names from Role constructor
2. **Compare** against test_users.json (from Step 1 state)
3. **Detect** mismatch (e.g., Role expects 'email', file has 'username')
4. **Return** NEEDS_RETRY with dynamic pattern template

### NEEDS_RETRY Response Format

```json
{
  "status": "NEEDS_RETRY",
  "fix_applied": "dynamic_credential_fields",
  "error": "Role expects 'email' but test_users.json has 'username'",
  "message": "Make Role use dynamic credential field resolution:",
  "scaffolding_needed": [{
    "type": "code_pattern",
    "location": "Role constructor (__init__)",
    "template": "self.user_data = user_data\nself.username = user_data.get('username') or user_data.get('email') or user_data.get('user_id')\nself.password = user_data.get('password') or user_data.get('pin')",
    "reason": "Flexible credential field resolution for any application"
  }]
}
```

### AI Handling Instructions

**When qg_role POST returns NEEDS_RETRY:**

1. Read `scaffolding_needed[0].template`
2. Replace hardcoded field names in Role constructor with dynamic pattern
3. Retry qg_role POST with updated code
4. Verify gate returns `status: "pass"`

**NO human approval needed** - this is a code quality fix, not a configuration decision.

---

## Implementation Phases

### Phase 1: Detection Logic (qg_role POST)

**File:** `mcp_server/tools/gates/qg_role.py`

**Add to POST validation:**

```python
@classmethod
def _check_credential_field_hardcoding(cls, code: str) -> Optional[Dict[str, Any]]:
    """
    Check if Role constructor hardcodes credential field names.

    Returns NEEDS_RETRY if hardcoded fields detected.
    """
    # Parse code to find __init__ method
    # Look for lines like: self.email = user_data.get('email')
    # Check if field names match test_users.json

    hardcoded_fields = []
    if "self.email = user_data.get('email')" in code:
        hardcoded_fields.append("email")
    if "self.password = user_data.get('password')" in code and "'username'" not in code:
        hardcoded_fields.append("password (no fallback)")

    if hardcoded_fields:
        return {
            "status": "NEEDS_RETRY",
            "fix_applied": "dynamic_credential_fields",
            "error": f"Role hardcodes credential fields: {', '.join(hardcoded_fields)}",
            "message": "Make Role use dynamic credential field resolution:",
            "scaffolding_needed": [{
                "type": "code_pattern",
                "location": "Role constructor (__init__)",
                "template": cls._get_dynamic_credential_pattern(),
                "reason": "Flexible credential field resolution for any application"
            }]
        }

    return None

@classmethod
def _get_dynamic_credential_pattern(cls) -> str:
    """Get template for dynamic credential field resolution."""
    return """# Dynamic credential resolution - works with any field names
self.user_data = user_data
self.username = (
    user_data.get('username') or
    user_data.get('email') or
    user_data.get('user_id') or
    user_data.get('login')
)
self.password = (
    user_data.get('password') or
    user_data.get('pin') or
    user_data.get('secret')
)

# Validate credentials present
if not self.username or not self.password:
    raise ValueError(f"RegisteredUser requires username and password. Got: {list(user_data.keys())}")"""
```

**Integration in validate():**

```python
@classmethod
def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
    # ... existing validation ...

    # Check for hardcoded credential fields
    credential_check = cls._check_credential_field_hardcoding(code)
    if credential_check:
        return credential_check  # NEEDS_RETRY

    # ... rest of validation ...
```

---

### Phase 2: Protocol Update (Step 8 Reference)

**File:** `.claude/skills/qa-management-layer/references/step-08.md`

**Add Section H:**

```markdown
## H. Dynamic Credential Field Resolution (DEF-063)

**Purpose:** Auto-detect credential field name mismatches and provide dynamic resolution pattern.

**Detection Logic:**

Gate checks if Role hardcodes credential field names:
- Looks for `self.email = user_data.get('email')` pattern
- Compares against test_users.json field names
- Returns NEEDS_RETRY if mismatch detected

**Scaffolding Response Format:**

When hardcoded fields detected, gate returns `status: "NEEDS_RETRY"`:

```json
{
  "status": "NEEDS_RETRY",
  "fix_applied": "dynamic_credential_fields",
  "error": "Role expects 'email' but test_users.json has 'username'",
  "message": "Make Role use dynamic credential field resolution:",
  "scaffolding_needed": [{
    "type": "code_pattern",
    "location": "Role constructor (__init__)",
    "template": "<dynamic pattern>",
    "reason": "Flexible credential field resolution"
  }]
}
```

**AI Handling Instructions:**

When gate returns `NEEDS_RETRY`:
1. Read `scaffolding_needed[0].template`
2. Replace hardcoded field assignments in Role `__init__` with dynamic pattern
3. Retry qg_role POST with updated code
4. Verify gate returns `status: "pass"`

**NO human approval needed** - code quality fix, not config decision.

**Idempotent:** If Role already uses dynamic pattern, gate returns `pass`.
```

---

## Comparison with DEF-060 and DEF-062

| Aspect | DEF-060 | DEF-062 | DEF-063 |
|--------|---------|---------|---------|
| **Scaffolds** | Test data files | Environment config | Code pattern |
| **Risk Level** | Low | Medium | Low |
| **Human Approval** | NO | YES | NO |
| **Reasoning** | Boilerplate files | Config decision | Code quality fix |
| **Pattern** | NEEDS_RETRY → AI scaffolds | NEEDS_RETRY → User approves → AI scaffolds | NEEDS_RETRY → AI refactors code |

---

## Testing Strategy

### Unit Tests (qg_role)

**File:** `mcp_server/_dev_tests/test_gates/test_qg_role.py`

Add test class:

```python
class TestDynamicCredentialFields:
    """Test credential field hardcoding detection (DEF-063)."""

    @pytest.mark.unit
    @pytest.mark.qg_role
    def test_detects_hardcoded_email(self):
        """Verify gate detects hardcoded 'email' field."""
        code = """
class RegisteredUser:
    def __init__(self, web_interface, user_data, base_url):
        self.email = user_data.get('email')
        self.password = user_data.get('password')
"""
        result = QGRole.validate({"mode": "POST", "code": code, "metadata": {...}})

        assert result["status"] == "NEEDS_RETRY"
        assert "email" in result["error"]
        assert "dynamic_credential_fields" == result["fix_applied"]

    @pytest.mark.unit
    @pytest.mark.qg_role
    def test_passes_dynamic_pattern(self):
        """Verify gate passes when dynamic pattern used."""
        code = """
class RegisteredUser:
    def __init__(self, web_interface, user_data, base_url):
        self.user_data = user_data
        self.username = user_data.get('username') or user_data.get('email')
        self.password = user_data.get('password')
"""
        result = QGRole.validate({"mode": "POST", "code": code, "metadata": {...}})

        assert result["status"] == "pass"
```

---

## Benefits

✓ **Application-agnostic** - Works with any credential field names
✓ **Auto-healing** - AI fixes the code without human intervention
✓ **Consistent pattern** - Uses same NEEDS_RETRY pattern as DEF-060/DEF-062
✓ **Clear separation** - Code quality fix (auto) vs config decision (human approval)
✓ **Future-proof** - Handles new field name variations automatically

---

## Rollout Plan

1. **Phase 1:** Implement detection logic in qg_role.py (Task X.1)
2. **Phase 2:** Add unit tests (Task X.2)
3. **Phase 3:** Update Step 8 protocol documentation (Task X.3)
4. **Phase 4:** Run integration tests (Task X.4)
5. **Phase 5:** Update Tool 5 to generate dynamic pattern by default (Task X.5 - optional optimization)

---

## Success Criteria

- [ ] Gate detects hardcoded credential fields
- [ ] NEEDS_RETRY response includes dynamic pattern
- [ ] AI successfully refactors Role code
- [ ] Retry passes validation
- [ ] ParaBank test (username/password) works
- [ ] E-commerce test (email/password) works
- [ ] No regressions in existing tests

---

**Design Complete:** 2026-01-15
**Next:** Create task list and implement
