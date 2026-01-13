# AI Agent Management Layer Vertical (Second Vertical)

**Date:** 2026-01-11
**Status:** IDEA - Use 4D Framework when ready to design
**Priority:** HIGH - Strategic platform expansion

---

## The Insight

**We're not eating our own dog food yet.**

Our testing agent uses:
- **Protocol** (guidance) → Markdown files with step-by-step instructions
- **NO Quality Gates** (enforcement) → Agent can skip steps, stop early, ignore protocol

The workflows being tested have gates, but the testing agent itself doesn't.

```
CURRENT (Not Isagawa Way):
Testing Agent → Reads Protocol (suggestion) → Maybe follows it → Unvalidated results

SHOULD BE (Isagawa Way):
Testing Agent → Gate 0: Preflight → Gate 1: Protocol Adherence →
Execute Step 1 → Gate 2: Checkpoint 1 → ... → Gate 12: Completion → Validated results
```

---

## The Opportunity

**Second Vertical: AI Agent Management Layer**

- **Domain-agnostic** - Applies to ANY multi-step agent workflow (not just QA)
- **10-20x bigger market** - Every company using AI agents needs governance
- **First-mover advantage** - No competitors in agent governance space yet
- **Validates platform thesis** - Dogfooding proves the model works

---

## Initial Scope (First Version)

### Quality Gates for Testing Agent:

1. **qg_test_agent_preflight** - Test parameters, site accessibility, protocol exists, MCP servers
2. **qg_test_agent_protocol_adherence** - Agent confirms protocol read, lists 10 steps
3. **qg_test_agent_checkpoint_1 through checkpoint_10** - Each step completion validated
4. **qg_test_agent_completion** - All steps complete, test passed, audit complete

### Implementation Areas:

- Gate modules in `mcp_server/tools/gates/qg_test_agent_*.py`
- Updated testing protocol with gate enforcement
- Sub-agent execution wrapper that enforces gates
- Validation that agent cannot bypass checkpoints

---

## Possible Design (Technical Implementation)

**Note:** See `.business/architecture/ai_agent_management_layer_generic_design.md` for the complete domain-agnostic platform design. This section shows how the QA testing agent would use that platform.

**Key Insight:** Protocols = Skills (the .md reference files in `.claude/skills/`)

### System Architecture

```
AI AGENT MANAGEMENT LAYER - COMPONENTS
════════════════════════════════════════════════════════════════════

┌─────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATION LAYER                          │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  AgentOrchestrator                                       │  │
│  │  - Wraps agent execution                                 │  │
│  │  - Enforces gate sequence                                │  │
│  │  - Manages protocol adherence                            │  │
│  │  - Tracks state across steps                             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           │                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ProtocolEngine                                          │  │
│  │  - Loads protocol definition (YAML/JSON)                 │  │
│  │  - Maps steps to gates                                   │  │
│  │  - Defines checkpoint contracts                          │  │
│  │  - Handles gate failures with guidance                   │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      VALIDATION LAYER                           │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │ Preflight Gate │  │ Checkpoint 1-9 │  │ Completion Gate│   │
│  │ • Parameters   │  │ • Step output  │  │ • All steps    │   │
│  │ • Environment  │  │ • Metadata     │  │ • Test result  │   │
│  │ • Resources    │  │ • Protocol     │  │ • Audit trail  │   │
│  │ • Protocol     │  │   adherence    │  │ • Artifacts    │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                       AUDIT LAYER                               │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ExecutionTracker                                        │  │
│  │  • Logs gate passage timestamps                          │  │
│  │  • Records validation results                            │  │
│  │  • Captures retry attempts                               │  │
│  │  • Stores checkpoint state snapshots                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### File Structure

```
mcp_server/
├── tools/
│   └── gates/
│       ├── agent_management/           ← NEW: Agent governance gates
│       │   ├── qg_test_agent_preflight.py
│       │   ├── qg_test_agent_protocol_adherence.py
│       │   ├── qg_test_agent_checkpoint_1.py
│       │   ├── qg_test_agent_checkpoint_2.py
│       │   ├── ... (checkpoints 3-9)
│       │   └── qg_test_agent_completion.py
│       │
│       └── workflow_gates/              ← EXISTING: QA workflow gates
│           ├── qg_preflight.py
│           ├── qg_test_scenarios.py
│           └── ...
│
├── orchestration/                       ← NEW: Agent execution control
│   ├── agent_orchestrator.py           ← Wraps agent, enforces gates
│   ├── protocol_engine.py              ← Loads/interprets protocols
│   ├── execution_tracker.py            ← Audit trail manager
│   └── checkpoint_manager.py           ← State persistence
│
└── protocols/                           ← NEW: Protocol definitions
    ├── testing_agent_protocol.yaml     ← Maps steps to Skills
    └── custom_protocol_template.yaml   ← For other agent types
