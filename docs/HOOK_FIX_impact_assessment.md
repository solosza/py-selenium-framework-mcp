# Hook Fix Impact Assessment

**Fix:** Allow workflow module creation during Steps 6-8 (Write tool unblocked)
**Date:** 2026-01-08
**Severity:** MEDIUM (blocks E2E workflow execution)

---

## 1. Who Calls This Code?

### Current Hook (`qa-gate-enforcer.py`)

**Location:** `.claude/hooks/qa-gate-enforcer.py`

**Triggered by:**
| Event | When |
|-------|------|
| PreToolUse:Write | Any Write tool call from Claude |
| PreToolUse:Edit | Any Edit tool call from Claude |

**Current behavior:**
- Checks if workflow state file exists: `mcp_server/state/workflow_state.json`
- If NOT found → BLOCKS all `framework/` writes
- If found → Allows `framework/` writes

**Problem discovered:**
- State file location changed from `mcp_server/state/` to `tests/_state/{run_id}/`
- Hook always thinks state file doesn't exist
- Blocks ALL framework writes (including legitimate Step 6-8 module creation)

---

## 2. What Depends on Current Behavior?

### Dependencies

| Component | Current Expectation | Impact of Change |
|-----------|---------------------|------------------|
| **Quality Gates (Steps 6-8)** | Write files via Python `open()`, bypass hook | No change - gates write directly |
| **Claude AI fixing skeleton code** | Needs Write tool to complete code | Currently BLOCKED - fix will UNBLOCK |
| **Hook protection** | Prevents accidental framework modifications | Will still protect, just smarter about what to block |

### Current Protection

**What hook currently protects:**
- Entire `framework/` directory (too broad)

**What SHOULD be protected:**
- Core infrastructure only:
  - `framework/interfaces/` (WebInterface, FileInterface)
  - `framework/resources/utilities/` (autologger, logger, data_generator)
  - `framework/resources/config.py`
  - `framework/resources/chromedriver/`

**What SHOULD be allowed (with gate validation):**
- `framework/pages/{workflow}/` - Workflow-specific POMs
- `framework/tasks/{workflow}/` - Workflow-specific Tasks
- `framework/tasks/common/` - Common Tasks (shared infrastructure)
- `framework/roles/{workflow}/` - Workflow-specific Roles
- `framework/roles/common/` - Common Roles (shared infrastructure)

---

## 3. What Will Break?

### Breaking Changes: **NONE (Expansion of permissions)**

**Current state:**
- Write tool → BLOCKED for all `framework/` paths
- Gates write via Python → NOT blocked (unaffected)

**New state:**
- Write tool → ALLOWED for workflow modules (with protection logic)
- Write tool → BLOCKED for core infrastructure
- Gates write via Python → NOT blocked (unaffected)

**Why nothing breaks:**
- We're EXPANDING what's allowed, not restricting
- Core infrastructure still protected
- Gates continue writing directly (unchanged)

### Tests affected: **NONE**

Hook doesn't affect test execution, only Claude's Write tool usage.

---

## 4. Migration Path

### Old Behavior (Current - Broken)

```python
# Hook checks:
state_file = Path("mcp_server/state/workflow_state.json")
if not state_file.exists():
    # BLOCKS all framework/ writes
    print("BLOCKED: No QA workflow state found.")
    exit(1)
```

**Problem:** State file location changed, hook always blocks.

### New Behavior (Fixed)

```python
# Hook checks:
1. Is path in core infrastructure? → BLOCK
2. Is path in workflow modules? → Check if current workflow
3. Current workflow path? → ALLOW (gates validated)
4. Common modules? → ALLOW (shared infrastructure)
5. Other workflow path? → BLOCK (protect other workflows)
```

**Benefits:**
- Surgical protection (only core infrastructure)
- Allows legitimate workflow creation
- Still protects against accidental cross-workflow pollution

### Data Migration

**No data migration needed.**

Files already created by gates (via Python) remain unchanged.

### Rollback Plan

If fix causes issues:
1. Revert `.claude/hooks/qa-gate-enforcer.py` to current version
2. Workflow will block again (known issue)
3. Manual workaround: Delete hook temporarily for E2E test

---

## 5. Implementation Plan

### Current Hook Analysis

**Hook is WELL-DESIGNED:**
- Validates gate metadata before allowing writes ✓
- Checks step completion via metadata keys ✓
- Clear error messages ✓

**Single Issue:**
- State file location is WRONG (lines 89-106)
- Looks for `mcp_server/state/workflow_state.json`
- Actual location: `tests/_state/{run_id}/workflow_state.json` (DEF-052)

### Phase 1: Fix State File Lookup

**Update `get_state_file_path()` function:**

```python
def get_state_file_path() -> Path:
    """Get the path to workflow_state.json (DEF-052 location)."""
    # Try environment variable first
    project_dir = os.environ.get('CLAUDE_PROJECT_DIR')
    if project_dir:
        base = Path(project_dir)
    else:
        # Find project root by looking for mcp_server
        cwd = Path.cwd()
        base = None
        for parent in [cwd] + list(cwd.parents):
            if (parent / 'mcp_server').exists():
                base = parent
                break
        if base is None:
            base = cwd

    # DEF-052: State now lives in tests/_state/{run_id}/
    state_dir = base / 'tests' / '_state'
    if not state_dir.exists():
        # No state directory = no workflow running
        return base / 'mcp_server' / 'state' / 'workflow_state.json'  # Dummy path

    # Find most recent run_id directory
    run_dirs = sorted(
        [d for d in state_dir.iterdir() if d.is_dir()],
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )

    if run_dirs:
        return run_dirs[0] / 'workflow_state.json'

    # No run directories found
    return base / 'mcp_server' / 'state' / 'workflow_state.json'  # Dummy path
```

