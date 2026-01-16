# CLAUDE.md

**Version:** v2.0.0 | **Status:** Production Development
**Company:** Isagawa Corp
**Product:** QA Management Engine (AI Management Layer - First Vertical)

---

# DIALOGUE PROTOCOL (Always Apply)

## After Every User Message
1. **STOP** - Do not respond immediately
2. **CHECK** - Does this fit existing patterns? If not, propose new reference with rationale
3. **RESPOND** - Following rules below

## Quick Rules
- **One topic at a time** - Queue multiple topics, present sequentially
- **Number all options** - User responds with just a number (1, 2, 3...)
- **Stop after each task** - When executing multiple tasks, stop after first, await confirmation
- **Never create new categories without approval** - Propose with rationale, wait for user

## Full Details
See `.claude/skills/dialogue-engine/` for complete protocol and references.

---

# PROJECT-SPECIFIC INFORMATION

## Project Overview

**Project:** py_sel_framework_mcp - QA Management Engine (Isagawa Corp)

**Company:** Isagawa Corp - The AI Management Layer for Complex Domains

**Purpose:** First implementation of Isagawa's AI Management Layer - a production system that enforces how AI executes QA test automation workflows through domain-specific rules, quality gates, and validation checkpoints.

**Platform Definition:** The Isagawa Platform is an AI Management Layer built on two primitives:
- **Protocols** (Skills) define the correct way AI must perform work
- **Smart Gates** enforce those protocols at every step

**Product Category:** AI Management Layer implemented as domain-specific Execution Engine

**Key Features:**
- Production-grade 4-layer architecture (Role → Task → Page → WebInterface)
- 11-step workflow with mandatory quality gates (v2.0)
- 28 Design Decisions enforced via MCP validation tools
- Hybrid architecture: Protocols (Skills for guidance) + Smart Gates (MCP Tools for enforcement)
- Progressive audit trail and state management
- Real-world test generation against live applications

**Target Application:** http://www.automationpractice.pl/index.php (demo), expandable to any web application

**Company Thesis:** See `.business/strategy/isagawa_corp_thesis_v3.1.md` for complete AI Management Layer vision

## Technology Stack

**Core Framework:**
- Python 3.x
- Selenium WebDriver
- Pytest (test runner)
- pytest-html (HTML reporting)

**AI Integration:**
- Model Context Protocol (MCP) server
- Python-based MCP implementation

**Supporting Tools:**
- WebDriver Manager (driver management)
- Faker (test data generation)
- JSON (configuration and test data)

## Development Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r mcp_server/requirements.txt
```

### Testing
```bash
# MCP Server development tests (code generation, tool chain)
cd mcp_server/_dev_tests
python test_complete_code_generation.py

# Framework tests (pytest)
cd tests
pytest -v --html=_reports/report.html --self-contained-html
```

### MCP Development Tests Location
**All MCP server development tests go in:** `mcp_server/_dev_tests/`
- Test tool chain (Tool 1-6)
- Code generation validation
- End-to-end workflow tests
- DO NOT create test scripts elsewhere - use this directory

## MCP Tool Usage (MANDATORY - NO EXCEPTIONS)

**CRITICAL: Before calling ANY MCP tool (Tools 1-6), you MUST read and follow FRAMEWORK.md Section 9.**

### 10-Step Workflow (v2) - Quick Reference

```
Step 1:  Pre-flight Configuration  → credential_strategy, test_data_location
Step 2:  User Input                → persona, URL
Step 3:  AI Processing             → metadata_context
Step 4:  Tool 1                    → test_scenarios
Step 5:  Tool 2                    → discovered_elements
Step 6:  Tool 3                    → pom_metadata
Step 7:  Tool 4                    → task_metadata
Step 8:  Tool 5                    → role_metadata
Step 9:  Tool 6                    → test_code
Step 10: Save & Run                → files saved, test executed
```

**Gate Enforcement:** Cannot proceed to Step N+1 until Step N quality gate passes.

**Full Details:** FRAMEWORK.md Section 9

### QA Guidance Layer (Protocol)

For guided 11-step workflow with quality gates:
```
.claude/skills/qa-management-layer/
├── SKILL.md              ← Overview and rules
└── references/
    ├── step-01.md        ← Per-step guidance
    ├── step-02.md
    └── ...
