# Generalized Quality Gates for Everyday AI Users

**Status:** Idea
**Date:** 2026-01-07
**Category:** New Product Concept (Horizontal)

---

## The Problem

AI users repeat themselves constantly. Even when instructions exist:
- AI reads instructions but doesn't apply them
- AI acknowledges rules then ignores them
- Users must manually remind AI to follow its own instructions
- No enforcement mechanism exists for personal workflows

**This happens everywhere:**
- ChatGPT custom instructions → ignored
- Claude project instructions → partially followed
- Cursor rules → acknowledged but not applied
- System prompts → forgotten mid-conversation

This is a universal pain point affecting every AI user, every AI tool, not just domain specialists.

---

## The Idea

A generalized, self-configuring quality gate that any AI user can use for any workflow.

**Core Concept:**
- User defines their rules (or AI helps extract them)
- Gate enforces those rules during AI execution
- Works with any AI tool (Claude, ChatGPT, Copilot, Cursor, etc.)
- Plug and play - minimal setup, immediate value

---

## Key Innovation

> **Naming Options (decide later):**
> - **Protocol Enforcement** = describes the action (what Smart Gates do)
> - **Smart Gates for Personal Protocols** = describes the product itself

The missing primitive in AI tooling is **Protocol Enforcement** - a mechanism that guarantees AI follows the protocols it was given, regardless of which AI tool is used.

Current state (every AI tool):
```
User provides protocol (instructions, rules, guidelines)
        ↓
AI acknowledges protocol
        ↓
AI partially follows or ignores it
        ↓
User repeats themselves or accepts bad output
```

With Protocol Enforcement:
```
User defines protocol (any format, any AI tool)
        ↓
Pre-Gate: "AI must acknowledge each rule explicitly"
        ↓
AI does work
        ↓
Post-Gate: "Validate output against protocol"
        ↓
Pass or Explicit Fix Required
```

**Agent-Agnostic Design:**

| AI Tool | How Instructions Are Given | How Gate Integrates |
|---------|---------------------------|---------------------|
| ChatGPT | Custom instructions, system prompt | Wrapper / browser extension |
| Claude.ai | Project instructions, system prompt | Wrapper / browser extension |
| Claude Code | Skills, CLAUDE.md | MCP tool |
| Cursor | .cursorrules | Extension / prompt injection |
| Copilot | Instructions file | Extension / prompt injection |
| Any API | System message | Middleware layer |

The gate is the **enforcement layer that sits between user and AI**, regardless of which AI.

---

## Isagawa Architecture: Protocols + Smart Gates

> **The Isagawa Platform is an AI Management Layer built on two primitives: Protocols and Smart Gates.**

This consumer product applies the same architecture used in domain-specific Execution Engines, adapted for personal use.

### How the Primitives Apply

| Primitive | Platform (Enterprise) | Consumer Product |
|-----------|----------------------|------------------|
| **Protocols** | Expert-authored, domain-specific (QA, Healthcare, Legal) | User-defined, personal workflows |
| **Smart Gates** | Enforce domain architecture, validate code patterns | Enforce user's rules, validate AI output |

### Architecture Comparison

**Platform (QA Execution Engine):**
```
Expert Protocol (10-step QA workflow)
        ↓
Smart Gate validates each step
        ↓
AI generates code following protocol
        ↓
Gate enforces: no skeleton code, correct patterns
        ↓
Pass or explicit fix pattern provided
```

**Consumer Product:**
```
User Protocol (personal rules, any workflow)
        ↓
Smart Gate validates AI acknowledged rules
        ↓
AI does work following user's protocol
        ↓
Gate enforces: output matches user's criteria
        ↓
Pass or explicit fix required
```

### Same Primitives, Different Scope

| Aspect | Platform | Consumer |
|--------|----------|----------|
| Protocol Author | Domain experts | User |
| Protocol Complexity | Deep (28 Design Decisions) | Simple (3-5 rules) |
| Gate Sophistication | Pattern matching, code analysis | Checklist, keyword, semantic |
| Enforcement Level | Non-bypassable (mandatory) | Configurable (strict/lenient) |
| Target | Enterprise teams | Individual AI users |

### Why This Matters

1. **Shared Infrastructure** - Same gate engine powers both products
2. **Upgrade Path** - Consumer users who need domain-specific enforcement → Platform
3. **Validated Architecture** - Platform proves the primitives work; Consumer scales them
4. **Consistent Branding** - "Isagawa = Protocols + Smart Gates" across all products

---

## Product Architecture

### Gate Types (Tiered Complexity)

| Tier | Name | What It Does | Target User |
|------|------|--------------|-------------|
| 1 | Checklist Gate | User defines 3-5 must-have criteria, gate validates | Beginners |
| 2 | Pattern Gate | Validates against patterns (format, structure, keywords) | Power users |
| 3 | Semantic Gate | AI-powered validation against natural language rules | Advanced |

### Self-Configuration Wizard

The product walks users through setup:

```
Step 1: "What kind of work are you doing?"
        → Writing, Coding, Research, Analysis, Other

Step 2: "What rules must AI always follow?"
        → User types natural language rules
        → AI extracts enforceable criteria

Step 3: "Any reference documents AI should always apply?"
        → User uploads/links documents
        → Gate tracks reference application

Step 4: "Test your gate"
        → User runs a sample task
        → Gate shows what passed/failed

Step 5: "Save as your personal protocol"
        → Reusable for future sessions
```

