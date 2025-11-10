# Test Automation Framework Architecture

## Overview

This is a production-grade Selenium test automation framework built with Python and Pytest. It uses a **4-layer architecture** that separates concerns and makes tests maintainable, scalable, and reusable.

**Key Principles:**
- **Separation of Concerns:** Each layer has a specific responsibility
- **Reusability:** Business logic can be reused across multiple test scenarios
- **Maintainability:** UI changes only require updates in one place (Page Objects)
- **Scalability:** Easy to add new workflows, roles, and test scenarios

---

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: Test Cases                                        │
│  (What to test - business scenarios)                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: Roles                                             │
│  (Who is performing actions - user personas)                │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Tasks                                             │
│  (Business workflows - login, navigate, submit)             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: Page Objects                                      │
│  (UI interactions - click, type, select)                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 5: WebInterface                                      │
│  (Selenium wrapper - low-level driver operations)           │
└─────────────────────────────────────────────────────────────┘
                           ↓
                    Selenium WebDriver
                           ↓
                        Browser
```

---

## Layer Breakdown

### **Layer 1: Test Cases** (`tests/`)

**Responsibility:** Define WHAT to test (business scenarios, acceptance criteria)

**Example:**
```python
def test_user_workflow_submission_and_approval(web_interface):
    """
    Tests that:
    - User A can submit a transaction
    - User B can review and recommend the transaction
    - User C can approve the transaction
    - User D can release the transaction
    """
    UserA(web_interface).submit_new_transaction(data)
    UserB(web_interface).review_and_recommend_transaction(data)
    UserC(web_interface).approve_transaction(data)
    UserD(web_interface).release_transaction(data)
```

**Key Characteristics:**
- Reads like a business requirement
- No UI interaction details (those are abstracted away)
- Focuses on user goals and outcomes
- Uses Roles to execute workflows

---

### **Layer 2: Roles** (`framework/roles/`)

**Responsibility:** Define WHO is performing actions (user personas with credentials)

**Base Class:** `role.py`
- Handles user authentication (user_id, password, role name)
- Pulls credentials from config files or test data
- Provides common `_log_in()` method

**Example Role:**
```python
class StandardUser(Role):
    def __init__(self, web_interface, user_id=None, password=None):
        super().__init__(web_interface, user_id, password, rolename="STANDARD_USER")

        # Compose tasks this role can perform
        self.common_tasks = CommonTasks(web_interface)
        self.workflow_tasks = WorkflowTasks(web_interface)

    def submit_new_transaction(self, data):
        """
        Business method: Submit a new transaction
        """
        self.common_tasks.log_in(self.user_id, self.password)
        self.workflow_tasks.navigate_to_transaction_page()
        self.workflow_tasks.complete_transaction_form(data)
```

**Key Characteristics:**
- Represents a user persona (e.g., Admin, Approver, Standard User)
- Encapsulates credentials and permissions
- Composes tasks from Task layer
- Provides high-level business methods

**17 Role Types in Current Framework:**
- Admin roles (system configuration)
- Workflow initiators (submit requests)
- Reviewers (recommend transactions)
- Approvers (approve/reject)
- Releasers (final authorization)

---

### **Layer 3: Tasks** (`framework/tasks/`)

**Responsibility:** Define business workflows (sequences of page interactions)

**Task Modules:**
- `common_tasks.py` - Shared workflows (login, logout, navigation)
- `workflow_tasks.py` - Domain-specific workflows (submit, approve, review)

**Example Task:**
```python
class WorkflowTasks:
    def __init__(self, web_interface):
        self.home_page = HomePage(web_interface)
        self.dashboard_component = DashboardComponent(web_interface)
        self.transaction_page = TransactionPage(web_interface)

    def navigate_to_transaction_page(self):
        """
        Navigate from home to transaction page
        """
        (self.home_page
            .click_tile("Dashboard"))

        (self.dashboard_component
            .click_tab("Transactions")
            .expand_accordion("My Transactions")
            .click_accordion_link("Submit Transaction"))

    def complete_transaction_form(self, data):
        """
        Fill out and submit transaction form
        """
        (self.transaction_page
            .enter_order_number(data["order_number"])
            .select_order_type(data["order_type"])
            .enter_days_authorized(data["days"])
            .add_attachment(data["attachment_path"])
            .submit())
