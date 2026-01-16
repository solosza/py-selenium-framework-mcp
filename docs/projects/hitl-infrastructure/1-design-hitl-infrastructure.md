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

### The Isagawa Way - Protocols + Smart Gates

**Core Design Principle:** Use the proven pattern from QA Engine - Protocols guide, Smart Gates enforce AND provide diagnostic context.

**Architecture (Same as QA Engine):**

```
┌─────────────────────────────────────────────────┐
│   HITL Protocol (Markdown Skill)                │
│   - Defines oversight rules                     │
│   - Human-readable guidance                     │
│   - EU AI Act compliance mapping                │
└─────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────┐
│   Smart Gate: hitl_checkpoint (MCP Tool)        │
│   - Validates execution results                 │
│   - Captures diagnostic context                 │
│   - Generates AI analysis (hypothesis, evidence)│
│   - Provides fix hints                          │
│   - Returns structured response                 │
└─────────────────────────────────────────────────┘
                        ↓
          ┌─────────────┴─────────────┐
          ▼                           ▼
    ┌──────────┐              ┌──────────────┐
    │ PASS     │              │ HITL TRIAGE  │
    │ (auto)   │              │ (human)      │
    └──────────┘              └──────────────┘
                                      ↓
                      ┌───────────────────────────┐
                      │ Triage Conversation       │
                      │ - Show diagnostic data    │
                      │ - AI analysis             │
                      │ - Structured options      │
                      │ - Custom guidance         │
                      └───────────────────────────┘
                                      ↓
┌─────────────────────────────────────────────────┐
│   Audit Trail (Progressive Logging)             │
│   - Checkpoint triggered                        │
│   - Diagnostic data captured                    │
│   - AI analysis logged                          │
│   - Human decision recorded                     │
└─────────────────────────────────────────────────┘
```

**Why This Works:**
- **Proven in QA Engine:** 11-step workflow with 11 quality gates
- **Step 11 IS HITL:** Extract it, make it domain-agnostic
- **Smart Gates do more than validate:** They capture context, generate analysis, provide fix hints
- **Same pattern, different domain:** Oversight instead of QA validation

### Smart Gates Provide Diagnostic Context

**Critical Design Pattern:** Smart Gates don't just return pass/fail - they build the diagnostic package.

**From QA Engine Step 11 (qg_execution):**

```python
# Smart Gate captures diagnostic context
@mcp_tool
def qg_execution(test_result):
    # 1. Validate execution
    if test_result["status"] == "passed":
        return pass_response()

    # 2. Capture diagnostic data (7 types)
    diagnostic_data = capture_diagnostic_context(test_result)

    # 3. Generate AI analysis
    ai_analysis = generate_hypothesis(diagnostic_data)

    # 4. Return structured fail response with rich context
    return fail_response(
        error="Test failed",
        fix_hint=format_triage_presentation(diagnostic_data, ai_analysis),
        metadata={
            "diagnostic_data": diagnostic_data,
            "ai_analysis": ai_analysis,
            "triage_options": ["fix_app", "fix_test", "investigate"]
        }
    )
```

**HITL Infrastructure Uses Same Pattern:**

```python
# Domain-agnostic Smart Gate
@mcp_tool
def hitl_checkpoint(step, diagnostic_data, risk_level):
    # 1. Validate against protocol
    protocol = load_protocol("hitl-oversight")

    # 2. Low risk + success = auto-approve
    if protocol.is_low_risk(risk_level, diagnostic_data):
        return pass_response(
            rationale="Low risk, auto-approved",
            metadata={"diagnostic_data": diagnostic_data}
        )

    # 3. High risk OR failure = capture context + generate analysis
    ai_analysis = generate_hypothesis(diagnostic_data)
    fix_suggestions = generate_fix_hints(diagnostic_data, ai_analysis)

    # 4. Return HITL triage response (not fail, but "needs human")
    return hitl_triage_response(
        checkpoint=step,
        diagnostic_data=diagnostic_data,  # Whatever caller provided
        ai_analysis=ai_analysis,
        fix_suggestions=fix_suggestions,
        triage_options=["approve", "reject", "investigate", "custom"]
    )
```

**Key Difference from Simple Approval Tools:**

| Simple Approval | Isagawa Smart Gates |
|-----------------|---------------------|
| "Action needs approval" | "Action needs approval BECAUSE..." |
| User clicks approve/reject | User sees diagnostic context, AI analysis, evidence |
| No context captured | Full diagnostic package built by gate |
| Binary decision | Conversational triage with options |

**This is our moat:** Smart Gates provide the diagnostic transparency that makes human oversight meaningful.

**Integration Examples:**

