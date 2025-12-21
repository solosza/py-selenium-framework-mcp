# AI-Orchestrated Design Phase

**Status:** Idea
**Created:** 2025-12-20
**Context:** Emerged during QA guidance layer design

---

## Problem

Currently, designing execution engine steps is manual:
- Human designs each step (7 sections)
- Human validates completeness
- Human runs design audit
- Human creates PRD

This is time-consuming and error-prone.

---

## Idea

Apply the same automation pattern we use for execution to the design phase itself:

```
CURRENT (Manual)              AUTOMATED (AI-Orchestrated)
────────────────              ──────────────────────────
Human designs Step 1    →     AI designs Step 1 (guided by skill)
Human checks complete   →     qg_step_design_complete validates
Human designs Step 2    →     AI designs Step 2 (guided by skill)
...                           ...
Human runs audit        →     qg_design_audit validates
Human creates PRD       →     AI creates PRD (guided by skill)
```

---

## Implementation Approach

| Component | Purpose |
|-----------|---------|
| `design-orchestrator` skill | Guides AI through designing each step |
| `qg_step_design_complete` | Validates step has all 7 sections |
| `qg_design_audit` | Validates DD coverage, contracts |
| Design state manager | Tracks which steps designed |

**AI would need as input:**
1. Tool chain definition (what tools exist, what they do)
2. Design decisions (DDs) to enforce
3. Meta-architecture to follow

**AI would produce as output:**
- Complete step files (step-01.md, step-02.md, ...)
- Design audit report
- PRD draft

---

## Automation Levels

| Level | Description |
|-------|-------------|
| **Guided** | AI follows skill, human approves each step design |
| **Semi-auto** | AI designs all steps, human reviews at end |
| **Full auto** | AI designs, validates, creates PRD (human approves final) |

---

## Value

- Faster design cycles
- Consistent step structure
- Automated validation
- Meta-level application of Isagawa pattern (using ruleset factory to design rulesets)

---

## Next Steps (When Picked Up)

1. Move to `backlog/`
2. Create PRD with specific requirements
3. Implement design-orchestrator skill
4. Test with a new vertical

---

*Parked to avoid scope creep during QA guidance layer implementation.*
