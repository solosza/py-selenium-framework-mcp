# Test Plan - py_sel_framework_mcp

**Project:** Python Selenium Test Automation Framework with MCP Integration
**Target Application:** http://www.automationpractice.pl/index.php
**Test Plan Version:** 1.0
**Author:** QA Lead
**Date:** 2025-01-11

---

## 1. Executive Summary

### Overview
This test plan defines the testing approach for the py_sel_framework_mcp project, a portfolio demonstration of QA Lead-level test automation architecture with AI integration (MCP server).

### Test Objectives
- Validate core e-commerce workflows (authentication, catalog browsing, shopping cart, checkout)
- Demonstrate professional 4-layer test automation framework (Role → Task → Page → WebInterface)
- Showcase AI integration via MCP server for test execution and analysis
- Create reusable framework template for future projects

### Scope
- **MVP:** 15 automated tests covering 4 critical workflows
- **Coverage:** 24% of designed scenarios (62 total scenarios, 15 MVP, 47 deferred to v2.0)
- **Environment:** Local execution against live site (automationpractice.pl)
- **Browser:** Chrome (headed mode for debugging)

### Key Milestones
- **Phase 0 Complete:** Test design documented (DONE)
- **Phase 1 Complete:** Test plan approved (this document)
- **Phase 2:** Task generation
- **Phase 3:** Framework + tests implementation + MCP integration

---

## 2. Test Objectives

### Primary Objectives
1. **Validate Core Workflows:** Ensure authentication, product browsing, cart management, and checkout function correctly
2. **Demonstrate Architecture:** Showcase professional 4-layer framework design (Roles, Tasks, Pages, WebInterface)
3. **Prove Maintainability:** Create modular, reusable components for future test expansion
4. **Showcase AI Integration:** Integrate MCP server to enable AI-assisted test execution and debugging

### Quality Goals
- **Pass Rate:** 90%+ pass rate for all MVP tests
- **Reliability:** Tests run consistently without flakiness (one retry allowed for real-world flakiness)
- **Execution Time:** Full suite completes in <15 minutes
- **Code Quality:** Clean, well-documented code demonstrating best practices

### Learning Objectives
- Master 4-layer test automation architecture
- Implement Model Context Protocol (MCP) for AI integration
- Demonstrate QA Lead-level technical skills for job interviews
- Create reusable framework template

---

## 3. Test Scope

### In Scope (MVP - 15 Tests)

#### Authentication (4 tests)
- Valid login with registered user
- Invalid credentials error handling
- New user registration flow
- User logout functionality

#### Product Catalog (4 tests)
- Browse products by category (Women)
- Filter products by multiple criteria (size + color)
- Sort products by price (Low to High)
- Quick View modal display

#### Shopping Cart (4 tests)
- Add product to cart from detail page
- Update product quantity in cart
- Remove product from cart
- View cart summary with totals

#### Checkout (3 tests)
- Complete checkout flow (registered user, end-to-end)
- Address validation error handling
- Payment method selection

**Total MVP Tests:** 15 tests covering critical path through application

---

### Out of Scope (Deferred to v2.0)

#### Authentication (10 scenarios deferred)
- Password recovery
- Registration validation (duplicate email, weak password, missing fields)
- Email format validation
- Empty field validation

#### Product Catalog (37 scenarios deferred)
- Search functionality
- Product comparison
- Add to cart from listing page
- Full product detail page
- Grid/List view toggle
- Advanced filter combinations
- All sorting options

#### Account Management (entire workflow deferred)
- View order history
- Manage saved addresses
- Update profile information
- View account dashboard

#### Additional Features (entire workflow deferred)
- Wishlist functionality
- Product reviews
- Contact form
- Newsletter subscription

**Total Deferred:** 47+ scenarios to v2.0 (focus on MVP demonstration)

---

## 4. Test Approach (Execution Strategy)

### Test Types

#### Functional Testing (Primary Focus)
- **UI Workflow Testing:** Automated browser-based tests validating user workflows
- **E2E Testing:** Complete user journeys from login to order confirmation
- **Validation Testing:** Error handling, form validation, data integrity

