# Phase 1: Design Discussion - HITL Infrastructure

## Project Overview

**Product:** HITL (Human-in-the-Loop) Compliance Infrastructure
**Category:** Cross-Product Platform (AI Management Layer)
**Target Market:** Companies building agentic AI products, enterprises deploying custom agents, framework developers
**Status:** Phase 1 Design Complete (Awaiting Approval)
**MVP Timeline:** 4 weeks (February 2026 launch target)
**Architecture:** Event-Driven Protocol Enforcement System (Protocols + Smart Gates)

---

## Purpose & Scope

### What Problem Does This Solve?

Every agentic AI product needs EU AI Act Article 14 compliance by August 2, 2026 (6 months away). Penalties: €35M or 7% global revenue.

Existing HITL tools (7+ MCP servers found) offer simple approval buttons but lack:
- Compliance-first design (no EU AI Act mapping)
- Diagnostic transparency (no execution context)
- Progressive audit trails (no immutable logging)
- Multi-checkpoint workflows (one-off approvals only)

### What Does This Module Do?

HITL Infrastructure = The compliance layer for agentic AI. Drop-in human oversight infrastructure (MCP server + API + SDK) that makes ANY AI product EU AI Act Article 14 compliant.

### Architectural Principle: Modular & Integration-Ready

**Core Design Principle:** HITL Infrastructure MUST be modular and integrate seamlessly into ANY system without forcing dependencies or architectural choices.

**Modular Architecture:**

```
┌─────────────────────────────────────────────────┐
│         HITL Core Engine (Framework-Agnostic)   │
│  - Protocol Parser                              │
│  - Risk Evaluator                               │
│  - Checkpoint Logic                             │
│  - No external dependencies                     │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│              Adapter Layer                      │
│  - Storage Adapter (use theirs OR ours)        │
│  - Auth Adapter (use theirs OR ours)           │
│  - Event Adapter (webhooks, callbacks)         │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│         Integration Methods (Choose Any)        │
│  - MCP Server                                   │
│  - REST API                                     │
│  - SDK Decorators                               │
└─────────────────────────────────────────────────┘
```

**Integration Flexibility:**

| Component | Host System Option | Isagawa Hosted Option |
|-----------|-------------------|---------------------|
| **Database** | Use your PostgreSQL/MySQL/MongoDB | Use Isagawa's managed database |
| **Auth** | Use your SSO/OAuth/API keys | Use Isagawa's auth system |
| **Dashboard** | Embed in your UI via iframe/component | Use Isagawa's hosted dashboard |
| **Audit Storage** | Write to your S3/GCS/Azure Blob | Use Isagawa's immutable audit storage |
| **Notifications** | Webhooks to your system | Isagawa's Slack/Email/Discord |

**Seamless Integration Examples:**

**Example 1: QA Engine Integration (Dogfooding)**
```python
# QA Engine uses HITL as standalone module
from isagawa_hitl import HITLCheckpoint

# Uses QA's own database and auth
checkpoint = HITLCheckpoint(
    storage=qa_engine_db,  # QA's existing PostgreSQL
    auth=qa_engine_auth,   # QA's existing auth
    dashboard_url=qa_dashboard  # Embedded in QA's UI
)

@checkpoint.gate(step="execute_test", risk_level="high")
def execute_test(test_data):
    return run_test(test_data)
```

**Example 2: External Product Integration**
```python
# External product uses Isagawa's hosted infrastructure
from isagawa_hitl import HITLCheckpoint

checkpoint = HITLCheckpoint(
    api_key="prod_xxx",  # Isagawa hosted
    workspace_id="acme-corp"
)

@checkpoint.gate(step="deploy_to_prod", risk_level="critical")
def deploy():
    return deploy_service()
```

### MVP Scope (4-Week Build)

**In Scope for MVP:**
- **Modular HITL Core Engine** (framework-agnostic, zero forced dependencies)
- **Adapter Layer** (storage, auth, events - bring your own OR use ours)
- **All three integration layers:**
  - MCP Server (drop-in for Claude Code, Cline)
  - REST API (any platform)
  - SDK Decorators (Python/JS)
