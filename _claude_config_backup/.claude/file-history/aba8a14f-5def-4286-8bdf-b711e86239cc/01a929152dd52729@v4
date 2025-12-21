# Defect Log - Framework Audit

**Project:** py_sel_framework_mcp
**Audit Start Date:** 2025-11-29
**Status:** In Progress

---

## Severity Definitions

| Severity | Description | Action Required |
|----------|-------------|-----------------|
| **CRITICAL** | Architecture violation - breaks 4-layer pattern | Fix immediately, blocks audit progress |
| **HIGH** | Wrong responsibility - code in wrong layer | Fix before completing parent task |
| **MEDIUM** | Missing elements - incomplete implementation | Fix during parent task |
| **LOW** | Style/naming - conventions not followed | Fix if time permits |

---

## Status Options

| Status | Description |
|--------|-------------|
| **OPEN** | Defect identified, not yet addressed |
| **IN_PROGRESS** | Currently being fixed |
| **RESOLVED** | Fix applied and verified |
| **WONT_FIX** | Intentionally not fixing (with justification) |

---

## Defect Entry Template

```markdown
### [DEF-XXX] Brief Description
**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Status:** OPEN | IN_PROGRESS | RESOLVED | WONT_FIX
**Layer:** Page | Task | Role | Test
**File:** `path/to/file.py`
**Line(s):** XX-XX

**Rule Violated:**
- [Which architectural rule was broken]

**Description:**
[What is wrong and why it's a problem]

**Fix:**
[How it was fixed, or how it should be fixed]

**Resolved Date:** YYYY-MM-DD (if resolved)
```

---

## Defects

### Page Object Layer (Task 2.0)

### [DEF-001] Composite methods in RegistrationPage belong in Task layer
**Severity:** HIGH
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/registration_page.py`
**Line(s):** 375-448

**Rule Violated:**
- POM methods must be atomic (one UI action per method)
- Composite workflows belong in Task layer

**Description:**
`fill_registration_form()` and `register_user()` are composite methods that orchestrate multiple field entries. This is Task-layer responsibility, not POM.

**Fix:**
Remove these methods from POM. Tasks should call individual atomic methods.

---

### [DEF-002] LoginPage missing state-check methods
**Severity:** MEDIUM
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/login_page.py`
**Line(s):** N/A

**Rule Violated:**
- POMs should have state-check methods for assertions

**Description:**
LoginPage has no state-check methods (is_page_loaded, is_error_displayed, etc.). Tests cannot verify state through this POM.

**Fix:**
Add state-check methods: `is_page_loaded()`, `has_error_message()`, `get_error_message()`.

---

### [DEF-003] RegistrationPage methods return None instead of self
**Severity:** MEDIUM
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/registration_page.py`
**Line(s):** 82-88, 121-149, 191-209, 233-249, 251-258, etc.

**Rule Violated:**
- POM methods should return `self` for fluent chaining

**Description:**
Many methods have `-> None` return type or no return statement, breaking fluent chaining pattern. Examples: `select_gender_mr()`, `enter_customer_firstname()`, `check_newsletter()`, etc.

**Fix:**
Update all action methods to return `self` with proper type hints.

---

### [DEF-004] BasePage.search() is composite method
**Severity:** MEDIUM
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/base_page.py`
**Line(s):** 99-108

**Rule Violated:**
- POM methods must be atomic (one UI action per method)

**Description:**
`search()` combines `enter_search_query()` + `click_search_button()`. Should be atomic.

**Fix:**
Remove composite `search()` method. Callers should use individual methods.

---

### [DEF-005] HomePage.search_for() is composite method
**Severity:** MEDIUM
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/common/home_page.py`
**Line(s):** 156-171

**Rule Violated:**
- POM methods must be atomic (one UI action per method)

**Description:**
`search_for()` combines type_text + send_keys(RETURN). Should be atomic.

**Fix:**
Split into `enter_search_term()` and `submit_search()` methods.

---

### [DEF-006] LoginPage locator naming convention violation
**Severity:** LOW
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/login_page.py`
**Line(s):** 31

