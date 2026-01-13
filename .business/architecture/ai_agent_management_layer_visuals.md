# AI Agent Management Layer - Complete Visual Architecture

**Date:** 2026-01-12
**Status:** Design Concept - Visual Documentation
**Purpose:** Comprehensive visual representations of all platform components

---

## 1. Platform Overview (30,000 Foot View)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│                     ISAGAWA AI AGENT MANAGEMENT LAYER                       │
│                     (Domain-Agnostic Platform)                              │
│                                                                             │
│  "Infrastructure that teaches AI how to succeed in multi-step workflows"    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
        ▼                             ▼                             ▼
┌───────────────────┐        ┌───────────────────┐        ┌───────────────────┐
│   VERTICAL 1:     │        │   VERTICAL 2:     │        │   VERTICAL N:     │
│  QA Execution     │        │ Customer Support  │        │ Any Domain You    │
│     Engine        │        │  Ticket Agent     │        │    Want to Add    │
├───────────────────┤        ├───────────────────┤        ├───────────────────┤
│ • Protocol YAML   │        │ • Protocol YAML   │        │ • Protocol YAML   │
│ • Custom Gates    │        │ • Custom Gates    │        │ • Custom Gates    │
│ • Skills          │        │ • Skills          │        │ • Skills          │
│ • Test Framework  │        │ • KB Integration  │        │ • Domain Logic    │
└───────────────────┘        └───────────────────┘        └───────────────────┘
        │                             │                             │
        └─────────────────────────────┼─────────────────────────────┘
                                      │
                                      │ All use same platform
                                      ▼
        ┌──────────────────────────────────────────────────────────┐
        │          SHARED PLATFORM COMPONENTS                      │
        │  • AgentOrchestrator                                     │
        │  • ProtocolEngine                                        │
        │  • GateRegistry                                          │
        │  • ExecutionTracker                                      │
        │  • CheckpointManager                                     │
        └──────────────────────────────────────────────────────────┘
