<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 4: Tool 1 - Generate Tests

**Purpose:** Generate test scenarios from BDD metadata using MCP tool.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 4 - Generate Tests (Tool 1) |
| **Dependencies** | Step 3 complete (bdd_scenarios, expected_states, intent exist) |
| **Input** | `metadata_context` from Step 3 (bdd_scenarios, expected_states, intent) |
| **Output** | `test_scenarios` array |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | None (unless AI fails 3 times, then user decides resolution) |
| **AI** | Prepares input (user_story, workflow), calls gate, calls operation, validates output |
| **Tool** | `qg_test_scenarios` validates input/output, `generate_tests_from_user_story` generates scenarios, operation saves state on SUCCESS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 3 complete (bdd_scenarios, expected_states, intent exist in state)

ACTION:
- PREPARE input (DD-19: import from tools/, never utils/):
  - FORMAT bdd_scenarios AS user_story STRING (see Section H)
  - SET workflow FROM domain
- CALL qg_test_scenarios (PRE-VALIDATE input)
- CALL generate_tests_from_user_story (OPERATION)
- CALL qg_test_scenarios (POST-VALIDATE output)

VALIDATE:
- PRE: Validate input before operation
- POST: Validate output after operation

RETRY:
- If PRE-VALIDATE fails: AI fixes input (max 3 attempts)
- If POST-VALIDATE fails: AI retries operation (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, tool input/output, PRE/POST gate results, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_tests_from_user_story` |
| **Quality Gate** | `qg_test_scenarios` |
| **Gate Mode** | PRE+POST (validates input before, output after) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `test_scenarios` array |
| **Who Saves** | Operation tool (`generate_tests_from_user_story`) |
| **When Saved** | On operation SUCCESS (after POST-VALIDATE passes) |
| **State Schema** | See below |

```json
{
  "step": 4,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "test_scenarios": [
      {
        "name": "test_valid_login",
        "given": "I am on the login page",
        "when": ["I enter valid email", "I enter valid password", "I click login"],
        "then": ["I should see my account dashboard", "I should see logout link"]
      }
    ]
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-19 (tool import), DD-23 (BDD format) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 5 until both PRE and POST gates pass** |

**PRE-Validation Checks:**

| Check | Rule |
|-------|------|
| `bdd_scenarios` | Present + valid Given/When/Then structure |
| `expected_states` | Present + at least one state |
| `workflow` | One of: auth, catalog, cart, checkout |

**POST-Validation Checks:**

| Check | Rule |
|-------|------|
| `test_scenarios` | Present + at least one scenario |
| Each scenario | Has name, given, when, then fields |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| PRE-VALIDATE fails | AI fixes input preparation (max 3) |
| OPERATION fails | AI retries with adjusted params (max 3) |
| POST-VALIDATE fails | AI retries operation (max 3) |
| After 3 total failures | STOP → REPORT → USER DECIDES |

**Known Defects:** None

**Error Message Template (After 3 Failures):**

```
"I've attempted 3 times and cannot generate valid test scenarios.

PRE-VALIDATE result:
[show pre-validation result]

OPERATION result:
[show operation result]

POST-VALIDATE result:
[show post-validation result]

How should we proceed?
1. Adjust BDD scenarios - Go back to Step 3
2. Abort workflow - Stop and log issue"
```

**Note:** No "proceed with incomplete" option. Bad scenarios never propagate.

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 4: TOOL 1 - GENERATE TESTS                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 3 complete?      │
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
              │  AI PREPARES:       │     │  BLOCKED        │
              │  - user_story       │     │  Go to Step 3   │
              │  - workflow         │     └─────────────────┘
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_test_scenarios (PRE-VALIDATE)                              │
│  - Validates input before operation                                         │
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
              │  OPERATION:         │     │  RETRY (max 3)  │
              │  generate_tests_    │     │  AI fixes input │
              │  from_user_story    │     └─────────────────┘
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_test_scenarios (POST-VALIDATE)                             │
│  - Validates output after operation                                         │
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
              │  STATE SAVED        │  │  RETRY (max 3)      │
              │  (by operation)     │  │  AI retries op      │
              └─────────────────────┘  │                     │
                         │             │  After 3:           │
                         │             │  STOP → REPORT →    │
                         │             │  USER DECIDES       │
                         │             └─────────────────────┘
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 5  │
              └─────────────────────┘
```

---

## H. Tool Chain Data Contracts (DD-26)

**Input Contract (AI prepares for Tool 1):**

Tool 1 expects `user_story` as a STRING with explicit BDD keywords. AI must format:

```python
# Step 3 output (object):
bdd_scenarios = [{
    "given": "I am on the login page",
    "when": ["I enter valid email", "I enter valid password", "I click login"],
    "then": ["I should see my account dashboard"]
}]

# AI converts to user_story STRING for Tool 1:
user_story = """
As a registered user
I want to login with valid credentials
So that I can access my account

Scenario: Valid login
Given I am on the login page
When I enter valid email
And I enter valid password
And I click login
Then I should see my account dashboard
"""
```

**CRITICAL:** Tool 1 rejects input without explicit `Scenario:` and `Given/When/Then` keywords.

**Output Contract (Tool 1 provides for Step 5):**

```json
{
  "test_scenarios": [
    {
      "title": "test_valid_login",
      "given": "I am on the login page",
      "when": "I enter valid email AND I enter valid password AND I click login",
      "then": "I should see my account dashboard",
      "workflow": "auth"
    }
  ]
}
```

---

*Next: Step 5 - Discover Elements (Tool 2)*