- Human review dashboard with **diagnostic-rich viewer** (embeddable OR hosted)
- Progressive audit trail (PostgreSQL + S3 immutable backup) - **configurable storage**
- **Freemium + paid pricing** (Free → Pro $49 → Business $499 → Enterprise)
- **US region only** (single region for MVP)
- Compliance deliverables (control catalog, compliance matrix, risk register)

**Out of Scope for MVP (Phase 2):**
- Screenshots in dashboard
- Historical pattern analysis
- Multi-region support (EU region)
- White-label customization (enterprise feature)
- Pattern recognition / ML-based risk scoring

---

## Design Options Comparison

### Option 1: Policy Engine (OPA - Open Policy Agent)

**Architecture:** Declarative policy-as-code using Rego DSL

```rego
# Policy defines when approval needed
package hitl
approve_needed {
    input.risk_level == "high"
    input.action_type == "production_change"
}
```

**Pros:**
- ✅ Mature standard (CNCF graduated)
- ✅ Declarative, testable policies
- ✅ Decoupled decision-making

**Cons:**
- ❌ Rego learning curve (new DSL)
- ❌ Focused on authorization, not workflow management
- ❌ Policies are code (not human-readable for auditors)
- ❌ No narrative guidance layer

**Assessment:** Wrong abstraction layer. OPA solves "can you do this?" (authorization). We solve "should human review this?" (oversight).

---

### Option 2: Workflow Engine (Temporal)

**Architecture:** Durable execution engine for distributed workflows

```python
@workflow.defn
class HITLWorkflow:
    @workflow.run
    async def run(self, action):
        approval = await workflow.wait_condition(lambda: self.approved)
        return approval
```

**Pros:**
- ✅ Durable execution (survives crashes)
- ✅ Code-based (familiar to developers)
- ✅ Enterprise-grade, proven at scale

**Cons:**
- ❌ Machine-to-machine focus (not human-centric)
- ❌ Workflows are code (not protocols)
- ❌ Complex for simple approval workflows
- ❌ Vendor lock-in (Temporal Cloud)

**Assessment:** Over-engineered for HITL. Temporal excels at long-running distributed workflows. We need lightweight checkpoints with human oversight.

---

### Option 3: Rules Engine (Traditional BRE)

**Architecture:** Business logic evaluation engine

```python
if risk_level > threshold and action_type in high_risk_actions:
    require_approval = True
```

**Pros:**
- ✅ Mature pattern (decades of use)
- ✅ Handles complex conditions

**Cons:**
- ❌ Rules scattered in code/DSL (not centralized)
- ❌ No narrative guidance
- ❌ Focused on automated decisions (not HITL)

**Assessment:** Rules engines answer "what should happen?" We need "should human review?" with diagnostic context. Wrong focus.

---

### Option 4: State Machine (AWS Step Functions, Azure Durable Functions)

**Architecture:** Event-driven state transitions

```json
{
  "States": {
    "CaptureContext": {"Type": "Task", "Next": "WaitForApproval"},
    "WaitForApproval": {"Type": "Task", "Next": "Execute"}
  }
}
```

**Pros:**
- ✅ Visual workflow definition
- ✅ Event-driven (72% industry adoption)
- ✅ Cloud-native options

**Cons:**
- ❌ YAML/JSON config (not human-readable protocols)
- ❌ No guidance narrative
- ❌ Requires external events
- ❌ Vendor lock-in

**Assessment:** Close but config-based, not protocol-driven. Also cloud vendor lock-in.

---

### Option 5: Event-Driven Protocol Enforcement System (RECOMMENDED)

**Architecture:** Markdown protocols (guidance) + MCP tools (enforcement)

```markdown
# HITL Oversight Protocol

## When Approval Required
- High-risk actions (production changes, financial transactions)
- Novel situations (no historical precedent)
- EU AI Act Article 14 requirements
- Error patterns (repeated failures)
```

```python
@mcp_tool
def hitl_checkpoint(action, risk_level, diagnostic_data):
    """Smart gate that enforces HITL protocol"""
    protocol = load_protocol("hitl-oversight")

    if protocol.requires_approval(risk_level, action):
        diagnostic_pkg = protocol.build_diagnostic_package(diagnostic_data)
        approval = queue_for_human_review(diagnostic_pkg)
        log_audit_trail(action, approval, protocol.version)
        return approval

    return {"status": "auto_approved", "rationale": "Low risk action"}
```

