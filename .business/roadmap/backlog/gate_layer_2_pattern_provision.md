# Gate Layer 2: Pattern Provision

**Status:** Idea
**Created:** 2026-01-15
**Target Version:** v1.1 (Data Provision), v1.2 (Pattern Provision)
**Effort:** v1.1: 6-8 hours, v1.2: 15-20 hours
**Impact:** High (completes Protocols + Gates pattern)

---

## Context

The QA Execution Engine uses a "Protocols + Smart Gates" pattern where:
- **Protocols (Skills)** provide AI guidance on HOW to do work
- **Smart Gates** enforce rules and provide fix patterns

Currently, gates have 2 layers:
- **Layer 1:** Data provision (provide missing values/defaults)
- **Layer 2:** Pattern provision (detect skeleton → provide fill pattern)

Layer 1 is partially implemented. Layer 2 needs completion across Steps 6, 8, 9.

---

## Problem

**Current State:**

| Step | Component | Layer 1 | Layer 2 | Status |
|------|-----------|---------|---------|--------|
| 1 | Pre-flight | ❌ | N/A | ⚠️ Pending |
| 2 | User Input | ❌ | N/A | ⚠️ Pending |
| 3 | AI Processing | ❌ | N/A | ⚠️ Pending |
| 4 | Test Scenarios | ❌ | N/A | ⚠️ Pending |
| 5 | Element Discovery | ✅ | N/A | ✅ Complete |
| 6 | POM Generation | ❌ | ⚠️ | ⚠️ Partial |
| 7 | Task Generation | ✅ | ⚠️ | ✅ Complete |
| 8 | Role Generation | ❌ | ⚠️ | ⚠️ Partial |
| 9 | Test Generation | ✅ | ⚠️ | ✅ Complete |
| 10 | Save & Run | ❌ | N/A | ⚠️ Pending |
| 11 | Execution | N/A | N/A | ✅ Complete |

**What's Missing:**
- Layer 1 (data provision) for Steps 1-4, 6, 8, 10
- Layer 2 (pattern provision) enhancements for Steps 6, 8

---

## How Pattern Provision Works

**Flow Across Code-Generating Steps (6-9):**

```
┌─────────────┐
│   Tool 3-6  │  Generates skeleton code (structure only)
│  (MCP Tool) │  - Class structure + signatures
└──────┬──────┘  - Empty method bodies
       │
       ▼
┌─────────────┐
│  Smart Gate │  Detects skeleton in POST validation
│ (qg_* tool) │  - Checks for incomplete methods
└──────┬──────┘  - Returns NEEDS_RETRY with pattern_template
       │
       ▼
┌─────────────┐
│     AI      │  Fills implementation using pattern
│  (Claude)   │  - Reads protocol (.claude/skills/.../step-XX.md)
└──────┬──────┘  - Implements method bodies following examples
       │          - Uses gate's dynamic_data for context
       ▼
┌─────────────┐
│  Smart Gate │  Validates complete code
│ (qg_* tool) │  - Checks architecture rules
└──────┬──────┘  - PASS → File written to disk immediately
       │
       ▼
  File Saved
```

**Example (Step 6: POM Generation):**

1. **Tool generates skeleton:**
```python
class LoginPage:
    EMAIL = (By.CSS_SELECTOR, "#email")
    PASSWORD = (By.CSS_SELECTOR, "#passwd")

    def enter_email(self, text: str) -> "LoginPage":
        pass  # ← SKELETON DETECTED
```

2. **Gate detects skeleton (POST validation):**
- Detects `pass` statements in method bodies
- Returns `NEEDS_RETRY` with:
  - `pattern_template`: Complete POM pattern from step-06.md
  - `dynamic_data`: {page_name: "LoginPage", elements: [...]}

3. **AI fills implementation:**
```python
def enter_email(self, text: str) -> "LoginPage":
    self.web.type_text(*self.EMAIL, text)
    return self  # ← AI added implementation
```

4. **Gate validates complete code:**
- ✅ Atomic methods return `self`
- ✅ State-check methods exist
- ✅ No locators in method bodies
- ✅ PASS → File written

---

## Value

**Why This Pattern Works:**

1. **Tools Stay Simple**
   - Generate structure, not business logic
   - No need to understand site-specific details
   - Skeleton output is predictable and testable

2. **Gates Enforce Patterns**
   - Validate architecture rules at each step
   - Provide fix guidance on violations
   - Block bad code before it propagates

3. **Protocols Guide AI**
   - Step-specific patterns in `.claude/skills/qa-management-layer/references/`
   - Examples show correct implementation
   - AI has complete context to fill skeleton

4. **Dynamic Not Hardcoded**
   - Pattern templates use placeholders: `{page_name}`, `{element}`, `{locator}`
   - Works for ANY website (not site-specific)
   - Gates provide site-specific data in `dynamic_data`

5. **Consistent Architecture**
   - Same pattern across all 4 layers (POM → Task → Role → Test)
   - Predictable flow: skeleton → pattern → fill → validate
   - Easy to understand and debug

**Platform Impact:**
- **QA Vertical:** Completes skeleton detection → pattern provision flow
- **Consumer Vertical:** User rules → validation pattern provision
- **Agent Management:** Protocol deviation detection → corrective pattern
- **Enterprise:** Compliance rule violation → remediation pattern

---

## Implementation Plan

**v1.1 Goals (Quick Win):**
- Implement Layer 1 (data provision) for Steps 1-4, 6, 8, 10
- Effort: 6-8 hours

**v1.2 Goals (Complete Pattern):**
- Enhance Layer 2 (pattern provision) for Steps 6, 8
- Refactor Tools 3-6 to skeleton-only generation
- Update protocols with complete AI fill instructions
- Cross-site validation (same workflow, 3 different sites)
- Effort: 15-20 hours

**v2.0 Goals (AI Self-Heal):**
- AI self-heal integration (AI suggests code fixes using patterns)
- Learning memory (remember successful pattern applications)
- Confidence scoring (pattern match confidence)

---

## Next Steps

1. Move to `.business/roadmap/backlog/` when ready to implement
2. Create PRD breaking down Layer 1 and Layer 2 implementation
3. Start with v1.1 (data provision) for quick wins
4. Follow with v1.2 (pattern provision) for complete pattern