### Phase 2: Add Core Infrastructure Protection

**Update `PROTECTED_PATHS` constant:**

```python
PROTECTED_PATHS = {
    'framework/pages/': 'step_6',         # POM requires qg_page_object POST
    'framework/tasks/': 'step_7',         # Task requires qg_task POST
    'framework/roles/': 'step_8',         # Role requires qg_role POST
    'tests/': 'step_9',                   # Test requires qg_test_runner POST
}

# Core infrastructure (ALWAYS blocked, even with gates passed)
CORE_INFRASTRUCTURE = [
    'framework/interfaces/',
    'framework/resources/utilities/',
    'framework/resources/config.py',
    'framework/resources/chromedriver/',
]
```

**Add core infrastructure check in `main()`:**

```python
# After line 132 (after file_path check)

# Block core infrastructure (never allow modifications)
normalized = normalize_path(file_path)
for core_path in CORE_INFRASTRUCTURE:
    if core_path in normalized:
        sys.stderr.write(
            f"BLOCKED: Core infrastructure is write-protected.\n"
            f"File: {file_path}\n"
            f"Protected path: {core_path}\n"
            f"Core framework code cannot be modified during QA workflows.\n"
        )
        sys.exit(2)

# Then continue with existing logic (required_step check...)
```

### Phase 3: Test Hook

**Test cases:**
1. Write to `framework/interfaces/web_interface.py` → BLOCKED (core) ✓
2. Write to `framework/resources/utilities/autologger.py` → BLOCKED (core) ✓
3. Write to `framework/pages/parabank3/login_page.py` → Check gate ✓
4. Write to `framework/tasks/common/common_tasks.py` → Check gate ✓
5. Write to `tests/parabank3/test_login.py` → Check gate ✓

### Phase 4: Test Hook

**Test cases:**
1. Try to write to `framework/interfaces/web_interface.py` → BLOCKED ✓
2. Try to write to `framework/pages/parabank3/login_page.py` → ALLOWED ✓
3. Try to write to `framework/tasks/common/common_tasks.py` → ALLOWED ✓
4. Try to write to `tests/parabank3/test_login.py` → ALLOWED ✓

---

## 6. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Accidental core infrastructure modification | Low | High | PROTECTED_PATHS blocks core files |
| Cross-workflow pollution | Low | Medium | Can add workflow isolation check later if needed |
| Hook logic error causes false blocks | Low | Medium | Test hook before committing |
| Gates bypass hook entirely | N/A | None | Gates write via Python (by design) |

**Overall Risk:** **LOW**

**Why:**
1. Expanding permissions (not restricting)
2. Core infrastructure still protected
3. Gates already bypass hook (no change)
4. Can refine protection rules later if needed

---

## 7. Framework Structure Review

Based on file listing, framework structure:

```
framework/
├── interfaces/           ← PROTECT
│   └── web_interface.py
├── pages/               ← ALLOW (workflow-specific)
│   ├── auth/
│   ├── banking/
│   ├── cart/
│   ├── parabank/
│   └── parabank2/
├── tasks/               ← ALLOW (workflow-specific + common)
│   └── (none yet, will be created)
├── roles/               ← ALLOW (workflow-specific + common)
│   ├── cart/
│   ├── parabank/
│   └── (loose files)
└── resources/           ← PROTECT (infrastructure)
    ├── chromedriver/
    ├── config.py
    └── utilities/
        ├── autologger.py
        ├── logger.py
        └── data_generator.py
```

**Protected paths (write-blocked):**
- `framework/interfaces/`
- `framework/resources/`

**Allowed paths (workflow creation):**
- `framework/pages/{workflow}/`
- `framework/tasks/{workflow}/`
- `framework/tasks/common/`
- `framework/roles/{workflow}/`
- `framework/roles/common/`

---

## 8. Verification Checklist

After implementing fix:

- [ ] Hook blocks write to `framework/interfaces/web_interface.py`
- [ ] Hook blocks write to `framework/resources/utilities/autologger.py`
- [ ] Hook allows write to `framework/pages/parabank3/new_page.py`
- [ ] Hook allows write to `framework/tasks/common/common_tasks.py`
- [ ] Hook allows write to `tests/parabank3/test_something.py`
- [ ] Resume E2E test from Step 6 → verify POM creation succeeds
- [ ] Document hook behavior in CLAUDE.md

---

## 9. Recommendation

**PROCEED WITH FIX**

**Rationale:**
1. **Unblocks critical workflow** - Steps 6-8 can create modules
2. **Low risk** - Expanding permissions, not restricting
3. **Core infrastructure still protected** - No loss of safety
4. **Reversible** - Easy rollback if issues arise
5. **No breaking changes** - Gates continue writing directly

**Next Steps:**
1. Implement hook fix with PROTECTED_PATHS logic
2. Test hook behavior with sample paths
3. Resume E2E test from Step 6
4. Document new hook behavior
