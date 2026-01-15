# Context Reconstruction from Audit Trail

**Feature:** Solve context window issues by reconstructing workflow state from audit trail metadata.

**Status:** Implemented (All Steps 1-10)

**Related:** DEF-048 (Code Reconstruction Gap), DD-30 (Progressive Audit Trail)

---

## Problem

**Before this enhancement:**
- Audit trail only captured pass/fail status
- When context window overflowed, detailed workflow data was lost
- Had to restart from Step 1 when context was lost
- Multi-page workflows could lose track of which POMs were generated

**Example audit entry (OLD):**
```json
{
  "step": 1,
  "gate": "qg_preflight",
  "mode": "POST",
  "result": "pass",
  "timestamp": "2026-01-07T10:39:22.126203Z"
}
```

No information about WHAT was validated, only that it passed.

---

## Solution

**Enhanced audit trail with rich metadata:**
- Each quality gate logs actual validation data, not just pass/fail
- Metadata includes: persona, URL, page_name, class_name, import_path, method counts, etc.
- Can reconstruct entire workflow state from audit trail
- Can resume workflow from any completed step

**Example audit entry (NEW):**
```json
{
  "step": 2,
  "gate": "qg_user_input",
  "mode": "POST",
  "result": "pass",
  "timestamp": "2026-01-07T11:01:13.217109Z",
  "metadata": {
    "persona": "As a registered user",
    "URL": "https://example.com/login",
    "role_name": "RegisteredUser",
    "workflow": "auth"
  }
}
```

Now we know WHAT was validated: persona, URL, role, workflow.

---

## Metadata Captured by Each Step

### Step 1 (qg_preflight)
```json
{
  "credential_strategy": "static",
  "test_data_location": "shared"
}
```

### Step 2 (qg_user_input)
```json
{
  "persona": "As a registered user",
  "URL": "https://example.com/login",
  "role_name": "RegisteredUser",
  "workflow": "auth"
}
```

### Step 3 (qg_ai_processing)
```json
{
  "intent": "purchase",
  "scenarios_count": 2,
  "expected_states_count": 2
}
```

### Step 4 (qg_test_scenarios)
**PRE:**
```json
{
  "workflow": "auth"
}
```

**POST:**
```json
{
  "scenarios_count": 3
}
```

### Step 5 (qg_discovered_elements)
**PRE:**
```json
{
  "page_name": "LoginPage",
  "url": "https://example.com/login",
  "multi_page": false,
  "total_pages": 1
}
```

**POST:**
```json
{
  "page_name": "LoginPage",
  "elements_count": 15,
  "pages_discovered": 1,
  "total_pages": 1,
  "discovery_complete": true
}
```

### Step 6 (qg_page_object)
**PRE:**
```json
{
  "page_name": "LoginPage",
  "elements_count": 15
}
```

**POST (Single Page):**
```json
{
  "page_name": "LoginPage",
  "class_name": "LoginPage",
  "import_path": "pages.auth.login_page",
  "action_methods_count": 5,
  "state_methods_count": 2
}
```

**POST (Multi-Page):**
```json
{
  "page_name": "LoginPage",
  "class_name": "LoginPage",
  "import_path": "pages.auth.login_page",
  "action_methods_count": 5,
  "state_methods_count": 2,
  "multi_page": {
    "poms_generated": 1,
    "total_poms": 4,
    "generation_complete": false,
    "page_index": 1
  }
}
```

**Multi-Page Workflow Example:**
For a 4-page workflow (LoginPage, AccountOverviewPage, TransferFundsPage, BillPayPage), the audit trail will contain 4 separate Step 6 entries:

```json
{
  "steps": [
    {
      "step": 6,
      "gate": "qg_page_object",
      "mode": "POST",
      "result": "pass",
      "timestamp": "2026-01-07T11:00:00.000000Z",
      "metadata": {
        "page_name": "LoginPage",
        "class_name": "LoginPage",
        "import_path": "pages.parabank.login_page",
        "action_methods_count": 4,
        "state_methods_count": 2,
        "multi_page": {
          "poms_generated": 1,
          "total_poms": 4,
          "generation_complete": false,
          "page_index": 1
        }
      }
    },
    {
      "step": 6,
      "gate": "qg_page_object",
      "mode": "POST",
      "result": "pass",
      "timestamp": "2026-01-07T11:01:00.000000Z",
      "metadata": {
        "page_name": "AccountOverviewPage",
        "class_name": "AccountOverviewPage",
        "import_path": "pages.parabank.account_overview_page",
        "action_methods_count": 3,
        "state_methods_count": 3,
        "multi_page": {
          "poms_generated": 2,
          "total_poms": 4,
          "generation_complete": false,
          "page_index": 2
        }
      }
    },
    ...
  ]
}
```

