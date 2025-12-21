# Step 3: AI Processing

**Purpose:** Transform user requirement into structured metadata (BDD scenarios, expected states, intent).

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 3 - AI Processing |
| **Dependencies** | Step 2 complete (persona, URL, role_name, domain, raw_requirement exist) |
| **Input** | Step 2 output + original requirement |
| **Output** | `bdd_scenarios`, `expected_states`, `intent` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | None (unless AI fails 3 times, then user decides resolution) |
| **AI** | Creates BDD scenario, extracts expected_states from "Then" clauses, determines intent |
| **Tool** | `qg_ai_processing` validates metadata structure, saves state on PASS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 2 complete (persona, URL, role_name, domain exist in state)

ACTION:
- READ raw_requirement from Step 2 state
- CREATE BDD scenario with Given/When/Then structure
- EXTRACT expected_states from "Then" clauses (DD-09)
- DETERMINE intent (action verb from requirement)

VALIDATE:
- CALL qg_ai_processing with metadata

RETRY:
- If gate FAIL: AI retries processing (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | - (none, AI processes) |
| **Quality Gate** | `qg_ai_processing` |
| **Gate Mode** | POST-only (validates AI-generated metadata) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `bdd_scenarios`, `expected_states`, `intent` |
| **Who Saves** | Quality gate (`qg_ai_processing`) |
| **When Saved** | On gate PASS |
| **State Schema** | See below |

```json
{
  "step": 3,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "bdd_scenarios": [
      {
        "given": "I am on the login page",
        "when": ["I enter valid email", "I enter valid password", "I click login"],
        "then": ["I should see my account dashboard", "I should see logout link"]
      }
    ],
    "expected_states": ["is_on_dashboard", "is_logout_visible"],
    "intent": "login"
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-03 (metadata context), DD-09 (expected_states from "Then") |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 4 until metadata complete** |

**Validation Checks:**

| Check | Rule |
|-------|------|
| `bdd_scenarios` | Must have valid Given/When/Then structure |
| `expected_states` | At least one state derived from "Then" clause |
| `intent` | Action verb extracted from requirement |

---

## G. Error Handling

**Failure Behavior:**

| Attempt | Behavior |
|---------|----------|
| 1-3 | Gate rejects → AI retries processing |
| After 3 | STOP → REPORT → USER DECIDES |

**Known Defects:** None

**Error Message Template (After 3 Failures):**

```
"I've attempted 3 times and cannot produce valid metadata.

Here's what I'm generating:
[show failing output]

Tool rejection reason:
[show error from gate]

How should we proceed?
1. Clarify requirement - Go back to Step 2
2. Abort workflow - Stop and log issue"
```

**Note:** No "proceed with incomplete" option. Incomplete data never propagates.

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 3: AI PROCESSING                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 2 complete?      │
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
              │  AI CREATES:        │     │  BLOCKED        │
              │  - BDD scenario     │     │  Go to Step 2   │
              │  - expected_states  │     └─────────────────┘
              │  - intent           │
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_ai_processing                                              │
│  - Validates metadata structure                                             │
│  - Saves state on PASS                                                      │
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
              │  (by qg_ai_proc)    │  │  AI retries         │
              └─────────────────────┘  │                     │
                         │             │  After 3:           │
                         │             │  STOP → REPORT →    │
                         │             │  USER DECIDES       │
                         │             └─────────────────────┘
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 4  │
              └─────────────────────┘
```

---

*Next: Step 4 - Generate Tests (Tool 1)*