```

### Protocol Definition File (Maps to Skills)

```yaml
# protocols/testing_agent_protocol.yaml
# ═══════════════════════════════════════════════════════════════

protocol_name: "QA Test Generation Agent"
protocol_version: "1.0"
execution_pattern: "assembly_line"  # sequential, parallel, hybrid

# Maps protocol steps to Skill references and validation gates
workflow:
  - step: 0
    name: "Preflight"
    description: "Validate environment and parameters"
    skill_reference: ".claude/skills/qa-guidance-layer/references/step-01.md"
    gate: "qg_test_agent_preflight"
    required_inputs:
      - test_parameters
      - target_url
      - protocol_reference
    outputs:
      - validated_environment
      - execution_context

  - step: 1
    name: "User Input"
    description: "Gather persona and URL"
    skill_reference: ".claude/skills/qa-guidance-layer/references/step-01.md"
    gate: "qg_test_agent_checkpoint_1"
    required_inputs:
      - validated_environment
    required_outputs:
      - persona
      - url
      - workflow
      - role_name
      - credential_strategy
      - test_data_location

  - step: 2
    name: "AI Processing"
    description: "Extract BDD scenarios and expected states"
    skill_reference: ".claude/skills/qa-guidance-layer/references/step-02.md"
    gate: "qg_test_agent_checkpoint_2"
    required_inputs:
      - persona
      - url
      - workflow
    required_outputs:
      - bdd_scenarios
      - expected_states
      - intent
      - metadata_context

  # ... steps 3-9 map to remaining skill references ...

  - step: 10
    name: "Completion"
    description: "Validate all steps complete"
    gate: "qg_test_agent_completion"
    required_inputs:
      - all_previous_outputs
    validation:
      - all_files_saved
      - test_executed
      - test_passed
      - audit_complete

# Gate failure handling
gate_failure_strategy:
  max_retries: 3
  retry_with_guidance: true
  halt_on_critical_failure: true

# Audit configuration
audit:
  track_gate_passage: true
  store_checkpoint_state: true
  log_retry_attempts: true
  output_directory: "tests/_audit/agent_executions/"
```

### Core Components

**1. AgentOrchestrator** (orchestration/agent_orchestrator.py)
- Wraps AI agent execution
- Enforces gate sequence (cannot skip steps)
- Manages execution state across workflow
- Handles gate failures and retries
- Provides checkpoint management

**2. ProtocolEngine** (orchestration/protocol_engine.py)
- Loads protocol YAML definitions
- Maps workflow steps to Skill references
- Defines required inputs/outputs per step
- Manages gate failure strategies

**3. ExecutionTracker** (orchestration/execution_tracker.py)
- Logs gate passage timestamps
- Records validation results
- Captures retry attempts with guidance
- Stores complete audit trail
- Writes execution logs to `tests/_audit/agent_executions/`

**4. Quality Gates** (tools/gates/agent_management/)
- Independent validation modules per step
- Smart gates that provide fix guidance
- Validate required inputs/outputs
- Enforce protocol adherence
- Cannot be bypassed by agent

### Execution Flow

```
1. User initiates agent workflow
   ↓
2. AgentOrchestrator loads protocol definition
   ↓
3. FOR EACH STEP in protocol:
   ├─ Load Skill reference (.md file)
   ├─ Present to agent with required inputs
   ├─ Agent executes step
   ├─ Gate validates output
   ├─ IF PASS: proceed to next step
   ├─ IF NEEDS_RETRY: gate provides guidance → retry
   └─ IF FAIL: halt execution
   ↓
4. Completion gate validates entire workflow
   ↓
5. Audit trail written to file
   ↓
6. Return execution result
```

### Key Differentiators

| Aspect | Skill-Only (Current) | Management Layer (Proposed) |
|--------|---------------------|----------------------------|
| **Enforcement** | Suggestion | Mandatory gates |
| **Step Skipping** | Possible | Impossible (sequence enforced) |
| **Validation** | Agent self-reports | Independent gate validates |
| **Failure Handling** | Agent decides | Protocol defines strategy |
| **Audit Trail** | None | Complete execution log |
| **Retry Logic** | Ad-hoc | Smart gates provide guidance |
| **State Management** | Agent memory | Checkpoints persisted |
| **Completion Guarantee** | No | Yes (via completion gate) |

### Usage Example

```python
from mcp_server.orchestration.agent_orchestrator import AgentOrchestrator

# Initialize orchestrator with protocol
orchestrator = AgentOrchestrator(
    protocol_path="mcp_server/protocols/testing_agent_protocol.yaml",
    agent_id="qa_test_gen_agent_001"
)