**What This Is (Standard Patterns):**
- Event-driven architecture (gate triggered by events)
- Rule-based workflow (protocol defines rules)
- State machine (gates control flow transitions)
- Audit trail (immutable compliance logging)

**The Innovation:**
- Protocols as first-class citizen (markdown, not code)
- Human-readable (auditors can read protocols)
- Compliance-first design (EU AI Act mapped)
- Diagnostic transparency (full execution context)

**Pros:**
- ✅ Human-readable protocols (markdown)
- ✅ Separation of guidance vs enforcement
- ✅ MCP-native (already built in QA Engine)
- ✅ Auditable (protocol + gate logs)
- ✅ Novel differentiation (no competitor has this)
- ✅ Compliance-first by design

**Cons:**
- ❌ Not standard (need to build tooling)
- ❌ Unproven at scale (but validated in QA Engine Step 11)
- ❌ Need to educate market

**Why This Wins:**
1. **Human-readable = compliance advantage** - EU AI Act Article 14 requires humans to understand AI system. Markdown protocols satisfy this. Code/DSL does not.
2. **We're solving oversight, not authorization** - Different domain than OPA/Temporal
3. **Already validated** - Step 11 HITL in QA Engine proves the pattern works
4. **MCP-native = instant distribution** - 97M+ monthly SDK downloads

---

## User-Facing Elements

### Integration Experience (Developer)

**Layer 1: MCP Server (Drop-in)**
```json
{
  "mcpServers": {
    "isagawa-hitl": {
      "command": "npx",
      "args": ["-y", "@isagawa/hitl-server"]
    }
  }
}
```

**Layer 2: REST API (Any Platform)**
```python
import requests

response = requests.post('https://api.isagawa.com/hitl/checkpoint', {
    'workflow_id': 'test-execution',
    'step_name': 'execute_test',
    'diagnostic_data': {...},
    'requires_approval': True
})

if response.json()['status'] == 'approved':
    execute_action()
```

**Layer 3: SDK (Decorator Pattern)**
```python
from isagawa_hitl import HITLGate

@HITLGate(
    step_name="execute_test",
    diagnostic_capture=True,
    compliance_mapping="EU_AI_Act_Article_14"
)
def execute_test(test_data):
    return run_test(test_data)
```

### Human Review Dashboard

**Queue View:**
- Pending approvals sorted by priority/risk level
- Risk indicator (low/medium/high/critical)
- Quick actions: Approve, Reject, Escalate, Request Changes

**Diagnostic Viewer:**
- Full execution context (inputs, outputs, duration, exit code)
- Error messages and stack traces
- Screenshots (if applicable)
- Historical patterns ("Similar action failed 3 times in past week")
- Environment configuration

**Approval Actions:**
- Approve with rationale (optional)
- Reject with feedback
- Request changes (structured feedback form)
- Escalate to higher authority

### Compliance Reports (Auto-Generated)

**Control Catalog:**
- List of all checkpoints/gates
- How each is enforced at runtime
- Mapping to EU AI Act articles

**Compliance Matrix:**
- Control → Article 14 requirement mapping
- Evidence of operational enforcement

**Risk Register:**
- Identified risks per workflow
- Risk owners
- Mitigation strategies

---

## Integration Points

### Modular System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  HOST SYSTEM (Your Product)                 │
│  - Your application code                                    │
│  - Your database                                            │
│  - Your auth system                                         │
└─────────────────────────────────────────────────────────────┘
                          ↓ (calls)
┌─────────────────────────────────────────────────────────────┐
│             HITL Integration Layer (Choose One)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  MCP Server  │  │  REST API    │  │  SDK Library │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          ↓ (delegates to)
┌─────────────────────────────────────────────────────────────┐
│            HITL Core Engine (Framework-Agnostic)            │
│  - Protocol Parser (markdown → rules)                       │
│  - Risk Evaluator (evaluate checkpoint)                     │
│  - Checkpoint Logic (approve/reject/queue)                  │
│  - NO external dependencies                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓ (uses)
┌─────────────────────────────────────────────────────────────┐
│                    Adapter Layer (Pluggable)                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │Storage Adapter│  │ Auth Adapter │  │Event Adapter │     │
│  │(YOUR DB or   │  │(YOUR auth or │  │(YOUR webhooks│     │
│  │ OURS)        │  │ OURS)        │  │ or OURS)     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          ↓ (persists to)
┌─────────────────────────────────────────────────────────────┐
│               EITHER: Your Infrastructure                   │
│  - Your PostgreSQL/MongoDB                                  │
│  - Your S3/GCS/Azure Blob                                   │
│  - Your SSO/OAuth                                           │
│                     OR                                       │
│              Isagawa Hosted Infrastructure                  │
│  - Isagawa managed PostgreSQL                               │
│  - Isagawa S3 audit storage                                 │
│  - Isagawa auth system                                      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
AI Agent Workflow
    ↓