#### Smoke Testing
**3-Test Smoke Suite for Quick Validation:**
1. `test_valid_login` - Core authentication works
2. `test_add_to_cart` - Core shopping flow works
3. `test_complete_checkout` - Core checkout flow works

**Purpose:** Quick validation before running full suite (under 5 minutes)

#### Regression Testing
- **Full Suite:** Run all 15 MVP tests before any code changes
- **Frequency:** On-demand (local development)
- **Future:** CI integration in v2.0

---

### Test Execution Strategy

#### Execution Model
- **Independent Tests:** Each test resets state, no dependencies between tests
- **Isolation:** Tests can run in any order, parallel execution possible in future
- **State Management:** Each test starts from known state (logged out, empty cart)

#### Browser Strategy
- **Browser:** Chrome (latest stable version)
- **Mode:** Headed (visible browser for debugging)
- **WebDriver:** ChromeDriver managed via WebDriver Manager (auto-download)
- **Future:** Add Firefox, Edge support in v2.0

#### Test Data Strategy
- **Registered Users:** Pre-created test accounts on automationpractice.pl (2-3 accounts stored in `users.json`)
- **Products:** Use existing products on site (dynamic discovery, first available in category)
- **Registration Data:** Generate using Faker library (unique email per run)
- **Addresses/Payment:** Generate using Faker library

#### Error Handling & Retry
- **Retry Strategy:** Retry once on failure (pytest-rerunfailures plugin)
- **Screenshot Capture:** On failure only (saves space)
- **Explicit Waits:** Use WebDriverWait for all dynamic elements (avoid flakiness)
- **Timeout Configuration:** Configurable via .env (default: 10s implicit, 30s explicit)

---

### Tools & Frameworks

#### Core Stack
- **Language:** Python 3.x
- **Test Runner:** Pytest
- **Browser Automation:** Selenium WebDriver
- **Reporting:** pytest-html (HTML test reports)
- **Test Data:** Faker library for data generation
- **Driver Management:** WebDriver Manager (auto-download ChromeDriver)

#### AI Integration
- **MCP Server:** Python-based Model Context Protocol server
- **MCP Tools:** 11 tools following the complete QA workflow (requirements → execution → coverage)
- **Purpose:** Enable AI assistants (Claude Code, Cursor, Zed, etc.) to automate the entire QA lifecycle from requirements to coverage tracking

**MCP Workflow (Tools Numbered by Execution Order):**
1. **Requirements → Test Scenarios:** generate_tests_from_user_story
2. **Test Scenarios → Elements:** discover_elements_for_test_scenario
3. **Elements → Framework Code:** generate_page_object, generate_task, generate_role
4. **Framework → Test Code:** generate_test_template
5. **Discovery:** list_tests, get_framework_structure
6. **Execution & Analysis:** run_test, analyze_failure
7. **Coverage Tracking:** get_test_coverage

**Value Proposition (QA Manager Perspective):**
- **Tool-Agnostic Standardization:** Works across all MCP-compatible IDEs (VS Code, Cursor, Zed, IntelliJ)
- **Cost & Scale:** Free infrastructure vs $20/month per seat for individual AI tool licenses (10 engineers = $2,400/year savings)
- **Team Enablement:** Junior engineers can go from user story to executable tests via chained tool workflow
- **Customization & Control:** Enforces team standards and best practices automatically
- **Requirements Traceability:** Direct chain from user story → test scenarios → elements → code → execution → coverage

---

### MCP Tool Specifications (Workflow Order)

#### Phase 1: Requirements Analysis
**Tool 1: generate_tests_from_user_story**
- **Purpose:** Break user story into test scenarios (Given-When-Then format)
- **Input:**
  - user_story: String with acceptance criteria
  - workflow: Target workflow (auth, catalog, cart, checkout)
- **Output:** JSON array of test scenarios
  ```json
  [
    {
      "name": "test_filter_by_size_m",
      "description": "Verify user can filter products by size M",
      "given": "User is on product listing page",
      "when": "User selects size M checkbox",
      "then": "Only M-sized products are displayed"
    }
  ]
  ```

