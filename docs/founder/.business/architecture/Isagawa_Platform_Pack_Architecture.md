# Isagawa Platform & Pack Architecture
## Unified Model for Tech and Non‑Tech Verticals

**Purpose:**  
This document defines how Isagawa scales across industries using a **single core platform** with **modular packs**, while protecting IP, enforcement integrity, and long‑term valuation.

It incorporates **all prior decisions** regarding:
- Platform vs Pack ownership
- SME participation (no engine ownership)
- Customization constraints
- Tech vs Non‑Tech go‑to‑market differences
- Healthcare as a flagship non‑tech example
- QA as the flagship tech example

---

## 1. Core Invariant (Applies to Every Vertical)

Isagawa is **never multiple engines**.

It is:

> **One enforcement platform**  
> + **Domain / Persona Packs**  
> + **Constrained configuration**

```
┌─────────────────────────────────────────────┐
│ ISAGAWA CORE PLATFORM                       │
│ • Quality Gates Engine                     │
│ • Enforcement runtime                      │
│ • Escalation & human handoff               │
│ • Audit & traceability                     │
│ • Policy / config layer                   │
│ • Pack runtime & versioning                │
└─────────────────────────────────────────────┘
                ▲
                │
┌─────────────────────────────────────────────┐
│ PACKS (DOMAIN OR PERSONA)                   │
│ • Enforced workflows                       │
│ • Rules & validation logic                 │
│ • Approved variants                        │
│ • SME‑validated content                   │
└─────────────────────────────────────────────┘
                ▲
                │
┌─────────────────────────────────────────────┐
│ CONFIGURATION (SAFE VARIANCE ONLY)          │
│ • Thresholds                               │
│ • Terminology                              │
│ • Timing & escalation tuning               │
│ • Local policy alignment                   │
└─────────────────────────────────────────────┘
```

**Non‑negotiable rule:**  
Packs and configuration may **never weaken enforcement**.  
They may only **specialize or strengthen it**.

---

## 2. SME Participation Model (Global Rule)

SMEs **never receive an engine**.

They participate as **Pack Contributors**.

### SMEs:
- Validate workflows
- Define required steps
- Define escalation boundaries
- Approve what is *safe to automate*

### SMEs do NOT:
- Control platform architecture
- Modify Quality Gates behavior
- Own IP
- Define roadmap
- Promise behavior to customers

### Revenue:
- Platform revenue → **100% Isagawa**
- Pack revenue → **shared with contributing SME(s)**
- Custom services → Isagawa‑led, SME optional

---

## 3. Customization Policy (Applies Everywhere)

### Allowed (sell early)
- Threshold tuning
- Role naming
- Escalation timing
- Policy mappings

### Controlled (sell later)
- Published **Variant Packs**
  - e.g., Acute Care vs Outpatient
  - e.g., Enterprise QA vs Startup QA

### Forbidden (never)
- Removing gates
- Bypassing enforcement
- One‑off logic forks
- “Just for us” exceptions

**Golden rule:**  
No customer can remove a gate. They can only add stricter ones.

---

## 4. TECH VERTICAL EXAMPLE — QA

### 4.1 What the Platform Is (Buyer View)

**Isagawa QA Execution Platform**

Bought by:
- Engineering leadership
- QA leadership
- Platform owners

Purpose:
- Enforce how AI‑generated tests are allowed to exist
- Prevent low‑quality, non‑compliant automation
- Provide auditability and safety

---

### 4.2 Pack Structure (Persona‑Based)

Tech packs are **persona‑aware**.

#### Developer Packs (Execution)
- **QA Test Authoring Pack**
- **UI Automation Pack**
- **API Testing Pack**

Focus:
> How work is produced

---

#### Admin / Governance Packs (Control)
- **QA Governance Pack**
- **Compliance & Audit Pack**
- **CI/CD Enforcement Pack**

Focus:
> What is allowed into production

---

### 4.3 QA Visual Architecture

```
ISAGAWA QA PLATFORM
│
├── Developer Packs
│   ├── Test Authoring
│   ├── UI Automation
│   └── API Testing
│
├── Admin / Governance Packs
│   ├── QA Governance
│   ├── Compliance & Audit
│   └── CI/CD Enforcement
│
└── Configuration
    ├── Org standards
    ├── Risk tolerance
    └── Repo policies
```

### 4.4 Distribution vs Sales (Tech)

- **Distribution:** bottom‑up (pip, GitHub, docs)
- **Sales:** platform license + pack expansion
- **Motion:** developers adopt → org formalizes

---

## 5. NON‑TECH VERTICAL EXAMPLE — HEALTHCARE

### 5.1 What the Platform Is (Buyer View)

**Isagawa Clinical Execution Platform**

Bought by:
- Hospital leadership
- Compliance & risk
- Operations

Purpose:
- Enforce clinical workflows
- Prevent missed steps
- Provide audit trails
- Reduce liability

⚠️ Explicitly NOT:
- Diagnosis
- Treatment recommendations
- Medical judgment

---

### 5.2 Healthcare Pack Structure (Workflow‑Based)

Non‑tech packs are **workflow‑centric**, not persona‑centric.

#### Example Packs:
- **Wound Care Pack**
- **Imaging Prep Pack**
- **Clinical Documentation Pack**
- **Care Transitions Pack**

Each pack:
- Contains multiple workflows
- Shares one enforcement engine
- Is validated by nurses + physicians
- Has strict escalation to humans

---

### 5.3 Healthcare Visual Architecture

```
ISAGAWA CLINICAL PLATFORM
│
├── Workflow Packs
│   ├── Wound Care
│   ├── Imaging Prep
│   ├── Documentation
│   └── Care Transitions
│
└── Configuration
    ├── Facility policies
    ├── Jurisdiction rules
    └── Escalation timing
```

---

### 5.4 Distribution vs Sales (Healthcare)

- **Distribution:** sales‑led only
- **Sales:** platform first → packs added
- **Motion:** land with one pack → expand per department

---

## 6. Tech vs Non‑Tech Comparison

| Dimension | Tech (QA) | Non‑Tech (Healthcare) |
|--------|-----------|-----------------------|
| Primary users | Developers | Clinicians / Ops |
| Buyer | Engineering leadership | Exec / Compliance |
| Pack type | Persona‑based | Workflow‑based |
| Distribution | Bottom‑up | Top‑down |
| Customization | Config + variants | Config + variants |
| SME role | Standards validator | Safety authority |

---

## 7. Generic Plug‑and‑Play Vertical Template

This is reusable for **any future vertical**.

```
ISAGAWA <VERTICAL> PLATFORM
│
├── Packs
│   ├── Core Workflow Pack
│   ├── Risk / Compliance Pack
│   ├── Advanced / Variant Pack(s)
│
└── Configuration
    ├── Local rules
    ├── Thresholds
    └── Escalation tuning
```

Examples:
- Construction → Project / RFI / Closeout Packs
- Real Estate → Due Diligence / Disclosure Packs
- Sales → Qualification / Disclosure Packs
- Education → Compliance / Documentation Packs

---

## 8. Why This Model Wins

- One engine → infinite verticals
- SMEs monetized without IP loss
- Clear enforcement authority
- Predictable land‑and‑expand
- Clean investor narrative
- High switching costs

---

## 9. Final Lock‑In Summary

Isagawa is:
- A **platform company**
- Owning **execution enforcement**
- Selling **standardized packs**
- Allowing **constrained variance**
- Scaling across **tech and non‑tech**

This document is the **operating truth** for all future decisions.
