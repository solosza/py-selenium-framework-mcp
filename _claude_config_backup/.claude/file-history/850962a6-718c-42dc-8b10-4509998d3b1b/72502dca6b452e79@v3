# Test Plan Template

Comprehensive test plan template for any project. Copy to `docs/TEST_PLAN.md` and customize.

---

# [Project Name] Test Plan

**Version:** 1.0
**Status:** Living Document
**Last Updated:** [DATE]

---

## 1. Overview

### 1.1 Project Summary
[Brief description of what the project does]

### 1.2 Test Objectives
- Verify [functional requirement 1]
- Validate [functional requirement 2]
- Ensure [quality attribute - performance, security, etc.]

### 1.3 Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [DATE] | [NAME] | Initial version |

---

## 2. Scope

### 2.1 In Scope

| Component | Description | Priority |
|-----------|-------------|----------|
| [Component 1] | [What it does] | P0 |
| [Component 2] | [What it does] | P1 |

### 2.2 Out of Scope
- [Feature/area not being tested]
- [Reason why]

### 2.3 Assumptions
- [Assumption 1 - e.g., "Test data is available"]
- [Assumption 2 - e.g., "Environment is stable"]

### 2.4 Dependencies
- [Dependency 1 - e.g., "External API available"]
- [Dependency 2 - e.g., "Database seeded"]

---

## 3. Test Strategy

### 3.1 Test Pyramid (Domain-Specific)

Define test layers for your domain before writing tests:

```
┌─────────────────────────────────────────────────────┐
│                    TEST PYRAMID                     │
├─────────────────────────────────────────────────────┤
│  1. DATA STRUCTURE    - Does the class work?        │
│  2. CORE LOGIC        - Does the algorithm work?    │
│  3. BATCH OPERATIONS  - Does it scale to N inputs?  │
│  4. EDGE CASES        - Does it handle weird input? │
│  5. ERROR HANDLING    - Does it fail gracefully?    │
│  6. INTEGRATION       - Does it connect to next?    │
└─────────────────────────────────────────────────────┘
```

**Customize pyramid for your domain.** Examples:
- API: Request Parsing → Business Logic → Response → Auth → Error
- UI: Render → Interaction → State → Accessibility → Error

### 3.2 Test Levels

| Level | Scope | Owner | Tools |
|-------|-------|-------|-------|
| Unit | Individual functions | Dev | pytest |
| Integration | Component interactions | Dev/QA | pytest |
| System | End-to-end workflows | QA | pytest/Selenium |
| Acceptance | Business requirements | QA/User | Manual/Automated |

### 3.3 Test Categories

| Category | Purpose | Example |
|----------|---------|---------|
| Happy Path | Normal expected behavior | Valid input → correct output |
| Negative | Invalid input, error conditions | Bad input → graceful error |
| Edge Cases | Unusual but valid inputs | Empty, unicode, special chars |
| Boundary | At limits, exact boundaries | Min, max, exact size |
| Parametric | Multiple parameter combinations | Size × config matrix |

### 3.4 Approach by Component

| Component | Test Approach | Coverage Target |
|-----------|---------------|-----------------|
| [Component 1] | Unit + Integration | 90% |
| [Component 2] | Unit + E2E | 85% |

---

## 4. Test Environment

### 4.1 Hardware Requirements
- [CPU, RAM, Disk requirements]
- [Or: "Standard development machine"]

### 4.2 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Python | 3.11+ | Runtime |
| pytest | 7.x | Test runner |
| [Tool] | [Version] | [Purpose] |

### 4.3 Test Data
- Source: [Where test data comes from]
- Refresh: [How often, how to reset]
- Sensitive data: [How handled - masked, synthetic, etc.]

### 4.4 Environment Setup
```bash
# Commands to set up test environment
pip install -r requirements.txt
pytest --collect-only  # Verify tests discovered
```

---

## 5. Entry/Exit Criteria

### 5.1 Entry Criteria (Start Testing When)
- [ ] Code complete for component
- [ ] Unit tests written by developer
- [ ] Build passes
- [ ] Test environment available

### 5.2 Exit Criteria (Stop Testing When)
- [ ] All P0 test cases executed
- [ ] All P0/P1 defects resolved
- [ ] Test coverage >= [target]%
- [ ] No open blockers

### 5.3 Suspension Criteria (Pause Testing If)
- Critical environment issue
- Blocker defect found
- Major requirement change

---

## 6. Test Schedule

### 6.1 Milestones

| Milestone | Target Date | Criteria |
|-----------|-------------|----------|
| Unit tests complete | [DATE] | All components have unit tests |
| Integration tests | [DATE] | Component interactions verified |
| System test | [DATE] | E2E workflows pass |
| Release | [DATE] | All exit criteria met |

### 6.2 Test Execution Schedule

| Phase | Tests | Frequency |
|-------|-------|-----------|
| Development | Unit | On commit |
| PR Review | Unit + Integration | On PR |
| Nightly | Full regression | Daily |
| Release | Full + Performance | On release |

---

## 7. Resources

### 7.1 Team

| Role | Name | Responsibilities |
|------|------|------------------|
| QA Lead | [Name] | Test strategy, planning |
| QA Engineer | [Name] | Test execution, automation |
| Developer | [Name] | Unit tests, bug fixes |

### 7.2 Tools

| Tool | Purpose | Owner |
|------|---------|-------|
| pytest | Test execution | QA |
| pytest-html | Reporting | QA |
| GitHub | Version control | All |

---

## 8. Risk Analysis

