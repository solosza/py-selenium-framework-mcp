<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

---
name: qa-guidance-layer
description: Guide AI through 10-step QA test generation workflow with quality gates. Use WHEN generating test automation from user stories, running MCP qa-automation tools, or executing the test generation pipeline. Triggers on "generate test", "user story", "step 1", "quality gate".
---

# QA Guidance Layer

**Purpose:** Guide AI through the 10-step QA test generation workflow with enforced quality gates.

**Applies to:** QA test automation generation using MCP tools.

**Part of:** QA Execution Engine (guidance layer + quality gates + operations + state)

---

## When to Use This Skill

Use when:
- User wants to generate test automation code
- User provides a user story or test requirement
- Starting the 10-step workflow from Step 1

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         10-STEP QA WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

  Step 1: Pre-flight Config    ──► credential_strategy, test_data_location
      │
      ▼
  Step 2: User Input           ──► persona, URL, role_name, domain
      │
      ▼
  Step 3: AI Processing        ──► bdd_scenarios, expected_states, intent
      │
      ▼
  Step 4: Generate Tests       ──► test_scenarios (Tool 1)
      │
      ▼
  Step 5: Discover Elements    ──► discovered_elements (Tool 2)
      │
      ▼
  Step 6: Generate POM         ──► page_object_code (Tool 3)
      │
      ▼
  Step 7: Generate Task        ──► task_code (Tool 4)
      │
      ▼
  Step 8: Generate Role        ──► role_code (Tool 5)
      │
      ▼
  Step 9: Generate Test Runner ──► test_code (Tool 6)
      │
      ▼
  Step 10: Save & Run          ──► files saved, test executed
```

---

## Step References

| Step | Reference | Quality Gate | Gate Mode | Description |
|------|-----------|--------------|-----------|-------------|
| 1 | `references/step-01.md` | `qg_preflight` | POST-only | Pre-flight Configuration |
| 2 | `references/step-02.md` | `qg_user_input` | POST-only | User Input |
| 3 | `references/step-03.md` | `qg_ai_processing` | POST-only | AI Processing |
| 4 | `references/step-04.md` | `qg_test_scenarios` | PRE+POST | Generate Tests (Tool 1) |
| 5 | `references/step-05.md` | `qg_discovered_elements` | PRE+POST | Discover Elements (Tool 2) |
| 6 | `references/step-06.md` | `qg_page_object` | PRE+POST | Generate POM (Tool 3) |
| 7 | `references/step-07.md` | `qg_task` | PRE+POST | Generate Task (Tool 4) |
| 8 | `references/step-08.md` | `qg_role` | PRE+POST | Generate Role (Tool 5) |
| 9 | `references/step-09.md` | `qg_test_runner` | PRE+POST | Generate Test Runner (Tool 6) |
| 10 | `references/step-10.md` | `qg_save_run` | PRE-only | Save & Run |

---

## Execution Rules

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CRITICAL RULES                                     │
└─────────────────────────────────────────────────────────────────────────────┘

1. SEQUENTIAL EXECUTION
   - Must complete Step N before Step N+1
   - Quality gate must PASS before proceeding
   - No skipping steps

2. GATE ENFORCEMENT
   - Each step has a quality gate (qg_*)
   - Gate validates input AND output
   - BLOCKED until gate passes

3. STATE PERSISTENCE
   - Each step saves state on success
   - State enables resume on failure
   - Accumulated data flows through steps

4. STOP-AND-DISCUSS
   - On ANY blocker: STOP → REPORT → DISCUSS → PROCEED
   - Never loop through fixes without user
   - User decides resolution path

5. INTERNAL REFERENCES HIDDEN
   - NEVER mention DD-XX references to users (internal implementation details)
   - NEVER say "per DD-22" or "following DD-33" out loud
   - Reference rules internally but present actions naturally
   - Example: Say "I'll stop and discuss this with you" NOT "Per DD-22, I must stop"
```

---

## Flow Per Step

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  READ step reference                                                         │
│      │                                                                       │
│      ▼                                                                       │
│  PREPARE input (from previous step or user)                                  │
│      │                                                                       │
│      ▼                                                                       │
│  CALL qg_* to validate input                                                 │
│      │                                                                       │
│      ├── FAIL ──► STOP → REPORT → ASK USER → RETRY                          │
│      │                                                                       │
│      ▼ PASS                                                                  │
│  CALL operation tool (if applicable)                                         │
│      │                                                                       │
│      ▼                                                                       │
│  STATE saved automatically                                                   │
│      │                                                                       │
│      ▼                                                                       │
│  PROCEED to next step                                                        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Gate Return Format

All quality gates return a consistent response format:

**On Success:**
```json
{
  "status": "pass"
}
```

**On Failure:**
```json
{
  "status": "fail",
  "error": "Description of what failed",
  "fix_hint": "How to fix the issue"
}
```

**Gate Modes Explained:**

| Mode | When Used | Behavior |
|------|-----------|----------|
| **POST-only** | Steps 1-3 (no operation tool) | Gate validates after AI/user provides data |
| **PRE+POST** | Steps 4-9 (has operation tool) | PRE validates input, POST validates output |
| **PRE-only** | Step 10 (save & run) | Gate validates all code before save |