#### Phase 2: Element Discovery
**Tool 2: discover_elements_for_test_scenario**
- **Purpose:** Analyze page and extract ONLY elements needed for specific test scenario
- **Input:**
  - url: Page URL to analyze
  - test_scenario: Scenario object from Tool 1 (Given-When-Then)
- **Output:** JSON with required locators and suggested methods
  ```json
  {
    "scenario": "test_filter_by_size_m",
    "required_elements": [
      {"locator": "#layered_id_attribute_2", "name": "SIZE_M_CHECKBOX", "needed_for": "when clause"},
      {"locator": ".product_list li", "name": "PRODUCT_LIST_ITEMS", "needed_for": "then clause"}
    ],
    "suggested_methods": ["filter_by_size(size: str)", "get_displayed_products()"]
  }
  ```

#### Phase 3: Framework Code Generation
**Tool 3: generate_page_object**
- **Purpose:** Create page object with locators from Tool 2
- **Input:**
  - page_name: "ProductListPage"
  - elements: Element array from Tool 2
- **Output:** JSON with generated Python code following framework patterns

**Tool 4: generate_task**
- **Purpose:** Create task workflow using page objects
- **Input:**
  - task_name: "CatalogTasks"
  - workflow_description: "Browse products, filter, sort"
- **Output:** JSON with generated task class code

**Tool 5: generate_role**
- **Purpose:** Create role with credentials and preconditions
- **Input:**
  - role_name: "RegisteredUser", "GuestUser"
  - capabilities: ["can_login", "has_cart_items"]
  - credentials: Optional user credentials
- **Output:** JSON with generated role class code

#### Phase 4: Test Code Generation
**Tool 6: generate_test_template**
- **Purpose:** Create pytest test from scenario (Tool 1 output)
- **Input:**
  - test_name: From scenario.name
  - workflow: "catalog"
  - scenario: Full scenario object from Tool 1
- **Output:** JSON with complete test code (AAA pattern, fixtures, autologger)

#### Phase 5: Framework Discovery
**Tool 7: list_tests**
- **Purpose:** Catalog all available tests
- **Input:** workflow (optional filter)
- **Output:** JSON with tests grouped by workflow

**Tool 8: get_framework_structure**
- **Purpose:** Map framework architecture for new team members
- **Input:** None
- **Output:** JSON with architecture layers, test coverage by workflow

#### Phase 6: Test Execution
**Tool 9: run_test**
- **Purpose:** Execute test(s) and return structured results
- **Input:** test_path, marker (optional), browser (optional), headless (optional)
- **Output:** JSON with status, duration, pass/fail counts, HTML report path, artifacts

#### Phase 7: Failure Analysis
**Tool 10: analyze_failure**
- **Purpose:** AI-powered debugging with actionable suggestions
- **Input:** test_name, run_id (optional)
- **Output:** JSON with error type, screenshot, log excerpt, likely cause, suggestions

#### Phase 8: Coverage Tracking
**Tool 11: get_test_coverage**
- **Purpose:** Track tested vs designed scenarios
- **Input:** workflow (optional filter)
- **Output:** JSON with scenarios designed vs implemented, coverage percent, gaps

---

#### Configuration Management
- **Environment Variables:** .env file for configuration
- **python-dotenv:** Load environment variables

#### Version Control
- **Git/GitHub:** Source control
- **Branch Strategy:** Feature branches for task implementation

---

## 5. Test Environment Setup

### Environment Details

| Environment | URL | Purpose | Browser | Credentials |
|-------------|-----|---------|---------|-------------|
| Local | http://www.automationpractice.pl/index.php | All testing | Chrome (headed) | Pre-created accounts in users.json |

**Note:** No staging or production environments - all testing against live public demo site.

---

### Browser & Device Matrix

| Browser | Version | OS | Mode | Priority |
|---------|---------|----|----|---------|
| Chrome | Latest stable | Windows 10/11 | Headed | P0 (MVP) |
| Firefox | Latest | Windows 10/11 | Headed | P1 (v2.0) |
| Edge | Latest | Windows 10/11 | Headed | P1 (v2.0) |

**MVP Focus:** Chrome only for initial implementation

---

### Dependencies

