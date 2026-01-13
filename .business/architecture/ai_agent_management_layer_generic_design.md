# AI Agent Management Layer - Generic Design

**Date:** 2026-01-12
**Status:** Design Concept - Domain-Agnostic Platform
**Purpose:** Reusable infrastructure for governing ANY multi-step AI agent workflow

---

## Platform Vision

**The Isagawa AI Agent Management Layer is domain-agnostic infrastructure that enforces how AI agents execute multi-step workflows through:**

1. **Protocol Definitions** - YAML files that define workflow steps, contracts, and validation rules
2. **Smart Gates** - Validation checkpoints that provide guidance, not just blocking
3. **Orchestration Engine** - Wrapper that enforces step sequence and state management
4. **Execution Tracking** - Complete audit trail of agent behavior

**This platform can manage:**
- QA test generation agents
- Customer support agents
- Document processing agents
- Data analysis agents
- Content generation agents
- ANY agent performing multi-step work

---

## System Architecture (Generic)

```
┌─────────────────────────────────────────────────────────────────────┐
│                   ISAGAWA PLATFORM LAYER                            │
│                   (Domain-Agnostic)                                 │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATION CORE                                                 │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  AgentOrchestrator (Generic)                               │   │
│  │  ─────────────────────────────────────────────────         │   │
│  │  • Loads protocol from registry                            │   │
│  │  • Enforces step sequence                                  │   │
│  │  • Manages execution state                                 │   │
│  │  • Handles gate validation                                 │   │
│  │  • Provides retry logic with guidance                      │   │
│  │  • Checkpoints state at each step                          │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              │ Uses                                 │
│                              ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  ProtocolEngine (Generic)                                  │   │
│  │  ─────────────────────────────────────────────────         │   │
│  │  • Parses protocol YAML                                    │   │
│  │  • Validates protocol schema                               │   │
│  │  • Resolves skill references                               │   │
│  │  • Builds step dependency graph                            │   │
│  │  • Determines execution pattern (sequential/parallel)      │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              │ Uses                                 │
│                              ▼                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  GateRegistry (Generic)                                    │   │
│  │  ─────────────────────────────────────────────────         │   │
│  │  • Registers gate implementations                          │   │
│  │  • Routes to correct gate based on protocol               │   │
│  │  • Supports pluggable gate modules                         │   │
│  │  • Provides gate discovery                                 │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  VALIDATION CORE                                                    │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  BaseGate (Abstract)                                       │   │
│  │  ─────────────────────────────────────────────────         │   │
│  │  • validate(input_data) → ValidationResult                 │   │
│  │  • provide_guidance(failure) → GuidancePackage             │   │
│  │  • check_required_fields(data, schema) → bool              │   │
│  │  • generate_fix_data(missing) → Dict                       │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│                              │ Extended By                          │
│                              ▼                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐    │
│  │  Preflight   │  │  Checkpoint  │  │  Completion          │    │
│  │  Gate        │  │  Gate        │  │  Gate                │    │
│  │  ────────    │  │  ────────    │  │  ────────            │    │
│  │  • Env check │  │  • Step I/O  │  │  • All steps done    │    │
│  │  • Resources │  │  • Metadata  │  │  • Artifacts present │    │
│  │  • Protocol  │  │  • Contract  │  │  • Audit complete    │    │
│  └──────────────┘  └──────────────┘  └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  STATE & AUDIT CORE                                                 │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  ExecutionTracker (Generic)                                │   │
│  │  ─────────────────────────────────────────────────         │   │
│  │  • start_execution(agent_id, protocol)                     │   │
│  │  • log_step_start/end(step, metadata)                      │   │
│  │  • log_gate_pass/fail/retry(gate, result)                  │   │
│  │  • log_agent_action(action, context)                       │   │
│  │  • end_execution(final_state)                              │   │
│  │  • export_audit_trail() → JSON                             │   │
│  └────────────────────────────────────────────────────────────┘   │
│                              │                                      │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  CheckpointManager (Generic)                               │   │
│  │  ─────────────────────────────────────────────────         │   │
│  │  • save_checkpoint(step, state)                            │   │
│  │  • load_checkpoint(execution_id, step) → State             │   │
│  │  • resume_execution(checkpoint_id) → State                 │   │
│  │  • cleanup_old_checkpoints(retention_days)                 │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│  PROTOCOL REGISTRY                                                  │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  ┌────────────────────────────────────────────────────────────┐   │
│  │  ProtocolRegistry (Generic)                                │   │
│  │  ─────────────────────────────────────────────────         │   │
│  │  • register_protocol(name, yaml_path)                      │   │
│  │  • get_protocol(name) → Protocol                           │   │
│  │  • list_protocols() → List[ProtocolMetadata]               │   │
│  │  • validate_protocol_schema(yaml) → ValidationResult       │   │
│  └────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

## File Structure (Generic Platform)

```
isagawa_platform/                    ← NEW: Domain-agnostic platform
├── __init__.py
│
├── orchestration/                   ← Core orchestration
│   ├── __init__.py
│   ├── agent_orchestrator.py       ← Generic agent wrapper
│   ├── protocol_engine.py          ← Protocol parser/executor
│   ├── protocol_registry.py        ← Protocol discovery/loading
│   └── execution_patterns.py       ← Assembly line, inspection team, hybrid
│
├── validation/                      ← Generic gate system
│   ├── __init__.py
│   ├── base_gate.py                ← Abstract base class
│   ├── gate_registry.py            ← Gate discovery/routing
│   ├── preflight_gate.py           ← Generic preflight validation
│   ├── checkpoint_gate.py          ← Generic step validation
│   ├── completion_gate.py          ← Generic completion validation
│   └── validation_result.py        ← Result schemas
│
├── state/                           ← State management
│   ├── __init__.py
│   ├── execution_tracker.py        ← Audit trail
│   ├── checkpoint_manager.py       ← State persistence
│   └── state_store.py              ← Pluggable storage (file, DB, S3)
│
├── protocols/                       ← Protocol schemas
│   ├── __init__.py
│   ├── protocol_schema.py          ← YAML schema definition
│   ├── protocol_validator.py       ← Schema validation
│   └── protocol_loader.py          ← YAML loading/parsing
│
├── skills/                          ← Skill management
│   ├── __init__.py
│   ├── skill_registry.py           ← Skill discovery
│   └── skill_loader.py             ← Load .md skill references
│
└── utils/                           ← Platform utilities
    ├── __init__.py
    ├── graph_builder.py            ← Build dependency graphs
    └── retry_handler.py            ← Smart retry logic


