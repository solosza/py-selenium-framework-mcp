# Product Requirements Document: HITL Infrastructure

**Status:** Pending (awaiting Phase 1 approval)
**Version:** 1.0
**Last Updated:** 2026-01-15

---

## Introduction/Overview

*To be completed after Phase 1 design approval*

HITL (Human-in-the-Loop) Compliance Infrastructure is a cross-product platform that provides event-driven protocol enforcement for human oversight in agentic AI systems. It enables ANY AI product to achieve EU AI Act Article 14 compliance through:

- Markdown-based protocols (human-readable guidance)
- Smart gates (enforcement via MCP tools)
- Diagnostic transparency (full execution context)
- Progressive audit trails (EU AI Act Article 12)
- Compliance deliverables (control catalog, compliance matrix, risk register)

---

## Goals

*To be elaborated after Phase 1 approval*

1. Launch HITL Infrastructure MVP by March 2026 (before Aug 2 EU AI Act deadline)
2. Achieve 1,000 free tier users and 50 paid users in first 30 days
3. Extract and modularize Step 11 HITL from QA Engine as proof of concept
4. Establish "Powered by Isagawa HITL" as standard for agentic AI compliance
5. Generate $3K MRR by April 2026, scaling to $250K MRR by December 2026

---

## User Stories

*To be detailed after Phase 1 approval and clarifying questions*

**As a developer building agentic AI products, I want to...**
- Integrate HITL compliance in 90 minutes so I can focus on my core product
- Use familiar tools (MCP/REST API) so there's minimal learning curve
- Get EU AI Act compliance documentation so I can satisfy auditors

**As an enterprise deploying custom agents, I want to...**
- Add human oversight checkpoints to existing workflows
- Review pending approvals with full diagnostic context
- Generate audit trails for compliance reporting

**As a compliance officer, I want to...**
- Read human-readable protocols to understand oversight rules
- Access immutable audit trails for regulatory audits
- Map controls to EU AI Act requirements

---

## Functional Requirements

*To be expanded after clarifying questions with user*

### Core Infrastructure

1. Protocol Engine must parse markdown protocols with YAML frontmatter
2. Smart Gates must evaluate protocol rules and determine approval requirements
3. Checkpoint API must accept workflow_id, step_name, diagnostic_data, and risk_level
4. System must queue approval requests when protocol requires human review
5. System must auto-approve low-risk actions per protocol configuration

### Integration Layers

6. MCP Server must be installable via `npx -y @isagawa/hitl-server`
7. REST API must provide `/hitl/checkpoint` endpoint
8. Python SDK must provide `@HITLGate` decorator
9. JavaScript SDK must provide equivalent decorator/wrapper

### Human Review

10. Dashboard must display pending approvals with priority sorting
11. Diagnostic Viewer must show full execution context (inputs, outputs, errors, duration)
12. Approval actions must support: Approve, Reject, Request Changes, Escalate
13. System must support multi-level approval chains (L1: team lead, L2: manager, L3: compliance)

### Audit Trail

14. System must log every checkpoint decision with timestamp
15. Audit logs must include: workflow_id, step_name, risk_level, human_decision, reviewer_id, rationale
16. Audit logs must be immutable (write-once, read-many)
17. System must support audit trail export in JSON, CSV, and PDF formats

### Compliance Deliverables

18. System must auto-generate Control Catalog from protocols
19. System must auto-generate Compliance Matrix mapping controls to EU AI Act articles
20. System must maintain Risk Register with identified risks, owners, and mitigations

---

## Non-Goals (Out of Scope)

*To be confirmed with user*

1. Pattern recognition / ML-based risk scoring (Phase 2+)
2. White-label customization (Enterprise tier only)
3. Visual diff / screenshot comparison (future enhancement)
4. Integration with specific CI/CD pipelines (Phase 2+)
5. Custom protocol DSL beyond YAML+Markdown (keep simple)

---

## Design Considerations

*Links to design documents, UI mockups, component architecture*

**Design Document:** See `1-design-hitl-infrastructure.md`

**Architecture Pattern:** Event-Driven Protocol Enforcement System
- Event → Protocol Evaluation → Smart Gate → Human Review → Audit Log

**Technology Stack (Proposed):**
- MCP SDK (existing)
- FastAPI or Flask (REST API)
- Next.js (Dashboard)
- PostgreSQL (audit trails, workspaces)
- S3 + versioning (immutable backup)

---

## Technical Considerations

*Dependencies, constraints, integration requirements*

