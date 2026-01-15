# Knowledge Base

Patterns and solutions for complex test automation challenges.

---

## Table of Contents

1. [User-Guided Workflow Discovery (Golden Standard)](#user-guided-workflow-discovery-golden-standard)
2. [Complex Workflow Investigation Protocol](#complex-workflow-investigation-protocol)
3. [Specific Patterns](#specific-patterns)
   - [Conditional Workflow Paths](#conditional-workflow-paths)
   - [Pointer Events Interception](#pointer-events-interception)

---

## User-Guided Workflow Discovery (Golden Standard)

**THE PRIMARY PROCESS for building automation on complex workflows.**

> Future: This process should become a slash command (e.g., `/discover-workflow`) to invoke after Step 10 of the QA workflow when test execution fails or when the workflow is too complex for automated discovery.

### When to Use

Use this process PROACTIVELY when:
- Building automation for multi-step workflows (wizards, forms, checkout flows)
- The UI has conditional paths based on data or state
- Element discovery alone won't reveal the full workflow
- You need to understand what each page/step requires before automating

### The Process

**Core Principle:** Step through the workflow WITH the user, one page at a time.

#### For Each Step/Page:

```
1. Navigate to the step
2. Take a snapshot → Show user the current state
3. ASK: "What needs to happen on this page?"
4. User confirms the required actions
5. Perform the actions (with user validation)
6. Take a snapshot → Show user the result
7. ASK: "Ready to proceed to next step?"
8. User confirms → Move to next step
9. Repeat until workflow complete
```

### Why This Works

| Problem | How This Solves It |
|---------|-------------------|
| Misunderstood workflow | User validates each step before proceeding |
| Wrong assumptions | User catches errors immediately |
| Hidden validation rules | Discovered through real interaction |
| Conditional paths | User guides which path to take |
| Missing elements | Identified before test is written |

### Key Rules

1. **Never assume** - Always ask "what should happen here?"
2. **One step at a time** - Don't rush through multiple pages
3. **User validates before proceeding** - Wait for confirmation
4. **Document as you go** - Each step becomes part of the automation
5. **Stop on unexpected behavior** - Discuss with user before continuing

### Output

After completing the workflow with user guidance:
- Full understanding of each step's requirements
- Validated locators and actions
- Known validation rules and edge cases
- Ready to write accurate automation code

---

## Complex Workflow Investigation Protocol

**Use this protocol when automation fails and you need to debug.**

> Future: This protocol could become a `/investigate` slash command.

This applies to:
- Workflows that don't behave as expected
- Elements that can't be located
- Tests that fail intermittently
- Any scenario requiring human observation to understand

### When to Use

Trigger this protocol when:
- AI has attempted 2-3 fixes without success
- Error messages don't clearly indicate the root cause
- The workflow involves dynamic/conditional behavior
- You need to see what the UI actually does vs what you expect

### Step-by-Step Protocol

#### Step 1: Stop and Acknowledge

Stop automated fix attempts. State:
- What you're trying to accomplish
- What's failing
- What you've already tried

#### Step 2: Interactive Investigation

Use a browser automation tool (Playwright MCP, etc.) to manually step through:

```
1. Navigate to the starting point
2. Take a snapshot (document current state)
3. Perform ONE action
4. Take a snapshot (document resulting state)
5. Compare: Did the UI behave as expected?
6. If yes → continue to next action
7. If no → STOP and document the divergence
8. Repeat until complete or issue found
```

#### Step 3: Document Findings

Record what you observed:
- **Expected:** What you thought would happen
- **Actual:** What actually happened
- **Divergence Point:** Where expected != actual
- **Root Cause:** Why it behaved differently (if known)

#### Step 4: Identify the Fix

Based on findings, determine:
- Is this a **code issue**? (wrong locators, wrong workflow)
- Is this a **data issue**? (input triggers different path)
- Is this a **timing issue**? (element not ready)
- Is this a **UI pattern issue**? (see Specific Patterns below)

#### Step 5: Apply and Verify

1. Make the fix
2. Run the test
3. If still failing → return to Step 2
4. If passing → document the pattern for future reference

### Key Principles

1. **Observe before fixing** - Don't guess; see what actually happens
2. **One action at a time** - Isolate where things go wrong
3. **Document divergence** - The gap between expected and actual is the clue
4. **Generalize learnings** - Add new patterns to this knowledge base

---

## Specific Patterns

### Conditional Workflow Paths

**Problem:** Workflow has different paths based on data/state. Test expects Path A, but UI takes Path B.

**Symptoms:**
- "Element not found" for elements that exist in a different flow
- Test passes with one data set, fails with another
- UI shows fewer/more steps than expected

**Investigation Focus:**
- Look for branching points (search results, validation states)
- Check if input data matches existing records
- Map all possible paths through the workflow

**Solutions:**
- Control input data to trigger intended path
- Add conditional logic to handle branches
- Use unique/random data to avoid collisions with existing records

---

### Pointer Events Interception

**Problem:** Click fails with "element intercepts pointer events"

**Cause:** Parent element (overlay, wrapper div) captures clicks via CSS

**Solution:** Use JavaScript click to bypass:

```python
self.web.click_js(*self.BUTTON_LOCATOR)  # Instead of click()
```

**Trade-off:** JS click skips visibility/enabled checks. Only use when standard click fails.

---

## Adding New Patterns

After solving a complex issue:

1. **Generalize** - Extract the pattern from the specific case
2. **Document** - Add to Specific Patterns with:
   - Problem description
   - Symptoms
   - Investigation focus
   - Solutions
3. **Reference** - Future investigations can check here first

---

*Last Updated: 2025-12-30*
