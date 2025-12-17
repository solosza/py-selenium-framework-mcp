# PRD: QA Vertical Validation Agents

**Version:** 1.0
**Status:** Draft
**Created:** 2025-12-16

---

## 1. Introduction/Overview

### Problem Statement

The QA framework (py_sel_framework_mcp) with Claude Code + MCP tool integration is complete and ready to ship. Before exposing it to human users, we need to validate that the AI-orchestrated 9-step process produces production-ready code that follows all 22 Design Decisions.

### Solution

Build a dual-agent validation system that:
1. Simulates a real QA Engineer providing test requirements
2. Validates generated artifacts against all 22 DDs and FRAMEWORK.md patterns
3. Reports pass/fail with detailed violation logs

### What We're Validating

**System Under Test (SUT):** Claude Code + MCP tools + 9-step process

**Validation Goal:** SUT produces correct artifacts (code that follows 22 DDs and FRAMEWORK.md patterns)

**Important Distinction:**
- If generated test finds a bug in target app = SUCCESS (test works)
- If generated code violates DDs = FAILURE (SUT has problem)
- If test fails due to framework issues = FAILURE (SUT has problem)

---

## 2. Goals

| Goal | Measurable Outcome |
|------|-------------------|
| Validate tool chain correctness | 3/3 pre-defined scenarios pass validation |
| Ensure DD compliance | All 22 DDs checked, 0 violations in generated code |
| Prove production readiness | Full validation report with no critical failures |
| Enable future vertical expansion | Agents follow reusable template pattern |

---

## 3. User Stories

### Primary User: Developer (You)

```
As a developer shipping the QA framework,
I want AI agents to validate the tool chain before human users,
So that I can be confident the system produces correct, DD-compliant code.
```

### Agent Stories

```
As the SR QA Engineer agent,
I want to provide realistic test requirements at varying complexity levels,
So that the tool chain is tested against real-world scenarios.
```

```
As the Reviewer agent,
I want to validate generated code against FRAMEWORK.md patterns and all 22 DDs,
So that violations are caught before execution.
```

```
As the Supervisor agent,
I want to coordinate the validation workflow and aggregate results,
So that the developer gets a clear pass/fail report.
```

---

## 4. Functional Requirements

### FR-01: Supervisor Agent

| ID | Requirement |
|----|-------------|
| FR-01.1 | Supervisor SHALL load pre-defined test scenarios (3 total: easy, mid, hard) |
| FR-01.2 | Supervisor SHALL execute scenarios sequentially |
| FR-01.3 | Supervisor SHALL stop immediately on any failure (Type 1 or Type 3) |
| FR-01.4 | Supervisor SHALL coordinate handoffs: SR QA → Orchestrator → Reviewer → Execute |
| FR-01.5 | Supervisor SHALL generate full validation report on completion |
| FR-01.6 | Supervisor SHALL track pass/fail status per scenario |

### FR-02: SR QA Engineer Agent

| ID | Requirement |
|----|-------------|
| FR-02.1 | Agent SHALL generate Step 1 input (persona + requirement + URL) |
| FR-02.2 | Agent SHALL use automationpractice.pl as target application |
| FR-02.3 | Agent SHALL provide input at specified complexity level (easy/mid/hard) |
| FR-02.4 | Agent SHALL output format compatible with 9-step process Step 1 |

### FR-03: Reviewer Agent

| ID | Requirement |
|----|-------------|
| FR-03.1 | Agent SHALL compare generated artifacts (POM, Task, Role, Test) against FRAMEWORK.md Section 4 patterns |
| FR-03.2 | Agent SHALL validate against ALL 22 Design Decisions |
| FR-03.3 | Agent SHALL report APPROVE or REJECT with violation list |
| FR-03.4 | Agent SHALL categorize violations by severity (CRITICAL, HIGH, MEDIUM, LOW) |
| FR-03.5 | Agent SHALL block Step 9 execution if any CRITICAL/HIGH violations found |

### FR-04: Human Expert Integration

| ID | Requirement |
|----|-------------|
| FR-04.1 | System SHALL pause for human input on hard tests when Orchestrator stuck |
| FR-04.2 | System SHALL pause for human input on any DD-21/DD-22 situation |
| FR-04.3 | System SHALL log human guidance for audit trail |

### FR-05: Validation Report