```

**Usage:** Read relevant step reference before executing each step.

**Meta Protocol:** See `design-execution-engine/` for patterns applicable to any vertical.

### Legacy Protocol (Deprecated - Use Section 9 Instead)

For old 9-step workflow:
```
/skill execute-from-step1
```

The protocol provides:
- Complete 9-step workflow guide
- Autonomous troubleshooting (iframe detection, shadow DOM, JS fallbacks)
- Step-by-step DevTools guidance when AI needs help
- Defect handling with mandatory restart-from-step-1

### 9-Step Flow Summary

```
Step 1: User Input (persona + URL)
Step 2: AI Processing (extract role, domain, BDD, expected_states)
Step 3: Tool 1 - generate_tests_from_user_story
Step 4: Tool 2 - discover_page_elements (static or dynamic DD-20)
Step 5: Tool 3 - generate_page_object
Step 6: Tool 4 - generate_task (check-existing DD-12)
Step 7: Tool 5 - generate_role (check-existing DD-12)
Step 8: Tool 6 - generate_test_runner
Step 9: Save files & run test
```

**Detailed rules:** FRAMEWORK.md Section 8

### Key Design Decisions (Quick Reference)

**Full details in FRAMEWORK.md Section 8.11-8.14**

| ID | Rule |
|----|------|
| DD-01 | User MUST specify persona ("As a...") - ASK if missing |
| DD-02 | URL required upfront - ASK if missing |
| DD-03 | Metadata context accumulated through tool chain |
| DD-04 | Single documentation source (FRAMEWORK.md) |
| DD-05 | Exact method names emerge from tool chain, not upfront |
| DD-06 | AI extracts intent, not exact method names |
| DD-07 | Domain determined by AI in Step 2, passed through metadata |
| DD-08 | AI orchestrates tool chain, tools don't call other tools |
| DD-09 | Extract expected_states from BDD "Then" clause for POM state methods |
| DD-10 | Action methods derived from element types (input→enter, button→click) |
| DD-11 | State method naming: is_*/has_* for bool, get_* for values |
| DD-12 | Check existing classes/methods BEFORE generating new |
| DD-13 | Each tool has specific AI prompting rules |
| DD-14 | One test file per scenario, grouped by domain folder |
| DD-15 | Test assertions MUST use POM state methods from metadata |
| DD-16 | AI overrides Tool 6 file paths to `tests/test1/`, `tests/test2/` |
| DD-17 | AI injects actual parameter values from requirement |
| DD-18 | AI validates import paths before saving |
| DD-19 | Tool invocation: import from `tools/`, never `utils/` |
| DD-20 | Dynamic elements: AI prepares page state before Tool 2 |
| DD-21 | AI-SDET collaboration for dynamic discovery |
| DD-22 | On ANY blocker: STOP → REPORT → DISCUSS with user → then proceed |
| DD-23 | BDD format required for Tool 1 (explicit Given/When/Then) |
| DD-24 | Test credentials: ASK user which strategy (static/dynamic/self-contained) |
| DD-25 | Skeleton code quality gate: STOP if any tool generates incomplete code |
| DD-26 | Tool chain data contracts: pass metadata directly between tools |
| DD-27 | Task code quality gate: NO locators in Tasks (CRITICAL) |
| DD-28 | Test data organization: ASK user shared vs workflow-specific data location |
| DD-29 | Slash command entry: `/qa-workflow` (prod) or `/qa-workflow-dev` (dev) |
| DD-30 | Progressive audit trail: PostToolUse hook writes to `tests/_audit/` after each gate |
| DD-33 | Dynamic element discovery: AI uses Playwright snapshot → extracts → builds |
| DD-44 | Multi-page scope discovery: AI MUST call scope_discovery before Step 5 |
| DD-46 | Visual feedback enforcement: AI MUST call RuntimeValidator for each element |
| DD-49 | Navigation responsibility: Only POMs navigate(); Tasks call pom.navigate() |
| DD-50 | Smart gate pattern: Gates provide fix data, not just block |

### DD-22: Stop-and-Discuss Protocol (CRITICAL)

**When ANY issue blocks progress:**
1. **STOP** - Do not attempt fixes autonomously
2. **REPORT** - Explain: what failed, what you observed, potential causes
3. **DISCUSS** - Wait for user input before proceeding
4. **PROCEED** - Only after user direction

**This applies to:**
- Test failures
- Element not found errors
- Unexpected behavior
- Any deviation from expected outcome
- Build/import errors

**NEVER loop through multiple fix attempts without user consultation.**

### DD-24: Test Credential Strategy

**When test requires user credentials, AI MUST ask which strategy:**

```
"Test requires credentials. Which approach?
1. Static - Use pre-existing account from test_users.json
2. Dynamic - Register fresh user, save to config for later tests
3. Self-contained - Test registers and uses within same test"
```

| Strategy | Description | Use When |
|----------|-------------|----------|
| **Static** | Pre-existing account in `tests/data/test_users.json`. Tests READ via conftest `test_users` fixture. | Login-only tests, known account needed |
| **Dynamic** | Test registers fresh user, saves to config via utility function (NOT conftest modification). | Registration → subsequent action flow |
| **Self-contained** | Test registers and uses credentials within same test run. | Independent tests, no cross-test dependency |

**Rules:**
- ASK at Step 1 (User Input) when credentials are involved
- NEVER modify conftest.py for credential saving
- Static credentials use existing `test_users` fixture
- Dynamic credentials use utility function to write to `test_users.json`

### DD-25: Skeleton Code Quality Gate (CRITICAL)

**After ANY MCP tool generates code (Tools 3-6), AI MUST verify completeness.**

**Skeleton code indicators (ANY of these = FAIL):**
- Empty sections with `pass` or `# Add ... as needed`
- Missing locators in POMs
- Missing atomic methods in POMs
- Missing workflow methods in Tasks/Roles
- Placeholder comments instead of actual code
- Empty method bodies