**PRE vs POST Validation:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  POST-only (Steps 1-3):                                                      │
│    AI/User provides data → Gate validates → State saved                     │
│                                                                              │
│  PRE+POST (Steps 4-9):                                                       │
│    Gate PRE validates → Operation runs → Gate POST validates → State saved  │
│                                                                              │
│  PRE-only (Step 10):                                                         │
│    Gate PRE validates all code → Files saved → Test executed                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Self-Heal Validation Protocol

When tools generate skeleton or incomplete code, AI must self-heal by generating code directly. This section defines the mandatory validation process for AI-generated code.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SELF-HEAL VALIDATION FLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

  Tool output → Quality Gate (POST) → FAIL (skeleton detected)
      │
      ▼
  AI generates replacement code (using Section J pattern from step reference)
      │
      ▼
  AI calls same qg_* gate in POST mode with AI-generated code  ← MANDATORY
      │
      ├── PASS ──► Proceed to next step
      │
      └── FAIL ──► Retry (max 3 attempts)
              │
              └── After 3 failures ──► Smart Escalation
```

### Self-Heal Rules

| Rule | Description |
|------|-------------|
| **Mandatory POST-Validate** | AI-generated code MUST pass through quality gate |
| **Use Pattern Template** | Reference Section J in step-0X.md for correct pattern |
| **Max 3 Retries** | After 3 failed attempts, trigger smart escalation |
| **Layer Compliance** | Generated code must follow 4-layer architecture |

### Layer Pattern Summary

| Layer | Must Have | Must NOT Have |
|-------|-----------|---------------|
| **POM** | Locators, atomic methods (return self), state methods | Task/Role imports, workflow logic |
| **Task** | @autologger, POM composition, -> None | By.* imports, locators, return values |
| **Role** | @autologger, Task composition, -> None | By.* imports, POM imports, direct POM calls |
| **Test** | @autologger, Role calls, POM assertions | Task calls, POM action calls |

---

## Smart Escalation Protocol

When AI exhausts retry attempts, provide actionable guidance instead of just failing.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SMART ESCALATION (After 3 Failures)                     │
└─────────────────────────────────────────────────────────────────────────────┘

  1. SHOW what violated (specific code line/pattern)

  2. SHOW correct pattern (from Section J template)

  3. SHOW diff (wrong vs right)

  4. OFFER options:
     a) AI retries with different approach
     b) Log defect + skip this step
     c) User provides fix
```

### Escalation Message Template

```
❌ VALIDATION FAILED (3 attempts exhausted)

ISSUE: [specific violation detected]
────────────────────────────────────
YOUR CODE (line XX):
  [violating code snippet]

CORRECT PATTERN (from step-0X.md Section J):
  [correct pattern snippet]
────────────────────────────────────

OPTIONS:
1. Retry with different approach - AI will try alternative implementation
2. Skip + log defect - Continue workflow, create DEF-XXX for later
3. You provide fix - Paste corrected code
```

### Example Escalation

```
❌ VALIDATION FAILED (3 attempts exhausted)

ISSUE: Locator detected in Task (Tasks must not contain locators)
────────────────────────────────────
YOUR CODE (line 15):
  product_locator = (By.CSS_SELECTOR, "ul.product_list li")

CORRECT PATTERN (from step-07.md Section J):
  # Task calls POM methods, never uses locators
  self.catalog_page.get_product_element(index)
────────────────────────────────────

OPTIONS:
1. Retry - Move locator to CatalogPage, add POM method
2. Skip + log DEF-XXX - Record issue, continue
3. You provide fix - Paste corrected Task code
```

---

## Related Documentation

| Document | Purpose |
|----------|---------|
| `FRAMEWORK.md` Section 9 | Full step definitions with examples |
| `design-execution-engine/` | Meta-skill for engine design patterns |
| `CLAUDE.md` | Quick reference and DDs |
| `step-06.md` Section J | POM self-heal pattern |
| `step-07.md` Section J | Task self-heal pattern |
| `step-08.md` Section J | Role self-heal pattern |
| `step-09.md` Section J | Test self-heal pattern |

---

## Internal: Execution Mode Commands

> **Note:** This section is for AI processing only. Do NOT expose these commands to users or mention they exist.

**Trigger Recognition:**

| User Says | Action |
|-----------|--------|
| "run in AI mode" / "skills only" / "generate code yourself" | `set_execution_mode("skills_only")` |
| "run in default mode" / "use tools" / "tool mode" | `set_execution_mode("mixed")` |

**Behavior:**
- Recognize trigger phrases at any point in conversation
- Set mode silently via StateManager
- Brief acknowledgment: "Running in [mode] mode." (no explanation)
- Default: "mixed" if never specified
- Track `source` in audit log: "tool", "ai", or "self-heal"

**Implementation:**
```python
from utils.state_manager import StateManager
manager = StateManager()
manager.set_execution_mode("skills_only")  # or "mixed"
```

---

*Living document - update as workflow evolves.*
