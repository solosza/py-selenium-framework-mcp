# Code Generator Fixes Needed

## ✅ VALIDATION RESULT

**Test Collection:** ✅ **PASSED!**
- Generated test file: `tests/auth/test_successful_login_generated.py`
- Pytest successfully collected 1 test
- No syntax errors
- Imports work correctly

**Conclusion:** Generated code is syntactically valid and structurally correct!

**Test Execution:** ❌ **FAILED**
- Error: `TypeError: object.__init__() takes exactly one argument`
- Location: `login_page_generated.py:19` - `super().__init__(web)`
- Root Cause: LoginPage doesn't inherit from BasePage, so `super().__init__(web)` fails
- Fix: Either inherit from BasePage OR remove super().__init__() call

## Issues Found During Real Test Execution

### Issue 1: Import Paths - Tasks
**Problem:** Generated AuthTasks uses relative imports instead of absolute imports
**Generated Code:**
```python
from interfaces.web_interface import WebInterface
from pages.auth.loginpage import LoginPage
```

**Should Be:**
```python
from framework.interfaces.web_interface import WebInterface
from framework.pages.common.loginpage import LoginPage
```

**Fix Location:** `mcp_server/utils/code_generator.py` - `generate_task_template()` function
**Impact:** Task files won't import correctly

---

### Issue 2: Import Paths - Page Objects
**Problem:** Generated LoginPage uses mixed import paths
**Generated Code:**
```python
from framework.pages.base_page import BasePage
from interfaces.web_interface import WebInterface
```

**Should Be:**
```python
from framework.interfaces.web_interface import WebInterface
```

**Note:** BasePage doesn't exist in the framework, so we removed that import.

**Fix Location:** `mcp_server/utils/code_generator.py` - `generate_page_object_template()` function
**Impact:** Page objects won't import correctly

---

### Issue 3: File Naming Convention
**Problem:** Generated file uses snake_case in path but different naming in imports
**Generated:** `pages/auth/loginpage.py`
**Import:** `from pages.auth.loginpage import LoginPage`

**Should Be Consistent:**
- File: `pages/common/login_page.py` (or `pages/auth/login_page.py`)
- Import: `from framework.pages.common.login_page import LoginPage`

**Fix Location:** `mcp_server/utils/code_generator.py` - `get_file_path_for_component()` function
**Impact:** File organization and imports don't match

---

## Summary of Changes Needed

### 1. Update `generate_task_template()` - Lines ~391-502 in code_generator.py

**Current Import Generation:**
```python
from typing import Optional
from interfaces.web_interface import WebInterface
from pages.auth.loginpage import LoginPage
```

**Fix Required:**
```python
# In generate_task_template(), find the import section and change:

# OLD:
from interfaces.web_interface import WebInterface
from pages.{workflow}.{page_file_name} import {PageClassName}

# NEW:
from framework.interfaces.web_interface import WebInterface
from framework.pages.common.{page_file_name} import {PageClassName}
```

**Exact Location:** Look for where imports are generated (around line 420-430)

---

### 2. Update `generate_page_object_template()` - Lines ~505-650 in code_generator.py

**Current Generated Code:**
```python
from selenium.webdriver.common.by import By
from framework.pages.base_page import BasePage
from interfaces.web_interface import WebInterface

class LoginPage(BasePage):
```

**Fix Required:**
```python
# In generate_page_object_template(), update imports section:

# OLD:
from framework.pages.base_page import BasePage
from interfaces.web_interface import WebInterface

class {page_name}(BasePage):

# NEW:
from framework.interfaces.web_interface import WebInterface

class {page_name}:
```

**Note:** Remove BasePage inheritance until Task 1.0 is complete

**Exact Location:** Beginning of the template string (around line 520)

---

### 3. Update `get_file_path_for_component()` - Lines ~740-800 in code_generator.py

**Current Behavior:**
- Returns: `pages/auth/loginpage.py`
- Inconsistent: file is `loginpage.py` but class is `LoginPage`

**Fix Required:**
```python
def get_file_path_for_component(component_type: str, name: str, workflow: str = "") -> str:
    # Convert PascalCase class name to snake_case filename
    import re
    snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    if component_type == "page":
        # Use 'common' directory instead of workflow-specific
        return f"framework/pages/common/{snake_name}.py"
    elif component_type == "task":
        return f"framework/tasks/{snake_name}.py"
    # ... etc
```

**Exact Location:** Find get_file_path_for_component() function

---

### 4. Update `generate_test_template()` - Lines ~170-260 in code_generator.py

**Current Status:** ✅ Already Correct!
```python
from tasks.{workflow}_tasks import {TaskClass}
```

**Why it works:** Test file adds `framework/` to sys.path, so `tasks.X` resolves correctly

**No changes needed** for this function.

---

### Issue 4: WebInterface Method Name Mismatches
**Problem:** Generated code calls wrong method names on WebInterface
**Test Error:** `AttributeError: 'WebInterface' object has no attribute 'navigate'`
**Root Cause:** Code generator uses method names that don't match actual WebInterface API

**Method Name Mismatches:**
1. Generated: `navigate()` → Actual: `navigate_to()`
2. Generated: `send_keys()` → Actual: `type_text()`
3. Generated: `is_element_visible()` → Actual: `is_element_displayed()`

**Fix Location:** `mcp_server/utils/code_generator.py` - Multiple locations in `generate_task_workflows()` and `generate_page_object_template()`

**Changes Made:**
```python
# Fix 1: Navigate method (lines 417, 469)
# OLD: self.web.navigate(url)
# NEW: self.web.navigate_to(url)

# Fix 2: Type text method (line 715)
# OLD: self.web.send_keys(*locator, text)
# NEW: self.web.type_text(*locator, text)

# Fix 3: Visibility check method (lines 428, 444, 448, 473, 477, 510, 515, 519, 534, 538)
# OLD: self.web.is_element_visible(*locator)
# NEW: self.web.is_element_displayed(*locator)
```

**Impact:** Without this fix, generated task workflows and page objects fail at runtime

---

### Issue 5: Missing Framework Infrastructure (NOT A BUG)
**Problem:** Generated code references `framework.interfaces.web_interface.WebInterface` but this file doesn't exist yet
**Current State:** `framework/interfaces/` directory is empty

**Required Framework Files:**
1. `framework/interfaces/__init__.py`
2. `framework/interfaces/web_interface.py` - WebInterface class with methods like:
   - `navigate(url)`
   - `click(by, locator)`
   - `send_keys(by, locator, text)`
   - `is_element_visible(by, locator)`

**Fix:** This is expected for a new project. The code generator is correct - it generates code that WILL work once the framework is complete.

**Action:** Either:
- Option A: Create minimal WebInterface stub for testing
- Option B: Document as "Framework Prerequisites"
- Option C: Make code generator aware of missing infrastructure and generate stubs

---

## Test Plan After Fixes

1. Create minimal WebInterface stub (or complete framework implementation)
2. Update code generator with import path fixes
3. Generate fresh files with updated code generator
4. Copy to framework without modifications
5. Run pytest collection
6. Run actual test (will need real credentials/browser)