```

---

## 2. Platform Core Components (Detailed)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       ISAGAWA PLATFORM CORE                                 │
│                       (isagawa_platform/)                                   │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 1: ORCHESTRATION (orchestration/)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  AgentOrchestrator                                                │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Public Methods:                                                  │     │
│  │  ├─ __init__(protocol_id, agent_id, agent_executor)             │     │
│  │  ├─ execute_workflow(initial_inputs) → Result                    │     │
│  │  ├─ resume_from_checkpoint(checkpoint_id) → Result               │     │
│  │  └─ get_execution_status() → Status                              │     │
│  │                                                                   │     │
│  │  Private Methods:                                                 │     │
│  │  ├─ _execute_sequential() → Result                               │     │
│  │  ├─ _execute_parallel() → Result                                 │     │
│  │  ├─ _execute_step_with_gate(step) → StepResult                   │     │
│  │  ├─ _validate_with_gate(gate, data) → ValidationResult           │     │
│  │  ├─ _load_guidance(step) → str                                   │     │
│  │  ├─ _build_step_inputs(step) → Dict                              │     │
│  │  └─ _handle_failure(step, result) → Result                       │     │
│  │                                                                   │     │
│  │  Dependencies:                                                    │     │
│  │  ├─ ProtocolEngine (loads protocol)                              │     │
│  │  ├─ ExecutionTracker (logs events)                               │     │
│  │  ├─ CheckpointManager (saves state)                              │     │
│  │  └─ GateRegistry (validates steps)                               │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                │                                            │
│                                │ uses                                       │
│                                ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  ProtocolEngine                                                   │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Public Methods:                                                  │     │
│  │  ├─ __init__(protocol: Protocol)                                 │     │
│  │  ├─ get_workflow_steps() → List[StepConfig]                      │     │
│  │  ├─ get_completion_step() → StepConfig                           │     │
│  │  ├─ build_dependency_graph() → DependencyGraph                   │     │
│  │  └─ get_execution_pattern() → str                                │     │
│  │                                                                   │     │
│  │  Private Methods:                                                 │     │
│  │  ├─ _parse_protocol_yaml() → Protocol                            │     │
│  │  ├─ _validate_protocol_schema() → bool                           │     │
│  │  ├─ _resolve_dependencies() → DependencyGraph                    │     │
│  │  └─ _detect_circular_dependencies() → bool                       │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                │                                            │
│                                │ uses                                       │
│                                ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  ProtocolRegistry                                                 │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Public Methods:                                                  │     │
│  │  ├─ register_protocol(id, yaml_path) → None                      │     │
│  │  ├─ get_protocol(id) → Protocol                                  │     │
│  │  ├─ list_protocols() → List[ProtocolMetadata]                    │     │
│  │  ├─ unregister_protocol(id) → None                               │     │
│  │  └─ validate_protocol(yaml_path) → ValidationResult              │     │
│  │                                                                   │     │
│  │  Storage:                                                         │     │
│  │  └─ _protocols: Dict[str, Protocol]                              │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 2: VALIDATION (validation/)                                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  BaseGate (Abstract)                                              │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Abstract Methods:                                                │     │
│  │  └─ validate(step_config, agent_output, state) → ValidationResult│     │
│  │                                                                   │     │
│  │  Concrete Methods:                                                │     │
│  │  ├─ check_required_fields(data, fields) → (bool, List[missing])  │     │
│  │  ├─ provide_guidance(missing, step_config) → Dict                │     │
│  │  └─ generate_fix_data(missing, state) → Dict                     │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                │                                            │
│                                │ extended by                                │
│                                ▼                                            │
│  ┌────────────────┐  ┌────────────────┐  ┌───────────────────────────┐    │
│  │ PreflightGate  │  │ CheckpointGate │  │ CompletionGate            │    │
│  │ ────────────── │  │ ────────────── │  │ ─────────────────────     │    │
│  │                │  │                │  │                           │    │
│  │ validate():    │  │ validate():    │  │ validate():               │    │
│  │ • Check env    │  │ • Check I/O    │  │ • All steps done?         │    │
│  │ • Resources OK?│  │ • Metadata OK? │  │ • Artifacts present?      │    │
│  │ • Protocol OK? │  │ • Contract OK? │  │ • Audit complete?         │    │
│  │                │  │                │  │ • Final state valid?      │    │
│  └────────────────┘  └────────────────┘  └───────────────────────────┘    │
│                                │                                            │
│                                │ registered in                              │
│                                ▼                                            │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  GateRegistry                                                     │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Public Methods:                                                  │     │
│  │  ├─ register(gate_id, gate_class) → None                         │     │
│  │  ├─ get_gate(gate_id) → BaseGate                                 │     │
│  │  ├─ list_gates() → List[str]                                     │     │
│  │  └─ unregister(gate_id) → None                                   │     │
│  │                                                                   │     │
│  │  Storage:                                                         │     │
│  │  └─ _gates: Dict[str, BaseGate]                                  │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 3: STATE & AUDIT (state/)                                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  ExecutionTracker                                                 │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Public Methods:                                                  │     │
│  │  ├─ start_execution(inputs) → None                               │     │
│  │  ├─ log_step_start(step, name) → None                            │     │
│  │  ├─ log_step_end(step, outputs) → None                           │     │
│  │  ├─ log_gate_pass(step, gate) → None                             │     │
│  │  ├─ log_gate_fail(step, gate, reason) → None                     │     │
│  │  ├─ log_retry(step, count, message) → None                       │     │
│  │  ├─ log_agent_action(action, context) → None                     │     │
│  │  ├─ end_execution(result) → None                                 │     │
│  │  └─ get_audit_trail() → List[Event]                              │     │
│  │                                                                   │     │
│  │  Storage:                                                         │     │
│  │  ├─ audit_log: List[Event]                                       │     │
│  │  ├─ execution_id: str                                            │     │
│  │  └─ timestamps: Dict[str, datetime]                              │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  CheckpointManager                                                │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Public Methods:                                                  │     │
│  │  ├─ save_checkpoint(step, state) → checkpoint_id                 │     │
│  │  ├─ load_checkpoint(checkpoint_id) → State                       │     │
│  │  ├─ list_checkpoints(execution_id) → List[Checkpoint]            │     │
│  │  ├─ delete_checkpoint(checkpoint_id) → None                      │     │
│  │  └─ cleanup_old_checkpoints(days) → int                          │     │
│  │                                                                   │     │
│  │  Storage Strategy:                                                │     │
│  │  ├─ File System (default)                                        │     │
│  │  ├─ Database (optional)                                          │     │
│  │  └─ S3/Cloud (optional)                                          │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 4: PROTOCOL DEFINITIONS (protocols/)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  ProtocolSchema                                                   │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Defines structure of protocol YAML files                        │     │
│  │                                                                   │     │
│  │  Sections:                                                        │     │
│  │  ├─ protocol_name: str                                           │     │
│  │  ├─ protocol_id: str                                             │     │
│  │  ├─ protocol_version: str                                        │     │
│  │  ├─ domain: str                                                  │     │
│  │  ├─ execution: ExecutionConfig                                   │     │
│  │  ├─ workflow: List[StepConfig]                                   │     │
│  │  ├─ gate_failure_strategies: Dict                                │     │
│  │  └─ audit: AuditConfig                                           │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  ProtocolValidator                                                │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Public Methods:                                                  │     │
│  │  ├─ validate_schema(yaml_content) → ValidationResult             │     │
│  │  ├─ validate_dependencies(workflow) → ValidationResult           │     │
│  │  ├─ validate_gates_exist(workflow, registry) → ValidationResult  │     │
│  │  └─ validate_data_contracts(workflow) → ValidationResult         │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  LAYER 5: SKILL INTEGRATION (skills/)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │  SkillLoader                                                      │     │
│  │  ────────────────────────────────────────────────────────         │     │
│  │                                                                   │     │
│  │  Public Methods:                                                  │     │
│  │  ├─ load(skill_path) → str                                       │     │
│  │  ├─ parse_skill(content) → SkillMetadata                         │     │
│  │  └─ validate_skill(content) → ValidationResult                   │     │
│  │                                                                   │     │
│  │  Supports:                                                        │     │
│  │  ├─ .md skill files (primary)                                    │     │
│  │  ├─ Inline instructions (fallback)                               │     │
│  │  └─ Remote skill URLs (future)                                   │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXECUTION DATA FLOW                                │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐
│   USER       │
│   REQUEST    │
└──────┬───────┘
       │
       │ Initial Inputs
       │ {
       │   "user_requirement": "...",
       │   "target_url": "...",
       │   ...
       │ }
       │
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  1. AgentOrchestrator.execute_workflow(initial_inputs)                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  execution_state = initial_inputs.copy()                                    │
│  tracker.start_execution(initial_inputs)                                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────┐         │
│  │  Load Protocol                                                │         │
│  │  ────────────────────────────────────────────────────         │         │
│  │  protocol = protocol_registry.get_protocol(protocol_id)       │         │
│  │  steps = protocol_engine.get_workflow_steps()                 │         │
│  │  pattern = protocol.execution.pattern                         │         │
│  └───────────────────────────────────────────────────────────────┘         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
       │
       │ For each step in workflow
       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  2. Execute Step with Gate                                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────┐         │
│  │  A. Load Guidance                                             │         │
│  │  ────────────────────────────────────────────────────         │         │
│  │  IF step.skill_reference:                                     │         │
│  │    guidance = SkillLoader.load(step.skill_reference)          │         │
│  │  ELSE:                                                         │         │
│  │    guidance = step.instructions                               │         │
│  └───────────────────────────────────────────────────────────────┘         │
│                      │                                                      │
│                      ▼                                                      │
│  ┌───────────────────────────────────────────────────────────────┐         │
│  │  B. Build Step Inputs                                         │         │
│  │  ────────────────────────────────────────────────────         │         │
│  │  step_inputs = {}                                             │         │
│  │  FOR field IN step.required_inputs:                           │         │
│  │    IF field.source == "previous_step":                        │         │
│  │      step_inputs[field.name] = execution_state[field.name]    │         │
│  │    ELIF field.source == "user_input":                         │         │
│  │      step_inputs[field.name] = initial_inputs[field.name]     │         │
│  └───────────────────────────────────────────────────────────────┘         │
│                      │                                                      │
│                      ▼                                                      │
│  ┌───────────────────────────────────────────────────────────────┐         │
│  │  C. Agent Performs Work                                       │         │
│  │  ────────────────────────────────────────────────────         │         │
│  │  agent_output = agent_executor(                               │         │
│  │    step_config=step,                                          │         │
│  │    guidance=guidance,                                         │         │
│  │    inputs=step_inputs                                         │         │
│  │  )                                                             │         │
│  │                                                                │         │
│  │  Agent produces:                                              │         │
│  │  {                                                             │         │
│  │    "field1": "value1",                                        │         │
│  │    "field2": "value2",                                        │         │
│  │    ...                                                         │         │
│  │  }                                                             │         │
│  └───────────────────────────────────────────────────────────────┘         │
│                      │                                                      │
│                      ▼                                                      │
│  ┌───────────────────────────────────────────────────────────────┐         │
│  │  D. Gate Validation                                           │         │
│  │  ────────────────────────────────────────────────────         │         │
│  │  gate = gate_registry.get_gate(step.gate)                     │         │
│  │  result = gate.validate(                                      │         │
│  │    step_config=step,                                          │         │
│  │    agent_output=agent_output,                                 │         │
│  │    execution_state=execution_state                            │         │
│  │  )                                                             │         │
│  │                                                                │         │
│  │  Result types:                                                │         │
│  │  • PASS       → proceed to next step                          │         │
│  │  • NEEDS_RETRY → provide guidance, retry                      │         │
│  │  • FAIL       → halt execution                                │         │
│  └───────────────────────────────────────────────────────────────┘         │
│                      │                                                      │
│                      │                                                      │
│         ┌────────────┴────────────┐                                        │
│         │                         │                                        │
│         ▼                         ▼                         ▼              │
│    ┌─────────┐            ┌──────────────┐          ┌──────────┐          │
│    │  PASS   │            │ NEEDS_RETRY  │          │   FAIL   │          │
│    └────┬────┘            └──────┬───────┘          └────┬─────┘          │
│         │                         │                       │                │
│         │                         │                       │                │
│         │                  ┌──────────────────────┐       │                │
│         │                  │ Provide Guidance     │       │                │
│         │                  │ ──────────────────── │       │                │
│         │                  │ guidance = {         │       │                │
│         │                  │   "field": {         │       │                │
│         │                  │     "why_failed":".."│       │                │
│         │                  │     "how_to_fix":".."│       │                │
│         │                  │     "example": "..." │       │                │
│         │                  │   },                 │       │                │
│         │                  │   "fix_data": {...}  │       │                │
│         │                  │ }                    │       │                │
│         │                  └──────┬───────────────┘       │                │
│         │                         │                       │                │
│         │                         │ Retry with guidance   │                │
│         │                         └──────► (back to B)    │                │
│         │                                                 │                │
│         │ Update state                           │ Halt execution          │
│         ▼                                        ▼                         │
│  ┌───────────────────────────────────────────────────────────────┐         │
│  │  E. Update Execution State                                    │         │
│  │  ────────────────────────────────────────────────────         │         │
│  │  execution_state.update(agent_output)                         │         │
│  │  tracker.log_gate_pass(step, gate)                            │         │
│  │  checkpoint_mgr.save_checkpoint(step, execution_state)        │         │
│  │  current_step += 1                                            │         │
│  └───────────────────────────────────────────────────────────────┘         │
│                      │                                                      │
└──────────────────────┼──────────────────────────────────────────────────────┘
                       │
                       │ Repeat for next step
                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  3. Completion Validation                                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  completion_gate.validate(all_outputs)                                      │
│  tracker.end_execution(result)                                              │
│  audit_trail = tracker.export_audit_trail()                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                       │
                       ▼
               ┌───────────────┐
               │  FINAL RESULT │
               ├───────────────┤
               │ status        │
               │ execution_state│
               │ audit_trail   │
               └───────────────┘
```

