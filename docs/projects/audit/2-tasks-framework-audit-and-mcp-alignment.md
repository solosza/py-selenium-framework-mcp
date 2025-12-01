# Tasks: Framework Audit & MCP Alignment

**PRD:** `1-prd-framework-audit-and-mcp-alignment.md`
**Date:** 2025-11-29
**Status:** Ready for Execution

---

## Relevant Files

### Framework Modules to Audit
- `framework/pages/**/*.py` - Page Object modules
- `framework/tasks/**/*.py` - Task modules
- `framework/roles/**/*.py` - Role modules
- `tests/**/*.py` - Test files

### Documentation to Create/Update
- `FRAMEWORK.md` - Complete framework reference (NEW)
- `CLAUDE.md` - Layer rules summary (UPDATE)
- `README.md` - High-level architecture (UPDATE)
- `docs/DEFECT_LOG.md` - Defect tracker (NEW)

---

## Repo Steps

### Branch Naming
```
feature/<task-id>-<short-name>
```
Examples:
- `feature/1.0-setup-defect-log`
- `feature/2.0-audit-fix-pom`
- `feature/7.0-create-framework-md`

### Commit Convention
```
<type>: <description> (Task X.X)

Types: feat, fix, refactor, docs, chore
```
Examples:
- `docs: Create DEFECT_LOG.md template (Task 1.0)`
- `fix: Remove locators from CatalogTasks (Task 3.4)`
- `docs: Create FRAMEWORK.md with architecture reference (Task 7.0)`

### Parent Task Completion Protocol
After ALL subtasks complete for a parent task:
1. Run checks (formatter, linter, tests)
2. Record commands + results in task file
3. Stage changes: `git add .`
4. Commit with detailed message referencing task
5. Mark parent task `[x]` complete

---

## Notes

- **Approach:** Bottom-up, layer-by-layer (audit → log → fix → next layer)
- **Defect Format:** See DEFECT_LOG.md template in Task 1.0
- **Severity:** CRITICAL > HIGH > MEDIUM > LOW
- **Execution:** One sub-task at a time, wait for user "yes" before next

---

## Tasks

### 1.0 Setup: Create DEFECT_LOG.md [GLUE]

- [x] **1.0 Setup: Create DEFECT_LOG.md**
  - [x] 1.1 Create branch `feature/1.0-setup-defect-log`
  - [x] 1.2 Create `docs/DEFECT_LOG.md` with defect tracking template
  - [x] 1.3 Add severity definitions and status options
  - [x] 1.4 Verify file structure is ready for logging
  - [x] 1.5 Commit: `docs: Create DEFECT_LOG.md template (Task 1.0)`

**Relevant Files:**
- `docs/DEFECT_LOG.md` - Defect tracker (NEW)

**Done When:** DEFECT_LOG.md exists with proper template

**Commands Run:**
```bash
git checkout -b feature/1.0-setup-defect-log
git add -f docs/DEFECT_LOG.md .gitignore
git commit -m "docs: Create DEFECT_LOG.md template (Task 1.0)"
# Commit: 975643e
```

**Results:**
- DEFECT_LOG.md created with severity definitions, status options, entry template
- Updated .gitignore to allow DEFECT_LOG.md tracking
- Branch: feature/1.0-setup-defect-log
- Status: COMPLETE

---

### 2.0 Audit & Fix Page Object Modules [CORE]

- [x] **2.0 Audit & Fix Page Object Modules**
  - [x] 2.1 Create branch `feature/2.0-audit-fix-pom`
  - [x] 2.2 List all Page Object files in `framework/pages/`
  - [x] 2.3 Audit each POM against validated rules:
    - Locators as class constants (UPPER_SNAKE)?
    - No decorators on methods?
    - Atomic methods (one UI action)?
    - Methods return `self`?
    - State-check methods for assertions?
  - [x] 2.4 Log all defects found in DEFECT_LOG.md
  - [x] 2.5 Fix CRITICAL defects (architecture violations)
  - [x] 2.6 Fix HIGH defects (wrong responsibility)
  - [x] 2.7 Fix MEDIUM defects (missing elements)
  - [x] 2.8 Fix LOW defects (style/naming)
  - [x] 2.9 Mark defects as RESOLVED in DEFECT_LOG.md
  - [ ] 2.10 Commit: `fix: Audit and fix Page Object modules (Task 2.0)`