**Example 1: QA Engine Integration (Dogfooding)**
```python
# QA Engine Step 11 calls hitl_checkpoint MCP tool
result = await mcp_client.call_tool(
    "hitl_checkpoint",
    workflow_id="qa-test-run",
    step_name="execute_test",
    diagnostic_data=test_result,
    risk_level="high"
)
```

**Example 2: External Product Integration (REST API)**
```python
import requests

response = requests.post('https://api.isagawa.com/hitl/checkpoint',
    headers={'Authorization': 'Bearer prod_xxx'},
    json={
        'workflow_id': 'deploy-prod',
        'step_name': 'deploy_service',
        'diagnostic_data': deployment_context,
        'risk_level': 'critical'
    }
)
```

**Example 3: SDK Decorator (Python)**
```python
from isagawa_hitl import checkpoint

@checkpoint(step="execute_test", risk_level="high")
def execute_test(test_data):
    return run_test(test_data)
```

### Human Approval Mechanism (The Step 11 Pattern)

**Core Pattern:** Context-aware approval - simple pass/fail OR full conversational triage.

**Inspired by QA Engine Step 11 HITL:**
- Test passed → Auto-approve (no human interaction)
- Test failed → Full triage conversation (AI analysis + structured options + custom guidance)

#### CLI Conversation (Terminal-Native)

**Simple Checkpoint (Auto-Pass):**
```
✓ HITL Checkpoint: execute_test (risk: low)
  Status: PASSED
  Duration: 2.3s

  → Auto-approved (low risk, no issues detected)
```

**Complex Checkpoint (Full Triage):**
```
⚠️  HITL Checkpoint: deploy_to_production (risk: critical)

Action: Production deployment validation
Status: FAILED
Duration: 15.2s

Error: Deployment validation failed - DATABASE_URL missing
Location: deployment_config/validation.py:45

AI Analysis (Confidence: 85%):
Missing environment variable DATABASE_URL in production config

Evidence:
- Environment check returned None for DATABASE_URL
- Previous successful deployments included this variable
- Production config validation expects this key

Suggested Fix:
Add DATABASE_URL to production environment configuration

==========================================

Diagnostic Data Provided:
{
  "deployment_config": {
    "environment": "production",
    "version": "v2.1.0",
    "target_region": "us-east-1"
  },
  "environment_vars": {
    "API_KEY": "[REDACTED]",
    "DATABASE_URL": null  ← Missing
  },
  "service_health": {
    "database": "unreachable",
    "api": "healthy"
  },
  "validation_results": {
    "config_complete": false,
    "connectivity_test": "failed"
  }
}

HOW SHOULD WE PROCEED?

1. Fix Configuration Issue
   → Add missing DATABASE_URL
   → AI can guide configuration update
   → Retry deployment after fix

2. Validation Logic Issue
   → Validation check is incorrect
   → DATABASE_URL not actually needed
   → AI investigates and proposes fix

3. Investigate Further
   → Show more diagnostic context
   → AI asks domain-specific questions
   → Review evidence before deciding

4. [Custom guidance]
   → Provide your own instructions
   → AI adapts to your domain context

Enter choice (1-4) or type custom guidance:
_
```

**Key Features:**
- **Domain-agnostic diagnostic capture:** Caller provides ANY JSON (no prescribed fields)
- **AI adapts to data:** Analyzes whatever is provided (deployment config, test output, payment data, etc.)
- **Evidence-based:** Shows supporting data from provided context
- **Conversational triage:** AI can ask domain-specific clarifying questions
- **Structured options + custom guidance:** 3 common paths + open-ended interaction

#### Local Web UI (Rich Diagnostic Viewer)

**Same triage workflow, but in web interface:**
- Left panel: Approval queue (pending checkpoints)
- Center: Rich diagnostic viewer (formatted data, syntax highlighting)
- Right: AI analysis panel (hypothesis, confidence, evidence)
- Bottom: Triage actions (buttons for 3 options + text area for custom)

**Auto-opens browser on checkpoint:**
```
⚠️  HITL Checkpoint triggered
→ Opening approval dashboard at http://localhost:3001/approvals

Review diagnostic data and make decision in browser...
```

#### Smart Default Behavior

```python
def hitl_checkpoint(action, diagnostic_data, risk_level):
    if risk_level == "low" and diagnostic_data.get("status") == "success":
        # Auto-approve (no human needed)
        return {"status": "auto_approved", "rationale": "Low risk, success"}

    elif running_in_terminal() and diagnostic_data_is_minimal():
        # CLI conversation (fast, for developers)
        return cli_triage_conversation(action, diagnostic_data)

    else:
        # Web UI (rich diagnostics, for complex approvals)
        queue_approval(action, diagnostic_data)
        open_browser("http://localhost:3001/approvals")
        return wait_for_approval()
```

