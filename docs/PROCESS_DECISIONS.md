# Process Decisions

Cross-cutting development process decisions that apply to ALL vertical engine builds.

These are NOT project-specific architectural decisions. These are meta-decisions about how we work.

---

## PD-001: Skills Require Quality Gates

**Date:** 2025-12-20
**Scope:** All skills with enforceable rules

**Context:**
Skills document conventions and rules, but documentation alone doesn't ensure compliance. Task 2.0 revealed tests were written without following the testing skill - the skill existed but wasn't consulted.

**Decision:**
Every skill with enforceable rules MUST have a corresponding quality gate that automates enforcement.

**Pattern:**
```
SKILL (documents rules)
   ↓
QUALITY GATE (enforces rules automatically)
```

**Examples:**

| Skill | Quality Gate | Enforcement Point |
|-------|--------------|-------------------|
| Testing Skill | TestStructureValidator | pytest collection |
| QA Guidance Layer | qg_* tools | MCP tool chain |
| Task Generation | (future) TaskValidator | Task list creation |

**Rationale:**
- Documentation can be ignored
- Automated gates cannot be bypassed
- Aligns with "Never Trust AI" principle
- Ensures consistency across vertical builds

**Implementation:**
- TestStructureValidator → Task 3.0 (pytest plugin)
- qg_* gates → Tasks 4.0-13.0

---

## PD-002: Audit Subtask in Every Parent Task

**Date:** 2025-12-20
**Scope:** Task generation template

**Context:**
Even with automated gates, explicit checkpoints help ensure compliance during development, not just at commit time.

**Decision:**
Every parent task in task lists includes an **"Audit: Verify skill conventions followed"** subtask before recording results.

**Template:**
```markdown
- [ ] X.N Run checks (lint, type, tests)
- [ ] X.N+1 **Audit: Verify skill conventions followed**
- [ ] X.N+2 Record results
- [ ] X.N+3 Commit
```

**Rationale:**
- Creates explicit checkpoint in workflow
- Visible in task list (can't be ignored)
- Belt + suspenders with automated gates
- Low cost, high compliance value

**Implementation:**
Updated `docs/2-dev-generate-tasks-v2.md` template.

---

## PD-003: TestStructureValidator Runs Automatically

**Date:** 2025-12-20
**Scope:** Testing process

**Context:**
Decision needed: Should test structure validation be manual (developer runs a script) or automated (runs during pytest)?

**Decision:**
TestStructureValidator runs **automatically as a pytest plugin** during test collection. No manual invocation required.

**Behavior:**
```
pytest collects tests
    ↓
TestStructureValidator hook runs
    ↓
Validates each test: AAA, markers, assertions, docstrings
    ↓
FAIL → Collection fails, tests blocked
PASS → Tests execute normally
```

**Rationale:**
- Manual = can be skipped
- Automated = enforcement, not guidance
- Fails fast before tests run
- Integrated into existing workflow (just run pytest)

**Implementation:**
- pytest plugin in `conftest.py`
- Validates against testing skill conventions
- Task 3.0 subtask 3.6

---

## PD-004: Process Decisions Are Portable

**Date:** 2025-12-20
**Scope:** Vertical engine builds

**Context:**
Process decisions made in one project should transfer to new vertical engine builds without being rediscovered.

**Decision:**
All cross-cutting process decisions live in `docs/PROCESS_DECISIONS.md` (this file) and travel with the codebase/skills.

**What goes here:**
- Dev workflow decisions
- Testing process decisions
- Task generation rules
- Skill enforcement patterns

**What does NOT go here:**
- Project-specific architecture (use project's DESIGN_DECISIONS.md)
- Feature decisions
- Technology choices for a specific component

**Rationale:**
- Single source of truth for process
- Portable across vertical builds
- Skills + this doc = complete process definition

---

## PD-005: The AI-Assisted Solopreneur Operating Model

**Date:** 2025-12-20
**Scope:** Foundational philosophy

**Context:**
Building vertical engines with AI sub-agents revealed a paradox: solopreneurs typically skip process (no one to enforce it), but AI-assisted solopreneurs NEED process (AI won't self-enforce).

**Decision:**
Adopt the **AI-Assisted Solopreneur Operating Model** as the foundational philosophy:

> "Process isn't overhead when your workers are AI. Process is the management layer that makes AI workers reliable."

**The Model:**

| Traditional Role | AI-Assisted Equivalent |
|------------------|------------------------|
| Job descriptions | Skills (documented conventions) |
| Performance management | Quality Gates (automated enforcement) |
| Training materials | Step definitions, references |
| Institutional memory | Decision docs (PD, DD) |
| HR policies | Process decisions |
| Quality assurance | Validators, gates |

**The Insight:**
You're not a solo developer. You're a **manager of digital workers** who need:
- Explicit rules (they can't infer intent)
- Enforcement (they won't self-police)
- Audit trails (they don't remember across sessions)

**Why This Isn't Over-Engineering:**
- Traditional solopreneur: "I'll just remember" → Works (human memory)
- AI-assisted solopreneur: "I'll just document" → Fails (AI skips docs)
- AI-assisted solopreneur: "I'll enforce with gates" → Works (can't bypass)

**The Minimum Viable Management Layer:**
```
Skills (what to do)
    ↓
Quality Gates (enforcement)
    ↓
Decision Docs (why we do it)
    ↓
Audit Steps (verify compliance)
```

This is the operating system for AI-assisted work.

**Rationale:**
- AI agents are powerful but unreliable without guardrails
- Documentation without enforcement = ignored
- Process IS the product when orchestrating AI
- Scales to multiple vertical engines

**Product Potential:**
This model could be packaged as a framework/product for other solopreneurs building with AI agents.

---

## Index

| PD | Title | Scope |
|----|-------|-------|
| PD-001 | Skills Require Quality Gates | All skills |
| PD-002 | Audit Subtask in Every Parent Task | Task generation |
| PD-003 | TestStructureValidator Runs Automatically | Testing process |
| PD-004 | Process Decisions Are Portable | Meta |
| PD-005 | AI-Assisted Solopreneur Operating Model | Foundational philosophy |
