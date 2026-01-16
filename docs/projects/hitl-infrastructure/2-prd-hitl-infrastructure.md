# Product Requirements Document: HITL Infrastructure

**Status:** Phase 1 Complete - PRD Updated with Checkpoint Workflow and Approval Mode Decisions
**Version:** 4.0
**Last Updated:** 2026-01-15

---

## Introduction/Overview

HITL (Human-in-the-Loop) Compliance Infrastructure is a domain-agnostic platform that provides human oversight checkpoints in AI agent workflows using the proven Isagawa pattern: **Protocols + Smart Gates**.

**MVP Scope (March 2026):** Local-only MCP Server that works across ANY domain - QA testing, DevOps, Finance, Healthcare, or custom workflows.

**Compliance Positioning:**
- **US Market:** Fully implements NIST AI Risk Management Framework (best practice for responsible AI)
- **International Market:** Technical foundation for EU AI Act Article 14 compliance (for companies with EU customers)
- **Enterprise:** ISO/IEC 42001 aligned (international AI governance standard)

**Core Capabilities:**
- Markdown-based protocols (human-readable oversight rules)
- Smart gates (enforcement via MCP tools with diagnostic context)
- Conversational triage (full execution context + AI analysis + evidence)
- Progressive audit trails (immutable logs with human decisions)
- Domain-agnostic design (arbitrary JSON, no hardcoded assumptions)

---

## Goals

### MVP Goals (March 2026)

1. **Launch standalone HITL MVP** - Local-only MCP Server (no hosted infrastructure)
2. **NIST AI RMF compliant** - Fully implement US best practices for responsible AI oversight
3. **Prove domain-agnostic pattern** - Works across QA, DevOps, Finance, Healthcare
4. **Validate Protocols + Smart Gates** - Step 11 pattern extracted from QA Engine
5. **Ship in 4 weeks** - Leverage proven components (StateManager, AuditLogger, BaseGate)
6. **Open-source launch** - Free MCP server, build community before monetization

### Post-MVP Goals (Phase 2+)

1. **Enterprise Compliance Package** - Role-based access, multi-level approvals, training certification
2. **EU AI Act Full Compliance** - Complete Article 14 requirements for EU market
3. **ISO/IEC 42001 Certification** - International AI governance standard
4. Add REST API + SDK for non-MCP integrations
5. Hosted dashboard for enterprise (approval queue, analytics)
6. Extract shared library (`isagawa-core`) for QA Engine + HITL + future products
7. Establish "Powered by Isagawa HITL" as standard for agentic AI compliance
8. Monetization: Freemium model (free local, paid hosted/enterprise)

---

## User Stories

### MVP User Stories

**Design Reference:** See `1-design-hitl-infrastructure.md` sections 11-15 for detailed design decisions.

**As a developer using Claude Code, I want to...**
- Install HITL MCP server with one command (`npx @isagawa/hitl-server`)
- Add `hitl_checkpoint` tool calls to my agent workflow
- Get approval requests in conversation (Claude asks, I respond)
- See full diagnostic context + AI analysis before deciding
- Have all decisions automatically logged to local audit trail

**As an AI agent developer, I want to...**
- Define oversight rules in markdown (protocols) without writing validation code
- Have Smart Gates automatically enforce those rules
- Provide arbitrary diagnostic data (domain-agnostic)
- Get AI analysis of failures with confidence scoring
- Resume workflows after human approval

**As a solo developer building AI tools, I want to...**
- Run everything locally (no cloud services, no sign-up)
- Review approval requests conversationally (Claude asks, I respond)
- Export audit logs for personal records
- Understand what happened without reading code

**MVP Approval Mode (Design Decision 12):**
- ✅ **Conversational mode** - AI orchestrates approval in conversation (fully implemented)
- 📋 **CLI mode** - Terminal-based approval (stubbed, fallback to conversational)
- 📋 **Web UI mode** - Browser-based approval (stubbed, fallback to conversational)

**Rationale:** Target audience is Claude Code users already in conversation. CLI/Web UI modes unlock new customer segments post-MVP (terminal-first DevOps, enterprise compliance). See `1-design-hitl-infrastructure.md` section 12-13 for analysis.

### Phase 2 User Stories (Post-MVP)

**As an enterprise deploying custom agents, I want to...**
- Review pending approvals in hosted dashboard (team access)
- Configure multi-level approval chains (L1 → L2 → L3)
- Integrate via REST API (not just MCP)
- Generate compliance reports (CSV, PDF) for auditors

**As a compliance officer, I want to...**
- Map protocols to EU AI Act Article 14 requirements
- Access 3-year audit trail retention
- Export compliance matrix for external audits
- Monitor approval patterns across teams

---

## Functional Requirements