# Execute workflow with gate enforcement
result = orchestrator.execute_workflow(
    initial_inputs={
        "user_request": "As a registered user, I want to purchase a product",
        "target_url": "http://www.automationpractice.pl",
        "skill_reference": ".claude/skills/qa-guidance-layer/"
    }
)

# Result contains:
# - status: SUCCESS | FAILED | HALTED
# - execution_state: All outputs from all steps
# - audit_trail: Complete log of gate passages, retries, failures
```

### Relationship to Existing Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  VERTICAL 2: AI Agent Management Layer (Proposed)            │
│  ├─ Orchestration components (AgentOrchestrator, etc.)       │
│  ├─ Agent-level gates (qg_test_agent_*)                      │
│  └─ Execution tracking and audit                             │
│                   │                                           │
│                   │ Manages/Controls                          │
│                   ▼                                           │
├──────────────────────────────────────────────────────────────┤
│  VERTICAL 1: QA Execution Engine (Existing)                  │
│  ├─ Workflow gates (qg_preflight, qg_test_scenarios, etc.)   │
│  ├─ Code generation tools (Tool 1-6)                         │
│  ├─ 4-layer framework (Role→Task→Page→WebInterface)          │
│  └─ Skills (protocols as .md references)                     │
└──────────────────────────────────────────────────────────────┘
```

### Implementation Strategy

**Phase 1: Core Infrastructure**
- Build AgentOrchestrator, ProtocolEngine, ExecutionTracker
- Create protocol YAML schema and loader
- Implement checkpoint management

**Phase 2: Testing Agent Gates**
- Implement 12 gates for testing agent workflow
- Map to existing 10-step Skill references
- Test gate enforcement and retry logic

**Phase 3: Integration**
- Wrap existing testing agent with orchestrator
- Validate gate passage on production workflows
- Measure completion rates and retry patterns

**Phase 4: Generalization**
- Extract domain-agnostic patterns
- Create protocol template for other agent types
- Document "how to add new agent protocols"

---

## Protocol Implementation Options

### The Core Question

**How should protocols be defined in the AI Agent Management Layer?**

A protocol defines:
- What steps exist in a workflow
- What each step requires (inputs) and produces (outputs)
- What gates validate each step
- How steps depend on each other
- How errors are handled

### Option 1: YAML + Skills (Recommended)

```
Structure:
├─ protocol.yaml        ← Machine-readable structure (metadata, I/O contracts, gates)
├─ skills/step-*.md     ← Human-readable guidance (instructions, examples)
└─ gates/*_gates.py     ← Validation logic (code)

Example:
protocols/qa_test_generation.yaml
- Defines 10 steps with inputs/outputs
- Maps each step to skill reference (.md file)
- Specifies gate for validation
- Declares dependencies

skills/qa-guidance-layer/step-01.md
- Instructions for step 1
- Examples and best practices
- Common mistakes to avoid
```

**Pros:**
- ✅ Industry standard (K8s, Docker, GitHub Actions use YAML)
- ✅ Non-developers can edit protocols
- ✅ Clear separation: YAML=structure, Skills=guidance
- ✅ Existing tooling (validators, parsers, IDE plugins)
- ✅ Version control friendly (clear diffs)
- ✅ Language-agnostic (can use from any language)
- ✅ Fast to implement (libraries exist)

**Cons:**
- ❌ No type safety (typos caught at runtime)
- ❌ Limited IDE autocomplete
- ❌ Two files to maintain (YAML + Skills)

**Why Skills Can't Be the Only Source:**
- Skills are for humans (narrative, flexible, examples)
- Protocols need machine-readable contracts (inputs/outputs, gates, dependencies)
- Parsing markdown reliably is hard
- Separating concerns is cleaner: YAML=structure, Skills=guidance

### Option 2: Python Classes

```
Structure:
├─ protocol.py          ← Python class with type annotations
├─ skills/step-*.md     ← Human-readable guidance
└─ gates/*_gates.py     ← Validation logic

Example:
class QATestGenerationProtocol(BaseProtocol):
    name = "QA Test Generation"
    steps = [
        StepConfig(
            step=0,
            name="Preflight",
            skill_reference=".../step-01.md",
            gate="preflight_gate",
            required_inputs=[...],
            required_outputs=[...]
        ),
    ]
```

**Pros:**
- ✅ Type safety (mypy, IDE type checking)
- ✅ IDE autocomplete and refactoring
- ✅ More expressive (functions, conditionals)
- ✅ Familiar to developers

**Cons:**
- ❌ Requires Python knowledge
- ❌ Not accessible to non-developers
- ❌ Tight coupling to Python
- ❌ Still need Skills for guidance