**Quality gate checklist:**

| Module | Required Components |
|--------|---------------------|
| **POM (Tool 3)** | Locators as class constants, atomic methods (return self), state-check methods |
| **Task (Tool 4)** | Constructor with POM composition, @autologger decorated methods, NO return values |
| **Role (Tool 5)** | Constructor with Task composition, @autologger decorated workflow methods, NO return values |
| **Test (Tool 6)** | Fixtures, AAA pattern, POM state assertions, proper imports |

**When skeleton code detected:**
1. **STOP** - Do not proceed to next step
2. **REPORT** - Identify which tool generated skeleton code
3. **FIX** - Either fix the tool OR AI manually completes the code
4. **VERIFY** - Confirm code is complete before proceeding
5. **RESTART** - After fix, restart from Step 1

**This is a hard quality gate. Incomplete code MUST NOT propagate through the tool chain.**

### DD-28: Test Data Organization Strategy

**When test requires test data, AI MUST ask which location strategy:**

```
"Test requires test data. Where should it live?
1. Shared - tests/data/ (credentials, cross-workflow data)
2. Workflow-specific - tests/{workflow}/data/ (isolated test data)
3. Both - shared credentials + workflow-specific test cases"
```

**Hybrid Data Model:**

```
tests/
├── data/                      ← SHARED (cross-workflow)
│   └── test_users.json        ← Credentials used by auth, cart, checkout
├── auth/
│   ├── data/                  ← WORKFLOW-SPECIFIC
│   │   └── invalid_logins.json
│   └── test_registration.py
├── catalog/
│   ├── data/
│   │   └── products.json      ← Catalog-specific test data
│   └── test_browse.py
└── conftest.py                ← Smart data loader (workflow-first, shared fallback)
```

| Data Type | Location | Example |
|-----------|----------|---------|
| **Credentials** | `tests/data/` | User accounts used across workflows |
| **Workflow-specific** | `tests/{workflow}/data/` | Invalid login combos, product lists |
| **Documents/files** | `tests/{workflow}/data/input/` | Upload test files |

**Rules:**
- ASK at Step 1 (User Input) when test data is involved
- Shared credentials → `tests/data/test_users.json`
- Workflow-isolated data → `tests/{workflow}/data/`
- conftest.py provides smart loader with fallback logic

**Implementation Note:**
Per-step protocols are being created to enforce tool chain contracts. DD-28 implementation
will be integrated into the appropriate step protocol (likely Step 1 or Step 9) once
DDs are ported to dedicated protocols. See DEF-B08/DEF-B09 for protocol architecture plan.