HITL Checkpoint (event triggered via MCP/REST/SDK)
    ↓
HITL Core Engine → Protocol Evaluation (requires approval?)
    ↓
YES → Queue for Human Review → Dashboard (embeddable OR hosted)
          ↓
      Human Decision (approve/reject)
          ↓
      Storage Adapter → Audit Trail (YOUR storage OR ours)
          ↓
      Return to Agent Workflow
    ↓
NO → Auto-approve (low risk) → Storage Adapter → Continue
```

### External Integrations

**Notification Systems:**
- Slack (webhook for approval requests)
- Discord (via MCP server)
- Email (for escalations)
- PagerDuty (critical approvals)

**Identity Providers:**
- SSO integration (SAML, OAuth)
- Role-based access control (RBAC)
- Multi-level approval chains

**Existing Systems:**
- QA Engine (first customer, dogfooding)
- Consumer Execution Engine (planned)
- Agent Management Layer (planned)

### Dependencies

**Core HITL Engine (Zero External Dependencies):**
- Protocol parser (markdown → structured data) - pure Python
- Risk evaluator - pure Python
- Checkpoint logic - pure Python
- NO framework dependencies (Flask, FastAPI, etc.)
- NO database dependencies (PostgreSQL, MongoDB, etc.)

**Adapter Layer (Optional Dependencies):**
- Storage Adapter interface (implementations for PostgreSQL, MongoDB, S3, local files)
- Auth Adapter interface (implementations for JWT, OAuth, API keys)
- Event Adapter interface (implementations for webhooks, MQTT, Redis Pub/Sub)

**Integration Methods:**
- MCP Server: MCP SDK (already using)
- REST API: FastAPI (lightweight wrapper over core)
- SDK: Pure Python/JS (thin client over core OR REST API)

**Dashboard (Optional - for hosted version):**
- Web framework (Next.js or similar)
- Authentication (NextAuth.js or similar)
- Database (PostgreSQL for hosted audit trail)

---

---

## Impact Assessment

### Who Calls This Code?

**Phase 1 (MVP):**
- QA Execution Engine (dogfooding Step 11 HITL)
- Direct API customers (early adopters)

**Phase 2 (Growth):**
- Consumer Execution Engine
- Agent Management Layer
- External products (TestMu AI, Virtuoso, mabl integrations)

### What Depends on Current Behavior?

**QA Engine Step 11:**
- Currently embedded in QA workflow
- Need to extract into standalone module
- Backward compatibility: QA Engine continues working during extraction

### What Will Break?

**Nothing initially** (net-new infrastructure)

**Future risk:**
- If we change protocol format → existing protocols need migration
- If we change API contract → SDK versions need updates
- Mitigation: Semantic versioning + deprecation notices

### Migration Path

**From QA Engine Step 11 → Standalone HITL:**
1. Extract checkpoint logic into shared module
2. Keep Step 11 working (call shared module)
3. Launch standalone HITL Infrastructure
4. QA Engine becomes customer of HITL Infrastructure
5. Marketing: "QA Engine powered by Isagawa HITL"

---

## Design Decisions

### 1. Architecture Pattern

**Decision:** Event-Driven Protocol Enforcement System (Option 5) - The Isagawa Way

**Rationale:**
- Human-readable protocols = compliance advantage
- Proven in QA Engine Step 11
- MCP-native = distribution built-in
- Novel differentiation vs OPA/Temporal

### 1a. Modular Architecture (CRITICAL)

**Decision:** Framework-agnostic core with adapter layer - "Bring Your Own Infrastructure"

**What This Means:**
- **HITL Core Engine** has ZERO forced dependencies (no framework lock-in)
- **Adapter Layer** for storage, auth, events (use theirs OR use ours)
- **Integration is opt-in** (choose MCP, REST API, or SDK)
- **Embeddable OR hosted** dashboard

**Why This Matters:**
- QA Engine can use HITL with its own database and auth (seamless integration)
- External products can use Isagawa's hosted infrastructure (zero setup)
- No vendor lock-in (can migrate to self-hosted later)
- Follows Stripe model: works with ANY tech stack

**Example Pattern:**
```python
# Option 1: Use your infrastructure
HITLCheckpoint(storage=your_db, auth=your_auth)

