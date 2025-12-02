# PRD: MCP Tool Refactor (Phase B)

**Version:** 1.0
**Status:** Draft
**Date:** 2025-12-01

---

## 1. Introduction / Overview

This PRD defines the scope and requirements for refactoring MCP code generation tools (3-6) to produce code that matches the validated 4-layer framework architecture patterns established in Phase A.

**Problem Statement:**
- Current `code_generator.py` is monolithic (1625 lines) and hard to maintain
- Generated code violates architecture rules (returns from Role/Task, decorators on POM)
- Generated tests assert on return values instead of POM state-check methods
- No separation of concerns - one file handles all layer generation

**Goal:**
Refactor tools 3-6 with dedicated per-layer generators that produce code matching production framework patterns exactly.

---

## 2. Goals

1. **Split `code_generator.py`** into dedicated generators per layer in `utils/generators/`
2. **Fix architecture violations** in generated code (no returns, no POM decorators)
3. **Validate generated code** via automated checks + manual review
4. **Demonstrate E2E workflow** - visible browser test from generation to HTML report
5. **Clean up dev test folders** before creating new test artifacts

---

## 3. User Stories

| As a... | I want to... | So that... |
|---------|--------------|------------|
| Developer | Have separate generator files per layer | Code is maintainable and easy to update |
| AI Agent | Generate code that matches production patterns | No manual fixes needed after generation |
| QA Engineer | See generated tests run in visible browser | I can verify the workflow works correctly |
| Portfolio Reviewer | See clean, consistent generated code | MCP tools demonstrate professional quality |

---

## 4. Functional Requirements

### 4.1 Generator Refactoring

| ID | Requirement |
|----|-------------|
| FR-01 | Create `mcp_server/utils/generators/` directory structure |
| FR-02 | Create `page_object_generator.py` - generates POMs with NO decorators, returns `self` |
| FR-03 | Create `task_generator.py` - generates Tasks with `@autologger("Task")`, returns `None` |
| FR-04 | Create `role_generator.py` - generates Roles with `@autologger("Role")`, returns `None` |
| FR-05 | Create `test_generator.py` - generates Tests that assert via POM state-check methods |
| FR-06 | Each generator embeds its layer's patterns inline (self-contained) |
| FR-07 | Generated code includes docstrings and inline comments on key code blocks |

### 4.2 Tool Updates

| ID | Requirement |
|----|-------------|
| FR-08 | Update Tool 3 (`tool_03_generate_page_object.py`) to use `page_object_generator` |
| FR-09 | Update Tool 4 (`tool_04_generate_task.py`) to use `task_generator` |
| FR-10 | Update Tool 5 (`tool_05_generate_role.py`) to use `role_generator` |
| FR-11 | Update Tool 6 (`tool_06_generate_test_template.py`) to use `test_generator` |

### 4.3 Validation Requirements

| ID | Requirement |
|----|-------------|
| FR-12 | Create automated validation script to check generated code against rules |
| FR-13 | Validation checks: no returns from Role/Task, no decorators on POM, correct imports |
| FR-14 | Manual review: compare generated code against existing framework code |

### 4.4 Cleanup Requirements

| ID | Requirement |
|----|-------------|
| FR-15 | Clean up existing dev test folders (`devtest1/`, etc.) before new testing |

### 4.5 E2E Demonstration Requirements

| ID | Requirement |
|----|-------------|
| FR-16 | Simple test case: Generate catalog browse test (navigate → verify products) |
| FR-17 | Medium complex test case: Generate auth + catalog test (login → browse → verify → logout) |
| FR-18 | Run generated tests with `--headless=False` (visible browser) |
| FR-19 | Generate HTML report for test results |
| FR-20 | Document full E2E workflow: generation → execution → report |

---

## 5. Non-Goals (Out of Scope)