```

**Key Characteristics:**
- Reusable business workflows
- Composes multiple Page Object calls
- Uses method chaining for readability
- No direct Selenium calls (abstracted in Page Objects)

**8 Task Modules in Current Framework:**
- Common tasks (login, logout, navigation)
- Domain-specific workflows (7 modules)

---

### **Layer 4: Page Objects** (`framework/pages/`)

**Responsibility:** Encapsulate UI element interactions for specific pages

**Structure:**
- `common/` - Shared pages (login, home)
- `components/` - Reusable UI components (navbar, dashboard, activity guides)
- `[workflow]/` - Domain-specific pages

**Example Page Object:**
```python
class TransactionPage:
    def __init__(self, web_interface):
        self.ui = web_interface

    def enter_order_number(self, order_number):
        """Enter order number in the form"""
        self.ui.send_keys("id", "ORDER_NUMBER_FIELD", order_number)
        return self

    def select_order_type(self, order_type):
        """Select order type from dropdown"""
        self.ui.select_by_text("id", "ORDER_TYPE_DROPDOWN", order_type)
        return self

    def add_attachment(self, file_path):
        """Upload a file attachment"""
        self.ui.click("id", "ATTACH_BUTTON")
        self.ui.switch_ptmodframe(0)
        self.ui.click("id", "UPLOAD_BUTTON")
        self.ui.select_file_from_dialog(file_path)
        self.ui.click("id", "CONFIRM_BUTTON")
        return self

    def submit(self):
        """Submit the form"""
        self.ui.click("id", "SUBMIT_BUTTON")
        return self
```

**Key Characteristics:**
- One class per page/component
- Methods return `self` for method chaining
- Uses `web_interface` for all Selenium operations
- Contains element locators (IDs, XPaths)

**40+ Page Objects in Current Framework:**
- Common pages (login, home, process monitor)
- Reusable components (navbar, dashboards, activity guides)
- Domain-specific pages organized by workflow

---

### **Layer 5: WebInterface** (`framework/interfaces/web_interface.py`)

**Responsibility:** Wrap Selenium WebDriver with custom wait strategies and helper methods

**Key Methods:**

**Wait Strategies:**
```python
wait_for_element_present(by, value, timeout=10)
wait_for_element_visible(by, value, timeout=10)
wait_for_element_clickable(by, value, timeout=10)
wait_for_element_invisible(by, value, timeout=10)
```

**Element Interactions:**
```python
click(by, value)                    # Wait until clickable, then click
send_keys(by, value, text)          # Wait until clickable, then type
select_by_text(by, value, text)     # Select dropdown option
clear_send_keys(by, value, text)    # Clear field, then type
```

**Advanced Helpers:**
```python
switch_frame(id)                    # Switch to iframe
switch_window(index)                # Switch browser tabs
scroll_to_element(element)          # Scroll element into view
get_grid_row_nums_by_col_vals()     # Find table rows by column values
upload_attachment(file_path)        # Handle file uploads
select_file_from_dialog(file_path)  # Interact with OS file dialogs
```

**Key Characteristics:**
- All Selenium calls go through WebInterface
- Automatic waits before interactions
- Custom wait for loading indicators
- Handles iframes, modals, file uploads
- Grid/table interaction utilities

---

## Execution Flow

### **Test Runner → Pytest → Test Execution**

```
1. execute_<scenario>.py (Entry Point)
   ├── Sets environment (SBX, PRT, IDV)
   ├── Sets headless mode
   ├── Calls main.main()
   └── Passes test path and report settings

2. main.py (Pytest Launcher)
   ├── Initializes logging (autologger)
   ├── Configures pytest args
   │   ├── --env=<environment>
   │   ├── --headless=<true/false>
   │   ├── --html=<report_path>
   │   └── Test path
   └── Launches pytest.main()

3. conftest.py (Pytest Fixtures)
   ├── @pytest.fixture driver()
   │   └── Creates ChromeDriver with headless option
   ├── @pytest.fixture environment()
   │   └── Loads environment config from JSON
   ├── @pytest.fixture elevated_users()
   │   └── Loads user credentials from JSON
   └── @pytest.fixture web_interface()
       └── Wraps driver + environment + users