# Option 2: Use Isagawa's hosted infrastructure
HITLCheckpoint(api_key="prod_xxx")
```

### 2. Integration Layers (MVP Scope)

**Decision:** All three layers for MVP

**What:**
- Layer 1: MCP Server (drop-in for Claude Code, Cline, MCP ecosystem)
- Layer 2: REST API (any platform - Python, JS, Go agents)
- Layer 3: SDK Decorators (Python/JS)

**Rationale:**
- MCP only = 1M addressable market
- All three = 100M+ addressable market (10x expansion)
- ~1 week total dev time (2-3 days MCP, 1 day REST, 1 day SDK)
- Stripe playbook: launched with multiple integration options from day 1
- Best DX wins developer adoption

### 3. Human Review Dashboard (MVP Scope)

**Decision:** Diagnostic-rich review (basic version)

**MVP Features:**
- Full execution context (inputs, outputs, errors, duration, risk level)
- Queue with risk indicators
- Approve/Reject/Escalate actions

**Phase 2 Features:**
- Screenshots
- Historical patterns
- Structured feedback forms

**Rationale:**
- Diagnostic transparency is core differentiation (our moat vs 7+ competitors)
- Simple approval queue is commoditized (everyone has this)
- Already capturing this data in QA Engine Step 11
- Basic version sufficient for MVP, rich features for Phase 2

### 4. Pricing Strategy

**Decision:** Freemium + Paid tiers

**Pricing Structure:**
```
Free Tier:
- 100 checkpoints/month
- 7-day audit retention
- Community support

Pro Tier: $49/month
- 1,000 checkpoints/month
- 90-day audit retention
- Email support

Business Tier: $499/month
- 10,000 checkpoints/month
- 1-year audit retention
- Priority support
- Multi-level approval chains

Enterprise Tier: Custom pricing
- Unlimited checkpoints
- 7-year audit retention
- White-label (Phase 2)
- Multi-region support
```

**Rationale:**
- Industry standard for dev tools (Stripe, Vercel, Auth0, Sentry all use this model)
- Free tier drives viral adoption via MCP distribution
- 2-5% conversion rate (industry standard)
- 1,000 free users → 20-50 paid users → $1K-2.5K MRR

### 5. Multi-Region Support

**Decision:** Phase 2 (not MVP)

**MVP:** US region only

**Phase 2 (before Aug 2026):** Add EU region

**Rationale:**
- EU AI Act applies to companies operating in EU (not where servers are hosted)
- Audit trails can live in US as long as EU auditors can access them
- GDPR compliance matters for data residency, but not launch blocker
- Multi-region adds 3-4 weeks dev time + $2K-4K/mo infrastructure cost
- Better to validate product-market fit with US region first

### 6. Launch Sequence

**Decision:** Standalone HITL first → Dogfood in QA Engine → Launch both

**Timeline:**
```
Week 1-2: Build standalone HITL Infrastructure
  - MCP Server
  - REST API
  - SDK Decorators
  - Basic Dashboard (diagnostic viewer)
  - Audit trail storage

Week 3: Dogfood in QA Engine
  - Extract Step 11 HITL logic
  - Replace with HITL Infrastructure API calls
  - Validate: Does it work as integrated system?

Week 4: Launch both
  - HITL Infrastructure: Public (freemium + paid)
  - QA Engine: Private beta
  - Marketing: "QA Engine powered by Isagawa HITL"
