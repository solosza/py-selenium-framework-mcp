# Isagawa Internal Ruleset Factory  
*One-Page Conceptual & Technical Diagram*

**Audience:** Internal (Founder, Engineers, Agents, Junior Contributors)  
**Purpose:** Provide a clear, visual understanding of how Isagawa turns domain expertise into enforceable execution at scale.

This document is **foundational**. It explains *how work becomes rules*, *how rules become enforcement*, and *how enforcement becomes scalable execution*.

---

## High-Level Concept

Isagawa operates as a **Ruleset Factory**.

The factory’s job is to reliably transform **human expertise** into **machine-enforced execution**, without rewriting the engine each time.

---

## End-to-End Flow (Bird’s Eye View)

```
Domain Expert
  (Human)
     │
     ▼
Domain Knowledge
(How work SHOULD be done)
     │
     ▼
Domain Decomposition
(Break work into steps)
     │
     ▼
Ruleset Definition
(Rules, constraints, invariants)
     │
     ▼
Quality Gates
(Validation & enforcement points)
     │
     ▼
Skill Assembly
(Composable execution units)
     │
     ▼
Execution Engine
(Orchestration & state)
     │
     ▼
Enforced Execution
(AI + rules + gates)
     │
     ▼
Consistent Outcomes
(Trust, reliability, scale)
```

Everything above the **Execution Engine** is *human-authored*.  
Everything below it is *machine-executed*.

---

## Layered Architecture (Mental Model)

```
┌───────────────────────────────────────┐
│        DOMAIN KNOWLEDGE LAYER          │
│  (Experts, SMEs, Founders)             │
└───────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│        RULESET CREATION LAYER          │
│  - Step definitions                   │
│  - Constraints                        │
│  - Invariants                         │
│  - Failure modes                      │
└───────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│        ENFORCEMENT LAYER               │
│  - Quality gates                      │
│  - Pass / Fail checks                 │
│  - Escalation rules                   │
└───────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│        EXECUTION ENGINE                │
│  - Orchestration                      │
│  - State management                   │
│  - Retry / stop logic                 │
└───────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│        DELIVERY & INTEGRATION          │
│  - IDE plugins                        │
│  - pip packages                       │
│  - MCP servers                        │
│  - CI/CD hooks                        │
└───────────────────────────────────────┘
```

---

## Ruleset Creation: Step-by-Step (Detailed)

### 1. Domain Decomposition
**Goal:** Break expert work into enforceable steps.

Questions asked:
- What are the required steps?
- What order must they occur in?
- Which steps are mandatory?
- Where do errors usually happen?

Output:
- Ordered step list
- Known failure points

---

### 2. Rule & Constraint Definition
**Goal:** Define what “correct” means.

Types of rules:
- Hard constraints (must always be true)
- Soft constraints (warnings or thresholds)
- Invariants (never allowed to change)
- Preconditions / postconditions

Output:
- Formal rule definitions
- Clear pass/fail criteria

---

### 3. Quality Gate Placement
**Goal:** Prevent bad execution early.

Quality gates:
- Validate output at each step
- Block progression if rules fail
- Escalate when ambiguity exists

Example:
```
Step Completed?
   │
   ├─ Pass → Continue
   └─ Fail → Retry / Stop / Escalate
```

Output:
- Gate logic bound to steps

---

### 4. Skill Assembly
**Goal:** Package rules + steps into reusable units.

A **Skill** includes:
- Steps
- Rules
- Gates
- Execution metadata

Skills are:
- Versioned
- Composable
- Domain-specific

---

### 5. Execution & Enforcement
**Goal:** Execute without improvisation.

```
Input
  ↓
Skill Invoked
  ↓
Step Executed
  ↓
Gate Checked
  ↓
Allowed? ── Yes → Next Step
          └─ No  → Stop / Retry / Escalate
```

The AI never bypasses gates.

---

## Human vs Machine Responsibilities (Clear Boundary)

```
HUMANS OWN:
- Architecture
- Doctrine
- Rules
- Constraints
- Approval of change

MACHINES OWN:
- Execution
- Repetition
- Enforcement
- State tracking
- Consistency
```

This boundary is intentional and enforced.

---

## Why This Scales Across Vertical

Only **Domain Knowledge** changes.

```
QA Ruleset        ┐
Legal Ruleset     │
Healthcare Ruleset│  → Same Engine
Finance Ruleset   │
Operations Ruleset┘
```

The factory stays the same.  
The inputs change.

---

## Junior-Friendly Summary

If you remember nothing else:

- Humans decide *what is correct*
- Isagawa enforces it
- AI executes inside the rules
- Nothing important is left to chance

---

## Status

- **Internal-only**
- **Foundational**
- **Referenced by thesis**
- **Used to onboard contributors**

---

Recommended next moves (in order)

Lock this doc (treat it as internal doctrine)

Use it to:

Evaluate any future technical partner

Guide AI-assisted development

Onboard a future principal implementer

Then:

90-day execution plan

First enforcement pilot

Clear “no-cofounder-yet” confidence

If/when you’re ready, we can:

Turn this into a single visual slide

Map it directly to repo structure

Use it to design a minimal QA reference implementation

You’ve now crossed from idea → system.

*End of Document*
