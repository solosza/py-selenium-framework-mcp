# PRD: MCP Tool Chain Refactor (Phase B)

**Version:** 2.0
**Status:** Draft
**Date:** 2025-12-02
**Previous Version:** 1.0 (2025-12-01)

---

## 1. Introduction / Overview

This PRD defines the scope and requirements for refactoring the MCP tool chain to implement the complete 9-step AI-assisted test generation workflow documented in FRAMEWORK.md Section 8.

**Problem Statement:**
- Current tools (3-6) are partially refactored but don't follow the full 9-step flow
- Tools 1-2 output doesn't include metadata needed by downstream tools
- No enforcement of AI prompting rules across the tool chain
- Generated code has architecture violations (returns from Role/Task, decorators on POM)
- Tests assert on return values instead of POM state-check methods
- No `expected_states` extraction from BDD "Then" clause

**Goal:**
Implement the complete 9-step workflow with metadata passing, AI rule enforcement, and E2E validation with visible browser and HTML reports.

---

## 2. Goals

1. **Implement full 9-step flow** as documented in FRAMEWORK.md Section 8
2. **Add metadata output** to Tools 1-2 for downstream consumption
3. **Enforce AI prompting rules** via CLAUDE.md + FRAMEWORK.md Section 8
4. **Fix architecture violations** in generated code (no returns, no POM decorators)
5. **Implement expected_states extraction** from BDD "Then" clause (DD-09)
6. **Implement check-existing pattern** for Tools 4-5 (DD-12)
7. **Demonstrate E2E workflow** with visible browser + HTML report

---

## 3. User Stories

| As a... | I want to... | So that... |
|---------|--------------|------------|
| AI Agent | Have clear rules for each step in the tool chain | I generate correct code without hallucinations |
| AI Agent | Receive metadata from each tool | I can pass accurate method names to downstream tools |
| Developer | Have separate generator files per layer | Code is maintainable and easy to update |
| QA Engineer | See generated tests run in visible browser | I can verify the workflow works correctly |
| Portfolio Reviewer | See clean, consistent generated code | MCP tools demonstrate professional quality |

---

## 4. Functional Requirements

### 4.1 Step 1-2: User Input & AI Processing

| ID | Requirement |
|----|-------------|
| FR-01 | AI must ask for persona ("As a...") if missing (DD-01) |
| FR-02 | AI must ask for URL if missing (DD-02) |
| FR-03 | AI must extract role_name from persona |
| FR-04 | AI must determine domain from intent (auth/catalog/cart/checkout) |
| FR-05 | AI must convert requirement to BDD format (Given/When/Then) |
| FR-06 | AI must extract expected_states from BDD "Then" clause (DD-09) |
| FR-07 | AI must initialize metadata context before calling tools |

### 4.2 Tool 1: generate_tests_from_user_story

| ID | Requirement |
|----|-------------|
| FR-08 | Tool 1 must output `test_scenarios[]` in metadata format |
| FR-09 | Each scenario must include: name, given, when, then, workflow |
| FR-10 | AI must add test_scenarios to metadata context |

### 4.3 Tool 2: discover_page_elements

| ID | Requirement |
|----|-------------|
| FR-11 | Tool 2 must output `discovered_elements[]` in metadata format |
| FR-12 | Each element must include: name, type, locator |
| FR-13 | AI must filter elements relevant to intent before passing to Tool 3 |
| FR-14 | AI must add discovered_elements to metadata context |

### 4.4 Tool 3: generate_page_object

| ID | Requirement |
|----|-------------|
| FR-15 | Tool 3 must accept `expected_states` parameter |
| FR-16 | Tool 3 must generate state-check methods from expected_states |
| FR-17 | Tool 3 must output `pom_metadata` with: class_name, import_path, locators[], action_methods[], state_methods[] |
| FR-18 | Generated POM must have NO decorators, return `self` from action methods |
| FR-19 | AI must add pom_metadata to metadata context |

### 4.5 Tool 4: generate_task

