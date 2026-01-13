# Isagawa Launch Roadmap

**Version:** 1.0
**Created:** 2026-01-05
**Status:** Phase 1 Complete, Phase 2 In Planning

---

## Overview

Prioritized task list for:
1. QA Platform MVP (Ship to first users)
2. Business Foundation (Legal, finance, infrastructure)
3. Revenue & Validation (First paying customer)
4. Healthcare Vertical (Second execution engine)

---

## PHASE 1: QA PLATFORM MVP 🔄 IN PROGRESS

**Goal:** Working product someone can install and use

**Current Status:** Defect fixes in progress

### Completed Work

| Project | Task | Description | Status |
|---------|------|-------------|--------|
| qa-execution-engine | 1.0-15.0 | All 10 quality gates + integration tests | ✅ DONE |
| release-readiness | 1.0-3.0 | Audit Trail, Self-Heal Cap, Execution Mode, License/Docs | ✅ DONE |
| enhanced-runtime | 1.0-8.5 | Scope Discovery, RuntimeValidator, Visual Feedback, WebInterface Checker | ✅ DONE |

### In Progress

| Project | Task | Description | Status |
|---------|------|-------------|--------|
| defect-fixes | 1.0-5.0 | Two-Pass Discovery (DEF-045), Test Redundancy (DEF-046) | 🔄 IN PROGRESS |

### Remaining Phase 1 Tasks

| # | Task | Owner | Status |
|---|------|-------|--------|
| 1.1 | Complete defect fixes (DEF-045, DEF-046) | FOUNDER | IN PROGRESS |
| 1.2 | Smoke Tests (2+ sites) | FOUNDER | IN PROGRESS (retest pending) |
| 1.3 | Adversarial Tests | FOUNDER | NOT STARTED |
| 1.4 | E2E Integration Verification | FOUNDER | IN PROGRESS (retest pending) |
| 1.5 | PyPI packaging (`pip install isagawa-qa`) | FOUNDER | NOT STARTED |
| 1.6 | README quick start | FOUNDER | STARTED |
| 1.7 | Landing page (1-pager) | CMO | NOT STARTED |
| 1.8 | First user outreach (3-5 targets) | FOUNDER | NOT STARTED |

**Flow:** 1.2/1.4 found defects → 1.1 fixing → retest 1.2/1.4 → then 1.5+

---

## PHASE 2: BUSINESS FOUNDATION

**Goal:** Legitimate entity ready to accept payment

| # | Task | Owner | Dependencies | Status |
|---|------|-------|--------------|--------|
| 2.1 | Register LLC (Isagawa Corp LLC) | CMO | None | NOT STARTED |
| 2.2 | Buy domains (isagawacorp.com + alternates) | CMO | None | NOT STARTED |
| 2.3 | Open business bank account | CMO | 2.1 | NOT STARTED |
| 2.4 | Set up Stripe for payments | CMO | 2.3 | NOT STARTED |
| 2.5 | Set up email (founders@isagawacorp.com) | CMO | 2.2 | NOT STARTED |
| 2.6 | Terms of service / license finalization | FOUNDER | 2.1 | STARTED (LICENSE.md) |

### Decisions Made

**Entity Type:** LLC
- Simpler structure for bootstrap phase
- Pass-through taxation
- Plan to convert to Corp later (hence "Isagawa Corp" naming)

**Domain Strategy:**

| Domain | Purpose | Status |
|--------|---------|--------|
| isagawa.com | Ideal | TAKEN |
| **isagawaco.com** | Primary for LLC (DBA: Isagawa Co.) | TO BUY |
| isagawacorp.com | Future (after Corp conversion) | TO BUY |
| isagawa.ai | Alternative | TO CHECK |
| isagawa.io | Alternative | TO CHECK |

**Note:** LLC formation won't allow "Corp" in name. Use DBA "Isagawa Co." until Corp conversion.

**Product Model (from Platform Pack Architecture):**

```
ISAGAWA CORE PLATFORM (100% Isagawa revenue)
├── Quality Gates Engine
├── Enforcement runtime
├── Escalation & human handoff
├── Audit & traceability
└── Pack runtime & versioning
        │
        ▼
PACKS (Revenue shared with SME contributors)

QA VERTICAL:
├── Developer Packs: Test Authoring, UI Automation, API Testing
└── Admin Packs: QA Governance, Compliance & Audit, CI/CD Enforcement

HEALTHCARE VERTICAL:
├── Workflow Packs: Clinical Documentation, Handoff/Transitions, Compliance Checklists
└── (Pack determined after SME discovery)
```

