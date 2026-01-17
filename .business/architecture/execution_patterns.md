# Isagawa Execution Patterns

## Overview

Isagawa enforces execution through defense-in-depth architecture. Multiple independent layers ensure AI executes work correctly.

> **Platform Definition:** The Isagawa Platform is an AI Management Layer built on six components:
>
> **Core Defense-in-Depth (4 Layers):**
> 1. **Protocols** - Define the correct way AI must perform work
> 2. **Smart Gates** - Validate execution AND teach fixes when violations detected
> 3. **Hooks** - Monitor continuously and auto-intervene on deviations
> 4. **State Checkpointing** - Enable recovery and resume from known good states
>
> **Supporting Infrastructure (2 Components):**
> 5. **Audit System** - Immutable logging of all actions for compliance and debugging
> 6. **HITL System** - Human-in-the-Loop confirmations for critical decisions

**Defense-in-Depth Philosophy:** Multiple independent layers, each catching different failure modes. If one layer fails, others provide redundancy.

---

## Component Selection Guide

**IMPORTANT FOR AI:** When implementing Isagawa patterns for a new project, select components based on project requirements:

### Universal Components (All Projects)

These components should be used in **every** Isagawa-based project:

1. ✅ **Protocols** (Layer 1) - REQUIRED
   - Every project needs workflow definitions
   - Minimal: YAML file defining steps

2. ✅ **Smart Gates** (Layer 2) - REQUIRED
   - Every project needs validation checkpoints
   - Minimal: Pre-flight and completion gates

3. ✅ **State Checkpointing** (Layer 4) - REQUIRED
   - Every project needs pause/resume capability
   - Minimal: JSON state files per workflow

### Optional Components (Project-Dependent)

Select these based on project complexity and requirements:

4. ⚠️ **Hooks** (Layer 3) - RECOMMENDED (skip only for simple projects)
   - Use when: Continuous monitoring needed
   - Skip when: Simple single-step workflows (<3 steps)
   - Example skip: Single API call with validation

5. ⚠️ **Audit System** - RECOMMENDED (skip only for non-regulated domains)
   - Use when: Compliance required, debugging complex workflows
   - Skip when: Personal projects, no audit requirements
   - Example skip: Personal task automation

6. ⚠️ **HITL System** - OPTIONAL (use when human approval needed)
   - Use when: Critical decisions, high-risk actions, user preferences
   - Skip when: Fully autonomous workflows, low-risk operations
   - Example skip: Read-only data analysis

### Component Selection Examples

**Example 1: Enterprise Compliance Workflow**
```
Use: ✅ Protocols, ✅ Smart Gates, ✅ Hooks, ✅ State, ✅ Audit, ✅ HITL
Why: High-risk, regulated, needs full defense-in-depth + compliance trail
```

**Example 2: Personal Task Automation**
```
Use: ✅ Protocols, ✅ Smart Gates, ✅ State
Skip: Hooks (simple workflow), Audit (no compliance), HITL (autonomous)
Why: Low-risk, non-regulated, simple workflow
```

**Example 3: Multi-Agent Research System**
```
Use: ✅ Protocols, ✅ Smart Gates, ✅ Hooks, ✅ State, ✅ Audit
Skip: HITL (autonomous research)
Why: Complex workflow needs monitoring, but fully autonomous
```

**Example 4: Code Review Automation**
```
Use: ✅ Protocols, ✅ Smart Gates, ✅ Hooks, ✅ State, ⚠️ HITL (approval only)
Skip: Audit (unless required by org policy)
Why: Needs monitoring + human approval, audit optional
```

### Domain-Specific Frameworks

**QA Test Automation Framework** (Selenium + Pytest + 4-layer architecture):
- **Only for:** QA/testing projects
- **Not needed for:** Intel, Consumer, Agent Management, or other verticals
- **Components:** Page Objects, Tasks, Roles, Tests
- **Integration:** Uses all 6 Isagawa platform components

**Other verticals** (Intel, Consumer, Agent Management):
- Use platform components (1-6) as selected above
- Do NOT include QA test automation framework

