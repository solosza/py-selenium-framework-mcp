# Smart Quality Gates

**Project:** smart-quality-gates
**Status:** PLANNING (Living Document - Pending 4D Framework)
**Created:** 2026-01-07
**Blocked By:** MVP v1.0 completion (DEF-045, DEF-046, smoke tests, E2E)

---

## Executive Summary

Enhance QA Execution Engine gates from "detect + hint" to "detect + provide fix data".

**Current State:** Gates validate well; Skills teach everything; AI gets text hints
**Target State:** Gates validate + provide structured fixes; Skills point only; AI gets actionable data

---

## The Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ SKILLS (Minimal)                                            │
│ - Light guidance: "what to do"                              │
│ - Points AI to correct step                                 │
│ - NOT heavy documentation                                   │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ GATES (Smart)                                               │
│ - Check: Is this correct?                                   │
│ - If NO: Provide example/fix → AI retries                   │
│ - If YES: Proceed                                           │
└─────────────────────────────────────────────────────────────┘
```

### The Shift

| OLD | NEW |
|-----|-----|
| Skills = heavy docs explaining everything | Skills = minimal pointers |
| Gates = detect + text hint | Gates = detect + structured fix data |
| AI memorizes rules | AI receives guidance at runtime |
| Documentation-heavy | Enforcement-heavy |

### Why This Works

- AI doesn't need to memorize rules
- Gates catch mistakes in real-time
- Gates provide the fix, not just the error
- Less documentation, more enforcement

---

## DD-50: Smart Gate Pattern

**Core Principle:** Infrastructure that teaches AI how to succeed.

```
Instead of:
  Gate: "You're missing scope_result. Go figure it out." ❌

We do:
  Gate: "You're missing scope_result. Here it is. Retry." ✅