---

## 4. Execution Patterns Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PATTERN 1: ASSEMBLY LINE                                │
│                     (Sequential Dependencies)                               │
└─────────────────────────────────────────────────────────────────────────────┘

Used by: QA Test Generation, Customer Support, Sequential workflows

┌──────┐     ┌──────┐     ┌──────┐     ┌──────┐     ┌──────┐
│Step 0│────►│Gate 0│────►│Step 1│────►│Gate 1│────►│Step 2│──► ...
└──────┘     └──────┘     └──────┘     └──────┘     └──────┘
   │            │            │            │            │
   │ outputs    │ validates  │ outputs    │ validates  │ outputs
   │            │            │            │            │
   └────────────┴────────────┴────────────┴────────────┴──────► Execution State

Characteristics:
• Step N+1 REQUIRES Step N outputs (strict dependency)
• Cannot skip steps (missing inputs = impossible)
• Linear progression
• Easy to reason about
• Predictable execution time

Enforcement Mechanism:
• Metadata contract between steps
• Next step cannot execute without previous outputs
• Gate validates required inputs present

Example Data Flow:
Step 0 outputs: {persona, url}
              ↓
Gate 0 validates: persona exists? url exists?
              ↓ PASS
Step 1 inputs: {persona, url} ← from Step 0
Step 1 outputs: {bdd_scenarios, expected_states}
              ↓
Gate 1 validates: bdd_scenarios valid? expected_states present?
              ↓ PASS
Step 2 inputs: {bdd_scenarios, expected_states} ← from Step 1
...



┌─────────────────────────────────────────────────────────────────────────────┐
│                     PATTERN 2: INSPECTION TEAM                              │
│                     (Parallel Fan-Out/Fan-In)                               │
└─────────────────────────────────────────────────────────────────────────────┘

Used by: Document Analysis, Multi-aspect Evaluation, Independent tasks

                          ┌──────┐
                          │Step 0│ (Preflight/Setup)
                          └───┬──┘
                              │ outputs: document_content
                              │
              ┌───────────────┼───────────────┬───────────────┐
              │               │               │               │
              ▼               ▼               ▼               ▼
        ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
        │ Step 1  │     │ Step 2  │     │ Step 3  │     │ Step 4  │
        │Sentiment│     │Entities │     │ Topics  │     │Language │
        └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
             │               │               │               │
             │ ALL run in PARALLEL (no dependencies)          │
             │               │               │               │
             ▼               ▼               ▼               ▼
        ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
        │ Gate 1  │     │ Gate 2  │     │ Gate 3  │     │ Gate 4  │
        └────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
             │               │               │               │
             │  sentiment    │  entities     │  topics       │  language
             │               │               │               │
             └───────────────┴───────────────┴───────────────┘
                                    │
                                    │ ALL outputs required
                                    ▼
                              ┌───────────┐
                              │  Step 5   │ (Aggregation)
                              │ Combine   │
                              └─────┬─────┘
                                    │
                                    ▼
                              ┌───────────┐
                              │  Gate 5   │ (Completion)
                              └───────────┘

Characteristics:
• Steps 1-4 are INDEPENDENT (no dependencies)
• Can execute in parallel (faster)
• Step 5 DEPENDS ON all of 1-4 (aggregation)
• Variable execution time (slowest step determines duration)