4. test_<scenario>.py (Actual Test)
   ├── Receives web_interface fixture
   ├── Loads test data from JSON
   ├── Instantiates Roles
   ├── Calls Role methods (business workflows)
   └── Roles → Tasks → Pages → WebInterface → Selenium

5. Test Completion
   ├── Driver quits (teardown in conftest)
   ├── HTML report generated
   └── Error log written (if failures)
```

---

## Directory Structure

```
framework_example_for_ai/
│
├── framework/                       # Framework code (reusable)
│   ├── interfaces/
│   │   ├── web_interface.py         # Selenium wrapper
│   │   ├── file_interface.py        # File I/O utilities
│   │   ├── excel_interface.py       # Excel read/write
│   │   └── oracle_interface.py      # Database queries
│   │
│   ├── pages/
│   │   ├── common/                  # Shared pages
│   │   │   ├── login_page.py
│   │   │   ├── home_page.py
│   │   │   └── process_monitor_page.py
│   │   │
│   │   ├── components/              # Reusable UI components
│   │   │   ├── navbar_component.py
│   │   │   ├── dashboard_component_superclass.py
│   │   │   └── activity_guide_component.py
│   │   │
│   │   └── [workflow_name]/         # Domain-specific pages
│   │       └── (multiple page objects per workflow)
│   │
│   ├── tasks/
│   │   ├── common_tasks.py          # Login, logout, navigation
│   │   └── [workflow]_tasks.py      # Domain-specific tasks (8 modules)
│   │
│   ├── roles/
│   │   ├── role.py                  # Base class for all roles
│   │   ├── admin.py                 # Admin role
│   │   └── [role_name].py           # 17 role implementations
│   │
│   └── resources/
│       ├── config/
│       │   ├── environment_config.json       # URLs, site IDs, passwords
│       │   └── elevated_user_config_*.json   # User credentials per env
│       │
│       ├── utilities/
│       │   ├── autologger.py        # Logging decorator and utilities
│       │   ├── test_data.py         # Test data loader
│       │   ├── arguments.py         # CLI argument parser
│       │   └── task_timer.py        # Performance timing
│       │
│       └── chromedriver/
│           └── driver.py            # WebDriver factory
│
└── tests/                           # Test scenarios
    ├── main.py                      # Pytest launcher (called by executors)
    ├── conftest.py                  # Pytest fixtures (driver, environment, etc.)
    │
    └── [scenario_name]/             # Test scenario folders
        ├── execute_[scenario].py    # Test runner (entry point)
        ├── tests/
        │   └── test_[scenario].py   # Actual test cases
        ├── data/
        │   └── input_data.json      # Test data
        └── _reports/                # HTML test reports and error logs
```

---

## Configuration Files

### **environment_config.json**
```json
{
  "IDV": {
    "id": "TESTSITE",
    "url": "https://test-environment.example.com",
    "default_password": "TestPass123"
  },
  "SBX": {
    "id": "SANDBOX",
    "url": "https://sandbox.example.com",
    "default_password": "SandboxPass123"
  }
}
```

### **elevated_user_config_SBX.json**
```json
{
  "ADMIN": {
    "user_id": "admin_user",
    "password": "AdminPass123"
  },
  "APPROVER": {
    "user_id": "approver_user",
    "password": "ApproverPass123"
  }
}
```

---

## Key Patterns

### **1. Method Chaining**

Page Objects and Tasks use method chaining for readability:

```python
(self.transaction_page
    .enter_order_number(data["order_number"])
    .select_order_type(data["order_type"])
    .enter_days(data["days"])
    .submit())
```

**Why:** Reads like natural language, easy to follow multi-step workflows

---

### **2. Role-Task-Page Composition**

Each layer composes the layer below:

```python
# Role composes Tasks
class StandardUser(Role):
    def __init__(self, web_interface):
        self.common_tasks = CommonTasks(web_interface)
        self.workflow_tasks = WorkflowTasks(web_interface)

# Task composes Pages
class WorkflowTasks:
    def __init__(self, web_interface):
        self.home_page = HomePage(web_interface)
        self.transaction_page = TransactionPage(web_interface)