verticals/                           ← Domain-specific implementations
├── qa_execution_engine/            ← QA vertical (existing)
│   ├── protocols/
│   │   └── test_generation_agent.yaml
│   ├── gates/
│   │   ├── qg_test_agent_preflight.py
│   │   ├── qg_test_agent_checkpoint_*.py
│   │   └── qg_test_agent_completion.py
│   └── skills/
│       └── qa-guidance-layer/      ← Existing skills
│
├── customer_support/               ← Example: Customer support vertical
│   ├── protocols/
│   │   └── ticket_resolution_agent.yaml
│   ├── gates/
│   │   ├── qg_support_ticket_intake.py
│   │   ├── qg_support_research.py
│   │   └── qg_support_response.py
│   └── skills/
│       └── support-guidance/
│
└── document_processing/            ← Example: Document processing vertical
    ├── protocols/
    │   └── document_analysis_agent.yaml
    ├── gates/
    │   ├── qg_doc_intake.py
    │   ├── qg_doc_extraction.py
    │   └── qg_doc_output.py
    └── skills/
        └── document-guidance/
```

---

## Generic Protocol Schema

```yaml
# isagawa_platform/protocols/protocol_schema.yaml
# ═══════════════════════════════════════════════════════════════

# PROTOCOL METADATA
protocol_name: string               # Human-readable name
protocol_id: string                 # Unique identifier
protocol_version: string            # Semantic version
domain: string                      # Domain/vertical (qa, support, doc_processing)
description: string                 # What this agent does

# EXECUTION CONFIGURATION
execution:
  pattern: enum                     # assembly_line | inspection_team | hybrid
  parallelization: bool             # Can steps run in parallel?
  timeout_seconds: int              # Max execution time
  allow_resume: bool                # Can execution resume from checkpoint?

