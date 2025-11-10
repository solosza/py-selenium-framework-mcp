# Python Selenium Test Automation Framework with MCP Integration

A production-grade test automation framework showcasing enterprise-level architecture and AI integration through Model Context Protocol (MCP).

## Overview

This project demonstrates QA Lead-level skills in test framework architecture, combined with forward-thinking AI integration. Built with Python, Selenium, and Pytest, it features a clean 4-layer architecture for maintainable, scalable test automation.

**Target Application:** [Automation Practice](http://www.automationpractice.pl/) - E-commerce demo site

**Status:** 🚧 In Development - Phase 0 (Design Discussion)

## Architecture

### 4-Layer Framework Design

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

**Why This Architecture?**
- **Separation of Concerns:** Each layer has a single responsibility
- **Maintainability:** Changes to UI don't cascade through entire codebase
- **Reusability:** Tasks and page objects shared across multiple tests
- **Scalability:** Easy to add new workflows without touching existing code

## Technology Stack

### Core Framework
- **Python 3.x** - Programming language
- **Selenium WebDriver** - Browser automation
- **Pytest** - Test runner and fixture management
- **pytest-html** - HTML test reports

### AI Integration
- **Model Context Protocol (MCP)** - AI agent interface
- **Python MCP Server** - Custom tools for test automation workflows

### Supporting Libraries
- **python-dotenv** - Environment configuration
- **Faker** - Dynamic test data generation

## Features

### Test Coverage (Planned)
- ✅ User authentication (login, registration, logout)
- ✅ Product catalog (search, browse, filter)
- ✅ Shopping cart workflows
- ✅ Checkout process (guest and registered users)
- ✅ Account management
- ✅ Order history

### Framework Features
- **Robust Error Handling:** Automatic retry logic with exponential backoff
- **Smart Waiting:** Implicit and explicit waits configured per environment
- **Screenshot Capture:** Automatic screenshots on test failure
- **Detailed Reporting:** HTML reports with screenshots, logs, and execution details
- **Test Data Management:** Hybrid approach (JSON files + Faker for dynamic data)
- **Environment Configuration:** `.env` file for easy environment switching

### MCP Integration (Planned - Week 2)
AI-assisted testing workflows through custom MCP server:
- Run specific tests via natural language commands
- Analyze test failures and suggest fixes
- Generate test coverage reports
- List available test scenarios and roles

## Project Structure

```
py_sel_framework_mcp/
├── framework/              # Framework code (reusable)
│   ├── interfaces/
│   │   └── web_interface.py
│   ├── pages/             # Page Object Model
│   │   ├── common/
│   │   ├── catalog/
│   │   ├── cart/
│   │   └── checkout/
│   ├── tasks/             # Business workflow implementations
│   ├── roles/             # User persona definitions
│   └── resources/
│       ├── config/        # Environment configurations
│       ├── data/          # Test data (JSON)
│       └── utilities/     # Helpers (logging, screenshots, data generation)
├── tests/                 # Test scenarios
│   ├── conftest.py        # Pytest fixtures
│   ├── authentication/
│   ├── catalog/
│   ├── cart/
│   └── checkout/
├── mcp_server/            # MCP integration (Week 2)
│   ├── server.py
│   └── tools/
├── docs/                  # Process documentation
│   └── 4D Framework process docs
├── tasks/                 # PRDs and task lists
├── CLAUDE.md              # AI assistant context and project guidelines
├── PROJECT_CONTEXT.md     # Idea validation and project scope
└── README.md              # This file
```

## Installation & Setup

**Coming soon after Phase 1 (Test Plan generation)**

## Usage

**Coming soon after Phase 3 (Implementation)**

## Development Process

This project follows the **4D Framework** (Design → Define → Divide → Deliver):

1. **Phase 0 - Design:** Requirements gathering and test planning (current phase)
2. **Phase 1 - Define:** Formal test plan creation with user stories and acceptance criteria
3. **Phase 2 - Divide:** Break test plan into implementation tasks
4. **Phase 3 - Deliver:** Execute tasks and build framework

See `docs/` for detailed process documentation.

## Why This Project?

### Differentiators
This is NOT another "AI generates tests autonomously" POC. This is a human-designed, production-grade framework that demonstrates:

- **QA Engineering Skills:** Enterprise test architecture, not toy demos
- **System Design:** Ability to architect maintainable, scalable test systems
- **AI Integration:** Forward-thinking approach to AI in QA (MCP as a tool, not a replacement)
- **Production Readiness:** Follows industry best practices from day one

### Portfolio Showcase
Built for QA Lead and AI Specialist role interviews, this project proves:
- Deep understanding of test automation architecture
- Ability to build frameworks from scratch (not just use existing tools)
- Knowledge of modern AI integration patterns (MCP)
- Clean code, documentation, and professional git workflow

## Timeline

- **Week 1:** Core framework implementation (architecture, roles, tasks, pages, tests)
- **Week 2:** MCP server integration, documentation, demo video

## Contributing

This is a portfolio project and not accepting contributions. However, feel free to fork and adapt for your own use.

## License

MIT License - See [LICENSE](LICENSE) for details

## Author

Built by [solosza](https://github.com/solosza) as a portfolio demonstration project.

## Acknowledgments

- Framework architecture inspired by enterprise patterns from production PeopleSoft test automation
- Target application provided by [Automation Practice](http://www.automationpractice.pl/)
- Built using the 4D Framework process (see `CLAUDE.md`)

---

**Status Updates:**
- 2025-01-10: Repository initialized, Phase 0 in progress