#### External Services
- **automationpractice.pl:** Target application (third-party demo site)
  - **Risk:** Site may be down or slow
  - **Mitigation:** Test site availability before test runs, implement explicit waits

#### No External Dependencies
- No payment gateway integration (site uses fake payment methods)
- No email verification required for registration
- No external APIs to mock

---

### Setup Instructions

#### Prerequisites
```bash
# Python 3.8+
python --version

# pip package manager
pip --version

# Git
git --version
```

#### Installation Steps
```bash
# 1. Clone repository
git clone <repo-url>
cd py_sel_framework_mcp

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your configuration

# 5. Verify ChromeDriver setup (WebDriver Manager handles this automatically)
pytest --collect-only  # Should list all tests without errors
```

#### Environment Variables (.env)
```bash
# Application
BASE_URL=http://www.automationpractice.pl/index.php

# Browser Configuration
BROWSER=chrome
HEADLESS=false

# Timeouts (seconds)
IMPLICIT_WAIT=10
EXPLICIT_WAIT=30

# Artifact Paths
SCREENSHOT_DIR=screenshots
LOG_DIR=logs
REPORT_DIR=_reports

# Test Data
TEST_DATA_DIR=framework/resources/data
```

---

## 6. Test Data Strategy

### Data Sources

#### Pre-Created Test Accounts (Registered Users)
**Storage:** `framework/resources/data/users.json`

**Accounts:**
```json
{
  "registered_user_1": {
    "email": "testuser1@example.com",
    "password": "Test123!",
    "first_name": "John",
    "last_name": "Doe"
  },
  "registered_user_2": {
    "email": "testuser2@example.com",
    "password": "Test123!",
    "first_name": "Jane",
    "last_name": "Smith"
  }
}
```

**Setup:** Manually register 2-3 accounts on automationpractice.pl before test execution

---

#### Generated Test Data (Faker)
**Use Cases:**
- Registration tests (unique email per run to avoid duplicate errors)
- Address entry during checkout
- Phone numbers, names for forms

**Example:**
```python
from faker import Faker
fake = Faker()

new_user = {
    "email": fake.email(),
    "password": "Test123!",
    "first_name": fake.first_name(),
    "last_name": fake.last_name(),
    "address": fake.street_address(),
    "city": fake.city(),
    "zip": fake.zipcode(),
    "phone": fake.phone_number()
}
```

---

#### Product Data (Dynamic Discovery)
**Strategy:** Use whatever products exist on automationpractice.pl
- Navigate to category (Women, Dresses, T-Shirts)
- Select first available product
- No hardcoded product IDs (flexible, but less explicit)

**Assumption:** Site has stable product catalog (validate during implementation)

---

### Data Management Approach

#### Per-Test Isolation
- Each test creates/uses its own data
- No shared state between tests
- Tests clean up after themselves (logout, clear cart)

**Example:**
- `test_valid_login`: Uses pre-created account from users.json
- `test_registration`: Generates unique email with Faker
- `test_add_to_cart`: Uses first product in Women category

#### No Database Access
- No direct database manipulation (site is third-party)
- All data setup via UI workflows
- Cleanup via UI actions (logout, cart removal)

#### Data Cleanup
- **Logout after tests:** Ensure user is logged out
- **Cart cleanup:** Not critical (cart is session-based, resets on logout)
- **Accounts:** Pre-created accounts remain (stable data)

---

## 7. Entry & Exit Criteria

### Entry Criteria (When can testing begin?)

- [x] **Phase 0 Test Design Complete:** All workflows designed, scenarios documented
- [ ] **Test Environment Accessible:** automationpractice.pl is reachable and functional
- [ ] **Test Framework Setup:** Base infrastructure implemented (WebInterface, conftest.py, fixtures)
- [ ] **Test Data Ready:** Pre-created test accounts registered on site, credentials stored in users.json
- [ ] **Dependencies Installed:** Python packages, ChromeDriver (via WebDriver Manager)

---

### Exit Criteria (When is testing complete?)