---

## Defense-in-Depth: The Four Layers

### Layer 1: Protocols (Preventive)

**What:** Structured definitions of correct execution workflows.

**Form:** YAML files, markdown documents, skill references.

**Purpose:** Teach AI the correct behavior BEFORE execution begins.

**Coverage:** Initial guidance, reduces likelihood of errors.

**Example:**
```yaml
# protocol: intel_scan.yaml
workflow:
  - step: "Scope Validation"
    required_inputs: ["products", "categories"]
    actions: ["Parse user input", "Confirm scope"]
  - step: "Category Execution"
    required_inputs: ["validated_scope"]
    actions: ["Execute searches", "Cover all products"]
```

**Failure Mode Caught:** Unclear instructions, ambiguous requirements.

**What Happens if Bypassed:** Layers 2-4 catch violations.

---

### Layer 2: Smart Gates (Detective + Corrective)

**What:** Validation checkpoints that enforce protocol compliance AND provide fixes.

**Form:** MCP tools invoked at critical workflow points.

**Purpose:** Validate execution against protocol rules. When violations detected, provide explicit fixes (not just error messages).

**Coverage:** Discrete checkpoints (pre-flight, mid-execution, post-execution).

**Two Functions:**
1. **Validate:** Check if protocol followed
2. **Teach:** Provide missing data or fix guidance when validation fails

**Example:**
```python
# Smart Gate: Coverage validation
if categories_scanned < 8:
    missing = [cat for cat in ALL_CATEGORIES if cat not in scanned]
    return {
        "status": "FAILED",
        "missing_work": missing,  # <-- TEACHING: What's missing
        "fix": f"Execute searches for: {', '.join(missing)}",  # <-- TEACHING: How to fix
        "block_execution": True
    }
```

**Failure Mode Caught:** Protocol violations, incomplete work, incorrect output format.

**What Happens if Bypassed:** Layer 3 (Hooks) catches gate bypass.

---

### Layer 3: Hooks (Continuous Detective)

**What:** Event-driven monitors that watch EVERY action in real-time.

**Form:** JavaScript hooks triggered on PreToolUse, PostToolUse, PreSave, PostAgentEnd, etc.

**Purpose:** Continuous surveillance. Catch violations that slip through Protocols + Gates.

**Coverage:** Every tool call, every file save, every subagent execution.

**Intervention Types:**
- **Alert:** Warn user of potential issue
- **Block:** Prevent action (e.g., block file save if format invalid)
- **Auto-Fix:** Correct minor issues automatically

**Example:**
```javascript
// Hook: PostToolUse - Track search coverage
if (toolName === "WebSearch") {
  coverageTracker[category] = true;

  if (stepCount > 50 && Object.keys(coverageTracker).length < 8) {
    return {
      alert: true,
      message: "Coverage gap: Only 6/8 categories scanned"
    };
  }
}
```

**Failure Mode Caught:** Gate bypasses, subagent deviations, format violations at save time.

**What Happens if Bypassed:** Layer 4 (Checkpointing) allows rollback.

---

### Layer 4: State Checkpointing (Recovery)

**What:** Save workflow state at each gate. Enable resume from known good state.

**Form:** State snapshots saved to disk/database after each gate passes.

**Purpose:** Enable recovery if workflow fails. Resume from last checkpoint instead of restarting.

**Coverage:** Persistent state across sessions, recoverable after crashes/errors.

**Checkpoint Structure:**
```json
{
  "checkpoint_id": "intel_scan_step_2",
  "timestamp": "2026-01-16T10:30:00Z",
  "workflow": "intel_scan",
  "gate_passed": "eg_coverage",
  "state": {
    "categories_scanned": [1,2,3,4,5,6,7,8],
    "products_scanned": 5,
    "search_results": {...}
  },
  "next_step": "generate_report",
  "audit_trail": [...]
}
```

**Recovery Scenarios:**
- Workflow interrupted → Resume from last checkpoint
- Error occurs → Rollback to checkpoint, retry
- User stops work → Resume next session from checkpoint

