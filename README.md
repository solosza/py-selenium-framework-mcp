# Selenium Test Automation Framework

[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.x-green.svg)](https://www.selenium.dev/)
[![MCP](https://img.shields.io/badge/MCP-enabled-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What Is Isagawa QA?

**Isagawa QA is an AI-enforced test execution system that ensures AI-generated tests follow professional QA standards by default.**

Instead of asking AI to "write tests" and hoping it does the right thing, Isagawa **forces correctness** through non-bypassable workflows, quality gates, and encoded domain rules.

AI does the work.
Isagawa ensures the work is done **the right way**.

This is not a suggestion layer.
This is enforced execution.

---

### What This Is

- ✅ An AI-enforced QA execution engine
- ✅ A system for governing *how* AI creates tests
- ✅ A way to encode expert QA standards as rules
- ✅ A replacement for manual QA oversight in AI workflows
- ✅ The first execution pack on a broader enforcement platform

### What This Is NOT

- ❌ A chatbot
- ❌ An AI agent
- ❌ A copilot
- ❌ A prompt library
- ❌ A test recorder
- ❌ A generic automation tool

If you're looking for something that *suggests* tests, this isn't it.
If you need something that **prevents bad tests from existing**, it is.

---

**One-sentence summary:**
_Isagawa QA enforces how AI executes test automation — not just what it produces._

---

A production-ready, 4-layer test automation framework with **AI-powered test generation** via Model Context Protocol (MCP). Built with Python and Selenium. Designed for teams who need structure and manual testers transitioning to automation.

```
Tests → Roles → Tasks → Pages → WebInterface
```

## Framework Overview (How It’s Implemented)

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

### Core Framework
- **4-Layer Architecture** - Clean separation of concerns
- **Page Object Model** - UI changes don't break your tests
- **Role-Based Testing** - Test as different user personas
- **TDD-Ready Structure** - Architecture supports test-driven development workflows
- **Built-in Logging** - Automatic logging at every layer
- **HTML Reports** - Professional test reports out of the box
- **Chrome Support** - Works with Chrome browser (extensible to others)
- **JSON Test Data** - Externalized, maintainable test data

### AI Integration (MCP Server)
- **AI-Powered Test Generation** - Convert requirements to working tests
- **Element Discovery** - AI discovers page elements automatically
- **Framework-Aware Code Generation** - Generated code follows all architecture conventions
- **Agent Agnostic** - Works with Claude Code, Cursor, Windsurf, or any MCP-compatible agent

## Quick Start

Get running in 5 minutes:

### Prerequisites

- Python 3.12 or higher
- Chrome browser installed
- Git
- MCP-compatible AI coding agent (Claude Code, Cursor, or Windsurf) - for AI-powered test generation

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

For AI-powered test generation, see the [MCP Setup](#mcp-setup) section below.

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
│ • Contains user context                                     │
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

For complete architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## MCP Integration: AI-Powered Test Generation

The framework includes an **MCP (Model Context Protocol) server** that enables AI-assisted test generation specifically designed for this framework's architecture.

### What It Does

The end product is a **working test automation script** that tests the supplied requirement. This is achieved through AI orchestration combined with the MCP server:

1. You provide a requirement (e.g., "As a registered user, I want to login")
2. AI orchestrates the MCP tools to generate all necessary components
3. Output: executable Page Objects, Tasks, Roles, and Tests that follow framework conventions

### Why Framework-Specific?

Generic AI code generation often produces code that doesn't follow project conventions. This MCP server understands the 4-layer architecture, ensuring generated code:
- Uses correct layer separation
- Applies proper decorators
- Implements state-check methods for assertions
- Returns appropriate values (self for POMs, None for Tasks/Roles)

### Supported AI Agents

Works with any MCP-compatible AI coding agent:
- **Claude Code** (Anthropic)
- **Cursor** (with MCP support)
- **Windsurf** (Codeium)
- **Any future MCP-compatible agent**

### MCP Setup

The AI-powered test generation requires two MCP servers:
1. **qa-automation** - This framework's test generation tools
2. **playwright** - Browser automation for element discovery

#### Step 1: Install Dependencies

```bash
# Install MCP server dependencies
pip install -r mcp_server/requirements.txt

# Install Node.js (required for Playwright MCP)
# Download from: https://nodejs.org/
```

#### Step 2: Configure MCP Servers

Create or edit `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "python",
      "args": ["mcp_server/server.py"],
      "cwd": "/path/to/py-selenium-framework-mcp/mcp_server"
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp"]
    }
  }
}
```

**Windows users:** Use full paths and forward slashes:
```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "C:/Users/YOUR_USER/AppData/Local/Programs/Python/Python311/python.exe",
      "args": ["D:/path/to/py-selenium-framework-mcp/mcp_server/server.py"],
      "cwd": "D:/path/to/py-selenium-framework-mcp/mcp_server"
    },
    "playwright": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@playwright/mcp"]
    }
  }
}
```

#### Step 3: Verify MCP Servers are Running

In Claude Code, check that both servers are enabled:
```bash
claude mcp list
```

You should see both `qa-automation` and `playwright` listed and enabled.

#### Step 4: Install Skills (Required for AI-Guided Workflow)

The framework includes **Claude Code skills** that guide AI through the 10-step test generation workflow with quality gates. Copy them to your project:

```bash
# Copy skills directory to your project
cp -r .claude/skills /path/to/your/project/.claude/skills
```

**Windows:**
```bash
xcopy /E /I .claude\skills C:\path\to\your\project\.claude\skills
```

The skills include:
- **qa-guidance-layer** - 10-step workflow with quality gates
- **testing** - TDD and test conventions
- **design-decisions** - Architecture decision recording
- **documentation** - Documentation conventions

These skills enable AI to:
- Follow the correct 10-step workflow sequence
- Validate generated code through quality gates
- Self-heal when tool output is incomplete
- Block progression until quality standards are met

#### Common MCP Issues

**Server not starting:**
- Check Python path is correct (run `where python` or `which python`)
- Ensure `mcp_server/server.py` path is absolute
- Check Node.js is installed (`node --version`)

**Playwright MCP not working:**
- Run `npx -y @playwright/mcp` manually to test
- On Windows, use `cmd /c npx` instead of just `npx`

**Tools not appearing:**
- Restart Claude Code after config changes
- Check `.mcp.json` syntax (valid JSON, no trailing commas)

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

### Step 4: Generate Your First Test (AI-Powered)

Use the MCP server with your AI coding agent:

1. Set up MCP server (see MCP Setup section above)
2. Provide a requirement: "As a guest user, I want to browse the Women category"
3. AI orchestrates the 9-step workflow to generate all framework components
4. Run the generated test:
   ```bash
   # Quick run - console output only
   pytest tests/your_test.py -v

   # With HTML report - opens in browser for detailed results
   pytest tests/your_test.py -v --html=reports/report.html --self-contained-html
   ```

### Step 5: Go Deeper

Read [ARCHITECTURE.md](ARCHITECTURE.md) for complete patterns and examples.

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
│       └── utilities/            # Logging, helpers
│
├── tests/                        # Test scenarios
│   ├── conftest.py               # Pytest fixtures
│   ├── data/                     # Test data (JSON)
│   ├── auth/                     # Authentication tests
│   └── catalog/                  # Catalog tests
│
├── mcp_server/                   # MCP AI integration
│   ├── server.py                 # MCP server entry point
│   ├── requirements.txt          # MCP dependencies
│   └── tools/                    # MCP tools
│
├── ARCHITECTURE.md               # Complete architecture reference
└── README.md                     # This file
```

## Configuration

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
framework/resources/data/users.json
```

Example structure:

```json
{
  "registered_user": {
    "email": "test@example.com",
    "password": "SecurePass123!"
  }
}
```

## Running Tests

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

### Getting Help

- **Architecture questions:** Read [ARCHITECTURE.md](ARCHITECTURE.md)
- **Bug reports:** Open an issue with Python version, error message, and steps to reproduce

## Contributing

The 4-layer architecture is framework-agnostic. The current implementation uses Selenium, but the patterns work with any browser automation tool.

**Contribution Ideas:**
- Port to Playwright (Python or TypeScript)
- Port to Cypress
- Add browser support (Firefox, Edge)
- Improve MCP tools

### Code Standards

- Follow the 4-layer architecture
- Locators only in Page Objects
- Tasks/Roles return `None`
- Use `@autologger` decorators
- See [ARCHITECTURE.md](ARCHITECTURE.md) for patterns

## License

**Framework Code (MIT):** The test automation framework (framework/, tests/) is MIT licensed - free to use, modify, and distribute.

**Skills (Proprietary):** The Claude Code skills (.claude/skills/) are proprietary. You may use them with Claude Code but may not redistribute or modify them. See [LICENSE.md](LICENSE.md) for full terms.

## Author

Built by [Alain Ignacio](https://github.com/solosza) as a portfolio project demonstrating QA engineering and test architecture skills.

---

**Questions?** Open an issue or check [ARCHITECTURE.md](ARCHITECTURE.md).
