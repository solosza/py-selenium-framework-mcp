# Known Issues

Issues discovered during testing. Workarounds provided where available.

---

## KI-001: `run_test` MCP tool doesn't pass `--env` parameter

**Severity:** Medium
**Status:** RESOLVED
**Discovered:** 2026-01-28
**Resolved:** 2026-01-28

### Description
The `run_test` MCP tool executes pytest but doesn't pass the `--env` parameter needed to load environment configuration. This causes tests to fail or timeout because they can't find the correct base URL.

### Symptoms
- Test times out (300s default)
- Test fails with missing config error
- Browser opens but navigates to wrong URL

### Workarounds

**Option 1: Run pytest manually**
```bash
pytest tests/auth/test_login.py --env parabank --headless False -v
```

**Option 2: Instruct AI to include --env parameter**
When asking AI to run tests, specify:
> "Run the test with `--env parabank`"

AI will use bash instead of the MCP tool and include the parameter.

### Root Cause
The `run_test` tool schema in `mcp_server/server.py` didn't expose the `env` parameter, even though the implementation supported it.

### Resolution
Added `env` as a **required** parameter in the MCP tool schema (`mcp_server/server.py`).

```python
"env": {
    "type": "string",
    "description": "Environment config key (e.g., parabank, automationex1)"
},
"required": ["test_path", "env"]
```

Now `run_test` requires explicit environment specification, preventing silent failures.

---
