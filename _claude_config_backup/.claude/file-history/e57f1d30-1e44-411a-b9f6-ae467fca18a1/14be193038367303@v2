# Skill: Create Vertical Validation Agents

**Version:** 1.0
**Purpose:** Template for creating AI agent validation systems for any DaaS vertical

---

## Overview

This skill provides a reusable pattern for creating AI agents that validate domain-specific enforcement layers before human users.

**Use when:** Setting up validation agents for a new vertical (QA, RAG, API, Sales Contracts, etc.)

---

## Architecture Pattern

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR AGENT                                                            │
│  └── Coordinates validation workflow                                        │
│  └── Manages test scenarios (easy, mid, hard)                               │
│  └── Aggregates results into final report                                   │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ├──→ Domain Expert Agent (Step 1 - Input)
          │    └── Provides domain-specific input for tool chain
          │    └── Simulates target user persona
          │
          ├──→ [Orchestrator = Claude Code + Domain MCP Tools]
          │    └── Runs domain tool chain (Steps 2-8)
          │    └── Generates domain artifacts
          │    └── May escalate to human expert for complex scenarios
          │
          ├──→ Reviewer Agent (Review Gate - before execution)
          │    └── Validates generated artifacts against domain DDs
          │    └── Approves or rejects before execution step
          │
          └──→ [Human Expert] (complex scenarios only)
               └── Consulted when Orchestrator is stuck
               └── Provides domain guidance
```

---

## Agent Definitions

### 1. Supervisor Agent

**Role:** Orchestrates the entire validation workflow.

**Responsibilities:**
- Launch test scenarios at each complexity level
- Coordinate handoffs between agents
- Track pass/fail status
- Generate final validation report

**Inputs:**
- List of pre-defined test scenarios
- Target application/system info
- Complexity levels to run

**Outputs:**
- Validation report (pass/fail per scenario)
- Detailed logs
- Recommendations

---

### 2. Domain Expert Agent

**Role:** Simulates a real user providing input to the system.

**Responsibilities:**
- Generate realistic domain input
- Know the target application/system
- Provide input at specified complexity level

**Naming Convention:** `<Domain> + <Persona>`
- QA Vertical: SR QA Engineer
- RAG Vertical: RAG Developer
- API Vertical: API Designer
- Contract Vertical: Contract Writer

**Inputs:**
- Complexity level (easy, mid, hard)
- Target application info
- Domain context

**Outputs:**
- Domain-specific input for tool chain (Step 1)

---

### 3. Reviewer Agent

**Role:** Quality gate before execution step.

**Responsibilities:**
- Read all generated artifacts
- Validate against domain Design Decisions (DDs)
- Report violations or approve

**Naming Convention:** `<Domain> Reviewer`
- QA Vertical: QA Reviewer
- RAG Vertical: RAG Reviewer
- API Vertical: API Reviewer

**Inputs:**
- Generated artifacts from Orchestrator
- Domain DDs (checklist)

**Outputs:**
- APPROVE or REJECT with violation list

---

### 4. Orchestrator (Not Built - System Under Test)

**Role:** The actual Claude Code + MCP system being validated.

**Note:** This is NOT an agent we build. It's the product we're testing.

---

## Test Scenario Structure

### Complexity Levels

| Level | Characteristics | Human Expert Needed? |
|-------|-----------------|---------------------|
| **Easy** | Static elements, simple flow, no edge cases | No |
| **Mid** | Some dynamic elements, standard variations | Rarely |
| **Hard** | Dynamic content, edge cases, ambiguity | Often (DD-21/DD-22) |

### Scenario Template

```yaml
scenario:
  id: "<VERTICAL>-<LEVEL>-<NUMBER>"
  name: "<descriptive name>"
  complexity: "easy | mid | hard"

  input:
    persona: "<user type performing action>"
    requirement: "<natural language requirement>"
    target_url: "<application URL>"

  expected_artifacts:
    - "<artifact 1>"
    - "<artifact 2>"

  validation_points:
    - dd_id: "<DD-XX>"
      check: "<what to validate>"

  success_criteria:
    - "<criterion 1>"
    - "<criterion 2>"
```

---

## Good/Bad Examples

### Domain Expert Agent

**GOOD - Provides complete, realistic input:**
```
Persona: "As a registered user"
Requirement: "I want to login with my email and password so I can access my account"
URL: "http://automationpractice.pl/index.php?controller=authentication"
```

**BAD - Vague, incomplete input:**
```
Requirement: "login"
URL: (missing)
```

**WHY:** Domain Expert must simulate a real user. Real users provide context. Missing persona or URL breaks the tool chain at Step 1.

---

### Reviewer Agent

**GOOD - Specific DD validation:**
```
Checking DD-03: Locators ONLY in Page Objects

VIOLATION FOUND:
- File: tasks/auth_tasks.py
- Line 24: self.web.click(By.ID, "submit")
- Issue: Locator in Task layer (should be in POM)
- Severity: CRITICAL

