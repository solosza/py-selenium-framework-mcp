# FRAMEWORK.md - Complete Architecture Reference

**Version:** 1.1
**Status:** Authoritative Source of Truth
**Last Updated:** 2025-12-18

---

## Table of Contents

1. [4-Layer Architecture](#1-4-layer-architecture)
2. [OOP Principles](#2-oop-principles)
3. [Layer Rules Summary](#3-layer-rules-summary)
4. [Code Samples](#4-code-samples)
   - [4.1 Page Object Layer](#41-page-object-layer)
   - [4.2 Task Layer](#42-task-layer)
   - [4.3 Role Layer](#43-role-layer)
   - [4.4 Test Layer](#44-test-layer)
   - [4.5 conftest.py Pattern](#45-conftestpy-pattern)
   - [4.6 JSON Test Data Structure](#46-json-test-data-structure)
5. [Terminology](#5-terminology)
6. [Directory Structure](#6-directory-structure)
7. [Naming Conventions](#7-naming-conventions)
8. [MCP Tool Chain & AI Workflow](#8-mcp-tool-chain--ai-workflow)
   - [8.1 Workflow Overview](#81-workflow-overview)
   - [8.2 Step 1: User Input](#82-step-1-user-input)
   - [8.3 Step 2: AI Processing](#83-step-2-ai-processing)
   - [8.4 Step 3: Tool 1](#84-step-3-tool-1-generate_tests_from_user_story)
   - [8.5 Step 4: Tool 2](#85-step-4-tool-2-discover_page_elements)
   - [8.6 Step 5: Tool 3](#86-step-5-tool-3-generate_page_object)
   - [8.7 Step 6: Tool 4](#87-step-6-tool-4-generate_task)
   - [8.8 Step 7: Tool 5](#88-step-7-tool-5-generate_role)
   - [8.9 Step 8: Tool 6](#89-step-8-tool-6-generate_test_runner)
   - [8.10 Step 9: Save & Report](#810-step-9-ai-saves--reports)
   - [8.11 Design Decisions (DD-01 to DD-28)](#811-design-decisions)
   - [8.12 DD-16, DD-17, DD-18: AI Post-Processing](#812-dd-16-dd-17-dd-18-ai-post-processing-rules)
   - [8.13 DD-19: Tool Invocation Pattern](#813-dd-19-tool-invocation-pattern)
   - [8.14 DD-22: Stop-and-Discuss Protocol](#814-dd-22-stop-and-discuss-protocol-critical)
   - [8.15 Claude Code Skills](#815-claude-code-skills)
   - [8.16 DD-23: BDD Format Required](#816-dd-23-bdd-format-required-for-tool-1)
   - [8.17 DD-24: Test Credential Strategies](#817-dd-24-test-credential-strategies)
   - [8.18 DD-25: Skeleton Code Quality Gate](#818-dd-25-skeleton-code-quality-gate)
   - [8.19 DD-26: Tool Chain Data Contracts](#819-dd-26-tool-chain-data-contracts)
   - [8.20 DD-27: Task Code Quality Gate](#820-dd-27-task-code-quality-gate-no-locators)
   - [8.21 DD-28: Test Data Organization](#821-dd-28-test-data-organization)
9. [10-Step Workflow with Quality Gates (v2)](#9-10-step-workflow-with-quality-gates-v2)
   - [9.1 Step 1: Pre-flight Configuration](#91-step-1-pre-flight-configuration)
   - [9.2 Step 2: User Input](#92-step-2-user-input)
   - [9.3 Step 3: AI Processing](#93-step-3-ai-processing)
   - [9.4 Step 4: Tool 1](#94-step-4-tool-1)
   - [9.5 Step 5: Tool 2](#95-step-5-tool-2)
   - [9.6 Step 6: Tool 3](#96-step-6-tool-3)
   - [9.7 Step 7: Tool 4](#97-step-7-tool-4)
   - [9.8 Step 8: Tool 5](#98-step-8-tool-5)
   - [9.9 Step 9: Tool 6](#99-step-9-tool-6)
   - [9.10 Step 10: Save & Run](#910-step-10-save--run)

---

## 1. 4-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ TEST                                                                 │
│ - @autologger("Test") decorator                                      │
│ - Load data from JSON                                                │
│ - Call ONE workflow method per Role                                  │
│ - Assert via Page Object state-check methods directly                │
│ - NO orchestration (don't call multiple Role/Task methods)           │
└─────────────────────────────────────────────────────────────────────┘
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ ROLE                                                                 │
│ - @autologger("Role") on workflow methods                            │
│ - @autologger("Role Constructor") on __init__                        │
│ - Composes Task modules (instantiates in constructor)                │
│ - Workflow methods call MULTIPLE Tasks in sequence                   │
│ - NO return values (returns None)                                    │
│ - NO locators                                                        │
└─────────────────────────────────────────────────────────────────────┘
                              │ composes
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ TASK                                                                 │
│ - @autologger("Task") on all methods                                 │
│ - NO decorator on constructor                                        │
│ - Composes Page Objects (instantiates in constructor)                │
│ - One domain operation per method (SRP)                              │
│ - NO return values (returns None)                                    │
│ - NO locators (only in POMs)                                         │
│ - Uses fluent POM API (method chaining)                              │
└─────────────────────────────────────────────────────────────────────┘
                              │ composes
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ PAGE OBJECT                                                          │
│ - NO decorators on any methods                                       │
│ - Locators as class constants (UPPER_SNAKE_CASE)                     │
│ - Atomic methods (one UI action per method)                          │
│ - Return self for fluent chaining                                    │
│ - State-check methods for test assertions (return bool/value)        │
│ - Composes WebInterface                                              │
└─────────────────────────────────────────────────────────────────────┘
                              │ uses
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│ WEB INTERFACE                                                        │
│ - Wraps Selenium WebDriver                                           │
│ - Built-in wait/retry logic                                          │
│ - NO decorators                                                      │
│ - Provides: click, type_text, find_element, wait methods, etc.       │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Test Data (JSON) ──► Test ──► Role ──► Task ──► Page Object ──► WebInterface ──► Browser
                       │                                              │
                       └──────── Assertions via POM state-checks ◄────┘
```

### Key Architecture Rules

1. **No Inheritance** - Use composition, no base classes
2. **Locators ONLY in Page Objects** - Never in Tasks, Roles, or Tests
3. **Assertions via Page Objects** - Tests use POM state-check methods, not return values
4. **Single Responsibility** - Each layer has ONE job
5. **Exceptions Bubble Up** - Errors propagate from POM → Task → Role → Test

---

## 2. OOP Principles

| Principle | Implementation |
|-----------|----------------|
| **Encapsulation** | Each layer hides its internals. Pages hide locators, Tasks hide page orchestration, Roles hide task sequences. |
| **Composition** | Roles COMPOSE Tasks. Tasks COMPOSE Page Objects. No inheritance hierarchy. |
| **Single Responsibility (SRP)** | Each layer has ONE job. Pages = UI actions. Tasks = domain operations. Roles = workflows. Tests = assertions. |
| **Separation of Concerns** | Locators ONLY in POMs. Orchestration ONLY in Roles. Assertions ONLY in Tests. |
| **Abstraction** | Higher layers don't know lower-layer details. Role doesn't know locators. Test doesn't know page structure. |

---

## 3. Layer Rules Summary

| Layer | Decorator | Return Value | Composes | Fluent API |
|-------|-----------|--------------|----------|------------|
| **Page Object** | None | `self` | WebInterface | Yes |
| **Task** | `@autologger("Task")` | None | Page Objects | No (uses POM fluent API) |
| **Role** | `@autologger("Role")` | None | Tasks | No |
| **Test** | `@autologger("Test")` | N/A | Roles + POMs (assert) | No |

### Critical Rules

- **Tasks return None** - NOT bool. Tests assert via POM state-check methods.
- **Roles return None** - NOT bool. Tests assert via POM state-check methods.
- **Page Objects return self** - Enables fluent chaining for Tasks.
- **State-check methods return bool/value** - These are for test assertions.

---

## 4. Code Samples

### 4.1 Page Object Layer

```python
"""
Example Page Object - Generic login page pattern.

Replace locators and URLs with your application's specifics.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class LoginPage:
    """
    Page Object for Login/Authentication page.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== LOCATORS (Class Constants) ====================
    # Replace these with your application's locators

    EMAIL_INPUT = (By.ID, "email")
    PASSWORD_INPUT = (By.ID, "password")
    SUBMIT_BUTTON = (By.ID, "submit-login")
    ERROR_MESSAGE = (By.CSS_SELECTOR, ".error-message")
    LOGOUT_LINK = (By.CSS_SELECTOR, ".logout")
    SIGN_IN_LINK = (By.CSS_SELECTOR, ".login")

    # ==================== ATOMIC METHODS (One UI Action) ====================

    def enter_email(self, email: str) -> "LoginPage":
        """Enter email address."""
        self.web.type_text(*self.EMAIL_INPUT, text=email)
        return self  # Fluent API

    def enter_password(self, password: str) -> "LoginPage":
        """Enter password."""
        self.web.type_text(*self.PASSWORD_INPUT, text=password)
        return self

    def click_submit(self) -> "LoginPage":
        """Click sign in button."""
        self.web.click(*self.SUBMIT_BUTTON)
        return self

    # ==================== STATE-CHECK METHODS (For Assertions) ====================

    def is_logged_in(self) -> bool:
        """Check if user is logged in (logout link visible)."""
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    def is_logged_out(self) -> bool:
        """Check if user is logged out (sign in link visible)."""
        return self.web.is_element_displayed(*self.SIGN_IN_LINK, timeout=5)

    def has_error_message(self) -> bool:
        """Check if error message is displayed."""
        return self.web.is_element_displayed(*self.ERROR_MESSAGE, timeout=3)

    def get_error_message(self) -> str:
        """Get error message text."""
        if not self.has_error_message():
            return ""
        return self.web.get_text(*self.ERROR_MESSAGE)

    def is_page_loaded(self) -> bool:
        """Check if login page is loaded."""
        return self.web.is_element_displayed(*self.SUBMIT_BUTTON, timeout=5)
```

### 4.2 Task Layer

```python
"""
Example Task Module - Generic authentication tasks pattern.

Replace URLs and page objects with your application's specifics.
"""

from interfaces.web_interface import WebInterface
from pages.auth.login_page import LoginPage
from resources.utilities import autologger


class AuthTasks:
    """
    Task module for authentication operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    def __init__(self, web: WebInterface, base_url: str):
        """Compose Page Objects - NO decorator on constructor."""
        self.web = web
        self.base_url = base_url
        self.login_page = LoginPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str):
        """
        Complete login operation.

        Single domain operation: authenticate user.
        NO return value - test asserts via POM.
        """
        # Navigate to login page (replace URL pattern for your app)
        self.web.navigate_to(f"{self.base_url}/login")

        # Use fluent POM API (method chaining)
        (self.login_page
            .enter_email(email)
            .enter_password(password)
            .click_submit())

        # NO return - test will assert via login_page.is_logged_in()

    @autologger.automation_logger("Task")
    def log_out(self):
        """
        Complete logout operation.

        NO return value.
        """
        self.login_page.click_logout()
        # NO return - test will assert via login_page.is_logged_out()

    @autologger.automation_logger("Task")
    def navigate_to_login_page(self):
        """Navigate to authentication page."""
        self.web.navigate_to(f"{self.base_url}/login")
        # NO return
```

### 4.3 Role Layer

```python
"""
Example Role - Generic authenticated user pattern.

Roles represent user personas (e.g., Admin, Customer, Guest).
Replace task modules and workflows with your application's specifics.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.auth_tasks import AuthTasks
from tasks.order_tasks import OrderTasks
from resources.utilities import autologger


class AuthenticatedUser:
    """
    Authenticated User role - orchestrates complete business workflows.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    - NO locators
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        """
        Initialize with credentials and compose Task modules.
        """
        self.web = web_interface
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.base_url = base_url

        # Validate required credentials
        if not self.email or not self.password:
            raise ValueError("AuthenticatedUser requires email and password")

        # Compose Task modules (add your application's task modules)
        self.auth_tasks = AuthTasks(web_interface, base_url)
        self.order_tasks = OrderTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login(self):
        """
        Login workflow.

        Orchestrates: navigate + enter credentials + submit
        NO return value - test asserts via POM.
        """
        self.auth_tasks.log_in(self.email, self.password)
        # NO return

    @autologger.automation_logger("Role")
    def logout(self):
        """
        Logout workflow.

        NO return value.
        """
        self.auth_tasks.log_out()
        # NO return

    @autologger.automation_logger("Role")
    def complete_purchase(self, product_data: Dict[str, Any]):
        """
        Complete purchase workflow.

        Orchestrates MULTIPLE task calls - this is what makes
        Role different from Task. A Role method is a complete
        user journey/story.

        NO return value - test asserts via POM.
        """
        self.order_tasks.add_to_cart(product_data)
        self.order_tasks.proceed_to_checkout()
        self.order_tasks.complete_payment()
        # NO return - test asserts via POM state-check methods
```

### 4.4 Test Layer

```python
"""
Example Test - Generic test pattern.

Replace role and page imports with your application's specifics.
"""

import pytest
from roles.authenticated_user import AuthenticatedUser
from pages.auth.login_page import LoginPage
from resources.utilities import autologger


class TestLogin:
    """
    Login test suite.

    - @autologger("Test") decorator
    - Load data from JSON (via fixture)
    - Call ONE workflow method per Role
    - Assert via Page Object state-check methods
    - NO orchestration (don't call multiple Role methods)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config, test_data):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config
        self.test_data = test_data
        self.login_page = LoginPage(web_interface)

    @autologger.automation_logger("Test")
    def test_valid_login(self):
        """
        Test that user can login with valid credentials.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check method
        """
        # Arrange
        user = AuthenticatedUser(
            self.web,
            self.test_data["valid_user"],
            self.config["base_url"]
        )

        # Act - ONE workflow call, NO return value
        user.login()

        # Assert - Via Page Object state-check method (NOT return value)
        assert self.login_page.is_logged_in(), "User should be logged in"

    @autologger.automation_logger("Test")
    def test_invalid_login(self):
        """Test that invalid credentials show error."""
        # Arrange
        user = AuthenticatedUser(
            self.web,
            self.test_data["invalid_user"],
            self.config["base_url"]
        )

        # Act - Role method returns nothing
        user.login()

        # Assert via POM state-check methods
        assert self.login_page.has_error_message(), "Error should be displayed"
```

### 4.5 conftest.py Pattern

```python
"""
Pytest fixtures for test automation framework.
"""

import pytest
import json
from pathlib import Path
from interfaces.web_interface import WebInterface


@pytest.fixture(scope="session")
def config():
    """Load configuration from JSON."""
    config_path = Path(__file__).parent / "config.json"
    with open(config_path) as f:
        return json.load(f)


@pytest.fixture(scope="function")
def web_interface(config):
    """
    Create WebInterface instance for each test.

    Handles browser setup and teardown.
    """
    web = WebInterface(
        browser=config.get("browser", "chrome"),
        headless=config.get("headless", False)
    )
    yield web
    web.quit()


@pytest.fixture(scope="function")
def test_data(request):
    """
    Load test data from JSON file in test's data/ directory.

    Expects: tests/<domain>/data/<test_name>.json
    """
    test_dir = Path(request.fspath).parent
    data_file = test_dir / "data" / f"{request.node.name}.json"

    if data_file.exists():
        with open(data_file) as f:
            return json.load(f)

    # Fallback to default data file
    default_file = test_dir / "data" / "default.json"
    if default_file.exists():
        with open(default_file) as f:
            return json.load(f)

    return {}
```

### 4.6 JSON Test Data Structure

```json
{
  "valid_user": {
    "email": "testuser@example.com",
    "password": "SecurePass123",
    "first_name": "Test",
    "last_name": "User"
  },
  "invalid_user": {
    "email": "invalid@example.com",
    "password": "wrongpassword"
  },
  "new_user": {
    "email": "newuser@example.com",
    "password": "NewPass123",
    "first_name": "New",
    "last_name": "User",
    "profile": {
      "address": "123 Test Street",
      "city": "Test City",
      "state": "Test State",
      "zipcode": "12345",
      "phone": "555-000-0000"
    }
  },
  "product": {
    "name": "Test Product",
    "quantity": 1
  }
}
```

**Note:** Structure your JSON to match your application's data requirements.
The fixture in conftest.py loads this data and passes it to tests.

---

## 5. Terminology

### OOP & Architecture Terms

| Term | Definition |
|------|------------|
| **Encapsulation** | Each layer hides its internals from other layers |
| **Composition** | Objects contain/instantiate other objects (preferred over inheritance) |
| **SRP** | Single Responsibility Principle - each layer has ONE job |
| **Separation of Concerns** | Specific responsibilities stay in specific layers |
| **Abstraction** | Higher layers don't know lower-layer implementation details |
| **No Inheritance** | Design decision - use composition, no base classes |

### Layer-Specific Terms

| Term | Definition |
|------|------------|
| **WebInterface** | Foundation layer that wraps Selenium WebDriver with wait/retry logic |
| **Atomic method** | Page Object method that performs ONE UI action |
| **State-check method** | Page Object method that returns bool/value for test assertions |
| **Fluent API** | Methods return `self` to enable chaining (Page Objects only) |
| **Class Constants** | Locators defined at class level using UPPER_SNAKE_CASE naming |
| **Domain operation** | Task method that performs one business operation |
| **Orchestration** | Role coordinates multiple Task calls in sequence |
| **Workflow method** | Role method that calls multiple Task methods to complete a business flow |
| **Credentials** | User authentication data (email, password) passed to Role |

### Code Pattern Terms

| Term | Definition |
|------|------------|
| **Decorator** | Python annotation (e.g., `@autologger`) that wraps a method |
| **Constructor** | `__init__` method that initializes class and composes dependencies |
| **Compose** | Create instances of lower-layer modules in constructor |
| **AAA Pattern** | Arrange, Act, Assert - standard test structure |
| **Data-driven** | Test data loaded from external JSON files, not hardcoded |
| **Fixtures** | Pytest setup/teardown mechanism defined in conftest.py |
| **Exceptions bubble up** | Errors propagate from POM → Task → Role → Test |

### Quality Terms

| Term | Definition |
|------|------------|
| **Layer violation** | Breaking architecture rules (e.g., locators in Task) |
| **CRITICAL defect** | Breaks 4-layer architecture |
| **HIGH defect** | Wrong layer responsibility |
| **MEDIUM defect** | Missing required elements |
| **LOW defect** | Style/naming issues |

---

## 6. Directory Structure

```
framework/
├── interfaces/
│   └── web_interface.py      # Selenium wrapper
├── pages/
│   ├── <domain>/              # Group pages by domain
│   │   ├── <name>_page.py
│   │   └── <name>_modal.py
│   └── common/                # Shared pages (login, home, etc.)
│       └── home_page.py
├── tasks/
│   ├── <domain>/              # Group tasks by domain
│   │   └── <domain>_tasks.py
│   └── common/                # Shared tasks
│       └── common_tasks.py
├── roles/
│   └── <persona>.py           # User personas (admin, customer, guest)
└── resources/
    └── utilities/             # Helpers
        └── autologger.py

tests/
├── <domain>/
│   ├── data/                  # JSON test data
│   │   └── <test_name>.json
│   └── test_<feature>.py
└── conftest.py                # Pytest fixtures
```

**Example for an e-commerce application:**
```
framework/
├── pages/
│   ├── auth/
│   │   ├── login_page.py
│   │   └── registration_page.py
│   ├── catalog/
│   │   ├── product_list_page.py
│   │   └── product_detail_page.py
│   └── checkout/
│       ├── cart_page.py
│       └── payment_page.py
├── tasks/
│   ├── auth_tasks.py
│   ├── catalog_tasks.py
│   └── checkout_tasks.py
└── roles/
    ├── customer.py
    ├── guest.py
    └── admin.py
```

---

## 7. Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Page Object class | `<Name>Page` or `<Name>Modal` | `LoginPage`, `QuickViewModal` |
| Task class | `<Domain>Tasks` | `CommonTasks`, `CatalogTasks` |
| Role class | `<Persona>` (no suffix) | `RegisteredUser`, `GuestUser` |
| Test class | `Test<Feature>` | `TestUserLogin`, `TestCatalog` |
| Test function | `test_<action>` | `test_valid_login`, `test_filter_products` |
| File names | `snake_case.py` | `login_page.py`, `common_tasks.py` |
| Locator constants | `UPPER_SNAKE_CASE` | `EMAIL_INPUT`, `SUBMIT_BUTTON` |
| Directories | `snake_case` | `common_tasks/`, `test_data/` |

---

## Quick Reference Card

```
┌────────────────────────────────────────────────────────────────┐
│                    LAYER QUICK REFERENCE                        │
├──────────┬─────────────────┬────────────┬──────────────────────┤
│ Layer    │ Decorator       │ Returns    │ Key Rule             │
├──────────┼─────────────────┼────────────┼──────────────────────┤
│ Page     │ None            │ self       │ Atomic methods only  │
│ Task     │ @auto..("Task") │ None       │ One domain operation │
│ Role     │ @auto..("Role") │ None       │ Orchestrate tasks    │
│ Test     │ @auto..("Test") │ N/A        │ Assert via POM       │
└──────────┴─────────────────┴────────────┴──────────────────────┘

GOLDEN RULES:
1. Locators ONLY in Page Objects
2. Tasks/Roles return NOTHING (None)
3. Tests assert via POM state-check methods
4. No inheritance - composition only
5. One responsibility per layer
```

---

## 8. MCP Tool Chain & AI Workflow

This section documents the complete AI-assisted test generation workflow. The MCP server exposes tools that generate code following the 4-layer architecture patterns defined above.

### 8.1 Workflow Overview

The tool chain uses a **bottom-up approach**: Page Object → Task → Role → Test. Each layer needs information from the previous one to generate accurate method calls.

```
USER INPUT → AI PROCESSING → TOOL 1 → TOOL 2 → TOOL 3 → TOOL 4 → TOOL 5 → TOOL 6 → GENERATED CODE
```

### 8.2 Step 1: User Input

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              STEP 1: USER INPUT                             │
│                                                                             │
│  User provides:                                                             │
│  1. Plain English requirement with persona                                  │
│     "As a registered user, I want to login with email and password"         │
│     "As a guest, I want to browse products by category"                     │
│                                                                             │
│  2. Target URL                                                              │
│     "http://automationpractice.pl/index.php?controller=authentication"      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.3 Step 2: AI Processing

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 2: AI PROCESSING                               │
│                                                                             │
│  AI receives input and:                                                     │
│                                                                             │
│  1. Extracts ROLE from requirement                                          │
│     "As a registered user..." → RegisteredUser                              │
│     "As a guest..." → GuestUser                                             │
│                                                                             │
│  2. Extracts USER INTENT (descriptive)                                      │
│     "I want to login" → intent: "login"                                     │
│     "I want to browse products" → intent: "browse_products"                 │
│                                                                             │
│  3. Determines DOMAIN (for folder organization)                             │
│     login/logout/register → domain: "auth"                                  │
│     browse/filter/search products → domain: "catalog"                       │
│     add to cart/update cart → domain: "cart"                                │
│     checkout/payment → domain: "checkout"                                   │
│                                                                             │
│  4. Converts plain English → BDD format                                     │
│     Given user is on login page                                             │
│     When user enters valid credentials and clicks login                     │
│     Then user is logged in and sees account page                            │
│                                                                             │
│  5. Extracts EXPECTED STATES from "Then" clause (for POM state methods)     │
│     "Then user is logged in" → expected_state: "is_logged_in"               │
│     "Then error message is displayed" → expected_state: "has_error_message" │
│     "Then cart shows 2 items" → expected_state: "get_cart_count"            │
│                                                                             │
│     Naming conventions for state methods:                                   │
│     - Boolean checks: is_* or has_* (returns bool)                          │
│     - Value retrieval: get_* (returns str/int)                              │
│                                                                             │
│  6. Initializes metadata context (passed through tool chain)                │
│     {                                                                       │
│       "role_name": "RegisteredUser",                                        │
│       "intent": "login",                                                    │
│       "domain": "auth",                                                     │
│       "url": "http://...",                                                  │
│       "bdd_scenarios": [...],                                               │
│       "expected_states": [                                                  │
│         { "name": "is_logged_in", "description": "user is logged in" }      │
│       ]                                                                     │
│     }                                                                       │
│                                                                             │
│  NOTE: Exact method names emerge from tool chain execution, not from this   │
│        step. Bottom-up approach means POM methods determine Task methods,   │
│        which determine Role methods.                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

AI PROMPTING RULES FOR STEP 2:
┌─────────────────────────────────────────────────────────────────────────────┐
│  When processing user input, AI MUST:                                       │
│                                                                             │
│  1. VALIDATE USER INPUT                                                     │
│     - Requirement MUST contain persona ("As a...")                          │
│     - If missing, ASK user: "What type of user performs this action?"       │
│     - URL MUST be provided                                                  │
│     - If missing, ASK user for the target page URL                          │
│                                                                             │
│  2. EXTRACT ROLE NAME ACCURATELY                                            │
│     - "As a registered user" → RegisteredUser                               │
│     - "As a guest" / "As a visitor" → GuestUser                             │
│     - "As an admin" / "As an administrator" → AdminUser                     │
│     - If ambiguous, ASK user to clarify                                     │
│                                                                             │
│  3. DETERMINE DOMAIN FROM INTENT                                            │
│     - Keywords: login, logout, sign in, register → domain: "auth"           │
│     - Keywords: browse, catalog, products, filter, search → domain:"catalog"│
│     - Keywords: cart, basket, add to cart → domain: "cart"                  │
│     - Keywords: checkout, payment, order → domain: "checkout"               │
│                                                                             │
│  4. CONVERT TO PROPER BDD FORMAT                                            │
│     - Each scenario MUST have Given, When, Then                             │
│     - Given = precondition/state                                            │
│     - When = action performed                                               │
│     - Then = expected outcome (becomes state-check method)                  │
│                                                                             │
│  5. EXTRACT EXPECTED STATES FOR ASSERTIONS                                  │
│     - Parse "Then" clause for state descriptions                            │
│     - Convert to method names: is_*, has_*, get_*                           │
│     - Example: "user is logged in" → is_logged_in                           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.4 Step 3: Tool 1 (generate_tests_from_user_story)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 3: TOOL 1                                      │
│                         generate_tests_from_user_story                      │
│                                                                             │
│  Input (from AI):                                                           │
│  {                                                                          │
│    "user_story": "As a registered user, I want to login...\n                │
│                   Given user is on login page\n                             │
│                   When user enters valid credentials and clicks login\n     │
│                   Then user is logged in",                                  │
│    "workflow": "auth"                                                       │
│  }                                                                          │
│                                                                             │
│  Tool does:                                                                 │
│  1. Parses BDD scenarios from user story text                               │
│  2. Validates Given/When/Then structure                                     │
│  3. Generates test scenario names from scenario content                     │
│                                                                             │
│  Output:                                                                    │
│  {                                                                          │
│    "status": "success",                                                     │
│    "scenarios": [                                                           │
│      {                                                                      │
│        "title": "test_user_logs_in_with_valid_credentials",                 │
│        "given": "user is on login page",                                    │
│        "when": "user enters valid credentials and clicks login",            │
│        "then": "user is logged in"                                          │
│      }                                                                      │
│    ],                                                                       │
│    "workflow": "auth"                                                       │
│  }                                                                          │
│                                                                             │
│  AI updates metadata context:                                               │
│  {                                                                          │
│    "role_name": "RegisteredUser",                                           │
│    "intent": "login",                                                       │
│    "domain": "auth",                                                        │
│    "url": "http://...",                                                     │
│    "bdd_scenarios": [...],                                                  │
│    "test_scenarios": [...]  ← Added from Tool 1 output                      │
│  }                                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

AI PROMPTING RULES FOR TOOL 1:
┌─────────────────────────────────────────────────────────────────────────────┐
│  Before calling Tool 1, AI MUST:                                            │
│                                                                             │
│  1. FORMAT BDD CORRECTLY                                                    │
│     - Include full user story with "As a..., I want..., So that..."         │
│     - Each scenario has Given/When/Then on separate lines                   │
│     - Use clear, action-oriented language                                   │
│                                                                             │
│  2. PASS CORRECT WORKFLOW                                                   │
│     - workflow = domain determined in Step 2                                │
│     - Must be one of: "auth", "catalog", "cart", "checkout"                 │
│                                                                             │
│  3. VALIDATE TOOL OUTPUT                                                    │
│     - Check status = "success"                                              │
│     - Verify scenarios array is not empty                                   │
│     - Each scenario must have title, given, when, then                      │
│                                                                             │
│  4. UPDATE METADATA CONTEXT                                                 │
│     - Add test_scenarios from Tool 1 output to metadata                     │
│     - Preserve all existing metadata fields                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.5 Step 4: Tool 2 (discover_page_elements)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 4: TOOL 2                                      │
│                         discover_page_elements                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  DECISION: Static or Dynamic Elements?                                      │
│  ─────────────────────────────────────                                      │
│                                                                             │
│  AI analyzes the requirement and determines:                                │
│  - Are target elements visible on page load? → STATIC FLOW                  │
│  - Do elements require interaction to appear? → DYNAMIC FLOW (DD-20)        │
│                                                                             │
│  Examples:                                                                  │
│  - Login form fields → STATIC (visible on load)                             │
│  - Cart confirmation modal → DYNAMIC (appears after Add to Cart click)      │
│  - Dropdown menu items → DYNAMIC (appears on hover/click)                   │
│  - Product list → STATIC (visible on load)                                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌─────────────────────────────────┐ ┌─────────────────────────────────────────┐
│      STATIC FLOW                │ │      DYNAMIC FLOW (DD-20)               │
│      (elements on page load)    │ │      (elements require interaction)     │
├─────────────────────────────────┤ ├─────────────────────────────────────────┤
│                                 │ │                                         │
│  Input (from AI):               │ │  AI PREPARES PAGE STATE FIRST:          │
│  {                              │ │                                         │
│    "url": "http://..."          │ │  1. AI reasons about page behavior:     │
│  }                              │ │     "Modal appears after Add to Cart"   │
│                                 │ │     "Button visible on product hover"   │
│  Tool 2 does:                   │ │                                         │
│  1. Creates WebDriver session   │ │  2. AI creates driver and manipulates:  │
│  2. Navigates to URL            │ │     driver = create_webdriver()         │
│  3. Waits for page load         │ │     driver.get(url)                     │
│  4. Discovers elements          │ │     driver.hover(".product-container")  │
│  5. Returns elements            │ │     driver.click(".add-to-cart")        │
│  6. Closes driver               │ │     wait(2)  # modal appears            │
│                                 │ │                                         │
│                                 │ │  3. AI calls Tool 2 with session:       │
│                                 │ │     {                                   │
│                                 │ │       "driver_session": driver,         │
│                                 │ │       "scope": "#modal-container"       │
│                                 │ │     }                                   │
│                                 │ │                                         │
│                                 │ │  Tool 2 does:                           │
│                                 │ │  1. Uses existing driver (no nav)       │
│                                 │ │  2. Discovers within scope              │
│                                 │ │  3. Returns elements                    │
│                                 │ │  4. Does NOT close driver (AI owns it)  │
│                                 │ │                                         │
└─────────────────────────────────┘ └─────────────────────────────────────────┘
                    │                               │
                    └───────────────┬───────────────┘
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Tool 2 Output (same format for both flows):                                │
│  {                                                                          │
│    "status": "success",                                                     │
│    "url": "http://...",                                                     │
│    "elements": [                                                            │
│      { "name": "email", "type": "input", "locator": "#email" },             │
│      { "name": "passwd", "type": "input", "locator": "#passwd" },           │
│      { "name": "SubmitLogin", "type": "button", "locator": "#SubmitLogin" } │
│    ],                                                                       │
│    "metadata": {                                                            │
│      "discovered_elements": [...]                                           │
│    }                                                                        │
│  }                                                                          │
│                                                                             │
│  AI updates metadata context:                                               │
│  {                                                                          │
│    "role_name": "RegisteredUser",                                           │
│    "intent": "login",                                                       │
│    "domain": "auth",                                                        │
│    "url": "http://...",                                                     │
│    "bdd_scenarios": [...],                                                  │
│    "test_scenarios": [...],                                                 │
│    "discovered_elements": [...]  ← Added from Tool 2 output                 │
│  }                                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

AI PROMPTING RULES FOR TOOL 2:
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  1. DETERMINE STATIC vs DYNAMIC                                             │
│     - Analyze requirement: do target elements exist on page load?           │
│     - If NO → use dynamic flow (prepare page state first)                   │
│     - If YES → use static flow (just pass URL)                              │
│                                                                             │
│  2. FOR DYNAMIC FLOW (DD-20)                                                │
│     - AI reasons about HOW to reveal the elements                           │
│     - AI creates WebDriver session using framework's WebInterface           │
│     - AI performs necessary interactions (hover, click, wait, etc.)         │
│     - AI passes driver_session to Tool 2 (NOT url)                          │
│     - AI optionally provides scope to limit discovery area                  │
│     - AI is responsible for closing driver after all discovery complete     │
│                                                                             │
│  3. VALIDATE URL (static flow only)                                         │
│     - URL must be complete (include protocol http/https)                    │
│     - URL must be accessible (target application must be running)           │
│                                                                             │
│  4. VALIDATE TOOL OUTPUT                                                    │
│     - Check status = "success"                                              │
│     - Verify elements array is not empty                                    │
│     - Each element must have name, type, locator                            │
│     - If empty, WARN user: "No interactive elements found"                  │
│                                                                             │
│  5. FILTER RELEVANT ELEMENTS                                                │
│     - Focus on elements relevant to the user's intent                       │
│     - For login: email input, password input, submit button                 │
│     - For modal: confirmation buttons, status text, close button            │
│     - Ignore generic navigation elements unless relevant                    │
│                                                                             │
│  6. UPDATE METADATA CONTEXT                                                 │
│     - Add discovered_elements from Tool 2 output to metadata                │
│     - Preserve all existing metadata fields                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

DD-21: AI-SDET COLLABORATION FOR DYNAMIC DISCOVERY
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  When AI is preparing page state for dynamic discovery (DD-20), it may      │
│  encounter issues: elements with zero dimensions, wrong page structure,     │
│  out-of-stock products, iframes, etc.                                       │
│                                                                             │
│  PRIMARY APPROACH (token-optimized):                                        │
│  ───────────────────────────────────                                        │
│                                                                             │
│    ┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐         │
│    │ AI tries │────▶│  Fails   │────▶│ AI tries │────▶│  Fails   │         │
│    │ script 1 │     │          │     │ script 2 │     │  again   │         │
│    └──────────┘     └──────────┘     └──────────┘     └────┬─────┘         │
│                                                            │                │
│                           AI recognizes: "Same error pattern, I'm stuck"    │
│                                                            │                │
│                                                            ▼                │
│    ┌────────────────────────────────────────────────────────────────────┐  │
│    │  AI asks SDET specific question:                                   │  │
│    │  - "Products report zero dimensions. Different page structure?"    │  │
│    │  - "Modal appeared but 0 elements. Is content in iframe?"          │  │
│    │  - "Add to Cart clicked but no modal. Product out of stock?"       │  │
│    └────────────────────────────────────────────────────────────────────┘  │
│                                                            │                │
│                                                            ▼                │
│    ┌──────────┐     ┌──────────────────────────────────────────────────┐   │
│    │  SDET    │────▶│  AI continues with new knowledge                 │   │
│    │ provides │     │  "Use category page, switch to iframe first"     │   │
│    │ guidance │     └──────────────────────────────────────────────────┘   │
│    └──────────┘                                                             │
│                                                                             │
│  ALTERNATE APPROACH (fully autonomous, higher token cost):                  │
│  ─────────────────────────────────────────────────────────                  │
│                                                                             │
│    ┌────────────────┐     ┌────────────────┐     ┌────────────────┐        │
│    │ AI uses        │────▶│ AI documents   │────▶│ AI writes      │        │
│    │ Playwright MCP │     │ site quirks:   │     │ Selenium script│        │
│    │ for visual     │     │ - iframes      │     │ with that      │        │
│    │ reconnaissance │     │ - selectors    │     │ knowledge      │        │
│    └────────────────┘     │ - page struct  │     └────────────────┘        │
│                           └────────────────┘                                │
│                                                                             │
│    Playwright = eyes for exploration                                        │
│    Selenium = hands for Tool 2 integration                                  │
│                                                                             │
│  WHEN TO USE ALTERNATE:                                                     │
│  ──────────────────────                                                     │
│    - SDET unavailable or wants hands-off                                    │
│    - Complex site with many dynamic elements                                │
│    - Token cost acceptable for full autonomy                                │
│    - Manual testers learning test automation (AI guides discovery)          │
│    - Junior devs/SDETs (reduces need for senior expertise)                  │
│                                                                             │
│  STATUS: Alternate approach documented for future testing                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.6 Step 5: Tool 3 (generate_page_object)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 5: TOOL 3                                      │
│                         generate_page_object                                │
│                                                                             │
│  Input (from AI):                                                           │
│  {                                                                          │
│    "page_name": "LoginPage",                                                │
│    "elements": [...],           ← From Tool 2                               │
│    "domain": "auth",            ← From metadata                             │
│    "expected_states": [         ← From AI (extracted from BDD "Then")       │
│      { "name": "is_logged_in", "description": "user is logged in" }         │
│    ]                                                                        │
│  }                                                                          │
│                                                                             │
│  Tool does:                                                                 │
│  1. Generates Page Object class with locators as UPPER_SNAKE constants      │
│  2. Creates atomic action methods based on element types:                   │
│     - input → enter_<name>(value: str)                                      │
│     - button → click_<name>()                                               │
│     - link → click_<name>()                                                 │
│     - select → select_<name>(option: str)                                   │
│     - checkbox → check_<name>(), uncheck_<name>()                           │
│  3. Creates state-check methods from expected_states:                       │
│     - is_* methods return bool                                              │
│     - has_* methods return bool                                             │
│     - get_* methods return str/int                                          │
│  4. Builds metadata describing all generated methods                        │
│                                                                             │
│  Output:                                                                    │
│  {                                                                          │
│    "status": "success",                                                     │
│    "code": "class LoginPage:\n    EMAIL_INPUT = ...",                       │
│    "file_path": "framework/pages/auth/login_page.py",                       │
│    "metadata": {                                                            │
│      "class_name": "LoginPage",                                             │
│      "import_path": "pages.auth.login_page",                                │
│      "locators": [                                                          │
│        { "name": "EMAIL_INPUT", "by": "CSS_SELECTOR", "value": "#email" }   │
│      ],                                                                     │
│      "action_methods": [                                                    │
│        { "name": "enter_email", "params": ["email: str"], "returns": "self"}│
│      ],                                                                     │
│      "state_methods": [                                                     │
│        { "name": "is_logged_in", "params": [], "returns": "bool" }          │
│      ]                                                                      │
│    }                                                                        │
│  }                                                                          │
│                                                                             │
│  AI updates metadata context:                                               │
│  {                                                                          │
│    ...,                                                                     │
│    "pom_metadata": { ... }  ← Added from Tool 3 output                      │
│  }                                                                          │
│                                                                             │
│  NOTE: POM metadata is critical - Tool 4 uses it to generate Task methods   │
│        that call actual POM methods (no hardcoding).                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

AI PROMPTING RULES FOR TOOL 3:
┌─────────────────────────────────────────────────────────────────────────────┐
│  Before calling Tool 3, AI MUST:                                            │
│                                                                             │
│  1. DETERMINE PAGE NAME                                                     │
│     - Use intent + "Page" suffix: LoginPage, ProductListPage, CartPage      │
│     - Name should reflect the page's purpose, not URL                       │
│                                                                             │
│  2. PASS EXPECTED STATES                                                    │
│     - Include expected_states from Step 2 metadata                          │
│     - These become state-check methods in the POM                           │
│     - Without this, Tool 3 cannot generate correct assertions               │
│                                                                             │
│  3. CHECK FOR EXISTING POM                                                  │
│     - Scan framework/pages/<domain>/ for existing page objects              │
│     - If similar page exists, consider extending vs creating new            │
│                                                                             │
│  4. VALIDATE TOOL OUTPUT                                                    │
│     - Check status = "success"                                              │
│     - Verify metadata contains class_name, action_methods, state_methods    │
│     - Verify state_methods includes methods from expected_states            │
│                                                                             │
│  5. UPDATE METADATA CONTEXT                                                 │
│     - Add pom_metadata from Tool 3 output                                   │
│     - This is CRITICAL for Tool 4 to generate correct Task methods          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.7 Step 6: Tool 4 (generate_task)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 6: TOOL 4                                      │
│                         generate_task                                       │
│                                                                             │
│  IMPORTANT: Check existing before creating new!                             │
│                                                                             │
│  Input (from AI):                                                           │
│  {                                                                          │
│    "task_name": "CommonTasks",       ← May use existing class               │
│    "domain": "auth",                                                        │
│    "pom_metadata": { ... },          ← From Tool 3                          │
│    "check_existing": true            ← Flag to scan for existing tasks      │
│  }                                                                          │
│                                                                             │
│  Tool does:                                                                 │
│  1. FIRST: Scans framework/tasks/ for existing Task classes                 │
│  2. If matching Task exists with needed methods → return existing info      │
│  3. If no match → generate new Task class                                   │
│  4. Reads POM metadata to know available action methods                     │
│  5. Groups related actions into Task methods                                │
│  6. Generates with @autologger("Task") decorators, NO return values         │
│  7. Builds metadata describing Task methods                                 │
│                                                                             │
│  Output (existing found):                                                   │
│  {                                                                          │
│    "status": "existing_found",                                              │
│    "message": "CommonTasks already has log_in method",                      │
│    "existing_class": "CommonTasks",                                         │
│    "existing_methods": ["log_in", "log_out", "register_new_user"],          │
│    "file_path": "framework/tasks/common/common_tasks.py",                   │
│    "metadata": { ... }               ← Metadata of existing class           │
│  }                                                                          │
│                                                                             │
│  Output (new generated):                                                    │
│  {                                                                          │
│    "status": "success",                                                     │
│    "code": "class CatalogTasks:\n    @autologger...",                       │
│    "file_path": "framework/tasks/catalog/catalog_tasks.py",                 │
│    "metadata": {                                                            │
│      "class_name": "CatalogTasks",                                          │
│      "import_path": "tasks.catalog.catalog_tasks",                          │
│      "composed_pages": ["ProductListPage"],                                 │
│      "task_methods": [                                                      │
│        { "name": "browse_category", "params": ["category: str"] }           │
│      ]                                                                      │
│    }                                                                        │
│  }                                                                          │
│                                                                             │
│  AI updates metadata context:                                               │
│  {                                                                          │
│    ...,                                                                     │
│    "task_metadata": { ... }  ← From Tool 4 output (existing or new)         │
│  }                                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

AI PROMPTING RULES FOR TOOL 4:
┌─────────────────────────────────────────────────────────────────────────────┐
│  Before calling Tool 4, AI MUST:                                            │
│                                                                             │
│  1. CHECK EXISTING TASKS FIRST                                              │
│     - Scan framework/tasks/ for existing Task classes                       │
│     - CommonTasks handles: log_in, log_out, register_new_user               │
│     - CatalogTasks handles: browse_category, filter_products, etc.          │
│     - If intent matches existing method → use it, don't create new          │
│                                                                             │
│  2. DETERMINE CORRECT TASK CLASS                                            │
│     - Auth operations → CommonTasks (already exists)                        │
│     - Catalog operations → CatalogTasks                                     │
│     - Cart operations → CartTasks                                           │
│     - Checkout operations → CheckoutTasks                                   │
│                                                                             │
│  3. ONLY CREATE NEW IF:                                                     │
│     - No existing Task class handles the domain, OR                         │
│     - Existing class lacks the specific method needed                       │
│                                                                             │
│  4. NAMING CONVENTIONS                                                      │
│     - Task class: <Domain>Tasks (e.g., CatalogTasks)                        │
│     - Task methods: verb_noun (e.g., browse_category, add_to_cart)          │
│     - Use snake_case for all method names                                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.8 Step 7: Tool 5 (generate_role)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 7: TOOL 5                                      │
│                         generate_role                                       │
│                                                                             │
│  IMPORTANT: Check existing before creating new!                             │
│                                                                             │
│  Input (from AI):                                                           │
│  {                                                                          │
│    "role_name": "RegisteredUser",    ← From Step 2                          │
│    "domain": "auth",                                                        │
│    "task_metadata": { ... },         ← From Tool 4                          │
│    "intent": "login",                ← Workflow method to generate          │
│    "check_existing": true                                                   │
│  }                                                                          │
│                                                                             │
│  Tool does:                                                                 │
│  1. FIRST: Scans framework/roles/ for existing Role classes                 │
│  2. If Role exists with needed workflow method → return existing info       │
│  3. If no match → generate new Role class or add method to existing         │
│  4. Reads Task metadata to know available Task methods                      │
│  5. Generates workflow method that orchestrates Task calls                  │
│  6. @autologger("Role") decorators, NO return values                        │
│                                                                             │
│  Output (existing found):                                                   │
│  {                                                                          │
│    "status": "existing_found",                                              │
│    "existing_class": "RegisteredUser",                                      │
│    "existing_methods": ["login", "logout", "register"],                     │
│    "file_path": "framework/roles/auth/registered_user.py",                  │
│    "metadata": { ... }                                                      │
│  }                                                                          │
│                                                                             │
│  Output (new generated):                                                    │
│  {                                                                          │
│    "status": "success",                                                     │
│    "code": "class GuestUser:\n    @autologger...",                          │
│    "file_path": "framework/roles/guest/guest_user.py",                      │
│    "metadata": {                                                            │
│      "class_name": "GuestUser",                                             │
│      "import_path": "roles.guest.guest_user",                               │
│      "composed_tasks": ["CatalogTasks"],                                    │
│      "workflow_methods": [                                                  │
│        { "name": "browse_category", "params": ["category: str"] }           │
│      ]                                                                      │
│    }                                                                        │
│  }                                                                          │
│                                                                             │
│  AI updates metadata context:                                               │
│  {                                                                          │
│    ...,                                                                     │
│    "role_metadata": { ... }  ← From Tool 5 output (existing or new)         │
│  }                                                                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

AI PROMPTING RULES FOR TOOL 5:
┌─────────────────────────────────────────────────────────────────────────────┐
│  Before calling Tool 5, AI MUST:                                            │
│                                                                             │
│  1. CHECK EXISTING ROLES FIRST                                              │
│     - Scan framework/roles/ for existing Role classes                       │
│     - RegisteredUser handles: login, logout, register                       │
│     - GuestUser handles: browse_category, filter_products, etc.             │
│     - If intent matches existing method → use it, don't create new          │
│                                                                             │
│  2. MATCH ROLE TO PERSONA                                                   │
│     - "As a registered user..." → RegisteredUser                            │
│     - "As a guest..." → GuestUser                                           │
│     - "As an admin..." → AdminUser                                          │
│                                                                             │
│  3. ONLY CREATE NEW IF:                                                     │
│     - No existing Role class matches the persona, OR                        │
│     - Existing Role lacks the specific workflow method needed               │
│                                                                             │
│  4. NAMING CONVENTIONS                                                      │
│     - Role class: <Persona>User or <Persona> (e.g., RegisteredUser, Admin)  │
│     - Workflow methods: simple verb (login, logout, browse_category)        │
│     - Don't duplicate persona in method name (login, not login_as_user)     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.9 Step 8: Tool 6 (generate_test_runner)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 8: TOOL 6                                      │
│                         generate_test_runner                                │
│                                                                             │
│  Input (from AI):                                                           │
│  {                                                                          │
│    "test_name": "test_valid_login",                                         │
│    "domain": "auth",                                                        │
│    "role_metadata": { ... },         ← From Tool 5                          │
│    "pom_metadata": { ... },          ← From Tool 3 (for assertions)         │
│    "test_scenarios": [ ... ]         ← From Tool 1                          │
│  }                                                                          │
│                                                                             │
│  Tool does:                                                                 │
│  1. Generates pytest file (one file per scenario)                           │
│  2. Creates test function(s) from BDD scenarios                             │
│  3. Each test: Arrange (create Role), Act (ONE workflow call), Assert       │
│  4. Assertions use POM state-check methods (from pom_metadata)              │
│  5. @autologger("Test") decorator, @pytest.mark.<domain>                    │
│                                                                             │
│  Output:                                                                    │
│  {                                                                          │
│    "status": "success",                                                     │
│    "code": "@pytest.mark.auth\ndef test_valid_login...",                    │
│    "file_path": "tests/auth/test_valid_login.py"                            │
│  }                                                                          │
│                                                                             │
│  AI saves file and reports to user.                                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

AI PROMPTING RULES FOR TOOL 6:
┌─────────────────────────────────────────────────────────────────────────────┐
│  Before calling Tool 6, AI MUST:                                            │
│                                                                             │
│  1. TEST FILE ORGANIZATION                                                  │
│     - One file per test scenario (not one class with many methods)          │
│     - Group by domain folder: tests/auth/, tests/catalog/, etc.             │
│     - File naming: test_<scenario>.py (e.g., test_valid_login.py)           │
│     - Multiple related test functions can be in same file                   │
│                                                                             │
│  2. TEST STRUCTURE (AAA Pattern)                                            │
│     - Arrange: Create Role instance, create POM for assertions              │
│     - Act: Call ONE Role workflow method (no return value)                  │
│     - Assert: Use POM state-check methods (from pom_metadata)               │
│                                                                             │
│  3. ASSERTIONS MUST USE POM STATE METHODS                                   │
│     - Get state method names from pom_metadata.state_methods                │
│     - Example: assert login_page.is_logged_in(), "message"                  │
│     - NEVER assert on return values (Role methods return None)              │
│                                                                             │
│  4. DECORATORS AND MARKERS                                                  │
│     - @pytest.mark.<domain> (e.g., @pytest.mark.auth)                       │
│     - @pytest.mark.smoke for critical path tests                            │
│     - @autologger.automation_logger("Test")                                 │
│                                                                             │
│  5. FIXTURES                                                                │
│     - Use: web_interface, config, test_users (from conftest.py)             │
│     - Don't create new fixtures unless necessary                            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.10 Step 9: AI Saves Files and Reports

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 9: AI SAVES & REPORTS                          │
│                                                                             │
│  After all tools complete, AI:                                              │
│                                                                             │
│  1. Saves generated files (if new code was generated)                       │
│     - POM: framework/pages/<domain>/<name>_page.py                          │
│     - Task: framework/tasks/<domain>/<name>_tasks.py                        │
│     - Role: framework/roles/<domain>/<name>.py                              │
│     - Test: tests/<domain>/test_<scenario>.py                               │
│                                                                             │
│  2. Reports to user what was created/reused                                 │
│     - List of new files created                                             │
│     - List of existing files reused                                         │
│     - Command to run the test                                               │
│                                                                             │
│  3. Optionally runs the test                                                │
│     pytest tests/<domain>/test_<scenario>.py -v --headless=False            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.11 Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-01 | User must specify persona in requirement ("As a...") | Eliminates ambiguity in Role naming |
| DD-02 | URL required upfront with requirement | Enables autonomous tool chain execution |
| DD-03 | Metadata context accumulated through tool chain | Consistent pattern, no separate state files |
| DD-04 | Single documentation source (FRAMEWORK.md) | One source of truth for framework + MCP workflow |
| DD-05 | Exact method names emerge from tool chain, not upfront | Bottom-up approach - POM → Task → Role determines naming |
| DD-06 | AI extracts intent, not exact method names | Intent guides generation; actual names depend on discovered elements |
| DD-07 | Domain determined by AI in Step 2, passed through metadata | Used for folder organization (auth/, catalog/, etc.) |
| DD-08 | AI orchestrates tool chain, tools don't call other tools | AI can handle errors, inspect outputs, make decisions; tools stay simple |
| DD-09 | AI extracts expected_states from BDD "Then" clause | Ensures correct state-check methods are generated; Tool 3 can't infer business logic |
| DD-10 | Action methods derived from element types (input→enter, button→click) | Predictable, consistent naming based on UI element semantics |
| DD-11 | State method naming: is_*/has_* for bool, get_* for values | Follows common naming conventions; clear return type expectations |
| DD-12 | Check existing classes/methods before generating new | Avoid duplicates; reuse production code; CommonTasks already handles auth |
| DD-13 | Each tool has specific AI prompting rules | Ensures consistent enforcement of patterns across all tool calls |
| DD-14 | One test file per scenario, grouped by domain folder | Better modularity; clearer reports; can run by marker or file |
| DD-15 | Test assertions use POM state methods from metadata | Ensures tests assert on actual generated methods; no hardcoding |
| DD-16 | AI overrides Tool 6 file paths to project convention | Tool 6 suggests `tests/<domain>/`, AI saves to `tests/test1/`, `tests/test2/` |
| DD-17 | AI injects actual parameter values from requirement | Tool generates placeholders; AI replaces with real values from user story |
| DD-18 | AI validates import paths before saving | Prevents runtime errors from incorrect imports |
| DD-19 | Tool invocation: ALWAYS import from `tools/`, never `utils/` | Tool wrappers handle arguments correctly; utils have different signatures |
| DD-20 | Dynamic element discovery: AI prepares page state before Tool 2 | Enables discovery of modals, hover elements, AJAX content |
| DD-21 | AI-SDET collaboration for dynamic discovery (see 8.5) | Balances autonomy with efficiency; human helps when AI stuck |
| DD-22 | Stop-and-Discuss: On ANY blocker, STOP → REPORT → DISCUSS → proceed | Prevents AI from looping on fixes; ensures user collaboration on blockers |
| DD-23 | BDD format required for Tool 1 (explicit Given/When/Then) | Tool 1 parser requires explicit BDD keywords; plain English fails (see 8.16) |
| DD-24 | Test credentials: ASK user which strategy (static/dynamic/self-contained) | Three strategies for credential management; prevents hardcoding (see 8.17) |
| DD-25 | Skeleton code quality gate: STOP if any tool generates incomplete code | Prevents broken code from propagating through tool chain (see 8.18) |
| DD-26 | Tool chain data contracts: pass metadata directly between tools | Tool outputs must flow unchanged to next tool; AI enforces contracts (see 8.19) |
| DD-27 | Task code quality gate: NO locators in Tasks (CRITICAL) | Architecture violation if Tasks contain By.* locators (see 8.20) |
| DD-28 | Test data organization: ASK user shared vs workflow-specific location | Hybrid model: shared + workflow-specific data; smart loader (see 8.21) |

### 8.12 DD-16, DD-17, DD-18: AI Post-Processing Rules

Tools generate code, but AI must post-process before saving:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ AI POST-PROCESSING (after Tool 6, before saving)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ DD-16: FILE PATH OVERRIDE                                                   │
│ ─────────────────────────                                                   │
│   Tool 6 suggests: tests/catalog/test_browse_category.py                   │
│   AI overrides to: tests/test1/test_browse_category.py                     │
│                                                                             │
│ DD-17: PARAMETER VALUE INJECTION                                            │
│ ────────────────────────────────                                            │
│   Tool 6 generates: user.browse_category("category_name_value")            │
│   AI replaces with: user.browse_category("Women")  ← from requirement      │
│                                                                             │
│ DD-18: IMPORT PATH VALIDATION                                               │
│ ─────────────────────────────                                               │
│   Before saving, AI verifies:                                               │
│   - Import paths match actual file locations                                │
│   - Classes exist at specified paths                                        │
│   - No circular imports                                                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.13 DD-19: Tool Invocation Pattern

When AI calls MCP Tools (1-6), use correct imports:

```python
# CORRECT - Tool wrappers (async, take arguments dict)
from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story
from tools.tool_02_discover_page_elements import discover_elements
from tools.tool_03_generate_page_object import generate_page_object
from tools.tool_04_generate_task import generate_task
from tools.tool_05_generate_role import generate_role
from tools.tool_06_generate_test_runner import generate_test_runner

# WRONG - Utility functions (different signatures, will cause errors)
from utils.element_discovery import discover_page_elements  # NO!
from utils.generators.page_object_generator import generate_page_object  # NO!
```

**Why:** Tool wrappers handle argument parsing, validation, and return JSON. Utility functions have different signatures and will fail with confusing errors.

---

### 8.14 DD-22: Stop-and-Discuss Protocol (CRITICAL)

When ANY issue blocks progress, AI must follow this protocol:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DD-22: STOP-AND-DISCUSS PROTOCOL                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ TRIGGER: Any blocker, error, or unexpected behavior                         │
│                                                                             │
│ 1. STOP                                                                     │
│    - Do NOT attempt autonomous fixes                                        │
│    - Do NOT retry the same approach                                         │
│    - Do NOT make assumptions about the solution                             │
│                                                                             │
│ 2. REPORT                                                                   │
│    - What action was being attempted                                        │
│    - What error/unexpected behavior occurred                                │
│    - What observations might indicate the cause                             │
│    - Potential root causes (as hypotheses, not conclusions)                 │
│                                                                             │
│ 3. DISCUSS                                                                  │
│    - Present options to the user                                            │
│    - Wait for user input/direction                                          │
│    - Use AskUserQuestion tool if appropriate                                │
│                                                                             │
│ 4. PROCEED                                                                  │
│    - Only after user provides direction                                     │
│    - Document the agreed approach                                           │
│    - If fix fails, return to step 1 (STOP)                                  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ APPLIES TO:                                                                 │
│ - Test failures                                                             │
│ - Element not found errors                                                  │
│ - Unexpected page state                                                     │
│ - Build/import errors                                                       │
│ - Any deviation from expected outcome                                       │
│                                                                             │
│ ANTI-PATTERN: Looping through multiple fix attempts without consultation   │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Example - Correct Behavior:**
```
AI: "The test failed with 'Login did not redirect to account page'.

Observations:
- URL stayed at `controller=authentication` after form submission
- No error message displayed on page
- Same test works in Playwright but not Selenium

Potential causes:
1. Bot detection blocking Selenium
2. Cookie/session handling difference
3. Chrome driver configuration issue

What would you like me to investigate first?"
```

---

### 8.15 Claude Code Skills

Claude Code Skills provide on-demand workflow guidance loaded via `/skill <name>`.

**Available Skills:**

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `execute-from-step1` | Full 9-step MCP workflow with autonomous troubleshooting | Running E2E tests, validating tool chain |

**Skill: execute-from-step1**

Location: `.claude/skills/execute-from-step1.md`

Features:
- Complete 9-step workflow guide
- Autonomous troubleshooting (DD-21):
  - Iframe/frame detection and switching
  - Shadow DOM handling
  - Dynamic content waits
  - Multiple selector strategies
  - JavaScript DOM queries and event triggering
- Step-by-step DevTools guidance when AI needs user help
- Defect handling with mandatory restart-from-step-1

Usage:
```
/skill execute-from-step1
```

**Skills vs CLAUDE.md:**
- CLAUDE.md: Core rules (DD-01 through DD-28), always loaded
- Skills: Detailed procedures, loaded on-demand to save tokens

---

### 8.16 DD-23: BDD Format Required for Tool 1

Tool 1 (generate_tests_from_user_story) parses BDD scenarios using explicit keyword detection.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DD-23: BDD FORMAT REQUIREMENT                                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ Tool 1 Parser expects explicit keywords: Given, When, Then                  │
│                                                                             │
│ ✗ FAILS - Plain English:                                                    │
│ ─────────────────────────                                                   │
│   "As a registered user, I want to login with email and password            │
│    so that I can access my account"                                         │
│                                                                             │
│   Result: { "scenarios": [] }  ← Empty! No keywords found                   │
│                                                                             │
│ ✓ WORKS - Explicit BDD:                                                     │
│ ─────────────────────────                                                   │
│   "As a registered user, I want to login...                                 │
│                                                                             │
│    Given user is on the login page                                          │
│    When user enters valid email and password                                │
│    And user clicks the sign in button                                       │
│    Then user is logged in and sees account page"                            │
│                                                                             │
│   Result: { "scenarios": [{ "given": "...", "when": "...", "then": "..." }] │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ AI RULE: Convert plain English to explicit BDD in Step 2 before Tool 1      │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Keywords Parsed:**
- `Given` - Precondition/initial state
- `When` - Action performed
- `And` - Additional steps (appended to previous section)
- `Then` - Expected outcome (→ becomes state-check method)

---

### 8.17 DD-24: Test Credential Strategies

When a test requires user credentials, AI must ask which strategy to use.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DD-24: TEST CREDENTIAL STRATEGIES                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ AI PROMPT (when credentials needed):                                        │
│ ────────────────────────────────────                                        │
│   "Test requires credentials. Which approach?                               │
│    1. Static - Use pre-existing account from test_users.json                │
│    2. Dynamic - Register fresh user, save to config for later tests         │
│    3. Self-contained - Test registers and uses within same test"            │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ STRATEGY COMPARISON:                                                        │
│                                                                             │
│ ┌─────────────┬───────────────────────────────┬──────────────────────────┐  │
│ │ Strategy    │ How It Works                  │ Use When                 │  │
│ ├─────────────┼───────────────────────────────┼──────────────────────────┤  │
│ │ STATIC      │ Read from tests/data/         │ Login-only tests         │  │
│ │             │ test_users.json via fixture   │ Known account needed     │  │
│ ├─────────────┼───────────────────────────────┼──────────────────────────┤  │
│ │ DYNAMIC     │ Test registers user, saves    │ Registration → action    │  │
│ │             │ to config via utility func    │ Multi-test flows         │  │
│ ├─────────────┼───────────────────────────────┼──────────────────────────┤  │
│ │ SELF-CONT   │ Test registers and uses       │ Independent tests        │  │
│ │             │ within same test run          │ No cross-test deps       │  │
│ └─────────────┴───────────────────────────────┴──────────────────────────┘  │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ DATA FLOW BY STRATEGY:                                                      │
│                                                                             │
│ STATIC:                                                                     │
│   tests/data/test_users.json ──► conftest.py fixture ──► test              │
│                                                                             │
│ DYNAMIC:                                                                    │
│   test registers ──► utility func ──► test_users.json ──► later tests      │
│                                                                             │
│ SELF-CONTAINED:                                                             │
│   test registers ──► same test uses credentials ──► test ends (no save)    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│ RULES:                                                                      │
│ - ASK at Step 1 (User Input) when credentials are involved                  │
│ - NEVER modify conftest.py for credential saving                            │
│ - Static credentials use existing test_users fixture                        │
│ - Dynamic credentials use utility function to write to test_users.json      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 8.18 DD-25: Skeleton Code Quality Gate

After ANY MCP tool generates code (Tools 3-6), AI MUST verify completeness.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DD-25: SKELETON CODE QUALITY GATE (HARD STOP)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ SKELETON CODE INDICATORS (ANY = FAIL):                                      │
│ ──────────────────────────────────────                                      │
│   ✗ Empty sections with `pass` or `# Add ... as needed`                     │
│   ✗ Missing locators in POMs                                                │
│   ✗ Missing atomic methods in POMs                                          │
│   ✗ Missing workflow methods in Tasks/Roles                                 │
│   ✗ Placeholder comments instead of actual code                             │
│   ✗ Empty method bodies                                                     │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ QUALITY CHECKLIST BY MODULE:                                                │
│                                                                             │
│ ┌────────────┬──────────────────────────────────────────────────────────┐   │
│ │ Module     │ Required Components                                      │   │
│ ├────────────┼──────────────────────────────────────────────────────────┤   │
│ │ POM        │ Locators as class constants                              │   │
│ │ (Tool 3)   │ Atomic methods (return self)                             │   │
│ │            │ State-check methods (return bool/value)                  │   │
│ ├────────────┼──────────────────────────────────────────────────────────┤   │
│ │ Task       │ Constructor with POM composition                         │   │
│ │ (Tool 4)   │ @autologger decorated methods                            │   │
│ │            │ NO return values, NO locators                            │   │
│ ├────────────┼──────────────────────────────────────────────────────────┤   │
│ │ Role       │ Constructor with Task composition                        │   │
│ │ (Tool 5)   │ @autologger decorated workflow methods                   │   │
│ │            │ NO return values                                         │   │
│ ├────────────┼──────────────────────────────────────────────────────────┤   │
│ │ Test       │ Fixtures (web_interface, config, test_users)             │   │
│ │ (Tool 6)   │ AAA pattern (Arrange, Act, Assert)                       │   │
│ │            │ POM state assertions, proper imports                     │   │
│ └────────────┴──────────────────────────────────────────────────────────┘   │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ WHEN SKELETON CODE DETECTED:                                                │
│ ────────────────────────────                                                │
│                                                                             │
│   Tool output ──► AI checks quality ──► SKELETON DETECTED                   │
│                                              │                              │
│                                              ▼                              │
│                            ┌─────────────────────────────────┐              │
│                            │ 1. STOP - Do not proceed        │              │
│                            │ 2. REPORT - Which tool failed   │              │
│                            │ 3. FIX - AI completes OR tool   │              │
│                            │ 4. VERIFY - Check completeness  │              │
│                            │ 5. RESTART - From Step 1        │              │
│                            └─────────────────────────────────┘              │
│                                                                             │
│ This is a HARD QUALITY GATE. Incomplete code MUST NOT propagate.            │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Example Skeleton Code (FAIL):**
```python
# BAD - Tool 4 generated skeleton task
class AuthTasks:
    def __init__(self, web, base_url):
        self.web = web
        self.base_url = base_url
        # Add page compositions as needed  ← SKELETON INDICATOR
        pass  ← SKELETON INDICATOR

    @autologger.automation_logger("Task")
    def log_in(self, email, password):
        # Add login implementation  ← SKELETON INDICATOR
        pass  ← SKELETON INDICATOR
```

---

### 8.19 DD-26: Tool Chain Data Contracts

Tool outputs MUST flow to next tool unchanged. AI enforces contracts.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DD-26: TOOL CHAIN DATA CONTRACTS                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ DATA FLOW BETWEEN TOOLS:                                                    │
│                                                                             │
│  Tool 1 ──► Tool 2 ──► Tool 3 ──► Tool 4 ──► Tool 5 ──► Tool 6              │
│    │          │          │          │          │          │                 │
│    ▼          ▼          ▼          ▼          ▼          ▼                 │
│  scenarios  elements   pom_meta   task_meta  role_meta   test               │
│                                                                             │
│ EACH TOOL OUTPUT BECOMES NEXT TOOL INPUT                                    │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ CONTRACT: Tool 3 → Tool 4                                                   │
│ ─────────────────────────                                                   │
│                                                                             │
│ Tool 3 outputs pom_metadata:                                                │
│ {                                                                           │
│   "class_name": "LoginPage",                                                │
│   "import_path": "pages.auth.login_page",                                   │
│   "action_methods": [                                                       │
│     { "name": "enter_email", "params": ["email: str"] },                    │
│     { "name": "enter_password", "params": ["password: str"] },              │
│     { "name": "click_submit", "params": [] }                                │
│   ],                                                                        │
│   "state_methods": [                                                        │
│     { "name": "is_logged_in", "returns": "bool" }                           │
│   ]                                                                         │
│ }                                                                           │
│                                                                             │
│ Tool 4 MUST receive this EXACTLY to generate correct Task code:             │
│ - Task composes LoginPage                                                   │
│ - Task methods call enter_email(), enter_password(), click_submit()         │
│ - Task DOES NOT hardcode method names                                       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ AI ENFORCEMENT:                                                             │
│ ───────────────                                                             │
│                                                                             │
│  ┌──────────┐    pom_metadata    ┌──────────┐                               │
│  │ Tool 3   │ ───────────────►  │ AI       │                                │
│  └──────────┘                    │ (stores) │                                │
│                                  └────┬─────┘                                │
│                                       │                                      │
│                    pom_metadata       │                                      │
│                    (unchanged)        ▼                                      │
│                                  ┌──────────┐                                │
│                                  │ Tool 4   │                                │
│                                  └──────────┘                                │
│                                                                             │
│ AI stores metadata in context, passes DIRECTLY to next tool.                │
│ AI does NOT modify, transform, or "interpret" metadata between tools.       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ANTI-PATTERN:                                                               │
│ ─────────────                                                               │
│   Tool 3 outputs: { "action_methods": [...] }                               │
│   AI "forgets" to pass it                                                   │
│   Tool 4 receives: {} ← Empty!                                              │
│   Tool 4 generates: skeleton code with pass statements                      │
│                                                                             │
│ DEFECT: DEF-B09 - Skeleton tasks from missing pom_metadata                  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 8.20 DD-27: Task Code Quality Gate (No Locators)

Tasks MUST NOT contain locators. This is a CRITICAL architecture violation.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DD-27: TASK CODE QUALITY GATE - NO LOCATORS (CRITICAL)                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ ARCHITECTURE RULE: Locators ONLY in Page Objects                            │
│                                                                             │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ Layer           │ Locators? │ Why                                       │ │
│ ├─────────────────┼───────────┼───────────────────────────────────────────┤ │
│ │ Page Object     │ ✓ YES     │ Owns UI element definitions               │ │
│ │ Task            │ ✗ NO      │ Orchestrates POMs, not UI elements        │ │
│ │ Role            │ ✗ NO      │ Orchestrates Tasks, higher abstraction    │ │
│ │ Test            │ ✗ NO      │ Asserts via POM methods                   │ │
│ └─────────────────┴───────────┴───────────────────────────────────────────┘ │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ VIOLATION INDICATORS:                                                       │
│ ─────────────────────                                                       │
│                                                                             │
│ ✗ VIOLATION - Locators in Task:                                             │
│   from selenium.webdriver.common.by import By  ← VIOLATION                  │
│                                                                             │
│   class AuthTasks:                                                          │
│       EMAIL_INPUT = (By.ID, "email")  ← VIOLATION                           │
│       PASSWORD = (By.ID, "passwd")    ← VIOLATION                           │
│                                                                             │
│       def log_in(self, email, password):                                    │
│           self.web.type_text(*self.EMAIL_INPUT, email)  ← VIOLATION         │
│                                                                             │
│ ✓ CORRECT - Task uses POM methods:                                          │
│   class AuthTasks:                                                          │
│       def __init__(self, web, base_url):                                    │
│           self.login_page = LoginPage(web)  ← Compose POM                   │
│                                                                             │
│       def log_in(self, email, password):                                    │
│           (self.login_page                                                  │
│               .enter_email(email)  ← Call POM method                        │
│               .enter_password(password)                                     │
│               .click_submit())                                              │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ DETECTION CHECKLIST:                                                        │
│ ────────────────────                                                        │
│                                                                             │
│ Scan Task code for these patterns:                                          │
│ [ ] "from selenium.webdriver.common.by import By"                           │
│ [ ] "By.ID", "By.CSS_SELECTOR", "By.XPATH", etc.                            │
│ [ ] Tuple locator patterns: (By.*, "...")                                   │
│ [ ] Direct self.web.click/type_text with locators                           │
│                                                                             │
│ If ANY found → CRITICAL VIOLATION → STOP → FIX → RESTART FROM STEP 1        │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ DEFECT REFERENCE: DEF-B10 - AI manual Task code included locators           │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

### 8.21 DD-28: Test Data Organization

Test data can be shared or workflow-specific. AI must ask which strategy.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ DD-28: TEST DATA ORGANIZATION (HYBRID MODEL)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ AI PROMPT (when test data needed):                                          │
│ ──────────────────────────────────                                          │
│   "Test requires test data. Where should it live?                           │
│    1. Shared - tests/data/ (credentials, cross-workflow data)               │
│    2. Workflow-specific - tests/{workflow}/data/ (isolated test data)       │
│    3. Both - shared credentials + workflow-specific test cases"             │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ HYBRID DATA MODEL STRUCTURE:                                                │
│ ────────────────────────────                                                │
│                                                                             │
│   tests/                                                                    │
│   ├── data/                      ← SHARED (cross-workflow)                  │
│   │   └── test_users.json        ← Credentials for auth, cart, checkout    │
│   │                                                                         │
│   ├── auth/                                                                 │
│   │   ├── data/                  ← WORKFLOW-SPECIFIC                        │
│   │   │   └── invalid_logins.json ← Auth-specific test cases               │
│   │   ├── test_registration.py                                              │
│   │   └── test_login.py                                                     │
│   │                                                                         │
│   ├── catalog/                                                              │
│   │   ├── data/                  ← WORKFLOW-SPECIFIC                        │
│   │   │   └── products.json      ← Catalog-specific product data           │
│   │   └── test_browse.py                                                    │
│   │                                                                         │
│   ├── cart/                                                                 │
│   │   ├── data/                  ← WORKFLOW-SPECIFIC                        │
│   │   │   └── cart_items.json    ← Cart-specific item combinations         │
│   │   └── test_add_to_cart.py                                               │
│   │                                                                         │
│   └── conftest.py                ← Smart data loader (workflow→shared)      │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ DATA TYPE → LOCATION MAPPING:                                               │
│                                                                             │
│ ┌─────────────────────┬──────────────────────────┬─────────────────────────┐│
│ │ Data Type           │ Location                 │ Example                 ││
│ ├─────────────────────┼──────────────────────────┼─────────────────────────┤│
│ │ Credentials         │ tests/data/              │ User accounts           ││
│ │ Cross-workflow      │ tests/data/              │ Shared config           ││
│ │ Workflow-specific   │ tests/{workflow}/data/   │ Invalid logins          ││
│ │ Documents/files     │ tests/{workflow}/input/  │ Upload test files       ││
│ └─────────────────────┴──────────────────────────┴─────────────────────────┘│
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ SMART DATA LOADER (conftest.py):                                            │
│ ────────────────────────────────                                            │
│                                                                             │
│   @pytest.fixture                                                           │
│   def test_data(request):                                                   │
│       """Load test data: workflow-specific first, shared fallback."""       │
│       test_dir = Path(request.fspath).parent                                │
│       workflow_data = test_dir / "data"                                     │
│       shared_data = Path(__file__).parent / "data"                          │
│                                                                             │
│       # Try workflow-specific first                                         │
│       if (workflow_data / "test_data.json").exists():                       │
│           return load_json(workflow_data / "test_data.json")                │
│                                                                             │
│       # Fallback to shared                                                  │
│       return load_json(shared_data / "test_data.json")                      │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│ RULES:                                                                      │
│ ──────                                                                      │
│ - ASK at Step 1 (User Input) when test data is involved                     │
│ - Shared credentials → tests/data/test_users.json                           │
│ - Workflow-isolated data → tests/{workflow}/data/                           │
│ - conftest.py provides smart loader with fallback logic                     │
│                                                                             │
│ IMPLEMENTATION NOTE:                                                        │
│ Per-step skills are being created to enforce tool chain contracts.          │
│ DD-28 implementation will be integrated into the appropriate step skill     │
│ (likely Step 1 or Step 9) once DDs are ported to dedicated skills.          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. 10-Step Workflow with Quality Gates (v2)

> **Note:** This section documents the updated workflow with explicit quality gates. Section 8 is preserved for reference during transition.

### Overview

The v2 workflow adds:
- Step 1: Pre-flight Configuration (new)
- Explicit quality gates at each step
- Gate enforcement: Cannot proceed until checks pass
- Four-layer architecture: Skill → Gates → Operations → State

> **Template Reference:** See `.claude/skills/design-execution-engine/SKILL.md` for the complete step template that applies to all verticals.

### Four-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ SKILL (guidance-layer)                                               │
│ - Guides AI through workflow                                         │
│ - .claude/skills/qa-guidance-layer/                                  │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ QUALITY GATES (qg_*)                                                 │
│ - Validates input/output at each step                               │
│ - mcp_server/tools/gates/                                           │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ OPERATION TOOLS                                                      │
│ - Does the actual work                                               │
│ - mcp_server/tools/operations/                                       │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STATE MANAGER                                                        │
│ - Persists workflow state after each step                           │
│ - mcp_server/utils/state_manager.py                                 │
└─────────────────────────────────────────────────────────────────────┘
```

### File Structure

```
mcp_server/
├── tools/
│   ├── operations/          ← Do the work
│   │   ├── generate_tests_from_user_story.py
│   │   ├── discover_page_elements.py
│   │   └── ...
│   │
│   └── gates/               ← Validate only (qg_* prefix)
│       ├── qg_preflight.py
│       ├── qg_user_input.py
│       └── ...
│
├── state/                   ← Workflow state persistence
│   └── workflow_state.json
│
└── utils/
    └── state_manager.py     ← Save/load state logic
```

### State Save Rules

| Step Type | Who Saves State |
|-----------|-----------------|
| Steps 1-3 (no operation tool) | Quality gate saves on PASS |
| Steps 4-9 (has operation tool) | Operation tool saves on SUCCESS |
| AI | NEVER calls state_manager directly |

### Tool Mapping

```
Step │ Operation Tool                  │ Quality Gate Tool
─────┼─────────────────────────────────┼─────────────────────────────
  1  │ -                               │ qg_preflight
  2  │ -                               │ qg_user_input
  3  │ -                               │ qg_ai_processing
  4  │ generate_tests_from_user_story  │ qg_test_scenarios
  5  │ discover_page_elements          │ qg_discovered_elements
  6  │ generate_page_object            │ qg_page_object
  7  │ generate_task                   │ qg_task
  8  │ generate_role                   │ qg_role
  9  │ generate_test_runner            │ qg_test_runner
 10  │ -                               │ qg_save_run
```

### Workflow Per Step

```
AI prepares → qg_* validates input → Operation executes → qg_* validates output → Next step
```

### Step Template

> **Complete Template:** See `.claude/skills/design-execution-engine/SKILL.md` for the full 7-section template.

Each step definition must include these sections:

| Section | Contents |
|---------|----------|
| **A. Identity & Flow** | Step, Dependencies, Input, Output |
| **B. Persona Map** | User Actions, AI Actions, Tool Actions |
| **C. Skill Instruction** | PRE-CHECK, ACTION, VALIDATE, RETRY |
| **D. Tools** | Operation Tool, Quality Gate, Gate Mode |
| **E. State Management** | State Saved, Who Saves, When Saved, State Schema |
| **F. Enforcement** | Rules That Apply, Validation Checks, Gate Enforcement |
| **G. Error Handling** | Failure Behavior, Error Message Templates, Known Defects |

**Skill Reference:** Each step has a corresponding file in `.claude/skills/qa-guidance-layer/references/step-NN.md`

---

### Tool Failure Handling Flow (CRITICAL)

This flow applies to ALL tool steps (Steps 4-9). When any tool validation fails:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MCP TOOL FAILURE HANDLING                         │
└─────────────────────────────────────────────────────────────────────┘

  AI calls MCP Tool
      │
      ▼
┌─────────────────┐
│ Tool validates  │
│ input           │
└─────────────────┘
      │
      ├── PASS ──► Tool executes ──► SUCCESS ──► Next step
      │
      └── FAIL ──► Tool returns error:
                   {
                     "status": "error",
                     "error_type": "[what failed]",
                     "message": "[description]",
                     "fix_hint": "[how to fix]",
                     "example": "[correct format]"
                   }
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ AI RECEIVES ERROR                                                    │
│                                                                      │
│ AI does NOT retry automatically                                      │
│ AI does NOT guess/assume                                             │
│                                                                      │
│ AI MUST:                                                             │
│ 1. STOP execution                                                    │
│ 2. REPORT to user (show error + hint)                                │
│ 3. ASK user for missing info                                         │
│ 4. WAIT for user response                                            │
│ 5. RETRY tool with corrected input                                   │
└─────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│ AI TO USER:                                                          │
│                                                                      │
│ "Tool validation failed:                                             │
│  - Missing: [field]                                                  │
│  - Fix: [hint]                                                       │
│  - Example: [example]                                                │
│                                                                      │
│  Please provide [what's needed]."                                    │
└─────────────────────────────────────────────────────────────────────┘
                         │
                         ▼
              User provides info
                         │
                         ▼
              AI retries tool with corrected input
                         │
                         ▼
              Loop until SUCCESS or USER CANCELS
```

**Key Principle: Tool Errors = User Collaboration (DD-22)**

```
┌─────────────────────────────────────────────────────────────────────┐
│  NEVER: AI guesses, assumes, or auto-fixes validation errors        │
│  ALWAYS: AI stops, reports, asks user, waits                        │
└─────────────────────────────────────────────────────────────────────┘
```

---

### 9.1 Step 1: Pre-flight Configuration

| Aspect | Details |
|--------|---------|
| **Step** | 1 - Pre-flight Configuration |
| **Skill Reference** | `qa-guidance-layer/references/step-01.md` |
| **Operation Tool** | - (none, AI asks user) |
| **Quality Gate** | `qg_preflight` |
| **Input** | None (first step) |
| **Output** | `credential_strategy`, `test_data_location` |
| **State Saved** | `{ step: 1, status: "complete", credential_strategy, test_data_location }` |
| **Dependencies** | None |
| **Who Executes** | AI asks → User answers → Gate validates |
| **DDs That Apply** | DD-24 (credential strategy), DD-28 (test data location) |

#### Visual Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 1: PRE-FLIGHT                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SKILL INSTRUCTION                                                           │
│                                                                              │
│  PRE-CHECK:                                                                  │
│  - None (first step)                                                        │
│                                                                              │
│  ACTION:                                                                     │
│  - ASK user Question 1 (DD-24: credential strategy)                         │
│  - WAIT for answer                                                          │
│  - ASK user Question 2 (DD-28: test data location)                          │
│  - WAIT for answer                                                          │
│                                                                              │
│  VALIDATE:                                                                   │
│  - Call qg_preflight with both answers                                      │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI ASKS USER                                                                │
│                                                                              │
│  Question 1 (DD-24):                                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ "Which credential approach for this test?"                             │ │
│  │  1. Static        - Use existing account from test_users.json          │ │
│  │  2. Dynamic       - Register fresh user, save for later tests          │ │
│  │  3. Self-contained - Register and use within same test                 │ │
│  │  4. None needed   - Test doesn't require credentials                   │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  Question 2 (DD-28):                                                         │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ "Where should test data live?"                                         │ │
│  │  1. Shared            - tests/data/ (cross-workflow)                   │ │
│  │  2. Workflow-specific - tests/{workflow}/data/                         │ │
│  │  3. Both              - Shared credentials + workflow-specific data    │ │
│  │  4. None needed       - Test doesn't require external data             │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_preflight                                                  │
│                                                                              │
│  Validates:                                                                  │
│  ┌──────────────────────────┬──────────────────────────────────────────────┐│
│  │ Field                    │ Valid Values                                 ││
│  ├──────────────────────────┼──────────────────────────────────────────────┤│
│  │ credential_strategy      │ static | dynamic | self-contained | none    ││
│  │ test_data_location       │ shared | workflow | both | none             ││
│  └──────────────────────────┴──────────────────────────────────────────────┘│
│                                                                              │
│  Gate Enforcement: BLOCKED until both fields valid                          │
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
              │  STATE SAVED        │  │  RE-ASK USER        │
              │                     │  │                     │
              │  {                  │  │  Show which field   │
              │    step: 1,         │  │  is missing/invalid │
              │    credential_      │  │                     │
              │      strategy: "x", │  │  Provide valid      │
              │    test_data_       │  │  options again      │
              │      location: "y"  │  │                     │
              │  }                  │  │                     │
              └─────────────────────┘  └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 2  │
              └─────────────────────┘
```

#### Quality Gate

| Check | Rule |
|-------|------|
| Credential strategy answered | Must be one of: Static / Dynamic / Self-contained / None needed |
| Test data location answered | Must be one of: Shared / Workflow-specific / Both / None needed |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 2 until both answers provided** |

#### Known Defects

None - this is a new step.

#### Failure Behavior

| Issue | Behavior |
|-------|----------|
| User skips question | RE-ASK with clarification |
| Invalid answer | RE-ASK with valid options |

#### Error Message Templates

```
Credential strategy:
"Which credential approach for this test?
1. Static - Use existing account from test_users.json
2. Dynamic - Register fresh user, save for later tests
3. Self-contained - Register and use within same test
4. None needed - Test doesn't require credentials"

Test data location:
"Where should test data live?
1. Shared - tests/data/ (cross-workflow)
2. Workflow-specific - tests/{workflow}/data/
3. Both - shared credentials + workflow-specific data
4. None needed - Test doesn't require external data"
```

#### Enforcement Location

TBD (decide after all steps analyzed)

---

### 9.2 Step 2: User Input

| Aspect | Details |
|--------|---------|
| **Step** | 2 - User Input |
| **Skill Reference** | `qa-guidance-layer/references/step-02.md` |
| **Operation Tool** | - (none, AI extracts from user input) |
| **Quality Gate** | `qg_user_input` |
| **Input** | User's natural language requirement |
| **Output** | Validated: `persona`, `URL`, `role_name`, `domain` |
| **State Saved** | `{ step: 2, status: "complete", persona, URL, role_name, domain }` |
| **Dependencies** | Step 1 complete (credential_strategy, test_data_location) |
| **Who Executes** | User provides → AI extracts → Gate validates |
| **DDs That Apply** | DD-01 (persona required), DD-02 (URL required) |

#### Visual Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 2: USER INPUT                                   │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SKILL INSTRUCTION                                                           │
│                                                                              │
│  PRE-CHECK:                                                                  │
│  - Verify Step 1 complete (credential_strategy, test_data_location exist)   │
│                                                                              │
│  ACTION:                                                                     │
│  - IF user hasn't provided requirement: ASK for it                          │
│    "What test do you want to create?                                        │
│     Format: 'As a [role], I want to [action]...'                            │
│     URL: [target page]"                                                     │
│  - IF user provided requirement: EXTRACT persona, URL, role_name, domain    │
│                                                                              │
│  VALIDATE:                                                                   │
│  - Call qg_user_input with extracted fields                                 │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  RECEIVE USER REQUIREMENT                                                    │
│                                                                              │
│  Expected format:                                                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ "As a [persona], I want to [action]..."                                │ │
│  │ URL: [target page URL]                                                 │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI EXTRACTS                                                                 │
│                                                                              │
│  ┌──────────────────────────┬──────────────────────────────────────────────┐│
│  │ Field                    │ Extracted From                               ││
│  ├──────────────────────────┼──────────────────────────────────────────────┤│
│  │ persona                  │ "As a [X]" → "registered user"              ││
│  │ URL                      │ Provided URL                                 ││
│  │ role_name                │ Derived → "RegisteredUser"                   ││
│  │ domain                   │ Inferred from intent → "authentication"      ││
│  └──────────────────────────┴──────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_user_input                                                 │
│                                                                              │
│  Validates:                                                                  │
│  ┌──────────────────────────┬──────────────────────────────────────────────┐│
│  │ Check                    │ Rule                                         ││
│  ├──────────────────────────┼──────────────────────────────────────────────┤│
│  │ persona                  │ Must be present (DD-01)                      ││
│  │ URL                      │ Must be valid URL (DD-02)                    ││
│  │ role_name                │ Must be derivable from persona               ││
│  │ domain                   │ Must be determinable from intent             ││
│  └──────────────────────────┴──────────────────────────────────────────────┘│
│                                                                              │
│  Gate Enforcement: BLOCKED until all fields valid                           │
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
              │                     │  │                     │
              │  {                  │  │  Show what's        │
              │    step: 2,         │  │  missing with       │
              │    persona,         │  │  example format     │
              │    URL,             │  │                     │
              │    role_name,       │  │                     │
              │    domain           │  │                     │
              │  }                  │  │                     │
              └─────────────────────┘  └─────────────────────┘
                         │
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 3  │
              └─────────────────────┘
```

**Example Input:**
```
"As a registered user, I want to login with email and password"
URL: http://automationpractice.pl/index.php?controller=authentication
```

**Example Output:**
```
persona: "registered user"
URL: "http://automationpractice.pl/index.php?controller=authentication"
role_name: "RegisteredUser"
domain: "authentication"
```

#### Quality Gate

| Check | Rule |
|-------|------|
| Persona present | Must contain "As a [role]..." |
| URL present | Must have target page URL |
| Role extractable | AI can determine role from persona |
| Domain determinable | AI can determine domain from intent |
| Requirement specific | Clear enough to create BDD in Step 3 |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 3 until all checks pass** |

#### Known Defects

| Defect | Issue |
|--------|-------|
| Enforcement gap | AI sometimes forgets to ask for missing info |

#### Failure Behavior

| Issue | Behavior |
|-------|----------|
| Persona missing | ASK USER: "Please specify persona. Example: 'As a customer, I want to...'" |
| URL missing | ASK USER: "Which page? Example: 'http://yoursite.com/login'" |
| Cannot determine role | ASK USER: "What type of user? Example: 'customer', 'admin', 'visitor'" |
| Cannot determine domain | ASK USER: "What workflow area? Example: 'authentication', 'product browsing', 'checkout'" |
| Requirement vague | ASK USER: "Please be more specific. Example: 'I want to add a blue t-shirt size M to cart'" |

#### Enforcement Location

TBD

---

### 9.3 Step 3: AI Processing

| Aspect | Details |
|--------|---------|
| **Step** | 3 - AI Processing |
| **Skill Reference** | `qa-guidance-layer/references/step-03.md` |
| **Operation Tool** | - (none, AI processes) |
| **Quality Gate** | `qg_ai_processing` |
| **Input** | Step 2 output: `persona`, `URL`, `role_name`, `domain` + original requirement |
| **Output** | `metadata_context`: `bdd_scenarios`, `expected_states`, `intent` |
| **State Saved** | `{ step: 3, bdd_scenarios, expected_states, intent }` |
| **Dependencies** | Step 2 complete (validated inputs) |
| **Who Executes** | AI creates → Gate validates |
| **DDs That Apply** | DD-03 (metadata context), DD-09 (expected_states from "Then" clause) |

#### Visual Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         STEP 3: AI PROCESSING                                │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SKILL INSTRUCTION                                                           │
│                                                                              │
│  PRE-CHECK:                                                                  │
│  - Verify Step 2 complete (persona, URL, role_name, domain exist)           │
│                                                                              │
│  ACTION:                                                                     │
│  - CREATE BDD scenario from requirement (Given/When/Then)                   │
│  - EXTRACT expected_states from "Then" clause (DD-09)                       │
│  - DETERMINE intent (action verb from requirement)                          │
│                                                                              │
│  VALIDATE:                                                                   │
│  - Call qg_ai_processing with metadata                                      │
│                                                                              │
│  RETRY (if validation fails):                                               │
│  - Max 3 attempts                                                           │
│  - After 3: STOP → REPORT → USER DECIDES                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  AI CREATES METADATA                                                         │
│                                                                              │
│  From requirement: "As a registered user, I want to login..."               │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ BDD Scenario:                                                          │ │
│  │   Given I am on the login page                                        │ │
│  │   When I enter valid email and password                               │ │
│  │   And I click the login button                                        │ │
│  │   Then I should see my account dashboard                              │ │
│  │   And I should see a logout link                                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────────┬──────────────────────────────────────────────┐│
│  │ Field                    │ Extracted Value                              ││
│  ├──────────────────────────┼──────────────────────────────────────────────┤│
│  │ expected_states          │ ["is_on_dashboard", "is_logout_visible"]    ││
│  │ intent                   │ "login"                                      ││
│  └──────────────────────────┴──────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_ai_processing                                              │
│                                                                              │
│  Validates:                                                                  │
│  ┌──────────────────────────┬──────────────────────────────────────────────┐│
│  │ Check                    │ Rule                                         ││
│  ├──────────────────────────┼──────────────────────────────────────────────┤│
│  │ bdd_scenarios            │ Must have valid Given/When/Then structure   ││
│  │ expected_states          │ At least one state from "Then" clause       ││
│  │ intent                   │ Action verb extracted from requirement       ││
│  └──────────────────────────┴──────────────────────────────────────────────┘│
│                                                                              │
│  Gate Enforcement: BLOCKED until all fields valid                           │
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
              │                     │  │                     │
              │  {                  │  │  After 3 failures:  │
              │    step: 3,         │  │  STOP → REPORT →    │
              │    bdd_scenarios,   │  │  USER DECIDES       │
              │    expected_states, │  │                     │
              │    intent           │  │  Options:           │
              │  }                  │  │  1. Go to Step 2    │
              └─────────────────────┘  │  2. Abort workflow  │
                         │             └─────────────────────┘
                         ▼
              ┌─────────────────────┐
              │  PROCEED TO STEP 4  │
              └─────────────────────┘
```

#### Quality Gate

| Check | Rule |
|-------|------|
| BDD created | Must have valid given/when/then structure |
| expected_states extracted | At least one state from "then" clause |
| intent determined | Action verb extracted from requirement |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 4 until metadata complete** |

#### Failure Behavior (Universal Retry Policy)

**Retry Limit:** 3 attempts

| Attempt | Behavior |
|---------|----------|
| 1-3 | Tool rejects → AI retries processing |
| After 3 | STOP → REPORT → USER DECIDES |

**Resolution Options (Step 3):**

```
"I've attempted 3 times and cannot produce valid metadata.

Here's what I'm generating:
[show failing output]

Tool rejection reason:
[show error from tool]

How should we proceed?
1. Clarify requirement - Go back to Step 2
2. Abort workflow - Stop and log issue internally"
```

**Note:** No "proceed with incomplete" option. Incomplete data never propagates.

---

### 9.4 Step 4: Tool 1 - generate_tests_from_user_story

| Aspect | Details |
|--------|---------|
| **Step** | 4 - Tool 1 |
| **Skill Reference** | `qa-guidance-layer/references/step-04.md` |
| **Operation Tool** | `generate_tests_from_user_story` |
| **Quality Gate** | `qg_test_scenarios` (pre + post validation) |
| **Input** | `metadata_context` from Step 3 |
| **Output** | `test_scenarios`: array of given/when/then objects |
| **State Saved** | `{ step: 4, test_scenarios }` |
| **Dependencies** | Step 3 complete (valid metadata) |
| **Who Executes** | AI prepares → Tool validates + generates |
| **DDs That Apply** | DD-23 (BDD format required) |

#### Visual Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STEP 4: TOOL 1 - GENERATE TESTS                           │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SKILL INSTRUCTION                                                           │
│                                                                              │
│  PRE-CHECK:                                                                  │
│  - Verify Step 3 complete (bdd_scenarios, expected_states, intent exist)    │
│                                                                              │
│  ACTION:                                                                     │
│  - PREPARE input: user_story, workflow                                      │
│  - CALL qg_test_scenarios (pre-validate input)                              │
│  - CALL generate_tests_from_user_story (operation)                          │
│  - CALL qg_test_scenarios (post-validate output)                            │
│                                                                              │
│  RETRY (if validation fails):                                               │
│  - Max 3 attempts (AI fixes, NOT user)                                      │
│  - After 3: STOP → REPORT → USER DECIDES                                    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_test_scenarios (PRE-VALIDATE)                              │
│                                                                              │
│  Validates input before operation:                                          │
│  ┌──────────────────────────┬──────────────────────────────────────────────┐│
│  │ Check                    │ Rule                                         ││
│  ├──────────────────────────┼──────────────────────────────────────────────┤│
│  │ bdd_scenarios            │ Present + valid Given/When/Then              ││
│  │ expected_states          │ Present + at least one state                 ││
│  │ workflow                 │ One of: auth, catalog, cart, checkout       ││
│  └──────────────────────────┴──────────────────────────────────────────────┘│
│                                                                              │
│  PASS → Continue to operation | FAIL → Retry (max 3)                        │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  OPERATION: generate_tests_from_user_story                                   │
│                                                                              │
│  Generates test_scenarios array:                                            │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │ test_scenarios: [                                                      │ │
│  │   { "name": "test_X", "given": "...", "when": [...], "then": [...] }  │ │
│  │ ]                                                                      │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  QUALITY GATE: qg_test_scenarios (POST-VALIDATE)                             │
│                                                                              │
│  Validates output after operation:                                          │
│  ┌──────────────────────────┬──────────────────────────────────────────────┐│
│  │ Check                    │ Rule                                         ││
│  ├──────────────────────────┼──────────────────────────────────────────────┤│
│  │ test_scenarios           │ Present + at least one scenario              ││
│  │ Each scenario            │ Has name, given, when, then                  ││
│  └──────────────────────────┴──────────────────────────────────────────────┘│
│                                                                              │
│  PASS → State saved | FAIL → Retry (max 3), then USER DECIDES               │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
              ┌─────────────────────────────────────────────┐
              │  STATE SAVED → PROCEED TO STEP 5            │
              │  { step: 4, test_scenarios }                │
              └─────────────────────────────────────────────┘
```

#### Quality Gate

| Check | Rule |
|-------|------|
| `bdd_scenarios` | Present + valid given/when/then structure |
| `expected_states` | Present + array with at least one state string |
| `intent` | Present + valid action verb (non-empty) |
| `role_name` | Present + non-empty string |
| `domain` | Present + non-empty string |
| `workflow` | Present + recognized workflow type |
| Output scenarios | At least one valid scenario object generated |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 5 until all checks pass** |

#### Failure Behavior

**Retry Limit:** 3 attempts

| Rejection | Behavior |
|-----------|----------|
| Invalid metadata | AI retries Step 3 processing (not user) |
| After 3 retries | STOP → REPORT → USER DECIDES |

**Resolution Options (Step 4):**
1. Clarify requirement - Go back to Step 2
2. Abort workflow - Stop and log issue internally

**Note:** Tool rejection = AI's problem. User only involved after retries exhausted.

---

### 9.5 Step 5: Discover Elements (Tool 2)

> **Full Details:** `.claude/skills/qa-guidance-layer/references/step-05.md`

| Field | Value |
|-------|-------|
| **Operation Tool** | `discover_page_elements` |
| **Quality Gate** | `qg_discovered_elements` |
| **Gate Mode** | PRE+POST |
| **Who Saves** | Operation tool |
| **Key Rules** | DD-20 (dynamic element prep), DD-24 (credential strategy) |

**Credential Handling:**
- Reads `credential_strategy` from Step 1
- If not "none": AI logs in before discovering elements
- Prepares page state to reveal dynamic elements

---

### 9.6 Step 6: Generate POM (Tool 3)

> **Full Details:** `.claude/skills/qa-guidance-layer/references/step-06.md`

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_page_object` |
| **Quality Gate** | `qg_page_object` |
| **Gate Mode** | PRE+POST |
| **Who Saves** | Operation tool |
| **Key Rules** | DD-25 (no skeleton code), DD-09 (state methods from expected_states) |

**DD-25 Enforcement:**
- No empty methods with `pass`
- All locators as class constants
- State-check methods for each expected_state

---

### 9.7 Step 7: Generate Task (Tool 4)

> **Full Details:** `.claude/skills/qa-guidance-layer/references/step-07.md`

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_task` |
| **Quality Gate** | `qg_task` |
| **Gate Mode** | PRE+POST |
| **Who Saves** | Operation tool |
| **Key Rules** | DD-12 (check existing), DD-25 (no skeleton), NO return values |

**DD-12 Enforcement:**
- Check if Task class already exists for domain
- If exists: Extend with new methods
- If not exists: Generate new class

---

### 9.8 Step 8: Generate Role (Tool 5)

> **Full Details:** `.claude/skills/qa-guidance-layer/references/step-08.md`

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_role` |
| **Quality Gate** | `qg_role` |
| **Gate Mode** | PRE+POST |
| **Who Saves** | Operation tool |
| **Key Rules** | DD-12 (check existing), DD-25 (no skeleton), NO return values, orchestrates MULTIPLE tasks |

**Role vs Task:**
- Task = single domain operation
- Role = complete workflow (calls MULTIPLE task methods)

---

### 9.9 Step 9: Generate Test Runner (Tool 6)

> **Full Details:** `.claude/skills/qa-guidance-layer/references/step-09.md`

| Field | Value |
|-------|-------|
| **Operation Tool** | `generate_test_runner` |
| **Quality Gate** | `qg_test_runner` |
| **Gate Mode** | PRE+POST |
| **Who Saves** | Operation tool |
| **Key Rules** | DD-15 (POM assertions), DD-16 (file paths), DD-17 (parameter injection), DD-18 (imports) |

**AI Post-Processing Required:**
- DD-16: Override file paths to `tests/{workflow}/`
- DD-17: Inject actual parameter values (no placeholders)
- DD-18: Validate all imports resolve
- DD-15: Assertions use POM state methods, not return values

---

### 9.10 Step 10: Save & Run

> **Full Details:** `.claude/skills/qa-guidance-layer/references/step-10.md`

| Field | Value |
|-------|-------|
| **Operation Tool** | File I/O, `run_test` |
| **Quality Gate** | `qg_save_run` |
| **Gate Mode** | PRE-only |
| **Who Saves** | AI (after file writes) |
| **Key Rules** | DD-22 (stop-and-discuss on failure) |

**File Save Locations:**
```
framework/pages/{domain}/{page_name}.py
framework/tasks/{domain}/{task_name}.py
framework/roles/{role_name}.py
tests/{domain}/test_{intent}.py
```

**On Test Failure (DD-22):**
- STOP → REPORT → DISCUSS with user
- NEVER attempt fixes without user consultation
- User decides: investigate, restart, manual fix, or abort

---

**Document Status:** This is the authoritative source of truth for framework architecture.
**Related Docs:** CLAUDE.md (quick reference), README.md (overview), `.claude/skills/` (workflow skills)