| ID | Requirement |
|----|-------------|
| FR-20 | Tool 4 must accept `pom_metadata` as input |
| FR-21 | Tool 4 must check existing tasks before generating new (DD-12) |
| FR-22 | Tool 4 must return `existing_found` status if task already exists |
| FR-23 | Tool 4 must generate Task methods that call actual POM methods from metadata |
| FR-24 | Tool 4 must output `task_metadata` with: class_name, import_path, composed_pages[], task_methods[] |
| FR-25 | Generated Task must have `@autologger("Task")`, return `None` |
| FR-26 | AI must add task_metadata to metadata context |

### 4.6 Tool 5: generate_role

| ID | Requirement |
|----|-------------|
| FR-27 | Tool 5 must accept `task_metadata` as input |
| FR-28 | Tool 5 must check existing roles before generating new (DD-12) |
| FR-29 | Tool 5 must return `existing_found` status if role already exists |
| FR-30 | Tool 5 must generate Role methods that call actual Task methods from metadata |
| FR-31 | Tool 5 must output `role_metadata` with: class_name, import_path, composed_tasks[], workflow_methods[] |
| FR-32 | Generated Role must have `@autologger("Role")`, return `None` |
| FR-33 | AI must add role_metadata to metadata context |

### 4.7 Tool 6: generate_test_runner

| ID | Requirement |
|----|-------------|
| FR-34 | Tool 6 must accept `role_metadata` + `pom_metadata` as input |
| FR-35 | Tool 6 must generate tests that call actual Role methods from metadata |
| FR-36 | Tool 6 must generate assertions using actual POM state methods from metadata (DD-15) |
| FR-37 | Generated Test must follow AAA pattern: Arrange, Act (ONE call), Assert (via POM) |
| FR-38 | Generated Test must have `@autologger("Test")`, `@pytest.mark.<domain>` |

### 4.8 Step 9: Save Files & Report

| ID | Requirement |
|----|-------------|
| FR-39 | AI must save generated files to suggested paths |
| FR-40 | AI must report: files created, files reused (existing), pytest run command |
| FR-41 | AI must offer to run test with `--headless=False` |

### 4.9 Generator Refactoring

| ID | Requirement |
|----|-------------|
| FR-42 | Maintain `mcp_server/utils/generators/` directory structure |
| FR-43 | Each generator embeds its layer's patterns inline (self-contained) |
| FR-44 | Generated code includes docstrings and inline comments |
| FR-45 | No hardcoded method names in generators - all derived from metadata |

---

## 5. Non-Goals (Out of Scope)