RESULT: REJECT
```

**BAD - Generic approval:**
```
Code looks fine. APPROVE.
```

**WHY:** Reviewer must validate against specific DDs. Generic approval misses violations and defeats the purpose.

---

### Test Scenarios

**GOOD - Complete scenario definition:**
```yaml
scenario:
  id: "QA-EASY-001"
  name: "Valid login with correct credentials"
  complexity: "easy"

  input:
    persona: "registered user"
    requirement: "As a registered user, I want to login with valid credentials"
    target_url: "http://automationpractice.pl/index.php?controller=authentication"

  expected_artifacts:
    - "framework/pages/auth/login_page.py"
    - "framework/tasks/auth/auth_tasks.py (or existing)"
    - "framework/roles/registered_user.py (or existing)"
    - "tests/auth/test_valid_login.py"

  validation_points:
    - dd_id: "DD-03"
      check: "Locators only in POM"
    - dd_id: "DD-15"
      check: "Test assertions use POM state methods"

  success_criteria:
    - "All artifacts generated without errors"
    - "Test executes and passes"
    - "No DD violations"
```

**BAD - Incomplete scenario:**
```yaml
scenario:
  name: "login test"
  complexity: "easy"
```

**WHY:** Without complete definition, validation is subjective. Pre-defined scenarios need explicit expectations.

---

### Supervisor Coordination

**GOOD - Clear handoff sequence:**
```
1. Supervisor: "Starting QA-EASY-001"
2. Supervisor → Domain Expert: "Generate Step 1 input for easy login test"
3. Domain Expert → Supervisor: Returns input
4. Supervisor → Orchestrator: "Run Steps 2-8 with this input"
5. Orchestrator → Supervisor: Returns generated artifacts
6. Supervisor → Reviewer: "Validate these artifacts against QA DDs"
7. Reviewer → Supervisor: "APPROVE" or "REJECT + violations"
8. If APPROVE: Supervisor → Orchestrator: "Execute Step 9"
9. Supervisor: Records result, moves to next scenario
```

**BAD - No clear handoffs:**
```
Run all the agents and see what happens.
```

**WHY:** Without explicit coordination, agents may run out of order or miss steps.

---

## Creating a New Vertical

### Step 1: Define Domain Context

```markdown
## Vertical: [NAME]

**Domain:** [What area of expertise]
**Target Users:** [Who uses this]
**Enforcement Layer:** [What DDs/rules exist]
**Tool Chain:** [What MCP tools are used]
```

### Step 2: Create Domain Expert Agent

```markdown
## Domain Expert: [Name]

**Simulates:** [User persona]
**Knows:** [Target application/system]
**Provides:** [What input format]

**Complexity Variations:**
- Easy: [Description]
- Mid: [Description]
- Hard: [Description]
```

### Step 3: Create Reviewer Agent

```markdown
## Reviewer: [Name]

**Validates Against:** [List of DDs]
**Artifacts Checked:** [What gets reviewed]
**Approval Criteria:** [What must pass]
```

### Step 4: Define Test Scenarios

Create 3+ scenarios per complexity level (9+ total minimum).

### Step 5: Configure Supervisor

```markdown
## Supervisor Configuration

**Scenarios:** [Path to scenario definitions]
**Agents:** [Domain Expert, Reviewer]
**Report Format:** [What output looks like]
```

---

## References

### Design Decisions (Cross-Vertical)

| ID | Decision | Applies To |
|----|----------|------------|
| DD-21 | AI-Expert collaboration for complex scenarios | All verticals |
| DD-22 | Stop-and-discuss protocol on blockers | All verticals |

### Vertical-Specific References

| Vertical | DDs Location | Tool Chain Docs |
|----------|--------------|-----------------|
| QA (UI/E2E) | `FRAMEWORK.md` Section 8.11 | `FRAMEWORK.md` Section 8 |
| RAG | TBD | TBD |
| API | TBD | TBD |
| Contracts | TBD | TBD |

### Related Documents

| Document | Purpose |
|----------|---------|
| `.business/daas_business_project_v1.8.md` | Business context, vertical ideas |
| `FRAMEWORK.md` | QA vertical architecture (template) |
| `CLAUDE.md` | Quick reference, DD summary |

### Agent SDK References

| Resource | URL |
|----------|-----|
| Claude Agent SDK | TBD - research needed |
| Claude Code Hooks | `.claude/settings.json` |

---

## Checklist: New Vertical Setup

- [ ] Domain context defined
- [ ] Domain Expert Agent designed
- [ ] Reviewer Agent designed
- [ ] Domain DDs documented
- [ ] Test scenarios defined (3+ per level)
- [ ] Supervisor configuration complete
- [ ] Integration tested

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12 | Initial template based on QA vertical |

---

*This skill is maintained as part of the DaaS project.*