**Revenue Model:**

| Component | Revenue |
|-----------|---------|
| Platform license | 100% Isagawa |
| Packs | Shared with contributing SME(s) |
| Custom services | Isagawa-led |

**Distribution (Tech/QA):**
- Bottom-up: pip install, GitHub, docs
- Sales: Platform license + pack expansion
- Motion: Developers adopt → org formalizes

**Reference:** See `Isagawa_Platform_Pack_Architecture.md` for full details

---

## PHASE 3: FIRST REVENUE & VALIDATION

**Goal:** Free beta → paid conversion + category creation

### Parallel Tracks

```
FOUNDER (Product/Sales):          CMO (Category/Content):
├── First user outreach           ├── Product onboarding
├── Beta onboarding               ├── Category-defining content
├── Feedback collection           ├── LinkedIn/distribution
├── Iterate product               ├── Case study from results
└── Convert to paid               └── Authority building
```

### Tasks

| # | Task | Owner | Dependencies | Status |
|---|------|-------|--------------|--------|
| 3.1 | Onboard CMO on product | FOUNDER + CMO | None | STARTED |
| 3.2 | First user outreach (3-4 personal contacts) | FOUNDER | None | NOT STARTED |
| 3.3 | Write category-defining content | CMO | 3.1 | NOT STARTED |
| 3.4 | First user beta onboarding | FOUNDER | 3.2 | NOT STARTED |
| 3.5 | Collect feedback, iterate product | FOUNDER | 3.4 | NOT STARTED |
| 3.6 | Publish category content (LinkedIn, blog) | CMO | 3.3 | NOT STARTED |
| 3.7 | Convert beta users to paid | FOUNDER | 3.5, 2.4 | NOT STARTED |
| 3.8 | First case study / testimonial | CMO | 3.7 | NOT STARTED |

### First User Targets (Personal Contacts)

| Role | Name | Status |
|------|------|--------|
| Principal Developer | TBD | NOT CONTACTED |
| QA Manager/Lead | TBD | NOT CONTACTED |
| Sr Test Automation Engineer | TBD | NOT CONTACTED |
| (Optional 4th) | TBD | NOT CONTACTED |

**Strategy:** Free beta → paid conversion based on value delivered

---

### CMO BRIEF: Category-Defining Content

**Why This Matters**

This is about **creating a new market category** rather than competing in an existing one.

**The Problem with Competing:**

If we say: *"Isagawa is an AI governance tool"*
- We compete with Credo AI, Holistic AI, IBM, etc.
- We're a small player in their category
- They define the rules

**The Power of Category Creation:**

If we say: *"AI Governance is the wrong approach. Here's why."*
- We CREATE a new category: **AI Execution Management**
- We define what it means
- Competitors are now playing catch-up in OUR category

---

**THE ONE PIECE OF CONTENT TO CREATE**

**Title:** "AI Governance vs AI Execution Management: Why Monitoring Isn't Enough"

**Structure:**
1. **The problem:** AI is doing real work now (not just answering questions)
2. **The current solution:** AI Governance (monitoring, compliance, documentation)
3. **Why it fails:** Watching AI work ≠ controlling how it works. Auditing after the fact ≠ preventing errors.
4. **The new category:** AI Execution Management (enforce, gate, escalate at runtime)
5. **The shift:** From "Did the AI do it right?" to "The AI can only do it right"
6. **Who's building this:** Isagawa

**Key Messaging:**

| AI Governance (What Others Build) | AI Execution Management (What Isagawa Builds) |
|-----------------------------------|----------------------------------------------|
| Monitors AI behavior | Controls AI behavior |
| Documents compliance | Enforces compliance |
| Alerts on violations | Prevents violations |
| Audits after execution | Gates during execution |
| *"Did the AI do it right?"* | *"The AI can only do it right"* |

**Format Options:**
- Blog post (primary)
- LinkedIn article
- Landing page manifesto

**Effect:** Everyone who reads it sees the world through OUR lens. Governance = old. Execution Management = new. Isagawa = the leader.

---

**Reference Documents for CMO:**
- `isagawa_corp_thesis_v3.1.md` - Full company thesis and positioning
- `Isagawa_Platform_Pack_Architecture.md` - Product model (Platform + Packs)
- `isagawa_marketing_brief_v3.0.md` - Marketing positioning
- `competitive_intel_2026-01-05.md` - Latest competitive landscape