**Failure Mode Caught:** Workflow interruptions, crashes, need to resume work.

**What Happens if Missing:** Must restart entire workflow from beginning.

---

## Supporting Infrastructure

The four defense-in-depth layers are supported by two additional components that provide observability and human oversight.

### Component 5: Audit System (Observability)

**What:** Immutable logging of all tool calls, decisions, and state changes.

**Form:** JSON log files written after each significant action (gate pass, tool invocation, state change).

**Purpose:** Provide complete audit trail for debugging, compliance, and pattern analysis.

**Coverage:** Every tool call, every gate validation, every state checkpoint.

**Log Structure:**
```json
{
  "timestamp": "2026-01-16T10:30:00Z",
  "workflow_id": "intel_scan_20260116",
  "type": "mcp_tool",
  "tool_name": "qg_coverage",
  "args": {"categories_scanned": 8},
  "result": {"status": "PASS"},
  "gate_status": "PASS"
}
```

**Use Cases:**
- **Debugging:** Replay workflow execution to identify failures
- **Compliance:** EU AI Act requires 3-year retention of AI decisions
- **Analytics:** Pattern detection (which steps fail most often?)
- **Forensics:** Investigate incidents, trace decision path

**Integration with Defense Layers:**
- **Layer 2 (Gates):** Log gate results (pass/fail, teaching data)
- **Layer 3 (Hooks):** PostToolUse hook writes audit entries
- **Layer 4 (Checkpoints):** Checkpoint includes audit trail reference

**Selection Guidance:**
- ✅ Use when: Compliance required, complex workflows, regulated industries
- ❌ Skip when: Personal projects, no audit requirements, simple automation

---

### Component 6: HITL System (Human Oversight)

**What:** Human-in-the-Loop confirmation for critical decisions or high-risk actions.

**Form:** Interactive prompts requesting user approval before proceeding.

**Purpose:** Enable human oversight at critical junctures. AI proposes, human approves.

**Coverage:** Configurable checkpoints where human judgment required.

**Confirmation Structure:**
```json
{
  "confirmation_type": "config_change",
  "context": {
    "file": "environment_config.json",
    "action": "add_environment",
    "proposed_change": {...}
  },
  "options": [
    {"id": "approve", "label": "Yes, proceed"},
    {"id": "modify", "label": "Let me change it"},
    {"id": "reject", "label": "Cancel"}
  ]
}
```

**Use Cases:**
- **High-Risk Actions:** Delete data, deploy to production, financial transactions
- **Ambiguous Requirements:** Multiple valid interpretations, need user preference
- **Quality Assurance:** User reviews AI-generated code/content before saving
- **Compliance:** Human approval required by regulation (EU AI Act high-risk systems)

**HITL Trigger Points:**
- **After Gate Failure:** Gate detects issue → AI proposes fix → HITL confirms
- **Before Irreversible Action:** Delete, deploy, commit → HITL confirms first
- **On Ambiguity:** Multiple valid approaches → AI presents options → HITL selects

**Integration with Defense Layers:**
- **Layer 1 (Protocols):** Protocol defines HITL trigger points
- **Layer 2 (Gates):** Gates can return "NEEDS_CONFIRMATION" status
- **Layer 3 (Hooks):** Hooks can trigger HITL on detected anomalies
- **Layer 4 (Checkpoints):** Checkpoint saved after HITL approval

**Selection Guidance:**
- ✅ Use when: High-risk actions, critical decisions, user preferences matter
- ❌ Skip when: Fully autonomous workflows, low-risk operations, read-only tasks

---

## How the Layers Work Together

**Scenario 1: Normal Execution (All Layers Pass)**

```
Layer 1 (Protocol): AI reads workflow definition
                   ↓
Layer 2 (Gate):    eg_preflight validates scope → PASS
                   ↓
Layer 4 (Checkpoint): Save state checkpoint_1
                   ↓
Layer 3 (Hook):    PostToolUse monitors searches → All good
                   ↓
Layer 2 (Gate):    eg_coverage validates completion → PASS
                   ↓
Layer 4 (Checkpoint): Save state checkpoint_2
                   ↓
Layer 2 (Gate):    eg_format validates report → PASS
                   ↓
Layer 3 (Hook):    PreSave validates structure → Allow save
                   ↓
                   SUCCESS ✅
```

