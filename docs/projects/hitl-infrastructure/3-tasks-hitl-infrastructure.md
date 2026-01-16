# Task List: HITL Infrastructure MVP

**PRD:** `2-prd-hitl-infrastructure.md` (v4.0)
**Design Doc:** `1-design-hitl-infrastructure.md` (sections 11-15 - latest design decisions)
**Status:** Phase 3 - Ready for Phase 4 (Deliver)
**Timeline:** 2-3 weeks (updated based on component reuse analysis)
**Last Updated:** 2026-01-15

---

## Design Decisions Reflected in Tasks

**Critical Context:**
1. **Checkpoint Workflow:** Synchronous return + AI orchestration (Design Decision 11)
2. **Approval Mode:** Conversational MVP only, CLI/Web UI stubbed (Design Decision 12)
3. **Target Audience:** Claude Code users (Design Decision 13)
4. **Component Reuse:** 90%+ from QA Engine, 2-3 days adaptation (Design Decision 14)
5. **Protocol System:** YAML + markdown with examples (Design Decision 15)

---

## Relevant Files

### Test Infrastructure (Task 0.0)
- `hitl_server/pytest.ini` - Pytest configuration with HTML reporting and coverage
- `hitl_server/requirements.txt` - Python dependencies
- `hitl_server/pyproject.toml` - Project metadata
- `docs/hitl-infrastructure/TEST_PLAN.md` - 12-section test plan (testing skill protocol)

### Protocol System (Task 1.0)
- `.claude/skills/hitl-protocols/qa_testing.md` - QA testing protocol with YAML frontmatter
- `.claude/skills/hitl-protocols/devops_deployment.md` - DevOps deployment protocol
- `.claude/skills/hitl-protocols/finance_transaction.md` - Financial transaction protocol
- `hitl_server/utils/protocol_parser.py` - Protocol loading and rule evaluation
- `hitl_server/utils/protocol_parser_test.py` - Unit tests for protocol parser

### Foundation Components (Task 2.0)
- `hitl_server/utils/state_manager.py` - Workflow state persistence (adapted from QA Engine)
- `hitl_server/utils/state_manager_test.py` - Unit tests for StateManager
- `hitl_server/utils/audit_logger.py` - Audit trail system (adapted from QA Engine)
- `hitl_server/utils/audit_logger_test.py` - Unit tests for AuditLogger
- `hitl_server/gates/base_checkpoint.py` - Base class for checkpoints (adapted from QA Engine BaseGate)
- `hitl_server/gates/base_checkpoint_test.py` - Unit tests for BaseCheckpoint

### Core Gate (Task 3.0)
- `hitl_server/gates/hitl_checkpoint_gate.py` - Main HITL checkpoint implementation
- `hitl_server/gates/hitl_checkpoint_gate_test.py` - Unit tests for HITLCheckpointGate
- `hitl_server/gates/hitl_checkpoint_integration_test.py` - Integration tests (MCP → Gate → Audit)

### MCP Server (Task 4.0)
- `hitl_server/server.py` - MCP server with tool registration
- `hitl_server/server_test.py` - MCP server integration tests

### Documentation & Examples (Task 5.0)
- `hitl_server/README.md` - Installation, usage, examples
- `examples/qa_example.py` - QA testing domain example
- `examples/devops_example.py` - DevOps deployment domain example
- `examples/finance_example.py` - Financial transaction domain example

---

## Testing Strategy

**Approach:** TDD for CORE components, integration tests for GLUE, shift-left methodology

**Key Principles:**
- Test infrastructure FIRST (Task 0.0) - enables all subsequent TDD
- Tests embedded in each task (Red → Green → Refactor per component)
- Test pyramid: Unit (many) → Integration (some) → E2E (few)
- Coverage targets: 90%+ CORE, 85%+ GLUE

**Testing Skill Reference:** `.claude/skills/testing/` protocol
- 12-section TEST_PLAN.md as living document
- Test pyramid per component (6 discovery questions)
- Failure protocol (STOP, REPORT, ANALYZE, FIX OPTIONS, IMPLEMENT)

---

## Tasks

### 0.0 Foundation - Project Setup & Test Infrastructure [FOUNDATION]

**Branch:** `feature/0.0-foundation-setup`

**Goal:** Set up project structure and test infrastructure BEFORE any implementation (shift-left).

