# Isagawa Execution Patterns

## Overview

Isagawa enforces execution through non-bypassable gates. The gate mechanism varies based on workflow topology.

---

## Pattern 1: Assembly Line (Sequential Pipeline)

**Used by:** QA Execution Engine (10-step workflow)

**Characteristics:**
- Steps are SEQUENTIAL and DEPENDENT
- Step N output is input to Step N+1
- Metadata flows through the pipeline
- Cannot parallelize

**Enforcement:** Gate between each step validates metadata contract.
**Skip a step?** Impossible. Next step has no input.

---

## Pattern 2: Inspection Team (Parallel Fan-Out/Fan-In)

**Used by:** Intel Scan (8-category competitive intelligence)

**Characteristics:**
- Categories are INDEPENDENT
- No dependencies between searches
- Can run in parallel
- Aggregation happens at the end

**Enforcement:** Aggregation gate requires all agents to complete.
**Skip an inspector?** Report wont generate. Missing input.

---

## The Isagawa Principle

**Infrastructure that teaches AI how to succeed.**

All Isagawa patterns share this core philosophy: the system doesn't just block incorrect execution - it guides AI to correct execution.

---

## Pattern 3: Self-Healing Gates (Cross-Cutting)

**Used by:** All Execution Engines

**Characteristics:**
- Gates detect missing or invalid data
- Gates PROVIDE the fix, not just report the error
- AI receives what it needs to retry successfully
- No guessing, no hallucination

**Two Layers:**

| Layer | Pattern |
|-------|---------|
| **Code Generation** (existing) | Tool generates skeleton → Gate detects → AI fills gaps → Gate validates ✅ |
| **Gate Orchestration** (NEW) | Gate detects missing data → Gate provides fix → AI retries → Gate passes ✅ |

**Example:**

```
Instead of:
  Gate: "You're missing scope_result. Go figure it out." ❌

We do:
  Gate: "You're missing scope_result. Here it is. Retry." ✅
```

**Implementation:**
```python
# Gate detects missing required data
if not input_data.get("scope_result"):
    # Gate PROVIDES the missing data instead of just failing
    scope_result = scope_discovery.analyze_workflow(url, ...)
    return {
        "status": "NEEDS_RETRY",
        "fix_applied": "scope_result",
        "scope_result": scope_result,  # <-- HERE'S YOUR DATA
        "message": "Missing scope_result. Provided. Retry with this."
    }
```

**Enforcement:** Smart infrastructure that helps, not just blocks.

---

## Pattern Selection Guide

| Workflow Shape | Pattern | Gate Location | Enforcement Mechanism |
|----------------|---------|---------------|----------------------|
| Sequential dependencies | Assembly Line | After each step | Metadata contract |
| Independent parallel | Inspection Team | After all agents | Aggregation requirement |

---

## Implementation Examples

### Assembly Line (QA Engine)
- Skills: 
- Gates: 
- Metadata flows via tool chain contracts

### Inspection Team (Intel Scan)
- Prompt spawns 8 parallel agents via Task tool
- Each agent returns structured category results
- Aggregation gate: all 8 must complete before report generation

---

*Both patterns are Isagawa. Both are non-bypassable. The topology dictates the pattern.*
