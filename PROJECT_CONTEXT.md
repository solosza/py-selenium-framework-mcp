# Project Context - py_sel_framework_mcp

**Date:** 2025-01-09
**Status:** Ready for Phase 0 (Design Discussion)

---

## Project Overview

**Goal:** Build a production-grade Python Selenium test automation framework with MCP integration as a portfolio showcase for QA Lead / AI Specialist roles.

**Target Application:** http://www.automationpractice.pl/index.php

**Timeline:** 2 weeks
- Week 1: Framework implementation (architecture, roles, tasks, pages, tests)
- Week 2: MCP server + polish + documentation + demo video

---

## Idea Validation Summary

### Problem Being Solved

**For Job Interviews:**
- Need portfolio project that demonstrates QA Lead-level skills
- Want to showcase AI integration expertise (AI Specialist role requirement)
- Must prove ability to architect production-grade test systems

**For Technical Demonstration:**
- Show enterprise test automation architecture (not toy demos)
- Demonstrate understanding of separation of concerns
- Prove ability to integrate modern AI tooling (MCP)

### Solution Validated

**Approach Chosen:** Build production-grade framework with AI enhancement (not AI-first autonomous testing)

**Why This Approach:**
- Showcases human QA engineering skills (architecture, test design)
- Demonstrates you can build systems, not just use tools
- MCP integration shows forward-thinking about AI+QA
- Differentiates from AI-first POCs flooding GitHub (which are 0-2 star experiments)

---

## Technical Stack

### Core Framework
- **Language:** Python
- **Browser Automation:** Selenium WebDriver
- **Test Runner:** Pytest
- **Reporting:** pytest-html (HTML reports)

### AI Integration
- **MCP Server:** Python-based Model Context Protocol server
- **AI Integration Points:** Claude Code can run tests, analyze failures, suggest fixes

