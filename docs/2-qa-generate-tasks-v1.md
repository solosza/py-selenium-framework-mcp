# Phase 2: Generate Tasks from Test Plan (QA 4D Framework)

**Version:** 1.0.0
**Last Updated:** 2025-01-11
**Status:** Active

---

## Goal

To guide an AI assistant in creating a detailed, step-by-step task list in Markdown format based on an existing Test Plan. The task list should guide a QA engineer through test framework implementation and test creation.

---

## Output

- **Format:** Markdown (`.md`)
- **Location:** `/tasks/`
- **Filename:** `tasks-test-plan-{project-name}.md` (e.g., `tasks-test-plan-py-sel-framework-mcp.md`)

---

## Process

### 1. Receive Test Plan Reference
The user points the AI to a specific Test Plan file (from Phase 1)

---

### 2. Analyze Test Plan
The AI reads and analyzes:
- Test scope (MVP scenarios)
- Test approach (execution strategy)
- Test environment setup
- Test data strategy
- Framework architecture decisions (from Phase 0)

**Key Inputs:**
- Test Plan document (`tasks/test-plan-{project-name}.md`)
- Phase 0 Test Design document (`docs/0-test-design-{project-name}.md`)
- Existing test framework structure (if any)

---

### 3. Assess Current State
Review the existing test framework (if any) to understand:
- Existing infrastructure (WebInterface, base classes, utilities)
- Framework patterns and conventions
- Existing page objects, task methods, roles
- Configuration management approach
- Test data management approach
- Fixtures and conftest.py setup

**For New Projects:** Identify what needs to be built from scratch
**For Existing Projects:** Identify what can be reused or needs modification

---

### 4. Phase 1: Generate Parent Tasks
Based on Test Plan and Phase 0 design, create high-level tasks.

**Typical Parent Task Structure:**

#### Option A: Layer-Based Breakdown (Framework-Heavy Projects)
1. **Foundation Layer** - Base infrastructure (WebInterface, config, utilities)
2. **Page Objects Layer** - All page object classes
3. **Task Methods Layer** - All task/workflow classes
4. **Role Layer** - User personas/roles (if applicable)
5. **Test Scenarios Layer** - Actual test files
6. **MCP Integration** - MCP server tools (if applicable)

#### Option B: Workflow-Based Breakdown (Test-Heavy Projects)
1. **Foundation Setup** - Base infrastructure + config
2. **Authentication Workflow** - Auth pages + tasks + tests
3. **Catalog Workflow** - Catalog pages + tasks + tests
4. **Cart Workflow** - Cart pages + tasks + tests
5. **Checkout Workflow** - Checkout pages + tasks + tests
6. **MCP Integration** - MCP server tools (if applicable)

**Choose based on:**
- Layer-based: New framework from scratch, focus on architecture
- Workflow-based: Adding tests to existing framework, focus on scenarios

Present parent tasks to user and inform:
**"I have generated the high-level tasks based on the Test Plan. Ready to generate the sub-tasks? Respond with 'Go' to proceed."**

---

### 5. Wait for Confirmation
Pause and wait for user to respond with **"Go"**

---

### 6. Phase 2: Generate Sub-Tasks
Once user confirms, break down each parent task into smaller, actionable sub-tasks.

**Sub-Task Categories:**

#### For Infrastructure Tasks
- Create file/class structure
- Implement core methods
- Add configuration management
- Create utility functions
- Write unit tests (if testing framework code)

#### For Page Object Tasks
- Identify page elements/locators
- Implement element interaction methods
- Implement verification/assertion methods
- Add wait strategies
- Document page object usage

#### For Task Method Tasks
- Implement workflow methods
- Chain page object interactions
- Add business logic
- Handle error cases
- Document task usage

#### For Test Tasks
- Implement test setup/teardown
- Write test steps
- Add assertions/verifications
- Handle test data
- Add test markers (@smoke, @regression)

#### For MCP Integration Tasks
- Implement MCP server
- Create tool definitions
- Implement tool executors
- Add error handling
- Write MCP tool tests

