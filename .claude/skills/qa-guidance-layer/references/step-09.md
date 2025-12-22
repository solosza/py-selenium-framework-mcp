# Step 9: Tool 6 - Generate Test Runner

**Purpose:** Generate pytest test code that calls Role workflow and asserts via POM state methods.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 9 - Generate Test Runner (Tool 6) |
| **Dependencies** | Step 8 complete (role_code, role_metadata exist), Step 6 (pom_metadata for assertions) |
| **Input** | `role_metadata` from Step 8, `pom_metadata` from Step 6, `test_scenarios` from Step 4 |
| **Output** | `test_code`, `test_metadata` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | None (unless AI fails 3 times, then user decides resolution) |
| **AI** | Injects actual parameter values (DD-17), fixes file paths (DD-16), validates imports (DD-18), ensures assertions use POM state methods (DD-15) |
| **Tool** | `qg_test_runner` validates input/output, `generate_test_runner` generates test code, operation saves state on SUCCESS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 8 complete (role_metadata exist in state)
- READ pom_metadata from Step 6 (for state method assertions)
- READ test_scenarios from Step 4 (for test structure)

ACTION:
- CALL qg_test_runner (PRE-VALIDATE)
- CALL generate_test_runner (OPERATION)
- AI POST-PROCESSING (before POST-VALIDATE):
  - DD-16: Override file paths to tests/test1/, tests/test2/, etc.
  - DD-17: Inject actual parameter values from requirement
  - DD-18: Validate import paths exist
  - DD-15: Ensure assertions use POM state methods from metadata
- CALL qg_test_runner (POST-VALIDATE)

VALIDATE (DD-25 - Skeleton Code Quality Gate):
- POST: Verify NO skeleton code (no placeholder tests)
- POST: Verify AAA pattern (Arrange, Act, Assert)
- POST: Verify assertions use POM state methods (not return values)
- POST: Verify correct imports