# WORKFLOW DEFINITION
workflow:
  - step: int                       # Step number (0-indexed)
    name: string                    # Step name
    description: string             # What this step does

    # SKILL REFERENCE (if using Skills as protocols)
    skill_reference: string         # Path to .md skill file (optional)

    # OR INLINE INSTRUCTIONS
    instructions: string            # Inline instructions (optional)

    # GATE VALIDATION
    gate: string                    # Gate identifier (maps to GateRegistry)
    gate_config:                    # Gate-specific configuration
      validation_rules: dict
      custom_params: dict

    # DATA CONTRACTS
    required_inputs:                # What this step needs
      - name: string
        type: string                # string | int | bool | dict | list
        source: string              # previous_step | user_input | environment
        validation: dict            # Custom validation rules

    required_outputs:               # What this step must produce
      - name: string
        type: string
        validation: dict

    # DEPENDENCIES
    depends_on: list[int]           # Step numbers this depends on
    blocking: bool                  # Must complete before next step?

    # ERROR HANDLING
    retry_strategy:
      max_retries: int
      retry_with_guidance: bool
      fallback_action: string       # skip | halt | use_default

    # TIMING
    timeout_seconds: int            # Step-level timeout
    estimated_duration: int         # For progress tracking

# GATE FAILURE STRATEGIES
gate_failure_strategies:
  preflight:
    action: halt                    # halt | warn | skip
    notify: bool
  checkpoint:
    action: retry_with_guidance
    max_retries: 3
    escalate_after: 2
  completion:
    action: halt
    require_manual_review: bool

# AUDIT CONFIGURATION
audit:
  track_gate_passage: bool
  store_checkpoint_state: bool
  log_retry_attempts: bool
  log_agent_actions: bool
  capture_intermediate_state: bool
  output_directory: string
  retention_days: int

# VALIDATION RULES (protocol-level)
validation:
  required_environment_vars: list[string]
  required_resources: list[string]
  required_mcp_tools: list[string]

# METADATA
metadata:
  author: string
  created_date: string
  last_modified: string
  tags: list[string]
```

---

## Generic Protocol Examples

### Example 1: QA Test Generation Agent

```yaml
# verticals/qa_execution_engine/protocols/test_generation_agent.yaml

protocol_name: "QA Test Generation Agent"
protocol_id: "qa.test_generation.v1"
protocol_version: "1.0.0"
domain: "qa_automation"
description: "Generates end-to-end test code from user requirements"

execution:
  pattern: assembly_line
  parallelization: false
  timeout_seconds: 1800
  allow_resume: true

workflow:
  - step: 0
    name: "Preflight"
    description: "Validate environment and gather inputs"
    skill_reference: ".claude/skills/qa-guidance-layer/references/step-01.md"
    gate: "preflight_gate"
    gate_config:
      validation_rules:
        check_mcp_servers: ["playwright", "qa-automation"]
        check_environment: ["tests directory exists"]
    required_inputs:
      - name: "user_requirement"
        type: "string"
        source: "user_input"
      - name: "target_url"
        type: "string"
        source: "user_input"
        validation:
          format: "url"
    required_outputs:
      - name: "validated_inputs"
        type: "dict"
      - name: "execution_context"
        type: "dict"
    depends_on: []
    blocking: true
    retry_strategy:
      max_retries: 0
      fallback_action: "halt"

  - step: 1
    name: "User Input Processing"
    description: "Extract persona, URL, workflow domain"
    skill_reference: ".claude/skills/qa-guidance-layer/references/step-01.md"
    gate: "checkpoint_gate_1"
    required_inputs:
      - name: "validated_inputs"
        type: "dict"
        source: "previous_step"
    required_outputs:
      - name: "persona"
        type: "string"
      - name: "url"
        type: "string"
      - name: "workflow"
        type: "string"
      - name: "role_name"
        type: "string"
    depends_on: [0]
    blocking: true
    retry_strategy:
      max_retries: 3
      retry_with_guidance: true

  # ... steps 2-9 ...

  - step: 10
    name: "Completion Validation"
    description: "Verify all files saved and test passed"
    gate: "completion_gate"
    required_inputs:
      - name: "all_previous_outputs"
        type: "dict"
        source: "execution_state"
    required_outputs:
      - name: "execution_summary"
        type: "dict"
    depends_on: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    blocking: true

gate_failure_strategies:
  preflight:
    action: halt
  checkpoint:
    action: retry_with_guidance
    max_retries: 3
  completion:
    action: halt

audit:
  track_gate_passage: true
  store_checkpoint_state: true
  log_retry_attempts: true
  output_directory: "tests/_audit/agent_executions/"
  retention_days: 90
```

### Example 2: Customer Support Ticket Resolution Agent

```yaml
# verticals/customer_support/protocols/ticket_resolution_agent.yaml

protocol_name: "Customer Support Ticket Resolution Agent"
protocol_id: "support.ticket_resolution.v1"
protocol_version: "1.0.0"
domain: "customer_support"
description: "Processes customer support tickets from intake to resolution"

