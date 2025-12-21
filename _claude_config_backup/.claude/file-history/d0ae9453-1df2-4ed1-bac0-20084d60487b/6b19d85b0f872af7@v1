# Testing Skill

Define and enforce a consistent testing process. Project-agnostic.

## Purpose

This skill defines the testing **process**:
- When to run tests
- Command format and required flags
- Visual feedback requirements
- Failure handling protocol

For project-specific conventions (folder structures, report locations), see `references/conventions.md`.

## Core Principles

1. **Tests are mandatory** — No code complete without tests
2. **Visual progress required** — User sees real-time feedback
3. **Persistent reports required** — HTML report every run
4. **Failures require discussion** — Never auto-fix
5. **Defects are tracked** — Failures logged systematically

## When to Run Tests

| Trigger | Description |
|---------|-------------|
| Component complete | After finishing a feature/component |
| Manual request | User asks to run tests |
| Before commit | Recommended |

**Agent prompts:** "Should I run tests for this component?"

## Test Command Format

```bash
pytest {test_path} -v --html={report_path} --self-contained-html
```

| Placeholder | Resolved By |
|-------------|-------------|
| `{test_path}` | Project convention |
| `{report_path}` | Project convention |

**Required flags:**

| Flag | Purpose |
|------|---------|
| `-v` | Verbose (real-time test names + status) |
| `--html` | Generate HTML report |
| `--self-contained-html` | Single-file report |

**Optional flags:**

| Flag | Purpose |
|------|---------|
| `-s` | Show print output |
| `-x` | Stop on first failure |
| `--tb=short` | Shorter tracebacks |

## Visual Feedback Requirements

**During execution, user sees:**
- Test names as they run
- PASSED/FAILED per test
- Progress (percentage)

**After execution, user sees:**
- Summary (X passed, Y failed)
- Report file path
- Clear verdict

## Failure Protocol

**On ANY test failure, follow this sequence:**

| Step | Action |
|------|--------|
| 1. STOP | Halt work, do not auto-fix |
| 2. REPORT | Show: test name, error, location |
| 3. ANALYZE | Explain: expected vs actual, likely cause |
| 4. DISCUSS DEFECT | Ask user: "Create defect entry?" |
| 5. DISCUSS FIX | Ask user: "Proposed fix: X. Proceed?" |
| 6. FIX | Implement approved fix only |
| 7. RE-TEST | Run same tests again |
| 8. RESOLVE | Update defect status if tracked |

For detailed failure handling and defect format, see `references/failure-handling.md`.

## Anti-Patterns

| Wrong | Right |
|-------|-------|
| Skip tests | Run tests before marking complete |
| Silent failures | STOP and REPORT every failure |
| No HTML report | Generate report every run |
| Auto-fix without asking | Discuss with user first |
| Untracked failures | Create defect entry |
| Fix without re-testing | Re-run after every fix |

## References

- `references/conventions.md` — Folder structures, report locations by project type
- `references/failure-handling.md` — Detailed failure protocol, defect format, RCA template
