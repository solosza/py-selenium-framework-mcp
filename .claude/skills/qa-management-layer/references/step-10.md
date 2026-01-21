<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 10: Validation

**Purpose:** Validate all generated files are saved to disk and ready for execution (Step 11).

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 10 - Validation |
| **Dependencies** | Step 9 complete (all code generated: POM, Task, Role, Test) |
| **Input** | All generated code from Steps 6-9 |
| **Output** | Validation confirmation (files exist and ready) |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | Reviews validation results |
| **AI** | Validates all files exist on disk and are ready for execution |
| **Tool** | `qg_save_run` validates all code present and files exist on disk |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 9 complete (test_code exist in state)
- Verify all code from Steps 6-9 is present and complete

ACTION:
- CALL qg_save_run (PRE-VALIDATE all code present + FILES EXIST)
- **NOTE:** Files already written in Steps 6-9 (DEF-051 immediate write)
- qg_save_run validates all generated files exist on disk:
  - POM files (may be multiple) → framework/pages/{workflow}/*.py
  - Task file → framework/tasks/{workflow}/{task_name}.py
  - Role file → framework/roles/{workflow}/{role_name}.py
  - Test file → tests/{workflow}/test_{scenario}.py
- REPORT validation results
- **PROCEED TO STEP 11** for test execution

AUTO-RECOVERY (NEEDS_RETRY):
- If validation fails, qg_save_run returns NEEDS_RETRY with recovery_action
- AI MUST follow recovery_action to fix issue and retry Step 10
- Recovery actions:
  - regenerate_layer: Go back to Step 6/7/8/9 to regenerate code
  - complete_skeleton: Complete incomplete code (DD-25)
  - write_files_from_state: Write missing files to disk (DEF-051 fix)
  - validate_through_post_gate: Validate reconstructed code via POST gate
  - create_test_data_files: Create missing test data files
  - complete_step_9: Complete Step 9 first
- Escalation: After 3 attempts, escalates to blocked (DD-22) for manual intervention
- Attempt count tracked in state with error history

VALIDATE:
- PRE:
  - All code present (input_data or fallback to state)
  - No skeleton code (DD-25 final sweep)
  - No reconstructed code without POST validation (DEF-048)
  - **ALL FILES EXIST ON DISK** (Task 19.0 - DEF-051 validation)
- POST: N/A (PRE-only gate)

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, files validated, gate results, timestamp, recovery actions if any
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
- **Test execution happens in Step 11**
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | None (files already saved in Steps 6-9 via DEF-051) |
| **Quality Gate** | `qg_save_run` |
| **Gate Mode** | PRE-only (validates all code and files ready for execution) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `files_validated` |
| **Who Saves** | AI (after successful validation) |
| **When Saved** | After qg_save_run PRE validation passes |
| **State Schema** | See below |

```json
{
  "step": 10,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "files_validated": [
      "framework/pages/auth/login_page.py",
      "framework/tasks/auth/auth_tasks.py",
      "framework/roles/registered_user.py",
      "tests/auth/test_login.py"
    ],
    "validation_complete": true,
    "ready_for_execution": true
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-25 (no skeleton code), FR-14.4 (test data files exist) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 11 until all files validated** |

**PRE-Validation Checks:**

| Check | Rule |
|-------|------|
| `pom_code` | Present from Step 6 |
| `task_code` | Present from Step 7 |
| `role_code` | Present from Step 8 |
| `test_code` | Present from Step 9 |
| All code | No skeleton indicators (DD-25 final check) |

---

## G. Error Handling

**Auto-Recovery via NEEDS_RETRY:**

Step 10 uses auto-recovery pattern for validation failures. Gate returns NEEDS_RETRY with recovery_action:

| Failure Point | Recovery Action | AI Behavior |
|---------------|-----------------|-------------|
| Missing code | `regenerate_layer` | Go back to relevant step (6, 7, 8, or 9) to regenerate |
| Empty code | `regenerate_layer` | Go back to relevant step to regenerate |
| Skeleton code | `complete_skeleton` | Complete incomplete code, remove placeholders (DD-25) |
| File not found | `write_files_from_state` | Write missing files from state (DEF-051 fix) |
| Reconstructed code | `validate_through_post_gate` | Validate modified code via POST gate (DEF-048) |
| Missing test data | `create_test_data_files` | Create missing test data infrastructure |
| Step 9 incomplete | `complete_step_9` | Complete Step 9 first |

**Escalation to Manual Intervention:**
- After 3 retry attempts, escalates to `blocked` status (DD-22)
- Returns error history and last recovery action attempted
- User must manually resolve issue and restart workflow

**Known Defects:** None

**CRITICAL:** Step 10 only validates - it does NOT execute tests. Test execution happens in Step 11.

---

## File Save Locations

| Code Type | Location Pattern |
|-----------|------------------|
| POM | `framework/pages/{domain}/{page_name}.py` |
| Task | `framework/tasks/{domain}/{task_name}.py` |
| Role | `framework/roles/{role_name}.py` |
| Test | `tests/{domain}/test_{intent}.py` |

**Example for login test:**
```
framework/pages/auth/login_page.py
framework/tasks/auth/auth_tasks.py
framework/roles/registered_user.py
tests/auth/test_login.py
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 10: VALIDATION                                       │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 9 complete?      │
                         │  All code present?     │
                         └────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  YES     │            │  NO      │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
┌─────────────────────────────────┐     ┌─────────────────┐
│  QUALITY GATE: qg_save_run      │     │  BLOCKED        │
│  - All code present             │     │  Go to missing  │
│  - No skeleton code             │     │  step           │
└─────────────────────────────────┘     └─────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  VALIDATE FILES:    │
              │  - POM exists       │
              │  - Task exists      │
              │  - Role exists      │
              │  - Test exists      │
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  REPORT RESULTS:    │
              │  All files valid    │
              │  Ready for Step 11  │
              └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  STEP 10 COMPLETE   │
              │                     │
              │  → PROCEED TO       │
              │     STEP 11         │
              │     (Test Execution)│
              └─────────────────────┘
```

---

## Step 10 Complete

Upon successful validation:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 10: VALIDATION COMPLETE                              │
│                                                                              │
│  Files validated:                                                           │
│  ✓ framework/pages/auth/login_page.py                                       │
│  ✓ framework/tasks/auth/auth_tasks.py                                       │
│  ✓ framework/roles/registered_user.py                                       │
│  ✓ tests/auth/test_login.py                                                 │
│                                                                              │
│  Status: Ready for execution                                                │
│                                                                              │
│  State saved to: mcp_server/state/<run_id>/step_10.json                     │
│                                                                              │
│  Audit trail: tests/_audit/<run_id>.json (Step 10 entry added)              │
│                                                                              │
│  → PROCEED TO STEP 11 (Execution & Validation)                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## H. Progressive Audit Trail

**Purpose:** Complete traceability for regulated verticals (healthcare, finance, legal, insurance).

### How It Works

A PostToolUse hook (`audit-trail-writer.py`) automatically captures each gate result:

```
Step 1 gate passes → Audit file created with step_1 data
Step 2 gate passes → step_2 appended
Step 3 gate passes → step_3 appended
...
Step 10 gate passes → Audit finalized
```

### Audit File Location

```
tests/_audit/
└── YYYY-MM-DD_HHMMSS_{workflow}_{intent}.json
```

**Example:** `2025-12-28_120000_cart_login_and_add_to_cart.json`

### Audit File Structure

```json
{
  "audit_metadata": {
    "created": "2025-12-28T12:00:00Z",
    "last_updated": "2025-12-28T12:03:00Z",
    "platform": "qa-automation",
    "version": "1.0"
  },
  "step_1": {
    "timestamp": "2025-12-28T12:00:00Z",
    "gate_result": "pass",
    "data": { "credential_strategy": "self-contained", "test_data_location": "both" }
  },
  "step_2": {
    "timestamp": "2025-12-28T12:00:05Z",
    "gate_result": "pass",
    "data": { "persona": "registered user", "URL": "...", "workflow": "cart" }
  },
  ...
  "step_10": {
    "timestamp": "2025-12-28T12:03:00Z",
    "gate_result": "pass",
    "data": { "files_saved": [...], "test_result": {...} }
  }
}
```

### Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Progressive (not final)** | If workflow crashes, audit exists up to that point |
| **Hook-based (SRP)** | Gates validate; hook writes audit (separation of concerns) |
| **Code stripped** | Raw code blobs replaced with `[CODE_STRIPPED_FOR_AUDIT]` to reduce file size |
| **Timestamped filename** | Each workflow run creates unique file (never overwrites) |
| **Session marker** | `.audit_session` file tracks current workflow's audit file |

### Compliance Use Cases

| Vertical | Audit Question Answered |
|----------|-------------------------|
| **Healthcare** | "Show every step that generated this patient report test" |
| **Finance** | "Prove this trading algorithm test was validated at each gate" |
| **Legal** | "Document chain for this contract review automation" |
| **Insurance** | "Compliance evidence for claims processing test" |

### Hook Registration

Located in `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "mcp__qa-automation__qg_.*",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/audit-trail-writer.py\""
          }
        ]
      }
    ]
  }
}
```

---

## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-10-01 | Primary: code from input_data; Fallback: code from state (resume scenario) | Normal flow passes code in input_data; resume/recovery reads from state | `validate_pre()` |
| IC-10-02 | PRE-only mode (no POST validation) | Gate validates before save; no output to validate after | `validate()` |
| IC-10-03 | Final skeleton sweep on ALL 4 layers (POM, Task, Role, Test) | Last line of defense before files hit disk (DD-25) | `validate_pre()` |
| IC-10-04 | Each code block validated independently; first failure stops validation | Fail-fast with clear error pointing to specific layer | `validate_pre()` |
| IC-10-05 | Missing code returns step hint (e.g., "Go back to Step 6 for POM") | Actionable fix guidance | `validate_pre()` |

**Date Added:** 2025-12-21
**Task Reference:** Task 13.0 (qg_save_run)

---

## K. User Communication

**Purpose:** Define clean, concise output to user (not verbose MCP JSON).

**What to Show:**
- Number of files validated
- Confirmation all exist on disk

**Output Format:**
```
✓ Step 10: Validation
  • Files validated: 4 (POM, Task, Role, Test)
  • All files exist on disk: YES
```

**What NOT to Show:**
- ❌ Full file paths in output
- ❌ Gate status
- ❌ File content summaries
- ❌ Timestamps

**Rule:** Follow user-communication-protocol.md - Signal, not noise.

---

*Step 10 validation complete. Proceed to Step 11 for test execution.*