| ID | Requirement |
|----|-------------|
| FR-05.1 | Report SHALL include pass/fail status per scenario |
| FR-05.2 | Report SHALL include all DD violations with file/line/description |
| FR-05.3 | Report SHALL include generated artifact paths |
| FR-05.4 | Report SHALL include execution logs (if Step 9 reached) |
| FR-05.5 | Report SHALL include timestamp and run duration |

---

## 5. Non-Goals (Out of Scope)

| Non-Goal | Rationale |
|----------|-----------|
| Multiple target applications | MVP uses automationpractice.pl only |
| Automated SDET Agent | Human steps in for hard tests (future enhancement) |
| Parallel scenario execution | Sequential execution for MVP (simpler debugging) |
| Self-healing on failures | Stop immediately, human investigates |
| CI/CD integration | Manual validation runs for MVP |

---

## 6. Design Considerations

### Agent Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR AGENT                                                            │
│  └── Loads scenarios, coordinates flow, generates report                    │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ├──→ SR QA Engineer Agent
          │    └── Provides Step 1 input (persona + requirement + URL)
          │
          ├──→ [Claude Code + MCP] (System Under Test)
          │    └── Runs Steps 2-8, generates artifacts
          │    └── On DD-21/DD-22: Pauses for human
          │
          ├──→ Reviewer Agent
          │    └── Compares artifacts against FRAMEWORK.md patterns
          │    └── Validates against 22 DDs
          │    └── APPROVE → Proceed to Step 9
          │    └── REJECT → Stop, report failure
          │
          └──→ [Human Expert] (You)
               └── Consulted for hard tests / DD-21/DD-22
```

### Workflow Sequence

```
1. Supervisor loads scenario (e.g., QA-EASY-001)
2. Supervisor → SR QA Engineer: "Generate input for easy test"
3. SR QA Engineer → Supervisor: Returns Step 1 input
4. Supervisor → Orchestrator: "Run Steps 2-8 with this input"
   └── [If DD-21/DD-22: Pause for human]
5. Orchestrator → Supervisor: Returns generated artifacts
6. Supervisor → Reviewer: "Validate against FRAMEWORK.md + 22 DDs"
7. Reviewer → Supervisor: APPROVE or REJECT
8. If APPROVE: Supervisor → Orchestrator: "Execute Step 9"
9. Supervisor: Records result
   └── If FAIL: Stop immediately, generate report
   └── If PASS: Continue to next scenario (or finish)
```

### Pre-Defined Scenarios

| ID | Complexity | Description |
|----|------------|-------------|
| QA-EASY-001 | Easy | Valid login with correct credentials |
| QA-MID-001 | Mid | Browse products by category |
| QA-HARD-001 | Hard | Add product to cart (dynamic modal) |

---

## 7. Technical Considerations

### Technology Stack

| Component | Technology |
|-----------|------------|
| Agent Framework | Claude Agent SDK (Python) - needs research |
| Orchestrator | Claude Code CLI or API |
| Target App | http://www.automationpractice.pl |
| Report Format | Markdown or JSON |

### Dependencies

- Claude Agent SDK (verify capabilities)
- Existing MCP tools (Tools 1-6)
- FRAMEWORK.md (22 DDs + Section 4 patterns)
- automationpractice.pl availability

### Open Technical Questions

1. How does Supervisor invoke Claude Code + MCP?
   - Option A: Agent with MCP tools (recreate capability)
   - Option B: Subprocess to Claude Code CLI
   - Option C: Anthropic API with tool calling

2. How do agents communicate?
   - Option A: File-based handoffs
   - Option B: In-memory (single process)
   - Option C: Message queue

---

## 8. Success Metrics

| Metric | Target |
|--------|--------|
| Scenarios passing | 3/3 (100%) |
| DD violations in generated code | 0 |
| Human interventions (easy/mid) | 0 |
| Human interventions (hard) | ≤2 |
| Validation run completes | Yes |

---

## 9. Test Strategy

### Unit Tests

| Component | Test Focus |
|-----------|------------|
| SR QA Engineer | Generates valid Step 1 input format |
| Reviewer | Correctly identifies DD violations |
| Supervisor | Coordinates workflow, stops on failure |

### Integration Tests

| Test | Description |
|------|-------------|
| End-to-end easy | Full flow with easy scenario |
| Reviewer rejection | Verify system stops on DD violation |
| Human escalation | Verify pause on DD-21/DD-22 |

### Acceptance Tests (Given/When/Then)

```gherkin
Scenario: Easy test passes validation
  Given a pre-defined easy scenario (QA-EASY-001)
  When Supervisor runs the validation workflow
  Then SR QA Engineer provides valid Step 1 input
  And Orchestrator generates artifacts without DD-21/DD-22 escalation
  And Reviewer approves all artifacts (0 DD violations)
  And Step 9 executes successfully
  And Supervisor reports PASS