---

**Scenario 2: Protocol Ignored (Layer 2 Catches)**

```
Layer 1 (Protocol): AI reads workflow but misunderstands Category 3
                   ↓
Layer 2 (Gate):    eg_coverage validates completion
                   → FAIL: "Missing Category 3: Enterprise Adoption"
                   → TEACH: "Execute WebSearch with query: 'enterprise adoption agentic AI 2026'"
                   ↓
                   AI executes missing search
                   ↓
Layer 2 (Gate):    eg_coverage retry → PASS
                   ↓
                   CONTINUE ✅
```

---

**Scenario 3: Gate Bypassed (Layer 3 Catches)**

```
Layer 1 (Protocol): AI reads workflow
                   ↓
Layer 2 (Gate):    Gate never invoked (bypassed!)
                   ↓
Layer 3 (Hook):    PostToolUse monitors searches
                   → Detects only 7/8 categories scanned
                   → ALERT: "Coverage gap detected"
                   ↓
                   User notified, fixes manually
                   ↓
Layer 3 (Hook):    PreSave validates before save
                   → Detects missing sections
                   → BLOCK SAVE
                   ↓
                   AI fixes report structure
                   ↓
Layer 3 (Hook):    PreSave retry → PASS
                   ↓
                   CONTINUE ✅
```

---

**Scenario 4: Workflow Interrupted (Layer 4 Recovers)**

```
Layer 1-3:         Normal execution through Step 2
                   ↓
Layer 4 (Checkpoint): State saved at checkpoint_2
                   ↓
                   [INTERRUPTION: User stops, session ends]
                   ↓
                   [NEW SESSION]
                   ↓
Layer 4 (Recovery): Load checkpoint_2
                   → Restore: categories_scanned, search_results
                   → Resume from: "generate_report"
                   ↓
Layer 2 (Gate):    eg_format validates report → PASS
                   ↓
                   CONTINUE ✅ (No need to redo 8 searches)
```

---

## Redundancy Matrix

### Defense Layers (Primary Protection)

| Failure Mode | Layer 1<br/>Protocol | Layer 2<br/>Gates | Layer 3<br/>Hooks | Layer 4<br/>Checkpoints | Audit<br/>System | HITL<br/>System |
|--------------|---------|---------|---------|---------|---------|---------|
| Unclear instructions | 🟢 Catch | - | - | - | 📝 Log | - |
| Protocol violations | ⚠️ Miss | 🟢 Catch | - | - | 📝 Log | 🔍 Review |
| Incomplete work | ⚠️ Miss | 🟢 Catch | 🟡 Alert | - | 📝 Log | 🔍 Review |
| Gate bypassed | ❌ Miss | ❌ Miss | 🟢 Catch | - | 📝 Log | - |
| Format violations | ⚠️ Miss | 🟢 Catch | 🟢 Block | - | 📝 Log | - |
| Workflow interrupted | ❌ N/A | ❌ N/A | ❌ N/A | 🟢 Recover | 📝 Log | - |
| High-risk action | ⚠️ Warn | 🟡 Validate | 🟡 Alert | - | 📝 Log | 🟢 Confirm |
| Ambiguous requirement | ⚠️ Miss | ❌ Miss | ❌ Miss | - | 📝 Log | 🟢 Clarify |

**Key:**
- 🟢 Primary defense (catches reliably)
- 🟡 Backup defense (provides warning)
- ⚠️ May catch (depends on AI interpretation)
- ❌ Cannot catch (not designed for this)
- 📝 Observability (logs for post-incident analysis)
- 🔍 Review assist (human can review logged data)

**Coverage:** Multiple layers ensure every failure mode has at least one defense (usually two or more). Audit and HITL are supporting components that enhance (not replace) the 4 defense layers.