### MVP Functional Requirements

#### FR-1: Core Smart Gate

1.1. **HITLCheckpointGate** must accept: workflow_id, step_name, diagnostic_data (arbitrary JSON), risk_level
1.2. Gate must load protocol from markdown file with YAML frontmatter
1.3. Gate must evaluate protocol rules to determine if approval is required
1.4. Gate must auto-approve low-risk actions per protocol configuration
1.5. Gate must capture diagnostic context for high-risk/failed actions
1.6. Gate must generate AI analysis with confidence scoring (0-100%)
1.7. Gate must format triage presentation with options (approve/reject/investigate/custom)
1.8. Gate must integrate with StateManager for workflow persistence
1.9. Gate must integrate with AuditLogger for immutable logging

**Design Pattern:** ONE gate class (not split validation/context) - follows QA Engine Step 11 pattern

#### FR-2: Protocol Engine

2.1. System must parse markdown protocols from `.claude/skills/hitl-protocols/`
2.2. Protocols must support YAML frontmatter for configuration
2.3. Protocols must define risk levels (low, medium, high, critical)
2.4. Protocols must specify auto-approve conditions
2.5. Protocols must be domain-agnostic (no hardcoded field names)

**Reuse:** Existing Protocol parser from QA Engine (already domain-agnostic)

#### FR-3: Human Approval Mechanism (Dual Mode)

3.1. **CLI Mode**: Terminal prompt with rich formatting (using Rich library)
3.2. **Web UI Mode**: Local web UI (Next.js on localhost:3001) with diagnostic viewer
3.3. **Smart Default**: Auto-detect mode based on context (terminal vs complex data)
3.4. Both modes must support: Approve, Reject, Investigate, Custom guidance
3.5. Both modes must display: Diagnostic data, AI analysis, evidence, suggested fixes
3.6. Approval requests must queue in local SQLite database

**Pattern:** Step 11 conversational triage, adapted for domain-agnostic use

#### FR-4: State Management

4.1. System must persist workflow state across checkpoints
4.2. StateManager must support per-run isolation (run_id-based directories)
4.3. StateManager must use atomic writes (crash-safe)
4.4. StateManager must track attempt counts (for retry policy)
4.5. StateManager must store execution mode (if applicable to domain)

**Reuse:** Copy StateManager from QA Engine, remove QA-specific constants

#### FR-5: Audit Trail

5.1. System must log every checkpoint call with timestamp
5.2. Audit logs must include: workflow_id, step_name, checkpoint_result, diagnostic_data, ai_analysis, human_decision
5.3. Audit logs must write to local JSON files (`tests/_audit/audit_log_<run_id>.json`)
5.4. Audit logs must use incremental persist (crash-safe, no data loss)
5.5. Audit logs must be immutable (write-once, read-many)
5.6. System must support JSON export (CSV/PDF export in Phase 2)

**Reuse:** Copy AuditLogger from QA Engine, adapt for domain-agnostic fields

#### FR-6: MCP Server Integration

6.1. MCP Server must register `hitl_checkpoint` tool
6.2. Tool must accept arbitrary JSON for diagnostic_data (domain-agnostic)
6.3. Tool must return pass_response OR hitl_triage_response
6.4. Server must be installable via npm (local installation)
6.5. Server must run on user's machine (no cloud services)

### Phase 2 Functional Requirements (Out of Scope for MVP)

- REST API endpoint (`/hitl/checkpoint`)
- Python/JavaScript SDKs with decorators
- Hosted dashboard with team access
- Multi-level approval chains (L1 → L2 → L3)
- Compliance matrix auto-generation
- CSV/PDF export formats
- 3-year audit retention policy
- Multi-region support

---

## Non-Goals (Out of Scope for MVP)

### Phase 2 Features (Not in MVP)
1. REST API / SDK (MCP only for MVP)
2. Hosted infrastructure (local-only for MVP)
3. Team collaboration / multi-user (single user for MVP)
4. Advanced analytics / dashboards (basic JSON logs for MVP)
5. CSV/PDF export (JSON only for MVP)
6. Multi-region support (single deployment)
7. SSO / OAuth integration (no auth needed for local)

### Never Features
1. Pattern recognition / ML-based risk scoring (AI analysis is heuristic-based)
2. White-label customization (open-source, fork if needed)
3. Visual diff / screenshot comparison (domain-agnostic, no UI assumptions)
4. Integration with specific CI/CD pipelines (tool-agnostic)
5. Custom protocol DSL beyond YAML+Markdown (keep simple)

---

## Design Considerations

**Design Document:** See `1-design-hitl-infrastructure.md` (complete Phase 1 design)