```

**Rationale - This Proves:**
✅ Product works independently (not just QA-specific)
✅ Integration story (if QA can integrate, anyone can)
✅ Platform thesis ("QA Engine powered by Isagawa HITL")
✅ Immediate revenue path (sell HITL standalone while QA is in beta)
✅ De-risks QA launch (QA isn't dependent on HITL being perfect)

This is the Stripe playbook:
- Stripe launched payments infrastructure FIRST
- Then used it in their own Stripe Atlas product
- Proved the infrastructure works by using it themselves

### 7. Protocol Format

**Decision:** Hybrid markdown with YAML frontmatter

**Rationale:**
- Human-readable (auditors)
- Machine-parseable (automation)
- Extensible (add fields without breaking)

### 8. Approval Timeout

**Decision:** Configurable with safe defaults (auto-reject)

**Rationale:**
- Flexibility per workflow needs
- Safe default (auto-reject) prevents compliance violations
- Escalation chains for critical workflows

### 9. Audit Trail

**Decision:** PostgreSQL + S3 immutable backup

**Rationale:**
- Queryable (PostgreSQL for dashboard)
- Immutable (S3 versioning for compliance)
- Tamper-evident (cryptographic signatures)

### 10. Multi-Tenant Isolation

**Decision:** Workspace-based with row-level security

**Rationale:**
- Simpler than database-per-tenant
- Secure with PostgreSQL RLS
- Cost-effective

---

## Next Steps

**Phase 1 Design: ✅ COMPLETE** (awaiting user approval to proceed)

**Once approved, proceed to:**
1. **Phase 2 (Define PRD):** Create detailed Product Requirements Document
2. **Phase 3 (Divide Tasks):** Generate task list from PRD
3. **Phase 4 (Deliver):** Execute tasks and ship MVP

**MVP Implementation Timeline: 4 Weeks**

```
Week 1-2: Build Standalone HITL Infrastructure
  - MCP Server (2-3 days)
  - REST API (1 day)
  - SDK Decorators (1 day)
  - Basic Dashboard with diagnostic viewer (2-3 days)
  - Audit trail storage (PostgreSQL + S3) (1-2 days)

Week 3: Dogfood Integration
  - Extract QA Engine Step 11 HITL logic
  - Replace with HITL Infrastructure API calls
  - Integration testing
  - Validate end-to-end workflow

Week 4: Launch Preparation
  - HITL Infrastructure: Public launch (freemium + paid)
  - QA Engine: Private beta (powered by HITL)
  - Marketing materials
  - Documentation
```

**Launch Target:** February 2026 (4 weeks from now)

**Post-Launch Roadmap:**
- **Phase 2 Features** (March-July 2026): Screenshots in dashboard, historical patterns, multi-region support (EU)
- **EU AI Act Compliance Ready:** August 2, 2026

---

## References

**Research Sources:**
- [HITL Design Patterns 2026 - Parseur](https://parseur.com/blog/future-of-hitl-ai)
- [Event-Driven Architecture Guide - Estuary](https://estuary.dev/blog/event-driven-architecture/)
- [Workflow vs Rules Engine - cflowapps](https://www.cflowapps.com/workflow-engine-or-business-rules-engine-comparison/)
- [Open Policy Agent Documentation](https://www.openpolicyagent.org/docs)
- [Temporal Workflow Engine Principles](https://temporal.io/blog/workflow-engine-principles)
- [EU AI Act Article 14 - Human Oversight](https://artificialintelligenceact.eu/article/14/)
- [Audit Trail Compliance - IntuitionLabs](https://intuitionlabs.ai/articles/audit-trails-21-cfr-part-11-annex-11-compliance)

**Competitive Analysis:**
- See `.business/intel_reports/competitive_intel_consolidated_HITL_2026-01-14.md` for complete competitive landscape

---

**Status:** Phase 1 Design Complete - Awaiting user approval to proceed to Phase 2 (PRD creation)

**Design Decisions Made:**
1. ✅ Architecture: Event-Driven Protocol Enforcement System (Isagawa way)
2. ✅ Integration Layers: All three (MCP + REST + SDK) for MVP
3. ✅ Dashboard: Diagnostic-rich review (basic version)
4. ✅ Pricing: Freemium + Paid tiers (Free → Pro $49 → Business $499 → Enterprise)
5. ✅ Multi-Region: Phase 2 (US-only for MVP)
6. ✅ Launch Sequence: Standalone first → Dogfood in QA → Launch both

**Ready to proceed with:** Phase 2 (PRD creation)

**Last Updated:** 2026-01-15
