# Pair Programming Workflow v4.0 - Design Discussion

**Date:** 2026-01-23
**Phase:** Design (4D Framework - Phase 1)
**Status:** Complete
**Next:** Define Phase (Create PRD)

---

## Overview

Design 7-step pair programming workflow with HITL iteration to replace current 4-step workflow that still contains autonomous workflow machinery.

**Core Philosophy:** Generate fast, iterate via HITL collaboration.

---

## Problem Statement

Current Step 4 protocol (`.claude/skills/qa-management-layer/references/step-04.md`) is designed for autonomous workflow execution:
- Navigation tracking machinery
- RuntimeValidator with visual feedback
- Multi-page detection loops
- Two-pass discovery complexity

**Gap:** Not designed for pair programming where AI and human collaborate iteratively.

**What we learned from Step 11 HITL:** The run → fail → fix → repeat pattern works better than element-by-element construction.

---

## Solution: 7-Step Architecture

```
Step 1: User Input ✓ (existing)
  • Persona, URL, requirement

Step 2: Pre-flight Config ✓ (existing)
  • Credential strategy, timeout

Step 3: AI Processing ✓ (existing)
  • Extract BDD scenarios, expected_states, intent

Step 4: Discovery (NEW - simplified)
  • Navigate + reveal elements
  • Snapshot extraction (input + output)
  • Save elements to state
  • FAST - 5 minutes

Step 5: Generate Skeleton (NEW)
  • AI writes POM + Task + Role + Test
  • Uses Step 4 elements
  • Goal: RUNNABLE (bugs OK)
  • Protocol + Gate (NO Python tool)
  • FAST - 10 minutes

Step 6: HITL Iteration (NEW - borrow Step 11 pattern)
  • Run → Fail → Triage → Fix → Repeat
  • 3 triage options (locator/flow/logic)
  • Protocol + HITL confirmations
  • Until test passes

Step 7: Framework Validation (NEW)
  • Gates check 4-layer compliance
  • DD-27, return values, decorators, etc.
  • Protocol + Gate
```

**Benefits:**
- Clear separation of concerns (discover → generate → iterate → validate)
- Each step has ONE job
- HITL iteration is explicit step (not buried in Step 4)
- Faster to working test (generate all 4 layers at once, then fix)

---

## Key Design Decisions

### Decision 1: AI Generates Code (Not Python Tools)

**Question:** Should we use Python code generator tools (like archived Tool 3-6) or AI with smart gates?

**Answer:** AI with smart gates.

**Rationale:**
- AI can read existing patterns (helios7 examples)
- AI can fix incrementally based on gate feedback
- Lighter weight (no Python generators to maintain)
- More flexible (adapts to context)
- True collaboration (AI thinks, not just executes)

**Pattern:**
```
Protocol → AI (generates code) → Gate (validates + teaches)
```

**NOT:**
```
Protocol → Python Tool (generates code) → Gate (validates)
```

**Division of Labor:**
- ✅ Python tools for OPERATIONS: `discover_page_elements` (Playwright), `run_test` (pytest)
- ❌ Python tools for CODE: `generate_page_object` (AI does this better)

---

### Decision 2: Protocols + Gates Teach (Not Examples)

**Question:** Should AI learn from examples (helios7) or protocols + gates?

**Answer:** Protocols + gates teach through enforcement.

**Comparison:**

| Learning Method | Approach | Signal | Quality |
|----------------|----------|--------|---------|
| **Examples (helios7)** | AI infers patterns | Passive observation | Can copy variations/inconsistencies |
| **Protocols + Gates** | AI learns by correction | Active teaching | Fix hints encode single correct pattern |

**How Gates Teach:**

```python
# Example from qg_page_object.py

# 1. Pattern constants encode rules
SKELETON_PATTERNS = [
    (r'^\s*pass\s*$', 'pass statement'),
    (r'raise\s+NotImplementedError', 'NotImplementedError'),
]

LAYER_VIOLATION_PATTERNS = [
    (r'from\s+tasks\.', 'Task import in POM'),
]

# 2. Fix hints teach correct pattern
return cls.fail_response(
    error="POM contains Task import (layer violation)",
    fix_hint="Remove Task imports. POMs only import WebInterface and By."
)
```

**Gates don't just validate - they encode framework architecture and teach through explicit corrections.**

---

### Decision 3: All 6 Defense-in-Depth Components

**Question:** Is using all 6 components over-engineering?

**Answer:** No. This product needs all 6.

**Justification:**
- Enterprise QA tool (compliance matters)
- High-value output (test automation code)
- Complex workflow (multi-step generation)
- Already has 4/6 implemented

From `.business/architecture/execution_patterns.md`:
> **Example 1: Enterprise Compliance Workflow**
> Use: ✅ All 6 components
> Why: High-risk, regulated, needs full defense-in-depth + compliance trail

**Components Applied to v4.0:**

| Component | Application | Status |
|-----------|-------------|--------|
| **1. Protocols** | Step 5-7 protocols define AI actions | To implement |
| **2. Smart Gates** | `qg_skeleton`, `qg_framework_compliance` validate + teach | To implement |
| **3. Hooks** | PostToolUse audit writer tracks gate results | ✅ Exists |
| **4. State Checkpointing** | Save after each gate passes | ✅ Exists |
| **5. Audit System** | Progressive audit trail logs all steps | ✅ Exists |
| **6. HITL System** | Step 6 triage options for collaborative fixing | To implement |

---

### Decision 4: Borrow Step 11 HITL Pattern

**What worked in archived Step 11:**
- Start with RUNNABLE code (all 4 layers already generated)
- Fast feedback loop: run → fail → fix → repeat
- Structured triage (3 options, not open-ended)
- Browser visible (user observes execution)

**Apply to Step 6:**

```
Step 6 HITL Pattern:
1. Run test (browser visible)
2. Test fails (capture diagnostics)
3. AI presents triage:
   • Locator issue → AI fixes POM selectors
   • Flow issue → AI fixes Task/Role orchestration
   • Logic issue → User guides fix
4. Fix → Re-run → Repeat until green
```

**Key Insight:** Don't build 4 layers element-by-element (death by 1000 cuts). Generate ALL 4 layers QUICKLY (10 min), then collaborate on FIXING what's broken via HITL iteration.

This matches how Step 11 worked - start with generated code, iterate until it works.

---

### Decision 5: Reuse Archived Validation Logic

**Question:** Start from scratch or reuse archived gate code?

**Answer:** Reuse core validation logic, strip out workflow-specific machinery.

**From `_archived/autonomous_workflow_v1/gates/qg_page_object.py`:**

**✅ REUSE (proven patterns):**
```python
# Pattern constants
SKELETON_PATTERNS            # Detects pass, TODO, NotImplementedError
LAYER_VIOLATION_PATTERNS     # Detects Task/Role imports in POM
HARDCODED_URL_PATTERNS       # Detects hardcoded http:// in navigate()
TRIVIAL_STATE_PATTERN        # Detects "return True" without element check

# Detection methods
_detect_skeleton_code()           # Check for skeleton code indicators
_detect_layer_violations()        # Check architecture layer violations
_detect_hardcoded_urls()          # Check DD-49 compliance (config["url"])
_detect_trivial_state_methods()   # Check state methods use actual elements

# Metadata validation methods
_validate_metadata_structure()    # Check class_name, import_path present
_validate_locators()              # Check locators array not empty
_validate_action_methods()        # Check action methods present
_validate_state_methods()         # Check state methods present
```

**❌ REMOVE (autonomous workflow specific):**
```python
# Multi-page generation loops (lines 436-529)
generated_poms[page_name] = {...}
poms_generated = len(generated_poms)
generation_complete = poms_generated >= total_pages

# File writing during POST validation (Task 15.0)
cls._write_pom_file(file_path, code)  # AI writes files, gate validates

# Tool 3 specific PRE validation
# Complex multi-page tracking
```

