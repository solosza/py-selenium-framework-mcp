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

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, extracted fields, gate result (PASS/FAIL with full error), timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
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
    "raw_requirement": "As a registered user, I want to login with email and password",
    "detected_env_id": "DEFAULT"
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

## H. Environment Auto-Detection (DEF-062)

**Purpose:** Auto-detect test environment from URL, scaffold config for unknown environments.

**Detection Logic:**

| URL Domain | Environment Detected | Behavior |
|------------|---------------------|----------|
| Matches environment_config.json | Auto-detect (e.g., "parabank") | Continue without NEEDS_RETRY |
| DEFAULT URL (automationpractice.pl) | "DEFAULT" | Continue without NEEDS_RETRY |
| Unknown domain | NEEDS_RETRY | AI scaffolds environment config |

**Scaffolding Response Format:**

When unknown environment detected, gate returns `status: "NEEDS_RETRY"`:

```json
{
  "status": "NEEDS_RETRY",
  "fix_applied": "environment_added_to_config",
  "error": "Unknown environment: new-app.example.com",
  "message": "Add environment for 'auth' workflow to environment_config.json:",
  "scaffolding_needed": [{
    "type": "config_entry",
    "path": "framework/resources/config/environment_config.json",
    "template": "{\n  \"auth\": {\n    \"url\": \"https://new-app.example.com\"\n  }\n}",
    "reason": "Environment config for auth workflow at https://new-app.example.com"
  }]
}
```

**AI Handling Instructions (HUMAN APPROVAL REQUIRED):**

When gate returns `NEEDS_RETRY`:
1. Read `scaffolding_needed[0].template`
2. Parse template to extract proposed environment config
3. **USE AskUserQuestion to request approval:**
   ```
   "I detected a new environment that's not in the config.

   Proposed environment config:
   {
     \"auth\": {
       \"url\": \"https://new-app.example.com\"
     }
   }

   Add this environment to environment_config.json?"

   Options:
   1. Yes, add as shown (Recommended)
   2. Modify environment name or URL
   ```
4. **If user approves (option 1):**
   - Read existing environment_config.json
   - Add new environment entry from template
   - Write updated environment_config.json using Write tool
   - Retry gate call
   - Verify gate returns `status: "pass"` with `detected_env_id` matching new environment
5. **If user wants to modify (option 2):**
   - Ask user for modified environment name and/or URL
   - Create modified template
   - Add modified environment to config
   - Retry gate call

**CRITICAL:** Never auto-scaffold environment config without user approval. Environment config affects test execution and requires user decision.

**Idempotent:** If environment already exists in config, gate returns `pass` (no scaffolding or approval needed).

**Temporary Stopgap:** This manual approval step will be replaced by full HITL system in future version.

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
│  - Auto-detects environment from URL (DEF-062)                              │
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
                         │     │ AI ASKS USER    │  │  ASK USER   │
                         │     │ approve env?    │  │  (fix issue)│
                         │     └─────────┬───────┘  └─────────────┘
                         │               │
                         │               ▼
                         │     ┌─────────────────┐
                         │     │ USER APPROVES   │
                         │     └─────────┬───────┘
                         │               │
                         │               ▼
                         │     ┌─────────────────┐
                         │     │ AI ADDS to      │
                         │     │ config.json     │
                         │     └─────────┬───────┘
                         │               │
                         │               ▼
                         │     ┌─────────────────┐
                         │     │ AI RETRIES      │
                         │     │ qg_user_input   │
                         │     └─────────┬───────┘
                         │               │
                         └───────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  STATE SAVED           │
                         │  (by qg_user_input)    │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PROCEED TO STEP 3     │
                         └────────────────────────┘
```

---

*Next: Step 3 - AI Processing*