### Target Application
- **Site:** Automation Practice (http://www.automationpractice.pl/)
- **Workflows:** E-commerce (registration, login, search, cart, checkout, account management)

---

## Architecture Overview

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
  ↓
Selenium WebDriver
```

**Based on existing production framework with:**
- 17 roles
- 40+ page objects
- 8 task modules
- Enterprise-proven patterns

**Reference:** See `FRAMEWORK_ARCHITECTURE.md` in the old framework for detailed architecture explanation.

---

## Scope for This Project

### Week 1: Core Framework

**Roles (5-6):**
- Guest User
- Registered User
- Returning Customer
- Admin (if accessible)
- Problem User (edge cases)

**Workflows (15-20 tests):**
- User registration
- Login (valid, invalid, locked)
- Product search
- Product filtering (category, price, color)
- Product details
- Add to cart
- Remove from cart
- Wishlist
- Checkout (guest vs registered)
- Order history
- Account management (addresses, personal info)
- Contact form
- Product reviews

**Framework Components:**
- WebInterface (Selenium wrapper with waits)
- Page Objects (login, home, product list, product details, cart, checkout, account)
- Tasks (common_tasks, ecommerce_tasks)
- Roles (guest_user, registered_user, etc.)
- Pytest fixtures (driver, environment, test data)

### Week 2: MCP Server + Polish

**MCP Server Tools (5-6 commands):**
1. `run_test(test_name, environment)` - Execute specific test
2. `list_tests()` - Show available tests
3. `get_test_report(test_name)` - Get latest HTML report
4. `analyze_failure(test_name)` - Parse error logs, suggest fixes
5. `get_coverage()` - Show which workflows are covered by tests
6. `list_roles()` - Show available user personas

**Documentation:**
- README.md (project overview, setup, usage)
- ARCHITECTURE.md (framework design explanation)
- MCP_INTEGRATION.md (how MCP works with framework)

**Demo:**
- 2-3 min Loom video showing framework + MCP in action
- Screenshots for README

---

## Competitor Analysis

### What Already Exists on GitHub

**MCP + Selenium Projects Found:**
- angiejones/mcp-selenium (TypeScript)
- themindmod/selenium-mcp-server
- decordoba/Selenium-MCP-server (Python)
- fbettag/selenium-mcp (Python + pytest)

**MCP + QA Framework Projects Found:**
- DhruvJadavv/Cypress-AI-MCP-Framework (AI test generation, 0 stars)
- talentinsight/agentic-playwright (Autonomous AI testing, 0 stars)
- NavyaG25/AI-mcp-ui-api-db-automation (POC, 0 stars)
- SagarRuhela1/TestPilot-AI (Autonomous QA agent, 1 star)

**Common Pattern:**
- All are AI-first (AI generates tests autonomously)
- All are POCs (0-2 stars, 2-5 commits)
- All focus on "can AI replace QA engineers?"
- All are experimental/research projects

### How This Project Is Different

| Aspect | Existing Projects | This Project |
|--------|------------------|--------------|
| **Purpose** | AI autonomously generates/runs tests | Professional framework with AI tooling |
| **Architecture** | AI-agent orchestration | Production 4-layer framework |
| **Maturity** | POCs (2-5 commits) | Complete implementation |
| **AI Role** | AI is the product | MCP is a helper tool |
| **Target** | AI researchers | QA Lead interviews |
| **Value** | "Can AI test?" | "Can YOU architect test systems?" |

**Key Differentiator:** This is a human-designed, production-grade framework that ALSO has AI integration. Not an AI experiment.

---

## Interview Talking Points

### What This Project Demonstrates

✅ **QA Engineering Skills:**
- Enterprise test automation architecture
- Separation of concerns (Role/Task/Page/Interface layers)
- Test design for complex workflows
- Maintainable, scalable code patterns

✅ **AI Integration Skills:**
- Understanding of Model Context Protocol
- Building MCP servers in Python
- AI-assisted QA workflows
- Forward-thinking about AI in testing

✅ **Technical Skills:**
- Python + Selenium + Pytest
- Page Object Model patterns
- Fixture-based test setup
- HTML reporting

### Interview Narrative

**Interviewer:** "Walk me through your test automation framework."

**You:** "I built a 4-layer architecture based on enterprise patterns I've used in production. Roles represent user personas, Tasks are business workflows, Page Objects encapsulate UI interactions, and WebInterface wraps Selenium with custom wait strategies. I tested a full e-commerce application with 15+ scenarios covering registration, checkout, search, and account management."

**Interviewer:** "What's this MCP server?"

**You:** "I added an MCP server so AI agents like Claude can interact with my framework - run tests, analyze failures, suggest fixes. It demonstrates I understand emerging AI+QA patterns. But the framework itself is human-designed - I'm not relying on AI to generate tests. I'm using AI as a productivity tool."

**Interviewer:** "Why not use one of those AI test generation frameworks?"

**You:** "Those are research projects exploring 'can AI replace QA engineers?' My goal was to demonstrate I can architect production-grade test systems. The MCP integration shows I'm aware of AI trends, but my value is in designing maintainable test architectures that scale."

---

## Design Decisions Made

### 1. Automation Practice vs Sauce Demo

**Decision:** Automation Practice

**Rationale:**
- Full e-commerce site (realistic complexity)
- 15-20 test scenarios possible (vs 5-6 on Sauce Demo)
- Better showcases framework architecture
- More impressive in interviews
- Sauce Demo too basic for QA Lead role

**Trade-off:** Occasional site slowness/downtime (acceptable for portfolio)

### 2. Selenium vs Playwright

**Decision:** Selenium (for now)

**Rationale:**
- Existing framework uses Selenium (proven architecture)
- Selenium is industry standard (more recognizable in interviews)
- Can migrate to Playwright later if desired

### 3. MCP Server Scope

**Decision:** 5-6 focused tools (not comprehensive automation)

**Rationale:**
- MCP is enhancement, not core value
- Focus on framework quality first
- MCP tools support common workflows (run tests, analyze failures)
- Avoids over-engineering

### 4. Test Coverage

**Decision:** 15-20 tests covering core e-commerce workflows

**Rationale:**
- Enough to demonstrate framework capabilities
- Not so many that it delays completion
- Covers typical QA interview questions ("How do you test checkout flow?")

---

## Next Steps

### Phase 0: Design Discussion

**What to Design:**

1. **Framework Structure**
   - Directory layout
   - Module organization
   - Naming conventions

2. **Test Scenarios**
   - Which workflows to test
   - Test data management
   - Environment configuration

3. **MCP Integration Points**
   - Which tools to build
   - How MCP interacts with framework
   - Tool input/output formats

4. **Reporting & Observability**
   - HTML reports
   - Logs
   - Screenshots on failure

**NOT Designing (Trust Claude on Implementation):**
- How to implement Selenium waits
- Specific locator strategies
- Database schemas
- API details

**Output:** Design decisions documented, ready for Phase 1 (PRD)

---

## Reference Materials

**Existing Framework:**
- Location: `C:\Users\solos\OneDrive\Documents\nakupuna\framework_example_for_ai\`
- Architecture Doc: `FRAMEWORK_ARCHITECTURE.md` (created, reference for patterns)

**4D Framework Process Docs:**
- Located in `docs/` folder of this project
- `0-design-discussion-v2.md`
- `1-create-prd-v2.md`
- `2-generate-tasks-v2.md`
- `3-process-task-list-v2.md`

**Target Application:**
- URL: http://www.automationpractice.pl/index.php
- Type: E-commerce demo site
- Features: Registration, login, product catalog, cart, checkout, account management

---

## Questions to Address in Phase 0

1. **Framework Structure:** Exact directory layout and file organization?
2. **Environment Management:** How to handle different environments (local vs CI)?
3. **Test Data:** JSON files? Python fixtures? Faker library?
4. **Roles:** Exact list of user personas to implement?
5. **Workflows:** Priority order for test scenario implementation?
6. **MCP Tools:** Specific input/output formats for each tool?
7. **Reporting:** What goes in HTML reports? Screenshots? Logs?
8. **CI/CD:** GitHub Actions integration? (Nice to have)

---

## Success Criteria

**Week 1 Complete:**
- ✅ Framework structure implemented
- ✅ 3-5 roles working
- ✅ 10-15 tests passing
- ✅ HTML reports generated
- ✅ Code is clean, documented, follows patterns

**Week 2 Complete:**
- ✅ MCP server functional (5-6 tools)
- ✅ README, ARCHITECTURE docs complete
- ✅ Demo video created (2-3 min)
- ✅ GitHub repo ready to share
- ✅ Ready to discuss in interviews

**Interview Ready:**
- ✅ Can explain architecture in 2 minutes
- ✅ Can live demo a test run
- ✅ Can show MCP integration
- ✅ Can walk through code structure
- ✅ Can discuss design decisions

---

## Resume This Session

**When you start Phase 0 in new Claude Code session:**

Say: **"Read PROJECT_CONTEXT.md and start Phase 0 Design Discussion"**

Claude will have all the context from our validation conversation and can begin designing the framework architecture with you.

---

**Last Updated:** 2025-01-09
**Next Phase:** Phase 0 - Design Discussion