**Role of Supporting Components:**
- **Audit System:** Provides observability for ALL failure modes. Enables post-incident forensics, compliance reporting, and pattern detection.
- **HITL System:** Enables human oversight for failure modes requiring judgment (high-risk actions, ambiguous requirements). Audit logs human decisions.

---

## Execution Topology Patterns

### Pattern A: Assembly Line (Sequential Pipeline)

**Used by:** QA Execution Engine (10-step workflow)

**Workflow Topology:**
- Steps are SEQUENTIAL and DEPENDENT
- Step N output is input to Step N+1
- Metadata flows through the pipeline
- Cannot parallelize

**Defense-in-Depth Application:**

| Component | Implementation |
|-------|----------------|
| **Layer 1 (Protocol)** | Skill defines each step: inputs, actions, outputs |
| **Layer 2 (Gate)** | Gate after each step validates metadata contract |
| **Layer 3 (Hook)** | PostToolUse monitors tool chain completion |
| **Layer 4 (Checkpoint)** | Save state after each gate passes |
| **Audit System** | PostToolUse hook logs all tool calls, gate results |
| **HITL System** | Optional confirmations for skeleton fixes, data creation |

**Enforcement Mechanism:** Metadata contract. Next step has no input if previous step skipped.

**Skip a step?** Impossible. Next step cannot proceed without required metadata from previous step.

**Example Flow:**
```
Step 1 → Gate validates → Checkpoint saved → Step 2 → Gate validates → Checkpoint saved → ...
```

---

### Pattern B: Inspection Team (Parallel Fan-Out/Fan-In)

**Used by:** Intel Scan (8-category competitive intelligence)

**Workflow Topology:**
- Categories are INDEPENDENT
- No dependencies between searches
- Can run in parallel
- Aggregation happens at the end

**Defense-in-Depth Application:**

| Component | Implementation |
|-------|----------------|
| **Layer 1 (Protocol)** | Protocol defines 8 categories, search requirements per category |
| **Layer 2 (Gate)** | Aggregation gate after all categories validates completeness |
| **Layer 3 (Hook)** | PostToolUse monitors each WebSearch, tracks coverage in real-time |
| **Layer 4 (Checkpoint)** | Save state after each category completes (enables partial resume) |
| **Audit System** | PostToolUse hook logs all WebSearch calls, tracks coverage progress |
| **HITL System** | Optional confirmations for scope validation, report format approval |

**Enforcement Mechanism:** Aggregation requirement. Report cannot generate without all 8 category results.

**Skip an inspector?** Report generation gate fails. Missing input data.

**Example Flow:**
```
Category 1 ──┐
Category 2 ──┤
Category 3 ──┤
   ...       ├──→ Aggregation Gate → Validates all 8 complete → Report Generation
Category 6 ──┤
Category 7 ──┤
Category 8 ──┘
```

**Hook Advantage:** Hooks detect incomplete coverage DURING execution (not just at aggregation gate). Early warning system.

---

## The Isagawa Principle

**Infrastructure that teaches AI how to succeed.**

All Isagawa patterns share this core philosophy:

**Core Defense-in-Depth (4 Layers):**
1. **Protocols teach** the correct way BEFORE execution
2. **Smart Gates validate AND teach** by providing explicit fixes when violations detected
3. **Hooks monitor continuously** and intervene early (not just at checkpoints)
4. **Checkpoints enable recovery** so work isn't lost

**Supporting Infrastructure (2 Components):**
5. **Audit System provides observability** - immutable logs for debugging, compliance, and pattern analysis
6. **HITL System enables oversight** - human judgment for critical decisions and ambiguous requirements

**Not just enforcement. Guided execution with observability and human oversight.**

---

## Pattern Selection Guide

| Workflow Shape | Pattern | Defense-in-Depth Strategy | Primary Enforcement |
|----------------|---------|--------------------------|---------------------|
| **Sequential dependencies** | Assembly Line | Gates after each step + Hooks monitoring tool chain | Metadata contract (next step needs previous output) |
| **Independent parallel** | Inspection Team | Aggregation gate + Hooks tracking coverage | Aggregation requirement (report needs all inputs) |
| **User-driven** | Interactive | Gates on user actions + Hooks on state changes | User cannot proceed until gate passes |
| **Event-driven** | Reactive | Hooks trigger gates on events + Checkpointing | Event handlers validate before processing |