Enforcement Mechanism:
• Aggregation gate requires ALL parallel outputs
• Cannot generate report without all inspections complete
• Missing inspector = incomplete data = gate fails

Example Data Flow:
Step 0 outputs: {document_content}
              ↓ (splits into parallel paths)
              ├─► Step 1 → sentiment_scores
              ├─► Step 2 → entities
              ├─► Step 3 → topics
              └─► Step 4 → language
                            ↓ (all converge)
Step 5 inputs: {sentiment_scores, entities, topics, language}
            ↑  ALL required for aggregation
Gate 5 validates: all 4 outputs present?
              ↓ PASS
Step 5 outputs: {analysis_report}



┌─────────────────────────────────────────────────────────────────────────────┐
│                     PATTERN 3: HYBRID                                       │
│                     (Mixed Sequential + Parallel)                           │
└─────────────────────────────────────────────────────────────────────────────┘

Used by: Complex workflows with both dependencies and parallelizable sections

┌──────┐     ┌──────┐     ┌──────┐
│Step 0│────►│Gate 0│────►│Step 1│ (Sequential setup)
└──────┘     └──────┘     └───┬──┘
                              │
                ┌─────────────┼─────────────┐
                │             │             │
                ▼             ▼             ▼
          ┌─────────┐   ┌─────────┐   ┌─────────┐
          │ Step 2A │   │ Step 2B │   │ Step 2C │ (Parallel processing)
          └────┬────┘   └────┬────┘   └────┬────┘
               │             │             │
               └─────────────┼─────────────┘
                             │
                             ▼
                       ┌──────────┐
                       │  Step 3  │ (Sequential continuation)
                       └─────┬────┘
                             │
                             ▼
                       ┌──────────┐
                       │  Gate 3  │
                       └──────────┘

Characteristics:
• Combines benefits of both patterns
• Sequential where dependencies exist
• Parallel where independent
• Optimizes for speed while maintaining correctness

