# Design: Isagawa Consumer Platform

**Version:** 0.1 (Draft)
**Created:** 2026-01-07
**Status:** Design Discussion

---

## 1. Overview

**Product:** Isagawa Consumer Platform - AI Management Layer for everyday LLM users.

**Problem:** AI users repeat themselves constantly. Custom instructions, project rules, .cursorrules - acknowledged but sometimes not followed or skipped. No enforcement mechanism exists.

**Solution:** Smart Gates that enforce user-defined protocols during AI execution. Inject rules before LLM call, validate output after, retry with fix if needed.

**Core Architecture:**
```
User Task + Rules → Pre-Gate (inject) → LLM Call → Post-Gate (validate) → Pass/Retry
```

**Scope:** Process-based enforcement for ANY LLM task (not domain-specific). Works for writing, code generation, research, data analysis, planning, learning, summarization - any task where you want AI to follow YOUR process rules.

**Category:** AI Management Layer (execution control), NOT AI Governance Layer (compliance/documentation).

---

## 2. What We're Building

### 2.1 The Product

A web application where users:
1. Define their protocol (3-5 rules)
2. Submit tasks (ANY LLM task)
3. Get AI output that follows their rules (enforced, not suggested)

### 2.2 Use Cases (Process-Based, Not Domain-Limited)

| Use Case | Rules Example | Current Problem | Isagawa Solution |
|----------|---------------|-----------------|------------------|
| **Writing** | "Under 500 words, include CTA, conversational tone" | ChatGPT: 800 words, no CTA | Validates word count, auto-retries |
| **Code Generation** | "Follow PEP 8, include docstrings, max 80 chars/line" | Claude: No docstrings, 120 char lines | Validates style, enforces standards |
| **Data Analysis** | "Always cite sources, show methodology, visualize results" | ChatGPT: No sources cited | Validates citations, retries |
| **Research** | "Cite 3+ peer-reviewed papers, academic tone, define terms" | Claude: Only 1 citation | Counts citations, enforces minimum |
| **Planning** | "Break into max 5 steps, estimate time, identify blockers" | ChatGPT: 12 steps, no estimates | Validates structure, enforces format |
| **Learning** | "ELI5 explanations, use analogies, avoid jargon" | Claude: Technical jargon | Checks language level, retries |
| **Summarization** | "Under 200 words, bullet points only, key takeaways" | ChatGPT: 400 words, paragraphs | Validates format and length |

**The pattern:** ANY task where you want AI to follow YOUR process rules.

**Market Size:**
- 100M+ ChatGPT weekly active users (potential TAM)
- 27M developers (code generation)
- 50M+ content creators (writing)
- 20M+ students (essays, homework)
- 8M+ researchers (academic work)
- 3M+ data analysts (analysis, reports)

### 2.2 The Differentiator

| Existing Tools | Isagawa |
|----------------|---------|
| Instructions = suggestions | Rules = enforced |
| AI acknowledges then ignores | AI must comply or retry |
| User repeats themselves | System handles enforcement |
| No validation | Post-gate validation |
| No fix guidance | Self-healing with explicit fixes |

### 2.3 Two Delivery Domains

| Domain | Protocol Source | Gate Location | Examples |
|--------|-----------------|---------------|----------|
| **Tech (IDE)** | Native (Skills, .cursorrules) | MCP tool (local) | QA Engine, DevOps |
| **Non-Tech (Web App)** | User-configured in our app | Server function | Consumer, Healthcare, Legal |

**MVP Focus:** Non-Tech (Web App) - Consumer product.

---

## 3. MVP Scope

### 3.1 What's In

| Component | Description |
|-----------|-------------|
| Web UI | Task input, rule config, output display |
| Pre-gate | Inject rules into prompt |
| LLM call | OpenAI/Anthropic API |
| Post-gate | Validate output against rules |
| Self-healing | Retry with fix prompt (max 3) |
| One template | "Writing" (blog, email, content) |

### 3.2 What's Out (MVP)

| Component | Why Out |
|-----------|---------|
| Multiple templates | Start with one, expand later |
| Rule retrieval | Manual selection sufficient for 3-5 rules |
| Browser extension | Unit economics don't work |
| Mobile app | Web-first |
| Team features | Individual users first |

### 3.3 MVP Code (~60 lines)

```python
# smart_gate.py

def pre_gate(user_input: str, rules: list[str]) -> dict:
    """Validate input, inject rules into prompt."""
    if not user_input or len(user_input.strip()) < 10:
        return {
            "status": "NEEDS_RETRY",
            "fixes": {"hint": "Provide clear task (10+ chars)"}
        }

    if not rules:
        return {
            "status": "NEEDS_RETRY",
            "fixes": {"default_rules": ["Be concise", "Be accurate"]}
        }

    rules_text = "\n".join(f"- {r}" for r in rules)
    return {
        "status": "PASS",
        "prompt": f"RULES YOU MUST FOLLOW:\n{rules_text}\n\nTASK: {user_input}"
    }


def post_gate(output: str, rules: list[str]) -> dict:
    """Validate output against rules, provide fix if needed."""
    violations = []
    fixes = {}

    for rule in rules:
        if not _check_rule(output, rule):
            violations.append(rule)
            fixes[rule] = f"Revise to address: '{rule}'"

    if violations:
        return {
            "status": "NEEDS_RETRY",
            "violations": violations,
            "fixes": fixes,
            "retry_prompt": _build_retry_prompt(output, violations, fixes)
        }

    return {"status": "PASS", "output": output}


def execute(task: str, rules: list[str], llm_client, max_retries=3) -> dict:
    """Execute with self-healing gates."""
    # Pre-gate
    pre = pre_gate(task, rules)
    if pre["status"] == "NEEDS_RETRY":
        rules = pre["fixes"].get("default_rules", rules)
        pre = pre_gate(task, rules)

    # LLM call
    response = llm_client.complete(pre["prompt"])

    # Post-gate with retries
    for _ in range(max_retries):
        post = post_gate(response, rules)
        if post["status"] == "PASS":
            return {"success": True, "output": post["output"]}
        response = llm_client.complete(post["retry_prompt"])

    return {"success": False, "output": response, "violations": post["violations"]}
```