**NEW for Step 5 Gate (qg_skeleton):**
```python
# Validate ALL 4 layers present
_validate_all_layers_exist()     # Check POM, Task, Role, Test files on disk

# Task-specific validation (DD-27)
_validate_no_locators_in_task()  # Critical: Tasks must not have locators

# Import validation
_validate_imports_resolve()       # Check all imports can be resolved

# Basic structure checks
_validate_basic_structure()       # Check each layer has required components
```

**Reuse Strategy:**
1. Copy `qg_page_object.py` → `qg_skeleton.py`
2. Keep detection methods + patterns (~200 lines)
3. Remove multi-page tracking (~100 lines)
4. Add 4-layer validation (~100 lines)
5. Update step numbers, class names

**Result:** ~60% reuse, 30 min vs. 2 hours from scratch.

---

## Implementation Approach

### Iterative Vertical Slice Pattern (Not Waterfall)

**Decision:** Implement one step at a time, fully complete before moving to next step.

**Workflow per Step:**
```
Step N: Design → PRD → Test Plan → Tasks → Implement → Validate → Ship
  ↓ (working code, lessons learned)
Step N+1: Design → PRD → Test Plan → Tasks → Implement → Validate → Ship
  ↓
Repeat for all 7 steps
```

**Why This Works Better:**
- ✅ **Faster to working code** - Step 1 fully implemented before designing Step 2
- ✅ **Validate design early** - Catch design issues when implementing Step 1, fix before Step 2
- ✅ **Shippable increments** - Each step completion = value delivered
- ✅ **Living documents** - PRD/Tasks grow with each step, not all upfront
- ✅ **Course correction** - Can adjust Step 2 design based on Step 1 learnings
- ✅ **Less rework** - Don't design all 7 steps then realize Step 1 assumptions were wrong

**vs Waterfall (Avoided):**
```
❌ Design ALL 7 steps → PRD ALL → Test Plan ALL → Tasks ALL → Implement ALL
   (Wastes time if early assumptions wrong, no course correction)
```

**Living Document Pattern:**
- `2-prd-v4.md`: Starts with Step 1 only, Step 2-7 added AFTER previous step validated
- `3-tasks-v4.md`: Starts with Step 1 only, Step 2-7 added AFTER previous step implemented
- `1-design-discussion-v4.md`: Has all 7 steps sketched (high level), detailed design per step iteratively

---

### Step 1 Implementation Cycle (Current)

```
✅ Phase 1: Design (COMPLETE)
  ✅ Discussed pair programming flow
  ✅ Identified key design decisions
  ✅ Defined 7-step architecture
  ✅ Designed Step 1 components in detail
  ✅ Defined testing strategy (3D matrix, TDD approach)

✅ Phase 2: Define (COMPLETE for Step 1)
  ✅ Created PRD for Step 1 (docs/projects/pair-programming/2-prd-v4.md)
  ✅ Documented Step 1 functional requirements (FR-1.1 through FR-1.8)
  ✅ Defined gate validation rules
  ✅ Defined test strategy with acceptance tests
  ✅ Documented success criteria

✅ Phase 3: Test Planning (COMPLETE for Step 1)
  ✅ Test pyramids for Step 1 components (in PRD)
  ✅ Acceptance tests defined (AT-1.1 through AT-1.10)
  ✅ Prioritized tests (P0/P1/P2)
  ✅ Non-functional SLAs defined

✅ Phase 4: Divide (COMPLETE for Step 1)
  ✅ Created tasks for Step 1 (docs/projects/pair-programming/3-tasks-v4.md)
  ✅ Broke into 7 parent tasks (setup → transcript → gate → protocol → integration → manual → docs)
  ✅ Marked CORE vs GLUE tasks
  ✅ Defined TDD tasks for TranscriptWriter and gate tests
  ✅ Created done-when criteria per task

⏳ Phase 5: Deliver (NEXT - Step 1 Implementation)
  ⬜ Execute Task 0.0: Verify existing components
  ⬜ Execute Task 1.0: Create test infrastructure
  ⬜ Execute Task 2.0: Implement TranscriptWriter (TDD)
  ⬜ Execute Task 3.0: Verify/create gate tests (TDD)
  ⬜ Execute Task 4.0: Update protocol (test-after)
  ⬜ Execute Task 5.0: Create E2E integration tests (TDD)
  ⬜ Execute Task 6.0: Manual testing & validation
  ⬜ Execute Task 7.0: Documentation & cleanup
```

**After Step 1 Complete:**
- Move to Step 2: Design → PRD → Test Plan → Tasks → Implement → Validate
- Repeat cycle with learnings from Step 1

---

### Updated 4D Framework Phases (Iterative, Per Step)

**For Each Step (Repeat 7 times):**

```
Phase 1: Design (1 session)
  - High-level component identification
  - Detailed component content design
  - Gap analysis vs existing implementations

Phase 2: Define (1-2 hours)
  - Create PRD section for this step
  - Functional requirements
  - Test strategy with acceptance tests
  - Success criteria

Phase 3: Test Planning (integrated into Phase 2)
  - Test pyramids for step components
  - Acceptance tests (GIVEN/WHEN/THEN)
  - Non-functional SLAs
  - Observability/telemetry

Phase 4: Divide (1 hour)
  - Create tasks for this step
  - Mark CORE vs GLUE
  - Define TDD tasks
  - Done-when criteria

Phase 5: Deliver (varies per step complexity)
  - TDD for Gates (test → implement → refactor)
  - TDD for new utilities (TranscriptWriter, etc.)
  - Test-After for Protocols
  - Integration tests (E2E flow)
  - Manual validation
  - Documentation
```

**Estimated Timeline:**
- Step 1: ~12 hours (2 days)
- Step 2-4: ~8 hours each (1-2 days each)
- Step 5-6: ~16 hours each (2-3 days each) - more complex (code generation, HITL)
- Step 7: ~4 hours (1 day) - validation only
- **Total:** ~6-8 weeks (assuming part-time work)

### TDD for Gates

**Why TDD:**
- Gates are CORE logic → need tests
- State management → already tested
- Hooks → already exist
- Protocols are guidance → less critical to test

**Test-First Pattern:**
```
1. Write failing test (Red)
2. Implement minimal code (Green)
3. Refactor (Refactor)
4. Repeat
```

**Test Coverage:**
- `mcp_server/_dev_tests/test_gates/test_qg_skeleton.py`
- `mcp_server/_dev_tests/test_gates/test_qg_framework_compliance.py`

---

## Files to Create

### New Step Protocols
- `.claude/skills/qa-management-layer/references/step-05.md` - Generate Skeleton
- `.claude/skills/qa-management-layer/references/step-06.md` - HITL Iteration
- `.claude/skills/qa-management-layer/references/step-07.md` - Framework Validation

### New Gates
- `mcp_server/tools/gates/qg_skeleton.py` - Step 5 validation
  - Copy from: `_archived/autonomous_workflow_v1/gates/qg_page_object.py`
  - Keep: Detection methods, pattern constants
  - Remove: Multi-page tracking, file writing
  - Add: 4-layer validation, DD-27 check

- `mcp_server/tools/gates/qg_framework_compliance.py` - Step 7 validation
  - New gate for final compliance check
  - Validates all Design Decisions (DD-27, return values, decorators)

### Gate Tests (TDD)
- `mcp_server/_dev_tests/test_gates/test_qg_skeleton.py`
- `mcp_server/_dev_tests/test_gates/test_qg_framework_compliance.py`

### Documentation Updates
- `SKILL.md` - Update to 7-step workflow v4.0
- `CLAUDE.md` - Update workflow overview
- `docs/projects/pair-programming/2-prd-v4.md` - NEW (next session)
- `docs/projects/pair-programming/3-tasks-v4.md` - NEW (after PRD)

---

## Architecture Comparison

### v3.1 (Current)
```
Step 1: User Input
Step 2: Pre-flight Config
Step 3: AI Processing
Step 4: Tool 2 (discover elements) + Manual Construction ← Problem
```