- [ ] **All MVP Tests Implemented:** 15 tests covering 4 workflows
- [ ] **Pass Rate Target Met:** 90%+ tests passing consistently
- [ ] **Smoke Suite Defined:** 3 critical tests tagged for quick validation
- [ ] **Test Reports Generated:** HTML reports produced for test runs
- [ ] **MCP Server Integrated:** 11 MCP tools implemented and functional (full workflow from requirements to coverage)
- [ ] **Tool Chaining Validated:** Tools 1→2→3→4→5→6 can chain together (user story to executable test)
- [ ] **Code Generation Validated:** MCP-generated code follows framework patterns and passes linting
- [ ] **Documentation Complete:** README with setup instructions, framework architecture documented, MCP tool workflow guide
- [ ] **Demo Prepared:** Full workflow demo ready (user story → generated test → execution → coverage tracking)

---

## 8. Risks & Mitigation

### Risk Assessment

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| **Target site (automationpractice.pl) is down or slow** | High | Medium | Test site availability before runs, implement explicit waits, increase timeouts if needed |
| **Site structure changes (locators break)** | High | Low | Use flexible locators (CSS/XPath), implement WebDriverWait, design for maintainability |
| **MCP integration complexity** | Medium | Medium | Defer MCP to Week 2 after framework stable, start with simple tools (run_test), expand gradually |
| **Framework learning curve** | Medium | High | Reference original framework (OGF) patterns, keep architecture simple initially, iterate |
| **Test flakiness (timing issues)** | High | High | Use explicit waits (WebDriverWait), avoid hard-coded sleeps, implement retry logic (pytest-rerunfailures) |
| **Test data issues (account lockout, duplicate emails)** | Medium | Medium | Use multiple pre-created accounts (rotation), generate unique emails for registration tests |
| **ChromeDriver version mismatch** | Low | Low | Use WebDriver Manager for auto-download/management |

---

### Contingency Plans

#### If Target Site Goes Down
- **Immediate:** Verify site is accessible via browser
- **Short-term:** Wait for site recovery (demo sites have downtime)
- **Long-term (v2.0):** Consider local mirror or alternative demo site

#### If Framework Architecture Too Complex
- **Fallback:** Simplify to 3-layer (remove Roles, keep Tasks → Pages → WebInterface)
- **Assessment:** Evaluate after implementing 3-5 tests, adjust if needed

#### If MCP Integration Blocked
- **Decision:** MCP is "nice to have," not critical for portfolio demonstration
- **Action:** Complete 15 tests first, add MCP as v2.0 feature if time runs out
- **Interview Value:** Framework architecture is more important than MCP

#### If Tests Are Flaky
- **Diagnosis:** Run tests 3-5 times, identify flaky tests
- **Fix:** Increase explicit waits, add debug logging, improve locators
- **Acceptable:** One retry allowed (pytest-rerunfailures), but fix root cause

---

## 9. Deliverables

### Code Deliverables

#### Framework Infrastructure
- [ ] `framework/interfaces/web_interface.py` - Selenium wrapper with enhanced methods
- [ ] `framework/pages/common/` - Common pages (authentication, home, header)
- [ ] `framework/pages/catalog/` - Catalog pages (product list, quick view modal)
- [ ] `framework/pages/cart/` - Cart pages (cart page, add to cart modal)
- [ ] `framework/pages/checkout/` - Checkout pages (address, shipping, payment, review, confirmation)
- [ ] `framework/tasks/common_tasks.py` - Authentication, navigation tasks
- [ ] `framework/tasks/catalog_tasks.py` - Catalog browsing tasks
- [ ] `framework/tasks/cart_tasks.py` - Cart management tasks
- [ ] `framework/tasks/checkout_tasks.py` - Checkout workflow tasks
- [ ] `framework/roles/` - User roles (guest, registered user)
- [ ] `framework/resources/data/users.json` - Test account credentials
- [ ] `framework/resources/utilities/data_generator.py` - Faker wrapper + JSON loader

