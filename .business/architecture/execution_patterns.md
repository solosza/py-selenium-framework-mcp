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