- Tools 7-11 refactoring (utility tools, don't generate framework code)
- Adding new MCP tools beyond 1-6
- Changing the 4-layer architecture itself
- Refactoring WebInterface layer
- Adding new framework features

---

## 6. Design Considerations

### 6.1 AI Rule Enforcement

**Location:** FRAMEWORK.md Section 8 + CLAUDE.md

**Pattern:**
```
CLAUDE.md                    FRAMEWORK.md Section 8
    │                              │
    │  "Read Section 8 before      │  Detailed "AI PROMPTING RULES"
    │   ANY tool call"             │  boxes for each step
    │                              │
    └──────────────────────────────┘
                   │
                   ▼
         AI follows rules for each step
```

### 6.2 Metadata Flow Architecture

```
Step 1-2 (User Input + AI Processing)
    │
    ├── role_name: "RegisteredUser"
    ├── intent: "login"
    ├── domain: "auth"
    ├── url: "http://..."
    ├── expected_states: [{name: "is_logged_in", ...}]
    └── bdd_scenarios: [...]
          │
          ▼
Tool 1 (generate_tests_from_user_story)
    │
    └── test_scenarios: [{name, given, when, then, workflow}]
          │
          ▼
Tool 2 (discover_page_elements)
    │
    └── discovered_elements: [{name, type, locator}]
          │
          ▼
Tool 3 (generate_page_object)
    │
    └── pom_metadata: {class_name, import_path, locators[], action_methods[], state_methods[]}
          │
          ▼
Tool 4 (generate_task)
    │
    └── task_metadata: {class_name, import_path, composed_pages[], task_methods[]}
          │
          ▼
Tool 5 (generate_role)
    │
    └── role_metadata: {class_name, import_path, composed_tasks[], workflow_methods[]}
          │
          ▼
Tool 6 (generate_test_runner)
    │
    └── Test file with correct method calls and assertions
```

### 6.3 Check-Existing Pattern (DD-12)

**Tool 4 (Task):**
```python
# Before generating new Task
1. Scan framework/tasks/ for existing Task classes
2. Check if existing class has method matching intent
3. If found: return {"status": "existing_found", "existing_class": "CommonTasks", ...}
4. AI decides: use existing OR force_generate=True
```

**Tool 5 (Role):**
```python
# Before generating new Role
1. Scan framework/roles/ for existing Role classes
2. Check if existing class matches persona
3. If found: return {"status": "existing_found", "existing_class": "RegisteredUser", ...}
4. AI decides: use existing OR force_generate=True
```

### 6.4 expected_states Extraction (DD-09)

**Source:** BDD "Then" clause from Step 2

**Process:**
```
"Then user is logged in"
    → expected_state: {name: "is_logged_in", type: "bool", description: "user is logged in"}

"Then error message is displayed"
    → expected_state: {name: "has_error_message", type: "bool", description: "error message displayed"}

"Then cart shows 2 items"
    → expected_state: {name: "get_cart_count", type: "int", description: "cart item count"}
```

**Naming Conventions:**
- `is_*` → returns bool (state check)
- `has_*` → returns bool (presence check)
- `get_*` → returns value (str/int)

### 6.5 Directory Structure

```
mcp_server/
├── tools/
│   ├── tool_01_generate_tests_from_user_story.py  # Add metadata output
│   ├── tool_02_discover_page_elements.py          # Add metadata output
│   ├── tool_03_generate_page_object.py            # Accept expected_states
│   ├── tool_04_generate_task.py                   # Check existing, accept POM metadata
│   ├── tool_05_generate_role.py                   # Check existing, accept Task metadata
│   └── tool_06_generate_test_runner.py            # Accept Role + POM metadata
├── utils/
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── page_object_generator.py   # POM patterns + metadata
│   │   ├── task_generator.py          # Task patterns + metadata
│   │   ├── role_generator.py          # Role patterns + metadata
│   │   └── test_generator.py          # Test patterns + metadata
│   └── ...
└── _dev_tests/                        # E2E test scripts
```

---

## 7. Technical Considerations

### 7.1 Dependencies
- Existing generators in `utils/generators/` - update with metadata support
- Tools currently partially refactored - complete the metadata chain
- Generated code must use existing framework imports (`WebInterface`, `autologger`)

### 7.2 Backwards Compatibility
- Tools must still work if called without full metadata (graceful degradation)
- Existing test artifacts should not break

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| Full 9-step flow documented | Yes |
| Tools 1-2 output metadata | Yes |
| Tools 3-6 accept/output metadata | Yes |
| Check-existing implemented (Tools 4-5) | Yes |
| expected_states extraction works | Yes |
| Simple E2E test (catalog browse) passes | Yes |
| Medium E2E test (auth + catalog) passes | Yes |
| Tests run with visible browser | Yes |
| HTML reports generated | Yes |
| User validates E2E tests visually | Yes |

---

## 9. Test Strategy

### 9.1 Unit Tests
- Location: `mcp_server/_dev_tests/`
- Each generator has unit tests validating output patterns
- Each tool has unit tests validating metadata output
- Run with: `python -m pytest mcp_server/_dev_tests/ -v`

### 9.2 E2E Tests
Two scenarios executed through full 9-step flow:

**Simple (Catalog Browse):**
```
Requirement: "As a guest, I want to browse products in the Women category"
URL: http://automationpractice.pl/index.php
Expected: Browser opens, navigates to Women category, verifies products displayed
```

**Medium (Auth + Catalog):**
```
Requirement: "As a registered user, I want to login and browse products"
URL: http://automationpractice.pl/index.php?controller=authentication
Expected: Browser opens, logs in, browses category, verifies products, logs out
```

### 9.3 E2E Demonstration Requirements
- Run with `--headless=False` (visible browser)
- Generate HTML report: `--html=reports/<test>_report.html`
- User watches browser execute test
- User validates report generated

---

## 10. Acceptance Tests

### AT-01: Step 2 AI Processing
```
GIVEN a user requirement "As a registered user, I want to login"
WHEN AI processes the requirement
THEN AI extracts role_name = "RegisteredUser"
AND AI determines domain = "auth"
AND AI extracts expected_states from "Then" clause
AND AI initializes metadata context
```

### AT-02: Tool 1 Metadata Output
```
GIVEN a BDD user story
WHEN Tool 1 processes it
THEN output includes test_scenarios[] with name, given, when, then, workflow
```

### AT-03: Tool 2 Metadata Output
```
GIVEN a page URL
WHEN Tool 2 discovers elements
THEN output includes discovered_elements[] with name, type, locator
```

### AT-04: Tool 3 expected_states
```
GIVEN expected_states = [{name: "is_logged_in", ...}]
WHEN Tool 3 generates POM
THEN POM includes is_logged_in() state-check method
AND pom_metadata.state_methods includes is_logged_in
```

### AT-05: Tool 4 Check Existing
```
GIVEN intent = "login" and CommonTasks already has log_in method
WHEN Tool 4 is called with check_existing=True
THEN Tool 4 returns status = "existing_found"
AND returns existing_class = "CommonTasks"
```

### AT-06: Tool 5 Check Existing
```
GIVEN role_name = "RegisteredUser" and RegisteredUser already exists
WHEN Tool 5 is called with check_existing=True
THEN Tool 5 returns status = "existing_found"
AND returns existing_class = "RegisteredUser"
```

### AT-07: Tool 6 Assertions via POM
```
GIVEN pom_metadata with state_methods = ["is_logged_in"]
WHEN Tool 6 generates test
THEN test assertions use login_page.is_logged_in()
AND test does NOT assert on return values
```

### AT-08: Simple E2E Test
```
GIVEN full 9-step flow for catalog browse requirement
WHEN running pytest with --headless=False
THEN browser opens visibly
AND navigates to Women category
AND test passes
AND HTML report generated
```

### AT-09: Medium E2E Test
```
GIVEN full 9-step flow for auth + catalog requirement
WHEN running pytest with --headless=False
THEN browser opens visibly
AND user logs in
AND browses category
AND test passes
AND HTML report generated
```

---

## 11. Implementation Order

| Phase | Task | Description |
|-------|------|-------------|
| B.1 | Tool 1-2 Metadata | Add metadata output to Tools 1-2 |
| B.2 | Tool 3 expected_states | Add expected_states input to Tool 3 |
| B.3 | Tool 4 Refactor | Check-existing + accept POM metadata |
| B.4 | Tool 5 Refactor | Check-existing + accept Task metadata |
| B.5 | Tool 6 Refactor | Accept Role + POM metadata for assertions |
| B.6 | Simple E2E | Full 9-step flow - catalog browse (visible browser) |
| B.7 | Medium E2E | Full 9-step flow - auth + catalog (visible browser) |
| B.8 | Cleanup | Final docs, merge to main |

---

## 12. Open Questions

None - all questions resolved via FRAMEWORK.md Section 8 Design Decisions.

---

## 13. Relevant Files

### Files to Update
- `mcp_server/tools/tool_01_generate_tests_from_user_story.py` - Add metadata output
- `mcp_server/tools/tool_02_discover_page_elements.py` - Add metadata output
- `mcp_server/tools/tool_03_generate_page_object.py` - Accept expected_states
- `mcp_server/tools/tool_04_generate_task.py` - Check existing, accept POM metadata
- `mcp_server/tools/tool_05_generate_role.py` - Check existing, accept Task metadata
- `mcp_server/tools/tool_06_generate_test_runner.py` - Accept Role + POM metadata
- `mcp_server/utils/generators/page_object_generator.py` - Generate state methods from expected_states
- `mcp_server/utils/generators/task_generator.py` - Accept POM metadata
- `mcp_server/utils/generators/role_generator.py` - Accept Task metadata
- `mcp_server/utils/generators/test_generator.py` - Accept Role + POM metadata
- `CLAUDE.md` - Updated with 9-step flow (DONE)

### Test Artifacts
- `framework/pages/test1/`, `framework/pages/test2/`
- `framework/tasks/test1/`, `framework/tasks/test2/`
- `framework/roles/test1/`, `framework/roles/test2/`
- `tests/test1/`, `tests/test2/`
- `reports/test1_report.html`, `reports/test2_report.html`

---

**PRD Status:** Ready for Task Generation (Phase 2)