execution:
  pattern: assembly_line
  parallelization: false
  timeout_seconds: 600
  allow_resume: true

workflow:
  - step: 0
    name: "Ticket Intake"
    description: "Parse ticket, extract customer info, categorize issue"
    instructions: |
      1. Extract customer name, email, account ID
      2. Parse ticket subject and body
      3. Categorize: billing | technical | product_question | other
      4. Determine urgency: critical | high | medium | low
    gate: "support_ticket_intake_gate"
    required_inputs:
      - name: "raw_ticket"
        type: "dict"
        source: "user_input"
    required_outputs:
      - name: "customer_info"
        type: "dict"
      - name: "issue_category"
        type: "string"
      - name: "urgency"
        type: "string"
      - name: "ticket_summary"
        type: "string"
    depends_on: []
    blocking: true

  - step: 1
    name: "Knowledge Base Search"
    description: "Search for relevant articles and past tickets"
    instructions: |
      1. Query knowledge base with issue keywords
      2. Find similar resolved tickets
      3. Identify potential solutions
    gate: "support_research_gate"
    required_inputs:
      - name: "issue_category"
        type: "string"
        source: "previous_step"
      - name: "ticket_summary"
        type: "string"
        source: "previous_step"
    required_outputs:
      - name: "relevant_articles"
        type: "list"
      - name: "similar_tickets"
        type: "list"
      - name: "suggested_solutions"
        type: "list"
    depends_on: [0]
    blocking: true

  - step: 2
    name: "Response Generation"
    description: "Generate response with solution and next steps"
    instructions: |
      1. Synthesize research findings
      2. Draft response in company tone
      3. Include step-by-step solution
      4. Add relevant knowledge base links
    gate: "support_response_gate"
    required_inputs:
      - name: "customer_info"
        type: "dict"
        source: "step_0"
      - name: "suggested_solutions"
        type: "list"
        source: "previous_step"
    required_outputs:
      - name: "response_draft"
        type: "string"
      - name: "solution_steps"
        type: "list"
      - name: "kb_links"
        type: "list"
    depends_on: [0, 1]
    blocking: true

  - step: 3
    name: "Quality Check"
    description: "Validate response meets quality standards"
    gate: "support_quality_gate"
    required_inputs:
      - name: "response_draft"
        type: "string"
        source: "previous_step"
    required_outputs:
      - name: "approved_response"
        type: "string"
      - name: "quality_score"
        type: "float"
    depends_on: [2]
    blocking: true

  - step: 4
    name: "Response Delivery"
    description: "Send response and log interaction"
    gate: "completion_gate"
    required_inputs:
      - name: "approved_response"
        type: "string"
        source: "previous_step"
    required_outputs:
      - name: "ticket_status"
        type: "string"
      - name: "response_sent"
        type: "bool"
    depends_on: [0, 1, 2, 3]
    blocking: true

gate_failure_strategies:
  preflight:
    action: halt
  checkpoint:
    action: retry_with_guidance
    max_retries: 2
  completion:
    action: halt
    require_manual_review: true

audit:
  track_gate_passage: true
  store_checkpoint_state: true
  log_retry_attempts: true
  log_agent_actions: true
  output_directory: "support/_audit/agent_executions/"
  retention_days: 365
```

### Example 3: Document Analysis Agent (Parallel Pattern)

```yaml
# verticals/document_processing/protocols/document_analysis_agent.yaml

protocol_name: "Document Analysis Agent"
protocol_id: "doc_proc.analysis.v1"
protocol_version: "1.0.0"
domain: "document_processing"
description: "Analyzes documents across multiple dimensions in parallel"

execution:
  pattern: inspection_team          # PARALLEL execution
  parallelization: true
  timeout_seconds: 900
  allow_resume: true