### 8.1 Risks

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R1 | [Risk description] | High/Med/Low | High/Med/Low | [Mitigation strategy] |
| R2 | Test data unavailable | Medium | High | Use synthetic data |
| R3 | Environment instability | Low | High | Backup environment |

### 8.2 Contingency
- If [risk occurs], then [action]

---

## 9. Test Matrix

### 9.1 Component Status

| Component | Status | Unit | Integration | E2E | Coverage |
|-----------|--------|------|-------------|-----|----------|
| [Component 1] | Done | 15 | 2 | 1 | 95% |
| [Component 2] | In Progress | 10 | - | - | 80% |
| [Component 3] | Not Started | - | - | - | - |

### 9.2 Test Categories per Component

| Component | Happy Path | Negative | Edge | Boundary |
|-----------|------------|----------|------|----------|
| [Component 1] | 5 | 4 | 3 | 3 |
| [Component 2] | 4 | 3 | 2 | 1 |

### 9.3 Priority Matrix

| Priority | Definition | Response |
|----------|------------|----------|
| P0 | Must have, blocks release | Fix immediately |
| P1 | Should have, impacts quality | Fix before release |
| P2 | Nice to have | Fix if time permits |

---

## 10. Test Cases

### 10.1 Test File Locations

| Component | Test File | Count |
|-----------|-----------|-------|
| [Component 1] | `tests/test_component1.py` | 15 |
| [Component 2] | `tests/test_component2.py` | 10 |

---

### 10.2 [Component 1] Coverage

Organize tests by functional area within each component:

#### 1. [Functional Area - e.g., Data Structure]

| Type | Test | Status |
|------|------|--------|
| Happy | [description] | Done |
| Happy | [description] | Done |
| Negative | [description] | Missing |
| Edge | [description] | Done |

#### 2. [Functional Area - e.g., Core Logic]

| Type | Test | Status |
|------|------|--------|
| Happy | [description] | Done |
| Negative | [description] | Done |
| Edge | [description] | Missing |
| Boundary | [description] | Done |

#### 3. [Functional Area - e.g., Batch Operations]

| Type | Test | Status |
|------|------|--------|
| Happy | [description] | Done |
| Negative | [description] | Missing |
| Edge | [description] | Done |

#### 4. [Functional Area - e.g., Integration]

| Type | Test | Status |
|------|------|--------|
| Happy | [description] | Done |
| Edge | [description] | Done |

---

### 10.3 Test Categories Reference

| Category | Definition | Example |
|----------|------------|---------|
| Happy | Normal expected behavior | Valid input → correct output |
| Negative | Invalid input, error conditions | Bad input → graceful error |
| Edge | Unusual but valid inputs | Empty, unicode, single char |
| Boundary | At exact limits | Min size, max size, exact boundary |
| Parametric | Multiple combinations | Config A × Config B matrix |
| Integration | Components together | Component1 → Component2 pipeline |

**Status values:** Done | Missing | Failing

---

## 11. Defect Management

### 11.1 Severity Definitions

| Severity | Definition | Example |
|----------|------------|---------|
| Critical | System unusable | Crash, data loss |
| High | Major feature broken | Cannot complete workflow |
| Medium | Feature impaired | Workaround exists |
| Low | Minor issue | Cosmetic, typo |

### 11.2 Defect Lifecycle

```
NEW → ASSIGNED → IN PROGRESS → FIXED → VERIFIED → CLOSED
                     ↓
                  REOPENED
```

### 11.3 Active Defects

| ID | Severity | Component | Description | Status |
|----|----------|-----------|-------------|--------|
| DEF-001 | Medium | [Component] | [Description] | Open |

See `docs/DEFECT_LOG.md` for full defect details.

---

## 12. Metrics & Reporting

### 12.1 Key Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Code coverage | 85% | [X]% |
| Pass rate | 100% | [X]% |
| Open defects | 0 Critical | [X] |

### 12.2 Code Coverage by File

| File | Stmts | Miss | Cover | Missing Lines |
|------|-------|------|-------|---------------|
| [module1.py] | [X] | [X] | [X]% | [lines] |
| [module2.py] | [X] | [X] | [X]% | [lines] |
| **TOTAL** | [X] | [X] | **[X]%** | |

**Coverage targets:**
- Core logic: 90%+
- Integration: 85%+
- Utilities: 80%+

### 12.3 Reports

| Report | Location | Generated By |
|--------|----------|--------------|
| Test results | `_reports/report.html` | pytest-html |
| Coverage HTML | `_reports/coverage/index.html` | pytest-cov |
| Coverage terminal | Console output | pytest-cov |

### 12.4 Test Commands

```bash
# Run all tests with HTML report
pytest tests/ -v --html=_reports/report.html --self-contained-html

# Run with coverage (terminal)
pytest --cov=[package] --cov-report=term-missing tests/

# Run with coverage (HTML report)
pytest --cov=[package] --cov-report=html:_reports/coverage tests/

# Run with both reports
pytest --cov=[package] --cov-report=term --cov-report=html:_reports/coverage --html=_reports/report.html tests/
pytest tests/ --cov=src --cov-report=html

# Run specific component
pytest tests/test_[component].py -v
```

---

## 13. Lessons Learned

### 13.1 By Component

**[Component 1]:**
- [Key insight 1]
- [Key insight 2]

**[Component 2]:**
- [Key insight 1]

### 13.2 Process Improvements
- [Improvement identified during testing]

---

## Appendix

### A. Glossary

| Term | Definition |
|------|------------|
| [Term] | [Definition] |

### B. References
- [Link to requirements doc]
- [Link to architecture doc]
- [Link to related test plans]

---

*Living document - updated after each component/sprint*