1. **Extract from QA Engine:** Step 11 HITL checkpoint logic
2. **Backward Compatibility:** QA Engine Step 11 must continue working during extraction
3. **MCP Integration:** Leverage existing MCP server patterns
4. **Database:** PostgreSQL with row-level security for multi-tenant isolation
5. **Authentication:** Support SSO (SAML, OAuth) + API key-based access

---

## Success Metrics

*How will success be measured?*

### Phase 1 (Launch - March 2026)
- 1,000 free tier users (MCP server installs)
- 50 paid users (Pro/Business tiers)
- $2.5K MRR

### Phase 2 (Growth - April-July 2026)
- 10 enterprise customers @ $2K-10K/mo
- $20-100K MRR
- 5,000+ free tier users

### Phase 3 (Platform Play - Aug 2026+)
- 50 enterprise customers @ avg $5K/mo
- $250K MRR
- "Powered by Isagawa HITL" badge adopted by 3+ major products

### Compliance Metrics
- 100% EU AI Act Article 14 compliance for all customers
- Average time to compliance: <90 days
- Audit success rate: 100% (all audits passed)

---

## Open Questions

*To be answered during clarifying questions phase*

1. **Protocol versioning:** How should protocol version changes be handled? (Breaking vs non-breaking)
2. **Pricing tiers:** Confirm Free ($0/100 checks), Pro ($49/1K checks), Business ($499/10K checks), Enterprise (custom)?
3. **Approval timeout defaults:** Auto-reject after 24 hours? Configurable per risk level?
4. **Multi-region support:** Single region (US) for MVP, or multi-region from start?
5. **Notification preferences:** Which channels are mandatory (email, Slack, Discord, PagerDuty)?

---

## Test Strategy (MVP)

*To be detailed during Phase 2 completion*

### Unit Tests
- Protocol parser (YAML + markdown)
- Risk evaluator (protocol rule evaluation)
- Gate logic (approval required vs auto-approve)
- Audit trail writer

### Integration Tests
- MCP server → Gate → Dashboard flow
- REST API → Gate → Database
- SDK decorator → API call → Audit log

### Acceptance Tests (GIVEN/WHEN/THEN)

**Scenario 1: High-risk action requires approval**
- GIVEN a protocol defines "production_changes" as high-risk
- WHEN an agent triggers hitl_checkpoint with risk_level="high"
- THEN approval request is queued for human review
- AND execution blocks until human approves

**Scenario 2: Low-risk action auto-approved**
- GIVEN a protocol defines "read_operations" as low-risk
- WHEN an agent triggers hitl_checkpoint with risk_level="low"
- THEN checkpoint returns "auto_approved"
- AND audit trail logs the decision

*Additional scenarios to be defined during clarifying questions*

---

## Non-Functional SLAs

*Performance targets, reliability, error handling*

- **Latency:** Checkpoint evaluation < 100ms (p95)
- **Availability:** 99.9% uptime (SLA for paid tiers)
- **Audit Trail Durability:** 100% (no data loss, immutable logs)
- **Approval Queue Processing:** < 1 second to queue request

---

## Observability/Telemetry

*Events, logs, metrics to emit*

**Events:**
- `hitl.checkpoint.triggered` (workflow_id, step_name, risk_level)
- `hitl.approval.requested` (approval_id, risk_level, reviewer_id)
- `hitl.approval.completed` (approval_id, decision, duration)
- `hitl.auto_approved` (workflow_id, risk_level)

**Metrics:**
- Checkpoint throughput (requests/minute)
- Approval latency (time from request to decision)
- Auto-approval rate (percentage)
- Audit trail write latency

---

## Security & Privacy

*Threats, abuse cases, data handling*

- **API Keys:** Scoped to workspace, rotate every 90 days
- **Secrets:** No secrets in logs or audit trails
- **Data Retention:** Audit trails retained per compliance requirements (7 years default)
- **GDPR:** Support data deletion requests (mark as deleted, retain audit trail hash)

---

## Rollout & Rollback

*Feature flags, phased rollout, smoke tests*

**Feature Flags:**
- `hitl_infrastructure_enabled` (default: true for new workspaces)
- `protocol_v2_enabled` (default: false, opt-in for protocol version 2)

**Rollout Plan:**
1. Dogfood in QA Engine (Week 1-2)
2. Private beta (5-10 early adopters, Week 3-4)
3. Public beta (open registration, Week 5-6)
4. General availability (March 2026)

**Rollback Plan:**
- Smoke test: Verify checkpoint can queue approval and return result
- Rollback: Feature flag disable + route to previous Step 11 implementation

---

**Next Steps:** Proceed to Phase 3 (Task Generation) after user review and approval

**Status:** Pending Phase 1 approval

**Last Updated:** 2026-01-15
