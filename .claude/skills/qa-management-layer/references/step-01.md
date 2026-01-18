<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 1: Pre-flight Configuration

**Purpose:** Establish configuration strategy before any test generation begins.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 1 - Pre-flight Configuration |
| **Dependencies** | None (first step) |
| **Input** | None |
| **Output** | `credential_strategy`, `test_data_location` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | Answers Question 1 (credential strategy), Answers Question 2 (test data location) |
| **AI** | Asks questions, waits for answers, passes answers to gate |
| **Tool** | `qg_preflight` validates answers, saves state on PASS |

---

## C. Skill Instruction

```
PRE-CHECK:
- None (first step)

ACTION:
- ASK user Question 1 (credential strategy)
- WAIT for answer
- ASK user Question 2 (test data location)
- WAIT for answer

VALIDATE:
- CALL qg_preflight with both answers

RETRY:
- If gate FAIL: RE-ASK the invalid/missing field
- No max retries (user provides input, not AI)

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, user answers, gate result (PASS/FAIL with full error), timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | - (none) |
| **Quality Gate** | `qg_preflight` |
| **Gate Mode** | POST-only (validates after user input) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `credential_strategy`, `test_data_location` |
| **Who Saves** | Quality gate (`qg_preflight`) |
| **When Saved** | On gate PASS |
| **State Schema** | See below |

```json
{
  "step": 1,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "credential_strategy": "static | dynamic | self-contained | none",
    "test_data_location": "shared | workflow | both | none"
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-24 (credential strategy), DD-28 (test data location) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 2 until both answers valid** |

**Validation Checks:**

| Check | Rule |
|-------|------|
| `credential_strategy` | Must be one of: static, dynamic, self-contained, none |
| `test_data_location` | Must be one of: shared, workflow, both, none |

---

## G. Error Handling

**Failure Behavior:**

| Issue | Behavior |
|-------|----------|
| User skips question | RE-ASK: "I need this to proceed. [repeat question]" |
| Invalid answer | RE-ASK: "Please choose from the options: 1, 2, 3, or 4" |
| User says "I don't know" | GUIDE: Explain each option briefly, recommend based on context |

**Known Defects:** None

**Error Message Templates:**

Missing credential_strategy:
```
"I need to know the credential approach before proceeding.

Which credential approach for this test?
1. Static        - Use existing account from test_users.json
2. Dynamic       - Register fresh user, save for later tests
3. Self-contained - Register and use within same test
4. None needed   - Test doesn't require credentials"
```

Missing test_data_location:
```
"I need to know where test data should live.

Where should test data live?
1. Shared            - tests/data/ (cross-workflow)
2. Workflow-specific - tests/{workflow}/data/
3. Both              - Shared credentials + workflow-specific data
4. None needed       - Test doesn't require external data"
```

---

## H. Test Data Infrastructure Scaffolding (DEF-060)

**Purpose:** Auto-create test data files/directories based on Step 1 configuration.

**Phase 1 (Step 1 POST):** Scaffold shared infrastructure immediately

| Strategy | Infrastructure Created |
|----------|----------------------|
| `static` or `dynamic` | `tests/data/` directory + `tests/data/test_users.json` |
| `self-contained` or `none` | `tests/data/` directory only (no credential file) |

**Scaffolding Response Format:**

When infrastructure missing, gate returns `status: "NEEDS_RETRY"`:

```json
{
  "status": "NEEDS_RETRY",
  "fix_applied": "test_data_infrastructure_scaffolded",
  "error": "Missing test data infrastructure",
  "message": "Create the following files/directories based on Step 1 config:",
  "scaffolding_needed": [
    {
      "type": "directory",
      "path": "tests/data",
      "reason": "Root directory for shared test data"
    },
    {
      "type": "file",
      "path": "tests/data/test_users.json",
      "template": "{\n  \"default_user\": {\n    \"username\": \"\",\n    \"password\": \"\",\n    \"email\": \"\"\n  }\n}",
      "reason": "Credential storage for static/dynamic strategies"
    }
  ]
}
```

**AI Handling Instructions:**

When gate returns `NEEDS_RETRY`:
1. Read `scaffolding_needed` array
2. For each item:
   - If `type: "directory"` → Create directory using Bash `mkdir -p {path}`
   - If `type: "file"` → Create file using Write tool with `template` content
3. Retry gate call after scaffolding complete
4. Verify gate returns `status: "pass"` on retry

**Idempotent:** If files/directories already exist, gate returns `pass` (no scaffolding needed).

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 1: PRE-FLIGHT                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  AI ASKS Question 1    │
                         │  (credential strategy) │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  USER answers          │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  AI ASKS Question 2    │
                         │  (test data location)  │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  USER answers          │
                         └────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_preflight                                                  │
│  - Validates both answers                                                   │
│  - Checks test data infrastructure (DEF-060)                                │
│  - Saves state on PASS                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────────────────┐
                          ▼                ▼                  ▼
                    ┌──────────┐    ┌──────────┐      ┌──────────┐
                    │  PASS    │    │NEEDS_RETRY│      │  FAIL    │
                    └────┬─────┘    └────┬─────┘      └────┬─────┘
                         │               │                   │
                         │               ▼                   ▼
                         │     ┌─────────────────┐  ┌─────────────┐
                         │     │ AI SCAFFOLDS    │  │  RE-ASK     │
                         │     │ files/dirs      │  │  USER       │
                         │     └─────────┬───────┘  └─────────────┘
                         │               │
                         │               ▼
                         │     ┌─────────────────┐
                         │     │ AI RETRIES      │
                         │     │ qg_preflight    │
                         │     └─────────┬───────┘
                         │               │
                         └───────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  STATE SAVED           │
                         │  (by qg_preflight)     │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PROCEED TO STEP 2     │
                         └────────────────────────┘
```

---

*Next: Step 2 - User Input*
