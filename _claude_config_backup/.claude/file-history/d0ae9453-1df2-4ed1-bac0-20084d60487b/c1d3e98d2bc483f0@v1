# Failure Handling

Detailed protocol for handling test failures, root cause analysis, and defect tracking.

## Failure Protocol (Expanded)

### Step 1: STOP

**What to do:**
- Immediately halt current work
- Do not proceed to next task
- Do not attempt fixes without analysis

**Why:** Prevents cascading issues, ensures focused debugging.

### Step 2: REPORT

**Present to user:**

```
FAILURE DETECTED
================
Test: {test_name}
File: {file_path}:{line_number}

Error Type: {AssertionError, TypeError, etc.}
Message: {error message}

Traceback (shortened):
{relevant stack trace}
```

**Include:**
- Exact test that failed
- File and line number
- Error type and message
- Relevant traceback (use `--tb=short` for concise output)

### Step 3: ROOT CAUSE ANALYSIS

**Explain to user:**

```
ROOT CAUSE ANALYSIS
===================
Expected: {what test expected}
Actual: {what actually happened}

Likely Cause:
{Your analysis of why this failed}

Affected Components:
- {component 1}
- {component 2}
```

**Analysis checklist:**
- [ ] Is this a test bug or code bug?
- [ ] Is the assertion correct?
- [ ] Did dependencies change?
- [ ] Is test data correct?
- [ ] Is environment correct?

### Step 4: DISCUSS DEFECT

**Prompt user:**

> "Should I create a defect entry for this failure? (Y/N)"

**If yes, proceed to create defect. If no, skip to Step 5.**

### Step 5: DISCUSS FIX

**Present proposed fix:**

```
PROPOSED FIX
============
Problem: {brief description}

Solution: {what you propose to do}

Files to modify:
- {file 1}: {change description}
- {file 2}: {change description}

Proceed with this fix? (Y/N)
```

**Wait for user approval before implementing.**

### Step 6: FIX

- Implement only the approved fix
- Make minimal changes
- Do not refactor unrelated code

### Step 7: RE-TEST

- Run the exact same test(s) that failed
- Verify the fix works
- Check for regressions if applicable

### Step 8: RESOLVE

If defect was created, update status:

```markdown
**Status:** RESOLVED
**Resolution:** {what was fixed}
**Verified:** {date}
```

## Defect Entry Format

```markdown
### DEF-{XXX}: {Brief Description}

**Date:** YYYY-MM-DD
**Test:** {full test path}
**Component:** {affected component}

**Error:**
```
{exact error message}
```

**Root Cause:**
{analysis of what caused the failure}

**Attempted Fixes:**
1. {first attempt} - {result}
2. {second attempt} - {result}

**Solution:**
{what ultimately fixed it}

**Status:** OPEN | IN_PROGRESS | RESOLVED | BLOCKED

**Resolution:** {if resolved, what was the fix}
**Verified:** {date verified}

**Prevention:**
{how to prevent this in future, if applicable}
```

## Defect ID Convention

- Format: `DEF-{NNN}`
- Sequential numbering: DEF-001, DEF-002, etc.
- Project-specific: Each project tracks its own sequence

## Common Failure Categories

| Category | Typical Cause | Typical Fix |
|----------|---------------|-------------|
| AssertionError | Logic bug or wrong expectation | Fix code or update test |
| AttributeError | Missing attribute/method | Check object initialization |
| ImportError | Wrong import path | Fix import statement |
| FileNotFoundError | Missing file or wrong path | Create file or fix path |
| TimeoutError | Slow operation or stuck process | Increase timeout or fix hang |
| TypeError | Wrong argument type | Fix type mismatch |

## When NOT to Create Defect

- Test environment issue (not code bug)
- User error (wrong command, missing dependency)
- Known/expected failure during development
- Duplicate of existing defect

**Ask user if unsure.**

## Escalation

If failure cannot be resolved after reasonable effort:

1. Document what was tried
2. Create/update defect with BLOCKED status
3. Discuss with user for guidance
4. Do not proceed without resolution path