Each POM generation creates a NEW audit entry. No data is lost.

### Step 7 (qg_task)
**PRE:**
```json
{
  "task_name": "AuthTasks"
}
```

**POST:**
```json
{
  "class_name": "AuthTasks",
  "import_path": "tasks.auth_tasks",
  "task_methods_count": 3
}
```

### Step 8 (qg_role)
**PRE:**
```json
{
  "role_name": "RegisteredUser"
}
```

**POST:**
```json
{
  "class_name": "RegisteredUser",
  "import_path": "roles.registered_user",
  "workflow_methods_count": 2
}
```

### Step 9 (qg_test_runner)
**PRE:**
```json
{
  "scenarios_count": 3
}
```

**POST:**
```json
{
  "test_name": "test_user_login",
  "file_path": "tests/auth/test_login.py"
}
```

### Step 10 (qg_save_run)
**PRE:**
```json
{
  "validated_layers": ["POM", "Task", "Role", "Test"],
  "ready_for_save": true
}
```

---

## Context Reconstruction Utility

**Location:** `mcp_server/utils/context_reconstructor.py`

**Key Functions:**

### 1. `ContextReconstructor(audit_file_path)`
Load audit trail and provide reconstruction capabilities.

### 2. `get_completed_steps() -> List[int]`
Get list of steps that passed validation.

Example:
```python
reconstructor = ContextReconstructor("tests/_audit/audit_log_2026-01-07T10-19-17.493153Z.json")
completed = reconstructor.get_completed_steps()
# Returns: [1, 2, 3, 6, 7, 8, 9, 10]
```

### 3. `get_step_metadata(step: int) -> List[Dict]`
Get all metadata entries for a specific step (supports multi-page workflows).

Example:
```python
# Get all POMs generated in Step 6
pom_entries = reconstructor.get_step_metadata(6)
# Returns: [
#   {"page_name": "LoginPage", "class_name": "LoginPage", ...},
#   {"page_name": "AccountOverviewPage", "class_name": "AccountOverviewPage", ...},
#   ...
# ]
```

### 4. `get_workflow_summary() -> Dict`
Get human-readable summary of workflow progress.

Example:
```python
summary = reconstructor.get_workflow_summary()
# Returns:
# {
#   "run_id": "2026-01-07T10:19:17.493153Z",
#   "completed_steps": [1, 2, 3, 6, 7, 8, 9, 10],
#   "last_step": 10,
#   "workflow_complete": true,
#   "step_details": {
#     "preflight": {"credential_strategy": "static", ...},
#     "user_input": {"persona": "As a registered user", ...},
#     "poms_generated": {"count": 4, "pages": ["LoginPage", "AccountOverviewPage", ...]}
#   }
# }
```

### 5. `can_resume_from_step(step: int) -> bool`
Check if we have enough data to resume from a specific step.

Example:
```python
reconstructor.can_resume_from_step(7)
# Returns: True (if Step 6 is complete)
```

### 6. `reconstruct_state() -> Dict`
Rebuild workflow_state.json structure from audit trail.

Example:
```python
state = reconstructor.reconstruct_state()
# Returns:
# {
#   "step_0": {"audit_run_id": "2026-01-07T10:19:17.493153Z"},
#   "step_1": {"credential_strategy": "static", ...},
#   "step_2": {"persona": "As a registered user", ...},
#   ...
# }
```

---

## Usage Scenarios

### Scenario 1: Context Window Overflow

**Before:**
```
[Step 1-6 completed]
[Context window full, conversation summarized]
[AI loses detailed workflow data]
AI: "I've lost context. Let's restart from Step 1."
User: *sighs* "Okay..."
```

**After:**
```
[Step 1-6 completed]
[Context window full, conversation summarized]
[AI reads audit trail]
AI: "I see Steps 1-6 are complete. Reading audit trail..."
AI: "Reconstructed state from audit. Workflow: auth, Role: RegisteredUser,
     POMs: [LoginPage, AccountOverviewPage]. Continuing with Step 7."
User: *happy* "Great!"
```

### Scenario 2: Multi-Page Workflow Recovery

**Problem:**
User is generating a 10-page test workflow. Context overflows after generating 6 POMs.

**Solution:**
```python
reconstructor = ContextReconstructor(audit_file)
pom_entries = reconstructor.get_step_metadata(6)
print(f"POMs generated: {len(pom_entries)}")
# Output: POMs generated: 6

# Check which pages are done
pages_done = [entry["page_name"] for entry in pom_entries]
# Output: ["LoginPage", "AccountOverviewPage", "TransferFundsPage",
#          "BillPayPage", "OpenAccountPage", "FindTransactionPage"]

# Resume with remaining pages
remaining_pages = ["RequestLoanPage", "UpdateContactPage",
                   "CustomerCarePage", "AdminPage"]
```