```

### Two Layers of Self-Healing

| Layer | Pattern |
|-------|---------|
| **Code Generation** (existing) | Tool generates skeleton → Gate detects → AI fills gaps → Gate validates |
| **Gate Orchestration** (NEW) | Gate detects missing data → Gate provides fix → AI retries → Gate passes |

---

## Analysis Methodology

**Repeatable process for dissecting each step when implementing Smart Gates.**

### Step-by-Step Process

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ STEP DISSECTION PROCESS                                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  1. READ SKILL FILE                                                         │
│     └── .claude/skills/qa-guidance-layer/references/step-XX.md              │
│         • What rules does skill teach?                                      │
│         • What code examples are provided?                                  │
│         • What decision guidance exists?                                    │
│                                                                             │
│  2. READ GATE FILE                                                          │
│     └── mcp_server/tools/gates/qg_*.py                                      │
│         • What patterns does gate detect?                                   │
│         • What helper methods exist?                                        │
│         • What does fail_response return?                                   │
│                                                                             │
│  3. CREATE COMPARISON TABLE                                                 │
│     ┌──────────────────┬──────────────────┬─────────────────┐               │
│     │ What Skill       │ What Gate        │ Gap             │               │
│     │ Teaches          │ Checks           │                 │               │
│     ├──────────────────┼──────────────────┼─────────────────┤               │
│     │ Rule X           │ Pattern X        │ None            │               │
│     │ Rule Y           │ (not checked)    │ Could move      │               │
│     │ Philosophy Z     │ (not applicable) │ Stays in skill  │               │
│     └──────────────────┴──────────────────┴─────────────────┘               │
│                                                                             │
│  4. CALCULATE CONTENT DISTRIBUTION                                          │
│     • % already in gate (detected + enforced)                               │
│     • % could move to gate (rules → detection patterns)                     │
│     • % stays in skill (philosophy, rationale, "why")                       │
│                                                                             │
│  5. ASSESS IMPLEMENTATION APPROACH                                          │
│     • Does gate need new validation patterns? (add detection)               │
│     • Does gate need richer responses? (add suggested_context)              │
│     • Is new helper method needed? (extract to private method)              │
│     • Is new architecture needed? (rare - avoid over-engineering)           │
│                                                                             │
│  6. PRIORITIZE BY IMPACT                                                    │
│     • User friction: How often do users hit this failure?                   │
│     • AI retry success: Will structured fix data help?                      │
│     • Downstream effect: Does this step affect later steps?                 │
│     • Complexity: How much work to enhance?                                 │
│                                                                             │
│  7. DOCUMENT FINDINGS                                                       │
│     • "Currently in Gate" - what's already enforced                         │
│     • "Could Move to Gate" - rules that become detection                    │
│     • "Stays in Skill" - philosophy and architecture rationale              │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### File Mapping Reference

| Step | Skill File | Gate File |
|------|------------|-----------|
| 5 | `references/step-05.md` | `qg_discovered_elements.py` |
| 6 | `references/step-06.md` | `qg_page_object.py` |
| 7 | `references/step-07.md` | `qg_task.py` |
| 8 | `references/step-08.md` | `qg_role.py` |
| 9 | `references/step-09.md` | `qg_test_runner.py` |

### Classification Criteria

| Category | Criteria | Example |
|----------|----------|---------|
| **In Gate** | Detected via regex/pattern matching | Skeleton code detection |
| **Could Move** | Currently text instruction, could become detection | "Use is_* prefix" → regex check |
| **Stays in Skill** | Architectural rationale, "why" not "what" | "Why POMs use composition" |

### Key Questions Per Step

1. **What fails without this check?** → Priority indicator
2. **Can this be pattern-matched?** → Gate candidate
3. **Does AI need example code?** → Add to suggested_context
4. **Is this about "why" or "what"?** → Skill vs Gate decision
5. **Does downstream step depend on this?** → Priority boost

### Anti-Patterns to Avoid

| Anti-Pattern | Why Bad | Instead Do |
|--------------|---------|------------|
| Move everything to gate | Bloats gate code | Keep "why" in skill |
| Add new module layer | Over-engineering | Enhance existing helpers |
| Skip comparison step | Miss gaps | Always table comparison |
| Assume without reading | Wrong conclusions | Read actual code first |

---

## Current State Analysis

### Gate Strength Assessment

Gates are **already well-structured** with comprehensive validation:

| Gate | Lines | Helper Methods | Validation Coverage |
|------|-------|----------------|---------------------|
| qg_page_object.py | ~808 | 14+ | Skeleton, locators, DD-49, metadata, WebInterface |
| qg_task.py | ~463 | 8+ | Skeleton, locators, navigation, return values, decorator |
| qg_role.py | ~519 | 10+ | Skeleton, locators, POM imports, task calls, decorator |
| qg_test_runner.py | ~638 | 10+ | Skeleton, assertions, role calls, redundancy |

### Content Distribution by Step

| Step | In Gate Already | Could Move to Gate | Stays in Skill |
|------|-----------------|-------------------|----------------|
| 5 (Discovery) | 25% | 40% | 35% |
| 6 (POM) | 40% | 30% | 30% |
| 7 (Task) | 60% | 20% | 20% |
| 8 (Role) | 50% | 20% | 30% |
| 9 (Test) | 50% | 30% | 20% |
| **Average** | **45%** | **32%** | **23%** |

### The Real Gap: Response Richness

Gates detect problems well. They return text hints, not structured fix data:

**Current Response:**
```python
{
    "status": "fail",
    "error": "Skeleton code detected: pass statement",
    "fix_hint": "AI must complete the code. Remove placeholders..."  # TEXT ONLY
}
```

**Smart Response:**
```python
{
    "status": "fail",
    "error": "Skeleton code detected: pass statement",
    "fix_hint": "AI must complete the code...",
    "suggested_context": {
        "code_template": "def is_logged_in(self) -> bool:\n    return self.web.is_element_displayed(*self.LOGOUT_LINK)",
        "common_mistakes": [
            {"pattern": "return True", "fix": "return self.web.is_element_displayed(...)"}
        ],
        "decision_tree": {
            "if": "state method needed",
            "then": ["use is_* for boolean", "use get_* for values"]
        }
    }
}
```

---

## Detailed Gap Analysis by Step

### Step 5: Element Discovery

**Currently in Gate:**
- Multi-page scope auto-detection (self-healing scope_result)
- Two-pass discovery validation (input/output elements)
- Credential strategy validation

**Could Move to Gate:**
- DD-33 decision tree (Playwright vs Tool 2)
- RuntimeValidator code template
- Two-pass discovery workflow sequence
- Visual feedback initialization pattern

**Stays in Skill:**
- Architectural rationale for discovery approaches
- When to use dynamic vs static discovery

---

### Step 6: Page Object Generation

**Currently in Gate:**
- Skeleton code detection (4 patterns + trivial state methods)
- Layer violation detection (Task/Role imports)
- DD-49 navigate() enforcement
- Multi-page generation tracking
- WebInterface method validation

**Could Move to Gate:**
- POM pattern checklist (8 rules as structured list)
- Method naming guide (is_*/has_*/get_* patterns)
- Action method patterns per element_type
- State method code templates

**Stays in Skill:**
- Why POMs use composition not inheritance
- Architectural boundaries explanation

---

### Step 7: Task Generation

**Currently in Gate (60% - strongest):**
- Skeleton code detection
- Locator detection (11 patterns)
- Navigation detection (DD-49)
- Return value detection
- Decorator validation

**Could Move to Gate:**
- Task pattern checklist (10 rules)
- Common mistakes catalog (8 anti-patterns)
- Code template showing proper structure

**Stays in Skill:**
- Domain operation vs workflow explanation
- When to split into multiple tasks

---

### Step 8: Role Generation

**Currently in Gate:**
- Skeleton code detection
- Locator detection
- POM import detection
- POM direct call detection
- Task method call validation
- Decorator validation

**Could Move to Gate:**
- Role pattern checklist (11 rules)
- Code templates (single-task and multi-task)
- Common mistakes catalog (6 anti-patterns)

**Stays in Skill:**
- Role orchestration philosophy
- When multi-task vs single-task

---

### Step 9: Test Runner Generation

**Currently in Gate:**
- Skeleton code detection
- Role method call validation
- Task call detection (bypasses Role)
- POM action detection (bypasses Role+Task)
- POM state assertion validation
- Return value assertion detection
- Test redundancy detection (DEF-046)

**Could Move to Gate:**
- AAA pattern template (Arrange/Act/Assert)
- Placeholder detection ("category_name_value" patterns)
- File path guidance (tests/{workflow}/)
- Common mistakes catalog (5 anti-patterns)
- Assertion examples (correct vs incorrect)

**Stays in Skill:**
- Multi-persona workflow explanation
- Complex scenario guidance

---

## Implementation Priority

### Rank 1: Step 9 (Test Runner) - High Impact
- Currently: 50% in gate, 30% could move
- Add: AAA template, placeholder detection, assertion examples
- Why: Tests have highest user friction (wrong assertions, missing decorators)

### Rank 2: Step 5 (Discovery) - Medium-High Impact
- Currently: 25% in gate, 40% could move
- Add: RuntimeValidator pattern, two-pass workflow, decision tree
- Why: Multi-page complexity needs structured guidance

### Rank 3: Step 6 (POM) - Medium Impact
- Currently: 40% in gate, 30% could move
- Add: Pattern checklist, method naming guide
- Why: Foundation for all downstream steps

### Rank 4: Step 8 (Role) - Medium Impact
- Currently: 50% in gate, 20% could move
- Add: Architecture boundary validation, code templates
- Why: Prevents Role/Task/POM confusion

### Rank 5: Step 7 (Task) - Low Impact
- Currently: 60% in gate (strongest), 20% could move
- Add: Common mistakes catalog
- Why: Already well-covered by existing gate

---

## Proposed Gate Response Contract

All gates should return this enhanced structure on failure:

```python
{
    "status": "fail",
    "error": str,                    # What failed (existing)
    "fix_hint": str,                 # How to fix - text (existing)
    "suggested_context": {           # NEW: Structured fix data
        "code_template": str,        # Working example code
        "common_mistakes": [         # Anti-patterns with fixes
            {"pattern": str, "fix": str}
        ],
        "decision_tree": {           # If/then guidance
            "if": str,
            "then": [str]
        },
        "pattern_checklist": [str],  # Rules to follow
        "naming_guide": {            # Naming conventions
            "prefix": str,
            "examples": [str]
        }
    },
    "step": int,
    "attempt": int
}
```

---

## Architecture Decision: No Suggesters Needed

Initial proposal was to add separate Suggester modules. After analysis:

**Finding:** Gates are already well-modularized with helper methods. Adding suggesters would be over-engineering.

**Decision:** Enhance existing gate response structure, not architecture.

**Approach:**
1. Keep current gate validation logic (it's solid)
2. Enhance `fail_response()` to include `suggested_context`
3. Add helper methods in gates for generating fix data
4. No new module layer needed

---

## Scope Breakdown

### Phase 1: Response Contract Enhancement
- Define `suggested_context` schema
- Update `BaseGate.fail_response()` to support new fields
- Low risk, foundation for all steps

### Phase 2: Step 9 Enhancement (Highest Impact)
- Add AAA pattern template
- Add placeholder pattern detection
- Add assertion examples
- Add file path guidance

### Phase 3: Step 5 Enhancement
- Add RuntimeValidator code template
- Add two-pass workflow object
- Add DD-33 decision tree

### Phase 4: Steps 6, 8, 7 Enhancement
- Add pattern checklists
- Add common mistakes catalogs
- Add code templates

### Phase 5: Skill Reduction
- Trim skill files by ~50%
- Move code examples to gate responses
- Keep only architectural guidance in skills

---

## Implementation Strategy

### Branch Strategy
```
main (current MVP - finish first)
  ↓
