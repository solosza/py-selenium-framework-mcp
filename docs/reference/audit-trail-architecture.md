# Audit Trail Architecture (Task 68.0 Phase 3)

**Version:** 2.0
**Status:** Production
**Pattern:** Defense-in-Depth (In-Process + External Validation)

---

## Overview

The QA Management Engine implements a dual-layer audit system that provides both in-process logging and external validation overlay. This architecture follows the defense-in-depth principle by maintaining two independent audit trails that validate each other.

**Key Principle:** Separate concerns - in-process audit tracks workflow execution, external compliance validates independently.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         WORKFLOW EXECUTION                          │
├─────────────────────────────────────────────────────────────────────┤
│  Step 1 → Step 2 → ... → Step 11                                    │
│     ↓        ↓              ↓                                        │
│  [Gate]  [Gate]        [Gate]                                       │
└────┬────────┬──────────────┬───────────────────────────────────────┘
     │        │              │
     │        │              │
     ↓        ↓              ↓
┌────────────────────────────────────────────────────────────────────┐
│               IN-PROCESS AUDIT (Primary Logger)                    │
├────────────────────────────────────────────────────────────────────┤
│  File: tests/_audit/audit_log_{run_id}.json                        │
│                                                                     │
│  Written by: AuditLogger (in BaseGate.pass_response)               │
│  Content:                                                           │
│    • Gate results (pass/fail)                                      │
│    • Step metadata                                                  │
│    • Self-heal attempts                                             │
│    • Generated file paths                                           │
│    • Timestamps                                                     │
└────────────────────────────────────────────────────────────────────┘
                            ↓
                    ┌──────────────┐
                    │  Metadata    │ ← Links both audit systems
                    │   File       │
                    └──────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────────┐
│            COMPLIANCE FILE (External Validation Overlay)           │
├────────────────────────────────────────────────────────────────────┤
│  File: tests/_audit/audit_log_{run_id}_compliance.json             │
│                                                                     │
│  Written by: PostToolUse hook (.claude/hooks/audit-trail-writer.py)│
│  Content:                                                           │
│    • Hook observations (minimal)                                   │
│    • Gate execution confirmations                                  │
│    • Timestamps                                                     │
│    • Tool names                                                     │
└────────────────────────────────────────────────────────────────────┘
                            ↓
                    ┌──────────────┐
                    │  Validation  │
                    │  (Step 11)   │
                    └──────────────┘
