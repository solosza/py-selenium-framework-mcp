<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 2: Pre-flight Configuration

**Purpose:** Establish configuration strategy before test construction begins.

**Workflow Version:** v3.0 (5-Step Pair Programming Workflow)

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 2 - Pre-flight Configuration |
| **Dependencies** | Step 1 (User Input) must be complete |
| **Input** | Step 1 output (persona, URL, workflow, etc.) |
| **Output** | `credential_strategy`, `test_data_location`, `browser_config`, `timeout_config` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | Answers configuration questions |
| **AI** | Asks questions, waits for answers, passes to gate |
| **Tool** | `qg_preflight` validates answers, scaffolds infrastructure, saves state on PASS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Step 1 must be complete (qg_user_input passed)

ACTION:
- ASK user Question 1: Credential strategy?
  Options:
  1. Static        - Use existing account from test_users.json
  2. Dynamic       - Register fresh user, save for later tests
  3. Self-contained - Register and use within same test
  4. None needed   - Test doesn't require credentials

- WAIT for answer

- ASK user Question 2: Test data location?
  Options:
  1. Shared            - tests/data/ (cross-workflow)
  2. Workflow-specific - tests/{workflow}/data/
  3. Both              - Shared credentials + workflow-specific data
  4. None needed       - Test doesn't require external data

- WAIT for answer

- ASK user Question 3: Browser visibility?
  Options:
  1. Visible (headless=false) - REQUIRED for pair programming
  (No other options - this is non-negotiable)

- WAIT for confirmation

- ASK user Question 4: Timeout monitoring?
  Options:
  1. Enabled (default 30s) - AI stops if element not found within threshold
  2. Custom threshold      - Specify seconds (e.g., 60s for slow apps)
  3. Disabled              - No timeout monitoring (use with caution)

- WAIT for answer

VALIDATE:
- CALL qg_preflight with all answers

RETRY:
- If gate FAIL: RE-ASK the invalid/missing field
- If gate NEEDS_RETRY with scaffolding: Create files/dirs, retry gate
- No max retries (user provides input, not AI)

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, user answers, gate result, timestamp
- Append mode (don't overwrite existing content)
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | None (configuration step) |
| **Quality Gate** | `qg_preflight` |
| **Gate Mode** | POST-only (validates after user input) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `credential_strategy`, `test_data_location`, `browser_config`, `timeout_config` |
| **Who Saves** | Quality gate (`qg_preflight`) |
| **When Saved** | On gate PASS |
| **State Schema** | See below |

```json
{
  "step": 2,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "credential_strategy": "static | dynamic | self-contained | none",
    "test_data_location": "shared | workflow | both | none",
    "browser_config": {
      "headless": false
    },
    "timeout_config": {
      "enabled": true,
      "threshold_seconds": 30
    }
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-24 (credential strategy), DD-28 (test data location), FR-8.1 (headless=false), FR-8.2 (timeout monitoring) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 3 until all answers valid** |

**Validation Checks:**

| Check | Rule |
|-------|------|
| `credential_strategy` | Must be one of: static, dynamic, self-contained, none |
| `test_data_location` | Must be one of: shared, workflow, both, none |
| `browser_config.headless` | Must be false (non-negotiable for pair programming) |
| `timeout_config.enabled` | Must be true or false |
| `timeout_config.threshold_seconds` | If enabled, must be positive integer (default 30) |

---

## G. Error Handling

**Failure Behavior:**

| Issue | Behavior |
|-------|----------|
| User skips question | RE-ASK: "I need this to proceed. [repeat question]" |
| Invalid answer | RE-ASK: "Please choose from the options: 1, 2, 3, or 4" |
| User says "I don't know" | GUIDE: Explain each option briefly, recommend based on context |
| User requests headless=true | REJECT: "Pair programming requires visible browser (headless=false is non-negotiable)" |

**Error Message Templates:**

Missing credential_strategy:
```
"Which credential approach for this test?

1. Static        - Use existing account from test_users.json
2. Dynamic       - Register fresh user, save for later tests
3. Self-contained - Register and use within same test
4. None needed   - Test doesn't require credentials"
```

Missing test_data_location:
```
"Where should test data live?

1. Shared            - tests/data/ (cross-workflow)
2. Workflow-specific - tests/{workflow}/data/
3. Both              - Shared credentials + workflow-specific data
4. None needed       - Test doesn't require external data"
```

Browser visibility (informational):
```
"Browser visibility: headless=false (visible)

This is required for pair programming so you can see AI actions in real-time."
```

Timeout monitoring:
```
"Timeout monitoring configuration?

1. Enabled (default 30s) - AI stops if element not found within threshold
2. Custom threshold      - Specify seconds (e.g., 60s for slow apps)
3. Disabled              - No timeout monitoring (use with caution)"
```

---

## H. Infrastructure Scaffolding

**Purpose:** Auto-create test data files/directories based on Step 2 configuration.

**Scaffolding Rules:**

| Strategy | Infrastructure Created |
|----------|----------------------|
| `static` or `dynamic` | `tests/data/` directory + `tests/data/test_users.json` |
| `workflow` or `both` | `tests/{workflow}/data/` directory |
| `self-contained` or `none` | `tests/data/` directory only (no credential file) |

**Gate Response Format (NEEDS_RETRY):**

```json
{
  "status": "NEEDS_RETRY",
  "fix_applied": "test_data_infrastructure_scaffolded",
  "error": "Missing test data infrastructure",
  "message": "Create the following files/directories based on Step 2 config:",
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

## I. User Communication

**What to Show:**
- Credential strategy chosen
- Test data location chosen
- Browser config (always visible)
- Timeout config

**Output Format:**
```
✓ Step 2: Pre-flight Configuration
  • Credentials: static (use existing account)
  • Test data: workflow-specific
  • Browser: visible (headless=false)
  • Timeout: 30s
```

---

## J. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   STEP 2: PRE-FLIGHT CONFIGURATION                           │
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
                         ┌────────────────────────┐
                         │  AI ASKS Question 3    │
                         │  (browser visibility)  │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  USER confirms         │
                         │  (headless=false)      │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  AI ASKS Question 4    │
                         │  (timeout monitoring)  │
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
│  - Validates all answers                                                    │
│  - Scaffolds infrastructure (DEF-060)                                       │
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
                         │  PROCEED TO STEP 3     │
                         └────────────────────────┘
```

---

*Next: Step 3 - AI Processing*
