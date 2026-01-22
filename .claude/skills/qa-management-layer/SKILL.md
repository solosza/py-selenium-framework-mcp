<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

---
name: qa-management-layer
description: Guide AI through 5-step QA test generation workflow with quality gates and collaborative construction. Use WHEN generating test automation from user stories, running MCP qa-automation tools, or executing the test generation pipeline. Triggers on "generate test", "user story", "step 1", "quality gate".
---

# QA Guidance Layer

**Purpose:** Guide AI through the 5-step QA test generation workflow with enforced quality gates and collaborative construction.

**Applies to:** QA test automation generation using MCP tools.

**Part of:** QA Management Engine (guidance layer + quality gates + operations + state)

**Workflow Type:** Pair Programming (Human guides, AI builds incrementally with real-time validation)

---

## When to Use This Skill

Use when:
- User wants to generate test automation code
- User provides a user story or test requirement
- Starting the 11-step workflow from Step 1

---

## Communication Guidelines

**DO NOT show users:**
- Internal gate status ("Gate: PASS", "POST-VALIDATE: PASS")
- Gate implementation details
- Internal field names (input_data, metadata)

**DO show users:**
- "Step X Complete" (without gate status)
- Progress indicators ("Discovering elements...", "Generating POM...")
- Actionable errors only (if gate fails, explain what to fix, not gate mechanics)

---

## Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         5-STEP QA WORKFLOW (Pair Programming)                │
└─────────────────────────────────────────────────────────────────────────────┘

  Step 1: User Input           ──► persona, URL, role_name, workflow
      │
      ▼
  Step 2: Pre-flight Config    ──► credential_strategy, test_data_location
      │
      ▼
  Step 3: AI Processing        ──► bdd_scenarios, expected_states, intent
      │
      ▼
  Step 4: Collaborative Construction (HITL Loop)
      │
      ├─► Tool 1: Generate BDD scenarios (structure)
      ├─► Tool 2: Discover elements (bulk extraction)
      │
      ├─► AI builds POMs manually (Edit/Write tools)
      ├─► AI builds Tasks manually (Edit/Write tools)
      ├─► AI builds Roles manually (Edit/Write tools)
      ├─► AI builds Tests manually (Edit/Write tools)
      │
      ├─► Gates validate each piece (framework compliance)
      ├─► HITL triggers at blockers (human guides)
      │
      └─► Repeat: build → save → test → discover gap → build more
      │
      ▼
  Step 5: Done
      │
      └─► Test passes ✓ = COMPLETE | Test fails ✗ = AWAITING TRIAGE

NOTE: Old 11-step autonomous workflow (Steps 6-11, Tools 3-6) archived to
_archived/autonomous_workflow_v1/ on 2026-01-22. New workflow uses collaborative
construction instead of autonomous code generation (96% failure rate).
```

---

## Step References

| Step | Reference | Quality Gate | Gate Mode | Description |
|------|-----------|--------------|-----------|-------------|
| 1 | `references/step-01.md` | `qg_user_input` | POST-only | User Input |
| 2 | `references/step-02.md` | `qg_preflight` | POST-only | Pre-flight Configuration |
| 3 | `references/step-03.md` | `qg_ai_processing` | POST-only | AI Processing |
| 4 | TBD: `references/step-04-construction.md` | Multiple gates | Varies | Collaborative Construction (HITL Loop) |
| 4a | `references/step-04.md` | `qg_test_scenarios` | PRE+POST | Generate Tests (Tool 1) - Part of Step 4 |
| 4b | `references/step-05.md` | `qg_discovered_elements`, `qg_discovery_complete` | PRE+POST, PRE-only | Discover Elements (Tool 2) - Part of Step 4 |
| 5 | TBD: `references/step-05-done.md` | N/A | N/A | Done (Test Execution & Triage) |

**Archived (2026-01-22):** Steps 6-11 moved to `_archived/autonomous_workflow_v1/protocols/`

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
| **PRE-only** | Step 10 (validation) | Gate validates all code before save |

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
│    Gate PRE validates all code → Files saved (execution in Step 11)         │
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