### Option 3: Hybrid (YAML + Python Extensions)

```
Structure:
├─ protocol.yaml        ← Base configuration (simple cases)
├─ extensions.py        ← Custom logic (complex cases)
├─ skills/step-*.md     ← Human-readable guidance
└─ gates/*_gates.py     ← Validation logic

Use YAML for simple protocols, add Python extensions when needed.
```

**Pros:**
- ✅ Best of both: declarative + dynamic
- ✅ Progressive complexity
- ✅ Non-devs edit YAML, devs add Python

**Cons:**
- ❌ Two config sources (complexity)
- ❌ Need to understand both YAML + Python

### Comparison Matrix

| Criteria | YAML + Skills | Python | Hybrid |
|----------|---------------|--------|--------|
| Ease of Use (Non-dev) | ★★★★☆ | ★★★☆☆ | ★★★☆☆ |
| Type Safety | ★☆☆☆☆ | ★★★★★ | ★★★☆☆ |
| IDE Support | ★★★☆☆ | ★★★★★ | ★★★★☆ |
| Tooling | ★★★★★ | ★★★★☆ | ★★★★☆ |
| Learning Curve | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ |
| Industry Standard | ★★★★★ | ★★★★☆ | ★★★☆☆ |
| Extensibility | ★★☆☆☆ | ★★★★★ | ★★★★★ |

### Recommendation: Start with YAML + Skills

**Rationale:**
1. **Industry proven** - YAML works for K8s, Docker Compose, GitHub Actions
2. **Multi-persona support** - Domain experts can edit protocols, devs write gates
3. **Fast to build** - Libraries and tooling exist
4. **Solid foundation** - Clear separation enables marketplace/registry
5. **Progressive** - Can add Python extensions later if needed

**Decision Tree:**
- Start with: **YAML + Skills** (default for new verticals)
- Move to Python if: All users are developers OR need complex protocol logic
- Add Hybrid if: Start simple, add complexity progressively

**Implementation Phases:**
1. **Phase 1**: Build YAML protocol engine + skill loader
2. **Phase 2**: Dogfood with QA vertical (10-step protocol)
3. **Phase 3**: Dogfood recursion (Agent Management vertical)
4. **Phase 4** (optional): Add Python extensions if YAML proves limiting

---

## The Complete System (All the Pieces)

### What You Need to Build a Vertical

```
PROTOCOL LAYER (What the workflow is)
═══════════════════════════════════════════════════════════
├─ YAML Protocol           ← Defines structure (steps, I/O, dependencies)
├─ Skills (.md files)      ← Provides guidance (instructions, examples)
└─ Result: "Blueprint" of the workflow


VALIDATION LAYER (How to verify correctness)
═══════════════════════════════════════════════════════════
├─ MCP Tools (Gates)       ← Validate each step (Python implementations)
├─ BaseGate (abstract)     ← All gates extend this
└─ Result: Independent validation at each checkpoint


EXECUTION LAYER (How to run the workflow)
═══════════════════════════════════════════════════════════
├─ AgentOrchestrator       ← Loads protocol, enforces steps, calls gates
├─ ProtocolEngine          ← Parses YAML, resolves dependencies
├─ Agent Executor          ← The AI agent doing the actual work
└─ Result: Workflow execution with enforcement


OBSERVABILITY LAYER (How to track what happened)
═══════════════════════════════════════════════════════════
├─ ExecutionTracker        ← Logs every event (gate pass/fail, retries)
├─ CheckpointManager       ← Saves state at each step (resume capability)
└─ Result: Complete audit trail + resumability
```

### Visual: How They All Work Together