### Domain-Agnostic Examples

**Same HITL Infrastructure, Different Domains:**

#### Example 1: QA Testing Domain
```python
hitl_checkpoint(
    step="execute_test",
    risk_level="high",
    diagnostic_data={
        "test_output": "FAILED: assert login_page.is_logged_in()",
        "page_state": {"url": "https://app.com/login", "title": "Login"},
        "expected": "User logged in",
        "actual": "Login failed"
    }
)
```

#### Example 2: DevOps Deployment Domain
```python
hitl_checkpoint(
    step="deploy_production",
    risk_level="critical",
    diagnostic_data={
        "deployment_config": {"env": "prod", "version": "v2.1.0"},
        "environment_vars": {"DATABASE_URL": None},  # Missing!
        "service_health": {"database": "unreachable"}
    }
)
```

#### Example 3: Financial Transaction Domain
```python
hitl_checkpoint(
    step="process_payment",
    risk_level="high",
    diagnostic_data={
        "transaction": {"amount": 50000, "currency": "USD"},
        "risk_score": 85,
        "fraud_signals": ["unusual_amount", "new_merchant"],
        "customer_history": {"avg_transaction": 500, "account_age_days": 7}
    }
)
```

#### Example 4: Healthcare Patient Data Domain
```python
hitl_checkpoint(
    step="update_patient_record",
    risk_level="critical",
    diagnostic_data={
        "patient_id": "P12345",
        "data_changes": {"medication": "old_drug → new_drug"},
        "interaction_warnings": ["potential_allergy_conflict"],
        "prescribing_physician": "Dr. Smith"
    }
)
```

**Key Point:** Same MCP tool, same triage workflow, different diagnostic data. Protocol guides what to include per domain. AI adapts to whatever is provided.

#### AI Can Ask Domain-Specific Clarifying Questions

**Example: Financial Transaction Triage**
```
User selects: 3. Investigate Further

AI: I see a high-risk transaction ($50,000) with fraud signals. Let me ask some
    clarifying questions to understand the context better:

    1. Is this customer a known high-value client?
    2. Has this merchant been verified in your system?
    3. What is the typical transaction limit for this customer tier?
    4. Are there any pending verification steps?

User: Yes, they're a known client. The merchant is new but verified.
      Limit is $100k. No pending verification.

AI: Based on your answers:
    - Customer is trusted (within limits)
    - Merchant is verified
    - Transaction under limit

    Recommendation: Approve with monitoring flag
    Updated Confidence: 75% → 90% (safe to proceed)

    Would you like to:
    1. Approve with monitoring
    2. Request additional verification
    3. Escalate to fraud team
```

**This conversational capability makes HITL domain-agnostic:**
- AI doesn't need to know all domains upfront
- Can adapt to any workflow
- Learns context through conversation
- Human provides domain expertise on-demand

### MVP Scope (4-Week Build)

**In Scope for MVP:**
- **HITL Protocol** (Markdown skill defining oversight rules)
  - Domain-specific guidance (what diagnostic data to include)
  - Risk level definitions per domain
  - Human-readable (auditors can read)
  - Machine-parseable (YAML frontmatter)
- **Smart Gate MCP Tool** (`hitl_checkpoint` - enforces protocol)
  - Accepts arbitrary diagnostic JSON (domain-agnostic)
  - Protocol-driven risk evaluation
  - Auto-approve OR queue for human
- **MCP Server only** (Claude Code, Cline, MCP ecosystem)
  - REST API and SDK deferred to Phase 2 (Stripe playbook)
- **Dual Approval Mechanism:**
  - CLI Conversation (terminal-native with AI triage)
  - Local Web UI (rich diagnostic viewer)
  - Smart default behavior (auto-selects based on context)
- **Domain-Agnostic Diagnostic System:**
  - Caller provides ANY JSON (no prescribed structure)
  - Protocol guides what to include (per domain)
  - AI analyzes whatever is provided
  - No hardcoded field assumptions
- **Adaptive AI Analysis Engine:**
  - Hypothesis generation (pattern matching on provided data)
  - Confidence scoring (0-100%)
  - Evidence extraction (from provided context)
  - Fix suggestions (domain-aware)
  - Can ask clarifying questions (conversational)
- **Progressive audit trail** (local JSON files)
  - All checkpoints logged
  - Triage decisions recorded
  - Diagnostic data captured (whatever was provided)
- **Local SQLite queue** (for web UI approvals)
- **Compliance deliverables** (control catalog, compliance matrix, risk register)