# Page uses WebInterface
class TransactionPage:
    def __init__(self, web_interface):
        self.ui = web_interface
```

**Why:** Clean separation of concerns, easy to test each layer independently

---

### **3. Fixture Injection (Pytest)**

Tests receive dependencies via fixtures:

```python
@pytest.fixture()
def web_interface(driver, environment, elevated_users):
    """Compose all dependencies into one object"""
    yield WebInterface(driver, environment, elevated_users)

def test_workflow(web_interface):
    """Test receives fully configured web_interface"""
    User(web_interface).perform_action(data)
```

**Why:** Tests don't manage setup/teardown, configuration is centralized

---

### **4. Automatic Logging**

Decorator logs entry/exit of methods:

```python
@autologger.automation_logger("Task")
def navigate_to_transaction_page(self):
    """Navigate to transaction page"""
    # Method implementation
```

**Logs Output:**
```
12:34:56 [Task] navigate_to_transaction_page - START
12:34:58 [Task] navigate_to_transaction_page - END
```

**Why:** Traceability, debugging, performance tracking

---

## Extending the Framework

### **Adding a New Test Scenario**

1. **Create test scenario folder:**
   ```
   tests/
   └── new_workflow/
       ├── execute_new_workflow.py
       ├── tests/
       │   └── test_new_workflow.py
       └── data/
           └── input_data.json
   ```

2. **Create test runner (`execute_new_workflow.py`):**
   ```python
   import sys
   from pathlib import Path
   sys.path.append(str(Path(__file__).parent.parent))
   import main

   if __name__ == "__main__":
       main.main(
           test_path="tests/test_new_workflow.py",
           env="SBX",
           headless=False
       )
   ```

3. **Create test case (`test_new_workflow.py`):**
   ```python
   from roles.new_role import NewRole

   def test_new_workflow(web_interface):
       data = load_test_data()
       NewRole(web_interface).perform_workflow(data)
   ```

---

### **Adding a New Role**

1. **Create role file (`framework/roles/new_role.py`):**
   ```python
   from roles.role import Role
   from tasks.common_tasks import CommonTasks
   from tasks.workflow_tasks import WorkflowTasks

   class NewRole(Role):
       def __init__(self, web_interface, user_id=None, password=None):
           super().__init__(web_interface, user_id, password, rolename="NEW_ROLE")

           self.common_tasks = CommonTasks(web_interface)
           self.workflow_tasks = WorkflowTasks(web_interface)

       def perform_workflow(self, data):
           """High-level business method"""
           self.common_tasks.log_in(self.user_id, self.password)
           self.workflow_tasks.execute_steps(data)
   ```

2. **Add credentials to config:**
   ```json
   {
     "NEW_ROLE": {
       "user_id": "new_user",
       "password": "NewPass123"
     }
   }
   ```

---

### **Adding a New Task**

1. **Create or update task file (`framework/tasks/workflow_tasks.py`):**
   ```python
   class WorkflowTasks:
       def __init__(self, web_interface):
           self.page1 = Page1(web_interface)
           self.page2 = Page2(web_interface)

       def new_workflow_step(self, data):
           """New business workflow"""
           self.page1.perform_action(data)
           self.page2.verify_result()
   ```

---

### **Adding a New Page Object**

1. **Create page file (`framework/pages/workflow/new_page.py`):**
   ```python
   class NewPage:
       def __init__(self, web_interface):
           self.ui = web_interface

       def enter_field(self, value):
           """Interact with form field"""
           self.ui.send_keys("id", "FIELD_ID", value)
           return self

       def submit(self):
           """Submit the form"""
           self.ui.click("id", "SUBMIT_BUTTON")
           return self
   ```

---

## Running Tests

### **Run Specific Test Scenario**
```bash
python tests/scenario_name/execute_scenario.py
```

### **Run with Custom Environment**
```python
main.main(
    test_path="tests/test_workflow.py",
    env="PRT",           # Production environment
    headless=True,       # Run in headless mode
    base_report_name="my_test"
)
```

### **Run Directly with Pytest**
```bash
pytest tests/scenario/tests/test_file.py --env=SBX --headless=False
```

---

## Reporting

### **HTML Reports**
Generated in `tests/[scenario]/_reports/`:
- `[scenario]_YYYYMMDD_HHMMSS.html` - Full test report with pass/fail status

### **Error Logs**
Generated in `tests/[scenario]/_reports/`:
- `ERROR_LOG_[scenario]_YYYYMMDD_HHMMSS.txt` - Stack traces and error messages

---

## Dependencies

**Core:**
- Python 3.x
- Selenium
- Pytest
- pytest-html (HTML reports)

**Utilities:**
- openpyxl (Excel operations)
- pywinauto (OS file dialog interactions)
- cx_Oracle (database queries)

---

## Best Practices

### **1. Keep Tests at Business Level**
```python
# Good - reads like a business requirement
def test_transaction_approval():
    Initiator(web_interface).submit_transaction(data)
    Approver(web_interface).approve_transaction(data)