---

## Implementation Guide

### Assembly Line Implementation (QA Engine Example)

**Layer 1 - Protocol:**
```yaml
# .claude/skills/qa-management-layer/references/step-03.md
step: 3
name: "Generate Page Object"
required_inputs: ["discovered_elements", "expected_states"]
actions:
  - "Invoke Tool 3: generate_page_object"
  - "Pass elements + expected_states"
outputs: ["pom_metadata"]
```

**Layer 2 - Smart Gate:**
```python
# mcp_server/tools/gates/qg_page_object.py (POST mode)
def validate_pom_code(code, metadata):
    if "pass" in code or "# TODO" in code:
        return {
            "status": "FAILED",
            "violation": "Skeleton code detected",
            "teach": "POM must have: Locators as class constants, atomic methods returning self, state-check methods",
            "example": generate_correct_pattern()  # <-- TEACHING
        }
```

**Layer 3 - Hook:**
```javascript
// .claude/hooks/PostToolUse.js
if (toolName === "generate_page_object") {
  if (!result.metadata || !result.metadata.locators) {
    alert("Tool 3 incomplete: Missing locators in metadata");
  }
}
```

**Layer 4 - Checkpoint:**
```json
// Saved after qg_page_object gate passes
{
  "checkpoint_id": "qa_engine_step_3",
  "gate_passed": "qg_page_object",
  "state": {
    "pom_metadata": {...},
    "pom_code": "...",
    "next_step": "generate_task"
  }
}
```

---

### Inspection Team Implementation (Intel Scan Example)

**Layer 1 - Protocol:**
```yaml
# protocols/intel_scan.yaml
workflow:
  - step: "Category Execution"
    actions:
      - "Spawn 8 parallel searches (Direct Competitors, Feature Convergence, ...)"
      - "Each search returns structured results"
    outputs: ["category_results"]
  - step: "Aggregation"
    required_inputs: ["category_results"]
    actions:
      - "Invoke eg_coverage gate"
      - "Validate all 8 categories present"
```

**Layer 2 - Smart Gate:**
```python
# tools/execution_gates/gates/eg_coverage.py
def validate_coverage(context):
    categories_scanned = context.get("categories_scanned", [])
    if len(categories_scanned) < 8:
        missing = [c for c in ALL_CATEGORIES if c not in categories_scanned]
        return {
            "status": "FAILED",
            "missing_categories": missing,
            "teach": f"Execute WebSearch for: {', '.join(missing)}",  # <-- TEACHING
            "queries": generate_search_queries(missing)  # <-- EXPLICIT FIX
        }
```

**Layer 3 - Hook:**
```javascript
// .claude/hooks/PostToolUse.js
const coverageTracker = {};

if (toolName === "WebSearch") {
  const category = classifySearchCategory(query);
  coverageTracker[category] = true;

  // Real-time coverage monitoring
  const progress = Object.keys(coverageTracker).length;
  console.log(`Coverage: ${progress}/8 categories`);

  // Early warning (before aggregation gate)
  if (stepCount > 50 && progress < 8) {
    return {
      alert: true,
      message: `Coverage gap: ${progress}/8. Missing: ${missing.join(", ")}`
    };
  }
}
```

**Layer 4 - Checkpoint:**
```json
// Checkpoint after each category completes (enables partial resume)
{
  "checkpoint_id": "intel_scan_category_3",
  "categories_complete": ["Direct Competitors", "Feature Convergence", "Enterprise Adoption"],
  "category_results": {...},
  "next_categories": ["Regulatory & Standards", "Developer & Open Source", ...]
}
```

**Resume Scenario:**
If user stops after Category 3, next session loads checkpoint and continues with Category 4-8 (no need to re-run 1-3).

---

