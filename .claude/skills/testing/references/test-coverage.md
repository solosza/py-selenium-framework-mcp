<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# Test Coverage Reference

Track what's covered vs not covered, identify gaps.

---

## Coverage Matrix Template

| Component | Unit | Integration | E2E | Lines % | Branches % | Gaps |
|-----------|------|-------------|-----|---------|------------|------|
| [name] | ✅/⬜ | ✅/⬜ | ✅/⬜ | XX% | XX% | [notes] |

**Legend:**
- ✅ = Covered
- ⬜ = Not covered
- 🔶 = Partial

---

## Coverage Targets

| Area | Target | Rationale |
|------|--------|-----------|
| Critical paths | 100% | No exceptions - these must work |
| Core logic | 90%+ | High confidence in business logic |
| Integration points | 80%+ | Key data flows verified |
| Glue/UI | 70%+ | Lower risk, harder to test |
| Utilities | 85%+ | Reused often, worth investing |

---

## Gap Analysis Template

| Gap | Risk | Priority | Action |
|-----|------|----------|--------|
| [what's missing] | High/Med/Low | P0/P1/P2 | [next step] |

---

## Coverage Report Command

```bash
pytest --cov={module} --cov-report=html --cov-report=term
```

Generates HTML report showing line-by-line coverage.

---

## TODO

- [ ] Add testing pyramid / shift-left decision matrix (nice to have)
  - When to push a test left (unit vs integration vs e2e)
  - Cost/speed tradeoffs
  - Decision criteria for test placement