#### Test Scenarios (15 Tests)
- [ ] `tests/auth/test_valid_login.py`
- [ ] `tests/auth/test_invalid_credentials.py`
- [ ] `tests/auth/test_registration.py`
- [ ] `tests/auth/test_logout.py`
- [ ] `tests/catalog/test_browse_category.py`
- [ ] `tests/catalog/test_filter_products.py`
- [ ] `tests/catalog/test_sort_by_price.py`
- [ ] `tests/catalog/test_quick_view.py`
- [ ] `tests/cart/test_add_to_cart.py`
- [ ] `tests/cart/test_update_quantity.py`
- [ ] `tests/cart/test_remove_from_cart.py`
- [ ] `tests/cart/test_view_cart_summary.py`
- [ ] `tests/checkout/test_complete_checkout.py`
- [ ] `tests/checkout/test_address_validation.py`
- [ ] `tests/checkout/test_payment_selection.py`

#### Configuration & Fixtures
- [ ] `.env.example` - Environment variable template
- [ ] `.env` - Local configuration (not committed)
- [ ] `conftest.py` - Pytest fixtures (driver, web_interface, test_users)
- [ ] `pytest.ini` - Pytest configuration
- [ ] `requirements.txt` - Python dependencies

#### MCP Server (11 Tools - Workflow Ordered)
- [ ] `mcp_server/server.py` - MCP server implementation
- [ ] `mcp_server/tools/` - Tool implementations (numbered by workflow phase):
  - [ ] `tool_01_generate_tests_from_user_story.py` - Requirements analysis
  - [ ] `tool_02_discover_elements_for_test_scenario.py` - Element discovery
  - [ ] `tool_03_generate_page_object.py` - Page object generation
  - [ ] `tool_04_generate_task.py` - Task generation
  - [ ] `tool_05_generate_role.py` - Role generation
  - [ ] `tool_06_generate_test_template.py` - Test code generation
  - [ ] `tool_07_list_tests.py` - Test catalog
  - [ ] `tool_08_get_framework_structure.py` - Framework mapping
  - [ ] `tool_09_run_test.py` - Test execution
  - [ ] `tool_10_analyze_failure.py` - Failure analysis
  - [ ] `tool_11_get_test_coverage.py` - Coverage tracking
- [ ] `mcp_server/utils/` - Supporting utilities:
  - [ ] `pytest_executor.py` - Pytest execution wrapper
  - [ ] `test_discovery.py` - Test scanner and catalog builder
  - [ ] `failure_analyzer.py` - Failure analysis engine
  - [ ] `code_generator.py` - Code scaffolding generator (templates for pages/tasks/roles)
  - [ ] `coverage_calculator.py` - Coverage calculation
  - [ ] `element_discovery.py` - Page element analyzer (uses Selenium for live inspection)
  - [ ] `requirements_parser.py` - User story and acceptance criteria parser
- [ ] `.claude/mcp_settings.json` - MCP server configuration (local, not committed)

---

### Documentation Deliverables

- [ ] `README.md` - Project overview, setup instructions, usage guide
- [ ] `docs/0-test-design-py-sel-framework-mcp.md` - Phase 0 test design (COMPLETE)
- [ ] `docs/FRAMEWORK_ARCHITECTURE.md` - Architecture diagram and design decisions (optional)
- [ ] `docs/mcp-learning-notes.md` - MCP concepts and rationale (COMPLETE)
- [ ] Test execution reports (HTML reports in `_reports/`)

---

### Demo Deliverables (Portfolio Presentation)

- [ ] **Demo Video or Live Demo:** Show framework in action
  - Execute smoke suite (3 tests)
  - Show test reports
  - Demonstrate MCP integration (Claude running tests)

- [ ] **Interview Talking Points:** Prepare to explain:
  - 4-layer architecture rationale
  - Design decisions (Page Object Model, task methods, roles)
  - MCP integration value proposition
  - Challenges faced and solutions

---

## 10. Success Criteria

### Functional Success

- [ ] **15 MVP Tests Passing:** All authentication, catalog, cart, and checkout tests implemented and passing
- [ ] **90%+ Pass Rate:** Tests run reliably (13-15 of 15 passing consistently)
- [ ] **End-to-End Flow Works:** Can successfully complete full user journey (login → browse → cart → checkout)
- [ ] **Execution Time:** Full suite completes in <15 minutes

---

### Technical Success