Example Use Case:
Step 0-1: Setup (sequential)
Step 2A-C: Multiple page analysis (parallel)
Step 3: Combine results (sequential)
```

---

## 5. Gate Validation Flow (Smart Gates)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    GATE VALIDATION FLOW                                     │
│                    (Smart Gate Pattern)                                     │
└─────────────────────────────────────────────────────────────────────────────┘


                          Agent Output
                          {
                            "field1": "value1",
                            "field2": null,  ← MISSING
                            ...
                          }
                                │
                                ▼
      ┌─────────────────────────────────────────────────────────────┐
      │  GATE.validate(step_config, agent_output, execution_state)  │
      └─────────────────────────────────────────────────────────────┘
                                │
                                │
      ┌─────────────────────────┼─────────────────────────┐
      │                         │                         │
      ▼                         ▼                         ▼
┌──────────────┐      ┌──────────────────┐      ┌──────────────┐
│   SCENARIO   │      │    SCENARIO      │      │   SCENARIO   │
│      A       │      │       B          │      │      C       │
│              │      │                  │      │              │
│     PASS     │      │   NEEDS_RETRY    │      │     FAIL     │
└──────────────┘      └──────────────────┘      └──────────────┘
      │                         │                         │
      │                         │                         │
      ▼                         ▼                         ▼


┌─────────────────────────────────────────────────────────────────────────────┐
│  SCENARIO A: PASS                                                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Gate Logic:                                                                │
│  ├─ Check required fields → ALL PRESENT ✓                                  │
│  ├─ Validate data types → ALL CORRECT ✓                                    │
│  ├─ Check business rules → ALL SATISFIED ✓                                 │
│  └─ Verify data contracts → ALL MET ✓                                      │
│                                                                             │
│  Result:                                                                    │
│  {                                                                          │
│    "status": "PASS",                                                        │
│    "message": "All validations passed",                                     │
│    "outputs": agent_output  ← Pass through to next step                    │
│  }                                                                          │
│                                                                             │
│  Next Action:                                                               │
│  └─► Proceed to next step                                                  │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  SCENARIO B: NEEDS_RETRY (Smart Gate - Provides Guidance)                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Gate Logic:                                                                │
│  ├─ Check required fields → SOME MISSING ✗                                 │
│  │   Missing: ["field2", "field3"]                                         │
│  │                                                                          │
│  ├─ Generate Guidance (SMART!)                                             │
│  │   FOR each missing field:                                               │
│  │     ├─ Load field definition from step_config                           │
│  │     ├─ Explain what's expected                                          │
│  │     ├─ Provide example                                                  │
│  │     └─ Suggest fix approach                                             │
│  │                                                                          │
│  └─ Generate Fix Data (SMART!)                                             │
│      ├─ Check if fix data can be auto-generated                            │
│      ├─ Query execution_state for related data                             │
│      └─ Provide pre-filled values where possible                           │
│                                                                             │
│  Result:                                                                    │
│  {                                                                          │
│    "status": "NEEDS_RETRY",                                                 │
│    "message": "Missing required fields: field2, field3",                    │
│    "guidance": {                                                            │
│      "field2": {                                                            │
│        "description": "BDD scenario in Given/When/Then format",             │
│        "expected_type": "dict",                                             │
│        "example": {                                                         │
│          "given": "User is on login page",                                  │
│          "when": "User enters credentials",                                 │
│          "then": "User is logged in"                                        │
│        },                                                                   │
│        "validation_rules": {                                                │
│          "must_have_keys": ["given", "when", "then"],                       │
│          "format": "string"                                                 │
│        }                                                                    │
│      },                                                                     │
│      "field3": {                                                            │
│        "description": "Expected states for POM state-check methods",        │
│        "expected_type": "list",                                             │
│        "example": ["is_logged_in", "is_error_displayed"],                  │
│        "extraction_hint": "Look for 'Then' clauses in BDD scenarios"        │
│      }                                                                      │
│    },                                                                       │
│    "fix_data": {                           ← GATE PROVIDES FIX!            │
│      "field3": ["is_logged_in"]           ← Auto-extracted from context    │
│    },                                                                       │
│    "retry_count": 1,                                                        │
│    "max_retries": 3                                                         │
│  }                                                                          │
│                                                                             │
│  Next Action:                                                               │
│  ├─► Merge guidance into agent prompt                                      │
│  ├─► Include fix_data as hint                                              │
│  └─► Retry step with enhanced context                                      │
│                                                                             │
│  Agent Retry Prompt:                                                        │
│  "Your previous output was missing: field2, field3                          │
│                                                                             │
│   field2 should be: BDD scenario in Given/When/Then format                  │
│   Example: {given: '...', when: '...', then: '...'}                        │
│                                                                             │
│   field3 should be: Expected states for POM state-check methods            │
│   Example: ['is_logged_in', 'is_error_displayed']                          │
│   Hint: I already extracted 'is_logged_in' from context.                   │
│         Add any additional states you find.                                 │
│                                                                             │
│   Please retry with complete output."                                       │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  SCENARIO C: FAIL (Unrecoverable Error)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Gate Logic:                                                                │
│  ├─ Check required fields → PRESENT ✓                                      │
│  ├─ Validate data types → CORRECT ✓                                        │
│  └─ Check business rules → VIOLATED ✗                                      │
│      └─ Example: URL returns 404, site is down                             │
│                                                                             │
│  Result:                                                                    │
│  {                                                                          │
│    "status": "FAIL",                                                        │
│    "message": "Target site unreachable: 404 Not Found",                     │
│    "error_type": "ENVIRONMENT_ERROR",                                       │
│    "error_details": {                                                       │
│      "url": "http://example.com",                                           │
│      "status_code": 404,                                                    │
│      "retry_possible": false                                                │
│    },                                                                       │
│    "recommendation": "Verify target URL and ensure site is accessible"      │
│  }                                                                          │
│                                                                             │
│  Next Action:                                                               │
│  ├─► Halt execution                                                        │
│  ├─► Log failure to audit trail                                            │
│  └─► Return error to user                                                  │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│  SMART GATE vs TRADITIONAL GATE                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Traditional Gate (blocking only):                                          │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │  Agent Output → Gate → Missing fields?                      │           │
│  │                         │                                    │           │
│  │                         ▼                                    │           │
│  │                      ❌ ERROR                                │           │
│  │                      "Missing: field2"                       │           │
│  │                      ← Agent has to guess what's needed      │           │
│  └─────────────────────────────────────────────────────────────┘           │
│                                                                             │
│  Smart Gate (provides guidance):                                            │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │  Agent Output → Gate → Missing fields?                      │           │
│  │                         │                                    │           │
│  │                         ▼                                    │           │
│  │                      ⚠️  NEEDS_RETRY                         │           │
│  │                      "Missing: field2                        │           │
│  │                       Here's what field2 should be: ...      │           │
│  │                       Here's an example: ...                 │           │
│  │                       Here's related data I found: ...       │           │
│  │                       Try again with this guidance."         │           │
│  │                      ← Agent has explicit guidance           │           │
│  └─────────────────────────────────────────────────────────────┘           │
│                                                                             │
│  Key Difference:                                                            │
│  Traditional: "You're wrong. Figure it out." ❌                             │
│  Smart:       "You're missing X. Here's X. Retry." ✅                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 6. Protocol Structure Visualization

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     PROTOCOL YAML STRUCTURE                                 │
└─────────────────────────────────────────────────────────────────────────────┘

protocol.yaml
│
├─ METADATA (Who, What, When)
│  ├─ protocol_name: "QA Test Generation Agent"
│  ├─ protocol_id: "qa.test_generation.v1"
│  ├─ protocol_version: "1.0.0"
│  ├─ domain: "qa_automation"
│  ├─ description: "Generates end-to-end test code..."
│  └─ metadata:
│     ├─ author: "Isagawa Corp"
│     ├─ created_date: "2026-01-12"
│     └─ tags: ["qa", "test-generation", "e2e"]
│
├─ EXECUTION CONFIG (How to run)
│  ├─ pattern: "assembly_line"  ← sequential | inspection_team | hybrid
│  ├─ parallelization: false    ← Can steps run in parallel?
│  ├─ timeout_seconds: 1800     ← Max execution time
│  └─ allow_resume: true        ← Checkpoint/resume support
│
├─ WORKFLOW (Steps definition)
│  │
│  ├─ STEP 0: Preflight
│  │  ├─ step: 0
│  │  ├─ name: "Preflight"
│  │  ├─ description: "Validate environment..."
│  │  │
│  │  ├─ GUIDANCE
│  │  │  ├─ skill_reference: "path/to/skill.md"  ← Option 1: Use skill
│  │  │  └─ instructions: "..."                  ← Option 2: Inline
│  │  │
│  │  ├─ GATE
│  │  │  ├─ gate: "preflight_gate"               ← Maps to GateRegistry
│  │  │  └─ gate_config:
│  │  │     └─ validation_rules: {...}
│  │  │
│  │  ├─ INPUTS (What this step needs)
│  │  │  ├─ required_inputs:
│  │  │  │  ├─ name: "user_requirement"
│  │  │  │  │  ├─ type: "string"
│  │  │  │  │  ├─ source: "user_input"          ← Where it comes from
│  │  │  │  │  └─ validation: {format: "..."}
│  │  │  │  └─ name: "target_url"
│  │  │  │     ├─ type: "string"
│  │  │  │     ├─ source: "user_input"
│  │  │  │     └─ validation: {format: "url"}
│  │  │
│  │  ├─ OUTPUTS (What this step produces)
│  │  │  └─ required_outputs:
│  │  │     ├─ name: "validated_inputs"
│  │  │     │  └─ type: "dict"
│  │  │     └─ name: "execution_context"
│  │  │        └─ type: "dict"
│  │  │
│  │  ├─ DEPENDENCIES
│  │  │  ├─ depends_on: []                       ← No dependencies (first step)
│  │  │  └─ blocking: true                       ← Must complete before next
│  │  │
│  │  ├─ ERROR HANDLING
│  │  │  └─ retry_strategy:
│  │  │     ├─ max_retries: 0                    ← No retries for preflight
│  │  │     └─ fallback_action: "halt"           ← Halt if fails
│  │  │
│  │  └─ TIMING
│  │     ├─ timeout_seconds: 60
│  │     └─ estimated_duration: 30
│  │
│  │
│  ├─ STEP 1: User Input Processing
│  │  ├─ step: 1
│  │  ├─ name: "User Input Processing"
│  │  ├─ skill_reference: "path/to/step-01.md"
│  │  ├─ gate: "checkpoint_gate_1"
│  │  │
│  │  ├─ required_inputs:
│  │  │  └─ name: "validated_inputs"
│  │  │     ├─ type: "dict"
│  │  │     └─ source: "previous_step"           ← From Step 0 output
│  │  │
│  │  ├─ required_outputs:
│  │  │  ├─ name: "persona"
│  │  │  ├─ name: "url"
│  │  │  ├─ name: "workflow"
│  │  │  └─ name: "role_name"
│  │  │
│  │  ├─ depends_on: [0]                         ← Depends on Step 0
│  │  ├─ blocking: true
│  │  │
│  │  └─ retry_strategy:
│  │     ├─ max_retries: 3
│  │     └─ retry_with_guidance: true            ← Smart gate provides help
│  │
│  │
│  ├─ STEP 2: AI Processing
│  │  ├─ ...
│  │  └─ depends_on: [0, 1]                      ← Depends on Steps 0 and 1
│  │
│  │
│  ├─ STEP N-1: ...
│  │
│  │
│  └─ STEP N: Completion
│     ├─ step: 10
│     ├─ name: "Completion Validation"
│     ├─ gate: "completion_gate"
│     ├─ depends_on: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]  ← All previous steps
│     └─ ...
│
│
├─ GATE FAILURE STRATEGIES (How to handle failures)
│  ├─ preflight:
│  │  └─ action: "halt"                          ← Stop immediately
│  ├─ checkpoint:
│  │  ├─ action: "retry_with_guidance"           ← Provide help and retry
│  │  └─ max_retries: 3
│  └─ completion:
│     ├─ action: "halt"
│     └─ require_manual_review: true             ← Need human review
│
│
└─ AUDIT CONFIGURATION (What to track)
   ├─ track_gate_passage: true                   ← Log when gates pass
   ├─ store_checkpoint_state: true               ← Save state at each step
   ├─ log_retry_attempts: true                   ← Log retry attempts
   ├─ log_agent_actions: true                    ← Log agent behavior
   ├─ capture_intermediate_state: true           ← Save intermediate data
   ├─ output_directory: "tests/_audit/..."       ← Where to save
   └─ retention_days: 90                         ← How long to keep


┌─────────────────────────────────────────────────────────────────────────────┐
│                     STEP DEPENDENCY GRAPH                                   │
│                     (Built from protocol.workflow)                          │
└─────────────────────────────────────────────────────────────────────────────┘

Example: QA Test Generation (Sequential)

      Step 0 (depends_on: [])
         │
         ├─► outputs: {validated_inputs}
         │
         ▼
      Step 1 (depends_on: [0])
         │
         ├─► outputs: {persona, url, workflow, role_name}
         │
         ▼
      Step 2 (depends_on: [0, 1])
         │
         ├─► outputs: {bdd_scenarios, expected_states}
         │
         ▼
      Step 3 (depends_on: [0, 1, 2])
         │
         ├─► outputs: {test_scenarios}
         │
         ▼
      ...
         │
         ▼
      Step N (depends_on: [0,1,2,...,N-1])
         │
         └─► outputs: {final_result}


Example: Document Analysis (Parallel)

                  Step 0 (depends_on: [])
                     │
                     ├─► outputs: {document_content}
                     │
      ┌──────────────┼──────────────┬──────────────┐
      │              │              │              │
      ▼              ▼              ▼              ▼
   Step 1         Step 2         Step 3         Step 4
(depends:[0])  (depends:[0])  (depends:[0])  (depends:[0])
   │              │              │              │
   │              │              │              │ ALL PARALLEL
   │              │              │              │ (no dependencies on each other)
   │              │              │              │
   └──────────────┴──────────────┴──────────────┘
                     │
                     ├─► Step 5 (depends_on: [1,2,3,4])
                     │   (aggregation - requires ALL parallel steps)
                     │
                     └─► outputs: {analysis_report}
```

