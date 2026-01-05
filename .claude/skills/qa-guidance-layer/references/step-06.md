<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Step 6: Tool 3 - Generate Page Object

**Purpose:** Generate Page Object Model (POM) code from discovered elements.

---

## A. Identity & Flow

| Field | Value |
|-------|-------|
| **Step** | 6 - Generate POM (Tool 3) |
| **Dependencies** | Step 5 complete (discovered_elements, page_name exist) |
| **Input** | `discovered_elements`, `page_name` from Step 5 |
| **Output** | `pom_code`, `pom_metadata` |

---

## B. Persona Map

| Persona | Actions |
|---------|---------|
| **User** | None (unless AI fails 3 times, then user decides resolution) |
| **AI** | Validates code completeness (DD-25), verifies no skeleton code, checks for state methods matching expected_states |
| **Tool** | `qg_page_object` validates input/output, `generate_page_object` generates POM code, operation saves state on SUCCESS |

---

## C. Skill Instruction

```
PRE-CHECK:
- Verify Step 5 complete (discovered_elements, page_name exist in state)
- READ expected_states from Step 3 (needed for state-check methods)

ACTION:
- CALL qg_page_object (PRE-VALIDATE)
- CALL generate_page_object (OPERATION)
- CALL qg_page_object (POST-VALIDATE)

VALIDATE (DD-25 - Skeleton Code Quality Gate):
- POST: Verify NO skeleton code indicators:
  - No empty sections with `pass`
  - No `# Add ... as needed` comments
  - All locators present as class constants
  - All atomic methods implemented (return self)
  - State-check methods for each expected_state

RETRY:
- If POST-VALIDATE fails (skeleton detected): AI completes the code (max 3 attempts)
- After 3 failures: STOP → REPORT → USER DECIDES
```

---

## D. Tools

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_page_object` |
| **Quality Gate** | `qg_page_object` |
| **Gate Mode** | PRE+POST (validates elements before, code quality after) |

---

## E. State Management

| Field | Value |
|-------|-------|
| **State Saved** | `pom_code`, `pom_metadata`, `generated_poms`, `poms_generated`, `total_poms`, `generation_complete` |
| **Who Saves** | Quality gate (`qg_page_object` POST) |
| **When Saved** | On POST-VALIDATE pass (for each page) |
| **State Schema** | See below |

**DEF-045: Dual Elements (NEW - Preferred):**

With two-pass discovery, POMs are generated using BOTH input and output elements:

```python
# From Step 5 state
step_5 = state_manager.get_step(5)
discovered_pages = step_5["discovered_pages"]

# Get BOTH element types for page
input_elements = discovered_pages["LoginPage"]["input_elements"]   # Forms, buttons
output_elements = discovered_pages["LoginPage"]["output_elements"] # Messages, confirmations

# Tool 3 call with dual elements
arguments = {
    "page_name": "LoginPage",
    "input_elements": input_elements,    # → Generate action methods
    "output_elements": output_elements,  # → Generate state methods
    "workflow": "auth",
    "expected_states": expected_states   # From Step 3
}
```

**Method Generation Logic:**
- **input_elements** → action methods (`enter_email`, `click_submit`)
- **output_elements + expected_states** → state-check methods (`is_logged_in`, `has_error_message`)

**Single-Page Workflow (Backward Compatible):**

```json
{
  "step": 6,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "pom_code": "class LoginPage:\n    EMAIL = (By.CSS_SELECTOR, '#email')\n    ...",
    "pom_metadata": {
      "class_name": "LoginPage",
      "file_path": "framework/pages/auth/login_page.py",
      "locators": ["EMAIL", "PASSWORD", "SUBMIT_BTN", "SUCCESS_MESSAGE"],
      "atomic_methods": ["enter_email", "enter_password", "click_submit"],
      "state_methods": ["is_logged_in", "is_error_displayed"]
    },
    "generated_poms": {"LoginPage": {"code": "...", "metadata": {...}}},
    "poms_generated": 1,
    "total_poms": 1,
    "generation_complete": true
  }
}
```

**Multi-Page Workflow (Task 8.5.9):**