workflow:
  - step: 0
    name: "Document Intake"
    description: "Load and validate document"
    gate: "preflight_gate"
    required_inputs:
      - name: "document_path"
        type: "string"
        source: "user_input"
    required_outputs:
      - name: "document_content"
        type: "string"
      - name: "document_metadata"
        type: "dict"
    depends_on: []
    blocking: true

  # PARALLEL ANALYSIS STEPS (can run simultaneously)
  - step: 1
    name: "Sentiment Analysis"
    description: "Analyze document sentiment"
    gate: "sentiment_gate"
    required_inputs:
      - name: "document_content"
        type: "string"
        source: "step_0"
    required_outputs:
      - name: "sentiment_scores"
        type: "dict"
    depends_on: [0]
    blocking: false               # Non-blocking (can run in parallel)

  - step: 2
    name: "Entity Extraction"
    description: "Extract named entities"
    gate: "entity_gate"
    required_inputs:
      - name: "document_content"
        type: "string"
        source: "step_0"
    required_outputs:
      - name: "entities"
        type: "list"
    depends_on: [0]
    blocking: false               # Non-blocking (can run in parallel)

  - step: 3
    name: "Topic Classification"
    description: "Classify document topics"
    gate: "topic_gate"
    required_inputs:
      - name: "document_content"
        type: "string"
        source: "step_0"
    required_outputs:
      - name: "topics"
        type: "list"
    depends_on: [0]
    blocking: false               # Non-blocking (can run in parallel)

  - step: 4
    name: "Language Detection"
    description: "Detect document language"
    gate: "language_gate"
    required_inputs:
      - name: "document_content"
        type: "string"
        source: "step_0"
    required_outputs:
      - name: "language"
        type: "string"
    depends_on: [0]
    blocking: false               # Non-blocking (can run in parallel)

  # AGGREGATION STEP (requires all parallel steps)
  - step: 5
    name: "Analysis Aggregation"
    description: "Combine all analysis results"
    gate: "completion_gate"
    required_inputs:
      - name: "sentiment_scores"
        type: "dict"
        source: "step_1"
      - name: "entities"
        type: "list"
        source: "step_2"
      - name: "topics"
        type: "list"
        source: "step_3"
      - name: "language"
        type: "string"
        source: "step_4"
    required_outputs:
      - name: "analysis_report"
        type: "dict"
    depends_on: [1, 2, 3, 4]      # Requires ALL parallel steps
    blocking: true

gate_failure_strategies:
  preflight:
    action: halt
  checkpoint:
    action: retry_with_guidance
    max_retries: 2
  completion:
    action: halt

audit:
  track_gate_passage: true
  store_checkpoint_state: true
  output_directory: "documents/_audit/agent_executions/"
  retention_days: 180
```

---

## Core Platform Components (Implementation Details)

### 1. AgentOrchestrator (Generic)

```python
# isagawa_platform/orchestration/agent_orchestrator.py

from typing import Dict, Any, Optional, Callable
from .protocol_engine import ProtocolEngine
from ..state.execution_tracker import ExecutionTracker
from ..state.checkpoint_manager import CheckpointManager
from ..validation.gate_registry import GateRegistry

