# Step 5: Tool 2 - Discover Elements

**Purpose:** Discover interactive elements on target page for POM generation.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 5 - Discover Elements (Tool 2) |
| **Dependencies** | Step 4 complete (test_scenarios exist), Step 1 for credential_strategy |
| **Input** | `URL` from Step 2, `credential_strategy` from Step 1 |
| **Output** | `discovered_elements` array |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | None (unless AI fails 3 times, then user decides resolution) |
| **AI** | Checks credential_strategy, logs in if needed (DD-20), prepares page state, navigates to reveal dynamic elements, calls gate and operation |
| **Tool** | `qg_discovered_elements` validates input/output, `discover_page_elements` discovers elements, operation saves state on SUCCESS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 4 complete (test_scenarios exist in state)
- READ credential_strategy from Step 1 state

PREPARE (Credential Handling):
- IF credential_strategy = "none": Skip to page navigation
- IF credential_strategy = "static": Load creds from test_users.json, login via auth flow
- IF credential_strategy = "dynamic": Register new user, save creds, login
- IF credential_strategy = "self-contained": Register in-session, login (don't persist)

NAVIGATION:
- NAVIGATE to target URL
- PREPARE page state (click/interact to reveal dynamic elements)
- WAIT for async content to load

┌─────────────────────────────────────────────────────────────────────────────┐
│  DD-33 DECISION POINT (MANDATORY)                                            │
└─────────────────────────────────────────────────────────────────────────────┘

  Was Playwright used to prepare page state (login, click, modal, form submit)?
      │
      ├── YES ──► MUST use DD-33 (Playwright snapshot extraction)
      │           discovery_method = "playwright"
      │
      │           DD-33 FLOW:
      │           1. browser_snapshot → get accessibility tree
      │           2. AI extracts relevant elements (token-optimized)
      │           3. AI builds elements array in Tool 2 format
      │           4. CALL qg_discovered_elements PRE with discovery_method="playwright"
      │           5. SKIP Tool 2 (already have elements)
      │           6. CALL qg_discovered_elements POST with discovery_method="playwright"
      │           7. Proceed to Tool 3
      │
      └── NO ───► May use Tool 2
                  discovery_method = "tool2"

                  TOOL 2 FLOW:
                  1. CALL qg_discovered_elements PRE with discovery_method="tool2"
                  2. CALL discover_page_elements (OPERATION)
                  3. CALL qg_discovered_elements POST with discovery_method="tool2"

VALIDATE:
- PRE: Validate URL reachable, page_name provided, discovery_method declared
- POST: Validate elements array returned, at least 1 interactive element

RETRY:
- If PRE-VALIDATE fails: AI adjusts page state (max 3 attempts)
- If POST-VALIDATE fails: AI re-prepares page, retries (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | `discover_page_elements` |
| **Quality Gate** | `qg_discovered_elements` |
| **Gate Mode** | PRE+POST (validates page ready before, elements found after) |

**Tool 2 Parameters (DD-20 Dynamic Flow):**

| Parameter | Type | When Used |
|-----------|------|-----------|
| `url` | string | STATIC flow - Tool creates driver |
| `headless` | bool | STATIC flow - default True |
| `driver_session` | WebDriver | DYNAMIC flow - AI passes prepared driver |
| `scope` | string | DYNAMIC flow - CSS selector to limit discovery |

**DYNAMIC Flow (DD-20):** When page requires interaction (login, hover, modal) before element discovery, AI prepares page state first, then passes `driver_session` to Tool 2.

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `discovered_elements` (from tool), `auth_completed` (AI-tracked), `page_name` (AI-tracked) |
| **Who Saves** | Operation tool saves `discovered_elements`; AI saves `auth_completed`, `page_name` |
| **When Saved** | On operation SUCCESS (after POST-VALIDATE passes) |
| **State Schema** | See below |

**Note:** Tool 2 only outputs `elements[]` and `metadata`. AI tracks `auth_completed` and `page_name` separately based on workflow execution.

```json
{
  "step": 5,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "auth_completed": true,
    "auth_strategy_used": "static",
    "page_name": "LoginPage",
    "discovered_elements": [
      {
        "name": "email_input",
        "type": "textbox",
        "selector": "#email",
        "selector_type": "css"
      },
      {
        "name": "password_input",
        "type": "textbox",
        "selector": "#passwd",
        "selector_type": "css"
      },
      {
        "name": "submit_button",
        "type": "button",
        "selector": "#SubmitLogin",
        "selector_type": "css"
      }
    ]
  }
}
```

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-19 (tool import), DD-20 (dynamic element prep), DD-21 (AI-SDET collaboration), DD-24 (credential strategy from Step 1), DD-33 (Playwright snapshot for dynamic) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 6 until elements discovered** |

**DD-33 Enforcement (CRITICAL):**

| Condition | Required Action | Violation Response |
|-----------|-----------------|-------------------|
| Playwright prepared page state | MUST use DD-33 (snapshot extraction) | BLOCKED if Tool 2 used after Playwright prep |
| Static page (no prep needed) | May use Tool 2 | N/A |
| discovery_method not declared | Gate fails | Must declare "playwright" or "tool2" |

**PRE-Validation Checks:**

| Check | Rule |
|-------|------|
| `URL` | Reachable, returns 200 |
| `page_name` | Provided by AI |
| Page state | Ready for discovery (no loading spinners) |

**POST-Validation Checks:**

| Check | Rule |
|-------|------|
| `discovered_elements` | Array present |
| Element count | At least 1 interactive element |
| Each element | Has name, type, selector, selector_type |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| Login fails | AI retries auth flow (max 3) |
| Page not ready | AI waits/retries navigation (max 3) |
| No elements found | AI re-prepares page state, retries (max 3) |
| After 3 total failures | STOP → REPORT → USER DECIDES |

**Known Defects:** DD-20 enforcement gap - AI sometimes forgets to prepare page state for dynamic elements

**DD-21 AI-SDET Collaboration:**
When AI cannot discover elements automatically (complex modals, dynamic content):
1. AI reports what it sees and what's missing
2. User (SDET) provides guidance (selectors, interaction sequence)
3. AI retries with user guidance
4. If still failing after 3 attempts → STOP → USER DECIDES

**Error Message Template (After 3 Failures):**

```
"I've attempted 3 times and cannot discover elements.

Credential handling:
[show auth result - success/fail]

Page state:
[show current URL, page title]

Discovery result:
[show what was found or error]

How should we proceed?
1. Different URL - Go back to Step 2
2. Manual element list - You provide selectors
3. Abort workflow - Stop and log issue"
```

---

## Credential Strategy Detail (AI Reference)

| Strategy | AI Actions |
|----------|------------|
| `none` | Skip auth entirely, proceed to page navigation |
| `static` | Read `tests/data/test_users.json` → navigate to login page → enter creds → submit → verify logged in |
| `dynamic` | Navigate to registration → fill form → submit → save creds to test_users.json → login with new creds |
| `self-contained` | Navigate to registration → fill form → submit → login → DO NOT persist creds |

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 5: TOOL 2 - DISCOVER ELEMENTS                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 4 complete?      │
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
              │  READ credential_   │     │  BLOCKED        │
              │  strategy from      │     │  Go to Step 4   │
              │  Step 1             │     └─────────────────┘
              └─────────────────────┘
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │  "none"  │   │ "static" │   │"dynamic" │
    └────┬─────┘   │"self-con"│   └────┬─────┘
         │         └────┬─────┘        │
         │              │              │
         │              ▼              ▼
         │    ┌─────────────────────────────┐
         │    │  LOGIN / REGISTER           │
         │    │  (per strategy)             │
         │    └─────────────────────────────┘
         │              │
         └──────────────┼──────────────────────
                        ▼
              ┌─────────────────────┐
              │  NAVIGATE to URL    │
              │  PREPARE page state │
              │  (reveal dynamic)   │
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_discovered_elements (PRE-VALIDATE)                         │
│  - Validates page ready for discovery                                       │
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
              │  discover_page_     │     │  AI preps page  │
              │  elements           │     └─────────────────┘
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_discovered_elements (POST-VALIDATE)                        │
│  - Validates elements found                                                 │
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
              │  (by operation)     │  │  AI re-preps page   │
              └─────────────────────┘  └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 6  │
              └─────────────────────┘
```

---

## H. Tool Chain Data Contracts (DD-26)

**Input Contract (from Step 4):**

| Field | Source | Required |
|-------|--------|----------|
| `URL` | Step 2 state | Yes |
| `test_scenarios` | Step 4 state | No (for context) |

**Tool 2 Input:**

```python
# STATIC flow:
arguments = {
    "url": "http://automationpractice.pl/...",
    "headless": True
}

# DYNAMIC flow (DD-20):
arguments = {
    "driver_session": driver,  # AI's prepared WebDriver
    "scope": "#modal_container"  # Optional: limit to modal
}
```

**Output Contract (Tool 2 provides for Step 6):**

```json
{
  "elements": [
    {
      "suggested_name": "EMAIL",
      "element_type": "inputs",
      "locator_id": "#email",
      "locator_css": "",
      "locator_xpath": "//input[@id='email']"
    }
  ],
  "metadata": {
    "discovered_elements": [
      {"name": "EMAIL", "type": "inputs", "locator": "#email"}
    ]
  }
}
```

**CRITICAL:** Pass `elements[]` array directly to Tool 3. Do NOT transform keys.

---

## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-05-01 | `credential_strategy` must be passed in PRE input_data (not read from state) | Explicit contract - AI passes what it read from Step 1 state. Maintains separation between state reading (AI) and validation (gate). | `validate_pre()` |
| IC-05-02 | `page_name` PascalCase pattern: `^[A-Z][a-zA-Z0-9]*$` | Flexible enough for `LoginPage`, `CartModal`, `CheckoutForm`. Allows digits for edge cases like `OAuth2Page`. | `validate_post()` |
| IC-05-03 | At least one locator (`locator_id`, `locator_css`, `locator_xpath`) must be non-empty string | Empty string locators are useless for POM generation. Element must have at least one usable locator. | `validate_post()` |

**Date Added:** 2025-12-21
**Task Reference:** Task 8.0 (qg_discovered_elements)

---

*Next: Step 6 - Generate POM (Tool 3)*