```
┌─────────────────────────────────────────────────────────────────┐
│                   USER INITIATES WORKFLOW                       │
│                   "As a user, I want to login"                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │  1. AgentOrchestrator                      │
        │     Loads protocol definition              │
        └────────────────────┬───────────────────────┘
                             │
                             ├─► Reads: protocol.yaml
                             │   • 10 steps defined
                             │   • Inputs/outputs per step
                             │   • Gate per step
                             │   • Dependencies
                             │
                             ▼
        ┌────────────────────────────────────────────┐
        │  2. FOR EACH STEP:                         │
        └────────────────────┬───────────────────────┘
                             │
                             ▼
        ┌─────────────────────────────────────────────────────┐
        │  A. Load Skill Reference                            │
        │     skill = load(".../step-01.md")                  │
        │     → Instructions, examples, best practices        │
        └───────────────────────┬─────────────────────────────┘
                                │
                                ▼
        ┌─────────────────────────────────────────────────────┐
        │  B. Build Inputs from Previous Step                │
        │     inputs = {                                      │
        │       "persona": execution_state["persona"],        │
        │       "url": execution_state["url"]                 │
        │     }                                               │
        └───────────────────────┬─────────────────────────────┘
                                │
                                ▼
        ┌─────────────────────────────────────────────────────┐
        │  C. Agent Performs Work                             │
        │     agent_output = agent_executor(                  │
        │       step_config=step,                             │
        │       guidance=skill,          ← From Skills        │
        │       inputs=inputs             ← From prev step    │
        │     )                                               │
        │                                                     │
        │     Agent produces:                                 │
        │     {                                               │
        │       "persona": "As a registered user",            │
        │       "url": "http://example.com",                  │
        │       "workflow": "auth"                            │
        │     }                                               │
        └───────────────────────┬─────────────────────────────┘
                                │
                                ▼
        ┌─────────────────────────────────────────────────────┐
        │  D. Gate Validation (MCP Tool)                      │
        │     gate = gate_registry.get("checkpoint_gate_1")   │
        │     result = gate.validate(                         │
        │       step_config=step,        ← From YAML          │
        │       agent_output=output,     ← From Agent         │
        │       execution_state=state                         │
        │     )                                               │
        │                                                     │
        │     Gate checks:                                    │
        │     • All required outputs present?                 │
        │     • Types correct?                                │
        │     • Validation rules met?                         │
        │                                                     │
        │     Returns: PASS | NEEDS_RETRY | FAIL              │
        └───────────────────────┬─────────────────────────────┘
                                │
                   ┌────────────┼────────────┐
                   │            │            │
                   ▼            ▼            ▼
              ┌────────┐  ┌──────────┐  ┌──────┐
              │  PASS  │  │  RETRY   │  │ FAIL │
              └───┬────┘  └────┬─────┘  └───┬──┘
                  │            │            │
                  │            │            └─► HALT
                  │            │
                  │            └─► Gate provides guidance → Retry
                  │
                  ▼
        ┌─────────────────────────────────────────────────────┐
        │  E. Update State & Checkpoint                       │
        │     execution_state.update(agent_output)            │
        │     tracker.log_gate_pass(step, gate)               │
        │     checkpoint_mgr.save(step, execution_state)      │
        └───────────────────────┬─────────────────────────────┘
                                │
                                └─► Next step (repeat A-E)

        ┌─────────────────────────────────────────────────────┐
        │  3. After All Steps: Completion Gate               │
        │     completion_gate.validate(all_outputs)           │
        │     tracker.end_execution()                         │
        └───────────────────────┬─────────────────────────────┘
                                │
                                ▼
                        ┌───────────────┐
                        │ FINAL RESULT  │
                        │ • Status      │
                        │ • Outputs     │
                        │ • Audit trail │
                        └───────────────┘
```

### The Five Components Explained

```
COMPONENT 1: YAML Protocol
═══════════════════════════════════════════════════════════
What:    protocol.yaml file
Purpose: Machine-readable workflow definition
Contains:
  • Metadata (name, version, domain)
  • Steps (number, name, description)
  • Data contracts (required inputs/outputs per step)
  • Gate mappings (which gate validates which step)
  • Dependencies (step N depends on steps X, Y)
  • Retry strategies (max retries, fallback actions)

Who creates: Domain experts + developers
When created: Once per vertical
Example: protocols/qa_test_generation.yaml


COMPONENT 2: Skills
═══════════════════════════════════════════════════════════
What:    Markdown files (.md)
Purpose: Human-readable step guidance
Contains:
  • Instructions (how to perform the step)
  • Examples (sample inputs/outputs)
  • Best practices (dos and don'ts)
  • Common mistakes (what to avoid)
  • Troubleshooting (how to fix issues)

Who creates: Domain experts
When created: Once per step
Example: skills/qa-guidance-layer/step-01.md


COMPONENT 3: MCP Tools (Gates)
═══════════════════════════════════════════════════════════
What:    Python modules implementing BaseGate
Purpose: Independent validation of step outputs
Contains:
  • validate() method - checks outputs
  • provide_guidance() - generates help on failure
  • generate_fix_data() - smart healing (optional)

Who creates: Developers
When created: Once per gate
Example: mcp_server/tools/gates/qg_test_agent_checkpoint_1.py


COMPONENT 4: Orchestration (Platform Core)
═══════════════════════════════════════════════════════════
What:    AgentOrchestrator + ProtocolEngine
Purpose: Execute workflow with enforcement
Contains:
  • Load protocol YAML
  • Load skills
  • Execute steps in order
  • Call gates for validation
  • Handle retries with guidance
  • Manage execution state

Who creates: Platform developers (you build this once)
When created: Core platform infrastructure
Example: isagawa_platform/orchestration/agent_orchestrator.py


COMPONENT 5: Observability (Platform Core)
═══════════════════════════════════════════════════════════
What:    ExecutionTracker + CheckpointManager
Purpose: Track everything that happens
Contains:
  • Log all events (step start/end, gate pass/fail)
  • Record retry attempts with guidance
  • Save state at each checkpoint
  • Export complete audit trail

Who creates: Platform developers (you build this once)
When created: Core platform infrastructure
Example: isagawa_platform/state/execution_tracker.py
```