## Cross-Pattern Principles

### 1. Gates Validate AND Teach

**Every gate provides two outputs:**
- **Validation result:** PASS or FAIL
- **Teaching content:** If FAIL, provide explicit fix

**Example (any pattern):**
```python
# Bad gate (just blocks)
return {"status": "FAILED", "message": "Invalid format"}

# Good gate (teaches)
return {
    "status": "FAILED",
    "message": "Invalid format",
    "expected_format": "PART 1-5 structure",
    "actual_format": "Individual reports",
    "fix": "Consolidate 5 reports into single file with sections: PART 1, PART 2, ...",
    "example": load_example_template()  # <-- Show correct format
}
```

### 2. Hooks Provide Early Detection

**Hooks don't wait for gates. They monitor continuously.**

**Advantage:** Detect issues DURING execution (not just at checkpoints).

**Example:**
- Gate catches incomplete work at Step 8 (after all work done)
- Hook catches incomplete work at Step 3 (while work in progress)
- Earlier detection = less wasted effort

### 3. Checkpoints Enable Partial Progress

**Long workflows benefit from checkpointing.**

**Scenarios:**
- 8-category intel scan takes 30 minutes → Checkpoint after each category → If interrupted at category 5, resume from 6 (not restart from 1)
- 10-step QA workflow takes 15 minutes → Checkpoint after each step → If error at Step 7, rollback to Step 6 and retry (not restart from 1)

### 4. All Four Layers Are Independent

**Critical:** Each layer operates independently. One layer's failure doesn't compromise others.

**Example:**
- Protocol ignored → Gates still validate
- Gates bypassed → Hooks still monitor
- Hooks disabled → Checkpoints still enable recovery

**True defense-in-depth.**

---

## Pattern Evolution

### Current State (v1.0)
- **Assembly Line:** Fully implemented (QA Engine with 11 steps)
- **Inspection Team:** Partially implemented (Intel Scan - gates pending)
- **Platform Components:**
  - ✅ Protocols (Layer 1) - Claude Skills for QA vertical
  - ✅ Smart Gates (Layer 2) - QA gates (11 steps), Intel gates pending
  - ⚠️ Hooks (Layer 3) - PostToolUse audit logging only
  - ✅ State Checkpointing (Layer 4) - Workflow state management
  - ⚠️ Audit System - Progressive audit trail (basic implementation)
  - ⚠️ HITL System - Step 11 only (test execution failures)

### Roadmap (v1.2)
- **Protocol Engine:** YAML-based protocol loader (tool-agnostic)
- **Hook Engine:** Event dispatcher with handler registry
- **Modular HITL:** Reusable confirmation system for all steps
- **Audit Enhancements:** Retention policies, basic analytics

### Roadmap (v2.0)
- **Protocol Composition:** Reusable patterns across verticals
- **Advanced Hooks:** Hook composition, conditional hooks, priorities
- **Audit Analytics:** SQLite indexing, compliance reporting, dashboards
- **State Management:** Multi-session workflows, state visualization

### Future Patterns (v3.0)
- **Interactive Pattern:** User-driven workflows with gates on user actions
- **Reactive Pattern:** Event-driven workflows with hooks triggering gates
- **Hybrid Pattern:** Combine Assembly Line + Inspection Team (sequential phases with parallel work within each phase)

---

## Summary

**Isagawa Platform = 6 Components:**
1. Protocols (Layer 1) - Teach correct execution
2. Smart Gates (Layer 2) - Validate AND teach
3. Hooks (Layer 3) - Monitor continuously
4. State Checkpointing (Layer 4) - Enable recovery
5. Audit System - Provide observability
6. HITL System - Enable human oversight

**Component Selection:** Use Components 1-3 (universal), 4 (recommended), and 5-6 (project-dependent). See Component Selection Guide for details.

**Domain-Specific Frameworks:** QA Test Automation Framework (Selenium + Pytest) is QA-specific. Other verticals use platform components only.

---

*All patterns are Isagawa. All use defense-in-depth. The workflow topology dictates the pattern choice.*