---

### 7. Identify Relevant Files
Based on tasks and Test Plan, identify files to create or modify.

**Include:**
- Page object files
- Task method files
- Role files (if applicable)
- Test files
- Utility files
- Configuration files
- Test data files
- MCP server files (if applicable)

**Format:**
```markdown
## Relevant Files

### Framework Infrastructure
- `framework/interfaces/web_interface.py` - Selenium wrapper with enhanced methods
- `framework/resources/config.py` - Configuration management
- `framework/resources/utilities/data_generator.py` - Test data generation

### Page Objects
- `framework/pages/common/authentication_page.py` - Login/registration page interactions
- `framework/pages/catalog/product_list_page.py` - Product listing page interactions
...

### Task Methods
- `framework/tasks/common_tasks.py` - Authentication and navigation workflows
- `framework/tasks/catalog_tasks.py` - Catalog browsing workflows
...

### Tests
- `tests/auth/test_valid_login.py` - Valid login test scenario
- `tests/catalog/test_browse_category.py` - Category browsing test
...

### Configuration & Fixtures
- `conftest.py` - Pytest fixtures (driver, web_interface, test_users)
- `pytest.ini` - Pytest configuration
- `.env.example` - Environment variable template
...

### MCP Server (if applicable)
- `mcp_server/server.py` - MCP server implementation
- `mcp_server/tool_executor.py` - Test execution wrapper
...
```

---

### 8. Generate Final Output
Combine parent tasks, sub-tasks, relevant files, and notes into final Markdown structure.

---

### 9. Save Task List
Save the generated document in `/tasks/` directory with filename `tasks-test-plan-{project-name}.md`

**Example:** `tasks-test-plan-py-sel-framework-mcp.md`

---

## Output Format

The generated task list **must** follow this structure:

```markdown
# Implementation Tasks - {Project Name}

**Based on:** Test Plan v1.0
**Phase:** Phase 2 - Task Generation
**Date:** YYYY-MM-DD

---

## Relevant Files

### Framework Infrastructure
- `framework/interfaces/web_interface.py` - Brief description
...

### Page Objects
- `framework/pages/common/authentication_page.py` - Brief description
...

### Task Methods
- `framework/tasks/common_tasks.py` - Brief description
...

### Tests
- `tests/auth/test_valid_login.py` - Brief description
...

### Configuration & Fixtures
- `conftest.py` - Brief description
...

---

## Tasks

- [ ] 1.0 Parent Task Title [CORE/GLUE]
  - [ ] 1.1 Sub-task description 1.1
  - [ ] 1.2 Sub-task description 1.2
  - [ ] 1.N Run checks: pytest tests/auth/ (or relevant test command)
  - [ ] 1.N+1 Record results in this file (paste output summary)
  - [ ] 1.N+2 Verify "Done When" criteria met

**Done When:**
- Specific acceptance criteria from Test Plan
- All relevant tests pass
- Commands + results documented below

**Feature Branch:** `feature/1.0-parent-task-name`

**Commands Run:**
\`\`\`bash
# Commands will be pasted here after execution
\`\`\`

**Results:**
- One-line summary of each command result

---

- [ ] 2.0 Next Parent Task Title [CORE/GLUE]
  ...
```

---

## Interaction Model

The process explicitly requires a pause after generating parent tasks to get user confirmation ("Go") before proceeding to generate detailed sub-tasks. This ensures the high-level plan aligns with user expectations before diving into details.

---

## Target Audience

Assume the primary reader of the task list is a **QA engineer or automation engineer** who will implement the test framework and tests, with awareness of the test architecture defined in Phase 0.

---

## Task Execution Rules (Reference for Task List)

Include these rules in the generated task list for reference:

### Execution Protocol
1. **One sub-task at a time:** Complete → mark `[x]` in markdown file → wait for "yes" to continue
2. **Parent task commits:** Commit ONLY after ALL sub-tasks complete
3. **Dual task tracking (DO BOTH):**
   - Update TodoWrite tool (UI progress)
   - Update `tasks/tasks-test-plan-{project-name}.md` (mark `[ ]` → `[x]`)