### What You Maintain Per Vertical

```
FOR EACH NEW VERTICAL (e.g., QA, Support, Docs):

You create:
├─ 1 YAML protocol       (workflow structure)
├─ N Skills (.md files)  (one per step)
└─ N MCP Tools (gates)   (one per checkpoint)

Platform provides (reuse):
├─ AgentOrchestrator     (generic)
├─ ProtocolEngine        (generic)
├─ ExecutionTracker      (generic)
└─ CheckpointManager     (generic)

Example for QA Vertical:
├─ protocols/qa_test_generation.yaml              ← You create
├─ skills/qa-guidance-layer/step-*.md (10 files)  ← You create
├─ gates/qg_test_agent_*.py (12 gates)            ← You create
└─ Uses platform orchestration/tracking           ← Platform provides
```

### Summary: You're Not Missing Anything

**The three things you mentioned:**
1. ✅ **YAML** - Protocol structure (steps, I/O, dependencies)
2. ✅ **Skills** - Guidance (instructions, examples)
3. ✅ **MCP Tools** - Validation (gates)

**Plus two platform components (build once, reuse everywhere):**
4. ✅ **Orchestration** - AgentOrchestrator + ProtocolEngine
5. ✅ **Observability** - ExecutionTracker + CheckpointManager

**That's the complete system.** The first three you create per vertical. The last two you build once as the platform core.

---

## Human-in-the-Loop (HITL) Integration

**Status:** Mandatory for 2026+ (MCP spec, EU AI Act, NIS2/DORA compliance)

### Why HITL is Critical

From competitive intel (Jan 2026):
- **2026 MCP spec** includes mandatory HITL protocol for high-risk actions
- **EU AI Act** requires human oversight for high-risk AI systems
- **NIS2 + DORA** require human accountability with personal liability
- **Industry consensus:** "By 2026, HITL is not a best practice, it's compliance"

**Isagawa advantage:** Gate architecture = built-in HITL enforcement (not bolted on after deployment)

### How HITL Works in Isagawa

```
HITL AS PART OF GATE VALIDATION
════════════════════════════════════════════════════════════

Normal Gate Flow (Low Risk):
Agent Output → Gate Validates → PASS/RETRY/FAIL → Continue

HITL Gate Flow (High Risk):
Agent Output → Gate Validates → Requires Human → Pause
                                        ↓
                                Human Reviews:
                                • Agent's proposed action
                                • Context/justification
                                • Risk assessment
                                        ↓
                        ┌───────────────┼───────────────┐
                        ▼               ▼               ▼
                    APPROVE         REJECT          MODIFY
                        │               │               │
                        ▼               ▼               ▼
                    Continue        Halt/Retry      Retry with guidance
```

### HITL Configuration in Protocol

```yaml
# protocol.yaml with HITL

workflow:
  - step: 5
    name: "Execute Payment Transaction"
    gate: "payment_execution_gate"

    # HITL Configuration
    hitl:
      enabled: true                    ← Turn HITL on/off per step
      trigger: "always"                ← always | risk_threshold | conditional
      risk_level: "high"               ← Determines urgency
      approvers:                       ← Who can approve
        - role: "finance_manager"
        - role: "senior_developer"
      timeout_seconds: 3600            ← How long to wait for human
      timeout_action: "halt"           ← What if timeout (halt | auto_approve | auto_reject)

    required_inputs:
      - name: "payment_amount"
        type: "float"
      - name: "recipient"
        type: "string"

    required_outputs:
      - name: "transaction_id"
        type: "string"
      - name: "approval_timestamp"
        type: "string"
      - name: "approved_by"
        type: "string"
```

### HITL Trigger Strategies

```
TRIGGER STRATEGY 1: Always Require (High Risk Steps)
═══════════════════════════════════════════════════════════
Use when: Financial transactions, data deletion, user access changes

workflow:
  - step: N
    hitl:
      trigger: "always"
      risk_level: "high"

→ Every execution pauses for human approval


TRIGGER STRATEGY 2: Risk Threshold (Conditional)
═══════════════════════════════════════════════════════════
Use when: Actions with variable risk based on values

workflow:
  - step: N
    hitl:
      trigger: "risk_threshold"
      conditions:
        - field: "payment_amount"
          operator: "greater_than"
          value: 10000

→ Require approval if payment > $10,000


TRIGGER STRATEGY 3: Failure Fallback (Gate Uncertain)
═══════════════════════════════════════════════════════════
Use when: Gate can't determine if output is safe

workflow:
  - step: N
    hitl:
      trigger: "conditional"
      condition: "gate_confidence < 0.8"

→ Require approval if gate confidence low
```