---

## 7. Vertical Integration Model

```
┌─────────────────────────────────────────────────────────────────────────────┐
│              HOW VERTICALS PLUG INTO THE PLATFORM                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│  PLATFORM CORE (isagawa_platform/)                                          │
│  ───────────────────────────────────────────────────────────────────────    │
│                                                                             │
│  ┌────────────────────────────────────────────────────────────┐            │
│  │  1. AgentOrchestrator (generic)                            │            │
│  │  2. ProtocolEngine (generic)                               │            │
│  │  3. BaseGate (abstract)                                    │            │
│  │  4. GateRegistry (pluggable)                               │            │
│  │  5. ExecutionTracker (generic)                             │            │
│  │  6. CheckpointManager (generic)                            │            │
│  └────────────────────────────────────────────────────────────┘            │
│                          ▲                                                  │
│                          │ Used by                                         │
│                          │                                                  │
└──────────────────────────┼──────────────────────────────────────────────────┘
                           │
                           │
    ┌──────────────────────┼──────────────────────┬──────────────────────────┐
    │                      │                      │                          │
    │                      │                      │                          │
┌───▼──────────────────────▼──────────────────────▼──────────────────────────┐
│                                                                             │
│  VERTICALS (domain-specific)                                               │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │  VERTICAL 1: QA Execution Engine                            │           │
│  │  ────────────────────────────────────────────────────        │           │
│  │                                                              │           │
│  │  What it provides:                                          │           │
│  │                                                              │           │
│  │  1. PROTOCOL DEFINITION                                     │           │
│  │     protocols/test_generation_agent.yaml                    │           │
│  │     • 10-step workflow                                      │           │
│  │     • Data contracts per step                               │           │
│  │     • Gate mappings                                         │           │
│  │                                                              │           │
│  │  2. CUSTOM GATES (extend BaseGate)                          │           │
│  │     gates/qg_test_agent_preflight.py                        │           │
│  │     gates/qg_test_agent_checkpoint_*.py                     │           │
│  │     gates/qg_test_agent_completion.py                       │           │
│  │     • QA-specific validation logic                          │           │
│  │     • Domain rules (DD-01, DD-24, etc.)                     │           │
│  │                                                              │           │
│  │  3. SKILLS (protocol guidance)                              │           │
│  │     skills/qa-guidance-layer/references/step-*.md           │           │
│  │     • Step-by-step instructions                             │           │
│  │     • QA best practices                                     │           │
│  │     • Framework patterns                                    │           │
│  │                                                              │           │
│  │  4. DOMAIN LOGIC                                            │           │
│  │     • 4-layer framework (Role→Task→Page→WebInterface)       │           │
│  │     • MCP tools (Tool 1-6)                                  │           │
│  │     • Test runner integration                               │           │
│  │                                                              │           │
│  │  5. AGENT EXECUTOR                                          │           │
│  │     def qa_agent_executor(step_config, guidance, inputs):   │           │
│  │       # Calls Claude API, Task tool, etc.                   │           │
│  │       # Returns agent output                                │           │
│  └─────────────────────────────────────────────────────────────┘           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │  VERTICAL 2: Customer Support                                │           │
│  │  ────────────────────────────────────────────────────        │           │
│  │                                                              │           │
│  │  What it provides:                                          │           │
│  │                                                              │           │
│  │  1. PROTOCOL DEFINITION                                     │           │
│  │     protocols/ticket_resolution_agent.yaml                  │           │
│  │     • 5-step workflow (intake → resolution)                 │           │
│  │     • Data contracts per step                               │           │
│  │     • Gate mappings                                         │           │
│  │                                                              │           │
│  │  2. CUSTOM GATES (extend BaseGate)                          │           │
│  │     gates/support_ticket_intake_gate.py                     │           │
│  │     gates/support_research_gate.py                          │           │
│  │     gates/support_response_gate.py                          │           │
│  │     gates/support_quality_gate.py                           │           │
│  │     • Support-specific validation                           │           │
│  │     • Quality standards                                     │           │
│  │     • Response tone checks                                  │           │
│  │                                                              │           │
│  │  3. SKILLS (protocol guidance)                              │           │
│  │     skills/support-guidance/                                │           │
│  │     • Ticket analysis best practices                        │           │
│  │     • Response templates                                    │           │
│  │     • Escalation criteria                                   │           │
│  │                                                              │           │
│  │  4. DOMAIN LOGIC                                            │           │
│  │     • Knowledge base integration                            │           │
│  │     • Ticket system API                                     │           │
│  │     • Response generation logic                             │           │
│  │                                                              │           │
│  │  5. AGENT EXECUTOR                                          │           │
│  │     def support_agent_executor(step_config, guidance, inputs):│         │
│  │       # Queries KB, generates response                      │           │
│  │       # Returns agent output                                │           │
│  └─────────────────────────────────────────────────────────────┘           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────┐           │
│  │  VERTICAL N: Your Custom Domain                             │           │
│  │  ────────────────────────────────────────────────────        │           │
│  │                                                              │           │
│  │  Just provide:                                              │           │
│  │  1. protocol.yaml → Define your workflow                    │           │
│  │  2. custom_gates.py → Extend BaseGate                       │           │
│  │  3. skills/ (optional) → Guidance documents                 │           │
│  │  4. domain logic → Your specific implementation             │           │
│  │  5. agent_executor → How agent performs work                │           │
│  │                                                              │           │
│  │  Platform handles:                                          │           │
│  │  ✓ Orchestration                                            │           │
│  │  ✓ Gate enforcement                                         │           │
│  │  ✓ State management                                         │           │
│  │  ✓ Audit trail                                              │           │
│  │  ✓ Retry logic                                              │           │
│  │  ✓ Checkpointing                                            │           │
│  └─────────────────────────────────────────────────────────────┘           │
└─────────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                                        │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1: Register Protocol
─────────────────────────────────────────────────────────────────────
from isagawa_platform.orchestration import ProtocolRegistry

protocol_registry = ProtocolRegistry()
protocol_registry.register(
    protocol_id="qa.test_generation.v1",
    yaml_path="verticals/qa_execution_engine/protocols/test_generation_agent.yaml"
)


Step 2: Register Gates
─────────────────────────────────────────────────────────────────────
from isagawa_platform.validation import GateRegistry
from verticals.qa_execution_engine.gates import *

gate_registry = GateRegistry()
gate_registry.register("qg_test_agent_preflight", QAPreflightGate)
gate_registry.register("qg_test_agent_checkpoint_1", QACheckpoint1Gate)
# ... register all gates


Step 3: Define Agent Executor
─────────────────────────────────────────────────────────────────────
def qa_agent_executor(step_config, guidance, inputs):
    """
    How the QA agent performs work at each step.

    This is domain-specific - you implement this for your vertical.
    """
    # Your implementation:
    # - Call Claude API
    # - Use Task tool
    # - Execute domain logic
    # - Return agent output

    return agent_output


Step 4: Initialize Orchestrator
─────────────────────────────────────────────────────────────────────
from isagawa_platform.orchestration import AgentOrchestrator

orchestrator = AgentOrchestrator(
    protocol_id="qa.test_generation.v1",
    agent_id="qa_agent_001",
    agent_executor=qa_agent_executor,
    protocol_registry=protocol_registry
)


Step 5: Execute Workflow
─────────────────────────────────────────────────────────────────────
result = orchestrator.execute_workflow(
    initial_inputs={
        "user_requirement": "As a registered user, I want to purchase a product",
        "target_url": "http://www.automationpractice.pl"
    }
)

# Platform handles:
# ✓ Loading protocol
# ✓ Executing steps in order
# ✓ Validating with gates
# ✓ Tracking execution
# ✓ Managing state
# ✓ Providing guidance on failures
```