**Problem:** Step 4 protocol still has autonomous machinery (navigation tracking, visual feedback, multi-page detection, two-pass discovery).

### v4.0 (New - Pair Programming)
```
Step 1: User Input ✓
Step 2: Pre-flight Config ✓
Step 3: AI Processing ✓
Step 4: Discovery (simplified)
Step 5: Generate Skeleton (AI + gate)
Step 6: HITL Iteration (Step 11 pattern)
Step 7: Framework Validation (gate)
```

**Benefits:**
- Clear separation of concerns (discover → generate → iterate → validate)
- Each step has ONE job
- HITL iteration is explicit step (not buried in Step 4)
- Faster to working test (generate all 4 layers at once, then iterate)

---

## Component Usage Logic (Reference)

### Defense-in-Depth Components (6 Total)

**From `.business/architecture/execution_patterns.md`:**

**Core Defense Layers (4):**
1. **Protocols (Layer 1)** - Preventive: Define correct behavior BEFORE execution
2. **Smart Gates (Layer 2)** - Detective + Corrective: Validate AND teach
3. **Hooks (Layer 3)** - Continuous Detective: Monitor EVERY action
4. **State Checkpointing (Layer 4)** - Recovery: Enable resume from known good state

**Supporting Infrastructure (2):**
5. **Audit System** - Observability: Immutable logging for compliance/debugging
6. **HITL System** - Human Oversight: Confirmations for critical decisions

### Our Workflow Pattern: Assembly Line (Sequential Pipeline)

**Characteristics:**
- Steps are SEQUENTIAL and DEPENDENT
- Step N output is input to Step N+1
- Metadata flows through pipeline
- Cannot skip steps (enforcement via gates)

**Component Application:**

| Component | When It Acts | Always Present? |
|-----------|--------------|-----------------|
| **Protocol** | BEFORE step execution (AI reads) | ✅ Every step |
| **Gate** | DURING step (PRE+POST validation) | ✅ Every step (except Step 6 iteration) |
| **Hook** | AFTER every tool call (PostToolUse) | ✅ System-wide (automatic) |
| **State** | AFTER gate PASS (checkpoint saved) | ✅ Every step |
| **Audit** | AFTER gate call (via PostToolUse hook) | ✅ System-wide (automatic) |
| **HITL** | DURING step (when decision needed) | ⚠️ Conditional (only Steps 2, 6) |

### Component Usage Per Step

| Step | Protocol | Gate | Hook | State | Audit | HITL |
|------|----------|------|------|-------|-------|------|
| 1. User Input | ✅ | ✅ PRE+POST | ✅ | ✅ | ✅ | ⚠️ See note |
| 2. Pre-flight | ✅ | ✅ PRE+POST | ✅ | ✅ | ✅ | ✅ Config choices |
| 3. AI Processing | ✅ | ✅ PRE+POST | ✅ | ✅ | ✅ | ❌ |
| 4. Discovery | ✅ | ✅ PRE+POST | ✅ | ✅ | ✅ | ❌ |
| 5. Generate Skeleton | ✅ | ✅ PRE+POST | ✅ | ✅ | ✅ | ❌ |
| 6. HITL Iteration | ✅ | ⚠️ See note | ✅ | ✅ | ✅ | ✅ Core feature |
| 7. Framework Validation | ✅ | ✅ PRE+POST | ✅ | ✅ | ✅ | ❌ |

**Notes:**

**Step 1 HITL (⚠️):**
- **NOT formal HITL** - Gate retry mechanism handles corrections
- Gate fails → Returns fix hint → User provides corrected input → Retry gate
- HITL is for structured choices between valid options (like Step 2 config)
- Step 1 is correcting invalid input, not choosing between valid options

**Step 6 Gate (⚠️):**
- **QUESTION:** Should Step 6 have exit gate to validate test is green before Step 7?
- Option A: No gate during iteration, Step 7 PRE checks test passing
- Option B: Exit gate after iteration confirms test green
- **TO BE DECIDED**

### HITL vs Gate Retry Pattern

**Gate Retry (Steps 1, 3, 4, 5, 7):**
```
Gate FAIL → Fix hint returned → User corrects input → Retry gate
Purpose: Corrective action after validation failure
Example: User provides invalid persona format
```

**HITL (Steps 2, 6):**
```
AI presents options → User chooses → Choice captured → Workflow continues
Purpose: Decision between multiple valid options
Example: Choose credential strategy (static/dynamic/self-contained)
```

---

## Detailed Step Design

**Design each step completely before moving to the next.**

### Design Completeness Checklist (Per Step)

For each step, design ALL of the following:

**1. Component Identification:**
- ✅ Which components apply?
- ✅ Why/why not for each?