class AgentOrchestrator:
    """
    Generic orchestrator for ANY agent workflow.

    Domain-agnostic - works with any protocol definition.
    """

    def __init__(
        self,
        protocol_id: str,
        agent_id: str,
        agent_executor: Callable,  # Function that executes agent work
        protocol_registry: 'ProtocolRegistry'
    ):
        """
        Initialize orchestrator.

        Args:
            protocol_id: Identifier for protocol to load
            agent_id: Unique identifier for this agent instance
            agent_executor: Callable that executes agent work
            protocol_registry: Registry to load protocols from
        """
        self.protocol = protocol_registry.get_protocol(protocol_id)
        self.engine = ProtocolEngine(self.protocol)
        self.tracker = ExecutionTracker(agent_id, protocol_id)
        self.checkpoint_mgr = CheckpointManager(agent_id)
        self.gate_registry = GateRegistry()
        self.agent_executor = agent_executor

        self.current_step = 0
        self.execution_state = {}

    def execute_workflow(
        self,
        initial_inputs: Dict[str, Any],
        resume_from_checkpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute complete workflow with gate enforcement.

        This is domain-agnostic - works for QA, support, docs, etc.
        """
        # Resume from checkpoint if provided
        if resume_from_checkpoint:
            return self._resume_execution(resume_from_checkpoint)

        # Start fresh execution
        self.tracker.start_execution(initial_inputs)
        self.execution_state = initial_inputs.copy()

        try:
            # Get execution pattern from protocol
            pattern = self.protocol.execution.pattern

            if pattern == "assembly_line":
                return self._execute_sequential()
            elif pattern == "inspection_team":
                return self._execute_parallel()
            elif pattern == "hybrid":
                return self._execute_hybrid()
            else:
                raise ValueError(f"Unknown execution pattern: {pattern}")

        except Exception as e:
            self.tracker.log_error(self.current_step, str(e))
            raise

    def _execute_sequential(self) -> Dict[str, Any]:
        """
        Execute workflow sequentially (assembly line pattern).
        """
        steps = self.engine.get_workflow_steps()

        for step_config in steps:
            # Enforce step sequence
            if step_config.step != self.current_step:
                raise GateViolationError(
                    f"Step sequence violation: Expected {self.current_step}, "
                    f"got {step_config.step}"
                )

            # Execute step with gate
            result = self._execute_step_with_gate(step_config)

            if result.status == "FAILED":
                return self._handle_failure(step_config, result)

            # Update state
            self.execution_state.update(result.outputs)
            self.current_step += 1

            # Checkpoint
            self.checkpoint_mgr.save_checkpoint(
                step=self.current_step,
                state=self.execution_state
            )

        # Completion validation
        completion_result = self._validate_completion()
        self.tracker.end_execution(completion_result)

        return {
            "status": "SUCCESS",
            "execution_state": self.execution_state,
            "audit_trail": self.tracker.get_audit_trail()
        }

    def _execute_parallel(self) -> Dict[str, Any]:
        """
        Execute workflow with parallel steps (inspection team pattern).

        Steps with blocking=false can run in parallel.
        """
        steps = self.engine.get_workflow_steps()
        dependency_graph = self.engine.build_dependency_graph()

        # Execute steps in dependency order, parallelizing where possible
        completed_steps = set()

        while len(completed_steps) < len(steps):
            # Find steps whose dependencies are satisfied
            ready_steps = [
                step for step in steps
                if step.step not in completed_steps
                and all(dep in completed_steps for dep in step.depends_on)
            ]

            if not ready_steps:
                raise RuntimeError("Circular dependency detected in workflow")

            # Separate blocking from non-blocking
            blocking_steps = [s for s in ready_steps if s.blocking]
            parallel_steps = [s for s in ready_steps if not s.blocking]

            # Execute parallel steps concurrently
            if parallel_steps:
                parallel_results = self._execute_parallel_batch(parallel_steps)
                for step, result in parallel_results.items():
                    if result.status == "FAILED":
                        return self._handle_failure(step, result)
                    self.execution_state.update(result.outputs)
                    completed_steps.add(step.step)

            # Execute blocking steps sequentially
            for step in blocking_steps:
                result = self._execute_step_with_gate(step)
                if result.status == "FAILED":
                    return self._handle_failure(step, result)
                self.execution_state.update(result.outputs)
                completed_steps.add(step.step)

        # Completion validation
        completion_result = self._validate_completion()
        self.tracker.end_execution(completion_result)

        return {
            "status": "SUCCESS",
            "execution_state": self.execution_state,
            "audit_trail": self.tracker.get_audit_trail()
        }

    def _execute_step_with_gate(self, step_config) -> 'StepResult':
        """
        Execute single step with gate validation.

        Domain-agnostic - works for any step type.
        """
        self.tracker.log_step_start(step_config.step, step_config.name)

        # Load guidance (skill reference or inline instructions)
        guidance = self._load_guidance(step_config)

        # Build inputs from execution state
        step_inputs = self._build_step_inputs(step_config)

        # Retry loop
        retry_count = 0
        max_retries = step_config.retry_strategy.max_retries

        while retry_count <= max_retries:
            # Agent performs work
            agent_output = self.agent_executor(
                step_config=step_config,
                guidance=guidance,
                inputs=step_inputs
            )

            # Gate validation
            gate = self.gate_registry.get_gate(step_config.gate)
            gate_result = gate.validate(
                step_config=step_config,
                agent_output=agent_output,
                execution_state=self.execution_state
            )

            if gate_result.status == "PASS":
                self.tracker.log_gate_pass(step_config.step, step_config.gate)
                return StepResult(
                    status="SUCCESS",
                    outputs=gate_result.outputs
                )

            elif gate_result.status == "NEEDS_RETRY":
                retry_count += 1
                self.tracker.log_retry(
                    step_config.step,
                    retry_count,
                    gate_result.message
                )

                # Smart gate provides guidance
                step_inputs = self._merge_guidance(
                    step_inputs,
                    gate_result.guidance
                )

            else:  # FAIL
                self.tracker.log_gate_fail(
                    step_config.step,
                    step_config.gate,
                    gate_result.message
                )
                return StepResult(
                    status="FAILED",
                    error=gate_result.message
                )

        # Max retries exceeded
        return StepResult(
            status="FAILED",
            error=f"Max retries ({max_retries}) exceeded"
        )

    def _load_guidance(self, step_config) -> str:
        """
        Load guidance from skill reference or inline instructions.
        """
        if step_config.skill_reference:
            # Load from .md file
            from ..skills.skill_loader import SkillLoader
            return SkillLoader.load(step_config.skill_reference)
        elif step_config.instructions:
            # Use inline instructions
            return step_config.instructions
        else:
            return ""

    def _build_step_inputs(self, step_config) -> Dict[str, Any]:
        """
        Build input data for step from execution state.
        """
        inputs = {}

        for required_input in step_config.required_inputs:
            if required_input.source == "previous_step":
                # Get from execution state
                inputs[required_input.name] = self.execution_state.get(
                    required_input.name
                )
            elif required_input.source == "user_input":
                # Already in execution state from initial inputs
                inputs[required_input.name] = self.execution_state.get(
                    required_input.name
                )
            elif required_input.source.startswith("step_"):
                # Get from specific step output
                step_num = int(required_input.source.split("_")[1])
                # Retrieve from checkpoint or execution state
                inputs[required_input.name] = self.execution_state.get(
                    required_input.name
                )

        return inputs

    def _validate_completion(self) -> Dict[str, Any]:
        """
        Final validation that workflow completed correctly.
        """
        completion_step = self.engine.get_completion_step()
        gate = self.gate_registry.get_gate(completion_step.gate)

        return gate.validate(
            step_config=completion_step,
            agent_output=self.execution_state,
            execution_state=self.execution_state
        )


class GateViolationError(Exception):
    """Raised when agent attempts to bypass gate enforcement."""
    pass


class StepResult:
    """Result of step execution."""
    def __init__(self, status: str, outputs: Dict = None, error: str = None):
        self.status = status
        self.outputs = outputs or {}
        self.error = error
```

### 2. BaseGate (Abstract)

```python
# isagawa_platform/validation/base_gate.py

from abc import ABC, abstractmethod
from typing import Dict, Any
from .validation_result import ValidationResult

class BaseGate(ABC):
    """
    Abstract base class for all quality gates.

    Domain-agnostic - subclasses implement domain-specific validation.
    """

    def __init__(self, gate_id: str):
        self.gate_id = gate_id

    @abstractmethod
    def validate(
        self,
        step_config: 'StepConfig',
        agent_output: Dict[str, Any],
        execution_state: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate step output against protocol requirements.

        Must return:
        - PASS: Validation successful, proceed
        - NEEDS_RETRY: Validation failed, but retryable with guidance
        - FAIL: Validation failed, halt execution
        """
        pass

    def check_required_fields(
        self,
        data: Dict[str, Any],
        required_fields: list
    ) -> tuple[bool, list]:
        """
        Generic field presence check.
        """
        missing = []
        for field in required_fields:
            if field.name not in data or not data[field.name]:
                missing.append(field.name)

        return (len(missing) == 0, missing)

    def provide_guidance(
        self,
        missing_fields: list,
        step_config: 'StepConfig'
    ) -> Dict[str, Any]:
        """
        Generate guidance for missing/invalid fields.
        """
        guidance = {}

        for field_name in missing_fields:
            # Find field definition in step config
            field_def = next(
                (f for f in step_config.required_outputs if f.name == field_name),
                None
            )

            if field_def:
                guidance[field_name] = {
                    "description": f"Required field: {field_name}",
                    "type": field_def.type,
                    "validation": field_def.validation
                }

        return guidance

    def generate_fix_data(
        self,
        missing_fields: list,
        execution_state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Smart gate: Generate fix data for missing fields.

        Subclasses override to provide domain-specific fixes.
        """
        return {}
```

### 3. GateRegistry

```python
# isagawa_platform/validation/gate_registry.py

from typing import Dict, Type
from .base_gate import BaseGate

class GateRegistry:
    """
    Registry for gate implementations.

    Allows pluggable gates per domain/vertical.
    """

    def __init__(self):
        self._gates: Dict[str, BaseGate] = {}

    def register(self, gate_id: str, gate_class: Type[BaseGate]):
        """Register a gate implementation."""
        self._gates[gate_id] = gate_class(gate_id)

    def get_gate(self, gate_id: str) -> BaseGate:
        """Get gate by identifier."""
        if gate_id not in self._gates:
            raise ValueError(f"Unknown gate: {gate_id}")
        return self._gates[gate_id]

    def list_gates(self) -> list:
        """List all registered gates."""
        return list(self._gates.keys())

    def unregister(self, gate_id: str):
        """Unregister a gate."""
        if gate_id in self._gates:
            del self._gates[gate_id]


# Global registry instance
_gate_registry = GateRegistry()

def register_gate(gate_id: str, gate_class: Type[BaseGate]):
    """Convenience function to register gates."""
    _gate_registry.register(gate_id, gate_class)

def get_gate_registry() -> GateRegistry:
    """Get global gate registry."""
    return _gate_registry
```

---

## Usage Examples

### Example 1: QA Agent (Existing Vertical)

```python
from isagawa_platform.orchestration import AgentOrchestrator, ProtocolRegistry
from isagawa_platform.validation import GateRegistry
from verticals.qa_execution_engine.gates import *

# Register QA-specific gates
gate_registry = GateRegistry()
gate_registry.register("qg_test_agent_preflight", QAPreflightGate)
gate_registry.register("qg_test_agent_checkpoint_1", QACheckpoint1Gate)
# ... register remaining gates

# Register protocol
protocol_registry = ProtocolRegistry()
protocol_registry.register(
    "qa.test_generation.v1",
    "verticals/qa_execution_engine/protocols/test_generation_agent.yaml"
)

# Define agent executor (how agent does work)
def qa_agent_executor(step_config, guidance, inputs):
    """Execute QA test generation step."""
    # Call Claude API, Task tool, or other execution method
    # Return agent output
    pass

# Initialize orchestrator
orchestrator = AgentOrchestrator(
    protocol_id="qa.test_generation.v1",
    agent_id="qa_agent_001",
    agent_executor=qa_agent_executor,
    protocol_registry=protocol_registry
)

# Execute workflow
result = orchestrator.execute_workflow(
    initial_inputs={
        "user_requirement": "As a registered user, I want to purchase a product",
        "target_url": "http://www.automationpractice.pl"
    }
)

print(result["status"])  # SUCCESS | FAILED
print(result["audit_trail"])
```

### Example 2: Customer Support Agent (New Vertical)

```python
from isagawa_platform.orchestration import AgentOrchestrator, ProtocolRegistry
from isagawa_platform.validation import GateRegistry
from verticals.customer_support.gates import *

# Register support-specific gates
gate_registry = GateRegistry()
gate_registry.register("support_ticket_intake_gate", TicketIntakeGate)
gate_registry.register("support_research_gate", ResearchGate)
gate_registry.register("support_response_gate", ResponseGate)
gate_registry.register("support_quality_gate", QualityCheckGate)

# Register protocol
protocol_registry = ProtocolRegistry()
protocol_registry.register(
    "support.ticket_resolution.v1",
    "verticals/customer_support/protocols/ticket_resolution_agent.yaml"
)

# Define agent executor
def support_agent_executor(step_config, guidance, inputs):
    """Execute support ticket resolution step."""
    # Call LLM, knowledge base API, etc.
    pass

# Initialize orchestrator
orchestrator = AgentOrchestrator(
    protocol_id="support.ticket_resolution.v1",
    agent_id="support_agent_001",
    agent_executor=support_agent_executor,
    protocol_registry=protocol_registry
)

# Execute workflow
result = orchestrator.execute_workflow(
    initial_inputs={
        "raw_ticket": {
            "from": "customer@example.com",
            "subject": "Cannot access account",
            "body": "I'm getting an error when trying to login..."
        }
    }
)
```

---

## Key Characteristics of Generic Design

| Aspect | Generic Platform | Vertical-Specific |
|--------|-----------------|-------------------|
| **Core Components** | AgentOrchestrator, ProtocolEngine, GateRegistry, ExecutionTracker | Domain logic, custom gates, protocols |
| **Reusability** | 100% reusable across domains | Domain-specific, not reusable |
| **Configuration** | YAML protocol definitions | Gate implementations, skill references |
| **Extensibility** | Pluggable gates, protocols, execution patterns | Subclass BaseGate, add protocols |
| **Installation** | `pip install isagawa-platform` | `pip install isagawa-qa` or custom |

---

## Competitive Advantages

**Generic AI Agent Management Layer provides:**

1. **Domain-Agnostic** - Works for QA, support, docs, analysis, etc.
2. **Protocol-Driven** - Declarative YAML, not code
3. **Smart Gates** - Provide guidance, not just blocking
4. **Execution Patterns** - Sequential, parallel, hybrid
5. **Complete Audit** - Every gate passage logged
6. **Resume Capability** - Checkpoint-based resumption
7. **Pluggable** - Add new domains without changing platform

**This is infrastructure for ANY multi-step agent workflow.**