```

---

## Three-File System

### 1. Metadata File (Linking Layer)

**File:** `mcp_server/state/.run_metadata_{run_id}.json`

**Purpose:** Links in-process audit with compliance file, provides run status tracking

**Created By:** BaseGate._save_session_run_id() (Step 1 or first gate pass)

**Updated By:** BaseGate._clear_session_marker() (Step 11 completion)

**Structure:**
```json
{
  "run_id": "2026-01-19T08-59-02.451942Z",
  "status": "active|completed",
  "created": "2026-01-19T08:59:02.451942+00:00",
  "audit_file": "D:/projects/tests/_audit/audit_log_2026-01-19T08-59-02.451942Z.json",
  "compliance_file": "D:/projects/tests/_audit/audit_log_2026-01-19T08-59-02.451942Z_compliance.json",
  "completed": "2026-01-19T09:15:33.123456+00:00"  // Added on workflow completion
}
```

**Lifecycle:**
1. Created when first gate passes (Step 1 or Step 2)
2. Status: "active" during workflow execution
3. Status updated to "completed" when session marker cleared (Step 11)
4. Persists after workflow completion for compliance validation

---

### 2. Audit File (In-Process, Primary)

**File:** `tests/_audit/audit_log_{run_id}.json`

**Purpose:** Primary audit trail - tracks all workflow execution details

**Created By:** AuditLogger (initialized on first BaseGate.pass_response)

**Written By:** AuditLogger.log_step() called from BaseGate.pass_response()

**Structure:**
```json
{
  "metadata": {
    "run_id": "2026-01-19T08-59-02.451942Z",
    "workflow": "helios1",
    "created": "2026-01-19T08:59:02.451942+00:00",
    "version": "2.0"
  },
  "steps": [
    {
      "step": 1,
      "gate": "qg_preflight",
      "status": "pass",
      "timestamp": "2026-01-19T08:59:02.500000+00:00",
      "metadata": {
        "credential_strategy": "static",
        "test_data_location": "shared"
      }
    },
    {
      "step": 2,
      "gate": "qg_user_input",
      "status": "pass",
      "timestamp": "2026-01-19T08:59:05.100000+00:00",
      "metadata": {
        "persona": "As a sales representative",
        "url": "https://heliosdigital-retail-qa.azurewebsites.net/customer-inquiry",
        "workflow": "helios1",
        "detected_env_id": "helios1"
      }
    }
    // ... steps 3-11
  ]
}
```

**Content Categories:**
- **Gate Results:** status (pass/fail), error messages, fix hints
- **Step Metadata:** All data passed through tool chain (persona, BDD, metadata, etc.)
- **Self-Heal Attempts:** Recorded when gates fail and auto-fix attempts made
- **Generated Files:** Paths to POM, Task, Role, Test files
- **Execution Details:** Timestamps, tool names, step numbers

---

### 3. Compliance File (External Validation Overlay)

**File:** `tests/_audit/audit_log_{run_id}_compliance.json`

**Purpose:** External validation overlay - independent confirmation of gate executions

**Created By:** PostToolUse hook (.claude/hooks/audit-trail-writer.py)

**Written By:** Hook appends after each gate passes (status: "pass")

**Structure:**
```json
{
  "compliance_metadata": {
    "created": "2026-01-19T08:59:02.600000+00:00",
    "source": "PostToolUse hook",
    "purpose": "External validation overlay",
    "version": "2.0",
    "last_updated": "2026-01-19T09:15:30.123456+00:00",
    "observation_count": 11
  },
  "observations": [
    {
      "timestamp": "2026-01-19T08:59:02.600000+00:00",
      "step": "step_1",
      "tool_name": "mcp__qa-automation__qg_preflight",
      "gate_status": "pass",
      "observed_by": "hook"
    },
    {
      "timestamp": "2026-01-19T08:59:05.200000+00:00",
      "step": "step_2",
      "tool_name": "mcp__qa-automation__qg_user_input",
      "gate_status": "pass",
      "observed_by": "hook"
    }
    // ... observations for steps 3-11
  ]
}
```

**Content (Minimal):**
- **Observation Timestamp:** When hook observed gate execution
- **Step Name:** step_1, step_2, ..., step_11
- **Tool Name:** Full MCP tool name (mcp__qa-automation__qg_*)
- **Gate Status:** pass (only logs passed gates)
- **Observer:** Always "hook" (external validation)

**Why Minimal?**
- Compliance file is for validation, not forensics
- Detailed data lives in primary audit file
- Reduces file contention risk
- Faster hook execution

---

## Data Flow

### Workflow Start (Step 1)

1. **BaseGate.pass_response()** called (first time)
2. **_save_session_run_id(run_id)** creates:
   - Session marker: `mcp_server/state/.run_session`
   - Metadata file: `mcp_server/state/.run_metadata_{run_id}.json` (status: "active")
3. **AuditLogger.log_step()** appends to:
   - Audit file: `tests/_audit/audit_log_{run_id}.json`
4. **PostToolUse hook** triggered after tool completes:
   - Reads metadata file to find compliance_file path
   - Appends observation to: `tests/_audit/audit_log_{run_id}_compliance.json`

### During Workflow (Steps 2-10)

1. Each gate pass → **AuditLogger.log_step()** → appends to audit file
2. PostToolUse hook → reads metadata → appends to compliance file
3. Both files grow independently, linked by run_id

### Workflow End (Step 11)

1. **qg_execution** (Step 11 gate) passes
2. **qg_workflow_complete** (meta-gate) validates:
   - Reads metadata file
   - Validates both audit and compliance files
   - Compares passed gate counts (Check 9)
3. **BaseGate._clear_session_marker()** called:
   - Updates metadata status → "completed"
   - Adds completion timestamp
   - Deletes session marker
4. All three files persist for post-workflow analysis

---

## Validation Logic (Check 9)

**Location:** `mcp_server/tools/gates/qg_workflow_complete.py::_validate_compliance_trail()`

**When:** After Step 11 test execution, before workflow completion

**Purpose:** Verify external hook observations match in-process audit

**Algorithm:**
```python
1. Read session marker → extract run_id
2. Load metadata file → get audit_file, compliance_file paths
3. Read audit file → count passed gates
4. Read compliance file → count observations
5. Compare:
   IF audit_pass_count == compliance_obs_count:
       return None  # Validation passed
   ELSE:
       return warning_dict  # Non-blocking, log mismatch