---

## PHASE 4: HEALTHCARE VERTICAL

**Goal:** Second vertical (Packs) + multi-domain validation

### Tasks

**Timing:** Start after QA first users onboarded (Phase 3.4+)

**SME Contact:** Nurse consultant (confirmed)

| # | Task | Owner | Dependencies | Status |
|---|------|-------|--------------|--------|
| 4.1 | Healthcare workflow research | FOUNDER | 3.4 | NOT STARTED |
| 4.2 | Engage nurse consultant as Pack Contributor | FOUNDER | 4.1 | NOT STARTED |
| 4.3 | SME partnership agreement (revenue share) | FOUNDER + CMO | 4.2 | NOT STARTED |
| 4.4 | Define healthcare-specific Design Decisions | FOUNDER + SME | 4.3 | NOT STARTED |
| 4.5 | Build thin web front-end for non-tech users | FOUNDER | 4.4 | NOT STARTED |
| 4.6 | Build first Healthcare Pack | FOUNDER | 4.5 | NOT STARTED |
| 4.7 | Healthcare quality gates | FOUNDER | 4.6 | NOT STARTED |
| 4.8 | Healthcare pilot user (hospital/clinic) | FOUNDER + CMO | 4.7 | NOT STARTED |
| 4.9 | Healthcare case study | CMO | 4.8 | NOT STARTED |

### Notes

**SME Network:**
- Nurse consultant (cousin) - Pack Contributor candidate
- ER/OR nurses (cousins) - pain point discovery
- Respiratory tech, Radiology tech, Podiatrist - validation/expansion
- Nephew (EA to Pharma Tech CEO) - pharma industry intro

**Pack candidates:** Clinical Documentation, Handoff/Transitions, Compliance Checklists

**Non-tech requirement:** Thin web front-end needed (nurses won't use CLI)

**Start with ONE pack**, validate, then expand

### Reference Documents

- `references/healthcare_sme_engagement.md` - Discovery questions, engagement strategy
- `Isagawa Domain Expansion Model.md` - SME partnership structure
- `Isagawa_Platform_Pack_Architecture.md` - Platform + Pack model (Section 5: Healthcare)

---

## Dependencies

```
PHASE 1 ────────────────────────────────────────────────────────┐
(QA MVP)                                                        │
  │                                                             │
  ├── 1.1 PyPI ──► 1.2 README ──► 1.4 First User ───────────────┤
  │                                                             │
  └── 1.3 Landing ──────────────────────────────────────────────┤
                                                                │
PHASE 2 ◄───────────────────────────────────────────────────────┤
(Business)                                                      │
  │                                                             │
  ├── 2.1 Entity ──► 2.2 Register ──► 2.3 Bank ──► 2.4 Stripe ──┤
  │                                                             │
  └── 2.5 Pricing ──────────────────────────────────────────────┤
                                                                │
PHASE 3 ◄───────────────────────────────────────────────────────┤
(Revenue)                                                       │
  │                                                             │
  └── 3.1 Feedback ──► 3.2 Iterate ──► 3.3 First $ ─────────────┤
                                                                │
PHASE 4 ◄───────────────────────────────────────────────────────┘
(Healthcare)
  │
  └── 4.1 Research ──► 4.2 SME ──► 4.3 DDs ──► 4.4 Engine ──► 4.6 Pilot
```

---

## Open Questions

### Phase 2
- [x] LLC or C-Corp? → **LLC** (convert to Corp later)
- [x] Pricing model? → **Platform + Packs** (see Platform Pack Architecture)
- [x] Domain name? → **isagawaco.com** (primary for LLC/DBA), isagawacorp.com (future Corp)

### Phase 3
- [x] Who are first user targets? → **Personal contacts** (Principal Dev, QA Manager, Sr Automation)
- [x] Free tier or straight to paid? → **Free beta → paid conversion**

### Phase 4
- [x] Healthcare timing? → **After QA first users onboarded** (Phase 3.4+)
- [x] Healthcare SME contact? → **Nurse consultant** (confirmed)
- [ ] Which Pack to start with? (Wound Care recommended - discuss with nurse consultant)

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-05 | Initial roadmap created, Phase 1 marked complete |
| 1.1 | 2026-01-06 | Added owner assignments (FOUNDER/CMO), Platform+Pack pricing model, CMO brief for category content, expanded Phase 4 Healthcare with Pack candidates and SME model |

---

*This document is the master launch roadmap. Update as phases complete.*