**Architecture Pattern:** Protocols + Smart Gates (The Isagawa Way)
- Protocol (Markdown) → Smart Gate (MCP Tool) → HITL Triage → Audit Log
- Gate does BOTH: validation + diagnostic context building (ONE responsibility)
- Follows QA Engine Step 11 pattern (proven in production)

**Core Design Decisions (Latest - 2026-01-15):**

**⚠️ IMPORTANT:** See `1-design-hitl-infrastructure.md` sections 11-15 for complete design rationale, alternatives rejected, and trade-off analysis.

### 1. Checkpoint Workflow Pattern (Design Decision 11)
**Synchronous Return + AI Orchestration**

MCP tool evaluates checkpoint and returns IMMEDIATELY with:
- Auto-approved (low-risk + protocol rules)
- Requires human (high-risk + diagnostic context + AI analysis)

AI orchestrates approval conversation. NOT async tasks, NOT blocking workflow.

**Rationale:** Domain-agnostic (seconds to days), proven (QA Engine Step 11), 90%+ component reuse.

### 2. Approval Mode Strategy (Design Decision 12)
**Conversational Mode MVP, Protocol-Driven Future**

**MVP:**
- ✅ Conversational: AI asks approval questions in conversation
- 📋 CLI: Stubbed (fallback to conversational)
- 📋 Web UI: Stubbed (fallback to conversational)

**Post-MVP:** Protocol field `approval_mode` enables per-domain modes (CLI for DevOps, Web UI for enterprise).

**Rationale:** Target audience (Claude Code users), fastest to value (1-2 weeks), validates pattern before complex infrastructure.

### 3. Component Adaptation (Design Decision 14)
**90%+ Reuse from QA Engine**

- StateManager: Add checkpoint methods, remove QA constants (4-6 hours)
- AuditLogger: Add log_checkpoint, make summary generic (4-6 hours)
- BaseGate → BaseCheckpoint: Rename + checkpoint responses (6-8 hours)

**Total:** 14-20 hours (2-3 days) vs 4-6 weeks from scratch.

### 4. Protocol System (Design Decision 15)
**YAML Frontmatter + Markdown Body**

```yaml
---
approval_mode: conversational
auto_approve:
  - when: risk_level == "low"
---
# Human-readable guidance here
```

**Rationale:** Human-readable (auditors), machine-parseable (automation), extensible.

---

**Earlier Design Decisions:**

1. **ONE Gate Class** - Not split into validation/context components
   - Responsibility: "Evaluate checkpoint and provide decision support"
   - Helper methods for organization, not separate classes
   - Follows QA Engine pattern (qg_execution.py)

2. **Component Reuse Strategy** - Copy proven components from QA Engine
   - StateManager (311 lines) - Atomic writes, per-run isolation, crash-safe
   - AuditLogger (296 lines) - Incremental persist, session continuation
   - BaseGate pattern (664 lines) - Validation utilities, response formatting
   - Minimal adaptation: Remove QA-specific constants, make domain-agnostic

3. **Domain-Agnostic by Design** - No prescribed diagnostic data structure
   - Caller provides arbitrary JSON (no required field names)
   - Protocol guides what to include (per domain)
   - AI analyzes whatever is provided (pattern matching + confidence scoring)
   - Can ask clarifying questions during triage

4. **Local-First MVP** - No hosted infrastructure
   - MCP Server runs locally (like QA Engine)
   - JSON files for audit trail (tests/_audit/)
   - SQLite for approval queue (local database)
   - Next.js on localhost:3001 (no deployment needed)

**Technology Stack (MVP):**
- **Python 3.11+** - MCP Server implementation
- **MCP SDK** - Tool registration and protocol
- **Rich** - CLI formatting for terminal mode
- **Next.js** - Local web UI (localhost:3001)
- **SQLite** - Approval queue (local database)
- **JSON Files** - Audit trail storage (tests/_audit/)
- **Markdown + YAML** - Protocol definitions (.claude/skills/)

---

## Technical Considerations

### Component Extraction Strategy

1. **Do NOT extract from QA Engine** - Build standalone, learn from Step 11 pattern
   - QA Engine Step 11 continues unchanged
   - Copy proven components (StateManager, AuditLogger, BaseGate)
   - Adapt for domain-agnostic use (remove QA-specific assumptions)
   - No backward compatibility concerns (separate codebase)

2. **Post-MVP: Extract Shared Library** (Phase 2)
   - Once both products validate the pattern
   - Create `isagawa-core` npm/pip package
   - QA Engine + HITL both depend on shared library
   - See backlog: `modular_hitl_system.md`, `audit_system_enhancements.md`

### Dependencies

- **Python 3.11+** - MCP Server runtime
- **MCP SDK (Python)** - @anthropic/mcp-sdk equivalent for Python
- **Rich** - Terminal formatting for CLI mode
- **Next.js** - Local web UI
- **SQLite3** - Built-in Python, no external database
- **No external services** - Fully offline-capable

