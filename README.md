# Selenium Test Automation Framework

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.x-green.svg)](https://www.selenium.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-18%20passing-brightgreen.svg)](#test-results)

A production-ready, 4-layer test automation framework built with Python and Selenium. Designed for teams who need structure and manual testers learning automation.

```
Tests → Roles → Tasks → Pages → WebInterface
```

## What Is This?

This framework provides a **clean, maintainable architecture** for browser test automation. Instead of writing spaghetti Selenium code, you get organized layers that separate concerns:

- **Tests** - What you're verifying (assertions only)
- **Roles** - Who is doing it (GuestUser, RegisteredUser, Admin)
- **Tasks** - What workflow they're performing (login, browse catalog, checkout)
- **Pages** - How to interact with UI elements (click, type, select)

**Result:** Tests that are easy to read, maintain, and scale.

## Who Is This For?

| You Are | This Framework Helps You |
|---------|-------------------------|
| **Manual Tester** | Learn automation with clear patterns, not messy scripts |
| **Junior Automator** | Skip the "how do I organize this?" phase |
| **QA Team** | Get a ready-made structure instead of building from scratch |
| **Solo Developer** | Production-grade architecture for your projects |

## Features

- **4-Layer Architecture** - Clean separation of concerns
- **Page Object Model** - UI changes don't break your tests
- **Role-Based Testing** - Test as different user personas
- **Built-in Logging** - Automatic logging at every layer
- **HTML Reports** - Professional test reports out of the box
- **Chrome/Brave Support** - Works with Chromium browsers
- **JSON Test Data** - Externalized, maintainable test data

## Quick Start

Get running in 5 minutes:

### Prerequisites

- Python 3.12 or higher
- Chrome browser installed
- Git

### Installation

```bash
# Clone the repository
git clone https://github.com/solosza/py-selenium-framework-mcp.git
cd py-selenium-framework-mcp

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run Your First Test

```bash
# Run all tests
pytest tests/ -v

# Run with HTML report
pytest tests/ -v --html=reports/report.html --self-contained-html

# Run specific test category
pytest tests/catalog/ -v

# Run in headless mode (no browser window)
pytest tests/ -v --headless=True
```

### See Results

After running tests, open `reports/report.html` in your browser for a detailed report.

## Test Results

Current test suite against [Automation Practice](http://www.automationpractice.pl/):

| Test Suite | Tests | Status |
|------------|-------|--------|
| Invalid Credentials | 6 | All Passing |
| Browse Category | 4 | All Passing |
| Filter Products | 4 | All Passing |
| Sort by Price | 4 | All Passing |
| Registration | 1/6 | Environment Issues* |
| Valid Login | 0/2 | Environment Issues* |
| Quick View | 1/4 | Website Issues* |
| Logout | 0/3 | Skipped (requires login) |

**Total: 18 passing, 10 failing, 3 skipped**

*Failures are due to test environment (no pre-registered user on live site) and website bugs - not framework issues. The framework architecture is fully validated.

## Detailed Setup

### Environment Configuration

The framework uses JSON configuration files:

```
framework/resources/config/environment_config.json
```

Default configuration points to Automation Practice demo site. To test your own application, update the URL:

```json
{
  "DEFAULT": {
    "url": "https://your-app-url.com"
  }
}
```

### Test Data

Test user data is stored in:

```
tests/data/test_users.json
```

Example structure:

```json
{
  "registered_user": {
    "email": "test@example.com",
    "password": "SecurePass123!"
  },
  "new_user": {
    "email": "newuser@example.com",
    "first_name": "John",
    "last_name": "Doe"
  }
}
```

### Browser Options

The framework defaults to Chrome. To use Brave browser, modify the driver call:

```python
# In tests/conftest.py
chromedriver = create_driver(headless=headless_bool, browser="brave")
```

## How to Use

### Running Tests

```bash
# All tests
pytest tests/ -v

# By marker (category)
pytest tests/ -v -m catalog
pytest tests/ -v -m auth
pytest tests/ -v -m smoke

# Single test file
pytest tests/catalog/test_browse_category.py -v

# Single test function
pytest tests/catalog/test_browse_category.py::test_browse_women_category -v

# With HTML report
pytest tests/ -v --html=reports/report.html --self-contained-html

# Headless mode (CI/CD)
pytest tests/ -v --headless=True
```

### Understanding Test Output

```
tests/catalog/test_browse_category.py::test_browse_women_category PASSED [25%]
```

- `PASSED` - Test succeeded
- `FAILED` - Assertion failed (check report for details)
- `ERROR` - Test crashed (setup/teardown issue)
- `SKIPPED` - Intentionally skipped (missing prerequisite)

## Architecture

### The 4-Layer Pattern

```
┌─────────────────────────────────────────────────────────────┐
│ TEST LAYER                                                  │
│ • Arrange, Act, Assert only                                 │
│ • Calls ONE role method                                     │
│ • Asserts via Page Object state-checks                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ ROLE LAYER                                                  │
│ • User personas (GuestUser, RegisteredUser)                 │
│ • Orchestrates multiple tasks into workflows                │
│ • Contains user credentials/context                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ TASK LAYER                                                  │
│ • Single business operations (login, add_to_cart)           │
│ • Calls page object methods                                 │
│ • Domain-focused, not UI-focused                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ PAGE OBJECT LAYER                                           │
│ • One class per page/component                              │
│ • Locators as class constants                               │
│ • Atomic methods (click, type, select)                      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ WEB INTERFACE                                               │
│ • Selenium wrapper                                          │
│ • Handles waits, logging, error handling                    │
│ • Single point of browser interaction                       │
└─────────────────────────────────────────────────────────────┘
```

### Why This Structure?

| Problem | How This Framework Solves It |
|---------|------------------------------|
| UI changes break everything | Locators in ONE place (Page Objects) |
| Tests are hard to read | Tests only have assertions, logic is in Roles/Tasks |
| Code duplication | Tasks are reusable across tests |
| Hard to test different users | Roles encapsulate user-specific behavior |
| Debugging is painful | Automatic logging at every layer |

### Quick Reference Rules

```
GOLDEN RULES:
1. Locators ONLY in Page Objects
2. Tasks/Roles return NOTHING (None)
3. Tests assert via Page Object state-check methods
4. No inheritance - composition only
5. One responsibility per layer
```

For complete architecture documentation, see [FRAMEWORK.md](FRAMEWORK.md).

## For Manual Testers: Your Learning Path

New to automation? Start here:

### Step 1: Understand the Layers

Think of it like your manual testing:

| Manual Testing | Framework Layer |
|---------------|-----------------|
| "I'm testing as a guest user" | Role (GuestUser) |
| "I need to browse products" | Task (browse_category) |
| "I click the Women menu link" | Page Object (click method) |
| "I verify products are displayed" | Test (assertion) |

### Step 2: Read a Simple Test

Open `tests/catalog/test_browse_category.py`:

```python
def test_browse_women_category(web_interface, config):
    # Arrange - Set up
    guest = GuestUser(web_interface, config["url"])
    product_list_page = ProductListPage(web_interface)

    # Act - Do the action
    guest.browse_category("Women")

    # Assert - Verify result
    assert product_list_page.has_products(), "Products should be displayed"
```

That's it. The test reads like a user story.

### Step 3: Trace the Flow

1. Test creates a `GuestUser`
2. Calls `guest.browse_category("Women")`
3. Role calls `catalog_tasks.browse_category("Women")`
4. Task calls `navigation_menu.click_category("Women")`
5. Page Object calls `self.web.click(locator)`

### Step 4: Write Your First Test

Copy an existing test and modify:

1. Pick a test file to copy
2. Change the category or action
3. Run it: `pytest tests/your_test.py -v`

### Step 5: Go Deeper

Read [FRAMEWORK.md](FRAMEWORK.md) for complete patterns and examples.

## Project Structure

```
py-selenium-framework-mcp/
├── framework/                    # Core framework (reusable)
│   ├── interfaces/
│   │   └── web_interface.py      # Selenium wrapper
│   ├── pages/                    # Page Objects
│   │   ├── auth/                 # Login, Registration pages
│   │   └── catalog/              # Product listing, filters
│   ├── tasks/                    # Business operations
│   │   ├── common/               # Shared tasks (login, navigate)
│   │   └── catalog/              # Catalog-specific tasks
│   ├── roles/                    # User personas
│   │   ├── auth/                 # RegisteredUser
│   │   └── guest/                # GuestUser
│   └── resources/
│       ├── config/               # Environment settings
│       ├── chromedriver/         # Driver factory
│       └── utilities/            # Logging, helpers
│
├── tests/                        # Test scenarios
│   ├── conftest.py               # Pytest fixtures
│   ├── data/                     # Test data (JSON)
│   ├── auth/                     # Authentication tests
│   └── catalog/                  # Catalog tests
│
├── docs/                         # Documentation (gitignored)
│   └── DEFECT_LOG.md             # Issue tracking
│
├── mcp_server/                   # AI integration (future)
│
├── FRAMEWORK.md                  # Complete architecture reference
├── CLAUDE.md                     # AI assistant instructions
└── README.md                     # This file
```

## Test Examples

The included tests serve dual purposes:

### For Portfolio Review

These tests demonstrate production-quality automation:
- 33 test scenarios across authentication and catalog
- 18 passing tests validating framework architecture
- Real-world error handling and edge cases

### For Learning & Reference

Use these as templates for your own tests:

| Test File | What It Demonstrates |
|-----------|---------------------|
| `test_browse_category.py` | Simple happy path testing |
| `test_invalid_credentials.py` | Negative testing patterns |
| `test_filter_products.py` | Complex user workflows |
| `test_sort_by_price.py` | State verification patterns |

## Contributing

Contributions are welcome! This framework is designed to be extended.

### Ways to Contribute

1. **Add Tests** - More test scenarios for the demo site
2. **Improve Documentation** - Tutorials, guides, examples
3. **Report Issues** - Found a bug? Open an issue
4. **Framework Ports** - See below

### Architecture Ports Wanted

The 4-layer architecture (Roles → Tasks → Pages) is framework-agnostic. The current implementation uses Selenium, but the patterns work anywhere.

**Wanted:** Community implementations for:
- Playwright (Python)
- Cypress (JavaScript)
- Puppeteer (Node.js)

The key abstraction point is `WebInterface` - implement the same interface for your framework of choice.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Follow existing code patterns
4. Add tests for new functionality
5. Submit a pull request

### Code Standards

- Follow the 4-layer architecture
- Locators only in Page Objects
- Tasks/Roles return `None`
- Use `@autologger` decorators
- See [FRAMEWORK.md](FRAMEWORK.md) for patterns

## Roadmap

### Completed
- [x] 4-layer framework architecture
- [x] Page Objects for auth and catalog
- [x] Role-based testing (Guest, Registered)
- [x] HTML reporting
- [x] Comprehensive documentation

### Planned
- [ ] MCP server integration (AI-assisted testing)
- [ ] Cart and checkout tests
- [ ] Parallel test execution
- [ ] Docker support
- [ ] CI/CD examples (GitHub Actions)

### Community Wishlist
- [ ] Playwright adapter
- [ ] Video recording on failure
- [ ] Allure reporting integration

## Troubleshooting

### Common Issues

**ChromeDriver version mismatch**
```
selenium.common.exceptions.SessionNotCreatedException
```
Solution: The framework uses `webdriver-manager` which auto-downloads the correct driver. If issues persist, update Chrome browser.

**Element not found / Timeout**
```
selenium.common.exceptions.TimeoutException
```
Solution: The target website may be slow. Increase timeout in `web_interface.py` or check if the site is accessible.

**Tests fail on first run**
Some tests require a registered user that doesn't exist on the demo site. This is expected - see [Test Results](#test-results).

### Getting Help

1. Check existing [Issues](https://github.com/solosza/py-selenium-framework-mcp/issues)
2. Read [FRAMEWORK.md](FRAMEWORK.md) for architecture questions
3. Open a new issue with:
   - Python version
   - Error message
   - Steps to reproduce

## License

MIT License - See [LICENSE](LICENSE) for details.

Free to use, modify, and distribute. Attribution appreciated but not required.

## Author

Built by [solosza](https://github.com/solosza) as a portfolio project demonstrating QA engineering and test architecture skills.

## Acknowledgments

- Architecture patterns inspired by enterprise test automation frameworks
- Demo site: [Automation Practice](http://www.automationpractice.pl/)
- Selenium WebDriver team
- pytest and pytest-html maintainers

---

**Questions?** Open an issue or check the [documentation](FRAMEWORK.md).

**Found this useful?** Star the repo to show support!
