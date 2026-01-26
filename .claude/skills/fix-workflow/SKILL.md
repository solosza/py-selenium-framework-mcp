# Fix Workflow

**Trigger:** `/fix` command or any request to fix existing code

**Purpose:** Ensure impact assessment before implementing fixes to prevent regressions.

---

## Impact Assessment (MANDATORY)

Before writing ANY code, answer ALL four questions:

### 1. Who calls this code?

```bash
# Run search, show results
grep -r "function_name" --include="*.py"
```

List all callers found.

### 2. What depends on current behavior?

- **Tests:** List test files that cover this code
- **Components:** List other modules that import/use this

### 3. What will break?

Explicit list:
- [ ] Test X will fail because...
- [ ] Component Y assumes...
- [ ] Integration Z depends on...

If nothing breaks, state: "No breaking changes identified"

### 4. Migration path?

- **Backward compatible?** Yes/No
- **Why:** Explain reasoning
- **Old data:** Any existing data that needs handling?

---

## Workflow

```
1. User invokes /fix (or requests a fix)
2. STOP - Do not implement yet
3. Run impact assessment
   - Search for callers
   - List tests
   - Identify what breaks
   - Check migration needs
4. Present assessment summary to user
5. WAIT for explicit approval ("proceed", "yes", etc.)
6. Implement fix
7. Run affected tests
8. Report results
```

---

## Assessment Template

When presenting to user, use this format:

```
## Impact Assessment: [Brief description of fix]

### 1. Callers
- `file.py:123` - function_a() calls this
- `other.py:45` - class_b uses this

### 2. Dependencies
- Tests: `test_file.py` (15 tests)
- Components: `module_x.py`, `module_y.py`

### 3. What Breaks
- [ ] `test_old_behavior` - expects old return value
- [x] Nothing else identified

### 4. Migration
- Backward compatible: Yes
- Reason: New behavior is additive, old interface unchanged

---

**Proceed with fix?**
```

---

## When to Use

- Bug fixes
- Refactoring existing code
- Changing function signatures
- Modifying shared utilities
- Updating hooks or gates

## When NOT Required

- New files (no existing callers)
- Documentation only
- Test-only changes (unless changing test utilities)