4. **Feature branches:** Use pattern `feature/<task-id>-short-name`
5. **Commit format:** Use conventional commits with detailed body for parent task commits

### Quality Gates
- Tests must pass before marking task complete
- Run test suite after each parent task
- Fix any failures before proceeding

---

## Addendum: QA-Specific Testing & Quality Gates (supplemental)

### Phase 0 — Test Framework Bootstrap (add once per project)
- Create test directory structure: `tests/auth/`, `tests/catalog/`, `tests/cart/`, `tests/checkout/`
- Add `conftest.py` with core fixtures (driver, web_interface, config)
- Add `pytest.ini` for pytest configuration
- Create `.env.example` for environment variables
- Set up test data directory: `framework/resources/data/`

### Phase 1 — Framework Infrastructure
- **WebInterface Layer:** Implement Selenium wrapper with enhanced methods (logging, screenshots, waits)
- **Configuration:** Implement config management (.env file, environment variables)
- **Test Data:** Implement data generation (Faker wrapper, JSON loaders)
- **Utilities:** Implement logging, screenshot capture, wait strategies
- **Fixtures:** Implement pytest fixtures for driver setup, teardown, test users

### Per-Workflow Parent Task Pattern (repeat for each workflow)

#### Mark Core vs Glue for Each Parent Task
- **Core** (framework infrastructure, reusable components) → Tests first (if testing framework code)
  - Example: WebInterface methods, utility functions
  - Write unit tests for reusable methods
- **Glue** (page objects, task methods, test scenarios) → Integration/acceptance coverage
  - Example: Page objects, tasks, tests
  - Validate by running actual test scenarios (end-to-end)

#### Run & Record Checks per Parent Task
Before marking parent task complete, run:
1. **Linter (if applicable):** `flake8` or `pylint` (check code quality)
2. **Type checker (if applicable):** `mypy` (check type hints)
3. **Test execution:**
   - `pytest tests/{workflow}/` (run workflow tests)
   - Or `pytest tests/` (run all tests if infrastructure change)
4. **Coverage (optional):** `pytest --cov=framework` (check coverage on changed code)

**Record commands and results in task list:**
```markdown
**Commands Run:**
```bash
pytest tests/auth/
# 4 passed in 12.3s
```

**Results:**
- All authentication tests passed (4/4)
```

#### Done When Criteria (per parent task)
- Specific acceptance criteria met (from Test Plan or Phase 0 design)
- All relevant tests pass (workflow tests or full suite)
- Page objects/tasks work as expected
- Test data setup is functional
- Commands + results documented in task list

#### Feature Branch Naming
- Pattern: `feature/<task-id>-short-name`
- Example: `feature/2.0-authentication-workflow`

#### Relevant Files Section
- List page objects, task methods, test files, utilities
- Brief description of why each file is relevant
- Include test data files if applicable

---

## Example Task Structure (Authentication Workflow)

```markdown
- [ ] 2.0 Implement Authentication Workflow [GLUE]
  - [ ] 2.1 Create AuthenticationPage class with login/registration locators and methods
  - [ ] 2.2 Create RegistrationPage class with form fields and methods
  - [ ] 2.3 Implement common_tasks.py with login(), logout(), register_new_user() methods
  - [ ] 2.4 Implement test_valid_login.py test scenario
  - [ ] 2.5 Implement test_invalid_credentials.py test scenario
  - [ ] 2.6 Implement test_registration.py test scenario
  - [ ] 2.7 Implement test_logout.py test scenario
  - [ ] 2.8 Run checks: pytest tests/auth/ -v
  - [ ] 2.9 Record results in this file (paste output)
  - [ ] 2.10 Verify "Done When" criteria met

**Done When:**
- AuthenticationPage and RegistrationPage page objects implemented
- common_tasks.py has login, logout, register_new_user methods
- 4 authentication tests implemented and passing
- Tests run reliably (90%+ pass rate)
- Commands + results documented below

**Feature Branch:** `feature/2.0-authentication-workflow`

**Commands Run:**
```bash
# Commands will be pasted here after execution
```

**Results:**
- Summary of test results
```