**Rule Violated:**
- Locators should use UPPER_SNAKE_CASE

**Description:**
`SUBMITLOGIN` should be `SUBMIT_LOGIN` per naming convention.

**Fix:**
Rename to `SUBMIT_LOGIN`.

---

### [DEF-007] AuthenticationPage missing return type hints
**Severity:** LOW
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/auth/authentication_page.py`
**Line(s):** 62-131

**Rule Violated:**
- Methods should have explicit return type hints

**Description:**
Several methods document "Returns: self for method chaining" but lack type hints.

**Fix:**
Add `-> "AuthenticationPage"` return type hints to all chaining methods.

---

### [DEF-008] ProductListPage uses explicit time.sleep()
**Severity:** LOW
**Status:** WONT_FIX
**Layer:** Page
**File:** `framework/pages/catalog/product_list_page.py`
**Line(s):** 135, 146, 157, 168, 197, 203, 208, 210, 237, 344

**Rule Violated:**
- Prefer WebInterface wait methods over explicit sleeps

**Description:**
Multiple `time.sleep()` calls for AJAX waits. Should use explicit waits where possible.

**Fix:**
WONT_FIX: time.sleep() is acceptable for complex AJAX interactions where explicit wait conditions are unreliable. These sleeps handle sorting/filtering AJAX reloads.

---

### [DEF-009] BasePage violates "No Inheritance" design decision
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** Page
**File:** `framework/pages/base_page.py`
**Line(s):** All

**Rule Violated:**
- PRD Section 6.5: "No Inheritance - use composition, no base classes"

**Description:**
BasePage exists and all POMs inherit from it. This violates the explicit "No Inheritance" design decision. POMs should compose WebInterface directly, not inherit from a base class.

**Fix:**
1. Deleted `framework/pages/base_page.py`
2. Updated all POMs to compose WebInterface directly (no inheritance)
3. Header elements already exist in HomePage

**Resolved Date:** 2025-11-29

---

### [DEF-010] Base Role violates "No Inheritance" design decision
**Severity:** CRITICAL
**Status:** RESOLVED
**Layer:** Role
**File:** `framework/roles/base/role.py`
**Line(s):** All

**Rule Violated:**
- PRD Section 6.5: "No Inheritance - use composition, no base classes"

**Description:**
Base Role class exists and all Roles inherit from it. This violates the explicit "No Inheritance" design decision. Roles should compose Tasks directly, not inherit from a base class.

**Fix:**
1. Deleted `framework/roles/base/role.py`
2. Updated RegisteredUser and GuestUser to be standalone classes (no inheritance)
3. Each Role now stores its own user_data and composes Tasks directly

**Resolved Date:** 2025-11-29

---

### Task Layer (Task 3.0)

_No defects logged yet._

---

### Role Layer (Task 4.0)

_No defects logged yet._

---

### Test Layer (Task 5.0)

_No defects logged yet._

---

## Summary

| Layer | CRITICAL | HIGH | MEDIUM | LOW | Total | Resolved |
|-------|----------|------|--------|-----|-------|----------|
| Page Objects | 1 | 1 | 4 | 3 | 9 | 8 (1 WONT_FIX) |
| Tasks | 0 | 0 | 0 | 0 | 0 | 0 |
| Roles | 1 | 0 | 0 | 0 | 1 | 1 |
| Tests | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total** | **2** | **1** | **4** | **3** | **10** | **9 + 1 WONT_FIX** |

---

## Audit Progress

- [x] Task 2.0: Page Objects audited
- [ ] Task 3.0: Tasks audited
- [ ] Task 4.0: Roles audited
- [ ] Task 5.0: Tests audited
- [ ] Task 6.0: All tests passing

---

**Last Updated:** 2025-11-29