**Done When:**
- hitl_server directory structure exists
- pytest.ini configured with HTML reporting and coverage
- TEST_PLAN.md created with 12 sections
- Can run `pytest tests/ -v` (even with no tests yet)
- All dependencies installed

**Sub-tasks:**
- [ ] 0.1 Create hitl_server directory structure (utils/, gates/, tests/)
- [ ] 0.2 Create pytest.ini with HTML reporting and coverage config
- [ ] 0.3 Create requirements.txt (pytest, pytest-html, pytest-cov, Rich, frontmatter, MCP SDK)
- [ ] 0.4 Create pyproject.toml with project metadata
- [ ] 0.5 Create docs/hitl-infrastructure/TEST_PLAN.md (12 sections per testing skill)
- [ ] 0.6 Section 1: Overview - HITL MVP test strategy summary
- [ ] 0.7 Section 2: Scope - In-scope (CORE, GLUE) vs out-of-scope
- [ ] 0.8 Section 3: Test Strategy - TDD for CORE, integration for GLUE
- [ ] 0.9 Section 4: Test Environment - Python 3.11+, pytest, MCP SDK
- [ ] 0.10 Section 5: Entry/Exit Criteria - When to start/stop testing
- [ ] 0.11 Section 6: Test Schedule - Timeline aligned with 2-3 week MVP
- [ ] 0.12 Section 7: Resources - Team, tools, infrastructure
- [ ] 0.13 Section 8: Risk Analysis - Identify testing risks and mitigations
- [ ] 0.14 Section 9: Test Matrix - Component → Test Type → Coverage Target
- [ ] 0.15 Section 10: Test Cases - High-level test case list per component
- [ ] 0.16 Section 11: Defect Management - Bug tracking and resolution process
- [ ] 0.17 Section 12: Metrics & Reporting - Coverage, pass rate, velocity
- [ ] 0.18 Create .gitignore
- [ ] 0.19 Run `pytest tests/ -v` (should pass with 0 tests)
- [ ] 0.20 Commit: `chore: Project foundation and test infrastructure (Task 0.0)`

**Commands Run:**
```bash
# (To be filled during execution)
```

**Results:**
- (To be filled during execution)

---

### 1.0 Protocol System Design & Implementation [CORE with TDD]

**Branch:** `feature/1.0-protocol-system`

**Goal:** Design and implement protocol system (YAML frontmatter + markdown) with 3 domain examples.

**Design Reference:** `1-design-hitl-infrastructure.md` section 15

**Done When:**
- 3 protocol examples exist (QA, DevOps, Finance) with YAML frontmatter + markdown
- ProtocolParser implemented with TDD (load, parse, evaluate rules)
- Unit tests pass (90%+ coverage)
- Can load protocol, evaluate auto-approve rules, evaluate require-approval rules

**Sub-tasks:**
- [ ] 1.1 Create `.claude/skills/hitl-protocols/` directory
- [ ] 1.2 Create `qa_testing.md` protocol (YAML: approval_mode, risk_levels, auto_approve, require_approval)
- [ ] 1.3 Create `devops_deployment.md` protocol (production deployment approval rules)
- [ ] 1.4 Create `finance_transaction.md` protocol (payment approval rules)
- [ ] 1.5 **Write ProtocolParser unit tests FIRST** (TDD Red)
  - Test: Load protocol from file
  - Test: Parse YAML frontmatter
  - Test: Parse markdown body
  - Test: Evaluate auto-approve rules
  - Test: Evaluate require-approval rules
  - Test: Default behavior (high/critical requires approval)
  - Target: 15-20 unit tests
- [ ] 1.6 **Implement ProtocolParser** (TDD Green)
  - `__init__(protocol_path)` - load file, parse YAML + markdown
  - `requires_approval(step, risk_level, data)` - evaluate rules
  - `_eval_rule(rule, context)` - simple rule evaluation
- [ ] 1.7 **Refactor ProtocolParser** (TDD Refactor)
- [ ] 1.8 **Verify Test Pyramid** (Unit: 15-20 tests, Integration: 0, E2E: 0)
- [ ] 1.9 Run coverage: `pytest tests/utils -v --cov=hitl_server/utils/protocol_parser.py`
- [ ] 1.10 **Record Metrics** (Coverage must be 90%+)
- [ ] 1.11 Commit: `feat: Protocol system with 3 domain examples (Task 1.0)`

