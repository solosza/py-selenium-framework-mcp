---
description: Validate framework code patterns against 4-layer architecture rules
---

# Framework Pattern Validation

Scan all framework layers and validate code patterns against FRAMEWORK.md rules.

## Instructions

1. **Scan these directories:**
   - `framework/pages/` - Page Objects (POMs)
   - `framework/tasks/` - Task modules
   - `framework/roles/` - Role modules
   - `tests/` - Test files (exclude conftest.py, __init__.py)

2. **Validate each layer against these rules:**

### POM Layer (`framework/pages/**/*.py`)
- [x] Has locators as class constants (tuples with By.*)
- [x] Has atomic methods returning `self`
- [x] Has state-check methods (`is_*`, `get_*`, `has_*`)
- [ ] VIOLATION: No `@autologger` decorator (POMs don't use it)
- [ ] VIOLATION: Imports from tasks/ or roles/
- [ ] VIOLATION (DD-49): `navigate_to("http` or `navigate_to('http` - must use `self.web.config["url"]`

### Task Layer (`framework/tasks/**/*.py`)
- [x] Has `@autologger.automation_logger("Task")` decorator
- [x] Methods return `None` (no return statements with values)
- [x] Imports from pages/ only
- [ ] VIOLATION: Contains `By.` imports or locator tuples
- [ ] VIOLATION: Imports from roles/
- [ ] VIOLATION (DD-49): `self.web.navigate_to(` - Tasks must call POM navigate() instead

### Role Layer (`framework/roles/**/*.py`)
- [x] Has `@autologger.automation_logger("Role")` decorator
- [x] Methods return `None` (no return statements with values)
- [x] Imports from tasks/ only
- [ ] VIOLATION: Contains `By.` imports or locator tuples
- [ ] VIOLATION: Imports from pages/ directly
- [ ] VIOLATION (DD-49): `self.web.navigate_to(` - Roles must NOT navigate directly

### Test Layer (`tests/**/*.py`)
- [x] Has `@autologger.automation_logger("Test")` decorator
- [x] Imports Role from roles/
- [x] Imports POM from pages/ (for assertions only)
- [x] Uses POM state-check methods in assertions
- [ ] VIOLATION: Contains `By.` imports or locator tuples
- [ ] VIOLATION: Imports from tasks/ directly
- [ ] VIOLATION: Calls multiple Role methods (should call ONE workflow method)

3. **Report format:**

```
FRAMEWORK CHECK RESULTS
=======================

✓ PASS: framework/pages/checkout/cart_page.py
✓ PASS: framework/tasks/checkout/checkout_tasks.py
✗ FAIL: framework/roles/checkout/registered_user.py
  - Line 5: VIOLATION - Imports from pages/ (should import tasks/ only)

Summary: 2 passed, 1 failed
```

4. **After scan, provide:**
   - List of all violations with file:line references
   - Suggested fixes for each violation
   - Overall pass/fail status