feature/smart-quality-gates (this refactor)
  ↓
main (merge when validated)
```

### Prerequisites
- [ ] Complete DEF-045 (two-pass discovery)
- [ ] Complete DEF-046 (test redundancy)
- [ ] Smoke tests pass (2+ sites)
- [ ] E2E verification pass
- [ ] Tag v1.0

### Success Criteria
- Gates provide structured fix data on failure
- AI retry success rate increases
- Skill files reduced by 50%
- No increase in "BLOCKED" states

---

## Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-50 | Smart gate pattern | Infrastructure teaches AI to succeed |
| - | No separate Suggester modules | Gates already modular; avoid over-engineering |
| - | Enhance response structure | Simpler than new architecture layer |
| - | Step 9 first priority | Highest user friction, most benefit |

---

## Open Questions (For 4D Framework)

- [ ] Exact schema for `suggested_context` fields?
- [ ] How much code template detail is optimal?
- [ ] Should templates be static or generated from metadata?
- [ ] How to measure "AI retry success rate"?
- [ ] What's the testing strategy for smart gate responses?

---

## Related Documents

- `FRAMEWORK.md` Section 8.27 (DD-50: Smart Gate Pattern)
- `.business/architecture/execution_patterns.md` (Pattern 3: Smart Gates)
- `.business/strategy/isagawa_corp_thesis_v3.1.md` (The Smart Gate Principle)

---

## Next Steps

**This PRD is a living document.** When MVP v1.0 ships:

1. Start 4D Framework Phase 0 (Design Discussion)
2. Refine scope based on MVP learnings
3. Create detailed task breakdown in Phase 2
4. Execute in feature branch

---

## Revision History

| Date | Change |
|------|--------|
| 2026-01-07 | Initial PRD created from architecture audit session |
| 2026-01-07 | Updated with accurate skill/gate analysis after code review |
| 2026-01-07 | Removed Suggester pattern - gates already modular |
| 2026-01-07 | Added implementation priority based on gap analysis |
| 2026-01-07 | Added Analysis Methodology section - repeatable process for step dissection |

---

*This is a living document. Will be revisited with 4D Framework after MVP ships.*