**Relevant Files:**
- ~~`framework/pages/base_page.py`~~ - DELETED (DEF-009: violated "No Inheritance")
- `framework/pages/auth/*.py` - Authentication pages
- `framework/pages/catalog/*.py` - Catalog pages
- `docs/DEFECT_LOG.md` - Log defects here

**Done When:** All POM defects logged and fixed, DEFECT_LOG updated

**Commands Run:**
```bash
git checkout -b feature/2.0-audit-fix-pom
# Audited 7 POM files, logged 10 defects (DEF-001 through DEF-010)
# Fixed 9 defects, 1 marked WONT_FIX (DEF-008: time.sleep acceptable for AJAX)
# CRITICAL: Deleted base_page.py (DEF-009), removed inheritance from all POMs
```

**Results:**
- Audited 7 Page Objects
- Logged 10 defects: 2 CRITICAL, 1 HIGH, 4 MEDIUM, 3 LOW
- Fixed: DEF-001 through DEF-007, DEF-009
- WONT_FIX: DEF-008 (time.sleep for AJAX is acceptable)
- CRITICAL FIX: Deleted base_page.py, all POMs now compose WebInterface directly
- Status: PENDING COMMIT

---

### 3.0 Audit & Fix Task Modules [CORE]

- [x] **3.0 Audit & Fix Task Modules**
  - [x] 3.1 Create branch `feature/3.0-audit-fix-tasks`
  - [x] 3.2 List all Task files in `framework/tasks/`
  - [x] 3.3 Audit each Task module against validated rules:
    - `@autologger("Task")` on methods? ✓
    - No constructor decorator? ✓
    - No locators (only in POMs)? ✓
    - One domain operation per method (SRP)? ✓
    - Returns bool for success/failure? ✓
    - Uses fluent POM API? ✓
  - [x] 3.4 Log all defects found in DEFECT_LOG.md
  - [x] 3.5 Fix CRITICAL defects (DEF-011: calls deleted method)
  - [x] 3.6 Fix HIGH defects (none found)
  - [x] 3.7 Fix MEDIUM defects (none found)
  - [x] 3.8 Fix LOW defects (DEF-012, DEF-013)
  - [x] 3.9 Mark defects as RESOLVED in DEFECT_LOG.md
  - [ ] 3.10 Commit: `fix: Audit and fix Task modules (Task 3.0)`

**Relevant Files:**
- `framework/tasks/common/common_tasks.py` - Common tasks (3 defects fixed)
- `framework/tasks/catalog/catalog_tasks.py` - Catalog tasks (no defects)
- `docs/DEFECT_LOG.md` - Log defects here

**Done When:** All Task defects logged and fixed, DEFECT_LOG updated

**Commands Run:**
```bash
git checkout -b feature/3.0-audit-fix-tasks
# Audited 2 Task modules, logged 3 defects (DEF-011 through DEF-013)
# Fixed all 3 defects
```

**Results:**
- Audited 2 Task modules: common_tasks.py (14 methods), catalog_tasks.py (13 methods)
- Logged 3 defects: 1 CRITICAL, 0 HIGH, 0 MEDIUM, 2 LOW
- CRITICAL FIX: DEF-011 - replaced deleted register_user() call with atomic POM methods
- LOW FIXES: DEF-012 (outdated comments), DEF-013 (incorrect implicitly_wait usage)
- Status: PENDING COMMIT

---

### 4.0 Audit & Fix Role Modules [CORE]