### NO HALLUCINATIONS Policy
- NEVER guess method names - use metadata from previous tool
- NEVER assume a class exists - scan framework/ first
- NEVER hardcode method calls - derive from POM/Task/Role metadata
- If unsure, ASK the user for clarification

### AI Orchestration Rules (Post-Tool Processing)
Tools generate code, but AI must post-process before saving. See DD-16, DD-17, DD-18.

**Example DD-17 (Parameter Value Injection):**
```python
# Tool 6 generates:
user.browse_category("category_name_value")

# AI must replace with actual value from requirement:
user.browse_category("Women")  # From "browse products in Women category"
```

### E2E Testing & Defect Handling

**Use the protocol for detailed workflow:**
```
/skill execute-from-step1
```

**Key Rules (always apply):**
- On ANY error: STOP → LOG → FIX → RESTART FROM STEP 1
- NEVER mark defect RESOLVED without clean E2E rerun from Step 1
- Agentic defects require new Design Decision (DD-XX) to prevent recurrence
- See `docs/DEFECT_LOG.md` for defect tracking format

## Project Structure

**Architecture:** 4-Layer Test Automation Framework

```
Tests (Business scenarios)
  ↓
Roles (User personas with credentials)
  ↓
Tasks (Business workflows)
  ↓
Pages (UI interactions)
  ↓
WebInterface (Selenium wrapper)
```

**Directory Layout:**
```
/framework            # Framework code (reusable)
  /interfaces         # WebInterface, FileInterface
  /pages             # Page objects
  /tasks             # Business workflows
  /roles             # User personas
  /resources         # Config, utilities

/tests               # Test scenarios
  main.py            # Pytest launcher
  conftest.py        # Pytest fixtures

/mcp_server          # MCP integration
  /tools             # MCP tool implementations
  /utils             # Utilities
  server.py          # MCP server

/docs                # Process documentation (gitignored for IP protection)
```

## 4-Layer Framework Architecture

**CRITICAL: Follow these patterns exactly. Generated code MUST match production code.**

**Authoritative Reference:** See `FRAMEWORK.md` for complete architecture documentation with code samples.

### Layer Overview
```
Test        → Calls ONE role workflow method, asserts via POM state-check methods
Role        → ORCHESTRATES multiple tasks into complete business workflow (NO return)
Task        → Orchestrates page object methods for a single domain operation (NO return)
Page        → Atomic UI interactions using WebInterface (returns self)
WebInterface → Selenium wrapper
```

### Layer 1: Page Objects (Atomic UI Interactions)

**Purpose:** Single page representation with atomic element interactions.

**Pattern:**
```python
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface

class LoginPage:
    # LOCATORS - Class-level constants
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWORD = (By.CSS_SELECTOR, "#passwd")
    SUBMIT_BTN = (By.CSS_SELECTOR, "#SubmitLogin")

    def __init__(self, web: WebInterface):
        self.web = web  # Compose WebInterface, NO inheritance

    # ATOMIC METHODS - One action per method, return self for chaining
    def enter_email(self, text: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text)
        return self

    def enter_password(self, text: str) -> "LoginPage":
        self.web.type_text(*self.PASSWORD, text)
        return self

    def click_submit(self) -> "LoginPage":
        self.web.click(*self.SUBMIT_BTN)
        return self

    # STATE-CHECK METHODS - For test assertions
    def is_logged_in(self) -> bool:
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)
```

**Rules:**
- Locators ONLY in Page Objects (never in Tasks or Roles)
- One action per method
- Return `self` for fluent chaining
- NO decorators on Page Objects (logging happens at Task/Role level)
- NO inheritance - compose WebInterface directly
- Include state-check methods for test assertions

### Layer 2: Tasks (Domain Operations)

**Purpose:** Orchestrate page object methods for single domain operations.

**Pattern:**
```python
from interfaces.web_interface import WebInterface
from pages.auth.login_page import LoginPage
from resources.utilities import autologger

class AuthTasks:
    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.base_url = base_url
        # Compose page objects
        self.login_page = LoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str):
        """Single domain operation: authenticate user. NO return value."""
        self.web.navigate_to(f"{self.base_url}/login")

        # Use page object methods (fluent chain)
        (self.login_page
            .enter_email(email)
            .enter_password(password)
            .click_submit())

        # NO return - test asserts via login_page.is_logged_in()

    @autologger.automation_logger("Task")
    def log_out(self):
        """Single domain operation: end session. NO return value."""
        self.login_page.click_logout()
        # NO return - test asserts via login_page.is_logged_out()
```

