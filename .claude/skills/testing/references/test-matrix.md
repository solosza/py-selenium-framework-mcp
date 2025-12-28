<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Test Matrix Reference

Complete test coverage framework with types, categories, and templates.

---

## Test Types

| Type | Scope | When Required | Question Answered |
|------|-------|---------------|-------------------|
| **Unit** | Single function/class | Every function | "Does this function work?" |
| **Integration** | Components together | After each component | "Do components connect?" |
| **E2E** | Full system flow | Before release | "Does the system work?" |
| **Smoke** | Quick sanity check | After deploy | "Is it basically working?" |
| **Regression** | Old bugs stay fixed | After any fix | "Did we break anything?" |
| **Performance** | Speed, load, memory | When scale matters | "Is it fast enough?" |
| **Contract** | API boundaries | External interfaces | "Is the I/O shape correct?" |
| **Security** | Vulnerabilities, auth | User input, auth flows | "Is it secure?" |
| **Acceptance** | Business requirements | Before release | "Does it meet requirements?" |

---

## Test Categories

| Category | Purpose | Example |
|----------|---------|---------|
| **Happy** | Normal expected behavior | Valid input → correct output |
| **Negative** | Invalid input, errors | Bad input → appropriate error |
| **Edge** | Boundary conditions | Empty, max size, limits |
| **Concurrency** | Race conditions | Parallel execution safe |
| **State** | Transitions | Before/after state correct |

---

## Test Matrix Template

For each component, fill in applicable cells:

| Type | Happy | Negative | Edge | Concurrency | State | Priority | When |
|------|-------|----------|------|-------------|-------|----------|------|
| Unit | [ ] | [ ] | [ ] | [ ] | [ ] | P0 | commit |
| Integration | [ ] | [ ] | [ ] | [ ] | [ ] | P0 | commit |
| E2E | [ ] | [ ] | [ ] | - | [ ] | P1 | PR |
| Smoke | [ ] | - | - | - | - | P0 | deploy |
| Regression | [ ] | [ ] | [ ] | - | - | P1 | nightly |
| Performance | [ ] | - | [ ] | [ ] | - | P2 | release |
| Contract | [ ] | [ ] | - | - | - | P1 | PR |
| Security | - | [ ] | [ ] | - | - | P1 | PR |

**Legend:**
- `[ ]` = Applicable, needs test
- `[x]` = Test exists
- `-` = Not applicable

---

## Priority Definitions

| Priority | Meaning | Gate |
|----------|---------|------|
| **P0** | Must have | Cannot ship without |
| **P1** | Should have | Should not ship without |
| **P2** | Nice to have | Ship if time permits |

---

## Schedule Definitions

| Schedule | When | What Runs |
|----------|------|-----------|
| **commit** | Every local commit | Unit, Integration |
| **PR** | Pull request | Unit, Integration, E2E, Contract |
| **nightly** | Overnight | Full suite + Regression |
| **release** | Before deploy | Full suite + Performance + Security |
| **deploy** | After deploy | Smoke |

---

## Quality Gates

| Gate | Criteria | Tests Required |
|------|----------|----------------|
| **Function complete** | Unit tests pass | Unit (happy + negative + edge) |
| **Component complete** | Integration tests pass | Unit + Integration |
| **Feature complete** | E2E tests pass | Unit + Integration + E2E |
| **Release ready** | Full suite passes | All P0 + P1, no open defects |

---

## Process Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    TEST MATRIX PROCESS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. LIST                                                    │
│     └─ Review test types table                              │
│     └─ Ask: "Does this component need [type] tests?"        │
│                                                             │
│  2. CATEGORIZE                                              │
│     └─ For each applicable type                             │
│     └─ Ask: "What scenarios? happy | negative | edge | ..." │
│                                                             │
│  3. PRIORITIZE                                              │
│     └─ P0 = must have (blocks ship)                         │
│     └─ P1 = should have (risky to skip)                     │
│     └─ P2 = nice to have (time permitting)                  │
│                                                             │
│  4. SCHEDULE                                                │
│     └─ When should each test run?                           │
│     └─ commit | PR | nightly | release | deploy             │
│                                                             │
│  5. CREATE                                                  │
│     └─ Write tests                                          │
│     └─ Note prerequisites (fixtures, mocks, data)           │
│                                                             │
│  6. GATE                                                    │
│     └─ Define pass criteria                                 │
│     └─ Do not proceed until gate passes                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Example: Chunker Component

| Type | Happy | Negative | Edge | Priority | When |
|------|-------|----------|------|----------|------|
| Unit | [x] splits correctly | [x] invalid params | [x] empty, single char | P0 | commit |
| Integration | [x] loader→chunker | [ ] loader fails | [x] empty file | P0 | commit |
| E2E | [ ] full RAG pipeline | - | - | P1 | PR |
| Smoke | [ ] chunk sample doc | - | - | P0 | deploy |

**Checklist format:**
```
[x] unit|happy|test_chunk_splits_correctly
[x] unit|negative|test_invalid_overlap_raises_error
[x] unit|edge|test_empty_document
[x] integration|happy|test_loader_chunker_flow
```