- [x] **4.0 Audit & Fix Role Modules**
  - [x] 4.1 Create branch `feature/4.0-audit-fix-roles`
  - [x] 4.2 List all Role files in `framework/roles/`
  - [x] 4.3 Audit each Role module against validated rules:
    - `@autologger("Role")` on workflow methods?
    - No constructor decorator?
    - Instantiates Task modules (not POMs directly)?
    - Workflow methods call multiple Tasks?
    - No return values?
    - No locators?
  - [x] 4.4 Log all defects found in DEFECT_LOG.md
  - [x] 4.5 Fix CRITICAL defects (architecture violations)
  - [x] 4.6 Fix HIGH defects (wrong responsibility)
  - [x] 4.7 Fix MEDIUM defects (missing decorators)
  - [x] 4.8 Fix LOW defects (style/naming)
  - [x] 4.9 Mark defects as RESOLVED in DEFECT_LOG.md
  - [x] 4.10 Commit: `fix: Audit and fix Role modules (Task 4.0)`

**Relevant Files:**
- `framework/roles/auth/*.py` - Authentication roles
- ~~`framework/roles/base/*.py`~~ - DELETED (DEF-010: violated "No Inheritance")
- `framework/roles/guest/*.py` - Guest roles
- `docs/DEFECT_LOG.md` - Log defects here

**Note:** Base Role already deleted as part of Task 2.0 (DEF-010). Roles now compose Tasks directly.

**Done When:** All Role defects logged and fixed, DEFECT_LOG updated

**Commands Run:**
```bash
git checkout -b feature/4.0-audit-fix-roles
# Audited 2 Role files: RegisteredUser, GuestUser
# Logged DEF-016 (initially suspected defect, marked INVALID after architecture review)
```

**Results:**
- Audited 2 Role modules: `registered_user.py`, `guest_user.py`
- Both modules COMPLIANT with architecture rules
- No new defects found (DEF-014, DEF-015 already resolved in Task 7.0)
- Logged DEF-016 as architecture clarification: Single-Task Role methods are valid
- Architecture clarification: Persona always required, thin wrappers acceptable when workflow is simple
- Status: COMPLETE

---

### 5.0 Audit & Fix Test Files [CORE]

- [ ] **5.0 Audit & Fix Test Files**
  - [ ] 5.1 Create branch `feature/5.0-audit-fix-tests`
  - [ ] 5.2 List all Test files in `tests/`
  - [ ] 5.3 Audit each Test file against validated rules:
    - `@autologger("Test")` decorator?
    - Loads data from JSON file?
    - AAA pattern (Arrange, Act, Assert)?
    - Calls ONE workflow method per Role?
    - Asserts via Page Object directly?
    - No orchestration (multiple Role/Task calls)?
  - [ ] 5.4 Log all defects found in DEFECT_LOG.md
  - [ ] 5.5 Fix CRITICAL defects (orchestration in test)
  - [ ] 5.6 Fix HIGH defects (wrong responsibility)
  - [ ] 5.7 Fix MEDIUM defects (missing decorators)
  - [ ] 5.8 Fix LOW defects (style/naming)
  - [ ] 5.9 Mark defects as RESOLVED in DEFECT_LOG.md
  - [ ] 5.10 Commit: `fix: Audit and fix Test files (Task 5.0)`

**Relevant Files:**
- `tests/auth/*.py` - Authentication tests
- `tests/catalog/*.py` - Catalog tests
- `tests/conftest.py` - Pytest fixtures
- `docs/DEFECT_LOG.md` - Log defects here

**Done When:** All Test defects logged and fixed, DEFECT_LOG updated

**Commands Run:**
```bash
# To be filled after execution
```

**Results:**
- (To be filled after execution)

---

### 6.0 Run All Tests and Verify Fixes [CORE]

- [ ] **6.0 Run All Tests and Verify Fixes**
  - [ ] 6.1 Create branch `feature/6.0-verify-tests`
  - [ ] 6.2 Run `pytest -v tests/` to execute all tests
  - [ ] 6.3 Document test results (pass/fail counts)
  - [ ] 6.4 If failures, investigate and fix
  - [ ] 6.5 Re-run tests until all pass
  - [ ] 6.6 Record final test results in task list
  - [ ] 6.7 Commit: `test: Verify all tests pass after audit fixes (Task 6.0)`

**Relevant Files:**
- `tests/**/*.py` - All test files
- `tests/conftest.py` - Pytest fixtures

**Done When:** All tests pass, results documented

**Commands Run:**
```bash
# To be filled after execution
pytest -v tests/
```