**Technology Stack:**
- MCP Server (Python, using existing MCP SDK patterns from QA Engine)
- CLI Interface (Rich library for formatted terminal output)
- Local Web UI (Next.js dev server on localhost:3001)
- SQLite (local queue for pending approvals)
- JSON files (audit trail storage, like QA Engine)

**Out of Scope for MVP (Phase 2):**
- REST API (add after MVP validation)
- SDK Decorators (add after REST API)
- Hosted infrastructure (MVP is local-only)
- PostgreSQL/S3 (use local JSON + SQLite for MVP)
- Screenshots in dashboard
- Historical pattern analysis
- Multi-region support
- "Bring your own infrastructure" adapters
- White-label customization
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

### System Architecture (MVP)

```
┌─────────────────────────────────────────────────────────────┐
│                  HOST SYSTEM (Your Product)                 │
│  - QA Engine, or any AI agent workflow                     │
└─────────────────────────────────────────────────────────────┘
                          ↓ (calls via)
┌─────────────────────────────────────────────────────────────┐
│             HITL Integration Layer (Choose One)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  MCP Server  │  │  REST API    │  │  SDK Library │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│            HITL Infrastructure (Hosted Service)             │
│  ┌──────────────────────────────────────────────────┐      │
│  │ Protocol Parser → Risk Evaluator → Checkpoint    │      │
│  └──────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │ PostgreSQL (audit logs) + S3 (backups)           │      │
│  └──────────────────────────────────────────────────┘      │
│  ┌──────────────────────────────────────────────────┐      │
│  │ Dashboard (Next.js - approval queue)             │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
AI Agent Workflow
    ↓
HITL Checkpoint (event triggered via MCP/REST/SDK)
    ↓
Protocol Evaluation (requires approval?)
    ↓
YES → Queue for Human Review → Dashboard
          ↓
      Human Decision (approve/reject)
          ↓
      Audit Trail (PostgreSQL + S3 backup)
          ↓
      Return to Agent Workflow
    ↓
NO → Auto-approve (low risk) → Audit Trail → Continue
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

**MCP Server:**
- MCP SDK (already using in QA Engine)
- Python 3.11+

**REST API:**
- FastAPI (lightweight wrapper over MCP tool)
- Uvicorn (ASGI server)

**SDK (Python/JS):**
- Thin client over REST API or MCP

**Dashboard:**
- Next.js
- NextAuth.js (authentication)
- PostgreSQL client

**Audit Storage:**
- PostgreSQL (primary storage)
- AWS S3 SDK (immutable backups)

**Auth:**
- JWT tokens
- API keys

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

**What This Means:**
- **Protocols (Markdown Skills)** define oversight rules
- **Smart Gates (MCP Tools)** enforce protocols at runtime
- **Same pattern as QA Engine** (proven with 11-step workflow)
- **Extract Step 11 HITL** and make it domain-agnostic

**Rationale:**
- Human-readable protocols = compliance advantage (EU AI Act requires understanding)
- Proven in QA Engine Step 11 (validates the pattern works)
- MCP-native = distribution built-in (97M+ monthly SDK downloads)
- Novel differentiation vs OPA/Temporal (not just code-based rules)

### 2. Integration Method (MVP Scope)

**Decision:** MCP Server only for MVP

**What:**
- MCP Server (drop-in for Claude Code, Cline, MCP ecosystem)
- Local execution (no hosted infrastructure)

**Deferred to Phase 2:**
- REST API (any platform)
- SDK Decorators (Python/JS)
- Hosted infrastructure

**Rationale:**
- Stripe launched with ONE integration method (REST API only)
- Prove product-market fit first, add distribution later
- MCP Server = 2-3 days dev time
- All three = 1 week (premature for MVP)
- Focus on proving diagnostic triage pattern works

### 3. Approval Mechanism (MVP Scope)

**Decision:** Dual mechanism - CLI Conversation + Local Web UI with smart defaults

**MVP Features:**
- **CLI Conversation** (Step 11 pattern):
  - Full conversational triage workflow
  - AI analysis with confidence scoring (0-100%)
  - 7 diagnostic data types captured
  - Structured options + custom guidance
  - Terminal-native (Rich library for formatting)
- **Local Web UI** (localhost:3001):
  - Rich diagnostic viewer (formatted data, syntax highlighting)
  - Same triage workflow as CLI
  - Approval queue for async review
  - Auto-opens browser on checkpoint
- **Smart Default Behavior**:
  - Low risk + success = auto-approve
  - Terminal + minimal data = CLI conversation
  - Complex data = web UI

**Phase 2 Features:**
- Screenshots in diagnostic viewer
- Historical pattern analysis
- Hosted dashboard option
- Embeddable components (for host system UIs)

**Rationale:**
- Step 11 proves full triage conversation works (not just y/n approval)
- Diagnostic transparency is core differentiation (our moat vs 7+ competitors)
- CLI gives immediate feedback for developers
- Web UI handles complex diagnostics and async approvals
- Smart defaults optimize for best UX per context
- Local-only simplifies MVP (no hosted infrastructure needed)

### 4. Infrastructure

**Decision:** Local-only for MVP (no hosted infrastructure)

**What:**
- MCP Server runs locally (like QA Engine)
- Audit logs write to local JSON files
- SQLite for approval queue
- Local Web UI (Next.js dev server on localhost:3001)

**Deferred to Phase 2:**
- Hosted infrastructure (PostgreSQL, S3)
- Hosted dashboard
- Multi-region support
- Freemium + paid pricing (requires hosted infrastructure)

**Rationale:**
- Stripe started local-first (developers integrated API locally), added hosted services later
- Prove HITL triage pattern works before building infrastructure
- Local-only = zero infrastructure cost for MVP
- Faster to ship (no cloud setup, auth, billing)
- QA Engine proves local MCP pattern works

### 5. Pricing Strategy

**Decision:** Phase 2 (deferred until hosted infrastructure)

**MVP:** Free, open-source MCP server (local-only)

**Phase 2 Pricing (when hosted infrastructure launches):**
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

Enterprise Tier: Custom pricing
- Unlimited checkpoints
- 7-year audit retention
- White-label
- Multi-region support
```