---

## 4. User Experience

### 4.1 Happy Path

```
1. User opens app
2. User defines rules:
   - "Include a call-to-action"
   - "Under 500 words"
   - "Professional tone"
3. User enters task: "Write a blog post about productivity"
4. System executes:
   - Pre-gate injects rules
   - LLM generates
   - Post-gate validates
   - All rules pass
5. User sees output + "Protocol Check: 3/3 Passed"
```

### 4.2 Retry Path

```
1-4. Same as above
5. Post-gate detects: "650 words (over by 150)"
6. System auto-retries with fix prompt
7. Attempt 2: 480 words - passes
8. User sees output + "Protocol Check: 3/3 Passed (1 retry)"
```

### 4.3 Failure Path

```
1-4. Same as above
5. Post-gate fails after 3 retries
6. User sees output + "Protocol Check: 2/3 Passed"
7. User sees which rule failed + suggested fix
8. User can: Edit rules, Regenerate, or Accept as-is
```

---

## 5. Technical Architecture

### 5.1 Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| Frontend | React/Next.js | Fast, familiar, good UX |
| Backend | FastAPI (Python) | Gate logic already in Python |
| LLM | OpenAI/Anthropic API | Start with one, add more |
| Database | PostgreSQL | User accounts, rule storage |
| Hosting | Vercel + Railway | Simple, scalable |

### 5.2 Data Model

```
User
├── id
├── email
├── subscription_tier
└── created_at

Protocol
├── id
├── user_id
├── name ("My Writing Rules")
├── rules[] ("Include CTA", "Under 500 words")
└── created_at

Execution
├── id
├── user_id
├── protocol_id
├── task_input
├── output
├── retries_used
├── rules_passed[]
├── rules_failed[]
└── created_at
```

### 5.3 API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/protocols` | GET, POST | List/create protocols |
| `/protocols/{id}` | GET, PUT, DELETE | Manage protocol |
| `/execute` | POST | Run task with protocol |
| `/executions` | GET | History |

---

## 6. Business Model

### 6.1 Pricing

| Tier | Price | Calls/mo | Target |
|------|-------|----------|--------|
| Free | $0 | 50 | Trial |
| Starter | $29/mo | 500 | Light users |
| Pro | $49/mo | 2,000 | Regular users |
| Power | $79/mo | 5,000 | Heavy users |

### 6.2 Unit Economics

```
Pro Tier Example:
├── Revenue: $49/mo
├── API cost (2K calls @ $0.02 avg): $40/mo
├── Gross margin: $9/mo (18%)

With volume discount (40% off API):
├── API cost: $24/mo
├── Gross margin: $25/mo (51%)
```

**Note:** Margins improve with scale (API volume discounts) and usage patterns (not all users max out).

### 6.3 Funnel

```
Free trial (50 calls)
      ↓
Starter ($29) - sees value
      ↓
Pro ($49) - regular user
      ↓
Power ($79) - heavy user
      ↓
Enterprise need → Upsell to Vertical Execution Engine
```

---

## 7. Success Metrics

### 7.1 MVP Launch

| Metric | Target |
|--------|--------|
| Users signed up | 500 |
| Free → Paid conversion | 5% |
| Retention (30-day) | 40% |
| Rules enforced successfully | 80% |

### 7.2 Post-MVP

| Metric | Target |
|--------|--------|
| MRR | $5K |
| Active users | 1,000 |
| NPS | 40+ |
| Retry success rate | 70% |

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API costs exceed revenue | High | High | Strict usage limits, monitor closely |
| Post-gate validation too simple | Medium | Medium | Start simple, add semantic later |
| Users don't configure rules | Medium | Medium | Templates, onboarding wizard |
| Competition from AI providers | Medium | High | Move fast, build brand |

---

## 9. Open Questions

1. **Validation sophistication:** Keyword matching sufficient for MVP, or need basic semantic?
2. **Template library:** How many templates at launch? Just Writing?
3. **Onboarding:** Wizard vs. blank slate?
4. **Branding:** "Isagawa" or separate consumer brand?

---

## 10. Next Steps

1. **Validate demand** - Landing page, waitlist
2. **Build MVP** - ~2 weeks for core functionality
3. **Alpha test** - 10-20 users, iterate
4. **Launch free tier** - Build user base
5. **Add paid tiers** - Monetize

---

*End of design doc. Ready for section-by-section review.*