```json
{
  "step": 6,
  "status": "complete",
  "timestamp": "ISO-8601",
  "data": {
    "pom_code": "class CheckoutPage:\n    ...",
    "pom_metadata": {"class_name": "CheckoutPage", ...},
    "generated_poms": {
      "LoginPage": {"code": "class LoginPage:\n    ...", "metadata": {...}},
      "InventoryPage": {"code": "class InventoryPage:\n    ...", "metadata": {...}},
      "CartPage": {"code": "class CartPage:\n    ...", "metadata": {...}},
      "CheckoutPage": {"code": "class CheckoutPage:\n    ...", "metadata": {...}}
    },
    "poms_generated": 4,
    "total_poms": 4,
    "generation_complete": true
  }
}
```

| Field | Purpose |
|-------|---------|
| `pom_code` | Last generated POM (backward compat) |
| `pom_metadata` | Last generated metadata (backward compat) |
| `generated_poms` | Per-page POM tracking (multi-page) |
| `poms_generated` | Progress counter |
| `total_poms` | Total from Step 5 `total_pages` |
| `generation_complete` | True when all POMs generated |

---

## F. Enforcement

| Field | Value |
|-------|-------|
| **Rules That Apply** | DD-09 (state methods from expected_states), DD-19 (tool import), DD-25 (skeleton code quality gate), DD-26 (data contracts) |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 7 until POM code complete (no skeleton)** |

**PRE-Validation Checks:**

| Check | Rule |
|-------|------|
| `discovered_elements` | Array present, at least 1 element |
| `page_name` | Valid PascalCase class name |
| `expected_states` | Present from Step 3 |

**POST-Validation Checks (DD-25):**

| Check | Rule |
|-------|------|
| Locators | All elements have class-level constant locators |
| Atomic methods | Each element has corresponding method (return self) |
| State methods | One method for each expected_state |
| No skeleton | No `pass`, no `# Add...`, no empty bodies |

---

## G. Error Handling

**Failure Behavior:**

| Failure Point | Behavior |
|---------------|----------|
| Missing elements | Go back to Step 5 |
| Skeleton code detected | AI completes the code (max 3) |
| Missing state methods | AI adds state methods for expected_states |
| After 3 total failures | STOP → REPORT → USER DECIDES |

**Known Defects:** Tools sometimes generate skeleton code with placeholders

**Error Message Template (Skeleton Detected):**

```
"Generated POM contains skeleton code. This violates DD-25.

Skeleton indicators found:
[list what was found - empty methods, pass statements, etc.]

Missing components:
[list what's missing - locators, methods, state checks]

I will complete the code before proceeding..."
```

**Error Message Template (After 3 Failures):**

```
"I've attempted 3 times and cannot generate complete POM code.

Last attempt result:
[show code and what's still missing]

How should we proceed?
1. Re-discover elements - Go back to Step 5
2. Manual POM - You provide the code
3. Abort workflow - Stop and log issue"
```

---

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 6: TOOL 3 - GENERATE POM                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
                         ┌────────────────────────┐
                         │  PRE-CHECK:            │
                         │  Step 5 complete?      │
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
              │  READ:              │     │  BLOCKED        │
              │  - discovered_elems │     │  Go to Step 5   │
              │  - page_name        │     └─────────────────┘
              │  - expected_states  │
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_page_object (PRE-VALIDATE)                                 │
│  - Validates inputs present                                                 │
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
              │  OPERATION:         │     │  Go to Step 5   │
              │  generate_page_     │     └─────────────────┘
              │  object             │
              └─────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_page_object (POST-VALIDATE)                                │
│  - DD-25: No skeleton code                                                  │
│  - All locators, methods, state-checks present                             │
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
              │  STATE SAVED        │  │  AI COMPLETES CODE  │
              │  (by operation)     │  │  (max 3 attempts)   │
              └─────────────────────┘  │                     │
                         │             │  After 3:           │
                         │             │  STOP → REPORT →    │
                         │             │  USER DECIDES       │
                         │             └─────────────────────┘
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 7  │
              └─────────────────────┘