### Pattern Library (Pre-built Templates)

| Category | Template | Rules Enforced |
|----------|----------|----------------|
| Writing | Blog Post | Structure, tone, SEO basics, CTA |
| Writing | Email | Professional tone, clear ask, appropriate length |
| Coding | Code Review | No TODOs, error handling, naming conventions |
| Coding | Documentation | All functions documented, examples included |
| Research | Summary | Sources cited, balanced view, key takeaways |
| Analysis | Report | Data-backed claims, visualizations described, recommendations |

Users can start from templates and customize.

---

## Technical Implementation

### Option A: MCP-Based (Claude Code, compatible tools)

```python
# Generalized gate structure
class UserDefinedGate:
    def __init__(self, user_rules: List[str], references: List[str]):
        self.rules = user_rules
        self.references = references

    def pre_validate(self, context: dict) -> dict:
        """Ensure all references are loaded before AI proceeds."""
        missing = self.check_references_loaded(context)
        if missing:
            return {
                "status": "blocked",
                "reason": f"References not loaded: {missing}",
                "action": "Load these references before proceeding"
            }
        return {"status": "pass"}

    def post_validate(self, output: str) -> dict:
        """Validate output against user's rules."""
        violations = []
        for rule in self.rules:
            if not self.check_rule(output, rule):
                violations.append(rule)

        if violations:
            return {
                "status": "fail",
                "violations": violations,
                "fix_hint": self.generate_fix_hint(violations)
            }
        return {"status": "pass"}
```

### Option B: Prompt-Based (Works with any AI)

For non-MCP environments, gate logic can be injected as structured prompts:

```
BEFORE YOU RESPOND:
1. Confirm you have read ALL of the following references: [list]
2. List the key rules from each reference
3. Only then proceed with the task

AFTER YOU COMPLETE THE TASK:
Self-check against these criteria:
[ ] Criteria 1
[ ] Criteria 2
[ ] Criteria 3

If any criteria not met, revise before presenting final output.
```

### Option C: Browser Extension / Wrapper

- Intercepts AI interactions
- Injects gate logic automatically
- Works with ChatGPT, Claude.ai, etc.
- No user action required after setup

---

## Business Model (Revised After Unit Economics Analysis)

| Tier | Target | Features | Price |
|------|--------|----------|-------|
| Free | Trial | 50 calls/mo, 3 rules, basic templates | $0 |
| Starter | Light users | 500 calls/mo, unlimited rules | $29/mo |
| Pro | Regular users | 2,000 calls/mo, pattern library, templates | $49/mo |
| Power | Heavy users | 5,000 calls/mo, priority support | $79/mo |

**Note:** Mass-market $15/mo is not viable due to API costs. See Unit Economics section.

**Funnel Strategy:**
```
Free users (try it)
        ↓
Starter/Pro conversion (paying users)
        ↓
Power users (heavy usage)
        ↓
Enterprise needs domain-specific → Upsell to Vertical Execution Engines
```

---

## CRITICAL: Unit Economics Problem (Browser Extension Model)

### The AI GTM Trap