**Rationale:**
- Can't monetize until hosted infrastructure exists
- MVP validates triage pattern + diagnostic transparency
- Freemium model requires hosted service (billing, auth, multi-tenancy)
- Launch free MCP server → validate → add hosted option → monetize

### 6. Launch Sequence

**Decision:** Build standalone HITL → Validate pattern → Look at QA Engine integration later

**Timeline:**
```
Week 1: HITL Core
  - MCP Server (Python)
  - hitl_checkpoint tool (protocol enforcement)
  - Diagnostic capture system (7 data types)
  - AI analysis engine (hypothesis, confidence, evidence)

Week 2: Approval Mechanisms
  - CLI conversation (Rich library, Step 11 pattern)
  - Local Web UI (Next.js, diagnostic viewer)
  - Smart default behavior
  - SQLite approval queue

Week 3: Polish & Testing
  - Audit trail (local JSON files)
  - Compliance deliverables (control catalog, matrix, register)
  - End-to-end testing
  - Documentation

Week 4: Launch & Validate
  - Public release (free, open-source MCP server)
  - Gather feedback from MCP community
  - Validate: Does triage pattern + diagnostic transparency work?
```

**Deferred to Phase 2:**
- QA Engine integration (may not be needed if HITL works standalone)
- Hosted infrastructure
- REST API / SDK
- Monetization

**Rationale:**
- Build standalone, prove the pattern works
- Don't tie to QA Engine (may not need it if HITL succeeds independently)
- Free/open-source MVP removes revenue pressure
- Validate diagnostic triage UX before building infrastructure
- QA Engine can integrate later IF there's demand

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

## Additional Design Decisions (Session 2026-01-15)

### 11. Checkpoint Workflow Pattern

**Decision:** Synchronous Return + AI Orchestration (follow QA Engine Step 11 exactly)

**Flow:**
```
AI calls hitl_checkpoint(workflow_id, step, data, risk_level)
  ↓
Gate evaluates:
  1. Load protocol
  2. Check risk level
  3. If low-risk + auto-approve rule → return approved immediately
  4. If high-risk → capture diagnostic context, generate AI analysis
  ↓
Gate returns IMMEDIATELY with:
  {
    "approved": false,  // or true if auto-approved
    "requires_human": true,
    "diagnostic_data": {...},
    "ai_analysis": {
      "confidence": 75,
      "recommendation": "approve",
      "concerns": ["data looks unusual", "high transaction amount"]
    },
    "options": ["approve", "reject", "investigate", "modify"]
  }
  ↓
AI orchestrates approval conversation:
  - Presents checkpoint context to user
  - Shows AI analysis + recommendation
  - Asks user to approve/reject/investigate
  - User responds
  - AI logs decision to audit trail
  - AI proceeds based on decision
```