---

## Differences from Dev Phase 2

| Aspect | Dev Phase 2 (Task Generation) | QA Phase 2 (Task Generation) |
|--------|-------------------------------|------------------------------|
| **Input** | PRD (product requirements) | Test Plan + Phase 0 Test Design |
| **Output** | Tasks to build product feature | Tasks to build test framework + tests |
| **Focus** | Implement product functionality | Implement test infrastructure and scenarios |
| **Parent Tasks** | Feature components (UI, API, DB) | Framework layers OR workflows |
| **Sub-Tasks** | Component implementation steps | Page objects, tasks, tests |
| **Relevant Files** | Product code files | Page objects, tasks, test files |
| **Testing** | Write tests for product code | Run the tests themselves |
| **Quality Gates** | Linter, tests, coverage on product | Linter, test execution, test pass rate |

**Key Insight:**
- Dev tasks build the **product**
- QA tasks build the **tests that validate the product**

---

## Task Breakdown Strategies

### Strategy 1: Layer-Based (New Framework from Scratch)
**Best for:** Building new test framework with no existing infrastructure

**Parent Tasks:**
1. Foundation Layer (WebInterface, config, utilities)
2. Page Objects Layer (all page classes)
3. Task Methods Layer (all workflow classes)
4. Role Layer (user personas)
5. Test Scenarios Layer (all test files)
6. MCP Integration (if applicable)

**Pros:**
- Clear separation of concerns
- Build foundation before tests
- Easy to track framework progress

**Cons:**
- Tests come last (long time before seeing results)
- Requires discipline to not skip ahead

---

### Strategy 2: Workflow-Based (Iterative, Test-Driven)
**Best for:** Iterative development, seeing results early

**Parent Tasks:**
1. Foundation Setup (minimal infrastructure)
2. Authentication Workflow (auth pages + tasks + tests)
3. Catalog Workflow (catalog pages + tasks + tests)
4. Cart Workflow (cart pages + tasks + tests)
5. Checkout Workflow (checkout pages + tasks + tests)
6. MCP Integration (if applicable)

**Pros:**
- See results early (tests running after Workflow 1)
- Iterative progress (4 tests done, 11 remaining)
- Can demo earlier

**Cons:**
- May need to refactor infrastructure as patterns emerge
- Less upfront architectural clarity

---

### Strategy 3: Hybrid (Foundation + Workflows)
**Best for:** Balance between architecture and iterative progress

**Parent Tasks:**
1. Foundation Layer (WebInterface, config, utilities, fixtures)
2. Authentication Workflow (pages + tasks + 4 tests)
3. Catalog Workflow (pages + tasks + 4 tests)
4. Cart Workflow (pages + tasks + 4 tests)
5. Checkout Workflow (pages + tasks + 3 tests)
6. MCP Integration (5 tools)

**Pros:**
- Solid foundation first
- Iterative test implementation
- Clear progress tracking

**Cons:**
- Foundation must be solid before starting workflows

---

**Recommendation:** Use **Strategy 3 (Hybrid)** for most projects - build foundation first, then workflows iteratively.

---

## Version History

**v1.0.0** (2025-01-11)
- Initial QA Phase 2 process documentation
- Adapted from 4D Dev Framework Phase 2 (task generation from PRD)
- Based on QA test framework implementation patterns

---

**For Next QA Project:**
1. Copy this template as guide
2. Read Test Plan document (Phase 1 output)
3. Read Phase 0 Test Design document
4. Generate parent tasks (layer-based, workflow-based, or hybrid)
5. Wait for user "Go" confirmation
6. Generate detailed sub-tasks
7. Identify relevant files
8. Save as `tasks/tasks-test-plan-{project-name}.md`
9. Proceed to Phase 3 (Task Execution)

---

**Questions? Updates?**
This template will evolve. Capture learnings and update as we use it on more QA projects.