**Commands Run:**
```bash
# (To be filled during execution)
```

**Results:**
- (To be filled during execution)

---

### 2.0 Foundation Components - Adapt from QA Engine [CORE with TDD]

**Branch:** `feature/2.0-foundation-components`

**Goal:** Adapt StateManager, AuditLogger, BaseGate from QA Engine with 90%+ reuse.

**Design Reference:** `1-design-hitl-infrastructure.md` section 14 (Component Adaptation Strategy)

**Adaptation Summary:**
- **StateManager:** Add checkpoint decision methods, remove QA constants (4-6 hours)
- **AuditLogger:** Add log_checkpoint method, make summary generic (4-6 hours)
- **BaseGate → BaseCheckpoint:** Rename, add checkpoint response helpers (6-8 hours)

**Done When:**
- All 3 components adapted with TDD
- Unit tests pass (90%+ coverage for each component)
- Integration test passes (StateManager + AuditLogger + BaseCheckpoint)
- Estimated effort: 14-20 hours (vs 4-6 weeks from scratch)

**Sub-tasks:**
- [ ] 2.1 Copy StateManager from QA Engine to hitl_server/utils/
- [ ] 2.2 Remove QA-specific constants (`VALID_STEPS`, `VALID_EXECUTION_MODES`)
- [ ] 2.3 **Write StateManager unit tests FIRST** (TDD Red)
  - Test: save/load/clear operations
  - Test: atomic writes
  - Test: per-run isolation (run_id)
  - Test: checkpoint decision storage (NEW)
  - Test: `save_checkpoint_decision(checkpoint_id, decision, rationale)` (NEW)
  - Target: 20-25 unit tests
- [ ] 2.4 **Implement StateManager adaptations** (TDD Green)
  - Add `save_checkpoint_decision()` method
  - Make step validation configurable (remove hardcoded VALID_STEPS)
- [ ] 2.5 **Refactor StateManager** (TDD Refactor)
- [ ] 2.6 Copy AuditLogger from QA Engine to hitl_server/utils/
- [ ] 2.7 **Write AuditLogger unit tests FIRST** (TDD Red)
  - Test: log_gate, log_self_heal, log_file_generated
  - Test: incremental persist
  - Test: session continuation
  - Test: `log_checkpoint(checkpoint_id, step, data, risk_level, ai_analysis, decision)` (NEW)
  - Test: get_summary (domain-agnostic, no QA field assumptions)
  - Target: 20-25 unit tests
- [ ] 2.8 **Implement AuditLogger adaptations** (TDD Green)
  - Add `log_checkpoint()` method
  - Make `get_summary()` domain-agnostic
- [ ] 2.9 **Refactor AuditLogger** (TDD Refactor)
- [ ] 2.10 Copy BaseGate from QA Engine to hitl_server/gates/
- [ ] 2.11 Rename BaseGate → BaseCheckpoint
- [ ] 2.12 **Write BaseCheckpoint unit tests FIRST** (TDD Red)
  - Test: pass_response, fail_response
  - Test: audit integration
  - Test: `checkpoint_response(approved, requires_human, ai_analysis, options)` (NEW)
  - Target: 15-20 unit tests
- [ ] 2.13 **Implement BaseCheckpoint adaptations** (TDD Green)
  - Add `checkpoint_response()` method
  - Add checkpoint-specific response helpers
- [ ] 2.14 **Refactor BaseCheckpoint** (TDD Refactor)
- [ ] 2.15 **Write integration test** (StateManager + AuditLogger + BaseCheckpoint)
- [ ] 2.16 **Verify Test Pyramid** (Unit: 55-70, Integration: 1, E2E: 0)
- [ ] 2.17 Run coverage: `pytest tests/utils tests/gates -v --cov=hitl_server/utils --cov=hitl_server/gates`
- [ ] 2.18 **Record Metrics** (Coverage must be 90%+)
- [ ] 2.19 Commit: `feat: Foundation components adapted from QA Engine (Task 2.0)`

**Commands Run:**
```bash
# (To be filled during execution)
```

**Results:**
- (To be filled during execution)

---

### 3.0 Core HITL Checkpoint Gate [CORE with TDD]

**Branch:** `feature/3.0-hitl-checkpoint-gate`