**Rules:**
- NO locators in Tasks (delegate to page objects)
- Each task method = one domain operation
- Use `@autologger.automation_logger("Task")` decorator
- **NO return values** - tests assert via POM state-check methods

### Layer 3: Roles (Workflow Orchestration)

**Purpose:** ORCHESTRATE multiple tasks into complete business workflows.

**Pattern:**
```python
from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.auth_tasks import AuthTasks
from tasks.catalog_tasks import CatalogTasks
from tasks.checkout_tasks import CheckoutTasks
from resources.utilities import autologger

class AuthenticatedUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        self.web = web_interface
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')

        # Compose ALL task modules needed - NO inheritance
        self.auth_tasks = AuthTasks(web_interface, base_url)
        self.catalog_tasks = CatalogTasks(web_interface, base_url)
        self.checkout_tasks = CheckoutTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def purchase_product(self, product_data: dict):
        """
        COMPLETE WORKFLOW: Login -> Browse -> Add to Cart -> Checkout

        This is what makes Role different from Task:
        - Role orchestrates MULTIPLE tasks
        - Role represents a complete user journey/story
        - NO return value - test asserts via POM
        """
        self.auth_tasks.log_in(self.email, self.password)
        self.catalog_tasks.browse_category(product_data["category"])
        self.catalog_tasks.add_to_cart(product_data["name"])
        self.checkout_tasks.complete_purchase()
        # NO return - test asserts via POM state-check methods
```

**Rules:**
- Role methods = COMPLETE business workflows (not single operations)
- Orchestrate MULTIPLE task methods in sequence
- Use `@autologger.automation_logger("Role")` decorator
- **NO return values** - tests assert via POM state-check methods
- NO inheritance - compose Tasks directly

### Layer 4: Tests (Assertions Only)

**Purpose:** Call ONE role workflow method, assert via POM state-check methods.

**Pattern:**
```python
import pytest
from roles.authenticated_user import AuthenticatedUser
from pages.checkout.order_confirmation_page import OrderConfirmationPage
from resources.utilities import autologger

@pytest.mark.purchase
@autologger.automation_logger("Test")
def test_user_can_purchase_product(web_interface, config, test_data):
    """
    Test that a registered user can complete a purchase.

    NOTE: Test does NOT orchestrate - it calls ONE role method.
    Assert via POM state-check methods, NOT return values.
    """
    # Arrange
    user = AuthenticatedUser(web_interface, test_data["user"], config["url"])
    product = test_data["product"]
    confirmation_page = OrderConfirmationPage(web_interface)

    # Act - ONE call to workflow method (no return value)
    user.purchase_product(product)

    # Assert - Via POM state-check methods
    assert confirmation_page.is_order_confirmed(), "Order should be confirmed"
    assert confirmation_page.get_order_total() > 0, "Order total should be positive"
```

**Rules:**
- Test calls ONE role workflow method
- Test does NOT orchestrate multiple role/task calls
- Test only does: Arrange, Act (one call), Assert
- **Assert via POM state-check methods** - NOT return values
- Use `@autologger.automation_logger("Test")` decorator

### Anti-Patterns to AVOID

**WRONG - Tasks/Roles returning values:**
```python
# BAD: Tasks should NOT return values
class AuthTasks:
    def log_in(self, email, password) -> bool:  # NO!
        ...
        return self.login_page.is_logged_in()  # NO!

# BAD: Roles should NOT return values
class AuthenticatedUser:
    def login(self) -> bool:  # NO!
        return self.auth_tasks.log_in(...)  # NO!
```

**WRONG - Test asserts on return value:**
```python
# BAD: Test should assert via POM, not return values
def test_login():
    result = user.login()  # NO! Role returns nothing
    assert result is True  # NO! Assert via POM instead
```

**WRONG - Test orchestrates workflow:**
```python
# BAD: Test is doing Role's job
def test_purchase():
    user.login()           # Multiple calls
    user.browse("Women")   # Test is orchestrating
    user.add_to_cart()     # This belongs in Role
    user.checkout()
```