RETRY:
- If POST-VALIDATE fails: AI fixes the code (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_test_runner` |
| **Quality Gate** | `qg_test_runner` |
| **Gate Mode** | PRE+POST (validates metadata before, code quality after) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `test_code`, `test_metadata` (file path, test names, assertions) |
| **Who Saves** | Operation tool (`generate_test_runner`) |
| **When Saved** | On operation SUCCESS (after POST-VALIDATE passes) |
| **State Schema** | See below |

```json
{
  "step": 9,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "test_code": "@pytest.mark.auth\ndef test_valid_login(web_interface, config, test_data):\n    user = RegisteredUser(...)\n    user.login_and_browse()\n    assert login_page.is_logged_in()",
    "test_metadata": {
      "file_path": "tests/auth/test_login.py",
      "test_names": ["test_valid_login"],
      "assertions": ["is_logged_in", "is_logout_visible"],
      "imports": ["RegisteredUser", "LoginPage"]
    }
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-15 (POM state assertions), DD-16 (file paths), DD-17 (parameter injection), DD-18 (import validation), DD-19 (tool import), DD-25 (no skeleton), DD-26 (data contracts) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 10 until test code complete** |

**PRE-Validation Checks:**

| Check | Rule |
|-------|------|
| `role_metadata` | Present from Step 8 |
| `pom_metadata` | Present from Step 6 (for state methods) |
| `test_scenarios` | Present from Step 4 |

**POST-Validation Checks (DD-25):**

| Check | Rule |
|-------|------|
| AAA Pattern | Arrange (setup), Act (one role call), Assert (POM state checks) |
| Assertions | Use POM state methods (e.g., `is_logged_in()`), NOT return values |
| Imports | All imports resolve to existing files |
| Parameters | Actual values injected (no placeholders like `"category_name_value"`) |
| File path | Correct tests/{workflow}/ location |
| No skeleton | No placeholder tests, no `pass`, no `# TODO` |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| Missing Role metadata | Go back to Step 8 |
| Placeholder parameters | AI injects actual values from requirement |
| Wrong assertions | AI fixes to use POM state methods |
| Bad imports | AI fixes import paths |
| Skeleton code | AI completes the test |
| After 3 total failures | STOP → REPORT → USER DECIDES |

**Known Defects:**
- Tool sometimes generates placeholder parameter values (DD-17 violation)
- Tool sometimes uses return value assertions (DD-15 violation)

**Error Message Template (After 3 Failures):**

```
"I've attempted 3 times and cannot generate complete test code.

Issues found:
[list what's wrong - placeholders, bad assertions, bad imports]

How should we proceed?
1. Re-generate Role - Go back to Step 8
2. Manual test - You provide the code
3. Abort workflow - Stop and log issue"
```

---

## AI Post-Processing Examples

**DD-17 (Parameter Value Injection):**
```python
# Tool generates:
user.browse_category("category_name_value")

# AI must replace with actual value from requirement:
user.browse_category("Women")  # From "browse products in Women category"
```

**DD-15 (POM State Assertions):**
```python
# WRONG - assert on return value:
result = user.login()
assert result is True

# CORRECT - assert via POM state method:
user.login()
assert login_page.is_logged_in()
```

**DD-16 (File Path Override):**
```python
# Tool generates:
"tests/test_login.py"

# AI overrides to:
"tests/auth/test_login.py"  # Workflow-specific folder
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 9: TOOL 6 - GENERATE TEST RUNNER                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 8 complete?      │
                         └────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  YES     │            │  NO      │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
              ┌─────────────────────┐     ┌─────────────────┐
              │  READ:              │     │  BLOCKED        │
              │  - role_metadata    │     │  Go to Step 8   │
              │  - pom_metadata     │     └─────────────────┘
              │  - test_scenarios   │
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_test_runner (PRE-VALIDATE)                                 │
│  - Validates all metadata present                                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  PASS    │            │  FAIL    │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
              ┌─────────────────────┐     ┌─────────────────┐
              │  OPERATION:         │     │  Go back        │
              │  generate_test_     │     │  (missing data) │
              │  runner             │     └─────────────────┘
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  AI POST-PROCESSING │
              │  - DD-16: Fix paths │
              │  - DD-17: Inject    │
              │    actual values    │
              │  - DD-18: Validate  │
              │    imports          │
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_test_runner (POST-VALIDATE)                                │
│  - DD-25: No skeleton code                                                  │
│  - DD-15: POM state assertions                                              │
│  - AAA pattern enforced                                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  PASS    │            │  FAIL    │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
              ┌─────────────────────┐  ┌─────────────────────┐
              │  STATE SAVED        │  │  AI FIXES CODE      │
              │  (by operation)     │  │  (max 3 attempts)   │
              └─────────────────────┘  └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 10 │
              └─────────────────────┘
```

---

## H. Tool Chain Data Contracts (DD-26)

**Input Contract (from Steps 6 and 8):**

Tool 6 requires BOTH role_metadata AND pom_metadata:

```python
# CORRECT - Pass both metadata objects:
arguments = {
    "test_name": "test_valid_login",
    "workflow": "auth",
    "role_metadata": tool_5_result["metadata"],  # From Tool 5
    "pom_metadata": tool_3_result["metadata"],   # From Tool 3 (for assertions)
    "scenario": {  # Optional, from Tool 1
        "description": "Verify user can login with valid credentials"
    }
}
```

**WRONG - Missing metadata produces generic template:**
```python
# WRONG - legacy format produces placeholder test:
arguments = {
    "test_name": "test_valid_login",
    "workflow": "auth",
    "role": "RegisteredUser"  # No methods known = placeholder
}
```

**Output Contract (Tool 6 provides for Step 10):**

```json
{
  "code": "@pytest.mark.auth\ndef test_valid_login(web_interface, config):\n    user = RegisteredUser(...)\n    user.login()\n    assert login_page.is_logged_in()",
  "metadata": {
    "file_path": "tests/auth/test_login.py",
    "test_methods": ["test_valid_login"],
    "role_used": "RegisteredUser",
    "page_used": "LoginPage",
    "assertions": ["is_logged_in"]
  }
}
```

**CRITICAL:** AI must apply DD-16 (override file path), DD-17 (inject actual values), DD-18 (validate imports) before saving.

---

## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-09-01 | test_scenarios from Step 4 required; scenario.description optional for docstrings | Tool uses description for docstring only; actual test structure from role_metadata | `validate_pre()` |
| IC-09-02 | Placeholder tests with `pass`/`TODO` are FAIL (DD-25) | Generator fallback produces skeleton when metadata incomplete | `validate_post()` |
| IC-09-03 | At least 1 role method call required; no max limit; multi-role allowed | Complex e2e scenarios (admin+user, buyer+seller) are legitimate | `validate_post()` |
| IC-09-04 | Assertions must use POM state methods (DD-15), not return values | Framework architecture: roles return None, tests assert via POM | `validate_post()` |
| IC-09-05 | @autologger.automation_logger("Test") required on test methods | Framework pattern consistency | `validate_post()` |

**Date Added:** 2025-12-21
**Task Reference:** Task 12.0 (qg_test_runner)

---

*Next: Step 10 - Save & Run*
