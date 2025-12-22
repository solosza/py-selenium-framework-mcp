# Design Execution Engine

**Purpose:** Guide the design of complete execution engines (guidance layer + quality gates + operations + state) for any tool chain workflow.

**Applies to:** Any vertical with multi-step tool workflows (QA, API, PM, etc.)

---

## When to Use This Skill

Use when:
- You have a tool chain where data flows between steps
- AI orchestration has enforcement gaps (rules exist but aren't followed)
- You need to design validation that catches violations at step boundaries

---

## Workflow

```
For each step in your tool chain:
1. Lock down step definition (input, output, quality gate)
2. Document in vertical-specific file (e.g., FRAMEWORK.md)
3. Document generalized version here
4. Repeat for next step
5. RUN DESIGN AUDIT before PRD creation
6. CREATE DESIGN DOC (0-design-*.md) consolidating all design work
7. CREATE PRD (1-prd-*.md)
```

---

## Design Doc Output (Phase 0 Deliverable)

**After design audit passes, create consolidated design doc.**

| Field | Value |
|-------|-------|
| **Location** | `docs/projects/{project-name}/0-design-{feature}.md` |
| **Purpose** | Consolidates all design work into single reference |
| **Created** | After design audit, before PRD |

### Design Doc Template

```markdown
# Design: {Feature Name}

## 1. Overview
Problem statement, solution summary

## 2. Architecture
Layer diagram, component relationships

## 3. Step/Workflow Summary
Table of all steps with tools, gates, gate modes

## 4. Step Template Used
Reference to 7-section template

## 5. Design Decisions Enforced
Which DDs apply to which steps

## 6. Data Contracts
Key input/output schemas between steps

## 7. Design Artifacts
Links to step files, architecture docs, skill files

## 8. Design Audit Results
DD coverage, architecture alignment, contract validation

## 9. Design Decisions Made
Key choices with rationale

## 10. Open Questions (Resolved)
Questions that came up, how they were resolved
```

### Checklist Before PRD

| Check | Required |
|-------|----------|
| Design audit passed | ✅ |
| Design doc created | ✅ |
| All step files complete | ✅ |
| Architecture doc updated | ✅ |

---

## Design Phase Quality Gates

Design phase has TWO levels of quality gates:

```
┌─────────────────────────────────────────────────────────────────────┐
│                 DESIGN PHASE QUALITY GATES                           │
└─────────────────────────────────────────────────────────────────────┘

  Design Step 1
        │
        ▼
  QG: Step 1 Complete? ──► FAIL ──► Fix step, re-check
        │
        ▼ PASS
  Design Step 2
        │
        ▼
  QG: Step 2 Complete? ──► FAIL ──► Fix step, re-check
        │
        ▼ PASS
       ...
        │
        ▼
  Design Step N
        │
        ▼
  QG: Step N Complete? ──► FAIL ──► Fix step, re-check
        │
        ▼ PASS
  ═══════════════════════════════════════════════════
  FINAL AUDIT (cross-step validation)
        │
        ▼
  QG: Design Audit ──► FAIL ──► Fix gaps, re-audit
        │
        ▼ PASS
  PROCEED TO PRD
```

---

### Gate 1: Per-Step Design Gate

**Run after designing each step.**

| Field | Value |
|-------|-------|
| **Gate** | `qg_step_design_complete` |
| **Trigger** | After each step is documented |
| **Pass Criteria** | All 7 sections present and complete |

**Checklist (must ALL be present):**

| Section | Required Content |
|---------|------------------|
| A. Identity & Flow | Step name, dependencies, input, output |
| B. Persona Map | User/AI/Tool actions defined |
| C. Skill Instruction | PRE-CHECK, ACTION, VALIDATE, RETRY |
| D. Tools | Operation tool, quality gate, gate mode |
| E. State Management | State saved, who saves, when, schema |
| F. Enforcement | Rules that apply, validation checks, gate enforcement |
| G. Error Handling | Failure behavior, error templates |
| H. Data Contracts | (Tool steps only) Input/output contract with examples |

**Fail Behavior:**
```
"Step [N] design incomplete.

Missing sections:
- [list missing sections]

Missing fields in [section]:
- [list missing fields]

Complete these before proceeding to Step [N+1]."
```

---

### Gate 2: Final Design Audit

**Run after ALL steps designed, BEFORE creating PRD.**

| Field | Value |
|-------|-------|
| **Gate** | `qg_design_audit` |
| **Trigger** | After last step designed |
| **Pass Criteria** | All 4 cross-step audits pass |

### Audit Checklist

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DESIGN AUDIT CHECKLIST                            │
└─────────────────────────────────────────────────────────────────────┘

1. DD COVERAGE AUDIT
   - List all Design Decisions (DD-01, DD-02, ...)
   - For each DD: Which step enforces it?
   - GAP if DD not in any step's Section F

2. ARCHITECTURE ALIGNMENT
   - Compare design layers to meta-architecture
   - Verify Human vs Machine boundaries
   - GAP if layer missing or misaligned

3. TOOL CONTRACT VALIDATION
   - For each tool step: Does step input match tool signature?
   - For each tool step: Does step output match tool return?
   - GAP if schema mismatch

4. DATA CONTRACT CHAIN
   - Step N output → Step N+1 input: schemas match?
   - Section H exists for each tool step?
   - GAP if contract missing or format wrong
```

### Validation Sources

| Source | Purpose |
|--------|---------|
| DEFECT_LOG.md | Extract all DDs + known issues |
| Meta-architecture doc | Validate layer alignment |
| Tool source files (tools/*.py) | Extract actual signatures |
| Step files (step-*.md) | Compare against sources |

### Audit Output Format

```markdown
## DD Coverage
| DD | Description | Enforced In | Status |
|----|-------------|-------------|--------|
| DD-01 | ... | Step 2 | ✅ |
| DD-19 | ... | *missing* | ❌ GAP |

## Architecture Alignment
| Layer | Our Implementation | Status |
|-------|-------------------|--------|
| Skill | Step references | ✅ |
| Enforcement | Quality gates | ✅ |

## Tool Contracts
| Step | Tool | Input Match | Output Match | Status |
|------|------|-------------|--------------|--------|
| 4 | Tool 1 | ⚠️ MISMATCH | ✅ | FIX |

## Gaps Found
1. [DD-XX] not enforced → Add to Step Y Section F
2. [Step N] input mismatch → Update Section H
```

### Fix Protocol

```
For each GAP found:
1. FIX the step file (add DD to Section F, fix Section H)
2. RE-VALIDATE after fix
3. PROCEED to PRD only when all checks pass
```

### When to Skip

Only skip audit if:
- Trivial design (<3 steps)
- No tool chain (pure AI processing)
- Prototype/throwaway work

Otherwise: **AUDIT IS MANDATORY**

---

## Step Template (Generalized)

Use this template for each step in any vertical. **All fields required unless marked optional.**

### A. Identity & Flow

| Field | Description |
|-------|-------------|
| **Step** | Step number and name |
| **Dependencies** | What prior steps must be complete |
| **Input** | What data comes in (with schema) |
| **Output** | What data goes out (with schema) |

### B. Persona Map (Who Does What)

| Field | Description |
|-------|-------------|
| **User Actions** | What human does in this step (or "None") |
| **AI Actions** | What AI does (prepare, extract, validate, retry) |
| **Tool Actions** | What MCP tools do (validate, execute, save state) |

### C. Skill Instruction

| Field | Description |
|-------|-------------|
| **PRE-CHECK** | What must exist before starting (from previous step) |
| **ACTION** | Sequence of actions (ASK, CALL, PREPARE, etc.) |
| **VALIDATE** | Which qg_* to call and when (pre/post) |
| **RETRY** | Max attempts, escalation path |

### D. Tools

| Field | Description |
|-------|-------------|
| **Operation Tool** | Tool that does the work (or "-" if none) |
| **Quality Gate** | qg_* tool that validates (always required) |
| **Gate Mode** | PRE-only, POST-only, or PRE+POST |

### E. State Management

| Field | Description |
|-------|-------------|
| **State Saved** | What data persists after this step |
| **Who Saves** | Quality gate (Steps 1-3) or Operation tool (Steps 4+) |
| **When Saved** | On gate PASS or operation SUCCESS |
| **State Schema** | JSON structure of saved state |

### F. Enforcement

| Field | Description |
|-------|-------------|
| **Rules That Apply** | Which design decisions/rules govern this step |
| **Validation Checks** | What qg_* tool validates (table format) |
| **Gate Enforcement** | BLOCKED: Cannot proceed to Step N+1 until X |

### G. Error Handling

| Field | Description |
|-------|-------------|
| **Failure Behavior** | What happens on validation failure |
| **Error Message Templates** | What to show on failure (with examples) |
| **Known Defects** | Which defects relate to this step (optional) |

**Note:** Two tool types in one MCP server:
- **Operation tools** (existing): Do the work (generate_tests, discover_elements, etc.)
- **Quality gate tools** (qg_*): Validate only (qg_preflight, qg_user_input, etc.)

**Naming Convention:**
- Operations: Keep existing names
- Gates: `qg_` prefix (e.g., qg_preflight, qg_test_scenarios)

**Future:** SDK with Python code enforcement for commercial deployments.

---

## Key Principles

1. **Explicit gate enforcement** - Every step must state: "BLOCKED: Cannot proceed until X"
2. **No AI "IF" decisions** - User answers all conditional questions explicitly
3. **Always include examples** - Even trivial prompts should have examples
4. **Generic options** - Don't assume domain-specific values; let user specify
5. **One topic at a time** - When asking user, ask one question, wait for answer

---

## Four-Layer Architecture

Every vertical should implement four layers:

```
┌─────────────────────────────────────────────────────────────────────┐
│ SKILL (guidance-layer)                                               │
│ - Guides AI through workflow                                         │
│ - Tells AI what step, what input, how to handle failures            │
│ - Orchestration layer                                                │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ QUALITY GATES (qg_*)                                                 │
│ - Validates input before operation                                   │
│ - Validates output after operation                                   │
│ - NEVER does work, only validates                                    │
│ - Enforcement layer                                                  │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ OPERATION TOOLS                                                      │
│ - Does the actual work                                               │
│ - Existing tools, keep names unchanged                               │
│ - Execution layer                                                    │
└─────────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────────┐
│ STATE MANAGER                                                        │
│ - Persists workflow state after each step                           │
│ - Called internally by gates/operations (NOT by AI)                 │
│ - Enables resume, audit trail, debugging                            │
│ - Persistence layer                                                  │
└─────────────────────────────────────────────────────────────────────┘
```

**Flow per step:**
```
Skill guides AI → AI prepares → qg_* validates → Operation executes → State saved → Skill guides next
```

**State Save Rules:**
- Steps without operation tool: Quality gate saves state on PASS
- Steps with operation tool: Operation saves state on SUCCESS
- AI NEVER calls state_manager directly (can't be skipped)

---

## Tool Organization

One MCP server with tools + state:

```
{vertical}-server/
├── tools/
│   ├── operations/          ← Do the work (keep existing names)
│   │   ├── tool_1.py
│   │   ├── tool_2.py
│   │   └── ...
│   │
│   └── gates/               ← Validate only (qg_* prefix)
│       ├── qg_preflight.py
│       ├── qg_step_1.py
│       └── ...
│
├── state/                   ← Workflow state persistence
│   └── workflow_state.json  ← Current workflow state
│
└── utils/
    └── state_manager.py     ← Save/load state logic
```

**Rules:**
- Operations keep existing names (don't rename working tools)
- Gates use `qg_` prefix for clarity
- Both in same server (not separate servers - avoid over-engineering)
- State manager is internal utility, not exposed as MCP tool

---

## State Manager

### Purpose
Persist workflow state so that:
- Workflow can resume after interruption
- Audit trail exists for debugging
- Data integrity is enforced (can't proceed without valid prior state)

### Implementation

```python
# utils/state_manager.py

class StateManager:
    def __init__(self, state_file: str = "state/workflow_state.json"):
        self.state_file = state_file

    def save(self, step: int, data: dict) -> None:
        """Save state after step completion. Called by gates/operations."""
        state = self.load() or {"workflow_id": str(uuid4()), "steps": {}}
        state["steps"][str(step)] = {
            "status": "complete",
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        self._write(state)

    def load(self) -> dict | None:
        """Load current workflow state."""
        if not exists(self.state_file):
            return None
        return self._read()

    def get_step(self, step: int) -> dict | None:
        """Get data from specific step."""
        state = self.load()
        if not state:
            return None
        return state.get("steps", {}).get(str(step), {}).get("data")

    def is_step_complete(self, step: int) -> bool:
        """Check if step is complete (for PRE-CHECK)."""
        step_data = self.get_step(step)
        return step_data is not None
```

### Usage Pattern (Generic)

**Quality gate (steps without operation tool):**
```python
def qg_step_N(input_field_1: str, input_field_2: str):
    # Validate inputs
    if not valid(input_field_1, input_field_2):
        return {"status": "fail", "error": "..."}

    # Save state on PASS
    state_manager.save(step=N, data={
        "field_1": input_field_1,
        "field_2": input_field_2
    })

    return {"status": "pass"}
```

**Operation tool (steps with operation):**
```python
def operation_tool(input_param: str, context: dict):
    # Do the work
    result = do_operation(input_param, context)

    # Save state on SUCCESS
    state_manager.save(step=N, data={
        "input": input_param,
        "output": result
    })

    return {"status": "success", "result": result}
```

### State Schema (Generic)

```json
{
  "workflow_id": "uuid-here",
  "steps": {
    "N": {
      "status": "complete",
      "timestamp": "ISO-8601",
      "data": { "...step-specific data..." }
    }
  }
}
```

---

### QA Vertical Example (Illustration)

The following shows how the QA vertical implements these patterns:

**Quality gate example (Step 1 - Pre-flight):**
```python
def qg_preflight(credential_strategy: str, test_data_location: str):
    # Validate
    if credential_strategy not in ["static", "dynamic", "self-contained", "none"]:
        return {"status": "fail", "error": "Invalid credential_strategy"}

    # Save state on PASS
    state_manager.save(step=1, data={
        "credential_strategy": credential_strategy,
        "test_data_location": test_data_location
    })

    return {"status": "pass"}
```

**Operation tool example (Step 6 - Generate POM):**
```python
def generate_page_object(page_name: str, elements: list):
    # Do the work
    code = create_pom(page_name, elements)

    # Save state on SUCCESS
    state_manager.save(step=6, data={
        "page_name": page_name,
        "pom_code": code
    })

    return {"status": "success", "code": code}
```

**QA State Schema example:**
```json
{
  "workflow_id": "uuid-here",
  "steps": {
    "1": {
      "status": "complete",
      "timestamp": "2025-12-20T10:30:00",
      "data": {
        "credential_strategy": "static",
        "test_data_location": "shared"
      }
    },
    "2": {
      "status": "complete",
      "timestamp": "2025-12-20T10:31:00",
      "data": {
        "persona": "registered user",
        "URL": "http://automationpractice.pl/...",
        "role_name": "RegisteredUser",
        "domain": "auth"
      }
    }
  }
}
```

---

## Universal Retry Policy

Apply same policy to all steps:

```
┌─────────────────────────────────────────────────────────────────────┐
│                    UNIVERSAL RETRY POLICY                            │
└─────────────────────────────────────────────────────────────────────┘

  Attempt 1 → FAIL
      │
      ▼
  Attempt 2 → FAIL
      │
      ▼
  Attempt 3 → FAIL
      │
      ▼
  STOP → REPORT → USER DECIDES

  Resolution options (per step):
  1. [Step-specific fix] - Go back to relevant step
  2. Abort workflow - Stop and log issue internally

  NEVER: "Proceed with incomplete" - Gates block bad data, always
```

**Key rules:**
- 3 attempts max before asking user
- Tool rejection = AI's problem (retry), not user's
- User only involved after retries exhausted
- No "proceed anyway" option - incomplete data never propagates

---

## Lessons Learned (Apply to All Verticals)

| Lesson | Description |
|--------|-------------|
| **Skill is critical** | Without orchestration layer, tools alone aren't enough |
| **qg_* only validates** | Never does work - strict separation of concerns |
| **Compare IS vs SHOULD** | Check implementation against design before locking step |
| **Keep existing names** | Don't rename working operation tools when adding gates |
| **One server, two types** | Avoid over-engineering with multiple servers |
| **No proceed incomplete** | Quality gates block bad data, always |
| **Performance awareness** | Fetch/process only what's needed (token + speed optimization) |
| **User answers conditionals** | AI never makes IF decisions - ask user explicitly |
| **Generic options** | Don't hardcode domain values - different sites/contexts vary |
| **3 retry universal** | Same policy all steps for consistency |
| **Pre-implementation check** | Before implementing gate, read step skill + FRAMEWORK.md + tool code + generator for inconsistencies |
| **IC documentation** | Every step needs Implementation Clarifications section documenting decisions made during gate implementation |
| **Proactive coverage** | Before writing tests, run coverage analysis to identify gaps in TDD approach |

---

## Pre-Implementation Consistency Check

**MANDATORY before implementing any quality gate.**

### Sources to Read

| Source | Purpose |
|--------|---------|
| Step skill reference (step-XX.md) | Design intent, validation rules |
| FRAMEWORK.md relevant section | Authoritative architecture patterns |
| Tool source code (tool_XX_*.py) | Actual implementation, input/output |
| Generator source code (*_generator.py) | What gets generated, edge cases |

### Consistency Check Process

```
1. READ all 4 sources
2. COMPARE step skill vs tool implementation
   - Input/output schema matches?
   - Required vs optional fields?
   - Edge cases documented?
3. COMPARE step skill vs FRAMEWORK.md
   - Numbering consistent?
   - Rules referenced correctly?
4. COMPARE generator vs DD-25
   - Any skeleton/placeholder code generated?
   - Gate must catch these patterns
5. DOCUMENT inconsistencies
6. PROPOSE ICs (Implementation Clarifications)
7. USER approves before implementation
```

### Common Inconsistencies

| Type | Example | Resolution |
|------|---------|------------|
| **Schema mismatch** | Skill says required, tool treats as optional | Add IC clarifying actual behavior |
| **Skeleton fallback** | Generator produces `pass`/`TODO` on edge cases | Gate must detect and fail |
| **Numbering** | Section 8.x vs Section 9.x (different workflow versions) | Document which version applies |
| **Missing patterns** | Decorator required but not in generator | Gate validates, AI fixes |

---

## Implementation Clarifications (IC) Pattern

**Every step reference must have Section I: Implementation Clarifications.**

### Purpose

- Document decisions made during gate implementation
- Resolve ambiguities in design docs
- Record what gate enforces vs what it doesn't
- Provide task/date reference for audit trail

### IC Format

```markdown
## I. Implementation Clarifications (Gate-Specific)

These clarifications document gate enforcement decisions. If bugs occur, check these for root cause.

| ID | Decision | Rationale | Enforced By |
|----|----------|-----------|-------------|
| IC-XX-01 | [Decision statement] | [Why this choice] | `validate_pre()` or `validate_post()` or N/A |
| IC-XX-02 | ... | ... | ... |

**Date Added:** YYYY-MM-DD
**Task Reference:** Task X.0 (gate name)
```

### IC Naming Convention

- `IC-XX-YY` where XX = step number, YY = sequential within step
- Example: IC-08-01 through IC-08-06 for Step 8

### What Requires an IC

| Scenario | IC Required |
|----------|-------------|
| Skill says required, tool treats as optional | Yes |
| Framework pattern not enforced by gate | Yes |
| Edge case behavior decided | Yes |
| Pattern acceptable per framework examples | Yes |
| Obvious validation (field present, not empty) | No |

### Test Complexity Allowances

Gates should enforce minimum quality, not restrict test complexity:

| Pattern | Allowed | Gate Enforces |
|---------|---------|---------------|
| Single role, single method call | ✅ Default | At least 1 role call |
| Single role, multiple method calls | ✅ Complex workflows | At least 1 role call |
| Multiple roles in one test | ✅ Multi-user scenarios | At least 1 role call per role used |

**Rationale:** Complex e2e scenarios (admin + user, buyer + seller) are legitimate test patterns.

---

## Step Definitions (Generalized)

### Step 1: Pre-flight Configuration

| Aspect | Details |
|--------|---------|
| **Step** | 1 - Pre-flight Configuration |
| **MCP Tool** | `validate_preflight_config` |
| **Input** | None (first step) |
| **Output** | Configuration choices that affect subsequent steps |
| **Dependencies** | None |
| **Who Executes** | AI asks → User answers → Tool validates |
| **Rules That Apply** | Vertical-specific configuration rules |

#### Quality Gate

| Check | Rule |
|-------|------|
| All configuration questions answered | Each must have valid answer |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 2 until all answers provided** |

#### Failure Behavior

| Issue | Behavior |
|-------|----------|
| User skips question | RE-ASK with clarification |
| Invalid answer | RE-ASK with valid options |

#### Error Message Template Pattern

```
"[Question about configuration]
1. Option A - Description
2. Option B - Description
3. Option C - Description
4. None needed - This doesn't apply"
```

---

### Step 2: User Input

| Aspect | Details |
|--------|---------|
| **Step** | 2 - User Input |
| **MCP Tool** | `validate_user_input` |
| **Input** | User's natural language requirement |
| **Output** | Validated core inputs (varies by vertical) |
| **Dependencies** | Step 1 complete |
| **Who Executes** | User provides → AI extracts → Tool validates |

#### Quality Gate

| Check | Rule |
|-------|------|
| Required inputs present | All mandatory fields provided |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step 3 until all required inputs provided** |

#### Failure Behavior

| Missing | Behavior |
|---------|----------|
| Required input | ASK USER with example |

#### Error Message Template Pattern

```
"[What is missing]
Format: [Expected format]
Example: '[Concrete example]'"
```

---

### Steps 3-N: Tool Steps

*Template for tool-based steps - document as each vertical defines them.*

| Aspect | Details |
|--------|---------|
| **Step** | N - Tool Name |
| **MCP Tool** | `tool_name` (quality gate for this step) |
| **Input** | Output from Step N-1 + metadata context |
| **Output** | Tool result + updated metadata |
| **Dependencies** | Step N-1 complete |
| **Who Executes** | AI prepares → MCP Tool validates + executes |
| **Rules That Apply** | Tool-specific design decisions |

#### Quality Gate

| Check | Rule |
|-------|------|
| Input valid | Matches expected schema from previous step |
| Tool success | Tool returns success status |
| Output valid | Contains required fields for next step |
| **Gate Enforcement** | **BLOCKED: Cannot proceed to Step N+1 until all checks pass** |

---

## Tool Failure Handling Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    TOOL FAILURE HANDLING                         │
└─────────────────────────────────────────────────────────────────┘

  AI calls Tool
      │
      ▼
┌─────────────┐
│ Tool        │
│ validates   │
│ input       │
└─────────────┘
      │
      ├── PASS ──► Tool executes ──► Success ──► Next step
      │
      └── FAIL ──► Tool returns error:
                   {
                     "status": "error",
                     "error_type": "[what failed]",
                     "message": "[description]",
                     "fix_hint": "[how to fix]",
                     "example": "[correct format]"
                   }
                         │
                         ▼
                   AI MUST:
                   1. STOP execution
                   2. REPORT to user (error + hint)
                   3. ASK user for correction
                   4. WAIT for response
                   5. RETRY with corrected input
                         │
                         ▼
                   Loop until SUCCESS or USER CANCELS
```

**Key Rule:** AI does NOT guess, assume, or auto-fix validation errors.

---

## Documentation Locations

After locking down each step:

| Location | Purpose | Content |
|----------|---------|---------|
| Vertical-specific doc | Full detail | Complete step definition |
| This skill | Generalized | Template + principles |
| Quick reference | Summary | One-liner per step |

---

*Living document - update as patterns emerge across verticals.*