**WRONG - Task has locators:**
```python
# BAD: Locators belong in Page Objects only
class CatalogTasks:
    def browse_category(self, name):
        from selenium.webdriver.common.by import By
        self.web.click(By.XPATH, f"//a[text()='{name}']")  # NO!
```

**WRONG - Using inheritance:**
```python
# BAD: Use composition, not inheritance
class LoginPage(BasePage):  # NO!
    pass

class RegisteredUser(Role):  # NO!
    pass
```

### Summary: Who Does What

| Layer | Responsibility | Returns | Calls |
|-------|---------------|---------|-------|
| Test | Assert via POM | N/A | ONE Role method + POM state-checks |
| Role | Orchestrate workflow | None | MULTIPLE Task methods |
| Task | Single operation | None | Page Object methods |
| Page | Atomic UI action | self | WebInterface methods |

### Quick Reference

```
GOLDEN RULES:
1. Locators ONLY in Page Objects
2. Tasks/Roles return NOTHING (None)
3. Tests assert via POM state-check methods
4. No inheritance - composition only
5. One responsibility per layer
```

## Intellectual Property Protection

**What's Protected:**
- `.business/` folder - Company strategy, thesis, business model, domain expansion plans
- `docs/` folder (gitignored) - Product design, PRDs, task lists, internal architecture decisions
- Reason: AI Management Layer implementation, execution engine architecture, and domain expertise encoding are proprietary competitive advantages for Isagawa Corp

**Backup Strategy:**
- Cloud backup via OneDrive/Google Drive/Dropbox
- Manual sync to cloud storage for disaster recovery

**What's Public (for distribution):**
- Framework code (`framework/`, `tests/`, `mcp_server/`) - distributed via `pip install isagawa-qa`
- Protocols (Skills as .md files) - distributed via Claude plugins
- README.md (product documentation)

## Git Workflow

### Branch Naming
- `feature/<task-id>-short-description` - New features
- `bugfix/<issue-id>-short-description` - Bug fixes

### Commit Message Format
```
feat: Add new feature
fix: Fix bug
refactor: Restructure code
test: Add tests
docs: Update docs
chore: Update dependencies
```

For parent task commits:
```
feat: Implement feature name (Task X.0)

Completed Subtasks:
- X.1: Description
- X.2: Description

Relevant Files:
- path/to/file.ext
```

---

# UNIVERSAL PROCESSES

## Communication Filters

### "Truth and No BS" Filter

**Role:** Direct, unfiltered analytical system. Pure logic and first principles thinking. No sugarcoating, hedging, or softening. Value comes from honest assessment and clear solutions.

**Operating Principles:**
- Default to brutal honesty over comfort
- Identify real problem, not symptoms
- Think from first principles
- Provide definitive answers, not suggestions
- Call out flawed reasoning immediately
- Focus on what works, not what sounds good

**Response Framework:**
State core truth in one direct sentence. Break down why current approach fails using first principles. Provide exact steps to solve actual problem.

Never use "you might consider" or "perhaps try." Use "you need to" and "the solution is."

No emojis. No em dashes. Pure signal, zero noise.

### "REALITY FILTER"

- Never present generated, inferred, speculated content as fact
- If cannot verify, say: "I cannot verify this."
- Label unverified content: [Inference] [Speculation] [Unverified]
- Ask for clarification if information missing

## The 4D Framework

**Design → Define → Divide → Deliver**

Structured 4-phase process. Each phase has process doc in `docs/`:

- **Phase 1 (Design):** `docs/1-design-discussion-v2.md` - Conversational design discussion
- **Phase 2 (Define):** `docs/2-define-create-prd-v2.md` - Create PRD
- **Phase 3 (Divide):** `docs/3-divide-generate-tasks-v2.md` - Break down into tasks
- **Phase 4 (Deliver):** `docs/4-deliver-execute-tasks-v2.md` - Execute and ship

## Task Generation Rules

### Per-Capability Parent Task Pattern:

1. **Impact Assessment** (MANDATORY for refactors/changes):
   - Who calls this code? (find all usage)
   - What depends on current behavior? (existing tests, other components)
   - What will break? (tests, integrations, assumptions)
   - Migration path? (old data, backward compatibility)

2. **Mark Core vs Glue**:
   - **Core** (logic/contracts) → TDD: write failing tests → implement → refactor
   - **Glue** (wiring/UX) → Ensure acceptance/integration coverage exists

