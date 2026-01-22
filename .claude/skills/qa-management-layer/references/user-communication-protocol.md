<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# User Communication Protocol

**Purpose:** Define how AI presents workflow progress to users - clear, concise, informative.

**Applies To:** All 11 steps in `/qa-workflow` and `/qa-workflow-dev`

---

## Core Principles

| Principle | Rule |
|-----------|------|
| **Signal, Not Noise** | Show 2-4 key data points per step, not full JSON |
| **Visual Progress** | Use ✓ (complete), ⚙ (in progress), ✗ (failed) |
| **Hide Implementation** | Never show "Gate: PASS" or internal validation details |
| **Context Awareness** | User should see where they are in 11-step flow |

---

## Output Format

### Step Completion (Standard)
```
✓ Step N: [Step Name]
  • [Key Fact 1]: [Value]
  • [Key Fact 2]: [Value]
  • [Key Fact 3]: [Value]
```

### Step In Progress
```
⚙ Step N: [Action in progress]...
  • [Context info]
  [Brief status message]
```

### Step Failure
```
✗ Step N: [Step Name] - Failed
  • Issue: [Brief error description]
  • Fix: [Actionable next step]
```

---

## Step-by-Step Communication Guide

### Step 1: Pre-flight Configuration
**Show:**
- Credential strategy chosen
- Test data location chosen

**Example:**
```
✓ Step 1: Pre-flight Configuration
  • Credentials: none (already logged in)
  • Test data: workflow-specific
```

---

### Step 2: User Input
**Show:**
- Role name derived
- Workflow/domain identified
- Environment detected (if applicable)

**Example:**
```
✓ Step 2: User Input
  • Role: SalesRepresentative
  • Workflow: helios1
  • Environment: helios1
```

---

### Step 3: AI Processing
**Show:**
- Intent extracted
- Number of scenarios
- Number of expected states

**Example:**
```
✓ Step 3: AI Processing
  • Intent: create_inquiry
  • Scenarios: 1
  • Expected states: 2
```

---

### Step 4: Test Scenarios
**Show:**
- Test name(s) generated

**Example:**
```
✓ Step 4: Test Scenarios
  • Generated: test_create_service_inquiry_with_dynamic_customer_data
```

---

### Step 5: Element Discovery
**In Progress:**
```
⚙ Step 5: Discovering Elements...
  • Page: InquiriesPage
  • URL: https://...
  [Playwright navigation in progress...]
```

**Complete:**
```
✓ Step 5: Element Discovery
  • Found: 18 interactive elements
  • Forms: Customer, Contact, Address, Inquiry
```

---

### Step 6: Page Object
**Show:**
- Page class name
- File location (relative path)
- Method count (actions + state checks)

**Example:**
```
✓ Step 6: Page Object
  • Generated: InquiriesPage
  • Location: framework/pages/helios1/inquiries_page.py
  • Methods: 18 actions + 2 state checks
```

---

### Step 7: Task Module
**Show:**
- Task class name + key method
- File location (relative path)

**Example:**
```
✓ Step 7: Task Module
  • Generated: InquiryTasks.create_inquiry()
  • Location: framework/tasks/helios1/inquiry_tasks.py
```

---

### Step 8: Role Module
**Show:**
- Role class name + key method
- File location (relative path)

**Example:**
```
✓ Step 8: Role Module
  • Generated: SalesRepresentative.create_inquiry()
  • Location: framework/roles/helios1/sales_representative.py
```

---

### Step 9: Test Runner
**Show:**
- Test file name
- File location (relative path)
- Number of assertions + method names

**Example:**
```
✓ Step 9: Test Runner
  • Generated: test_create_service_inquiry_with_dynamic_customer_data.py
  • Location: tests/helios1/
  • Assertions: 2 (is_inquiry_created, is_inquiry_in_list)
```

---

### Step 10: Validation
**Show:**
- Number of files validated
- Confirmation all exist on disk

**Example:**
```
✓ Step 10: Validation
  • Files validated: 4 (POM, Task, Role, Test)
  • All files exist on disk: YES
```

---

### Step 11: Test Execution

**In Progress:**
```
⚙ Step 11: Executing Test...
  • Test: tests/helios1/test_create_service_inquiry.py
  • Environment: helios1
  • Browser: visible
  [Test execution in progress...]
```

**Complete (Passed):**
```
✓ Step 11: Test Execution
  • Status: PASSED
  • Duration: 12.3s
  • Report: tests/_reports/2026-01-19T00-20-55.248039Z/
```

**Complete (Failed):**
```
✗ Step 11: Test Execution - Failed
  • Status: FAILED
  • Assertion: is_inquiry_created() returned False
  • Next: Choose fix strategy (1: Debug, 2: Regenerate, 3: Manual)
```

---

## Workflow Header/Footer

### Opening (Optional)
```
───────────────────────────────────────────────────
  11-Step Workflow: [Test Scenario Name]
───────────────────────────────────────────────────
```

### Closing (Optional)
```
───────────────────────────────────────────────────
  Workflow Complete ✓
───────────────────────────────────────────────────
```

---

## What NOT to Show

| ❌ Don't Show | ✓ Show Instead |
|---------------|----------------|
| Full JSON tool output | 2-4 key bullet points |
| "Gate: PASS" or "result": "pass" | ✓ visual indicator |
| Internal validation checks | Just the outcome |
| Timestamps (unless debugging) | Step number + name |
| Raw metadata dictionaries | Parsed human-readable values |
| Stack traces (unless failure) | "Issue + Fix" one-liners |

---

## Error Communication

**Principle:** Errors should be actionable, not overwhelming.

**Format:**
```
✗ Step N: [Step Name] - Failed
  • Issue: [What went wrong in 1 sentence]
  • Fix: [What to do next in 1 sentence]
  • Details: [Optional - only if user needs context]
```

**Example:**
```
✗ Step 5: Element Discovery - Failed
  • Issue: Page took >30s to load, navigation timeout
  • Fix: Check URL is accessible or increase timeout
```

---

## Integration with Step References

**Add to each step-XX.md file:**

```markdown
## K. User Communication

**What to Show:**
- [Key fact 1]
- [Key fact 2]
- [Key fact 3]

**Output Format:**
```
✓ Step X: [Step Name]
  • [Fact 1]: [Value]
  • [Fact 2]: [Value]
```
**
```

---

## DEF-029 Resolution

This protocol resolves:
- **DEF-029:** Internal gate status shown to user (Severity: LOW, Status: OPEN)

**Before:**
```
Step 3 Complete - Gate: PASS
{full JSON dump}
```

**After:**
```
✓ Step 3: AI Processing
  • Intent: create_inquiry
  • Scenarios: 1
```

---

**Status:** ACTIVE (added 2026-01-18)
**Related Defect:** DEF-029
**Applies To:** All 11 workflow steps