- Tools 1-2 refactoring (requirements gathering, not code generation)
- Tools 7-11 refactoring (utility tools, don't generate framework code)
- Adding new MCP tools
- Changing the 4-layer architecture itself
- Refactoring WebInterface layer
- Adding new framework features

---

## 6. Design Considerations

### 6.1 Directory Structure

```
mcp_server/
├── utils/
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── page_object_generator.py   # POM patterns + generation
│   │   ├── task_generator.py          # Task patterns + generation
│   │   ├── role_generator.py          # Role patterns + generation
│   │   └── test_generator.py          # Test patterns + generation
│   ├── code_generator.py              # (deprecate after migration)
│   └── ...other utils
├── tools/
│   ├── tool_03_generate_page_object.py  # Thin wrapper → page_object_generator
│   ├── tool_04_generate_task.py         # Thin wrapper → task_generator
│   ├── tool_05_generate_role.py         # Thin wrapper → role_generator
│   └── tool_06_generate_test_template.py # Thin wrapper → test_generator
```

### 6.2 Generated Code Patterns

**Page Object (NO decorators, returns `self`):**
```python
class ProductListPage:
    PRODUCT_ITEMS = (By.CSS_SELECTOR, "ul.product_list li")

    def __init__(self, web: WebInterface):
        self.web = web

    def click_category(self, name: str) -> "ProductListPage":
        """Click category link. Returns self for chaining."""
        self.web.click(*self.CATEGORY_LINK)
        return self

    def has_products(self) -> bool:
        """State-check method for test assertions."""
        return self.get_product_count() > 0
```

**Task (`@autologger("Task")`, returns `None`):**
```python
class CatalogTasks:
    @autologger.automation_logger("Task")
    def browse_category(self, category_name: str) -> None:
        """Browse to category. Tests assert via POM."""
        self.web.navigate_to(self.base_url)
        self.product_list_page.click_category(category_name)
        # NO return - test asserts via product_list_page.has_products()
```

**Role (`@autologger("Role")`, returns `None`):**
```python
class GuestUser:
    @autologger.automation_logger("Role")
    def browse_category(self, category_name: str) -> None:
        """Browse category workflow. Tests assert via POM."""
        self.catalog_tasks.browse_category(category_name)
        # NO return - test asserts via POM state-check methods
```

**Test (asserts via POM, NOT return values):**
```python
@pytest.mark.catalog
@autologger.automation_logger("Test")
def test_browse_women_category(web_interface, config):
    """Test browsing Women category."""
    # Arrange
    guest = GuestUser(web_interface, config["url"])
    product_list_page = ProductListPage(web_interface)

    # Act - ONE role method call, NO return value
    guest.browse_category("Women")

    # Assert - Via POM state-check methods
    assert product_list_page.has_products(), "Products should be displayed"
```

### 6.3 Test Folder Structure

```
framework/
├── pages/test1/       # Generated POMs for simple test
├── pages/test2/       # Generated POMs for medium test
├── tasks/test1/
├── tasks/test2/
├── roles/test1/
├── roles/test2/
tests/
├── test1/             # Simple test: catalog browse
├── test2/             # Medium test: auth + catalog
```

---

## 7. Technical Considerations

### 7.1 Dependencies
- Existing `code_generator.py` functions can be referenced during refactor
- Tools currently import from `utils.code_generator` - update imports incrementally
- Generated code must use existing framework imports (`WebInterface`, `autologger`)

### 7.2 Deprecation Strategy
1. Create new generators in `utils/generators/`
2. Update tools one at a time (3 → 4 → 5 → 6)
3. Keep `code_generator.py` during transition
4. Delete `code_generator.py` after all tools migrated and validated

### 7.3 Validation Script Rules
```python
# Automated checks for generated code:
VALIDATION_RULES = {
    "page_object": {
        "no_decorators": True,           # No @autologger on methods
        "returns_self": True,            # Action methods return self
        "locators_as_constants": True,   # UPPER_SNAKE at class level
        "has_state_checks": True         # Methods like is_*, has_*, get_*
    },
    "task": {
        "has_decorator": "@autologger.automation_logger(\"Task\")",
        "returns_none": True,            # No return statements
        "no_locators": True              # Locators only in POM
    },
    "role": {
        "has_decorator": "@autologger.automation_logger(\"Role\")",
        "returns_none": True,            # No return statements
        "composes_tasks": True           # Has task instances
    },
    "test": {
        "has_decorator": "@autologger.automation_logger(\"Test\")",
        "asserts_via_pom": True,         # assert page.method(), not result
        "single_role_call": True         # ONE workflow method call
    }
}
```

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| All 4 generators created | 100% |
| All 4 tools updated | 100% |
| Automated validation passes | 100% |
| Manual review confirms pattern match | Yes |
| Simple test case runs with visible browser | Yes |
| Medium test case runs with visible browser | Yes |
| HTML reports generated | Yes |
| `code_generator.py` deprecated | Yes |

---

## 9. Test Strategy

### 9.1 Unit Tests
- Location: `mcp_server/_dev_tests/`
- Each generator has unit tests validating output patterns
- Run with: `python -m pytest mcp_server/_dev_tests/ -v`

### 9.2 Integration Tests
- Generate code via MCP tools
- Place in `test1/`, `test2/` folders
- Run with visible browser: `pytest tests/test1/ -v --headless=False`
- Verify HTML report: `--html=reports/test1_report.html`

### 9.3 E2E Demonstration
Full workflow demonstration:
1. User provides requirement
2. MCP tools generate all layers (POM → Task → Role → Test)
3. Run pytest with `--headless=False`
4. Watch browser execute test
5. View HTML report

---

## 10. Acceptance Tests

### AT-01: Page Object Generator
```
GIVEN a request to generate a ProductListPage
WHEN the page_object_generator creates code
THEN the code has NO @autologger decorators
AND action methods return self
AND locators are class-level UPPER_SNAKE constants
AND state-check methods (has_products, is_loaded) exist
```

### AT-02: Task Generator
```
GIVEN a request to generate CatalogTasks
WHEN the task_generator creates code
THEN methods have @autologger.automation_logger("Task") decorator
AND methods return None (no return statements)
AND no locators are present in the code
AND page objects are composed in __init__
```

### AT-03: Role Generator
```
GIVEN a request to generate GuestUser role
WHEN the role_generator creates code
THEN workflow methods have @autologger.automation_logger("Role") decorator
AND methods return None (no return statements)
AND tasks are composed in __init__
AND workflow methods call multiple task methods
```

### AT-04: Test Generator
```
GIVEN a request to generate test_browse_women_category
WHEN the test_generator creates code
THEN test has @autologger.automation_logger("Test") decorator
AND test calls ONE role workflow method
AND assertions use POM state-check methods (assert page.has_products())
AND assertions do NOT check return values (not: assert result is True)
```

### AT-05: Simple E2E Test (Catalog Browse)
```
GIVEN generated code for catalog browse test
WHEN running pytest with --headless=False
THEN browser opens visibly
AND navigates to category page
AND test passes
AND HTML report is generated
```

### AT-06: Medium E2E Test (Auth + Catalog)
```
GIVEN generated code for auth + catalog test
WHEN running pytest with --headless=False
THEN browser opens visibly
AND user logs in
AND browses to category
AND verifies products displayed
AND logs out
AND test passes
AND HTML report is generated
```

### AT-07: Automated Validation
```
GIVEN generated code from all tools
WHEN running validation script
THEN all architecture rules pass
AND no violations reported
```

---

## 11. Implementation Order

Sequential bottom-up (matches framework layers):

| Phase | Task | Description |
|-------|------|-------------|
| B.1 | Setup | Create `utils/generators/` structure, cleanup dev folders |
| B.2 | Tool 3 | Create `page_object_generator.py`, update tool |
| B.3 | Tool 4 | Create `task_generator.py`, update tool |
| B.4 | Tool 5 | Create `role_generator.py`, update tool |
| B.5 | Tool 6 | Create `test_generator.py`, update tool |
| B.6 | Validation | Create automated validation script |
| B.7 | Simple E2E | Generate + run catalog browse test (visible browser) |
| B.8 | Medium E2E | Generate + run auth + catalog test (visible browser) |
| B.9 | Cleanup | Deprecate `code_generator.py`, final documentation |

---

## 12. Open Questions

None - all questions resolved during Phase 0 design discussion.

---

## 13. Relevant Files

### Files to Create
- `mcp_server/utils/generators/__init__.py`
- `mcp_server/utils/generators/page_object_generator.py`
- `mcp_server/utils/generators/task_generator.py`
- `mcp_server/utils/generators/role_generator.py`
- `mcp_server/utils/generators/test_generator.py`
- `mcp_server/_dev_tests/test_generators.py` (validation script)

### Files to Update
- `mcp_server/tools/tool_03_generate_page_object.py`
- `mcp_server/tools/tool_04_generate_task.py`
- `mcp_server/tools/tool_05_generate_role.py`
- `mcp_server/tools/tool_06_generate_test_template.py`

### Files to Deprecate
- `mcp_server/utils/code_generator.py` (after migration complete)

### Test Artifacts
- `framework/pages/test1/`, `framework/pages/test2/`
- `framework/tasks/test1/`, `framework/tasks/test2/`
- `framework/roles/test1/`, `framework/roles/test2/`
- `tests/test1/`, `tests/test2/`
- `reports/test1_report.html`, `reports/test2_report.html`

---

**PRD Status:** Ready for Task Generation (Phase 2)
