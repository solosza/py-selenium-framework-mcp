<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 4: Tool 2 - Discover Elements

**NOTE:** This is Step 4 in the 5-step workflow (v4.0).
The old 11-step workflow was archived on 2026-01-22.

**Purpose:** Discover interactive elements on target page for manual POM construction.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 4 - Discover Elements (Tool 2) |
| **Dependencies** | Step 3 complete (bdd_scenarios, expected_states, intent exist), Step 2 for credential_strategy |
| **Input** | `URL` from Step 1, `credential_strategy` from Step 2 |
| **Output** | `discovered_elements` array |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | None (unless AI fails 3 times, then user decides resolution) |
| **AI** | Checks credential_strategy, logs in if needed (DD-20), prepares page state, navigates to reveal dynamic elements, calls gate and operation |
| **Tool** | `qg_discovered_elements` validates input/output, `discover_page_elements` discovers elements, operation saves state on SUCCESS |

---

## ⚠️ CRITICAL: Runtime HITL - Immediate Triggers

**READ THIS FIRST. This section takes precedence over all other instructions.**

### Rule: STOP on ANY Failure

When ANY failure occurs during discovery, you MUST:
1. **STOP** - Do not attempt autonomous fixes
2. **REPORT** - Show user exactly what failed and why
3. **WAIT** - Get human decision before proceeding

### Failure Types That Trigger HITL

| Category | Examples | Action |
|----------|----------|--------|
| **Navigation** | Page not found, timeout, redirect loop | STOP → REPORT → HITL |
| **Click/Interaction** | Element not clickable, stale reference, covered by overlay | STOP → REPORT → HITL |
| **Element State** | Element not visible, disabled, detached from DOM | STOP → REPORT → HITL |
| **Page State** | Unexpected modal, loading spinner won't clear, wrong page | STOP → REPORT → HITL |
| **Authentication** | Login failed, session expired, access denied | STOP → REPORT → HITL |
| **Validation** | RuntimeValidator returns is_valid=false | STOP → REPORT → HITL |
| **Network** | API errors, resource blocked, CORS issues | STOP → REPORT → HITL |
| **Unexpected UI** | Layout different than expected, missing elements | STOP → REPORT → HITL |

### What NOT To Do

❌ **Do NOT** retry silently 3 times then report
❌ **Do NOT** assume you can fix it autonomously
❌ **Do NOT** skip elements and continue
❌ **Do NOT** proceed without human confirmation on failure

### HITL Report Template (On Any Failure)

```
===== DISCOVERY FAILURE =====

What happened: [Specific failure]
Where: [URL, element, action]
Error: [Exact error message]

What I observed: [Browser state description]

HOW SHOULD WE PROCEED?
1. AI Investigates - I analyze and propose fix
2. Provide Guidance - You tell me what you see
3. Skip + Continue - Proceed without this element
4. Abort - Stop workflow entirely
5. Other - Describe what you want to do

Enter choice (1-5) or describe how you'd like to proceed:
```

**This is the MVP approach: Strong protocol enforcement + existing gates.**

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 3 complete (bdd_scenarios, expected_states, intent exist in state)
- READ credential_strategy from Step 2 state

┌─────────────────────────────────────────────────────────────────────────────┐
│  INITIALIZE NAVIGATION TRACKER (MANDATORY - DD-44 ENFORCEMENT)               │
└─────────────────────────────────────────────────────────────────────────────┘

BEFORE any navigation, create tracker:

from mcp_server.utils.scope_discovery import create_navigation_tracker

# Create tracker with visual feedback (for Playwright)
def eval_js(js_code):
    return mcp__playwright__browser_evaluate(function=js_code)

tracker = create_navigation_tracker(evaluate_fn=eval_js)

**CRITICAL:** Call tracker.register_page(url) AFTER EVERY navigation.
This is the ONLY reliable way to detect multi-page workflows.

PREPARE (Credential Handling):
- IF credential_strategy = "none": Skip to page navigation
- IF credential_strategy = "static":
  - Load creds from test_users.json
  - Navigate to login page
  - **tracker.register_page(login_url)**  ← MANDATORY
  - Perform login