- [ ] **4-Layer Architecture Demonstrated:** Framework uses Role → Task → Page → WebInterface pattern
- [ ] **Code Quality:** Clean, maintainable code with clear separation of concerns
- [ ] **Reusable Components:** Page objects, tasks, roles can be reused for future tests
- [ ] **MCP Integration Functional:** 11 MCP tools working in chained workflow (requirements → coverage)
- [ ] **Tool Chaining Proven:** Can execute full workflow: Tool 1 (user story) → Tool 2 (elements) → Tools 3-5 (framework) → Tool 6 (tests) → Tool 9 (execute) → Tool 11 (coverage)
- [ ] **Documentation Complete:** README and architecture docs enable others to understand and extend framework
- [ ] **Generated Code Follows Framework Patterns:** Code generated by MCP tools passes linting and matches framework conventions

---

### Business Success (Portfolio/Interview Goals)

- [ ] **Portfolio-Ready:** Project demonstrates QA Lead/QA Manager-level skills
- [ ] **Interview Preparedness:** Can explain architecture, design decisions, technical challenges, and team infrastructure value
- [ ] **Differentiation:** MCP integration shows forward-thinking AI+QA vision and team leadership
- [ ] **Reusability:** Framework serves as template for future test automation projects

**Interview Talking Points - "Why Not Just Use Claude Code?"**

When asked why build an MCP server instead of just using Claude Code directly:

1. **Tool-Agnostic Team Standardization**
   - "Not all team members use the same IDE - we have VS Code, Cursor, Zed, and IntelliJ users"
   - "MCP server works with any MCP-compatible client, ensuring consistent workflows across the team"
   - "Individual tool licenses don't help the engineer using a different IDE"

2. **Cost & Scale**
   - "Claude Code is $20/month per seat - for a team of 10 engineers, that's $2,400/year"
   - "MCP server is free infrastructure that scales to unlimited team members"
   - "As QA Manager, I need cost-effective solutions that work for the entire team"

3. **Customization & Control**
   - "MCP tools enforce our framework patterns - generated code automatically follows team standards"
   - "We control the code generation templates, ensuring consistency across all engineers"
   - "Junior engineers get guardrails through standardized scaffolding, reducing code review burden"

4. **Team Enablement vs Individual Productivity**
   - "Claude Code solves individual productivity, MCP server solves team infrastructure"
   - "As a manager, I'm building tools that enable the team, not just myself"
   - "This demonstrates thinking at the QA Manager level - infrastructure over individual efficiency"

5. **Complete Workflow Automation (NEW - Key Differentiator)**
   - "Our MCP server automates the entire QA lifecycle: requirements → test scenarios → element discovery → framework code → test code → execution → coverage"
   - "Tools are chained: Tool 1 output feeds into Tool 2, which feeds into Tools 3-5, etc."
   - "A junior QA can hand a user story to the MCP server and get executable tests that follow our patterns"
   - "This isn't just test execution - it's requirements traceability, design, implementation, and reporting in one workflow"
   - "Claude Code gives you AI assistance; our MCP server gives you a complete QA process engine"

---

## 11. Appendix

### Reference Documents

- **Phase 0 Test Design:** `docs/0-test-design-py-sel-framework-mcp.md`
- **QA 4D Framework Process Docs:**
  - `docs/0-requirements-and-test-design-v1.md` (Phase 0 template)
  - `docs/1-create-test-plan-v1.md` (Phase 1 template - this document follows this structure)
- **MCP Learning Notes:** `docs/mcp-learning-notes.md`
- **Target Application:** http://www.automationpractice.pl/index.php
- **Design Decisions:** `docs/DESIGN_DECISIONS.md` (architectural decisions documented during implementation)

**Note on MCP PRD:** A development-track PRD was initially created at `tasks/0006-prd-mcp-server.md` but was created in error (this is a QA track project using test design + test plan, not dev PRD). The MCP server information from that document has been integrated into this test plan. The PRD file contains useful detail but should be considered reference material, not the authoritative planning document.

---

### Test Scenarios Summary (MVP)

#### Authentication (4 Scenarios)
1. **Valid Login:** Registered user logs in with correct credentials, redirected to My Account
2. **Invalid Credentials:** User enters wrong password, sees "Authentication failed" error
3. **Registration:** New user creates account with valid data, auto-logged in
4. **Logout:** Logged-in user clicks "Sign out," successfully logged out