```

---

## G.1 Multi-Page POM Generation Loop (Task 8.5.9)

**For multi-page workflows (DD-44), repeat Step 6 for each discovered page.**

### Flow Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    MULTI-PAGE POM GENERATION LOOP                            │
└─────────────────────────────────────────────────────────────────────────────┘

Step 5 State:
  discovered_pages = {
    "LoginPage": [...elements...],
    "InventoryPage": [...elements...],
    "CartPage": [...elements...],
    "CheckoutPage": [...elements...]
  }
  total_pages = 4

                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  FOR EACH page IN discovered_pages: │
                    └─────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
             ┌───────────┐    ┌───────────┐      ┌───────────┐
             │ LoginPage │    │ Inventory │ ...  │ Checkout  │
             └─────┬─────┘    │   Page    │      │   Page    │
                   │          └─────┬─────┘      └─────┬─────┘
                   │                │                  │
                   ▼                ▼                  ▼
             ┌──────────────────────────────────────────────┐
             │  PRE → GENERATE → POST (for each page)       │
             │  State tracks: poms_generated / total_poms   │
             │  POST returns: multi_page_progress           │
             └──────────────────────────────────────────────┘
                                      │
                                      ▼
                    ┌─────────────────────────────────────┐
                    │  generation_complete = True?         │
                    └─────────────────────────────────────┘
                                      │
                          ┌───────────┴───────────┐
                          ▼                       ▼
                    ┌──────────┐            ┌──────────┐
                    │  YES     │            │  NO      │
                    └────┬─────┘            └────┬─────┘
                         │                       │
                         ▼                       ▼
              ┌─────────────────────┐  ┌─────────────────────┐
              │  PROCEED TO STEP 7  │  │  Continue loop      │
              │  with ALL POMs      │  │  for remaining      │
              └─────────────────────┘  │  pages              │
                                       └─────────────────────┘
```

### AI Orchestration for Multi-Page

```python
# Get all discovered pages from Step 5 state
step_5_state = state_manager.get_step(5)
discovered_pages = step_5_state.get("discovered_pages", {})
total_pages = step_5_state.get("total_pages", 1)

# Loop: Generate POM for each page
for page_name, elements in discovered_pages.items():
    # PRE-VALIDATE
    pre_result = qg_page_object(mode="PRE", discovered_elements=elements, page_name=page_name)

    # OPERATION
    pom_result = generate_page_object(page_name=page_name, elements=elements, ...)

    # POST-VALIDATE (automatically tracks progress)
    post_result = qg_page_object(mode="POST", code=pom_result["code"], metadata=pom_result["metadata"], page_name=page_name)

    # Check progress
    progress = post_result.get("multi_page_progress", {})
    print(f"Generated {progress['poms_generated']}/{progress['total_poms']} POMs")

# Verify all POMs generated before Step 7
if not QGPageObject.is_generation_complete():
    # Handle incomplete generation
    pass
```

### Helper Methods

| Method | Purpose |
|--------|---------|
| `QGPageObject.is_generation_complete()` | Returns True when all POMs generated |
| `QGPageObject.get_generation_progress()` | Returns progress dict with generated_pages list |

---

## H. Tool Chain Data Contracts (DD-26)

**Input Contract (from Step 5):**

Tool 3 expects elements in Tool 2's output format:

```python
# CORRECT - Pass Tool 2 output directly:
elements = tool_2_result["elements"]

# Tool 3 call:
arguments = {
    "page_name": "LoginPage",
    "elements": elements,  # From Tool 2
    "workflow": "auth",
    "expected_states": [  # From Step 3
        {"name": "is_logged_in", "description": "user is logged in"}
    ]
}
```

**WRONG - Do NOT transform element keys:**
```python
# WRONG - invented format:
elements = [{"name": "X", "type": "Y", "locator": "Z"}]

# Tool 3 expects: suggested_name, element_type, locator_id/locator_css/locator_xpath
```

**Output Contract (Tool 3 provides for Step 7):**

```json
{
  "code": "class LoginPage:\n    EMAIL = (By.CSS_SELECTOR, '#email')...",
  "metadata": {
    "class_name": "LoginPage",
    "import_path": "pages.auth.login_page",
    "action_methods": [
      {"name": "enter_email", "params": ["text: str"]},
      {"name": "click_submit", "params": []}
    ],
    "state_methods": [
      {"name": "is_logged_in", "params": []}
    ]
  }
}
```

**CRITICAL:** Pass `metadata` object to Tool 4 as `pom_metadata`.

---

## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-06-01 | `state_methods` must match `expected_states` from Step 3 input | DD-09 enforcement - if expected_states was provided in PRE, POST must verify each expected_state has a corresponding state_method in metadata. Strict match, not just presence. | `validate_post()` |
| IC-06-02 | `NotImplementedError` in code is skeleton code (DD-25 violation) | Generator produces `raise NotImplementedError` for expected_states methods. This is a placeholder that AI must complete. Empty method bodies are not acceptable. | `validate_post()` |
| IC-06-03 | `action_methods` empty when `locators` exist is a FAIL | If locators were generated (elements had name + locator), but no action_methods exist, the element_type data from Tool 2 is missing/invalid. This is a data quality issue in the Tool 2 → Tool 3 handoff. | `validate_post()` |