**Rationale:**
- ✅ Fits existing smart gate pattern (evaluate + return, don't orchestrate)
- ✅ Domain-agnostic (works for any approval timeline: seconds to days)
- ✅ Minimal component changes (reuse existing StateManager, AuditLogger)
- ✅ AI orchestrates approval conversation (consistent with our architecture)
- ✅ Protocol-based automation (low-risk auto-approved)
- ✅ Proven pattern (QA Engine Step 11 already works this way)

**Alternatives Rejected:**
1. **MCP Async Tasks** - Complex state management, task queue overhead, less natural UX
2. **GitHub Actions Blocking** - Breaks for multi-day approvals, not domain-agnostic
3. **Terraform Pattern** - Infrastructure-specific, user must be available immediately

**Key Trade-offs:**
- ✅ Simple implementation, high component reuse
- ⚠️ Requires active conversation (can pause/resume via StateManager)
- ⚠️ No dedicated approval queue UI in MVP (can add in Phase 2)

### 12. Approval Mode Strategy (Protocol-Driven)

**Decision:** Protocol-driven approval mode selection with conversational mode for MVP

**Protocol Specification:**
```yaml
# .claude/skills/hitl-protocols/qa_testing.md
---
domain: qa_testing
approval_mode: conversational  # or "cli" or "web_ui"
auto_approve:
  - when: risk_level == "low"
---
```

**MVP Scope (March 2026):**
- ✅ **Conversational mode** (fully implemented) - AI orchestrates approval in conversation
- 📋 **CLI mode** (stubbed - fallback to conversational) - Terminal-based blocking approval
- 📋 **Web UI mode** (stubbed - fallback to conversational) - Browser-based async approval

**Post-MVP Rollout:**
- **Phase 2:** Add CLI mode (terminal-native users, DevOps workflows)
- **Phase 3:** Add Web UI mode (enterprise, multi-day approvals, compliance queues)

**Rationale:**
- **Target Audience First:** Day 1 customers are Claude Code users (already in conversation)
- **Fastest to Value:** 90% reuse from QA Engine Step 11 (1-2 weeks vs 4-6 weeks)
- **Validates Pattern:** Proves protocol system, smart gates, audit trail work
- **Unlocks Segments:** CLI → terminal-native DevOps, Web UI → enterprise compliance

**Approval Mode Comparison:**

| Mode | Target Audience | Use Case | Timeline | Priority |
|------|----------------|----------|----------|----------|
| **Conversational** | Claude Code users | QA testing, agent dev | Seconds | 🎯 **MVP** |
| **CLI** | Terminal-first DevOps | Terraform plan, deployments | Minutes | **Phase 2** |
| **Web UI** | Enterprise compliance | Financial approvals, healthcare | Hours to days | **Phase 3** |

### 13. Target Audience Analysis

**Day 1 Customer:** Developers using Claude Code for AI-assisted workflows

**User Story:**
```
Developer: "Generate tests for login page"
  ↓
Claude calls hitl_checkpoint (high-risk: generates code)
  ↓
Claude: "I need approval to generate tests. Here's what I'll create:
         - LoginPage POM with 8 elements
         - LoginTasks with 2 methods
         - 3 test scenarios

         AI Analysis (confidence 90%):
         ✓ Element selectors look stable
         ✓ Test coverage looks good

         Approve? [yes/no]"
  ↓
Developer: "yes"
  ↓
Claude: "Approved. Generating tests..." [proceeds]
```

**Why Conversational Mode First:**
- Natural conversation flow (no context switch)
- Fast approvals (developer is right there)
- Educational (AI explains what it's doing)
- Fastest to ship (90% reuse from QA Engine Step 11)

**Customer Segmentation:**

| Segment | Approval Mode | When to Add | Revenue Potential |
|---------|---------------|-------------|-------------------|
| **Claude Code users** | Conversational | ✅ MVP | Low (free tier) |
| **Terminal-first DevOps** | CLI | Phase 2 (Week 4-5) | Medium (Pro tier) |
| **Enterprise compliance** | Web UI | Phase 3 (Week 6-8) | High (Enterprise tier) |
| **Multi-user teams** | Web UI + Routing | Phase 4 (3+ months) | High (Enterprise tier) |

### 14. Component Adaptation Strategy

**Decision:** Minimal adaptation - 90%+ reuse from QA Engine

**StateManager Changes:**
- ✅ Keep: per-run isolation (run_id), atomic writes, session continuation
- ✅ Keep: `save()`, `load()`, `get_step()`, `is_step_complete()` methods
- ➕ Add: `save_checkpoint_decision(checkpoint_id, decision, rationale)` method
- ➖ Remove: QA-specific constants (`VALID_STEPS = range(1, 12)`, `VALID_EXECUTION_MODES`)
- **Adaptation:** Make step validation configurable instead of hardcoded

**AuditLogger Changes:**
- ✅ Keep: incremental persist, session continuation, atomic writes
- ✅ Keep: `log_gate()`, `log_self_heal()`, `log_file_generated()` methods
- ➕ Add: `log_checkpoint(checkpoint_id, step, data, risk_level, ai_analysis, decision)` method
- ➖ Remove: QA-specific field assumptions in `get_summary()`
- **Adaptation:** Make summary statistics domain-agnostic

**BaseGate → BaseCheckpoint Changes:**
- ✅ Keep: `pass_response()`, `fail_response()`, audit integration
- ➕ Add: `checkpoint_response(approved, requires_human, ai_analysis, options)` method
- ✅ Keep: Skeleton code detection patterns, validation utilities
- ➖ Remove: QA-specific response formats
- **Adaptation:** Rename class, add checkpoint-specific response helpers

**Estimated Adaptation Effort:**
- StateManager: 4-6 hours (add checkpoint methods, remove QA constants)
- AuditLogger: 4-6 hours (add log_checkpoint, make summary generic)
- BaseGate → BaseCheckpoint: 6-8 hours (rename, add checkpoint responses)
- **Total:** 14-20 hours (~2-3 days) vs 4-6 weeks from scratch

### 15. Protocol System Design (Detailed)

**Decision:** YAML frontmatter + Markdown body (human-readable + machine-parseable)

**Protocol File Structure:**
```yaml
# .claude/skills/hitl-protocols/qa_testing.md
---
# YAML Frontmatter (machine-parseable)
domain: qa_testing
approval_mode: conversational
risk_levels:
  low: [generate_page_object, discover_elements]
  medium: [generate_task, generate_role]
  high: [generate_test, execute_test]
  critical: [modify_framework, delete_files]

auto_approve:
  - when: risk_level == "low" AND status == "success"
  - when: step_name == "generate_page_object" AND element_count < 20

require_approval:
  - when: risk_level == "high"
  - when: status == "failed"
  - when: confidence_score < 70

approval_prompt: |
  Review the QA test generation carefully:
  - Check element selectors are stable
  - Verify test scenarios match requirements
  - Confirm no hardcoded test data
---

# Markdown Body (human-readable guidance)

## QA Testing Oversight Protocol

**Purpose:** Ensure AI-generated tests are high-quality, maintainable, and match requirements.

**When Approval Required:**
- High-risk test generation (integration tests, E2E tests)
- Test execution failures (need human triage)
- Low confidence in generated code (< 70%)

**Diagnostic Data to Include:**
- `test_scenarios`: List of scenarios being generated
- `page_elements`: Elements discovered on page
- `confidence_score`: AI's confidence in generation (0-100)
- `code_preview`: First 10 lines of generated code

**Approval Criteria:**
- Element selectors are CSS/XPath (not text-based)
- Test follows AAA pattern (Arrange, Act, Assert)
- No hardcoded credentials or test data
- Assertions use POM state-check methods
```

**Protocol Parser Implementation:**
```python
import yaml
import frontmatter

class ProtocolParser:
    def __init__(self, protocol_path: str):
        with open(protocol_path) as f:
            post = frontmatter.load(f)
            self.metadata = post.metadata  # YAML frontmatter (dict)
            self.guidance = post.content   # Markdown body (string)

    def requires_approval(self, step_name: str, risk_level: str,
                         diagnostic_data: dict) -> bool:
        """Evaluate if checkpoint requires approval."""

        # Check auto-approve rules first
        for rule in self.metadata.get("auto_approve", []):
            if self._eval_rule(rule, step_name, risk_level, diagnostic_data):
                return False  # Auto-approved

        # Check require-approval rules
        for rule in self.metadata.get("require_approval", []):
            if self._eval_rule(rule, step_name, risk_level, diagnostic_data):
                return True  # Requires approval

        # Default: require approval for high/critical risk
        return risk_level in ["high", "critical"]

    def _eval_rule(self, rule: dict, step_name: str, risk_level: str,
                   diagnostic_data: dict) -> bool:
        """Simple rule evaluation (can use Python's eval or safer parser)."""
        when_clause = rule["when"]
        # Parse "risk_level == 'low' AND status == 'success'"
        # Evaluate against current context
        # Return True/False
        pass
```

**Protocol Examples (3 Domains):**
1. **QA Testing** (qa_testing.md) - Test generation approval
2. **DevOps Deployment** (devops_deployment.md) - Production deployment approval
3. **Financial Transaction** (finance_transaction.md) - Payment approval

**Deferred to Implementation:**
- Rule evaluation engine (simple eval vs safe parser)
- Protocol versioning strategy
- Protocol validation schema
- Protocol migration tools

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

## Phase 2 Design Considerations

**Note:** The following design options were discussed but deferred to Phase 2. This section preserves valuable architectural thinking for post-MVP evolution.

### Modular Architecture Pattern

**When to Implement:** After MVP validation, if customers request self-hosting or "bring your own infrastructure" options.

**Architecture:**

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

**"Bring Your Own Infrastructure" Options:**

| Component | Host System Option | Isagawa Hosted Option |
|-----------|-------------------|---------------------|
| **Database** | Use your PostgreSQL/MySQL/MongoDB | Use Isagawa's managed database |
| **Auth** | Use your SSO/OAuth/API keys | Use Isagawa's auth system |
| **Dashboard** | Embed in your UI via iframe/component | Use Isagawa's hosted dashboard |
| **Audit Storage** | Write to your S3/GCS/Azure Blob | Use Isagawa's immutable audit storage |
| **Notifications** | Webhooks to your system | Isagawa's Slack/Email/Discord |

**Implementation Approach:**

```python
# Phase 2: Framework-agnostic core with adapters

# Option 1: Use your infrastructure
checkpoint = HITLCheckpoint(
    storage=StorageAdapter(your_db),
    auth=AuthAdapter(your_auth),
    dashboard_url=your_dashboard
)

# Option 2: Use Isagawa's hosted infrastructure
checkpoint = HITLCheckpoint(
    api_key="prod_xxx",
    workspace_id="acme-corp"
)
```

**Why Defer to Phase 2:**
- MVP needs to prove product-market fit first
- Modular architecture adds 2-3 weeks dev time
- Increases testing surface (test all adapter combinations)
- Stripe launched with opinionated stack, added flexibility later
- Implement AFTER customers request self-hosting/custom infrastructure

### Self-Hosting Option

**When to Implement:** After enterprise customers request on-premise deployment for security/compliance.

**Components:**
- Docker images for all services (MCP server, REST API, Dashboard)
- Kubernetes deployment manifests
- Database migration scripts
- Infrastructure-as-code (Terraform/CloudFormation)
- Self-hosting documentation

**Pricing Impact:**
- Enterprise tier feature (custom pricing)
- Includes white-label customization
- Annual contracts (not monthly)

### Embeddable Dashboard Components

**When to Implement:** After customers request dashboard integration into their existing UIs.

**Approach:**
- React components library
- Web components (framework-agnostic)
- iframe embedding with postMessage API
- Webhook integrations for custom dashboards

**Use Cases:**
- QA Engine embeds approval queue in its UI
- External products show HITL status inline
- Custom dashboards for specific workflows

### Advanced Features (Post-MVP)

**Screenshots in Dashboard:**
- Capture page screenshots at checkpoint
- Store in S3
- Display in diagnostic viewer
- Increases storage costs

**Historical Pattern Analysis:**
- ML-based pattern recognition
- "Similar action failed 3x this week"
- Risk scoring based on history
- Requires data science infrastructure

**Multi-Region Support:**
- EU region for GDPR compliance
- Multi-region replication
- Read/write split (eventual consistency)
- Adds $2K-4K/mo infrastructure cost

**White-Label Customization:**
- Custom branding (logo, colors, domain)
- Custom protocol templates
- Custom compliance frameworks
- Enterprise tier only

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
1. ✅ Architecture: Protocols + Smart Gates (proven QA Engine Step 11 pattern)
2. ✅ Integration: MCP Server only for MVP (Stripe playbook: one method first)
3. ✅ Approval Mechanism: Dual (CLI conversation + Local Web UI with smart defaults)
4. ✅ Infrastructure: Local-only (no hosted services for MVP)
5. ✅ Pricing: Phase 2 (free/open-source MCP server for MVP)
6. ✅ Launch Sequence: Build standalone → Validate pattern → QA integration if needed

**Key Principle:** Use Step 11 HITL conversational triage pattern (AI analysis + evidence + structured options), make it domain-agnostic (caller provides ANY JSON), ship as free/open-source local MCP server

**MVP Scope:**
- MCP Server (local, Python)
- CLI conversation (Step 11 pattern: AI analysis, structured options, custom guidance)
- Local Web UI (rich diagnostic viewer on localhost:3001)
- Smart defaults (auto-approve low risk, CLI for simple, Web UI for complex)
- **Domain-agnostic:** Caller provides arbitrary diagnostic JSON (no prescribed fields)
- **Adaptive AI:** Analyzes whatever is provided, can ask clarifying questions
- Local audit trail (JSON files + SQLite queue)
- 4-week timeline

**Deferred to Phase 2:**
- REST API / SDK
- Hosted infrastructure
- Monetization
- QA Engine integration (if needed)

**Ready to proceed with:** Phase 2 (PRD creation)

**Last Updated:** 2026-01-15 (Updated with checkpoint workflow and approval mode decisions)