#### Product Catalog (4 Scenarios)
1. **Browse Category:** Navigate to Women category, verify products load and breadcrumbs display
2. **Filter Products:** Apply size "M" and color "Blue" filters, verify results update
3. **Sort by Price:** Sort products by "Price: Low to High," verify ascending order
4. **Quick View Modal:** Open Quick View for product, verify modal displays details

#### Shopping Cart (4 Scenarios)
1. **Add to Cart:** Add product from detail page, verify cart counter increments
2. **Update Quantity:** Change quantity from 1 to 2 in cart, verify totals update
3. **Remove Product:** Delete product from cart, verify cart empty state
4. **View Cart Summary:** Add 2 products, verify totals calculate correctly (subtotal + shipping = total)

#### Checkout (3 Scenarios)
1. **Complete Checkout:** Full end-to-end flow from cart to order confirmation (registered user)
2. **Address Validation:** Attempt checkout with incomplete address, verify error messages
3. **Payment Selection:** Select different payment methods (Bank wire, Check), verify selection persists

---

### Smoke Test Suite (3 Tests)

**Purpose:** Quick validation before running full suite (~5 minutes)

**Tagged with:** `@smoke` marker

1. `test_valid_login` - Core authentication
2. `test_add_to_cart` - Core shopping flow
3. `test_complete_checkout` - Core checkout flow

**Execution:**
```bash
pytest -m smoke
```

---

### Test Execution Commands

#### Run All Tests
```bash
pytest tests/
```

#### Run Smoke Suite
```bash
pytest -m smoke
```

#### Run Specific Workflow
```bash
pytest tests/auth/
pytest tests/catalog/
pytest tests/cart/
pytest tests/checkout/
```

#### Run Single Test
```bash
pytest tests/auth/test_valid_login.py
```

#### Generate HTML Report
```bash
pytest tests/ --html=_reports/report.html --self-contained-html
```

#### Run with Retry (Handle Flakiness)
```bash
pytest tests/ --reruns 1
```

---

### Coverage Tracking

**Expected Coverage (MVP):**
- **Authentication:** 28.6% (4 of 14 scenarios)
- **Catalog:** 9.8% (4 of 41 scenarios)
- **Cart:** 100% (4 of 4 scenarios)
- **Checkout:** 100% (3 of 3 scenarios)
- **Overall:** 24.2% (15 of 62 scenarios)

**Coverage Calculation:**
Use MCP tool `get_coverage()` to track implemented vs designed scenarios.

---

### Known Limitations (MVP)

1. **Browser Support:** Chrome only (Firefox, Edge deferred to v2.0)
2. **CI/CD:** No pipeline integration in MVP (local execution only)
3. **Parallel Execution:** Sequential execution only (parallel deferred to v2.0)
4. **Cross-Browser Testing:** Not included in MVP
5. **Mobile Testing:** Not included (desktop browser only)
6. **API Testing:** No API tests (UI functional tests only)
7. **Performance Testing:** No load/performance tests
8. **Security Testing:** No penetration or security tests

---

### Next Steps (After Test Plan Approval)

1. **Phase 2: Task Generation**
   - Break down test plan into implementation tasks
   - Create `tasks/tasks-test-plan-py-sel-framework-mcp.md`
   - Identify relevant files for each task

2. **Phase 3: Implementation**
   - Build framework infrastructure (WebInterface, pages, tasks, roles)
   - Implement 15 MVP tests
   - Integrate MCP server
   - Generate test reports

3. **Demo Preparation**
   - Execute smoke suite
   - Generate HTML reports
   - Prepare interview talking points

4. **Future Enhancements (v2.0)**
   - Add deferred test scenarios (47 scenarios)
   - CI/CD integration (GitHub Actions)
   - Cross-browser testing (Firefox, Edge)
   - Parallel execution (pytest-xdist)
   - Allure reporting (rich reports)

---

**Test Plan Status:** Draft - Awaiting Approval

**Last Updated:** 2025-01-11

**Approved By:** [Pending]

**Approval Date:** [Pending]