**Goal:** Implement HITLCheckpointGate following synchronous return + AI orchestration pattern.

**Design Reference:** `1-design-hitl-infrastructure.md` section 11 (Checkpoint Workflow Pattern)

**Pattern:** Gate evaluates checkpoint, returns immediately with approval status + diagnostic context. AI orchestrates approval conversation.

**Done When:**
- HITLCheckpointGate implements: protocol loading, risk evaluation, AI analysis, diagnostic capture
- Conversational mode fully implemented
- CLI/Web UI modes stubbed (return "not implemented, using conversational")
- Unit tests pass (90%+ coverage)
- Integration test passes (MCP → Gate → Audit)

**Sub-tasks:**
- [ ] 3.1 Create HITLCheckpointGate class extending BaseCheckpoint
- [ ] 3.2 **Write unit tests FIRST** for protocol loading (TDD Red)
- [ ] 3.3 Implement protocol loading (load from `.claude/skills/hitl-protocols/`)
- [ ] 3.4 **Write unit tests FIRST** for risk evaluation (TDD Red)
- [ ] 3.5 Implement risk evaluation (check auto-approve, require-approval rules)
- [ ] 3.6 **Write unit tests FIRST** for diagnostic capture (TDD Red)
- [ ] 3.7 Implement diagnostic capture (arbitrary JSON, no hardcoded fields)
- [ ] 3.8 **Write unit tests FIRST** for AI analysis (TDD Red)
- [ ] 3.9 Implement AI analysis (pattern matching, confidence scoring 0-100%)
- [ ] 3.10 **Write unit tests FIRST** for triage formatting (TDD Red)
- [ ] 3.11 Implement triage formatting (conversational response with options)
- [ ] 3.12 **Write unit tests FIRST** for approval mode routing (TDD Red)
- [ ] 3.13 Implement approval mode routing:
  - `conversational` → return checkpoint_response with ai_analysis
  - `cli` → stub: log warning, fallback to conversational
  - `web_ui` → stub: log warning, fallback to conversational
- [ ] 3.14 **Write integration test** (MCP → Gate → Audit trail)
- [ ] 3.15 **Verify Test Pyramid** (Unit: 25-30, Integration: 2-3, E2E: 1)
- [ ] 3.16 Run coverage: `pytest tests/gates -v --cov=hitl_server/gates`
- [ ] 3.17 **Record Metrics** (Coverage must be 90%+)
- [ ] 3.18 Commit: `feat: HITL checkpoint gate with conversational mode (Task 3.0)`

**Commands Run:**
```bash
# (To be filled during execution)
```

**Results:**
- (To be filled during execution)

---

### 4.0 MCP Server Integration [GLUE with Integration Testing]

**Branch:** `feature/4.0-mcp-server-integration`

**Goal:** Create MCP server with hitl_checkpoint tool registration following QA Engine patterns.

**Done When:**
- MCP server.py registers hitl_checkpoint tool
- Tool accepts: workflow_id, step_name, diagnostic_data (arbitrary JSON), risk_level
- Integration test passes (MCP tool call → Gate → Approval → Audit)
- Server starts without errors
- Coverage 85%+ (GLUE target)

**Sub-tasks:**
- [ ] 4.1 Create hitl_server/server.py with MCP SDK setup
- [ ] 4.2 **Write integration tests FIRST** for tool registration
- [ ] 4.3 Register hitl_checkpoint tool with schema:
  - workflow_id (required): Workflow identifier
  - step_name (required): Checkpoint name
  - diagnostic_data (required): Arbitrary JSON (domain-agnostic)
  - risk_level (required): low, medium, high, critical
  - domain (optional): Protocol domain (defaults to workflow_id)
- [ ] 4.4 **Write integration test** for tool handler (call HITLCheckpointGate)
- [ ] 4.5 Implement tool handler:
  - Load protocol for domain
  - Call HITLCheckpointGate.validate()
  - Return checkpoint response to MCP client
- [ ] 4.6 Integrate StateManager for run_id persistence
- [ ] 4.7 Integrate AuditLogger for checkpoint logging
- [ ] 4.8 **Write E2E test** (MCP tool call → Gate → Conversational Response → Audit)
- [ ] 4.9 **Verify Test Pyramid** (Unit: 5-8, Integration: 3-5, E2E: 2-3)
- [ ] 4.10 Run coverage: `pytest tests/integration -v --cov=hitl_server`
- [ ] 4.11 **Record Metrics** (Coverage must be 85%+)
- [ ] 4.12 Test MCP server startup: `python hitl_server/server.py`
- [ ] 4.13 Commit: `feat: MCP server with hitl_checkpoint tool (Task 4.0)`

