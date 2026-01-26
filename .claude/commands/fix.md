---
description: Run impact assessment before implementing a fix
---

# Fix Command

Run impact assessment before implementing any fix to existing code.

## Usage

```
/fix the hook isn't creating transcripts
/fix function X returns wrong value
/fix
```

## Instructions

**Read and apply: `.claude/skills/fix-workflow/SKILL.md`**

### Step 1: Understand the Fix

If `$ARGUMENTS` provided, that's the fix description.
If empty, ask user: "What needs to be fixed?"

### Step 2: Impact Assessment (MANDATORY)

Before writing ANY code, complete ALL four:

#### 2.1 Who calls this code?

```bash
grep -r "function_or_class_name" --include="*.py" .
```

Show all callers found.

#### 2.2 What depends on current behavior?

- List test files covering this code
- List other components that import/use this

#### 2.3 What will break?

Explicit list:
- Tests that will fail
- Integrations affected
- Assumptions broken

If nothing, state: "No breaking changes identified"

#### 2.4 Migration path?

- Backward compatible? Yes/No + why
- Old data handling needed?

### Step 3: Present Assessment

Show summary using this format:

```
## Impact Assessment: [Fix description]

### 1. Callers
- `file.py:123` - calls this
- `other.py:45` - uses this

### 2. Dependencies
- Tests: `test_x.py` (N tests)
- Components: `module_a.py`, `module_b.py`

### 3. What Breaks
- `test_old_behavior` - expects X, will get Y
- (or "None identified")

### 4. Migration
- Backward compatible: Yes/No
- Reason: [explanation]

**Proceed with fix?**
```

### Step 4: Wait for Approval

Do NOT implement until user explicitly approves.

### Step 5: Implement Fix

After approval:
1. Make the code changes
2. Run affected tests
3. Report results

## Example

```
User: /fix the hook isn't creating transcripts

Claude: ## Impact Assessment: Hook not creating transcripts

### 1. Callers
- Hook is triggered by PostToolUse on `mcp__qa-automation__qg_*`
- No direct code callers (event-driven)

### 2. Dependencies
- Tests: `test_hook_audit_trail_writer.py` (16 tests)
- Components: `TranscriptWriter` (not currently called)

### 3. What Breaks
- None - adding new functionality

### 4. Migration
- Backward compatible: Yes
- Reason: Adding TranscriptWriter call, existing audit log behavior unchanged

**Proceed with fix?**

User: yes

Claude: [implements fix, runs tests]
```