---

## 8. Audit Trail Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          AUDIT TRAIL OUTPUT                                 │
│              (Saved to tests/_audit/agent_executions/)                      │
└─────────────────────────────────────────────────────────────────────────────┘

execution_qa_agent_001_2026-01-12T10-30-00.json
{
  "execution_id": "qa_agent_001_2026-01-12T10-30-00",
  "agent_id": "qa_agent_001",
  "protocol_id": "qa.test_generation.v1",
  "protocol_version": "1.0.0",

  "start_time": "2026-01-12T10:30:00.000Z",
  "end_time": "2026-01-12T10:35:45.123Z",
  "duration_seconds": 345.123,
  "status": "SUCCESS",

  "initial_inputs": {
    "user_requirement": "As a registered user, I want to purchase a product",
    "target_url": "http://www.automationpractice.pl"
  },

  "final_outputs": {
    "test_file_path": "tests/auth/test_purchase_product.py",
    "test_passed": true,
    "all_artifacts_saved": true
  },

  "events": [
    {
      "timestamp": "2026-01-12T10:30:00.001Z",
      "event": "execution_start",
      "details": {
        "protocol_id": "qa.test_generation.v1",
        "agent_id": "qa_agent_001"
      }
    },
    {
      "timestamp": "2026-01-12T10:30:01.234Z",
      "event": "step_start",
      "step": 0,
      "step_name": "Preflight",
      "details": {}
    },
    {
      "timestamp": "2026-01-12T10:30:05.567Z",
      "event": "gate_pass",
      "step": 0,
      "gate": "qg_test_agent_preflight",
      "validation_result": {
        "status": "PASS",
        "checks_performed": [
          "MCP servers running",
          "Test directory exists",
          "URL accessible"
        ]
      }
    },
    {
      "timestamp": "2026-01-12T10:30:05.789Z",
      "event": "checkpoint_saved",
      "step": 0,
      "checkpoint_id": "qa_agent_001_step_0_2026-01-12T10-30-05"
    },
    {
      "timestamp": "2026-01-12T10:30:06.000Z",
      "event": "step_start",
      "step": 1,
      "step_name": "User Input Processing"
    },
    {
      "timestamp": "2026-01-12T10:30:10.123Z",
      "event": "gate_fail",
      "step": 1,
      "gate": "qg_test_agent_checkpoint_1",
      "validation_result": {
        "status": "NEEDS_RETRY",
        "message": "Missing required field: credential_strategy",
        "missing_fields": ["credential_strategy"]
      }
    },
    {
      "timestamp": "2026-01-12T10:30:10.124Z",
      "event": "retry",
      "step": 1,
      "retry_count": 1,
      "message": "Retrying with guidance for missing fields",
      "guidance_provided": {
        "credential_strategy": {
          "description": "How test handles credentials (DD-24)",
          "options": ["static", "dynamic", "self-contained", "none"]
        }
      }
    },
    {
      "timestamp": "2026-01-12T10:30:15.456Z",
      "event": "gate_pass",
      "step": 1,
      "gate": "qg_test_agent_checkpoint_1",
      "validation_result": {
        "status": "PASS",
        "retry_count": 1
      }
    },
    {
      "timestamp": "2026-01-12T10:30:15.678Z",
      "event": "checkpoint_saved",
      "step": 1,
      "checkpoint_id": "qa_agent_001_step_1_2026-01-12T10-30-15"
    },
    // ... events for steps 2-9 ...
    {
      "timestamp": "2026-01-12T10:35:40.000Z",
      "event": "step_start",
      "step": 10,
      "step_name": "Completion Validation"
    },
    {
      "timestamp": "2026-01-12T10:35:45.000Z",
      "event": "gate_pass",
      "step": 10,
      "gate": "qg_test_agent_completion",
      "validation_result": {
        "status": "PASS",
        "checks_performed": [
          "All files saved",
          "Test executed",
          "Test passed",
          "Audit trail complete"
        ]
      }
    },
    {
      "timestamp": "2026-01-12T10:35:45.123Z",
      "event": "execution_end",
      "status": "SUCCESS",
      "duration_seconds": 345.123
    }
  ],

  "statistics": {
    "total_steps": 11,
    "steps_completed": 11,
    "gates_passed": 11,
    "gates_failed": 0,
    "total_retries": 1,
    "checkpoints_saved": 11
  },

  "execution_state_snapshots": {
    "step_0": {
      "validated_inputs": {...},
      "execution_context": {...}
    },
    "step_1": {
      "persona": "As a registered user",
      "url": "http://www.automationpractice.pl",
      "workflow": "auth",
      "role_name": "RegisteredUser",
      "credential_strategy": "static"
    },
    // ... snapshots for each step ...
  }
}
```

---

## 9. Platform Comparison

```
┌─────────────────────────────────────────────────────────────────────────────┐
│          ISAGAWA PLATFORM vs OTHER APPROACHES                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  WITHOUT ISAGAWA (Traditional Agent)                                   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  User Request → Agent (LLM) → Unstructured Work → Maybe Done?         │
│                       │                                                │
│                       ├─ Can skip steps                                │
│                       ├─ Can stop early                                │
│                       ├─ No validation                                 │
│                       ├─ No audit trail                                │
│                       └─ No guarantees                                 │
│                                                                        │
│  Problems:                                                             │
│  ✗ Inconsistent results                                               │
│  ✗ No way to enforce process                                          │
│  ✗ Can't resume on failure                                            │
│  ✗ No visibility into what agent did                                  │
│  ✗ Hallucinations unchecked                                           │
└────────────────────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────────────────────┐
│  WITH ISAGAWA (Governed Agent)                                         │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  User Request → Protocol → Orchestrator → Step 1 → Gate 1 →           │
│                              │              ▼        ▼                 │
│                              │            Step 2 → Gate 2 →            │
│                              │              ▼        ▼                 │
│                              │            Step N → Gate N →            │
│                              │              ▼        ▼                 │
│                              │         Completion → Done ✓             │
│                              │                                         │
│                              ├─ Cannot skip steps (enforced)           │
│                              ├─ Cannot stop early (gates block)        │
│                              ├─ Every step validated                   │
│                              ├─ Complete audit trail                   │
│                              └─ Success guaranteed or clear failure    │
│                                                                        │
│  Benefits:                                                             │
│  ✓ Consistent, repeatable results                                     │
│  ✓ Process enforced by infrastructure                                 │
│  ✓ Resume from any checkpoint                                         │
│  ✓ Complete visibility (audit trail)                                  │
│  ✓ Smart gates catch/fix hallucinations                               │
└────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────────┐
│                     FEATURE COMPARISON TABLE                                │
├────────────────┬─────────────────────┬─────────────────────┬────────────────┤
│ Feature        │ Traditional Agent   │ Prompt Engineering  │ Isagawa        │
├────────────────┼─────────────────────┼─────────────────────┼────────────────┤
│ Step Sequence  │ Suggested           │ Suggested           │ Enforced       │
│ Validation     │ None                │ Self-check          │ Independent    │
│ Audit Trail    │ None                │ None                │ Complete       │
│ Resume         │ No                  │ No                  │ Yes (checkp.)  │
│ Guidance       │ None                │ In prompt           │ Smart gates    │
│ Retry Logic    │ Ad-hoc              │ Ad-hoc              │ Structured     │
│ Multi-domain   │ No                  │ No                  │ Yes (YAML)     │
│ Guarantees     │ None                │ None                │ Strong         │
│ Visibility     │ Low                 │ Low                 │ Complete       │
└────────────────┴─────────────────────┴─────────────────────┴────────────────┘
```

---

This comprehensive visual documentation covers:
1. Platform overview and component relationships
2. Detailed core component architecture
3. Complete data flow diagrams
4. Execution pattern comparisons
5. Smart gate validation flows
6. Protocol structure visualization
7. Vertical integration model
8. Audit trail structure
9. Platform comparison charts

All components are fully visualized showing inputs, outputs, responsibilities, and relationships.