**Commands Run:**
```bash
# (To be filled during execution)
```

**Results:**
- (To be filled during execution)

---

### 5.0 Documentation and Examples [GLUE]

**Branch:** `feature/5.0-documentation-examples`

**Goal:** Complete README, protocol documentation, and 3 domain examples.

**Done When:**
- README.md covers: Installation, Quick Start, MCP server setup, protocol creation
- 3 Python examples run successfully (QA, DevOps, Finance)
- Protocol documentation complete
- All examples have acceptance tests

**Sub-tasks:**
- [ ] 5.1 Write README.md: Overview, Installation, Quick Start
- [ ] 5.2 README section: MCP server setup (add to claude_desktop_config.json)
- [ ] 5.3 README section: Protocol creation guide (YAML + markdown)
- [ ] 5.4 Write examples/qa_example.py (QA testing workflow with checkpoints)
  - Scenario: Test generation approval workflow
  - Checkpoint: generate_test (high-risk)
  - Diagnostic data: test_scenarios, element_count, confidence_score
- [ ] 5.5 Write examples/devops_example.py (DevOps deployment workflow)
  - Scenario: Production deployment approval
  - Checkpoint: deploy_production (critical risk)
  - Diagnostic data: deployment_config, environment_vars, service_health
- [ ] 5.6 Write examples/finance_example.py (Financial transaction workflow)
  - Scenario: High-value payment approval
  - Checkpoint: process_payment (high-risk)
  - Diagnostic data: transaction, risk_score, fraud_signals, customer_history
- [ ] 5.7 **Write acceptance tests** for all 3 examples
- [ ] 5.8 Test all 3 examples run without errors
- [ ] 5.9 Document protocol creation process
- [ ] 5.10 Document approval mode configuration
- [ ] 5.11 Document diagnostic data best practices
- [ ] 5.12 Run acceptance tests: `pytest examples/ -v`
- [ ] 5.13 **Record Results** (All examples pass)
- [ ] 5.14 Commit: `docs: README, examples, and protocol documentation (Task 5.0)`

**Commands Run:**
```bash
# (To be filled during execution)
```

**Results:**
- (To be filled during execution)

---

## Phase Completion Criteria

**MVP Complete When:**
- [ ] All 5 parent tasks marked complete (0.0-5.0)
- [ ] All unit tests pass (90%+ coverage for CORE: Tasks 1-3)
- [ ] All integration tests pass (85%+ coverage for GLUE: Tasks 4-5)
- [ ] MCP server starts without errors
- [ ] 3 domain examples run successfully
- [ ] TEST_PLAN.md has 12 complete sections
- [ ] README.md covers installation and usage
- [ ] Audit trail captures all checkpoint decisions
- [ ] Conversational mode works end-to-end
- [ ] CLI/Web UI modes stubbed with fallback to conversational

**Success Metrics:**
- Test coverage: 90%+ CORE, 85%+ GLUE
- All protocols load and evaluate correctly
- Checkpoint workflow follows Design Decision 11 (synchronous return + AI orchestration)
- Component reuse validated (90%+ from QA Engine)
- Effort estimate validated (2-3 weeks vs 4-6 weeks)

**Next Phase:** Phase 4 (Deliver) - Execute tasks following TDD and shift-left methodology

---

## Timeline Estimate

**Updated based on component reuse analysis:**

**Week 1:**
- Task 0.0: Project Setup (1 day)
- Task 1.0: Protocol System (2 days)
- Task 2.0: Foundation Components (2-3 days - adaptation only)

**Week 2:**
- Task 3.0: Core Gate (2-3 days)
- Task 4.0: MCP Server (1-2 days)

**Week 3:**
- Task 5.0: Documentation (2 days)
- Polish, testing, bug fixes (3 days)

**Total: 2-3 weeks** (vs original 4 weeks estimate)

**Confidence:** High - 90%+ component reuse validated, clear design decisions documented

---

**Status:** Ready for Phase 4 (Deliver)
**Next:** Execute Task 0.0 (Foundation Setup)