Reference: [AI GTM Unit Economics - Jeff Ignacio](https://www.linkedin.com/pulse/ai-gtm-unit-economics-jeff-ignacio-mlgzc/)

Traditional SaaS enjoys 80% gross margins. AI-native products operate at 50-65% due to API costs consuming 30-50% of revenue.

### Why Consumer Browser Extension FAILS

```
User on ChatGPT.com (THEIR infrastructure)
        ↓
ChatGPT makes AI call (THEIR cost)
        ↓
We intercept response
        ↓
We validate with AI (OUR cost) ← ADDITIONAL COST
        ↓
User pays $15/mo, we pay $50/mo in API
        ↓
ECONOMICS BROKEN - WE LOSE MONEY
```

| Model | Who Calls AI | Validation Cost | Unit Economics |
|-------|--------------|-----------------|----------------|
| **Browser Extension** | ChatGPT/Claude (them) | We pay EXTRA | ❌ Broken |
| **Own App (Vertical)** | We call AI | Part of existing call | ✅ Works |
| **IDE/MCP** | User's environment | Local logic, $0 | ✅ Works |

### Why This Might Kill the Consumer Product

- $15-20/mo consumer pricing
- API calls for semantic validation = $0.50-2.00 each
- Heavy user (100 validations/mo) = $50-200 in API costs
- **We lose money on every active user**

### The Hard Truth

> **Maybe this is why nobody has built consumer AI management layer - the economics don't work at consumer price points.**

### What Dies vs. What Lives

| Product | Status | Why |
|---------|--------|-----|
| Consumer Browser Extension | ❌ DEAD | Piggybacking on other AI, extra validation cost |
| QA Engine (IDE/MCP) | ✅ LIVES | Local validation, no extra cost |
| Non-Tech Verticals (Own App) | ✅ LIVES | We own AI call, validation wraps it |

### Potential Paths Forward (If Pursuing Consumer)

| Option | Viability | Problem |
|--------|-----------|---------|
| Local-only validation (regex, checklist) | Maybe | Too limited, no semantic |
| Local LLM in browser | No | Can't run real models |
| Desktop app with local LLM | Maybe | Distribution nightmare |
| High price point ($50+/mo) | Maybe | Not "mass market" anymore |
| Prompt injection only (no post-validation) | Maybe | Same problem as custom instructions |

### Conclusion (Revised)

The **browser extension** model is dead. But "own the app" works at any scale:

| Model | Price | Viable? |
|-------|-------|---------|
| Browser extension | $15/mo | ❌ Dead |
| Own app (consumer/prosumer) | $30-50/mo | ✅ Alive |
| Own app (enterprise) | $500-2,500/mo | ✅ Alive |

**The pivot:** Don't piggyback on ChatGPT. Build our own consumer app.

---

## Consumer "Own App" Model (Revised Strategy)

### The Viable Consumer Path

Instead of browser extension, build **Isagawa for Everyone** as a standalone app:

```
┌─────────────────────────────────────────────────────────────────┐
│              ISAGAWA CONSUMER APP (Web/Mobile)                  │
│                                                                  │
│  User: "Write a blog post about productivity"                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  User's Protocol (configured in app)                       │ │
│  │  ├── Rule 1: Include CTA                                   │ │
│  │  ├── Rule 2: Under 800 words                               │ │
│  │  └── Rule 3: Professional tone                             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  PRE-GATE: Inject rules into prompt (local, $0)            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  AI CALL: We call OpenAI/Anthropic (our cost, in pricing)  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  POST-GATE: Validate against rules (local, $0)             │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  User sees: Response + Protocol Check (✅ Passed / ❌ Failed)   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Proof This Model Works

| Product | Price | Model | They Do |
|---------|-------|-------|---------|
| Jasper | $49/mo | Own app | AI writing with brand voice |
| Copy.ai | $49/mo | Own app | AI writing with templates |
| Writesonic | $19-49/mo | Own app | AI writing with tools |

They're not browser extensions. They own the AI call. **We can do the same with Protocol Enforcement as the differentiator.**

### Consumer App Pricing

| Tier | Price | Calls/mo | Target |
|------|-------|----------|--------|
| **Free** | $0 | 50 | Try it out |
| **Starter** | $19/mo | 500 | Light users |
| **Pro** | $39/mo | 2,000 | Regular users |
| **Power** | $79/mo | 5,000 | Heavy users |

### Unit Economics (Own App)

```
Pro Tier Example:
├── Revenue: $39/mo
├── API cost (2K calls @ $0.03): $60/mo ← PROBLEM
└── Still negative at low price

Power Tier Example:
├── Revenue: $79/mo
├── API cost (5K calls @ $0.03): $150/mo ← STILL PROBLEM
└── Heavy users still unprofitable
```

### The Real Math Problem

Even with own app, consumer pricing ($19-79/mo) struggles if users are heavy:

| Calls/mo | API Cost | Break-even Price |
|----------|----------|------------------|
| 500 | $15 | $25/mo |
| 1,000 | $30 | $50/mo |
| 2,000 | $60 | $100/mo |
| 5,000 | $150 | $250/mo |

**Insight:** Consumer own-app works only if:
1. Usage is light (< 500 calls/mo)
2. OR price is higher ($50+/mo, becoming "prosumer")
3. OR we get significant API volume discounts

### Revised Product Tiers

| Segment | Price | Target | Viable? |
|---------|-------|--------|---------|
| Consumer (light) | $29/mo | Casual users, <500 calls | ✅ Maybe |
| Prosumer | $49-79/mo | Writers, creators | ✅ Yes |
| SMB | $149-299/mo | Small teams | ✅ Yes |
| Enterprise | $500-2,500/mo | Clinics, firms | ✅ Yes |

**The mass-market $15/mo dream is dead. Prosumer at $49+/mo is viable.**

---

## Platform Architecture: Reusable Thin UI Layer

### The Insight

The "own app" thin UI layer designed for consumer is **reusable across all non-tech verticals**. This isn't just a consumer product - it's platform infrastructure.

### Shared UI Shell

```
┌─────────────────────────────────────────────────────────────────┐
│                    ISAGAWA THIN UI LAYER                        │
│                    (Shared Platform Component)                   │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  User Input Area                                           │ │
│  │  (same across all verticals)                               │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  PRE-GATE: Inject domain protocol (local, $0)              │ │
│  │  └── Consumer: Personal rules                              │ │
│  │  └── Healthcare: Clinical protocols                        │ │
│  │  └── Legal: Contract review rules                          │ │
│  │  └── Finance: Compliance requirements                      │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  AI CALL: Single integration (OpenAI/Anthropic)            │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  POST-GATE: Domain-specific validation (local, $0)         │ │
│  └────────────────────────────────────────────────────────────┘ │
│                              ↓                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Output + Protocol Check Display                           │ │
│  │  (same pattern, domain-specific labeling)                  │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### What Changes Per Vertical

| Component | Shared | Per-Vertical |
|-----------|--------|--------------|
| UI shell | ✅ Same | Branding/skin only |
| Input area | ✅ Same | Domain hints |
| AI integration | ✅ Same | - |
| Pre-gate engine | ✅ Same | Protocol content |
| Post-gate engine | ✅ Same | Validation rules |
| Output display | ✅ Same | Domain labels |

### What This Means

1. **Build Once, Deploy Many**
   - Thin UI is ~80% shared code
   - Each vertical = new protocol pack + skin
   - Dramatically reduces per-vertical development cost

2. **Consistent User Experience**
   - Same interaction pattern across all products
   - Users learn once, apply everywhere
   - "It's Isagawa" becomes recognizable

3. **Faster Vertical Launch**
   ```
   Traditional: Build Healthcare app from scratch (6 months)
   With Shared UI: Configure Healthcare protocol pack (6 weeks)
   ```

4. **Single Codebase Benefits**
   - One team maintains UI
   - Bug fixes apply everywhere
   - Performance improvements shared

### Vertical Configuration Model

```
isagawa-platform/
├── ui-shell/                    ← SHARED (build once)
│   ├── input-component/
│   ├── output-component/
│   ├── gate-display/
│   └── core-layout/
│
├── verticals/
│   ├── consumer/                ← CONFIGURATION
│   │   ├── protocols/           ← Personal rules
│   │   ├── templates/           ← Writing, Research, etc.
│   │   └── branding/            ← "Isagawa Personal"
│   │
│   ├── healthcare/              ← CONFIGURATION
│   │   ├── protocols/           ← Clinical, HIPAA
│   │   ├── templates/           ← Patient notes, referrals
│   │   └── branding/            ← "Isagawa Health"
│   │
│   └── legal/                   ← CONFIGURATION
│       ├── protocols/           ← Contract review, due diligence
│       ├── templates/           ← NDA review, clause analysis
│       └── branding/            ← "Isagawa Legal"
│
└── shared/
    ├── gate-engine/             ← SHARED
    ├── ai-integration/          ← SHARED
    └── audit-trail/             ← SHARED
```

### Strategic Implication

> **Consumer product isn't just a product. It's building platform infrastructure that accelerates ALL future verticals.**

By building Consumer first:
- We build the shared thin UI layer
- We prove the gate engine at scale
- We establish the UX pattern
- Healthcare/Legal/Finance become **configuration projects**, not **development projects**

This changes the economics of vertical expansion dramatically.

---

## MVP Architecture: Stripped Down

### Two Delivery Domains

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ISAGAWA PLATFORM                                     │
│                                                                              │
│  ┌─────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │      TECH DOMAIN (IDE)          │  │    NON-TECH DOMAIN (Web App)    │  │
│  │                                 │  │                                 │  │
│  │  Protocol = Skills/.cursorrules │  │  Protocol = User-configured     │  │
│  │  (native to AI tool)            │  │  rules (we define in our app)   │  │
│  │                                 │  │                                 │  │
│  │  Verticals:                     │  │  Verticals:                     │  │
│  │  ├── QA Automation              │  │  ├── Healthcare                 │  │
│  │  ├── DevOps                     │  │  ├── Legal                      │  │
│  │  └── Code Review                │  │  ├── Finance                    │  │
│  │                                 │  │  └── Consumer (Personal)        │  │
│  │                                 │  │                                 │  │
│  │  Gate = MCP tool (local, $0)    │  │  Gate = Server function ($0)    │  │
│  └─────────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                              │
│                    ┌─────────────────────────────────┐                      │
│                    │      SHARED: Smart Gate Logic   │                      │
│                    │      (~50 lines of code)        │                      │
│                    └─────────────────────────────────┘                      │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Protocol Definition by Domain

| Domain | What "Protocol" Means | Who Defines It |
|--------|----------------------|----------------|
| **Tech (IDE)** | Skills, .cursorrules, CLAUDE.md | Native to AI tool |
| **Non-Tech (Web App)** | User's rules configured in our app | User + our templates |

**Key insight:** In IDE, we don't build Protocol - we build the Gate that enforces existing protocols. In our own app, we define both.

### The Isagawa Principle (from execution_patterns.md)

> **Infrastructure that teaches AI how to succeed.**

Gates don't just block. They **provide the fix**.

```
WRONG:
  Gate: "You're missing X. Go figure it out." ❌

RIGHT:
  Gate: "You're missing X. Here it is. Retry." ✅
```

### MVP Visual: The Self-Healing Loop

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER'S REQUEST                                     │
│                                                                              │
│   "Write a blog post about productivity"                                    │
│   + Protocol: ["Include CTA", "Under 500 words", "Professional tone"]       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            PRE-GATE                                          │
│                                                                              │
│   ✓ Input valid?                                                            │
│   ✓ Protocol rules exist?                                                   │
│                                                                              │
│   OUTPUT: Augmented prompt with rules injected                              │
│   "RULES YOU MUST FOLLOW:                                                   │
│    - Include CTA                                                            │
│    - Under 500 words                                                        │
│    - Professional tone                                                      │
│                                                                              │
│    TASK: Write a blog post about productivity"                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            AI CALL                                           │
│                                                                              │
│   OpenAI/Anthropic processes augmented prompt                               │
│   Returns: AI-generated blog post                                           │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           POST-GATE                                          │
│                                                                              │
│   Check each rule against output:                                           │
│   ✓ "Include CTA" → Found "Sign up today" → PASS                           │
│   ✗ "Under 500 words" → 650 words → FAIL                                   │
│   ✓ "Professional tone" → Formal language → PASS                           │
│                                                                              │
│   VIOLATION DETECTED!                                                        │
│                                                                              │
│   Instead of: "Failed. Figure it out." ❌                                   │
│   We provide: "Here's exactly how to fix it." ✅                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                        ┌───────────┴───────────┐
                        │                       │
                   PASS ▼                  FAIL ▼
┌─────────────────────────────┐    ┌─────────────────────────────────────────┐
│                             │    │           SELF-HEALING RETRY             │
│   Return success +          │    │                                         │
│   validated output          │    │   Gate builds retry prompt:             │
│                             │    │   "Your output violated: Under 500      │
│                             │    │    words (currently 650)                │
│                             │    │                                         │
│                             │    │    TO FIX:                              │
│                             │    │    - Revise to address: 'Under 500     │
│                             │    │      words'                             │
│                             │    │                                         │
│                             │    │    REVISE THIS:                         │
│                             │    │    [original output]"                   │
│                             │    │                                         │
│                             │    │   → Back to AI CALL with fix prompt    │
│                             │    │   → Loop up to 3 times                 │
│                             │    │                                         │
└─────────────────────────────┘    └─────────────────────────────────────────┘
```

### MVP Visual: User Experience (Web App)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ISAGAWA                                              [Settings] [Profile]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─── YOUR PROTOCOL ───────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │  Active Rules:                                                           ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │ ✓ Include a call-to-action                               [Remove]  │││
│  │  │ ✓ Keep under 500 words                                   [Remove]  │││
│  │  │ ✓ Use professional tone                                  [Remove]  │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  │  [+ Add Rule]                        [Load Template ▼]                  ││
│  │                                                                          ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─── YOUR TASK ────────────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │  Write a blog post about productivity tips for remote workers            ││
│  │                                                                          ││
│  │                                                            [Execute →]   ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
│  ┌─── OUTPUT ───────────────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │  # 5 Productivity Tips for Remote Workers                                ││
│  │                                                                          ││
│  │  Working from home has become the new normal...                          ││
│  │  [... blog post content ...]                                             ││
│  │  Ready to boost your productivity? Sign up for our newsletter today!     ││
│  │                                                                          ││
│  │  ─────────────────────────────────────────────────────────────────────   ││
│  │                                                                          ││
│  │  PROTOCOL CHECK:                                                         ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │ ✅ Include a call-to-action     → "Sign up for our newsletter"     │││
│  │  │ ✅ Keep under 500 words         → 487 words                        │││
│  │  │ ✅ Use professional tone        → Formal language detected         │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  │                                                                          ││
│  │  [Copy] [Regenerate] [Edit Protocol]                                     ││
│  │                                                                          ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### MVP Visual: Self-Healing in Action (Failure Case)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ISAGAWA                                              [Settings] [Profile]  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─── OUTPUT ───────────────────────────────────────────────────────────────┐│
│  │                                                                          ││
│  │  # 5 Productivity Tips for Remote Workers                                ││
│  │  [... blog post content ...]                                             ││
│  │                                                                          ││
│  │  ─────────────────────────────────────────────────────────────────────   ││
│  │                                                                          ││
│  │  PROTOCOL CHECK:                                                         ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │ ✅ Include a call-to-action     → Found                            │││
│  │  │ ❌ Keep under 500 words         → 650 words (over by 150)          │││
│  │  │ ✅ Use professional tone        → Passed                           │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  │                                                                          ││
│  │  ⚠️  1 VIOLATION - AUTO-RETRYING (Attempt 2 of 3)                       ││
│  │                                                                          ││
│  │  ┌─────────────────────────────────────────────────────────────────────┐││
│  │  │  Fixing: "Keep under 500 words"                                     │││
│  │  │  AI is revising to reduce word count...                             │││
│  │  │  [████████████░░░░░░░░]                                             │││
│  │  └─────────────────────────────────────────────────────────────────────┘││
│  │                                                                          ││
│  └──────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### MVP Visual: Data Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  User    │     │ Pre-Gate │     │    AI    │     │Post-Gate │
└────┬─────┘     └────┬─────┘     └────┬─────┘     └────┬─────┘
     │                │                │                │
     │  task + rules  │                │                │
     │───────────────>│                │                │
     │                │                │                │
     │                │ augmented      │                │
     │                │ prompt         │                │
     │                │───────────────>│                │
     │                │                │                │
     │                │                │  response      │
     │                │                │───────────────>│
     │                │                │                │
     │                │                │                │──┐
     │                │                │                │  │ check
     │                │                │                │  │ rules
     │                │                │                │<─┘
     │                │                │                │
     │                │                │   ┌───────────┐│
     │                │                │   │  PASS?    ││
     │                │                │   └─────┬─────┘│
     │                │                │         │      │
     │                │                │    YES  │  NO  │
     │                │                │    ┌────┴────┐ │
     │                │                │    │         │ │
     │                │                │    ▼         ▼ │
     │                │                │ return    retry│
     │                │                │ output    with │
     │   result       │                │           fix  │
     │<───────────────┼────────────────┼────────────────│
     │                │                │                │
```

### MVP Code: ~60 Lines Total (Self-Healing Gates)

No abstract classes. No factories. No adapters. Just functions that work.

```python
# ============================================================
# smart_gate.py - The only thing we build
# ============================================================

def pre_gate(user_input: str, protocol_rules: list[str]) -> dict:
    """
    Validate input is complete. If not, PROVIDE what's missing.
    """
    issues = []
    fixes = {}

    # Check user input exists
    if not user_input or len(user_input.strip()) < 10:
        issues.append("user_input too short")
        fixes["user_input_hint"] = "Provide a clear task description (10+ chars)"

    # Check protocol has rules
    if not protocol_rules:
        issues.append("no protocol rules defined")
        fixes["default_rules"] = ["Be concise", "Be accurate", "Cite sources"]

    if issues:
        return {
            "status": "NEEDS_RETRY",
            "issues": issues,
            "fixes": fixes,  # <-- HERE'S WHAT YOU NEED
            "message": "Missing required input. Fixes provided. Retry."
        }

    return {
        "status": "PASS",
        "augmented_prompt": _inject_protocol(user_input, protocol_rules)
    }


def post_gate(output: str, protocol_rules: list[str]) -> dict:
    """
    Validate output against protocol. If violations, PROVIDE fix pattern.
    """
    violations = []
    fixes = {}

    for rule in protocol_rules:
        if not _check_rule(output, rule):
            violations.append(rule)
            fixes[rule] = f"Revise to address: '{rule}'"  # <-- HERE'S HOW TO FIX

    if violations:
        return {
            "status": "NEEDS_RETRY",
            "violations": violations,
            "fixes": fixes,
            "retry_prompt": _build_retry_prompt(output, violations, fixes)
        }

    return {"status": "PASS", "output": output}


def _inject_protocol(user_input: str, rules: list[str]) -> str:
    """Inject protocol rules into prompt."""
    rules_text = "\n".join(f"- {r}" for r in rules)
    return f"RULES YOU MUST FOLLOW:\n{rules_text}\n\nTASK: {user_input}"


def _check_rule(output: str, rule: str) -> bool:
    """Check if output satisfies rule. MVP: keyword match."""
    keywords = [w for w in rule.lower().split() if len(w) > 3]
    return any(kw in output.lower() for kw in keywords)


def _build_retry_prompt(output: str, violations: list, fixes: dict) -> str:
    """Build retry prompt with specific fixes."""
    fix_instructions = "\n".join(f"- {fixes[v]}" for v in violations)
    return f"Your output violated: {violations}\n\nTO FIX:\n{fix_instructions}\n\nREVISE THIS:\n{output}"


# ============================================================
# execute.py - Thin orchestration with self-healing
# ============================================================

def execute(user_input: str, protocol_rules: list[str], ai_client, max_retries=3):
    """Execute with self-healing gates."""

    # PRE-GATE
    pre = pre_gate(user_input, protocol_rules)
    if pre["status"] == "NEEDS_RETRY":
        # Apply fixes and continue
        if "default_rules" in pre.get("fixes", {}):
            protocol_rules = pre["fixes"]["default_rules"]
        pre = pre_gate(user_input, protocol_rules)

    # AI CALL
    response = ai_client.complete(pre["augmented_prompt"])

    # POST-GATE (with retries)
    for attempt in range(max_retries):
        post = post_gate(response, protocol_rules)

        if post["status"] == "PASS":
            return {"success": True, "output": post["output"]}

        # Self-healing: use the retry prompt gate provided
        response = ai_client.complete(post["retry_prompt"])

    return {
        "success": False,
        "output": response,
        "message": f"Failed after {max_retries} retries",
        "violations": post["violations"]
    }
```

### Usage

```python
# Define protocol (user's rules)
my_rules = [
    "Include a call-to-action",
    "Keep under 500 words",
    "Professional tone"
]

# Execute with enforcement
result = execute(
    user_input="Write a blog post about productivity",
    protocol_rules=my_rules,
    ai_client=openai_client
)

if result["success"]:
    print(result["output"])
else:
    print(f"Failed: {result['violations']}")
```

### File Structure

```
isagawa/
├── smart_gate.py    # pre_gate, post_gate (~40 lines)
├── execute.py       # execute function (~20 lines)
└── app.py           # FastAPI web app (delivery)
```

### What We Stripped

| Removed | Why Not Needed (Yet) |
|---------|---------------------|
| Abstract base classes | One protocol type for now |
| Validator strategy pattern | One validation method for now |
| Factory pattern | Direct instantiation works |
| Delivery adapters | Build web app directly |
| Value objects | Plain dicts are fine |
| Separate Gate classes | Functions do the job |

### What We Kept

| Kept | Why Essential |
|------|---------------|
| Protocol (rules list) | Core primitive |
| Pre-gate (inject + validate input) | Core primitive |
| Post-gate (validate output + provide fix) | Core primitive |
| Self-healing retry | The Isagawa differentiator |

### When to Add OOP Back

Add abstraction when you feel the pain:
- Multiple protocol types behaving differently → Protocol class
- Multiple validation strategies in use → Validator interface
- Multiple delivery channels active → Adapter pattern
- Code duplication across verticals → Factory pattern

**YAGNI:** Don't build for problems you don't have.

### Future: Protocol Retrieval (Enterprise Only)

**Not for MVP. Note for future enterprise capability.**

When protocol libraries grow large (50-200+ rules), manual rule selection becomes a burden. At that point, consider **Protocol Retrieval**:

```
Consumer (MVP):     User picks 3-5 rules manually → inject → validate
Enterprise (Future): Task triggers retrieval of relevant rules → inject → validate
```

| Trigger | Capability |
|---------|------------|
| Protocol library exceeds ~30 rules | Consider retrieval |
| Users complain "too many rules to track" | Build retrieval |
| Domain experts can't remember which rules apply | Build retrieval |

**What it is:**
- Similarity search to find relevant rules for the task
- Not RAG (document retrieval for knowledge)
- Protocol Retrieval (rule retrieval for enforcement)

**What it requires:**
- Rule indexing/embeddings
- Vector store
- Retrieval logic

**QA Engine already hints at this:**
- 28 Design Decisions
- Each step enforces specific DDs (not all 28)
- That's manual retrieval baked into step definitions
- Automated retrieval when DD count grows

**Decision:** Don't build for MVP. Revisit when enterprise protocol libraries justify it.

---

## Enterprise Vertical Pricing: The Clinic Example

### The Scenario

One healthcare clinic (enterprise customer):
- 20-50 staff (doctors, nurses, admin)
- Each person makes 10-50 AI calls/day
- High volume, high stakes

### Usage Math

```
Small Clinic:
├── 20 users
├── 20 calls/user/day
├── 400 calls/day
├── 8,000 calls/month
├── API cost @ $0.05/call = $400/mo
└── Need to price above $400/mo + margin

Large Clinic:
├── 50 users
├── 40 calls/user/day
├── 2,000 calls/day
├── 40,000 calls/month
├── API cost @ $0.05/call = $2,000/mo
└── Need to price above $2,000/mo + margin
```

### Pricing Options

| Model | Structure | Pros | Cons |
|-------|-----------|------|------|
| **Per-seat** | $50/user/mo | Scales with size | Heavy users kill margin |
| **Usage-based** | $0.10/call | Aligned with costs | Customers hate unpredictable |
| **Tiered flat** | $X for Y users + Z calls | Predictable both sides | Overages complex |
| **Per-clinic** | Flat rate per location | Simple sales | Must estimate usage |

### Recommended: Tiered Clinic Packages

| Package | Users | Calls/mo | Price | Our Margin |
|---------|-------|----------|-------|------------|
| **Clinic Starter** | Up to 10 | 5,000 | $500/mo | ~60% |
| **Clinic Pro** | Up to 25 | 15,000 | $1,200/mo | ~65% |
| **Clinic Enterprise** | Up to 50 | 40,000 | $2,500/mo | ~68% |
| **Health System** | Unlimited | Custom | Custom | Negotiated |

**Overage:** $0.08/call beyond included (still profitable)

### Why This Works

```
Clinic Pro Example:
├── Revenue: $1,200/mo
├── API cost (15K calls @ $0.05): $750/mo
├── Validation: $0 (local logic)
├── Infrastructure: ~$50/mo
├── Gross margin: $400/mo (33%)
│
├── With volume API discount (40% off):
├── API cost: $450/mo
├── Gross margin: $700/mo (58%)
└── VIABLE
```

### Key Levers

1. **Volume API discounts** - Negotiate with OpenAI/Anthropic as usage grows
2. **Local validation** - Gates run locally, not API calls
3. **Included calls** - Baseline profitable, overage is gravy
4. **Annual contracts** - Lock in revenue, negotiate better API rates

### The Enterprise Difference

| Consumer | Enterprise |
|----------|------------|
| Price sensitive ($15/mo max) | Budget available ($1K-5K/mo) |
| Unpredictable usage | Estimable usage patterns |
| Churn risk | Annual contracts |
| Support burden | Dedicated success |
| Can't negotiate API rates | Volume discounts |

**Enterprise non-tech verticals work because price tolerance accommodates AI costs.**

---

## Competitive Landscape

| Competitor | What They Do | Gap |
|------------|--------------|-----|
| Custom GPTs | User defines instructions | No enforcement, AI ignores them |
| Claude Projects | Persistent context | No validation, no reference tracking |
| Cursor Rules | IDE-specific protocols | No enforcement mechanism |
| System Prompts | One-time instructions | No progressive validation |

**Our Differentiation:** We don't just define rules. We **enforce** them.

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Scope creep ("good for nothing") | Start with ONE gate type (checklist), prove value, expand |
| Validation complexity | Tiered approach - simple first, semantic later |
| User effort to configure | Pattern library + AI-assisted rule extraction |
| Platform dependency | Multi-platform from day 1 (MCP + prompt-based + extension) |

---

## MVP Scope

**Ship this first:**

1. **Reference Tracker** - Validates AI read ALL references before proceeding
2. **Checklist Gate** - User defines 3-5 criteria, gate validates output
3. **One template** - Start with "Writing" (largest user base)
4. **Claude Code only** - Prove concept in MCP environment first

**Success Metrics:**
- Users report fewer "AI ignored my instructions" incidents
- Measurable improvement in output quality (user surveys)
- Retention: users who configure gates keep using them

---

## Relationship to Isagawa Platform

| Aspect | This Product | Platform |
|--------|--------------|----------|
| Positioning | Horizontal, prosumer | Vertical, domain-specific |
| Protocols | User-defined | Expert-authored |
| Smart Gates | Generic enforcement | Domain architecture enforcement |
| Revenue | Volume ($29-79/mo) | Enterprise ($500-2,500/mo) |
| Strategic Role | Top of funnel, distribution | Core business, high margin |

**Not a replacement.** This is lead generation for the platform.

Users who need deeper, domain-specific enforcement (QA, Legal, Finance) graduate to Execution Engines.

---

## Strategic Sequencing: Why Personal Product Before Healthcare

**Decision:** Pursue Personal Product as second product (after QA), before Healthcare vertical.

### The Trade-off

| Factor | Healthcare Vertical | Personal Product |
|--------|--------------------|--------------------|
| **TAM** | Large (enterprise) | Massive (every AI user) |
| **Margin** | High ($$$$/customer) | Low ($15/user) but volume |
| **Sales Cycle** | 6-12 months | Days (self-serve) |
| **Validation Speed** | Slow (enterprise) | Fast (usage data in weeks) |
| **Competition** | Credo AI, Holistic AI present | **Nobody** |
| **Domain Expertise** | Required (HIPAA, clinical) | Not required |

### Rationale: Distribution Before Depth

1. **Distribution Moat**
   - Personal Product puts Isagawa in front of millions
   - When Healthcare launches, brand awareness already exists
   - Healthcare sales pitch: "We're the company behind [popular consumer product]"

2. **Validation Speed**
   - Personal Product validates Protocols + Smart Gates at scale
   - Learn faster with 10,000 users than 10 enterprise pilots

3. **No Competition Window**
   - Healthcare: Credo AI, Holistic AI, Arthur already positioned
   - Personal: Wide open. First mover wins.

4. **Funnel Economics**
   ```
   Millions of Personal users (free/low cost)
           ↓
   Some become power users ($15-20/mo)
           ↓
   Some work at enterprises → "We need this for our domain"
           ↓
   Healthcare/Finance/Legal Execution Engine sale ($$$)
   ```

5. **Lower Risk**
   - Personal Product: Ship MVP, see if it works, iterate fast
   - Healthcare: 12-month commitment before knowing if it sells

### Proposed Sequencing

| Timeline | Product | Focus |
|----------|---------|-------|
| **Now** | QA Execution Engine | Current vertical |
| **Q2 2026** | Personal Product MVP | Checklist Gate + Writing template |
| **Q3 2026** | Personal Product Pro | Pattern library, cross-platform |
| **Q4 2026** | Healthcare Execution Engine | With distribution from Personal |

**The Personal Product becomes the distribution moat that makes ALL future verticals easier to sell.**

---

## Partnership Strategy: Compliance vs. Execution

### The Landscape

| Company | Layer | What They Do |
|---------|-------|--------------|
| **Credo AI** | Compliance | AI inventory, risk assessment, regulatory alignment |
| **Holistic AI** | Compliance | Bias detection, risk scoring, audit trails |
| **Arthur AI** | Compliance | Agent discovery, monitoring, observability |
| **Isagawa** | Execution | Step-by-step enforcement, non-bypassable gates |

**Key Insight:** They observe and report. We enforce during execution. These are **complementary, not competitive.**

### The Partnership Logic

```
Enterprise Customer Wants:
├── Compliance Layer (Credo AI) → "Prove we followed the rules"
└── Execution Layer (Isagawa)   → "Enforce rules during work"

Together = Complete AI Governance Stack
```

Bundling makes sense. Enterprises want both layers.

### Risk Assessment

| Partnership Timing | Risk of Idea Theft | Our Leverage |
|-------------------|-------------------|---------------|
| **Now** (pre-distribution) | **HIGH** | Low - they don't need us |
| **After Personal Product** | Medium | Medium - we have users |
| **After multiple verticals** | Low | High - we have brand + customers |

### Why They Might NOT Copy Us

- **Execution is hard** - 28 Design Decisions, Quality Gates architecture = months of work
- **Different DNA** - They're compliance people, not execution people
- **Focus** - They're busy expanding their compliance stack
- **If they could, they would** - Execution enforcement is obvious; they haven't built it

### Why They MIGHT Copy Us

- **Resources** - They have more engineers, more funding
- **Customer access** - Already in enterprise accounts
- **Natural extension** - "We do compliance... why not enforcement?"

### Partnership Options

| Option | Risk | Reward |
|--------|------|--------|
| **No partnership** | Compete for same budget | Keep full ownership |
| **Technical integration** | Low - API level only | Access their customers |
| **Strategic partnership** | High - they see everything | Joint GTM, faster sales |
| **Acquisition target** | They validate market | Exit opportunity |

### Recommended Approach: Partner from Strength

```
Phase 1 (Now): Build Alone
   └── Ship QA Engine + Personal Product
   └── Establish brand + distribution
   └── NO partnerships yet

Phase 2 (After Distribution): Technical Integration
   └── "Isagawa works with Credo AI"
   └── API-level only, no strategic sharing
   └── We plug into their compliance dashboard

Phase 3 (From Strength): Consider Strategic Partnership
   └── We have users, brand, multiple verticals
   └── Partnership from position of leverage
   └── OR acquisition at premium valuation
```

### The Protection Principle

> **Distribution is your protection.**

With millions of Personal Product users + enterprise customers, competitors can't just "steal the idea" - they'd have to steal market position. That's much harder.

**Partner from strength, not weakness.**

---

## Open Questions

1. **Branding:** Same brand? Sub-brand? Separate?
2. **Key Innovation Naming:** "Protocol Enforcement" (action) vs "Smart Gates for Personal Protocols" (product)?
3. **Platform priority:** MCP first? Browser extension first? Both?
4. **Pricing:** Is $15/mo right for Pro tier?
5. **Templates:** Which categories first beyond Writing?

---

## Next Steps (If Approved)

1. Validate demand - Quick landing page, gauge interest
2. Build MVP - Reference Tracker + Checklist Gate
3. Test with 10 users - Iterate based on feedback
4. Launch free tier - Build user base
5. Add Pro features - Monetize

---

*End of idea document.*
