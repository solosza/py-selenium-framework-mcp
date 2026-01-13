<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 2: User Input

**Purpose:** Collect and validate user's test requirement (persona + URL).

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 2 - User Input |
| **Dependencies** | Step 1 complete (credential_strategy, test_data_location exist) |
| **Input** | User's natural language requirement |
| **Output** | `persona`, `URL`, `role_name`, `workflow`, `raw_requirement` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | Provides test requirement in "As a [role], I want to..." format with URL |
| **AI** | Asks for requirement if not provided, extracts persona/URL/role_name/workflow, passes to gate |
| **Tool** | `qg_user_input` validates extracted fields, saves state on PASS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 1 complete (credential_strategy, test_data_location exist in state)

ACTION:
- IF user hasn't provided requirement: ASK for it
  "What test do you want to create?
   Format: 'As a [role], I want to [action]...'
   URL: [target page]"
- IF user provided requirement: EXTRACT persona, URL, role_name, workflow

VALIDATE:
- CALL qg_user_input with extracted fields

RETRY:
- If gate FAIL: ASK user for missing/invalid field with example
- No max retries (user provides input, not AI)
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | - (none) |
| **Quality Gate** | `qg_user_input` |
| **Gate Mode** | POST-only (validates after AI extraction) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `persona`, `URL`, `role_name`, `workflow`, `raw_requirement` |
| **Who Saves** | Quality gate (`qg_user_input`) |
| **When Saved** | On gate PASS |
| **State Schema** | See below |

```json
{
  "step": 2,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "persona": "registered user",
    "URL": "http://automationpractice.pl/index.php?controller=authentication",
    "role_name": "RegisteredUser",
    "workflow": "auth",
    "raw_requirement": "As a registered user, I want to login with email and password"
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-01 (persona required), DD-02 (URL required) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 3 until all fields valid** |

**Validation Checks:**

| Check | Rule |
|-------|------|
| `persona` | Must be present (extracted from "As a [X]") |
| `URL` | Must be valid URL format |
| `role_name` | Must be derivable from persona (PascalCase) |
| `workflow` | Must be non-empty string (accepts `domain` for backwards compatibility) |
| `raw_requirement` | Must be specific enough for BDD generation |

---

## G. Error Handling

**Failure Behavior:**

| Issue | Behavior |
|-------|----------|
| Persona missing | ASK: "Please specify persona. Example: 'As a customer, I want to...'" |
| URL missing | ASK: "Which page? Example: 'http://yoursite.com/login'" |
| Cannot determine role | ASK: "What type of user? Example: 'customer', 'admin', 'visitor'" |
| Cannot determine workflow | ASK: "What workflow area? Example: 'auth', 'search', 'checkout', or any custom name" |
| Requirement vague | ASK: "Please be more specific. Example: 'I want to add a blue t-shirt size M to cart'" |

**Known Defects:** Enforcement gap - AI sometimes forgets to ask for missing info

**Error Message Templates:**

Missing persona (DD-01):
```
"I need to know the user persona.

Please provide in format: 'As a [role], I want to [action]...'
Example: 'As a registered user, I want to login with email and password'"
```

Missing URL (DD-02):
```
"I need the target page URL.

Which page should the test interact with?
Example: 'http://automationpractice.pl/index.php?controller=authentication'"
```

Vague requirement:
```
"The requirement isn't specific enough for test generation.

Please add details. Instead of:
  'I want to browse products'

Say:
  'I want to browse products in the Women category and add a Printed Dress to cart'"
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 2: USER INPUT                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 1 complete?      │
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
              │  Receive/Ask for    │     │  BLOCKED        │
              │  user requirement   │     │  Go to Step 1   │
              └─────────────────────┘     └─────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  AI EXTRACTS:       │
              │  - persona          │
              │  - URL              │
              │  - role_name        │
              │  - workflow         │
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_user_input                                                 │
│  - Validates all extracted fields                                           │
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
              │  STATE SAVED        │  │  ASK USER           │
              │  (by qg_user_input) │  │  (show what's wrong)│
              └─────────────────────┘  └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 3  │
              └─────────────────────┘
```

---

*Next: Step 3 - AI Processing*