### Constraints

- **Local-only for MVP** - No cloud infrastructure, no deployment
- **Single-user for MVP** - No authentication, no multi-tenant
- **MCP-only integration** - REST API deferred to Phase 2
- **4-week timeline** - Leverage existing components, no greenfield work

### Integration Requirements

- **MCP Tool Registration** - Server exposes `hitl_checkpoint` tool
- **Protocol Discovery** - Read markdown from `.claude/skills/hitl-protocols/`
- **Audit Trail** - Write to local `audit/audit_log_<run_id>.json`
- **State Persistence** - Write to local `state/<run_id>/workflow_state.json`
- **Approval Queue** - SQLite database at `approvals.db`

---

## Regulatory Compliance

### Applicability: Who Needs This?

**US Companies:**
- ✅ **NIST AI RMF Compliance** - Voluntary best practice for responsible AI (applies to all US companies)
- ⚠️ **EU AI Act Applies IF** - You have EU customers/users (extraterritorial reach like GDPR)
- ✅ **Industry-Specific** - Healthcare (HIPAA), Finance (OCC Model Risk Management), etc.

**International Companies:**
- ✅ **EU AI Act** - Mandatory if selling/deploying in EU market (Aug 2, 2026 enforcement)
- ✅ **ISO/IEC 42001** - International AI management standard (voluntary, certification available)

**Our Product Positioning:**
- **Primary (US Market):** "NIST AI RMF compliant" - Implements recommended human oversight controls
- **Secondary (EU Market):** "Technical foundation for EU AI Act Article 14 compliance"
- **Enterprise:** "ISO/IEC 42001 aligned" - International standard for AI governance

### NIST AI Risk Management Framework Compliance (US Best Practice)

**MVP Implementation Status:**

| NIST Function | Our Implementation | Status |
|---------------|-------------------|--------|
| **GOVERN** | Protocols define oversight rules (human-readable markdown) | ✅ MVP |
| **MAP** | Risk levels mapped per domain (low/medium/high/critical) | ✅ MVP |
| **MEASURE** | AI analysis with confidence scoring + evidence extraction | ✅ MVP |
| **MANAGE** | Human approval required for high-risk + audit trail | ✅ MVP |

**NIST Recommendations for High-Risk AI:**
- ✅ Human oversight for critical decisions - **Our core feature**
- ✅ Transparency and explainability - **Diagnostic context + AI analysis**
- ✅ Documentation and audit trails - **Immutable logs with full context**
- ✅ Risk assessment and mitigation - **Protocol-based risk levels**

**Marketing Claim:** "Compliant with NIST AI Risk Management Framework best practices"

### EU AI Act Article 14 (For Companies with EU Customers)

**When EU AI Act Applies to You:**
1. You place AI systems on the EU market (sell to EU customers)
2. You deploy AI systems in the EU
3. Your AI system's outputs are used by people in the EU

**Extraterritorial Reach:** Like GDPR, the EU AI Act applies to non-EU companies if AI is used in EU.

**Our MVP as Technical Foundation:**

| Article 14 Requirement | Our Implementation | Status |
|----------------------|-------------------|--------|
| **Human Oversight Model** | HITL (Human-in-the-Loop) with real-time intervention | ✅ MVP |
| **Pre-decision Approval** | High-risk checkpoints block until human approves | ✅ MVP |
| **Diagnostic Transparency** | Full execution context with AI analysis | ✅ MVP |
| **Immutable Audit Trail** | Progressive audit trail (Article 12) | ✅ MVP |
| **Risk Prevention** | Protocol-based risk evaluation + auto-approve for low-risk | ✅ MVP |
| **Competent Personnel** | Deployer responsibility - protocol configurable | 📋 Documentation |
| **Training Requirements** | Deployer responsibility - guidance provided | 📋 Documentation |
| **Authority to Intervene** | Approve/Reject/Escalate options | ✅ MVP (single-level), ⚠️ Phase 2 (multi-level) |

**Three Oversight Models:**
- **HITL (MVP):** Real-time intervention, pre-decision approval for high-risk actions
- **HOTL (Phase 2):** Monitoring with intervention capability
- **HIC (Phase 2):** Full control with override authority