Scenario: Reviewer catches DD violation
  Given generated code with a locator in Task layer (DD-03 violation)
  When Reviewer validates against FRAMEWORK.md patterns and 22 DDs
  Then Reviewer reports REJECT with violation details
  And Supervisor stops immediately
  And Final report shows failure with DD-03 violation

Scenario: Hard test requires human input
  Given a pre-defined hard scenario (QA-HARD-001)
  When Orchestrator encounters dynamic element discovery issue
  Then System pauses and requests human guidance (DD-21)
  And Human provides guidance
  And Orchestrator continues with guidance
  And Validation completes

Scenario: System under test produces bad locator
  Given Orchestrator generates code with invalid locator
  When Step 9 executes and test fails due to element not found
  Then Supervisor identifies this as Type 3 failure (framework issue)
  And Supervisor stops immediately
  And Report shows execution failure with details

Scenario: Generated test finds bug in target app
  Given Orchestrator generates correct code (0 DD violations)
  When Step 9 executes and test fails due to app bug
  Then Supervisor identifies this as Type 2 (test working correctly)
  And Supervisor logs as PASS for validation
  And Report notes "test correctly identified app defect"
```

---

## 10. Rollout Plan

### Phase 1: Build Agents
- Create SR QA Engineer agent
- Create Reviewer agent
- Create Supervisor agent

### Phase 2: Define Scenarios
- Create 3 pre-defined scenarios (easy, mid, hard)
- Document expected artifacts per scenario

### Phase 3: Integration
- Connect agents to Claude Code + MCP
- Test handoff flow

### Phase 4: Validation Run
- Execute full validation
- Fix any issues found
- Re-run until 3/3 pass

### Phase 5: Document & Ship
- Document validation results
- Update SESSION.md
- Proceed to human user testing

---

## 11. Open Questions

| # | Question | Status |
|---|----------|--------|
| 1 | Claude Agent SDK capabilities - can it invoke MCP tools? | Needs research |
| 2 | How to programmatically trigger Claude Code? | Needs research |
| 3 | Exact format for agent-to-agent handoffs? | Design during implementation |
| 4 | Where to store generated artifacts during validation? | Design during implementation |

---

## 12. References

| Document | Purpose |
|----------|---------|
| `FRAMEWORK.md` Section 4 | Code patterns for each layer |
| `FRAMEWORK.md` Section 8 | 9-step process, 22 DDs |
| `.claude/skills/create-vertical-validation-agents/SKILL.md` | Agent template |
| `.business/daas_business_project_v1.8.md` | Business context |

---

## Appendix: 22 Design Decisions (Quick Reference)

| ID | Decision | Severity |
|----|----------|----------|
| DD-01 | User must specify persona ("As a...") | HIGH |
| DD-02 | URL required upfront | HIGH |
| DD-03 | Locators ONLY in Page Objects | CRITICAL |
| DD-04 | Single documentation source | LOW |
| DD-05 | Method names emerge from tool chain | MEDIUM |
| DD-06 | AI extracts intent, not exact method names | MEDIUM |
| DD-07 | Domain from AI in Step 2 | MEDIUM |
| DD-08 | AI orchestrates, tools don't call tools | HIGH |
| DD-09 | Extract expected_states from BDD "Then" | HIGH |
| DD-10 | Action methods from element types | MEDIUM |
| DD-11 | State method naming: is_*/has_*/get_* | MEDIUM |
| DD-12 | Check existing before generating new | HIGH |
| DD-13 | Each tool has AI prompting rules | MEDIUM |
| DD-14 | One test file per scenario | LOW |
| DD-15 | Test assertions use POM state methods | CRITICAL |
| DD-16 | AI overrides Tool 6 file paths | MEDIUM |
| DD-17 | AI injects actual parameter values | HIGH |
| DD-18 | AI validates import paths | HIGH |
| DD-19 | Import from tools/, not utils/ | HIGH |
| DD-20 | Dynamic elements: AI prepares page state | MEDIUM |
| DD-21 | AI-SDET collaboration | MEDIUM |
| DD-22 | Stop-and-discuss on blockers | CRITICAL |

---

*PRD created as part of 4D Framework Phase 1*