3. **Run & Record Checks** before marking parent complete:
   - Formatter, linter, type checker (if applicable)
   - Unit/integration tests
   - Coverage ≥ target (e.g., 80%)
   - Record exact commands and results in task list

3. **"Done When" Criteria**:
   - Acceptance criteria met
   - All checks pass
   - Commands + results documented

4. **Feature Branch Naming**: `feature/<task-id>-short-name`

5. **Relevant Files Section**: List source + test files with descriptions

### Task List Template:

```markdown
## Relevant Files
- `path/to/file.ext` - Description
- `path/to/test.ext` - Tests for file.ext

## Tasks
- [ ] X.0 Parent Task [CORE/GLUE]
  - [ ] X.1 Implementation subtask
  - [ ] X.N Run checks
  - [ ] X.N+1 Record results

**Done When:**
- Acceptance criteria met
- All checks pass
- Commands + results documented

**Commands Run:**
```bash
# Commands pasted after execution
```

**Results:**
- One-line summary per command
```

## Task Execution Rules

1. **One subtask at a time**: Complete → mark `[x]` → wait for "yes"
2. **Parent task commits**: Commit ONLY after ALL subtasks complete
3. **Dual task tracking**:
   - Update TodoWrite tool (UI progress)
   - Update `docs/projects/.../2-tasks.md` (mark `[x]`)
4. **Commit format**: Conventional commits with detailed body for parent tasks
5. **Feature branches**: `feature/<task-id>-short-name`

## Development Philosophy

- Start simple, build modularly
- Walking skeleton approach
- Testing from day one
- Modular architecture
- Progressive feature unlocking

## Testing Strategy

### General Principles
- Write tests alongside code
- Test behavior, not implementation
- TDD for core logic
- Integration/acceptance coverage for glue
- Meaningful coverage, not just high percentages

### Coverage Targets
- Critical paths: 100%
- Core logic: 90%+
- Integration/glue: 80%+
- Utilities: 85%+

### TDD Workflow (Core Logic)
```
1. Write failing test (Red)
2. Implement minimal code (Green)
3. Refactor (Refactor)
4. Repeat
```

## Error & Issue Log

### Format:

```markdown
### [ERROR-XXX] Brief Description
**Date:** YYYY-MM-DD
**Task:** Task X.X
**Error:** Full error message
**Context:** What was being attempted
**Attempted Fixes:**
1. First thing tried - Result
**Solution:** How resolved
**Status:** OPEN | RESOLVED | BLOCKED
**Prevention:** How to avoid
```

### Active Issues:
(See `docs/DEFECT_LOG.md` for full defect tracking - DEF-019 and DEF-020 are open)

### Resolved Issues:
(See `docs/DEFECT_LOG.md`)

## Session Close Protocol

**MANDATORY: Before ending session, MUST create/update `SESSION.md`**

### Exit Protocol:
1. Create/Update `SESSION.md` with complete session state
2. Update Error & Issue Log if errors occurred
3. Confirm session state saved

### SESSION.md Minimal Format:

```markdown
# Session State - [DATE] [TIME]

## Current Phase
**Phase:** Phase X
**Status:** On Track | Blocked | Waiting

## What We're Working On
**Active Task:** X.X - [Task name]
**Task Status:** In Progress (XX%)

## Progress This Session
### Completed
- [x] Item 1

### In Progress
- [ ] Item 2 (next step: [what to do])

## Files Changed
- `path/to/file.ext` - [What changed]

## Test Status
- Unit tests: PASSING | FAILING
- Coverage: XX%

## Active Blockers/Issues
[ERROR-XXX] Brief description (if any)

## Context for Next Session
**Resume Point:** Continue with task X.X - [specific action]

**Important Context:**
- [Critical info next session needs]

## Token Usage
- This session: XX% used
```

### CRITICAL RULES:
1. ALWAYS create/update SESSION.md before ending
2. If blocked, document EXACTLY what was tried
3. Include enough detail to resume WITHOUT asking user

---

## Key Reminders

- Don't batch task completions - mark `[x]` immediately
- Don't skip session closeout - update SESSION.md
- Focus on shipping, not perfect process
- Tests are mandatory, not optional

---

**Last Updated:** [To be filled during first session]