**Marketing Claim:** "Technical foundation for EU AI Act Article 14 compliance" (system + deployer's personnel = full compliance)

### ISO/IEC 42001 Compliance

| Requirement | Our Implementation | Status |
|-------------|-------------------|--------|
| **Human-in-the-Loop Controls** | Mandatory checkpoints for critical decisions | ✅ MVP |
| **AI Lifecycle Management** | State management, workflow tracking | ✅ MVP |
| **Transparency** | Protocol-defined rules (human-readable) | ✅ MVP |
| **Accountability** | Audit trail with human decisions + rationale | ✅ MVP |
| **Explainability** | AI analysis with confidence + evidence | ✅ MVP |
| **Bias Mitigation** | Domain-agnostic (no hardcoded assumptions) | ✅ MVP |
| **Risk Management** | Protocol-based risk levels (low/medium/high/critical) | ✅ MVP |
| **Audit Documentation** | Immutable JSON logs, exportable | ✅ MVP (JSON), ⚠️ Phase 2 (CSV/PDF) |

### NIST AI Risk Management Framework Alignment

| Principle | Our Implementation |
|-----------|-------------------|
| **Govern** | Protocols define oversight rules |
| **Map** | Risk levels mapped per domain |
| **Measure** | AI analysis with confidence scoring |
| **Manage** | Human approval + audit trail |

### Compliance Gaps (Phase 2 Roadmap)

**For US Market (NIST AI RMF):**
- ✅ MVP fully implements NIST recommendations (no gaps)

**For EU Market (Article 14):**

| Gap | Impact | Mitigation Timeline |
|-----|--------|-------------------|
| **Competency Verification** | Cannot verify approver qualifications (Article 26(2)) | Phase 2: Role-based access control |
| **Multi-level Approval** | Single approver only | Phase 2: L1→L2→L3 escalation chains |
| **Formal Risk Assessment** | Protocol-based, not formally documented | Phase 2: Risk register, compliance matrix |
| **Training Documentation** | No formal training program (Article 26(2)) | Phase 2: Certification system |
| **CSV/PDF Export** | JSON only | Phase 2: Compliance report formats |

**Note:** Gaps are organizational/process requirements that deployers must implement. MVP provides technical foundation.

### Compliance Certification Strategy

**MVP (Local-Only, Open-Source):**
- ✅ **US:** Fully compliant with NIST AI RMF (best practice, no certification needed)
- ✅ **EU:** Technical foundation for Article 14 (deployer adds organizational requirements)
- Documentation provides compliance guidance for both markets
- Open-source allows audit of implementation

**Phase 2 (Hosted Tier, Enterprise):**
- **US:** SOC 2 Type II certification (security + availability)
- **EU:** ISO/IEC 42001 certification pursuit, EU AI Act conformity assessment
- **International:** ISO 27001 (information security)
- Third-party penetration testing

**References:**
- [EU AI Act Article 14](https://artificialintelligenceact.eu/article/14/)
- [EU AI Act Human Oversight Guide](https://www.eyreact.com/eu-ai-act-human-oversight-requirements-comprehensive-implementation-guide/)
- [ISO/IEC 42001 Explained](https://www.cornerstoneondemand.com/resources/article/iso-iec-42001-explained/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [Human Oversight Legal Aspects](https://newtech.law/en/articles/human-oversight-of-ai-systems)

---

## Success Metrics

### MVP Success Metrics (4 Weeks)

**Shipping Goals:**
- ✅ Standalone HITL MCP Server launched (GitHub repo)
- ✅ Works across 3+ domains (QA, DevOps, Finance examples)
- ✅ CLI + Web UI both functional
- ✅ Full documentation (README, protocol examples)

**Technical Validation:**
- Pattern proven: Step 11 triage conversation works domain-agnostic
- Components validated: StateManager, AuditLogger, BaseGate work standalone
- Zero regressions: QA Engine Step 11 continues working unchanged

**Community Validation (First 30 Days):**
- 100+ GitHub stars (validation of interest)
- 10+ issues/discussions (community engagement)
- 3+ external use cases shared (beyond QA/DevOps/Finance)

### Phase 2 Success Metrics (Post-MVP)

**Adoption (60 Days):**
- 1,000 MCP server installs
- 50 active users (weekly usage)
- 5 community contributions (PRs, protocols)

**Product Expansion:**
- REST API launched
- Python/JavaScript SDKs released
- Hosted dashboard MVP (team collaboration)

### Phase 3 Success Metrics (Aug 2026+)

**Business Goals:**
- 10 paid customers ($500-2K/mo hosted tier)
- $5K-20K MRR
- "Powered by Isagawa HITL" badge on 3+ products

**Platform Recognition:**
- Referenced in EU AI Act compliance guides
- Presented at AI governance conferences
- Integrated with popular agent frameworks (LangGraph, CrewAI)

### Non-Functional Success Criteria

**Performance:**
- Checkpoint evaluation < 100ms (p95)
- Approval queue response < 1s
- Audit trail write < 50ms

**Reliability:**
- Zero data loss (crash-safe writes)
- 100% audit trail completeness
- Graceful handling of missing protocols

**Developer Experience:**
- Installation in < 5 minutes
- First checkpoint in < 15 minutes
- Clear error messages with fix hints

---

## Open Questions

### Resolved in Phase 1 Design

1. ✅ **Integration method:** MCP only for MVP (REST API Phase 2)
2. ✅ **Infrastructure:** Local-only (no hosted services for MVP)
3. ✅ **Approval mechanism:** Dual mode (CLI + Web UI with smart defaults)
4. ✅ **Component reuse:** Copy from QA Engine, don't extract yet
5. ✅ **Gate design:** ONE class (validation + context), not split
6. ✅ **Domain-agnostic:** Arbitrary JSON for diagnostic_data

### Still Open (MVP Scope)

1. **Protocol versioning:** How to handle protocol updates without breaking existing workflows?
   - Proposal: Version in YAML frontmatter, backward compatibility layer

2. **Retry policy defaults:** Should gates track attempt counts like QA Engine?
   - QA Engine: Max 2 same errors, 5 total attempts
   - HITL: Make configurable per protocol?

3. **Web UI port:** localhost:3001 or auto-detect available port?
   - Conflict risk with other services
   - Proposal: Try 3001, 3002, 3003 in sequence

4. **Approval queue expiration:** How long to keep pending approvals?
   - Proposal: 7 days default, configurable per protocol

5. **Error signature tracking:** Hash errors like QA Engine Step 11?
   - Helps detect same error recurring
   - Proposal: Yes, use MD5 hash of error message + location

### Deferred to Phase 2

1. **Pricing tiers:** Free open-source, paid hosted tier pricing TBD
2. **Multi-region support:** Single deployment for MVP
3. **Notification channels:** No notifications for MVP (local-only)
4. **Multi-level approvals:** Single approver for MVP (L1 → L2 → L3 in Phase 2)
5. **Compliance reporting:** JSON only for MVP (CSV/PDF in Phase 2)

---

## Test Strategy (MVP)

**Testing Approach:** TDD (Test-Driven Development) following QA Engine pattern

**Detailed Test Plan:** Will be created in Phase 3 (Divide) as `docs/TEST_PLAN.md` following `.claude/skills/testing/` protocol with 12 standard sections:
1. Overview, 2. Scope, 3. Test Strategy, 4. Test Environment, 5. Entry/Exit Criteria, 6. Test Schedule, 7. Resources, 8. Risk Analysis, 9. Test Matrix, 10. Test Cases, 11. Defect Management, 12. Metrics & Reporting

**High-Level Testing Strategy (Summary for PRD):**

### Unit Tests (Core Components)

**StateManager Tests** (copied from QA Engine, adapted)
- Atomic writes (crash-safe)
- Per-run isolation (run_id-based directories)
- Attempt count tracking
- Execution mode get/set

**AuditLogger Tests** (copied from QA Engine, adapted)
- Incremental persist (crash-safe)
- Session continuation (reuse run_id)
- Summary statistics calculation
- Domain-agnostic field storage

**HITLCheckpointGate Tests** (new, based on QG Execution pattern)
- Protocol loading and parsing
- Risk level evaluation
- Auto-approve vs human-required decision
- Diagnostic context capture (arbitrary JSON)
- AI analysis generation (confidence scoring)
- Triage message formatting
- Response structure (pass_response vs hitl_triage_response)

**ProtocolParser Tests** (reuse existing)
- YAML frontmatter parsing
- Markdown content extraction
- Risk level configuration
- Auto-approve conditions

### Integration Tests (End-to-End Flows)

**Test 1: MCP Tool → Gate → Audit Trail**
- Call `hitl_checkpoint` via MCP server
- Verify gate processes request
- Verify audit log written to disk
- Verify state persisted correctly

**Test 2: Low-Risk Auto-Approve Flow**
- Protocol defines low-risk action
- Call checkpoint with risk_level="low"
- Verify auto-approve (no human interaction)
- Verify audit trail logs "auto_approved"

**Test 3: High-Risk HITL Triage Flow**
- Protocol defines high-risk action
- Call checkpoint with risk_level="high"
- Verify approval queued in SQLite
- Verify diagnostic context captured
- Verify AI analysis generated
- Verify triage message formatted

**Test 4: CLI Mode Approval**
- Queue approval request
- Simulate CLI mode selection
- Verify human decision logged
- Verify workflow resumes

**Test 5: Web UI Mode Approval**
- Queue approval request
- Simulate Web UI interaction
- Verify diagnostic viewer displays data
- Verify human decision logged

### Acceptance Tests (BDD Format)

**Scenario 1: DevOps deployment requires approval**
```gherkin
GIVEN a protocol defines "production_deployment" as high-risk
  AND diagnostic data includes: deployment_config, environment_vars, service_health
WHEN an agent triggers hitl_checkpoint with risk_level="critical"
THEN approval request is queued with full diagnostic context
  AND AI analysis suggests potential issues
  AND triage presents options: approve, reject, investigate
  AND execution blocks until human approves
  AND audit trail logs checkpoint + diagnostic data + human decision
```

**Scenario 2: QA test passed - auto-approve**
```gherkin
GIVEN a protocol defines "test_passed" as low-risk
  AND diagnostic data includes: test_result with status="passed"
WHEN an agent triggers hitl_checkpoint with risk_level="low"
THEN checkpoint returns "auto_approved"
  AND audit trail logs the decision
  AND no human interaction required
```

**Scenario 3: Financial transaction flagged**
```gherkin
GIVEN a protocol defines "high_value_transaction" as high-risk
  AND diagnostic data includes: transaction amount=$50000, fraud_signals
WHEN an agent triggers hitl_checkpoint with risk_level="high"
THEN AI analysis detects fraud signals (confidence: 85%)
  AND triage presents evidence and suggested action
  AND human approves/rejects with rationale
  AND audit trail captures full decision context
```

**Scenario 4: Domain-agnostic - custom workflow**
```gherkin
GIVEN a custom protocol for "content_moderation"
  AND diagnostic data includes: post_content, toxicity_score, user_history
WHEN an agent triggers hitl_checkpoint with risk_level="medium"
THEN gate processes arbitrary JSON without field validation
  AND AI analyzes based on pattern matching (no domain assumptions)
  AND triage asks clarifying questions if needed
  AND audit trail stores domain-agnostic data
```

### Test Coverage Goals

- **Core Components:** 90%+ (StateManager, AuditLogger, Gate)
- **Integration Flows:** 80%+ (MCP → Gate → Audit)
- **Acceptance Scenarios:** 100% (all user stories tested)

### Test Execution

**Local Development:**
```bash
pytest tests/ -v --cov=hitl_server --cov-report=html
```

**CI/CD (GitHub Actions):**
- Run on every PR
- Python 3.11, 3.12 matrix
- Generate coverage report
- Block merge if < 85% coverage

---

## Non-Functional SLAs

### Performance (MVP Targets)

- **Checkpoint Evaluation:** < 100ms (p95) for protocol load + gate logic
- **Diagnostic Context Capture:** < 50ms for arbitrary JSON processing
- **AI Analysis Generation:** < 200ms for pattern matching + confidence scoring
- **State Persistence:** < 50ms for atomic write (StateManager)
- **Audit Trail Write:** < 50ms for incremental persist (AuditLogger)
- **Approval Queue:** < 1s to queue request in SQLite

### Reliability

- **Data Durability:** 100% - No data loss, atomic writes, crash-safe
- **Audit Trail Completeness:** 100% - Every checkpoint logged, incremental persist
- **State Consistency:** 100% - Per-run isolation prevents cross-contamination
- **Graceful Degradation:** Checkpoint fails safely if protocol missing (clear error message)

### Error Handling

- **Missing Protocol:** Return fail_response with protocol path guidance
- **Invalid Diagnostic Data:** Accept arbitrary JSON, no field validation errors
- **Approval Queue Full:** No limits for MVP (SQLite handles growth)
- **Web UI Unavailable:** Fallback to CLI mode automatically
- **Audit Write Failure:** Block checkpoint (DD-30 enforcement from QA Engine)

### Scalability (MVP - Not a Concern)

- **Local-only:** Single user, no concurrent requests
- **File System:** Local disk, no cloud storage limits
- **SQLite:** Handles thousands of approvals (sufficient for MVP)
- **Phase 2:** Add PostgreSQL for multi-user hosted tier

---

## Observability/Telemetry

### MVP Observability (Local Audit Trail Only)

**Audit Trail Events** (Logged to JSON):
- `checkpoint.triggered` - workflow_id, step_name, risk_level, diagnostic_data
- `checkpoint.auto_approved` - workflow_id, risk_level, protocol_rule
- `checkpoint.approval_required` - workflow_id, diagnostic_context, ai_analysis
- `approval.queued` - approval_id, risk_level, timestamp
- `approval.completed` - approval_id, decision, rationale, duration
- `error.protocol_missing` - workflow_id, protocol_name, timestamp
- `error.audit_write_failed` - run_id, error_message (critical)

**Summary Statistics** (Calculated on Demand):
- Total checkpoints processed
- Auto-approval rate (%)
- Human approval rate (%)
- Average approval latency
- AI analysis confidence distribution

**Debug Logging** (Python logging module):
- `DEBUG`: Protocol loading, gate evaluation logic
- `INFO`: Checkpoint results, approval decisions
- `WARNING`: Missing protocols, fallback modes
- `ERROR`: Audit write failures, state corruption

### Phase 2 Observability (Hosted Metrics)

- Prometheus metrics endpoint
- Grafana dashboards
- Real-time approval queue monitoring
- Compliance report generation

---

## Security & Privacy

### MVP Security (Local-Only)

**No Authentication Required** - Single-user local deployment
- No API keys (local MCP server)
- No user accounts
- No password management
- Phase 2: Add auth for hosted tier

**Data Privacy:**
- **Secrets in Diagnostic Data:** Caller's responsibility to redact (domain-agnostic, no auto-detection)
- **Audit Trail:** Stores whatever caller provides - no automatic PII filtering
- **Local Storage:** All data stays on user's machine (no cloud upload)
- **File Permissions:** Standard OS permissions for audit/state directories

**Threat Model (MVP):**
- **Threat:** Secrets logged to audit trail
  - **Mitigation:** Documentation warns users to redact secrets before passing diagnostic_data
- **Threat:** Audit trail tampering
  - **Mitigation:** Write-once files (no update capability), atomic writes
- **Threat:** State corruption
  - **Mitigation:** Atomic writes, per-run isolation, graceful handling of corrupted files

### Phase 2 Security (Hosted Tier)

- **Authentication:** OAuth, SSO (SAML)
- **Authorization:** Role-based access control (RBAC)
- **Secrets Management:** Vault integration for sensitive data
- **Encryption:** TLS in transit, AES-256 at rest
- **Data Retention:** Configurable (7 years for compliance)
- **GDPR:** Data deletion, right to access

---

## Rollout & Rollback

### MVP Rollout (4-Week Timeline)

**Week 1: Foundation**
- Copy StateManager, AuditLogger, BaseGate from QA Engine
- Adapt for domain-agnostic use (remove QA-specific constants)
- Write unit tests (TDD approach)

**Week 2: Core Gate**
- Implement HITLCheckpointGate (following QG Execution pattern)
- Integrate ProtocolParser (reuse from QA Engine)
- AI analysis generation (pattern matching + confidence scoring)
- Integration tests (MCP → Gate → Audit)

**Week 3: Approval Mechanism**
- CLI mode (Rich library for terminal formatting)
- SQLite approval queue
- Web UI skeleton (Next.js on localhost:3001)
- Diagnostic viewer UI

**Week 4: Polish & Launch**
- Documentation (README, protocol examples)
- 3 domain examples (QA, DevOps, Finance)
- Acceptance tests (BDD scenarios)
- GitHub repo launch (open-source)

### Rollout Strategy

**No Feature Flags** - Standalone product, no gradual rollout needed
- MVP launches as complete product
- Users install or don't install (no partial features)

**Dogfooding:**
- Internal use: Apply HITL to QA Engine Step 11 refactor (future task)
- Validation: Prove pattern works before public launch

**Launch Sequence:**
1. GitHub repo public (open-source)
2. Announce on Twitter, Hacker News, Reddit (r/programming, r/artificial)
3. Submit to Show HN (Hacker News)
4. Blog post: "Building EU AI Act Compliance into Any AI Agent"
5. Demo video: 3-domain examples (QA, DevOps, Finance)

### Rollback Plan

**Standalone Product** - No rollback needed (users uninstall if issues)
- Critical bug: Hot-fix patch release
- Major issue: Revert GitHub commit, release previous version

**Smoke Tests (Pre-Launch):**
1. Install MCP server → Success
2. Call `hitl_checkpoint` with low risk → Auto-approve
3. Call `hitl_checkpoint` with high risk → Queue approval
4. CLI mode approval → Logs decision to audit trail
5. Web UI mode approval → Displays diagnostic viewer
6. Audit trail written → File exists, valid JSON
7. State persisted → Run_id-based directory created

**Quality Gate (Must Pass Before Launch):**
- All unit tests pass (90%+ coverage)
- All integration tests pass
- All acceptance scenarios pass
- 3 domain examples working end-to-end
- Documentation complete (README, protocol examples)

---

---

**Next Steps:** Proceed to Phase 3 (Task Generation)

**Status:** Phase 2 Complete - PRD finalized with:
- Design decisions from Phase 1
- US compliance positioning (NIST AI RMF primary, EU AI Act secondary)
- Testing strategy integrated with testing skill protocol
- Regulatory compliance requirements validated

**Last Updated:** 2026-01-15

**Version:** 3.0 (Updated with US compliance positioning + testing integration)

---

## Document Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-15 | Initial PRD skeleton |
| 2.0 | 2026-01-15 | Updated with Phase 1 design decisions |
| 3.0 | 2026-01-15 | US compliance positioning, testing skill integration, regulatory validation |