### HITL User Experience

```
HUMAN APPROVAL INTERFACE
════════════════════════════════════════════════════════════

┌────────────────────────────────────────────────────────────┐
│  APPROVAL REQUIRED                                         │
│  Agent: qa_test_gen_agent_001                              │
│  Protocol: QA Test Generation                              │
│  Step: 5 - Generate Test Code                              │
│  Risk Level: MEDIUM                                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  AGENT PROPOSES:                                           │
│  Generate test file: tests/admin/test_delete_users.py     │
│                                                            │
│  JUSTIFICATION:                                            │
│  "User requirement: Test admin can delete user accounts"  │
│                                                            │
│  RISK ASSESSMENT:                                          │
│  ⚠️  Test involves account deletion (high-risk action)     │
│  ✓  Sandbox environment detected                           │
│  ✓  Test uses test data (not production)                   │
│                                                            │
│  CONTEXT:                                                  │
│  • Previous steps completed successfully                   │
│  • All validations passed                                  │
│  • Execution state: {...}                                  │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  YOUR OPTIONS:                                             │
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐         │
│  │ APPROVE  │  │ REJECT   │  │ MODIFY & RETRY   │         │
│  └──────────┘  └──────────┘  └──────────────────┘         │
│                                                            │
│  Comments (optional):                                      │
│  ┌────────────────────────────────────────────────────┐   │
│  │                                                    │   │
│  └────────────────────────────────────────────────────┘   │
│                                                            │
│  Approver: john.smith@company.com (finance_manager)       │
│  Timeout: 58 minutes remaining                             │
└────────────────────────────────────────────────────────────┘
```

### HITL Gate Implementation

```
Gate with HITL Support
════════════════════════════════════════════════════════════

class PaymentExecutionGate(BaseGate):
    """
    Gate that requires human approval for payments.
    """

    def validate(self, step_config, agent_output, execution_state):
        # Standard validation first
        validation_result = self._validate_payment(agent_output)

        if validation_result.status == "FAIL":
            return validation_result

        # Check if HITL required
        hitl_config = step_config.get("hitl", {})

        if self._hitl_required(hitl_config, agent_output):
            # Pause execution, request human approval
            return ValidationResult(
                status="AWAITING_HUMAN_APPROVAL",
                message="Payment requires human approval",
                hitl_request={
                    "agent_proposal": agent_output,
                    "risk_assessment": self._assess_risk(agent_output),
                    "context": execution_state,
                    "approvers": hitl_config.get("approvers"),
                    "timeout_seconds": hitl_config.get("timeout_seconds")
                }
            )

        # No HITL needed, proceed
        return ValidationResult(status="PASS")

    def _hitl_required(self, hitl_config, agent_output):
        """Determine if HITL approval needed."""
        if not hitl_config.get("enabled"):
            return False

        trigger = hitl_config.get("trigger")

        if trigger == "always":
            return True

        elif trigger == "risk_threshold":
            # Check conditions
            conditions = hitl_config.get("conditions", [])
            for condition in conditions:
                if self._evaluate_condition(condition, agent_output):
                    return True

        return False
```

### HITL in Execution Flow

```
ORCHESTRATOR WITH HITL SUPPORT
════════════════════════════════════════════════════════════

def _execute_step_with_gate(self, step_config):
    # Agent does work
    agent_output = self.agent_executor(step_config, guidance, inputs)

    # Gate validation
    gate_result = self.gate_registry.get_gate(step_config.gate).validate(
        step_config, agent_output, self.execution_state
    )

    # Check if human approval needed
    if gate_result.status == "AWAITING_HUMAN_APPROVAL":
        # Log HITL request
        self.tracker.log_hitl_request(
            step=step_config.step,
            request=gate_result.hitl_request
        )

        # Send to approval system (UI, Slack, email, etc.)
        hitl_system = self._get_hitl_system()
        human_decision = hitl_system.request_approval(
            request=gate_result.hitl_request,
            timeout=step_config.hitl.timeout_seconds
        )

        # Log human decision
        self.tracker.log_hitl_decision(
            step=step_config.step,
            decision=human_decision.action,  # APPROVE | REJECT | MODIFY
            approver=human_decision.approver,
            comments=human_decision.comments
        )

        # Handle decision
        if human_decision.action == "APPROVE":
            return StepResult(status="SUCCESS", outputs=agent_output)

        elif human_decision.action == "REJECT":
            return StepResult(
                status="FAILED",
                error="Human rejected proposed action",
                reason=human_decision.comments
            )

        elif human_decision.action == "MODIFY":
            # Retry with human guidance
            modified_guidance = human_decision.modifications
            return self._retry_with_guidance(step_config, modified_guidance)

        elif human_decision.action == "TIMEOUT":
            # Handle timeout per config
            timeout_action = step_config.hitl.timeout_action
            if timeout_action == "halt":
                return StepResult(status="FAILED", error="HITL timeout")
            elif timeout_action == "auto_approve":
                self.tracker.log_warning("HITL timeout, auto-approved")
                return StepResult(status="SUCCESS", outputs=agent_output)
            # ... handle other timeout actions

    # No HITL needed or already handled
    return gate_result
```

