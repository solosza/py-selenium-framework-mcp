<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 1: User Input

**Purpose:** Capture test requirement, persona, URL, and workflow identifier from user.

**Workflow Version:** v3.0 (5-Step Pair Programming Workflow)

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 1 - User Input |
| **Dependencies** | None (first step) |
| **Input** | User describes test requirement |
| **Output** | `persona`, `URL`, `role_name`, `workflow`, `raw_requirement`, `detected_env_id` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | Describes test requirement (persona, action, URL) |
| **AI** | Asks questions, extracts data, auto-detects environment |
| **Tool** | `qg_user_input` validates all fields, saves state on PASS |

---

## C. Skill Instruction

```
PRE-CHECK:
- None (first step)

ACTION:
- ASK user: "What test do you want to create?"
  Format: "As a [persona], I want to [action]"
  Example: "As a sales representative, I want to submit a service inquiry"

- ASK user: "What is the URL for this action?"
  Example: "https://example.com/inquiries"

- ASK user: "Workflow identifier?"
  Explanation: "This creates folders at framework/pages/{workflow}/ and tests/{workflow}/
               Use to organize tests by: test run (helios7), feature (checkout-v2), sprint (auth-sprint-2)"

- EXTRACT from requirement:
  - persona: Extract from "As a [X]" pattern
  - role_name: Convert persona to PascalCase (sales representative → SalesRepresentative)
  - raw_requirement: Store full user requirement verbatim

- AUTO-DETECT environment:
  - Check URL against framework/resources/config/environment_config.json
  - If match found → detected_env_id = environment name
  - If no match → ASK user: "Unknown environment. Should I create config for '{url_domain}'?"

VALIDATE:
- CALL qg_user_input with all extracted data

RETRY:
- If gate FAIL: RE-ASK the invalid/missing field
- If gate NEEDS_RETRY with scaffolding: Create files/dirs, retry gate
- No max retries (user provides input, not AI)

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, user inputs, extracted fields, gate result, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | None (data collection step) |
| **Quality Gate** | `qg_user_input` |
| **Gate Mode** | POST-only (validates after user input) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `persona`, `URL`, `role_name`, `workflow`, `raw_requirement`, `detected_env_id` |
| **Who Saves** | Quality gate (`qg_user_input`) |
| **When Saved** | On gate PASS |
| **State Schema** | See below |

```json
{
  "step": 1,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "persona": "sales representative",
    "URL": "https://example.com/inquiries",
    "role_name": "SalesRepresentative",
    "workflow": "helios8",
    "raw_requirement": "As a sales representative, I want to submit a service inquiry",
    "detected_env_id": "helios1"
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-01 (persona required), DD-02 (URL required), DD-07 (workflow determined) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 2 until all fields valid** |

**Validation Checks:**

| Check | Rule |
|-------|------|
| `persona` | Must be present, extracted from "As a [X]" pattern |
| `URL` | Must be valid HTTP/HTTPS URL |
| `role_name` | Must be PascalCase conversion of persona |
| `workflow` | Must be valid identifier (alphanumeric + hyphen/underscore) |
| `raw_requirement` | Must be present (full user input) |

---

## G. Error Handling

**Failure Behavior:**

| Issue | Behavior |
|-------|----------|
| User skips persona | RE-ASK: "I need a persona to proceed. Example: 'As a sales representative, I want to...'" |
| Missing URL | RE-ASK: "What is the URL where this action happens?" |
| Invalid URL format | RE-ASK: "Please provide a valid HTTP/HTTPS URL" |
| Missing workflow | RE-ASK: "What workflow identifier should I use? (e.g., helios7, checkout-v2)" |
| Unknown environment | ASK: "Should I create environment config for '{domain}'? (yes/no)" |

**Error Message Templates:**

Missing persona:
```
"I need a persona to create the test.

Please describe the test in this format:
'As a [persona], I want to [action]'

Example: As a sales representative, I want to submit a service inquiry"
```

Missing URL:
```
"What is the URL where this action takes place?

Example: https://example.com/inquiries"
```

Missing workflow:
```
"What workflow identifier should I use?

This creates folders at:
- framework/pages/{workflow}/
- tests/{workflow}/

Use to organize tests by test run, feature, or sprint.

Example: helios7, checkout-v2, auth-sprint-2"
```

---

## H. Environment Auto-Detection

**Purpose:** Detect which environment config to use based on URL.

**Process:**
1. Extract domain from URL (e.g., "example.com" from "https://example.com/inquiries")
2. Check `framework/resources/config/environment_config.json` for matching base_url
3. If match found → `detected_env_id` = environment name
4. If no match → Ask user to create new environment config

**Example environment_config.json:**
```json
{
  "helios1": {
    "base_url": "https://helios-app.com",
    "browser": "chrome"
  },
  "staging": {
    "base_url": "https://staging.example.com",
    "browser": "chrome"
  }
}
```

**If URL is "https://helios-app.com/inquiries":**
- Match found: `detected_env_id = "helios1"`

**If URL is "https://unknown-site.com/inquiries":**
- No match: Ask user "Unknown environment. Should I create config for 'unknown-site.com'?"

---

## I. User Communication

**What to Show:**
- Persona extracted
- Role name derived
- Workflow identified
- Environment detected (if applicable)

**Output Format:**
```
✓ Step 1: User Input
  • Persona: sales representative
  • Role: SalesRepresentative
  • Workflow: helios8
  • Environment: helios1
```

---

## J. Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 1: USER INPUT                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  AI ASKS:              │
                         │  "What test do you     │
                         │   want to create?"     │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  USER provides         │
                         │  requirement           │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  AI ASKS: "URL?"       │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  USER provides URL     │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  AI ASKS:              │
                         │  "Workflow ID?"        │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  USER provides         │
                         │  workflow              │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  AI EXTRACTS:          │
                         │  - persona             │
                         │  - role_name           │
                         │  - raw_requirement     │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  AI AUTO-DETECTS       │
                         │  environment           │
                         └────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_user_input                                                 │
│  - Validates all fields                                                     │
│  - Saves state on PASS                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐           ┌──────────┐
                    │  PASS    │           │  FAIL    │
                    └────┬─────┘           └────┬─────┘
                         │                       │
                         │                       ▼
                         │              ┌─────────────┐
                         │              │  RE-ASK     │
                         │              │  USER       │
                         │              └─────────────┘
                         │
                         ▼
                         ┌────────────────────────┐
                         │  STATE SAVED           │
                         │  (by qg_user_input)    │
                         └────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PROCEED TO STEP 2     │
                         └────────────────────────┘
```

---

*Next: Step 2 - Pre-flight Configuration*