**2. Component Content (What's IN each component):**
- **Protocol:** Step-by-step actions AI must perform
- **Gate:** Exact PRE/POST validation rules, fix hints
- **Hook:** What events trigger, what gets logged
- **State:** Schema (what fields saved, data types)
- **Audit:** Log entry format, what events logged
- **HITL:** Options presented, how choice captured (if applicable)
- **Workflow Transcript:** What gets written to markdown file

**3. Data Flow:**
- Inputs (from previous step)
- Outputs (to next step)
- State transformations

**4. Error Handling:**
- What can fail?
- How to recover?
- Fix hints for each error

**5. Success Criteria:**
- When is step complete?
- What must be true to proceed to next step?

---

## Step 1: User Input

### Component Identification

| Component | Used? | Why / Why Not |
|-----------|-------|---------------|
| **Protocol** | ✅ | Defines step-by-step actions for collecting user input |
| **Gate** | ✅ | `qg_user_input` validates persona format, URL, extracts role/workflow |
| **Hook** | ✅ | PostToolUse automatically logs all gate calls |
| **State** | ✅ | Saves checkpoint with persona, role_name, workflow, url |
| **Audit** | ✅ | Logs gate results, workflow transcript updated |
| **HITL** | ❌ | NOT formal HITL - Gate retry handles input corrections. User corrects invalid input (not choosing between valid options). |

**HITL Clarification:**
- If user provides invalid persona → Gate FAIL → Fix hint shown → User corrects → Retry
- This is **gate retry**, not HITL (no structured choice between valid options)

### Execution Flow

```
┌─────────────────────────────────────────────────────────┐
│                   STEP 1: USER INPUT                     │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │ BEFORE EXECUTION    │
              │ Protocol defines    │
              │ actions             │
              └─────────────────────┘
                          │
                          ▼
              ┌─────────────────────┐
              │ DURING EXECUTION    │
              └─────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼
   ┌────────┐      ┌────────────┐    ┌──────────┐
   │ Gate   │      │ Hook       │    │ State    │
   │ PRE    │──┬──▶│ PostToolUse│───▶│ (on PASS)│
   └────────┘  │   └────────────┘    └──────────┘
        │      │          │                 │
        │      └──────────┼─────────────────┤
        │                 ▼                 ▼
        │           ┌────────────┐    ┌──────────┐
        │           │ Audit Log  │    │ Workflow │
        │           │ Gate PRE   │    │ Transcript│
        │           └────────────┘    └──────────┘
        ▼
   AI extracts:
   - role_name
   - workflow
        │
        ▼
   ┌────────┐
   │ Gate   │
   │ POST   │──┬───▶ Hook ───▶ Audit + Transcript
   └────────┘  │
        │      │
        ▼      ▼
   PASS?   State Checkpoint Saved
        │
        ├─ YES ──▶ Proceed to Step 2
        │
        └─ NO ──▶ Fix hint → User corrects → Retry
```

### Inputs

**From User:**
- Persona (e.g., "As a registered user...")
- URL (target application)
- Requirement (what they want to test)

**From System:**
- None (first step)

### Outputs

**To Step 2:**
- `persona` - User persona string
- `role_name` - Extracted role (e.g., "RegisteredUser")
- `workflow` - Detected workflow domain (e.g., "auth", "catalog")
- `url` - Target application URL

**To State:**
- All above fields saved to `tests/_state/{run_id}/workflow_state.json`

### Gap Analysis (Current vs v4.0 Requirements)

**Current Implementation Review:**
- Protocol: `.claude/skills/qa-management-layer/references/step-01.md`
- Gate: `mcp_server/tools/gates/qg_user_input.py`

| Component | What Exists | What's Missing | Gap Status |
|-----------|-------------|----------------|------------|
| **Protocol** | ✅ Step-by-step actions defined<br>✅ ASK questions format<br>✅ EXTRACT data logic<br>✅ Environment auto-detect | ⚠️ Hook behavior not documented<br>⚠️ Audit log format not specified<br>⚠️ Workflow transcript format missing | MINOR GAPS |
| **Gate** | ✅ POST validation implemented<br>✅ All field validators<br>✅ Fix hints for all errors<br>✅ Environment detection | ❌ PRE mode not implemented (POST-only)<br>❓ Do we need PRE for Step 1? | QUESTION |
| **Hook** | ✅ System-wide (automatic) | ❌ Not documented in protocol<br>❌ What events logged? | DOCUMENTATION GAP |
| **State** | ✅ Schema defined<br>✅ Saves on gate PASS<br>✅ All fields specified | ✅ Complete | NO GAPS |
| **Audit** | ⚠️ Mentioned in protocol | ❌ Log entry format not specified<br>❌ What fields logged? | SPECIFICATION GAP |
| **HITL** | ❌ Not present | ✅ Correctly not present (gate retry handles corrections) | NO GAPS |
| **Workflow Transcript** | ⚠️ Mentioned in protocol | ❌ Markdown format not specified<br>❌ What content included? | SPECIFICATION GAP |

### Design Decisions for Step 1

**Decision 1: Does Step 1 need PRE mode gate?**

**DECIDED:** ✅ No PRE gate needed (POST-only is sufficient)

**Rationale:**
- Step 1 is first step (no prerequisites to validate)
- POST validation covers all requirements (persona, URL, role_name, workflow)
- Keeps implementation simple
- PRE would be redundant

**Implementation:** Keep current POST-only gate

---

**Decision 2: Workflow Transcript Format**

**DECIDED:** ✅ Simple markdown format for user visibility

**Purpose:** User-visible progress tracking (NOT for compliance - audit log handles that)

**Location:** `tests/_reports/<run_id>/workflow_transcript.md`

**Format:**

```markdown
# Workflow Transcript - 2026-01-23T10-30-45.123456Z

**Workflow:** helios7
**Environment:** staging
**Started:** 2026-01-23 10:30:45 UTC
**Status:** In Progress

---

## Step 1: User Input ✓
**Completed:** 2026-01-23 10:30:52 UTC
**Duration:** 7 seconds

### User Inputs
- **Requirement:** "As a registered user, I want to login with email and password"
- **URL:** https://staging.example.com/login
- **Workflow:** helios7

### Extracted Data
- **Persona:** registered user
- **Role Name:** RegisteredUser
- **Environment Detected:** staging

### Gate Result
✓ **PASS** - qg_user_input (POST)

---

## Step 2: Pre-flight Configuration
**Status:** In Progress
**Started:** 2026-01-23 10:30:53 UTC

### Configuration Decisions
⏳ Pending...

---

## Summary
- **Steps Completed:** 1 / 7
- **Gates Passed:** 1
- **Gates Failed:** 0
- **Current Step:** 2 (Pre-flight Configuration)
```

**Rules:**
- Append-only (don't overwrite)
- One section per step
- Show user inputs, extracted data, gate results
- Simple markdown (readable in any editor)
- Status indicators (✓ ⏳ ❌)
- Timestamps + durations
- Running summary at bottom

---

**Decision 3: Audit Log Entry Format**

**DECIDED:** ✅ Use existing audit schema for MVP, defer compliance upgrades to post-MVP

**MVP Approach:** Use existing audit schema (v1.0) - already implemented and sufficient for MVP.

**Current Audit Schema (v1.0 - EXISTING):**

```python
{
  "workflow_id": "2026-01-23T10-30-45.123456Z",
  "events": [
    {
      "type": "gate_validation",
      "step": 1,
      "gate": "qg_user_input",
      "mode": "POST",
      "result": "pass",
      "timestamp": "2026-01-23T10-30-45.567890Z",
      "source": "tool",  # Optional
      "error": "...",   # Optional (on fail)
      "metadata": {     # Optional
        "persona": "registered user",
        "URL": "https://example.com/login",
        "role_name": "RegisteredUser"
      }
    },

    {
      "type": "self-heal",
      "step": 2,
      "attempt": 1,
      "error": "...",
      "timestamp": "2026-01-23T10-30-46.678901Z"
    }
  ]
}
```

**What's Already Implemented:**
- ✅ Event-driven audit trail (typed events)
- ✅ Atomic writes per event (crash-safe, DEF-040)
- ✅ Immutable logging to `tests/_audit/`
- ✅ Timestamping (ISO-8601)
- ✅ Per-run isolation (unique workflow_id)
- ✅ Gate validation logging
- ✅ Self-heal attempt logging

**MVP Scope:**
- Use existing AuditLogger as-is
- No schema changes needed
- Already sufficient for development and initial customers

**Post-MVP (Out of Scope - See "Future Work" Section):**
- Regulatory compliance upgrades (HIPAA, SOX, GDPR, EU AI Act)
- Actor tracking (WHO)
- Decision rationale (WHY)
- Integrity hashing (tamper detection)
- Retention metadata
- Feature flag-based compliance profiles

---

### Component Content Design

**STATUS:** ✅ Complete - All specifications defined

#### Protocol: Step-by-Step Actions

**v4.0 PROTOCOL (Updated from step-01.md):**

```
PRE-CHECK:
- None (first step)

ACTION:
1. ASK user: "What test do you want to create?"
   Format: "As a [persona], I want to [action]"
   Example: "As a registered user, I want to login with email and password"

2. ASK user: "What is the URL for this action?"
   Example: "https://example.com/login"

3. ASK user: "Workflow identifier?"
   Explanation: "This creates folders at framework/pages/{workflow}/ and tests/{workflow}/
                Use to organize tests by: test run (helios7), feature (checkout-v2), sprint (auth-sprint-2)"

4. EXTRACT from requirement:
   - persona: Extract from "As a [X]" pattern
   - role_name: Convert persona to PascalCase (registered user → RegisteredUser)
   - raw_requirement: Store full user requirement verbatim

5. AUTO-DETECT environment:
   - Check URL against framework/resources/config/environment_config.json
   - If match found → detected_env_id = environment name
   - If no match → ASK user: "Unknown environment. Should I create config for '{url_domain}'?"

VALIDATE:
6. CALL qg_user_input (POST mode only - no PRE gate)
   - Validates all extracted fields
   - Returns PASS/FAIL with fix hints

RETRY:
7. If gate FAIL: RE-ASK the invalid/missing field with fix hint
   - No max retries (user provides input, not AI)

POST-ACTION:
8. WRITE workflow transcript entry to tests/_reports/<run_id>/workflow_transcript.md
   - Include: step name, user inputs, extracted fields, gate result, timestamp
   - Append mode (don't overwrite existing content)
   - Create directory and file on first write if they don't exist

9. Proceed to Step 2
```

**Key Changes from v3.0:**
- ✅ No PRE gate (Decision 1)
- ✅ Workflow transcript format specified (Decision 2)
- ✅ Audit log v2.0 format specified (Decision 3)

---

#### Gate Validation Rules

**POST Validation (POST-only, no PRE):**

**Required Fields:**
- `persona` - Must be present and non-empty
- `URL` - Must be valid HTTP/HTTPS URL
- `role_name` - Must be PascalCase (e.g., RegisteredUser)
- `workflow` - Must be non-empty string (dynamic, not hardcoded)
- `raw_requirement` - Must be present (full user input)

**Validation Logic (from qg_user_input.py):**

```python
# Persona validation (DD-01)
def _is_valid_persona(cls, value: Any) -> bool:
    if value is None or value == "":
        return False
    return isinstance(value, str) and len(value.strip()) > 0

# URL validation (DD-02)
def _is_valid_url(cls, value: Any) -> bool:
    if not cls.URL_PATTERN.match(value):  # r'^https?://\S+$'
        return False
    result = urlparse(value)
    return all([result.scheme in ('http', 'https'), result.netloc])

# Role name validation
def _is_valid_role_name(cls, value: Any) -> bool:
    # Must be PascalCase (starts with uppercase, alphanumeric)
    return bool(cls.PASCAL_CASE_PATTERN.match(value))  # r'^[A-Z][a-zA-Z0-9]*$'

# Workflow validation
def _is_valid_workflow(cls, value: Any) -> bool:
    # Any non-empty string (dynamic, not hardcoded)
    return isinstance(value, str) and len(value.strip()) > 0
```

**Environment Detection:**
- Matches URL domain against `environment_config.json`
- Returns `detected_env_id` or NEEDS_RETRY with scaffolding template

**Fix Hints (Teaching Pattern):**

```python
# Example: Invalid persona
return cls.fail_response(
    error="Invalid persona: must be non-empty",
    fix_hint="Persona must be a non-empty string describing the user role. "
             "Example: 'registered user', 'guest', 'admin'"
)

# Example: Invalid URL
return cls.fail_response(
    error=f"Invalid URL format: '{url}'",
    fix_hint="URL must be a valid HTTP or HTTPS URL. "
             "Example: 'http://automationpractice.pl/index.php?controller=authentication'"
)

# Example: Invalid role_name
return cls.fail_response(
    error=f"Invalid role_name: '{role_name}' must be PascalCase",
    fix_hint="role_name must be a PascalCase identifier derived from persona. "
             "Example: 'RegisteredUser', 'GuestUser', 'AdminUser'"
)
```

**On PASS:**
- Gate calls StateManager to save checkpoint
- Returns `{"status": "pass"}`

**On FAIL:**
- Returns `{"status": "fail", "error": "...", "fix_hint": "..."}`
- AI presents fix hint to user
- User corrects input
- Retry validation

---

#### State Schema

**Saved to:** `tests/_state/{run_id}/workflow_state.json`

**Format:**

```json
{
  "step": 1,
  "status": "complete",
  "timestamp": "2026-01-23T10:30:52.123456Z",
  "data": {
    "persona": "registered user",
    "URL": "https://staging.example.com/login",
    "role_name": "RegisteredUser",
    "workflow": "helios7",
    "raw_requirement": "As a registered user, I want to login with email and password",
    "detected_env_id": "staging"
  }
}
```

**State Management:**
- Saved by `qg_user_input` gate on PASS (via BaseGate.validate_and_pass())
- Per-run isolation (unique run_id)
- Used by subsequent steps to retrieve user input

---

#### Audit Log Entries (v1.0 Schema - MVP)

**Step 1 Audit Event:**

```json
{
  "type": "gate_validation",
  "step": 1,
  "gate": "qg_user_input",
  "mode": "POST",
  "result": "pass",
  "timestamp": "2026-01-23T10:30:52.567890Z",
  "source": "tool",
  "metadata": {
    "persona": "registered user",
    "URL": "https://staging.example.com/login",
    "role_name": "RegisteredUser",
    "workflow": "helios7",
    "detected_env_id": "staging"
  }
}
```

**Top-Level Structure:**

```json
{
  "workflow_id": "2026-01-23T10-30-45.123456Z",
  "events": [
    {
      "type": "gate_validation",
      "step": 1,
      "gate": "qg_user_input",
      "mode": "POST",
      "result": "pass",
      "timestamp": "2026-01-23T10:30:52.567890Z",
      "source": "tool",
      "metadata": {...}
    }
  ]
}
```

---

#### Hook Behavior

**PostToolUse Hook (audit-trail-writer.py):**

**Trigger:** After EVERY MCP tool call (including qg_user_input)

**Behavior:**
1. Intercepts tool result
2. Extracts gate name, step, result, metadata
3. Calls AuditLogger.log_gate()
4. Writes to `tests/_audit/audit_log_{run_id}.json` (atomic persist)
5. Non-blocking (doesn't interfere with workflow)

**What Gets Logged:**
- Gate name (qg_user_input)
- Step number (1)
- Mode (POST)
- Result (pass/fail)
- Error message (if fail)
- Metadata (persona, URL, role_name, workflow, detected_env_id)
- Source (tool/ai/self-heal) - optional
- Timestamp

**Crash Safety:**
- Atomic write after each event (DEF-040)
- No data loss even if workflow crashes mid-step

---

#### Workflow Transcript

**Location:** `tests/_reports/{run_id}/workflow_transcript.md`

**Step 1 Entry:**

```markdown
## Step 1: User Input ✓
**Completed:** 2026-01-23 10:30:52 UTC
**Duration:** 7 seconds

### User Inputs
- **Requirement:** "As a registered user, I want to login with email and password"
- **URL:** https://staging.example.com/login
- **Workflow:** helios7

### Extracted Data
- **Persona:** registered user
- **Role Name:** RegisteredUser
- **Environment Detected:** staging

### Gate Result
✓ **PASS** - qg_user_input (POST)
```

**Write Pattern:**
- AI writes entry after gate PASS
- Append mode (don't overwrite)
- Create file on first write if doesn't exist
- Simple markdown (readable without tools)

### Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| Missing persona | User didn't provide persona | ASK user for persona |
| Invalid persona format | Doesn't start with "As a" | Show fix hint with format |
| Missing URL | User didn't provide URL | ASK user for URL |
| Invalid URL | Malformed URL | Show fix hint with example |
| Role extraction failed | Persona doesn't contain clear role | ASK user to clarify role |

**On error:**
1. Gate returns FAIL with fix hint
2. AI presents fix hint to user
3. User provides corrected input
4. Retry gate validation

### Success Criteria

**Step 1 Complete When:**
- ✅ `qg_user_input` POST validation passes
- ✅ State saved with all required fields (persona, role_name, workflow, URL, raw_requirement, detected_env_id)
- ✅ Workflow transcript entry written
- ✅ Audit log event recorded (gate_validation + workflow_transition)

**Ready for Step 2 When:**
- All above criteria met
- State contains: `persona`, `role_name`, `workflow`, `URL`, `detected_env_id`
- Workflow transcript shows Step 1 ✓ complete

**Data Flow to Step 2:**
```
Step 1 State → Step 2 Inputs
  persona → Used for credential strategy question
  workflow → Used for test data location question
  URL → Used for browser navigation target
  role_name → Used for Role class scaffolding
  detected_env_id → Used for environment config selection
```

---

## ✅ Step 1: DESIGN COMPLETE

**Summary:**
- ✅ Component identification complete (Protocol, Gate, State, Audit, Hook, Transcript)
- ✅ All 3 design decisions finalized
- ✅ Protocol actions specified
- ✅ Gate validation rules documented
- ✅ State schema defined
- ✅ Audit log schema (v1.0 MVP - existing implementation)
- ✅ Workflow transcript format specified
- ✅ Error handling defined
- ✅ Success criteria established

**Key Design Outcomes:**
1. **No PRE gate** - POST-only validation (Decision 1)
2. **Workflow transcript format** - Simple markdown for user visibility (Decision 2)
3. **Audit v1.0 schema** - Use existing implementation for MVP, defer compliance upgrades to post-MVP (Decision 3)

**Implementation Notes:**
- Reuse existing `qg_user_input.py` gate (POST validation already implemented)
- Upgrade `AuditLogger` to v2.0 schema (P0: actor tracking, retention metadata, workflow context)
- Protocol updates: Add workflow transcript write step
- Hook: PostToolUse already implemented (`.claude/hooks/audit-trail-writer.py`)

**Ready for:** Step 2 Design

---

## Step 2: Pre-flight Configuration

**STATUS:** Ready to design

### Components Used

| Component | Used? | Purpose |
|-----------|-------|---------|
| Protocol | ✅ | TBD |
| Gate | ✅ | TBD |
| Hook | ✅ | TBD |
| State | ✅ | TBD |
| Audit | ✅ | TBD |
| HITL | ❌ | TBD |

### Inputs
TBD

### Outputs
TBD

### Component Details
TBD

---

## Step 3: AI Processing

**STATUS:** To be designed

---

## Step 4: Discovery (Simplified)

**Purpose:** Discover elements quickly, save to state.

**Actions:**
1. Navigate to target URL
2. Reveal dynamic elements (login if needed)
3. Playwright snapshot extraction
4. Extract input + output elements
5. Save to state

**Time:** 5 minutes

**Gate:** `qg_discovered_elements` (existing, simplified)

**Output:** `discovered_elements` array in state

---

### Step 5: Generate Skeleton

**Purpose:** Generate ALL 4 layers (POM, Task, Role, Test) quickly.

**Actions:**
1. AI reads Step 4 elements
2. AI writes POM code using elements
3. AI writes Task code using POM
4. AI writes Role code using Task
5. AI writes Test code using Role
6. Gate validates basic structure

**Time:** 10 minutes

**Gate:** `qg_skeleton` (NEW)

**Output:** 4 files on disk (RUNNABLE, bugs OK)

**NO Python tool** - AI generates code directly, gate validates

**Gate Validation:**
- All 4 files exist
- No skeleton code (pass, TODO, NotImplementedError)
- No layer violations (Tasks importing POMs ✓, POMs importing Tasks ✗)
- DD-27: No locators in Tasks (CRITICAL)
- Imports resolve
- Basic structure present

---

### Step 6: HITL Iteration

**Purpose:** Collaborate with user to fix bugs until test passes.

**Pattern:** Run → Fail → Triage → Fix → Repeat

**Actions:**
1. AI runs test (browser visible)
2. Test fails
3. AI captures diagnostics (7 types from Step 11)
4. AI presents 3 triage options:
   - **Locator issue** → AI fixes POM selectors
   - **Flow issue** → AI fixes Task/Role orchestration
   - **Logic issue** → User guides fix
5. User selects option
6. AI implements fix
7. Repeat until test passes

**Time:** Variable (depends on complexity)

**Gate:** None (validation happens in Step 7)

**HITL:** 3 structured triage options

**Output:** Working test (green)

**Borrowed from:** Archived Step 11 HITL pattern

---

### Step 7: Framework Validation

**Purpose:** Final compliance check - ensure code matches 4-layer architecture.

**Actions:**
1. Gate validates all Design Decisions
2. Check DD-27 (no locators in Tasks) - CRITICAL
3. Check return values (POMs return self, Tasks/Roles return None)
4. Check decorators (@autologger placement)
5. Check layer boundaries (composition not inheritance)

**Time:** 1 minute (automated validation)

**Gate:** `qg_framework_compliance` (NEW)

**Output:** Framework-compliant code

**State:** Mark workflow complete

---

## Key Insights

### 1. Protocols + Gates = Teaching System

Gates don't just validate - they encode framework rules and teach through fix hints. This is more reliable than AI inferring patterns from examples.

**Example:**
```python
# Gate teaches via fix hint
return cls.fail_response(
    error="Task contains locators (DD-27 violation)",
    fix_hint="Remove locators from Task. Only POMs should have locators. Tasks call POM methods."
)
```

### 2. AI for Code, Tools for Operations

Clear division of labor:
- **AI generates CODE:** POM, Task, Role, Test (adaptable, context-aware)
- **Python tools for OPERATIONS:** Playwright interaction, pytest subprocess

This is lighter weight and more flexible than maintaining Python code generators.

### 3. Generate Fast, Iterate via HITL

Don't build 4 layers element-by-element (too slow, loses momentum). Generate all 4 layers quickly (10 min), then iterate via HITL until working.

**Key insight from Step 11:** Fast feedback loop (run → fail → fix) works better than perfect upfront construction.

### 4. Defense-in-Depth is Not Over-Engineering

This product needs all 6 components:
- Enterprise QA tool (compliance)
- High-value output (test code)
- Complex workflow (7 steps)
- Already has 4/6 implemented

The 6-component architecture is appropriate for this product's requirements.

### 5. Reuse 60% of Validation Logic

Archived gates contain proven validation patterns. Reuse core detection methods, strip autonomous workflow machinery, add 4-layer checks.

Faster implementation, battle-tested patterns.

---

## References

### Architecture
- `.business/architecture/execution_patterns.md` - 6-component defense-in-depth model

### Archived Autonomous Workflow (Reference)
- `_archived/autonomous_workflow_v1/protocols/step-06.md` - Old POM generation protocol
- `_archived/autonomous_workflow_v1/gates/qg_page_object.py` - Reusable validation logic
- `_archived/autonomous_workflow_v1/protocols/step-11.md` - HITL pattern (borrow for Step 6)

### Current Working Components
**Protocols:**
- `.claude/skills/qa-management-layer/references/step-01.md` - User Input
- `.claude/skills/qa-management-layer/references/step-02.md` - Pre-flight Config
- `.claude/skills/qa-management-layer/references/step-03.md` - AI Processing
- `.claude/skills/qa-management-layer/references/step-04.md` - Discover Elements (to simplify)

**Gates:**
- `mcp_server/tools/gates/qg_user_input.py`
- `mcp_server/tools/gates/qg_preflight.py`
- `mcp_server/tools/gates/qg_ai_processing.py`
- `mcp_server/tools/gates/qg_discovered_elements.py`

**Example Code (Framework Patterns):**
- `tests/helios7/test_submit_new_customer_inquiry.py` - 4-layer example
- `framework/roles/helios7/dealership_staff_member.py` - Role pattern
- `framework/tasks/helios7/helios7_tasks.py` - Task pattern
- `framework/pages/helios7/customer_search_page.py` - POM pattern

---

## Future Work (Post-MVP)

### Compliance Audit System v2.0

**Status:** Out of scope for MVP. Designed for future vertical expansion (healthcare, finance, AI-regulated industries).

**Design Complete:** Feature flag-based compliance profiles with regulatory mapping.

#### Architecture: Configuration-Driven Compliance

**Compliance Profiles:** `mcp_server/config/audit_config.json`

```json
{
  "compliance_profile": "minimal",  // Active profile

  "profiles": {
    "minimal": {
      "description": "Basic audit trail (MVP/development)",
      "regulations": [],
      "enabled_fields": ["event_id", "type", "timestamp", "actor"]
    },

    "healthcare": {
      "description": "HIPAA compliance",
      "regulations": ["HIPAA"],
      "enabled_fields": ["event_id", "type", "timestamp", "actor", "retention", "integrity_hash", "access_log"]
    },

    "finance": {
      "description": "SOX compliance",
      "regulations": ["SOX"],
      "enabled_fields": ["event_id", "type", "timestamp", "actor", "retention", "integrity_hash", "workflow_context"]
    },

    "ai_regulated": {
      "description": "EU AI Act compliance",
      "regulations": ["EU_AI_ACT"],
      "enabled_fields": ["event_id", "type", "timestamp", "actor", "decision_rationale", "retention", "workflow_context"]
    },

    "full_compliance": {
      "description": "All regulations",
      "regulations": ["HIPAA", "SOX", "GDPR", "EU_AI_ACT"],
      "enabled_fields": ["event_id", "type", "timestamp", "actor", "decision_rationale", "retention", "integrity_hash", "workflow_context", "access_log"]
    }
  }
}
```

#### Enhanced Audit Schema (v2.0)

**New Fields (enabled via profiles):**

| Field | Required By | Description |
|-------|-------------|-------------|
| `actor` | HIPAA, SOX | WHO triggered action (user/AI/system) |
| `decision_rationale` | EU AI Act Article 13 | WHY AI made this decision |
| `retention` | GDPR, HIPAA (6yr), EU AI Act (3yr) | Expiry, compliance tags, data classification |
| `integrity_hash` | SOX, HIPAA | SHA-256 tamper detection |
| `workflow_context` | All | Persona, workflow, env_id (top-level) |
| `access_log` | HIPAA | Who reads audit data |

**Example Enhanced Event:**

```json
{
  "event_id": "evt_001",
  "type": "gate_validation",
  "timestamp": "2026-01-23T10:30:52.567890Z",

  "actor": {
    "type": "ai",
    "id": "claude-sonnet-4.5",
    "session_id": "cli_session_xyz"
  },

  "decision_rationale": {
    "extracted_intent": "user_login",
    "confidence": 0.95,
    "alternatives_considered": ["user_registration"],
    "why_chosen": "BDD contains 'existing user' and 'login' keywords"
  },

  "metadata": {...}
}
```

#### Benefits of Feature Flag Approach

✅ **Simple gate logic** - Gates call `log_gate()`, config handles compliance
✅ **Easy profile switching** - Change one line, entire system adapts
✅ **No code changes per vertical** - Same codebase, different config
✅ **Clear compliance mapping** - Each field documents regulation
✅ **Gradual adoption** - Start minimal, enable fields as needed
✅ **Testable** - Test each profile independently
✅ **No N/A clutter** - Disabled fields not logged

#### Implementation Phases

**Phase 1 (Post-MVP):**
1. Create `AuditConfigManager` class
2. Update `AuditLogger` to use config-driven validation
3. Add field definitions with regulatory mapping

**Phase 2 (Vertical Expansion):**
4. Test `healthcare` profile against HIPAA checklist
5. Test `finance` profile against SOX checklist
6. Test `ai_regulated` profile against EU AI Act checklist

**Phase 3 (Enterprise):**
7. Platform settings UI for profile selection
8. Per-customer profile configuration
9. Compliance report generator

---

## Next Steps

### Phase 2: Define (Next Session)
1. **Create PRD** - `docs/projects/pair-programming/2-prd-v4.md`
   - Step 5: Generate Skeleton requirements
   - Step 6: HITL Iteration requirements
   - Step 7: Framework Validation requirements
   - Gate validation rules
   - HITL triage options
   - Component interactions

### Phase 3: Test Planning (After PRD)
2. **Create Test Pyramids** - For each of 6 components
   - Analyze each component using 6 discovery questions
   - Define unique test layers per component
   - Ensure layers answer distinct questions

3. **Create Test Matrix** - `docs/TEST_PLAN.md`
   - 3D matrix: 7 steps × 6 components × pyramid layers
   - Apply test categories (happy, negative, edge)
   - Assign priorities (P0, P1, P2)
   - Define entry/exit criteria

### Phase 4: Divide (After Test Plan)
4. **Break into Tasks** - `docs/projects/pair-programming/3-tasks-v4.md`
   - TDD tasks (gates, state, audit)
   - Test-after tasks (protocols, hooks, HITL)
   - Prioritize tasks
   - Add done-when criteria

### Phase 5: Deliver (TDD Implementation)
5. **Gates (TDD)** - `qg_skeleton.py`, `qg_framework_compliance.py`
   - Write tests first (pattern detection, validation logic, fix hints)
   - Implement to make tests pass
   - Refactor
   - Reuse from `qg_page_object.py` where applicable

6. **State (TDD)** - State validation tests
   - Write tests first (save/load, isolation, recovery)
   - Implement validation
   - Refactor

7. **Audit (TDD)** - Audit logging tests
   - Write tests first (format, immutability, completeness)
   - Implement logging
   - Refactor

8. **Protocols (Test-After)** - `step-05.md`, `step-06.md`, `step-07.md`
   - Implement protocols
   - Write integration tests
   - Verify AI behavior

9. **Hooks (Test-After)** - Hook verification
   - Verify existing hooks work
   - Write integration tests
   - Test non-blocking behavior

10. **HITL (Test-After)** - Step 6 iteration flow
    - Implement triage options
    - Write integration tests
    - Verify user interaction flow

11. **Integration**
    - Register gates with MCP server
    - Update SKILL.md
    - Test E2E workflow
    - Verify coverage targets met

---

## Testing Strategy

### Testing Philosophy

**Test ALL 6 defense-in-depth components, not just gates.**

From `.business/architecture/execution_patterns.md`:
> The Isagawa Platform is built on six components: Protocols, Smart Gates, Hooks, State Checkpointing, Audit System, HITL System.

**Each component must be tested to validate the defense-in-depth architecture works.**

### 3D Testing Matrix

**Dimension 1: Steps (1-7)**
- Each of the 7 workflow steps

**Dimension 2: Components (6 types)**
1. Protocol
2. Gate
3. Hook
4. State
5. Audit
6. HITL

**Dimension 3: Test Pyramid Layers (unique per component)**
- Each component gets its own pyramid based on what it does
- Pyramid layers answer the 6 discovery questions from `.claude/skills/testing/SKILL.md`

**Coverage Matrix:**

```
           │ Protocol │ Gate │ Hook │ State │ Audit │ HITL │
───────────┼──────────┼──────┼──────┼───────┼───────┼──────┤
Step 1     │    [ ]   │  [x] │  [x] │  [x]  │  [x]  │  -   │
Step 2     │    [ ]   │  [x] │  [x] │  [x]  │  [x]  │  -   │
Step 3     │    [ ]   │  [x] │  [x] │  [x]  │  [x]  │  -   │
Step 4     │    [ ]   │  [x] │  [x] │  [x]  │  [x]  │  -   │
Step 5     │    [ ]   │  [ ] │  [x] │  [x]  │  [x]  │  -   │
Step 6     │    [ ]   │  -   │  [x] │  [x]  │  [x]  │  [ ] │
Step 7     │    [ ]   │  [ ] │  [x] │  [x]  │  [x]  │  -   │
```

Legend:
- `[x]` = Component exists, needs tests
- `[ ]` = Component to be implemented, needs tests
- `-` = Not applicable

### Test Pyramid Examples (Illustrative)

**These are examples - actual pyramids created in Phase 3 after PRD.**

**Gate Component:**
```
┌─────────────────────────────────────────────────────┐
│                 GATE TEST PYRAMID                   │
├─────────────────────────────────────────────────────┤
│  1. PATTERN DETECTION  - Does it detect violations? │
│  2. VALIDATION LOGIC   - Does PRE/POST work?        │
│  3. FIX HINT QUALITY   - Are hints actionable?      │
│  4. STATE INTEGRATION  - Read/write state correct?  │
│  5. AUDIT INTEGRATION  - Logging works?             │
│  6. TEACHING EFFECT    - Do hints lead to fixes?    │
└─────────────────────────────────────────────────────┘
```

**Protocol Component:**
```
┌─────────────────────────────────────────────────────┐
│              PROTOCOL TEST PYRAMID                  │
├─────────────────────────────────────────────────────┤
│  1. STEP COMPLETENESS  - All actions defined?       │
│  2. AI COMPREHENSION   - Does AI understand steps?  │
│  3. OUTPUT FORMAT      - Correct structure?         │
│  4. GATE INTEGRATION   - Calls gates correctly?     │
│  5. ERROR RECOVERY     - Handles failures?          │
│  6. WORKFLOW FLOW      - Step → step transitions?   │
└─────────────────────────────────────────────────────┘
```

**State Component:**
```
┌─────────────────────────────────────────────────────┐
│               STATE TEST PYRAMID                    │
├─────────────────────────────────────────────────────┤
│  1. SAVE/LOAD          - Data persists correctly?   │
│  2. CHECKPOINT         - Recovery from checkpoint?  │
│  3. STATE ISOLATION    - Per-run isolation works?   │
│  4. CORRUPTION         - Handles bad state?         │
│  5. CONCURRENCY        - Safe parallel access?      │
│  6. CLEANUP            - Old states cleaned up?     │
└─────────────────────────────────────────────────────┘
```

**Audit Component:**
```
┌─────────────────────────────────────────────────────┐
│               AUDIT TEST PYRAMID                    │
├─────────────────────────────────────────────────────┤
│  1. LOG FORMAT         - JSON schema correct?       │
│  2. IMMUTABILITY       - Cannot modify logs?        │
│  3. COMPLETENESS       - All actions logged?        │
│  4. TIMESTAMP          - Accurate timestamps?       │
│  5. CORRELATION        - run_id tracking works?     │
│  6. RETENTION          - Old logs preserved?        │
└─────────────────────────────────────────────────────┘
```

**Hook Component:**
```
┌─────────────────────────────────────────────────────┐
│                HOOK TEST PYRAMID                    │
├─────────────────────────────────────────────────────┤
│  1. TRIGGER            - Fires on correct event?    │
│  2. EXECUTION          - Hook logic runs?           │
│  3. NON-BLOCKING       - Doesn't block workflow?    │
│  4. ERROR HANDLING     - Hook failure isolated?     │
│  5. AUDIT WRITE        - PostToolUse logs correctly?│
│  6. PERFORMANCE        - Fast enough?               │
└─────────────────────────────────────────────────────┘
```

**HITL Component:**
```
┌─────────────────────────────────────────────────────┐
│                HITL TEST PYRAMID                    │
├─────────────────────────────────────────────────────┤
│  1. TRIAGE OPTIONS     - 3 options presented?       │
│  2. USER CHOICE        - Choice captured?           │
│  3. FIX APPLICATION    - Fix applied correctly?     │
│  4. ITERATION          - Loop until green works?    │
│  5. DIAGNOSTICS        - 7 types captured?          │
│  6. AUDIT TRAIL        - Iterations logged?         │
└─────────────────────────────────────────────────────┘
```

### TDD Approach

**TDD Applicable (Test-First):**

| Component | Why TDD? | What to Test |
|-----------|----------|--------------|
| **Gates** | Deterministic validation logic | Pattern detection, PRE/POST validation, fix hints |
| **State** | Deterministic save/load | Persistence, isolation, recovery |
| **Audit** | Deterministic logging | Format, immutability, completeness |

**Test-After Applicable (Behavior Verification):**

| Component | Why Test-After? | What to Test |
|-----------|-----------------|--------------|
| **Protocols** | AI behavior guidance | AI follows steps, output format correct |
| **Hooks** | Event-driven integration | Triggers fire, execution completes, non-blocking |
| **HITL** | User interaction flow | Options presented, choice captured, iteration works |

**TDD Pattern (Gates, State, Audit):**
```
1. Write failing test (Red)
2. Implement minimal code (Green)
3. Refactor (Refactor)
4. Repeat for each test layer
```

**Test-After Pattern (Protocols, Hooks, HITL):**
```
1. Implement component
2. Write integration tests
3. Verify behavior matches design
4. Refactor if needed
```

### Phase Integration with Testing

**Updated 4D Framework with Testing:**

```
Phase 1: Design ✅ DONE
  └─ 7-step architecture
  └─ Key design decisions
  └─ Testing strategy defined (3D matrix, TDD approach)

Phase 2: Define (NEXT)
  └─ Create PRD for Steps 5-7
  └─ Detailed requirements per step
  └─ Gate validation rules
  └─ Component interactions
  └─ HITL triage options

Phase 3: Test Planning (AFTER PRD)
  └─ Create test pyramids for all 6 components
  └─ Apply pyramids across 7 steps
  └─ Test matrix (7 × 6 × pyramid layers)
  └─ Prioritize tests (P0, P1, P2)
  └─ Create docs/TEST_PLAN.md

Phase 4: Divide (AFTER test plan)
  └─ Break into implementation tasks
  └─ Break into test tasks (TDD tasks first)
  └─ Prioritize tasks
  └─ Add done-when criteria

Phase 5: Deliver (TDD where applicable)
  └─ TDD for Gates:
     • Write test for pattern detection
     • Implement detection
     • Write test for validation logic
     • Implement validation
     • Repeat per pyramid layer
  └─ TDD for State:
     • Write test for save/load
     • Implement persistence
     • Repeat per pyramid layer
  └─ TDD for Audit:
     • Write test for log format
     • Implement logging
     • Repeat per pyramid layer
  └─ Test-After for Protocols, Hooks, HITL:
     • Implement component
     • Write integration tests
     • Verify behavior
```

### Test Deliverables

**Phase 3 Output (Test Planning):**
- `docs/TEST_PLAN.md` - Comprehensive test plan with:
  - Test pyramids for all 6 components
  - Test matrix (7 steps × 6 components)
  - Priority assignments (P0, P1, P2)
  - Schedule (commit, PR, nightly, release)
  - Entry/Exit criteria

**Phase 5 Output (Delivery):**
- Gate tests: `mcp_server/_dev_tests/test_gates/`
- State tests: `mcp_server/_dev_tests/test_state/`
- Audit tests: `mcp_server/_dev_tests/test_audit/`
- Protocol tests: `mcp_server/_dev_tests/test_protocols/`
- Hook tests: `mcp_server/_dev_tests/test_hooks/`
- HITL tests: `mcp_server/_dev_tests/test_hitl/`

### Test Coverage Goals

**Per Component:**

| Component | Coverage Target | Why |
|-----------|----------------|-----|
| Gates | 95%+ | Core validation logic, critical path |
| State | 90%+ | Data integrity critical |
| Audit | 90%+ | Compliance logging |
| Protocols | 80%+ | Behavior validation |
| Hooks | 85%+ | Event handling |
| HITL | 75%+ | User interaction (harder to test) |

**Quality Gates:**

| Gate | Criteria |
|------|----------|
| Step complete | All P0 tests pass |
| PR merge | All P0 + P1 tests pass |
| Release | All tests pass, coverage targets met |

---

## Success Criteria

**Design Phase Complete When:**
- ✅ 7-step architecture defined
- ✅ Key design decisions documented
- ✅ Reusable artifacts identified
- ✅ Implementation approach defined
- ✅ Testing strategy defined

**Next Phase (Define) Complete When:**
- ⬜ PRD created with detailed requirements
- ⬜ Gate validation rules specified
- ⬜ HITL triage options defined
- ⬜ Component interactions documented

**Test Planning Phase Complete When:**
- ⬜ Test pyramids for all 6 components created
- ⬜ Test matrix (7 × 6 × pyramid layers) completed
- ⬜ docs/TEST_PLAN.md created
- ⬜ Priorities assigned (P0, P1, P2)

**Divide Phase Complete When:**
- ⬜ Implementation tasks broken down
- ⬜ Test tasks broken down (TDD tasks first)
- ⬜ Done-when criteria added
- ⬜ Task priorities assigned

**Delivery Phase Complete When:**
- ⬜ All P0 tests written and passing
- ⬜ All P1 tests written and passing
- ⬜ Gates implemented (TDD)
- ⬜ State validation implemented (TDD)
- ⬜ Audit logging implemented (TDD)
- ⬜ Protocols created (test-after)
- ⬜ Hooks verified (test-after)
- ⬜ HITL flow verified (test-after)
- ⬜ Coverage targets met
- ⬜ SKILL.md updated
- ⬜ E2E workflow tested and passing

---

**Design Phase Status:** ✅ COMPLETE

**Next Phase:** Define (Create PRD for Steps 5-7)

**Approach:**
- 4D Framework for design
- TDD for gates/state/audit
- Test-after for protocols/hooks/HITL
- Test pyramids created after PRD
- 3D testing matrix (steps × components × pyramid layers)