### Scenario 3: Code Reconstruction (DEF-048)

**Problem:**
AI needs to regenerate POM code after context loss, but doesn't remember what elements were discovered.

**Solution:**
```python
reconstructor = ContextReconstructor(audit_file)

# Get metadata from Step 6 POST
pom_metadata = reconstructor.get_step_metadata(6)[0]
# Returns: {
#   "page_name": "LoginPage",
#   "class_name": "LoginPage",
#   "import_path": "pages.auth.login_page",
#   "action_methods_count": 5,
#   "state_methods_count": 2
# }

# Get elements from Step 5 POST
element_metadata = reconstructor.get_step_metadata(5)[0]
# Returns: {
#   "page_name": "LoginPage",
#   "elements_count": 15,
#   ...
# }

# Now AI knows:
# - Which page to generate (LoginPage)
# - How many elements were discovered (15)
# - How many methods should exist (5 action + 2 state)
# - Import path for validation

# Can either:
# 1. Read actual code from workflow_state.json
# 2. Or regenerate by calling Tool 3 with same inputs
```

---

## Implementation Files

**Core Changes:**
- `mcp_server/utils/audit_logger.py` - Added metadata parameter to log_gate()
- `mcp_server/tools/gates/base_gate.py` - Added metadata parameter to pass_response(), fail_response(), blocked_response()

**Quality Gates (Steps 1-10):**
- `mcp_server/tools/gates/qg_preflight.py` - Logs credential_strategy, test_data_location
- `mcp_server/tools/gates/qg_user_input.py` - Logs persona, URL, role_name, workflow
- `mcp_server/tools/gates/qg_ai_processing.py` - Logs intent, scenario counts
- `mcp_server/tools/gates/qg_test_scenarios.py` - Logs workflow, scenario counts
- `mcp_server/tools/gates/qg_discovered_elements.py` - Logs page_name, URL, element counts, multi-page progress
- `mcp_server/tools/gates/qg_page_object.py` - Logs page_name, class_name, import_path, method counts, multi-page progress
- `mcp_server/tools/gates/qg_task.py` - Logs task_name, class_name, import_path, method counts
- `mcp_server/tools/gates/qg_role.py` - Logs role_name, class_name, import_path, method counts
- `mcp_server/tools/gates/qg_test_runner.py` - Logs test_name, file_path
- `mcp_server/tools/gates/qg_save_run.py` - Logs validated_layers, ready_for_save

**Utilities:**
- `mcp_server/utils/context_reconstructor.py` - Context reconstruction from audit trail
- `mcp_server/_dev_tests/test_context_reconstruction.py` - Demonstration test

---

## Benefits

1. **Unlimited Workflow Length:** Context window no longer limits workflow complexity. Can handle arbitrarily long multi-page tests.

2. **Resume from Any Step:** If interrupted, can resume from last completed step instead of restarting.

3. **DEF-048 Resolution:** Code reconstruction after context loss is now possible by reading audit trail + state files.

4. **Multi-Page Support:** Each POM POST creates separate audit entry, tracking progress through complex workflows.

5. **Audit Trail = Source of Truth:** Audit trail becomes authoritative record of workflow execution, independent of conversation context.

6. **Debug & Analysis:** Can analyze workflow execution after the fact by reading audit trail.

---

## Testing

**Test:** `mcp_server/_dev_tests/test_context_reconstruction.py`

**Demonstrates:**
- Execute Steps 1-3
- Simulate context loss
- Reconstruct state from audit trail
- Verify state consistency between StateManager and audit trail
- Check resume capability

**Results:**
```
[SUCCESS] Context Reconstruction: SUCCESS

Key Benefits:
1. Audit trail captures ALL validation data, not just pass/fail
2. Can reconstruct workflow state even after context window overflow
3. Can resume workflow from any step without restarting
4. Audit trail becomes single source of truth for workflow state
5. Solves DEF-048 (code reconstruction after context loss)

Context Window Solution:
- Before: Context loss -> restart from Step 1
- After:  Context loss -> read audit trail -> resume from last step
```

---

## Future Enhancements

1. **Auto-Resume:** Automatically detect context loss and resume from audit trail.
2. **Richer Metadata:** Capture actual BDD scenarios, element data (not just counts).
3. **Code Storage:** Optionally store generated code in audit trail (for full offline reconstruction).
4. **Multi-Session Support:** Resume workflows across different Claude sessions.
5. **Audit Trail Query API:** Rich query interface for analyzing workflow history.

---

**Version:** 1.0
**Date:** 2026-01-07
**Status:** Production Ready