```

**Non-Blocking:**
- Compliance validation is **observational**, not blocking
- Workflow can complete even if mismatch detected
- Warning logged to escalation message (if other checks fail)
- Allows graceful degradation if hook fails

**Expected Counts:**
- **Normal workflow:** 11 observations (Steps 1-11 all pass)
- **With self-heal:** More observations (gates may pass multiple times)
- **Hook failure:** Fewer observations (some gates not observed)

**Mismatch Scenarios:**

| Scenario | Audit Count | Compliance Count | Action |
|----------|-------------|------------------|--------|
| **Normal** | 11 | 11 | Pass (no warning) |
| **Hook failed** | 11 | 7 | Warn (hook missed steps 8-11) |
| **Self-heal** | 15 | 15 | Pass (extra retries logged) |
| **No compliance file** | 11 | N/A | Warn (hook never ran) |

---

## Benefits of Dual-Layer Architecture

### 1. Defense-in-Depth
- **Primary audit** tracks execution from inside the process
- **Compliance** validates from external observer (hook)
- Independent failures don't compromise the other layer

### 2. File Contention Prevention
- Separate files = no write conflicts
- In-process logger writes to audit file
- Hook writes to compliance file
- Metadata file is write-once (created) then update-once (completed)

### 3. Clear Ownership
- **Audit file:** AuditLogger owns, writes detailed data
- **Compliance file:** Hook owns, writes minimal observations
- **Metadata file:** BaseGate owns, coordinates both systems

### 4. Compliance-Ready
- Compliance file provides external validation for regulated verticals
- Demonstrates independent verification of workflow execution
- Timestamped observations with external observer attribution

### 5. Graceful Degradation
- If hook fails, in-process audit continues
- If in-process logger fails, hook provides fallback observations
- Validation is non-blocking (warns but doesn't block workflow)

### 6. Debuggability
- Two perspectives on same workflow
- Can cross-reference timestamps between files
- Metadata file provides run status and file paths

---

## Usage Examples

### Example 1: Normal Workflow (All Checks Pass)

**Files Created:**
```
mcp_server/state/.run_metadata_2026-01-19T10-00-00.000000Z.json
tests/_audit/audit_log_2026-01-19T10-00-00.000000Z.json
tests/_audit/audit_log_2026-01-19T10-00-00.000000Z_compliance.json
```

**Validation Result (Step 11):**
```
Check 9: Compliance trail valid - PASSED
  - Audit passed gates: 11
  - Compliance observations: 11
  - Match: ✓
```

---

### Example 2: Hook Failure (Partial Compliance)

**Scenario:** PostToolUse hook fails at Step 8

**Files Created:**
```
mcp_server/state/.run_metadata_2026-01-19T10-05-00.000000Z.json
tests/_audit/audit_log_2026-01-19T10-05-00.000000Z.json  (complete, 11 steps)
tests/_audit/audit_log_2026-01-19T10-05-00.000000Z_compliance.json  (partial, 7 observations)
```

**Validation Result (Step 11):**
```
Check 9: Compliance trail valid - WARNING (non-blocking)
  - Audit passed gates: 11
  - Compliance observations: 7
  - Mismatch: Hook missed steps 8-11
  - Suggested Fix: Check PostToolUse hook execution
  - Note: This is observational - workflow can proceed
```

**Workflow Action:** Continues to completion, warning logged

---

### Example 3: Self-Heal Workflow (Extra Observations)

**Scenario:** Step 6 fails once, self-heals, passes on retry

**Files Created:**
```
tests/_audit/audit_log_2026-01-19T10-10-00.000000Z.json:
  - step 6 (fail)
  - step 6 (pass)  ← Retry
  - steps 7-11 (pass)
  Total: 12 entries (1 fail + 11 pass)

tests/_audit/audit_log_2026-01-19T10-10-00.000000Z_compliance.json:
  - step_6 observation (first pass attempt)
  - step_6 observation (retry pass)
  - steps 7-11 observations
  Total: 12 observations
```

**Validation Result (Step 11):**
```
Check 9: Compliance trail valid - PASSED
  - Audit passed gates: 12
  - Compliance observations: 12
  - Match: ✓ (includes self-heal retry)
```

---

### Example 4: No Compliance File (Hook Never Ran)

**Scenario:** Hook configuration missing or disabled

**Files Created:**
```
mcp_server/state/.run_metadata_2026-01-19T10-15-00.000000Z.json
tests/_audit/audit_log_2026-01-19T10-15-00.000000Z.json
(no compliance file)
```

**Validation Result (Step 11):**
```
Check 9: Compliance trail valid - WARNING (non-blocking)
  - Error: Compliance file not found
  - Context: PostToolUse hook may not have executed or failed
  - Expected path: tests/_audit/audit_log_2026-01-19T10-15-00.000000Z_compliance.json
  - Suggested Fix: Check .claude/hooks/audit-trail-writer.py hook configuration
  - Severity: warning