# Bad - exposes implementation details
def test_transaction_approval():
    driver.find_element(By.ID, "submit").click()
    driver.find_element(By.ID, "approve").click()
```

### **2. Use Method Chaining**
```python
# Good - readable, fluent
(self.page
    .enter_name("John")
    .enter_email("john@example.com")
    .submit())

# Bad - verbose
self.page.enter_name("John")
self.page.enter_email("john@example.com")
self.page.submit()
```

### **3. Return `self` from Page Methods**
```python
def click_button(self):
    self.ui.click("id", "BUTTON")
    return self  # Enable chaining
```

### **4. Use Fixtures for Setup**
```python
# Good - use pytest fixtures
def test_workflow(web_interface, data):
    User(web_interface).execute(data)

# Bad - manual setup in each test
def test_workflow():
    driver = webdriver.Chrome()
    data = json.load(open("data.json"))
    # ...test code...
    driver.quit()
```

### **5. Keep Page Objects Focused**
- One page object per page/component
- Methods should do ONE thing
- No business logic in page objects (put in Tasks)

---

## Framework Statistics

**Current Production Framework:**
- **17 Roles** - User personas across different permission levels
- **8 Task Modules** - Reusable business workflows
- **40+ Page Objects** - UI interaction encapsulation
- **Multiple Test Scenarios** - End-to-end workflow coverage
- **Environment Support** - IDV (dev), SBX (sandbox), PRT (production)
- **Reporting** - HTML reports with pass/fail status and error logs

---

## Framework Advantages

### **Maintainability**
- UI changes only require updates in Page Objects
- Business logic changes only require updates in Tasks
- Test scenarios remain stable

### **Reusability**
- Roles can be reused across multiple tests
- Tasks can be composed in different sequences
- Page Objects used by multiple Tasks

### **Readability**
- Tests read like business requirements
- No low-level Selenium details in tests
- Method chaining creates fluent, natural language

### **Scalability**
- Easy to add new test scenarios
- Easy to add new user roles
- Easy to add new workflows

### **Parallel Execution Ready**
- Function-scoped driver fixtures (one per test)
- No shared state between tests
- Can run tests in parallel with pytest-xdist

---

## Next Steps for Framework Evolution

**Potential Enhancements:**
1. **Page Object Generator** - Auto-generate page objects from page inspection
2. **Visual Regression Testing** - Screenshot comparison with baseline images
3. **API Testing Layer** - Add REST API validation alongside UI tests
4. **Performance Metrics** - Track page load times, transaction durations
5. **CI/CD Integration** - GitHub Actions or Jenkins pipeline
6. **Cross-Browser Support** - Firefox, Safari, Edge drivers
7. **Mobile Testing** - Appium integration for mobile apps
8. **AI Integration** - MCP server for AI-assisted test creation/debugging

---

## Glossary

**Role:** User persona with specific permissions and credentials

**Task:** Business workflow composed of multiple page interactions

**Page Object:** Encapsulation of UI elements and interactions for a specific page

**WebInterface:** Selenium wrapper providing wait strategies and helper methods

**Fixture:** Pytest setup/teardown mechanism for test dependencies

**Method Chaining:** Returning `self` from methods to enable fluent syntax

**Activity Guide:** Multi-step wizard/form workflow

**Elevated User:** User with special permissions (admin, approver, etc.)

---

**Framework Version:** Production (Enterprise)
**Last Updated:** 2025-04-11
**Framework Type:** Selenium + Pytest + 4-Layer Architecture