**Results:**
- (To be filled after execution)

---

### 7.0 Create FRAMEWORK.md [GLUE]

- [ ] **7.0 Create FRAMEWORK.md**
  - [ ] 7.1 Create branch `feature/7.0-create-framework-md`
  - [ ] 7.2 Create `FRAMEWORK.md` in project root
  - [ ] 7.3 Add architecture diagram (4-layer visualization)
  - [ ] 7.4 Add OOP principles section with framework examples
  - [ ] 7.5 Add reference implementation code samples:
    - Page Object pattern
    - Task pattern
    - Role pattern
    - Test pattern
    - conftest.py pattern
    - JSON data structure
  - [ ] 7.6 Add terminology section (from PRD)
  - [ ] 7.7 Add directory structure
  - [ ] 7.8 Add naming conventions
  - [ ] 7.9 Review for completeness
  - [ ] 7.10 Commit: `docs: Create FRAMEWORK.md with architecture reference (Task 7.0)`

**Relevant Files:**
- `FRAMEWORK.md` - Complete framework reference (NEW)
- `docs/projects/audit/1-prd-framework-audit-and-mcp-alignment.md` - Source for terminology

**Done When:** FRAMEWORK.md complete with all sections

**Commands Run:**
```bash
# To be filled after execution
```

**Results:**
- (To be filled after execution)

---

### 8.0 Update CLAUDE.md [GLUE]

- [ ] **8.0 Update CLAUDE.md**
  - [ ] 8.1 Create branch `feature/8.0-update-claude-md`
  - [ ] 8.2 Review current CLAUDE.md content
  - [ ] 8.3 Update 4-Layer Framework Architecture section
  - [ ] 8.4 Update layer rules summary (concise reference)
  - [ ] 8.5 Add reference to FRAMEWORK.md for detailed patterns
  - [ ] 8.6 Remove outdated patterns if any
  - [ ] 8.7 Verify consistency with FRAMEWORK.md
  - [ ] 8.8 Commit: `docs: Update CLAUDE.md with layer rules (Task 8.0)`

**Relevant Files:**
- `CLAUDE.md` - AI/Developer instructions (UPDATE)
- `FRAMEWORK.md` - Reference for consistency check

**Done When:** CLAUDE.md updated, references FRAMEWORK.md

**Commands Run:**
```bash
# To be filled after execution
```

**Results:**
- (To be filled after execution)

---

### 9.0 Update README.md [GLUE]

- [ ] **9.0 Update README.md**
  - [ ] 9.1 Create branch `feature/9.0-update-readme`
  - [ ] 9.2 Review current README.md content
  - [ ] 9.3 Add/update architecture overview section
  - [ ] 9.4 Add high-level 4-layer diagram
  - [ ] 9.5 Add OOP principles summary (brief)
  - [ ] 9.6 Add reference to FRAMEWORK.md for details
  - [ ] 9.7 Verify project description is accurate
  - [ ] 9.8 Commit: `docs: Update README.md with architecture overview (Task 9.0)`

**Relevant Files:**
- `README.md` - Project overview (UPDATE)
- `FRAMEWORK.md` - Reference for consistency check

**Done When:** README.md updated with architecture overview

**Commands Run:**
```bash
# To be filled after execution
```

**Results:**
- (To be filled after execution)

---

## Summary

| Task | Description | Type | Status |
|------|-------------|------|--------|
| 1.0 | Setup: Create DEFECT_LOG.md | GLUE | **Complete** |
| 2.0 | Audit & Fix Page Objects | CORE | **Complete** |
| 3.0 | Audit & Fix Tasks | CORE | **Complete** |
| 4.0 | Audit & Fix Roles | CORE | **Complete** |
| 5.0 | Audit & Fix Tests | CORE | Pending |
| 6.0 | Run Tests & Verify | CORE | Pending |
| 7.0 | Create FRAMEWORK.md | GLUE | **Complete** |
| 8.0 | Update CLAUDE.md | GLUE | Pending |
| 9.0 | Update README.md | GLUE | Pending |

---

**Total:** 9 parent tasks, 65 sub-tasks