```

**Workflow Action:** Continues to completion, warning logged

---

## Implementation Details

### BaseGate Enhancement (Task 68.0 Phase 3)

**File:** `mcp_server/tools/gates/base_gate.py`

**Changes:**

1. **_save_session_run_id()** (lines 151-196)
   - Creates session marker (existing)
   - **NEW:** Creates metadata file with audit + compliance paths
   - Non-blocking (try/except)

2. **_clear_session_marker()** (lines 198-241)
   - **NEW:** Updates metadata status to "completed"
   - **NEW:** Adds completion timestamp
   - Deletes session marker (existing)
   - Non-blocking (try/except)

**Code Pattern:**
```python
# Non-blocking metadata write
try:
    metadata_file.write_text(json.dumps(metadata, indent=2))
except Exception:
    pass  # Metadata is optional, don't block workflow
```

---

### Hook Enhancement (Task 68.0 Phase 3)

**File:** `.claude/hooks/audit-trail-writer.py`

**Changes:**

1. **find_current_run()** (NEW)
   - Reads session marker → extracts run_id
   - Loads metadata file → returns metadata dict
   - Returns empty dict if no active run

2. **append_to_compliance_file()** (NEW)
   - Reads existing compliance file (or creates new)
   - Appends minimal observation
   - Updates observation count
   - Non-blocking write

3. **main()** (REWRITTEN)
   - Old: Read workflow_state.json (unreliable)
   - **NEW:** Read metadata file via find_current_run()
   - Only logs passed gates (status: "pass")
   - Exits silently if no metadata found

**Trigger:** PostToolUse hook after any qg_* MCP tool completes

**Exit Codes:**
- 0 = Success (observation written or not applicable)
- Non-zero exits logged but don't block workflow

---

### Validation Enhancement (Task 68.0 Phase 3)

**File:** `mcp_server/tools/gates/qg_workflow_complete.py`

**Changes:**

1. **validate()** - Updated checks list (line 84-93)
   - Added: `("Compliance trail valid", cls._validate_compliance_trail)`
   - Now runs 9 checks instead of 8

2. **_validate_compliance_trail()** (NEW, lines 586-683)
   - Reads metadata file to find audit + compliance paths
   - Compares passed gate counts
   - Returns None if match, warning dict if mismatch
   - Non-blocking (returns warnings, not errors)

**Integration:** Called as Check 9 in workflow completion validation

---

## Maintenance

### Adding New Steps

When adding Step 12 to workflow:

1. **No changes needed** to audit architecture
2. **AuditLogger:** Auto-logs Step 12 when gate passes
3. **Hook:** Auto-observes Step 12 (already watches all qg_* tools)
4. **Validation:** Auto-validates (counts all passed gates)

### Troubleshooting

**Problem:** Compliance file missing

**Check:**
1. Is `.claude/hooks/audit-trail-writer.py` configured?
2. Is PostToolUse hook enabled in Claude Code settings?
3. Are hook permissions correct? (must be executable)

**Problem:** Compliance count mismatch

**Check:**
1. Review audit file for failed gates (not logged to compliance)
2. Check hook exit codes (non-zero = hook error)
3. Verify metadata file exists and has correct paths

**Problem:** Metadata file not created

**Check:**
1. Is `BaseGate._save_session_run_id()` called? (should happen on first gate pass)
2. Check file permissions for `mcp_server/state/` directory
3. Review BaseGate code for exceptions (should be caught and ignored)

---

## Related Design Decisions

- **DD-30:** Progressive audit trail (PostToolUse hook writes to tests/_audit/)
- **Task 68.0:** 3 Workflow Polish Fixes (Phase 3: Audit Trail Integration)
- **DEF-052:** Audit trail writer hook cannot access workflow state (fixed via metadata file)

---

## Future Enhancements

### Phase 4 (If Needed)

1. **Audit File Rotation:** Archive old audit files after N days
2. **Compliance Dashboard:** Web UI to view compliance trail visualizations
3. **Real-Time Validation:** Validate compliance during workflow (not just at end)
4. **Detailed Mismatch Analysis:** Track which specific steps have mismatched observations

### Regulated Verticals

For industries requiring compliance certification:
1. **Digital Signatures:** Sign compliance file with cryptographic signature
2. **Tamper Detection:** Hash compliance file, verify integrity
3. **Audit Export:** Export compliance trail to regulatory format (CSV, XML)
4. **Retention Policies:** Implement automatic archival and retention rules

---

**End of Architecture Document**