**Date Added:** 2025-12-21
**Task Reference:** Task 9.0 (qg_page_object)

---

## J. Self-Heal Pattern Template

**When AI must complete/fix POM code, use this pattern:**

```python
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class ExamplePage:
    """Page Object for [page description]."""

    # ═══════════════════════════════════════════════════════════════════════════
    # LOCATORS - Class-level constants, UPPER_SNAKE_CASE
    # ═══════════════════════════════════════════════════════════════════════════
    EMAIL_INPUT = (By.CSS_SELECTOR, "#email")
    PASSWORD_INPUT = (By.CSS_SELECTOR, "#passwd")
    SUBMIT_BTN = (By.CSS_SELECTOR, "#SubmitLogin")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".alert-danger")
    LOGOUT_LINK = (By.CSS_SELECTOR, "a.logout")

    # ═══════════════════════════════════════════════════════════════════════════
    # CONSTRUCTOR - Compose WebInterface, NO inheritance
    # ═══════════════════════════════════════════════════════════════════════════
    def __init__(self, web: WebInterface):
        self.web = web

    # ═══════════════════════════════════════════════════════════════════════════
    # NAVIGATION - POM owns navigation, gets URL from WebInterface.config
    # ═══════════════════════════════════════════════════════════════════════════
    def navigate(self) -> "ExamplePage":
        """Navigate to this page. Gets URL from WebInterface config."""
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/index.php?controller=authentication")
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # ATOMIC METHODS - One action per method, return self for chaining
    # ═══════════════════════════════════════════════════════════════════════════
    def enter_email(self, text: str) -> "ExamplePage":
        """Enter text into email field."""
        self.web.type_text(*self.EMAIL_INPUT, text)
        return self

    def enter_password(self, text: str) -> "ExamplePage":
        """Enter text into password field."""
        self.web.type_text(*self.PASSWORD_INPUT, text)
        return self

    def click_submit(self) -> "ExamplePage":
        """Click the submit button."""
        self.web.click(*self.SUBMIT_BTN)
        return self

    # ═══════════════════════════════════════════════════════════════════════════
    # STATE-CHECK METHODS - For test assertions, return bool
    # ═══════════════════════════════════════════════════════════════════════════
    def is_page_loaded(self) -> bool:
        """Check if page is fully loaded."""
        return self.web.is_element_displayed(*self.EMAIL_INPUT, timeout=5)

    def is_logged_in(self) -> bool:
        """Check if user is logged in (logout link visible)."""
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    def is_error_displayed(self) -> bool:
        """Check if error message is visible."""
        return self.web.is_element_displayed(*self.ERROR_MESSAGE, timeout=3)

    def get_error_message(self) -> str:
        """Get the error message text."""
        return self.web.get_text(*self.ERROR_MESSAGE)
```

**POM Pattern Rules (Checklist):**

| ✓ | Rule |
|---|------|
| ☐ | Locators as class-level constants (UPPER_SNAKE_CASE) |
| ☐ | Compose `WebInterface` in `__init__`, NO inheritance |
| ☐ | `navigate()` method gets URL from `self.web.config["url"]` |
| ☐ | Atomic methods: one UI action per method |
| ☐ | Atomic methods return `self` for fluent chaining |
| ☐ | State-check methods return `bool` |
| ☐ | NO `@autologger` decorator (logging at Task/Role level) |
| ☐ | NO Task/Role imports |
| ☐ | NO workflow logic (just UI interactions) |

**Anti-Patterns to Avoid:**

```python
# ❌ WRONG: Composite method (belongs in Task)
def login(self, email, password):
    self.enter_email(email)
    self.enter_password(password)
    self.click_submit()

# ❌ WRONG: Returning None instead of self
def enter_email(self, text: str) -> None:
    self.web.type_text(*self.EMAIL_INPUT, text)
    # Missing return self

# ❌ WRONG: Inheritance
class LoginPage(BasePage):  # NO - use composition
    pass

# ❌ WRONG: Skeleton state method
def is_page_loaded(self) -> bool:
    return True  # Must check actual element
```

---

*Next: Step 7 - Generate Task (Tool 4)*
