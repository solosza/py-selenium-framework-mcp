# CLAUDE.md

**Version:** v1.7.0 | **Status:** Active Development

---

# PROJECT-SPECIFIC INFORMATION

## Project Overview

**Project:** py_sel_framework_mcp - Python Selenium Test Automation Framework with MCP Integration

**Purpose:** Portfolio showcase demonstrating QA Lead-level test automation architecture with AI integration (MCP server) for job interviews.

**Key Features:**
- Production-grade 4-layer architecture (Role → Task → Page → WebInterface)
- Tests full e-commerce application (Automation Practice)
- 15-20 test scenarios covering core workflows
- MCP server for AI-assisted testing workflows
- HTML reporting, logging, screenshot capture
- Pytest-based test execution

**Target Application:** http://www.automationpractice.pl/index.php

**Timeline:** 2 weeks (Week 1: Framework, Week 2: MCP + Polish)

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

**CRITICAL: Before calling ANY MCP tool (Tools 1-6), you MUST read and follow FRAMEWORK.md Section 8.**

### Quick Start: Use the Skill

For full 9-step workflow with autonomous troubleshooting:
```
/skill execute-from-step1
```

The skill provides:
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
| DD-08 | AI orchestrates tool chain, tools don't call other tools |
| DD-09 | Extract expected_states from BDD "Then" clause for POM state methods |
| DD-12 | Check existing classes/methods BEFORE generating new |
| DD-15 | Test assertions MUST use POM state methods from metadata |
| DD-16 | AI overrides Tool 6 file paths to `tests/test1/`, `tests/test2/` |
| DD-17 | AI injects actual parameter values from requirement |
| DD-18 | AI validates import paths before saving |
| DD-19 | Tool invocation: import from `tools/`, never `utils/` |
| DD-20 | Dynamic elements: AI prepares page state before Tool 2 |
| DD-21 | AI-SDET collaboration for dynamic discovery |
| DD-22 | On ANY blocker: STOP → REPORT → DISCUSS with user → then proceed |

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

**Use the skill for detailed workflow:**
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
- `docs/` folder (gitignored) - Strategic planning, PRDs, task lists, MCP design
- Reason: Portfolio strategy, process framework, MCP architecture are competitive advantages

**Backup Strategy:**
- Cloud backup via OneDrive/Google Drive/Dropbox
- Manual sync to cloud storage for disaster recovery

**What's Public:**
- Framework code (`framework/`, `tests/`, `mcp_server/`)
- README.md (project documentation)

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

- **Phase 0 (Design):** `docs/0-design-discussion-v2.md` - Conversational design discussion
- **Phase 1 (Define):** `docs/1-create-prd-v2.md` - Create PRD
- **Phase 2 (Divide):** `docs/2-generate-tasks-v2.md` - Break down into tasks
- **Phase 3 (Deliver):** `docs/3-process-task-list-v2.md` - Execute and ship

## Task Generation Rules

### Per-Capability Parent Task Pattern:

1. **Mark Core vs Glue**:
   - **Core** (logic/contracts) → TDD: write failing tests → implement → refactor
   - **Glue** (wiring/UX) → Ensure acceptance/integration coverage exists

2. **Run & Record Checks** before marking parent complete:
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
