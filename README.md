# AI-Assisted QA Automation Framework

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Selenium](https://img.shields.io/badge/selenium-4.x-green.svg)](https://www.selenium.dev/)
[![MCP](https://img.shields.io/badge/MCP-enabled-purple.svg)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-grade Python Selenium framework with **AI-powered test generation**. Describe what you want to test in plain English, and AI generates complete, maintainable test automation code.

---

## What You Get

- **AI generates tests from requirements** - Describe a user story, get working test code
- **Production-grade architecture** - 4-layer pattern (Role > Task > Page > WebInterface) that scales
- **Consistent code patterns** - Every generated test follows the same structure
- **Works with your AI tool** - Claude Code, Cursor, Windsurf, or any MCP-compatible agent

---

## How It Works

```
1. You describe: "As a registered user, I want to login and view my account"
2. AI discovers page elements automatically (via Playwright)
3. AI generates: Page Objects, Tasks, Roles, and Tests
4. You run: pytest tests/your_test.py
```

The generated code follows strict architectural patterns - no spaghetti, no "every engineer writes it differently" problems.

---

## Prerequisites

Before installing, ensure you have:

| Requirement | Version | Check Command | Download |
|-------------|---------|---------------|----------|
| Python | 3.11+ | `python --version` | [python.org](https://www.python.org/downloads/) |
| Node.js | 18+ | `node --version` | [nodejs.org](https://nodejs.org/) |
| Chrome | Latest | Open Chrome > Help > About | [google.com/chrome](https://www.google.com/chrome/) |
| Git | Any | `git --version` | [git-scm.com](https://git-scm.com/) |
| MCP-compatible AI | - | - | Claude Code, Cursor, or Windsurf |

### AI Agent Options

This framework requires an MCP-compatible AI coding agent:

| Agent | MCP Support | Notes |
|-------|-------------|-------|
| [Claude Code](https://claude.ai/download) | Native | Recommended - best MCP integration |
| [Cursor](https://cursor.sh/) | Via config | Requires MCP configuration |
| [Windsurf](https://codeium.com/windsurf) | Via config | Requires MCP configuration |

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/isagawa-qa/isagawa-qa.git
cd py-selenium-framework-mcp
```

### Step 2: Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Python Dependencies

```bash
# Core framework dependencies
pip install -r requirements.txt

# MCP server dependencies
pip install -r mcp_server/requirements.txt
```

### Step 4: Verify Installation

```bash
# Check Selenium is installed
python -c "import selenium; print(f'Selenium {selenium.__version__} installed')"

# Check pytest is installed
pytest --version

# Check MCP dependencies
python -c "import mcp; print('MCP SDK installed')"
```

---

## MCP Server Setup

The framework uses two MCP servers:
1. **qa-automation** - Generates test automation code
2. **playwright** - Discovers page elements via browser automation

### Step 1: Locate Your Python Path

**Windows:**
```powershell
where python
# Example output: C:\Users\YourName\AppData\Local\Programs\Python\Python311\python.exe
```

**macOS / Linux:**
```bash
which python3
# Example output: /usr/local/bin/python3
```

### Step 2: Create MCP Configuration

Create or edit `.mcp.json` in your project root:

**Windows Configuration:**
```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "C:/Users/YOUR_USERNAME/AppData/Local/Programs/Python/Python311/python.exe",
      "args": ["D:/path/to/py-selenium-framework-mcp/mcp_server/server.py"],
      "cwd": "D:/path/to/py-selenium-framework-mcp/mcp_server"
    },
    "playwright": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@playwright/mcp@latest"]
    }
  }
}
```

**macOS / Linux Configuration:**
```json
{
  "mcpServers": {
    "qa-automation": {
      "command": "/usr/local/bin/python3",
      "args": ["/path/to/py-selenium-framework-mcp/mcp_server/server.py"],
      "cwd": "/path/to/py-selenium-framework-mcp/mcp_server"
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp@latest"]
    }
  }
}
```

**Important:**
- Replace `YOUR_USERNAME` with your actual Windows username
- Replace `/path/to/` with your actual project path
- Use **forward slashes** (`/`) even on Windows
- Use **absolute paths** for reliability

### Step 3: Install Playwright Browser

The Playwright MCP server needs a browser installed:

```bash
npx playwright install chromium
```

### Step 4: Verify MCP Servers

**Claude Code:**
```bash
# List configured servers
claude mcp list

# You should see both qa-automation and playwright listed
```

**Cursor / Windsurf:**
- Open settings/preferences
- Navigate to MCP configuration
- Verify both servers are listed and enabled

### Step 5: Test MCP Connection

In your AI agent, ask:
```
What MCP tools are available?
```

You should see tools like:
- `mcp__qa-automation__generate_page_object`
- `mcp__qa-automation__generate_task`
- `mcp__qa-automation__generate_role`
- `mcp__playwright__browser_navigate`
- `mcp__playwright__browser_snapshot`

---

## Quick Start: Generate Your First Test

### Option A: Use the Workflow Command (Recommended)

In Claude Code, run:
```
/qa-workflow
```

Then provide your requirement:
```
As a guest user, I want to browse the Women category on automationpractice.pl
```

The AI will:
1. Navigate to the site and discover elements
2. Generate Page Objects, Tasks, Roles, and Tests
3. Save files to the correct locations
4. Run the test

### Option B: Manual Conversation

Start a conversation with your AI agent:

```
I want to create a test for this requirement:

As a registered user, I want to login to automationpractice.pl

URL: http://www.automationpractice.pl/index.php?controller=authentication

Use static credentials from tests/data/test_users.json
```

---

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/auth/test_login.py -v
```

### Run with HTML Report
```bash
pytest tests/ -v --html=tests/_reports/report.html --self-contained-html
```

### Run in Headless Mode (No Browser Window)
```bash
pytest tests/ -v --headless
```

### View Test Report
After running with `--html`, open `tests/_reports/report.html` in your browser.

---

## Architecture: The 4-Layer Pattern

Generated code follows a strict 4-layer architecture:

```
┌─────────────────────────────────────────────────────────────┐
│  TEST                                                        │
│  • Arrange, Act, Assert                                      │
│  • Calls ONE role method                                     │
│  • Asserts via Page Object state methods                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  ROLE                                                        │
│  • User personas (GuestUser, RegisteredUser)                 │
│  • Orchestrates multiple tasks into workflows                │
│  • Example: login > browse > add to cart > checkout          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  TASK                                                        │
│  • Single business operations (login, add_to_cart)           │
│  • Calls page object methods                                 │
│  • Domain-focused, not UI-focused                            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PAGE OBJECT                                                 │
│  • One class per page/component                              │
│  • Contains all locators                                     │
│  • Atomic methods: click, type, select                       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  WEB INTERFACE                                               │
│  • Selenium wrapper                                          │
│  • Handles waits, logging, screenshots                       │
│  • Single point of browser interaction                       │
└─────────────────────────────────────────────────────────────┘
```

### Why This Matters

| Problem | How This Framework Solves It |
|---------|------------------------------|
| UI changes break tests | Locators in ONE place (Page Objects) |
| Tests are hard to read | Tests only assert, logic is in Roles/Tasks |
| Code duplication | Tasks are reusable across tests |
| Different coding styles | AI generates consistent patterns |
| Hard to onboard new team members | Clear layer separation, same patterns everywhere |

### Golden Rules

```
1. Locators ONLY in Page Objects
2. Tasks/Roles return NOTHING (None)
3. Tests assert via Page Object state-check methods
4. No inheritance - composition only
5. One responsibility per layer
```

---

## Project Structure

```
py-selenium-framework-mcp/
├── framework/                    # Reusable framework code
│   ├── interfaces/
│   │   └── web_interface.py      # Selenium wrapper
│   ├── pages/                    # Page Objects (UI elements)
│   │   ├── auth/                 # Login, registration pages
│   │   └── catalog/              # Product pages
│   ├── tasks/                    # Business operations
│   │   └── auth/                 # Login, logout tasks
│   ├── roles/                    # User personas
│   │   └── auth/                 # RegisteredUser, GuestUser
│   └── resources/
│       ├── config/               # Environment settings
│       └── utilities/            # Logging, helpers
│
├── tests/                        # Test files
│   ├── conftest.py               # Pytest fixtures
│   ├── data/                     # Test data (JSON)
│   │   └── test_users.json       # User credentials
│   ├── auth/                     # Authentication tests
│   └── catalog/                  # Catalog tests
│
├── mcp_server/                   # AI integration
│   ├── server.py                 # MCP server entry
│   ├── tools/                    # Code generation tools
│   └── requirements.txt          # MCP dependencies
│
└── .mcp.json                     # MCP configuration
```

---

## Configuration

### Environment Config

Edit `framework/resources/config/environment_config.json`:

```json
{
  "DEFAULT": {
    "url": "http://www.automationpractice.pl/index.php",
    "browser": "chrome",
    "headless": false,
    "implicit_wait": 10
  }
}
```

### Test Users

Edit `tests/data/test_users.json`:

```json
{
  "registered_user": {
    "email": "your-test-email@example.com",
    "password": "YourTestPassword123"
  }
}
```

---

## Test Data Strategies

When generating tests that require credentials, you have three options:

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| **Static** | Use existing account from `tests/data/test_users.json` | Login-only tests |
| **Dynamic** | Register fresh user, save for later tests | Registration flows |
| **Self-contained** | Register and use within same test | Independent tests |

Tell the AI which strategy you want when providing your requirement.

---

## Workflow Naming

To avoid overwriting files from previous test runs, use unique workflow names:

```
# First test on ParaBank
workflow_name: "parabank"

# Subsequent tests
workflow_name: "parabank2"
workflow_name: "parabank_login"
workflow_name: "parabank_transfer"
```

Files are generated in:
- `framework/pages/{workflow_name}/`
- `framework/tasks/{workflow_name}/`
- `framework/roles/{workflow_name}/`
- `tests/{workflow_name}/`

---

## Troubleshooting

### MCP Server Not Starting

**Symptom:** AI agent can't find MCP tools

**Solutions:**
1. Check Python path is correct:
   ```bash
   # Windows
   where python

   # macOS/Linux
   which python3
   ```

2. Verify paths in `.mcp.json` are absolute and use forward slashes

3. Restart your AI agent after config changes

4. Test MCP server manually:
   ```bash
   python mcp_server/server.py
   # Should start without errors
   ```

### Playwright MCP Not Working

**Symptom:** Element discovery fails, browser doesn't open

**Solutions:**
1. Install Playwright browser:
   ```bash
   npx playwright install chromium
   ```

2. Test Playwright MCP manually:
   ```bash
   npx -y @playwright/mcp@latest
   ```

3. Windows users: Ensure using `cmd /c npx` in `.mcp.json`

### ChromeDriver Version Mismatch

**Symptom:** `SessionNotCreatedException` error

**Solution:** The framework uses `webdriver-manager` which auto-downloads the correct driver. Update Chrome browser to latest version.

### Element Not Found / Timeout

**Symptom:** `TimeoutException` during test run

**Solutions:**
1. Increase timeout in `framework/resources/config/environment_config.json`
2. Check if target website is accessible
3. Verify locators match current page structure

### Import Errors

**Symptom:** `ModuleNotFoundError` when running tests

**Solutions:**
1. Ensure virtual environment is activated
2. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r mcp_server/requirements.txt
   ```

---

## For Manual Testers: Your Learning Path

New to automation? Here's how this maps to manual testing:

| Manual Testing | Framework Layer |
|---------------|-----------------|
| "I'm testing as a guest user" | Role (GuestUser) |
| "I need to browse products" | Task (browse_category) |
| "I click the Women menu link" | Page Object (click method) |
| "I verify products are displayed" | Test (assertion) |

### Read a Simple Test

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

The test reads like a user story.

---

## Support

- **Issues:** [GitHub Issues](https://github.com/isagawa-qa/isagawa-qa/issues)
- **Architecture Details:** See `FRAMEWORK.md`

---

## License

**Framework Code (MIT):** Free to use, modify, and distribute.

See [LICENSE.md](LICENSE.md) for full terms.

---

Built for QA engineers who want AI to write tests the right way.