### Audit Trail with HITL

```
EXECUTION LOG WITH HITL EVENTS
════════════════════════════════════════════════════════════

{
  "execution_id": "qa_agent_001_2026-01-12",
  "events": [
    {
      "timestamp": "2026-01-12T10:30:15",
      "event": "step_start",
      "step": 5,
      "step_name": "Generate Test Code"
    },
    {
      "timestamp": "2026-01-12T10:30:20",
      "event": "hitl_request",
      "step": 5,
      "gate": "test_generation_gate",
      "request": {
        "agent_proposal": "Generate admin deletion test",
        "risk_level": "medium",
        "required_approvers": ["finance_manager"]
      }
    },
    {
      "timestamp": "2026-01-12T10:45:33",
      "event": "hitl_decision",
      "step": 5,
      "decision": "APPROVE",
      "approver": "john.smith@company.com",
      "approver_role": "finance_manager",
      "comments": "Approved - sandbox environment confirmed",
      "approval_duration_seconds": 913
    },
    {
      "timestamp": "2026-01-12T10:45:35",
      "event": "gate_pass",
      "step": 5,
      "gate": "test_generation_gate",
      "validation_result": {
        "status": "PASS",
        "hitl_approved": true
      }
    }
  ]
}
```

### HITL Benefits for Isagawa

**Compliance:**
- ✅ Meets 2026 MCP spec mandatory HITL requirement
- ✅ Satisfies EU AI Act human oversight requirement
- ✅ Fulfills NIS2/DORA accountability requirements
- ✅ Built-in audit trail (who approved what, when, why)

**Competitive Advantage:**
- ✅ Built INTO gates (not bolted on after)
- ✅ Protocol-driven (declarative configuration)
- ✅ Flexible triggers (always, risk-based, conditional)
- ✅ Complete audit trail (demonstrable compliance)

**vs Competitors:**
- Arthur ADG: Observability-first, must add HITL retroactively
- Google Vertex: Tool governance, no workflow HITL
- OneTrust: Compliance monitoring, not execution control
- **Isagawa:** HITL enforcement at every checkpoint (proactive)

### HITL Deployment Strategy

**Phase 1: Core Infrastructure**
- Build HITL system (approval requests, UI, notifications)
- Integrate with orchestrator
- Add HITL support to BaseGate

**Phase 2: Protocol Support**
- Add HITL config to YAML schema
- Implement trigger strategies (always, risk-based, conditional)
- Build timeout handling

**Phase 3: Dogfood on QA Vertical**
- Add HITL to high-risk test generation steps
- Test approval flows
- Validate audit trail completeness

**Phase 4: Enterprise Features**
- Multi-approver workflows
- Role-based approvals
- Integration with enterprise systems (Slack, Teams, ServiceNow)
- SLA tracking

---

## Why This Matters

1. **Validates Thesis** - If we can't use our own product, how can we expect others to?
2. **Creates Second Revenue Stream** - Agent governance is huge market
3. **Improves QA Platform** - More reliable testing through enforced protocols
4. **Strategic Positioning** - First AI Management Layer for multi-step agents
5. **Competitive Moat** - Infrastructure + methodology + proof of concept

---

## Next Steps (When Ready)

**Use 4D Framework:**

1. **Design** - Conversational design discussion (Phase 1)
2. **Define** - Create PRD (Phase 2)
3. **Divide** - Break into tasks (Phase 3)
4. **Deliver** - Execute and ship (Phase 4)

**Context:** Come back to this after completing second test run (parabank7) to validate current QA platform stability.

---

## Related Documents

- `.business/strategy/isagawa_corp_thesis_v3.1.md` - Company thesis
- `FRAMEWORK.md` - Current QA platform architecture
- `.claude/skills/qa-guidance-layer/references/testing-protocol-10-step-e2e-v1.1.md` - Protocol to be enhanced with gates