- IF credential_strategy = "dynamic":
  - Navigate to registration
  - **tracker.register_page(registration_url)**  ← MANDATORY
  - Register user, save creds, login
- IF credential_strategy = "self-contained":
  - Navigate to registration
  - **tracker.register_page(registration_url)**  ← MANDATORY
  - Register in-session, login (don't persist)

NAVIGATION:
- NAVIGATE to target URL
- **tracker.register_page(target_url)**  ← MANDATORY
- PREPARE page state (click/interact to reveal dynamic elements)
- WAIT for async content to load

GET SCOPE RESULT (BEFORE DISCOVERY):
- scope_result = tracker.get_scope_result()
- This finalizes page tracking and provides scope_result for gate
- **page_count = scope_result.page_count**  ← Use this for multi-page detection

┌─────────────────────────────────────────────────────────────────────────────┐
│  DISCOVERY METHOD: PLAYWRIGHT ONLY (DD-33)                                   │
└─────────────────────────────────────────────────────────────────────────────┘

  **IMPORTANT:** Tool 2 (discover_page_elements) is DEPRECATED.
  Always use Playwright snapshot extraction for element discovery.
  This gives AI visibility into navigation failures and enables Runtime HITL.

  PLAYWRIGHT DISCOVERY FLOW (for EACH page in scope_result.pages):

  1. NAVIGATE to target URL:
     ```python
     mcp__playwright__browser_navigate(url=target_url)
     ```
     ⚠️ If navigation fails (404, timeout, error) → TRIGGER RUNTIME HITL (see Section B above)

  2. TAKE SNAPSHOT:
     ```python
     mcp__playwright__browser_snapshot()
     ```
     → Returns accessibility tree with interactive elements

  3. AI EXTRACTS relevant elements from snapshot (token-optimized)
     - Look for: inputs, buttons, links, selects, textareas
     - Build elements array in standard format

  4. CALL qg_discovered_elements PRE with:
     - discovery_method="playwright"
     - scope_result=scope_result.to_dict() (MANDATORY if multi-page)

  5. CALL qg_discovered_elements POST with:
     - discovery_method="playwright"
     - elements=<extracted elements array>
     - scope_result=scope_result.to_dict() (MANDATORY if multi-page)

  6. If multi-page: repeat for next page

  7. Proceed to Tool 3

VALIDATE:
- PRE: Validate URL reachable, page_name provided, discovery_method declared
- POST: Validate elements array returned, at least 1 interactive element

┌─────────────────────────────────────────────────────────────────────────────┐
│  VALIDATE ELEMENTS (MANDATORY - TRIGGERS VISUAL FEEDBACK)                    │
└─────────────────────────────────────────────────────────────────────────────┘

After discovery, MUST validate each element via RuntimeValidator:

1. INITIALIZE visual feedback:
   ```python
   from utils.runtime_validator import RuntimeValidator
   from utils.visual_feedback import VisualFeedback

   # VisualFeedback is injected into RuntimeValidator via constructor
   visual = VisualFeedback(evaluate_fn=browser_evaluate)
   validator = RuntimeValidator(visual_feedback=visual)
   visual.initialize()
   ```

2. For EACH discovered element:
   ```python
   result = validator.validate_element(element)
   # RuntimeValidator automatically calls:
   #   - visual.highlight_valid(ref) if valid
   #   - visual.highlight_invalid(ref, error_category) if invalid
   ```

3. COLLECT validation_results:
   ```python
   validation_results = {
       "valid_count": N,
       "error_count": M,
       "elements": [
           {"name": "...", "ref": "...", "is_valid": True/False, "error_category": "..."}
       ]
   }
   ```

4. PASS validation_results to qg_discovered_elements POST

**Why Mandatory:** Visual feedback shows user which elements passed/failed validation
in real-time. Skipping RuntimeValidator = no visual highlights = poor user experience.

RETRY:
- If PRE-VALIDATE fails: AI adjusts page state (max 3 attempts)
- If POST-VALIDATE fails: AI re-prepares page, retries (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES

POST-ACTION:
- WRITE transcript entry to tests/_reports/<run_id>/workflow_transcript.md
- Include: step name, pages discovered, element counts, PRE/POST gate results, timestamp
- Append mode (don't overwrite existing content)
- Create directory and file on first write if they don't exist

┌─────────────────────────────────────────────────────────────────────────────┐
│  AUDIT-BASED NAVIGATION TRACKING (Task 26.0 - FR-14.8)                      │
└─────────────────────────────────────────────────────────────────────────────┘

**PASS 0: Navigation-First Multi-Page Detection**

The quality gate automatically detects multi-page workflows by reading navigation
history from the audit log. This provides MORE RELIABLE detection than BDD-only.

HOW IT WORKS (Automatic - No AI action required):
1. Gate reads audit log for browser_navigate calls
2. Extracts URLs, deduplicates
3. Infers page names from URLs (e.g., /parabank/login.htm → ParabankLoginPage)
4. Builds scope_result with detected pages
5. Falls back to BDD detection if no navigation calls exist

WHEN NAVIGATION TRACKING ACTIVATES:
- AI used browser_navigate during workflow (login flow, multi-step form, etc.)
- Navigation calls were logged to audit trail
- Gate automatically reads and processes navigation history

URL → PAGE NAME INFERENCE:
- Single segment: /checkout → CheckoutPage
- Multi-segment: /accounts/overview → AccountsOverviewPage
- With domain: /parabank/login.htm → ParabankLoginPage

BENEFIT:
- Captures ACTUAL navigation flow (not just BDD intent)
- More accurate page detection
- Automatic - no explicit scope_discovery call needed
- Backward compatible - BDD fallback ensures old workflows work

AI ACTION:
✓ Navigation tracking is AUTOMATIC - gate handles it
✓ Continue using existing navigation tracker for consistency
✓ Both approaches work together (audit-based + tracker-based)
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
| **State Saved** | `discovered_elements` (from tool), `validation_results` (from RuntimeValidator), `auth_completed` (AI-tracked), `page_name` (AI-tracked) |
| **Who Saves** | Operation tool saves `discovered_elements`; RuntimeValidator produces `validation_results`; AI saves `auth_completed`, `page_name` |
| **When Saved** | On operation SUCCESS (after POST-VALIDATE passes) |
| **State Schema** | See below |

**Note:** Tool 2 only outputs `elements[]` and `metadata`. RuntimeValidator produces `validation_results` with visual feedback. AI tracks `auth_completed` and `page_name` separately based on workflow execution.

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
| **Rules That Apply** | DD-19 (tool import), DD-20 (dynamic element prep), DD-21 (AI-SDET collaboration), DD-24 (credential strategy from Step 1), DD-33 (Playwright snapshot for dynamic), DD-46 (visual feedback via RuntimeValidator) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 6 until elements discovered AND validated** |

**DD-46 Visual Feedback Enforcement (MANDATORY):**

| Condition | Required Action | Violation Response |
|-----------|-----------------|-------------------|
| Elements discovered | MUST call RuntimeValidator for each element | BLOCKED if validation_results missing |
| RuntimeValidator called | Automatically triggers VisualFeedback | Visual highlights appear in browser |
| validation_results missing in POST | Gate fails | "Must validate elements via RuntimeValidator" |

**DD-33 Enforcement (CRITICAL):**

| Condition | Required Action | Violation Response |
|-----------|-----------------|-------------------|
| Any page | MUST use Playwright snapshot extraction | Tool 2 is DEPRECATED |
| discovery_method not declared | Gate fails | Must declare "playwright" |
| discovery_method="tool2" | Gate warns (deprecated) | Use "playwright" instead |

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

**Failure Types:**

| Type | Description | Response |
|------|-------------|----------|
| **Structural** | AI passed wrong parameters (missing fields, wrong types) | `fail` response - AI fixes without human |
| **Runtime** | Discovery/validation issues (elements not found, timeout, page state) | `NEEDS_RETRY` with `hitl_required` - Human triage |

**Runtime Failure Indicators (triggers HITL):**
- "elements is empty"
- "no valid locator"
- "error_count" > 0
- "validation failed"
- "element not found"
- "timeout"
- "stale"
- "not interactable"

**HITL Triage Workflow (on runtime failure):**

When qg_discovered_elements returns `NEEDS_RETRY` with `fix_applied: "hitl_required"`:

```
===== STEP 4: DISCOVERY ISSUE =====

Page: [page_name]
URL: [current_url]
Discovery Method: playwright
Elements Found: [count]

Result: [error message]
[Failed elements summary if available]

AI Observation (Confidence: XX%):
[likely_cause]
[observation]

==========================================

HOW SHOULD WE PROCEED?

1. AI Investigates + Attempts Fix
   -> AI analyzes the issue and proposes a solution
   -> Re-runs discovery after fix attempt

2. Provide Guidance
   -> You describe what you observe in the browser
   -> AI follows your instructions

3. Skip + Continue
   -> Proceed without failed elements
   -> Can add elements manually later

4. Abort Workflow
   -> Stop the workflow entirely
   -> Review and restart when ready

5. Other
   -> Describe what you want to do
   -> AI follows your instructions

Enter choice (1-5):
```

**Triage Decision Actions:**

| Option | Action | Blocking? |
|--------|--------|-----------|
| **1. AI Investigates** | AI analyzes diagnostic data, proposes fix, re-runs | NO |
| **2. Provide Guidance** | User describes what they see, AI follows | YES (awaits input) |
| **3. Skip + Continue** | Proceed with valid elements only | NO |
| **4. Abort** | Stop workflow entirely | YES |
| **5. Other** | User describes custom action, AI follows | YES (awaits input) |

**Key Rule:** AI must NOT proceed without user decision when hitl_required is returned.

**Legacy Behavior (3 failures):**

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

## Navigation Tracking Example (DD-44 Enforcement)

**This is how AI MUST track pages during Step 5:**

```python
from mcp_server.utils.scope_discovery import create_navigation_tracker

# 1. Initialize tracker BEFORE any navigation
def eval_js(js_code):
    return mcp__playwright__browser_evaluate(function=js_code)

tracker = create_navigation_tracker(evaluate_fn=eval_js)

# 2. Credential handling (static strategy example)
login_url = "https://parabank.parasoft.com/parabank/index.htm"
mcp__playwright__browser_navigate(url=login_url)
tracker.register_page(login_url)  # ← Track login page

# Perform login...
# (fill username, password, click submit)

# 3. Navigate to target workflow page
transfer_url = "https://parabank.parasoft.com/parabank/transfer.htm"
mcp__playwright__browser_navigate(url=transfer_url)
tracker.register_page(transfer_url)  # ← Track transfer page

# 4. Get scope result BEFORE calling gates
scope_result = tracker.get_scope_result()
# → ScopeResult(page_count=2, pages=[LoginPage, TransferFundsPage])

# 5. Convert to dict for gate calls
scope_dict = {
    "page_count": scope_result.page_count,
    "pages": [
        {"name": p.name, "order": p.order, "url": p.url, "depends_on": p.depends_on}
        for p in scope_result.pages
    ]
}

# 6. Discover elements for EACH page
for page_info in scope_result.pages:
    # Navigate to page if needed (may already be there)
    # Discover input elements (PASS 1)
    mcp__qa-automation__qg_discovered_elements(
        mode="PRE",
        url=page_info.url,
        page_name=page_info.name,
        credential_strategy="static",
        discovery_method="playwright",
        type="input",
        scope_result=scope_dict  # ← MANDATORY for multi-page
    )

    # Extract elements from snapshot...
    # Call POST gate...

    # Discover output elements (PASS 2)
    # ... same pattern
```

**Key Points:**
- tracker.register_page() called AFTER EVERY browser_navigate()
- tracker.get_scope_result() called ONCE after all navigation complete
- scope_result passed to EVERY gate call (PRE and POST)
- Gate tracks progress: "2/2 pages discovered"

---

## Multi-Page Discovery (DD-44) - MANDATORY CHECK

**When does this apply?** When BDD scenarios reference multiple pages (e.g., wizard flows, multi-step forms).

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  DD-44 MULTI-PAGE SCOPE DISCOVERY (MANDATORY)                                │
└─────────────────────────────────────────────────────────────────────────────┘

BEFORE first element discovery:
1. Call scope_discovery.analyze_workflow(bdd_scenarios)
   → Returns: {page_count: N, pages: [{name: "Page1Page", order: 1}, ...]}

2. IF page_count > 1:
   → Gate REQUIRES scope_result parameter
   → Must discover elements for EACH page before Step 6

DISCOVERY LOOP (for each page in scope):
   ┌─────────────────────────────────────────┐
   │  For page in scope_result.pages:       │
   │    1. Navigate to page URL             │
   │    2. Prepare page state (reveal       │
   │       dynamic elements)                │
   │    3. Call qg_discovered_elements PRE  │
   │       with scope_result                │
   │    4. Extract elements (Playwright     │
   │       snapshot or Tool 2)              │
   │    5. Call qg_discovered_elements POST │
   │       with scope_result                │
   │    6. Gate tracks progress:            │
   │       discovered_pages[page_name] =    │
   │       elements                         │
   └─────────────────────────────────────────┘

STEP 6 BLOCKED UNTIL:
- is_discovery_complete() returns True
- All pages in scope have been discovered

GATE ENFORCEMENT:
| Check | When | Behavior |
|-------|------|----------|
| Multi-page detected, no scope_result | PRE Step 5 | FAIL: "Call scope_discovery first" |
| Discovery incomplete | PRE Step 6 | FAIL: "N/M pages discovered" |
| scope_result.page_count mismatch | POST Step 5 | Warn but allow |
```

**Example Multi-Page Flow (4-Step Wizard):**

```python
# 1. Analyze scope
from utils.scope_discovery import ScopeDiscovery
discovery = ScopeDiscovery()
scope_result = discovery.analyze_workflow(bdd_scenarios)
# → page_count: 4, pages: [SearchPage, CustomerPage, ContactsPage, AddressPage]

# 2. For each page, discover elements
for page_info in scope_result.pages:
    # Navigate to reveal page
    # ... playwright interactions ...

    # PRE-VALIDATE (pass scope_result)
    pre_result = qg_discovered_elements.validate_pre({
        "mode": "PRE",
        "url": page_info.entry_url,
        "page_name": page_info.name,
        "credential_strategy": "none",
        "discovery_method": "playwright",
        "scope_result": scope_result.to_dict()  # REQUIRED for multi-page
    })

    # Extract elements from snapshot
    elements = extract_from_snapshot(...)

    # POST-VALIDATE (pass scope_result)
    post_result = qg_discovered_elements.validate_post({
        "mode": "POST",
        "elements": elements,
        "page_name": page_info.name,
        "scope_result": scope_result.to_dict()
    })
    # → Returns: {status: "pass", multi_page_progress: {pages_discovered: N, ...}}

# 3. Verify complete before Step 6
if not qg_discovered_elements.is_discovery_complete():
    # BLOCKED - continue discovery loop
    pass
else:
    # PROCEED to Step 6
    pass
```

---

## Two-Pass Discovery (DEF-045) - Input + Output Elements

**Purpose:** Discover BOTH input elements (forms, buttons) AND output elements (confirmations, messages) to enable real state-check methods in POMs (not guesses).

**Problem Solved:** AI previously generated state-check methods without observing confirmation pages, leading to guessed implementations (DEF-045).

**Solution:** Two-pass discovery per page - PASS 1 for input elements, PASS 2 for output elements.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  TWO-PASS DISCOVERY FLOW (extends DD-44 multi-page loop)                    │
└─────────────────────────────────────────────────────────────────────────────┘

BEFORE discovery:
1. Call scope_discovery.analyze_workflow(bdd_scenarios) → scope_result

PASS 1: INPUT ELEMENT DISCOVERY (for all pages)
   ┌─────────────────────────────────────────┐
   │  For page in scope_result.pages:       │
   │    1. Navigate to input page URL       │
   │       (e.g., login form)               │
   │    2. Prepare page state (reveal       │
   │       forms, buttons)                  │
   │    3. Call qg_discovered_elements PRE  │
   │       with type="input"                │
   │    4. Extract INPUT elements           │
   │       (textboxes, buttons, dropdowns)  │
   │    5. Call qg_discovered_elements POST │
   │       with type="input"                │
   │    6. Gate tracks:                     │
   │       discovered_pages[page_name]      │
   │         ["input_elements"] = elements  │
   └─────────────────────────────────────────┘

PASS 2: OUTPUT ELEMENT DISCOVERY (for all pages)
   ┌─────────────────────────────────────────┐
   │  For page in scope_result.pages:       │
   │    1. Navigate/trigger to OUTPUT page  │
   │       (e.g., confirmation after login) │
   │    2. Prepare page state (submit form, │
   │       reveal messages)                 │
   │    3. Call qg_discovered_elements PRE  │
   │       with type="output"               │
   │    4. Extract OUTPUT elements          │
   │       (success messages, error msgs,   │
   │        confirmation text)              │
   │    5. Call qg_discovered_elements POST │
   │       with type="output"               │
   │    6. Gate tracks:                     │
   │       discovered_pages[page_name]      │
   │         ["output_elements"] = elements │
   └─────────────────────────────────────────┘

CHECKPOINT: Before Step 6
- Verify ALL pages have BOTH input_elements AND output_elements
- is_discovery_complete() checks both types present for each page
```

**Type Parameter (NEW):**

| Type | When | Elements Discovered |
|------|------|---------------------|
| `input` (default) | PASS 1 | Forms, buttons, textboxes, dropdowns - elements user INTERACTS with |
| `output` | PASS 2 | Success messages, error messages, confirmation text - elements user OBSERVES |

**Example Two-Pass Flow:**

```python
from utils.scope_discovery import ScopeDiscovery

# 1. Analyze scope
discovery = ScopeDiscovery()
scope_result = discovery.analyze_workflow(bdd_scenarios)

# PASS 1: Input elements for all pages
for page_info in scope_result.pages:
    # Navigate to INPUT page (e.g., login form)
    browser.navigate(page_info.entry_url)

    # PRE-VALIDATE with type="input"
    pre_result = qg_discovered_elements.validate_pre({
        "mode": "PRE",
        "url": page_info.entry_url,
        "page_name": page_info.name,
        "credential_strategy": "none",
        "discovery_method": "playwright",
        "type": "input",  # NEW: Specify element type
        "scope_result": scope_result.to_dict()
    })

    # Extract INPUT elements (forms, buttons)
    input_elements = extract_input_elements_from_snapshot(...)

    # POST-VALIDATE with type="input"
    post_result = qg_discovered_elements.validate_post({
        "mode": "POST",
        "elements": input_elements,
        "page_name": page_info.name,
        "type": "input",  # NEW: Specify element type
        "validation_results": {...},  # DD-46
        "scope_result": scope_result.to_dict()
    })
    # → Saves to discovered_pages[page_name]["input_elements"]

# PASS 2: Output elements for all pages
for page_info in scope_result.pages:
    # Navigate/trigger to OUTPUT page (e.g., submit form, see confirmation)
    browser.navigate(page_info.entry_url)
    # ... perform action to reveal output (submit form, click button)

    # PRE-VALIDATE with type="output"
    pre_result = qg_discovered_elements.validate_pre({
        "mode": "PRE",
        "url": page_info.confirmation_url,
        "page_name": page_info.name,
        "credential_strategy": "none",
        "discovery_method": "playwright",
        "type": "output",  # NEW: Specify element type
        "scope_result": scope_result.to_dict()
    })

    # Extract OUTPUT elements (messages, confirmations)
    output_elements = extract_output_elements_from_snapshot(...)

    # POST-VALIDATE with type="output"
    post_result = qg_discovered_elements.validate_post({
        "mode": "POST",
        "elements": output_elements,
        "page_name": page_info.name,
        "type": "output",  # NEW: Specify element type
        "validation_results": {...},  # DD-46
        "scope_result": scope_result.to_dict()
    })
    # → Saves to discovered_pages[page_name]["output_elements"]

# 3. CHECKPOINT: Verify BOTH types discovered for ALL pages (NEW - DEF-045)
from tools.gates.qg_discovery_complete import QGDiscoveryComplete

checkpoint_result = QGDiscoveryComplete.validate_pre({})
# → Reads Step 5 state, validates ALL pages have input_elements AND output_elements

if checkpoint_result["status"] == "fail":
    # BLOCKED - missing input or output for some page
    print(f"Discovery incomplete: {checkpoint_result['error']}")
    print(f"Fix: {checkpoint_result['fix_hint']}")
    raise Exception("Discovery checkpoint failed - cannot proceed to Step 6")
else:
    # PROCEED to Step 6 - Generate POMs with BOTH element types
    pass
```

**State Structure (NEW):**

```python
# Step 5 state after two-pass discovery:
{
    "discovered_pages": {
        "LoginPage": {
            "input_elements": [
                {"suggested_name": "EMAIL", "element_type": "textbox", "locator_id": "#email"},
                {"suggested_name": "PASSWORD", "element_type": "textbox", "locator_id": "#passwd"},
                {"suggested_name": "SUBMIT_BTN", "element_type": "button", "locator_id": "#SubmitLogin"}
            ],
            "output_elements": [
                {"suggested_name": "SUCCESS_MESSAGE", "element_type": "text", "locator_css": ".success"},
                {"suggested_name": "ERROR_MESSAGE", "element_type": "text", "locator_css": ".alert-danger"}
            ]
        }
    },
    "pages_discovered": 1,  # Number of pages with BOTH types
    "total_pages": 1,
    "discovery_complete": true  # True only if ALL pages have BOTH types
}
```

**Backward Compatibility:**

- If `type` parameter omitted → defaults to "input"
- Old code calling without `type` still works (single-pass discovery)
- Nested state structure preserves old `discovered_elements` field (last page)

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
│  - Runtime failures → HITL triage (NEEDS_RETRY)                             │
│  - Structural failures → fail response (AI fixes)                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
              ┌──────────┐     ┌──────────────┐   ┌──────────┐
              │  PASS    │     │ NEEDS_RETRY  │   │  FAIL    │
              └────┬─────┘     │ (hitl_req'd) │   │(structural)
                   │           └──────┬───────┘   └────┬─────┘
                   │                  │                │
                   │                  ▼                ▼
                   │    ┌────────────────────────┐  ┌─────────────┐
                   │    │  HITL TRIAGE:          │  │  AI FIXES   │
                   │    │  1. AI Investigates    │  │  (no human) │
                   │    │  2. Provide Guidance   │  └─────────────┘
                   │    │  3. Skip + Continue    │
                   │    │  4. Abort              │
                   │    └────────────────────────┘
                   │                  │
                   │       ┌──────────┼──────────┐
                   │       ▼          ▼          ▼
                   │  ┌────────┐ ┌────────┐ ┌────────┐
                   │  │ Fix +  │ │ Skip + │ │ Abort  │
                   │  │ Retry  │ │Continue│ │        │
                   │  └───┬────┘ └───┬────┘ └────────┘
                   │      │          │
                   ▼      ▼          ▼
              ┌─────────────────────────────┐
              │  STATE SAVED / PROCEED      │
              │  (by operation)             │
              └─────────────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 5  │
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

*Next: Manual Construction Phase*

**NEW Workflow:** AI manually builds POMs, Tasks, Roles, and Tests using Edit/Write tools (NOT Tool 3-6).
Gates validate framework compliance. HITL triggers when AI gets blocked.

**OLD Workflow (ARCHIVED):** Step 6 - Generate POM (Tool 3) - See `_archived/autonomous_workflow_v1/`
