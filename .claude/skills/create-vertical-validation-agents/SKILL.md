---
name: create-vertical-validation-agents
description: Template for creating AI agent validation systems for DaaS verticals. Use WHEN setting up validation agents for new verticals (QA, RAG, API, Sales Contracts). Triggers on "validation agent", "vertical validation", "DaaS agent".
---

# Skill: Create Vertical Validation Agents

**Version:** 1.4
**Purpose:** Template for creating AI agent validation systems for any DaaS vertical

---

## Overview

This skill provides a reusable pattern for creating AI agents that validate domain-specific enforcement layers before human users.

**Use when:** Setting up validation agents for a new vertical (QA, RAG, API, Sales Contracts, etc.)

---

## Visual Flow

### Validation Run Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VALIDATION RUN                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR AGENT (Claude Agent SDK)                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  system_prompt: "You are a [vertical] validation supervisor..."         ││
│  │  allowed_tools: [domain_expert_tool, reviewer_tool, Task, Read, Glob]   ││
│  │  mcp_servers: {validation: in-process, domain-tools: external}          ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
          │
          │ Step 1: Get domain input
          ▼
┌─────────────────────────────────────────┐
│  @tool("get_scenario")                  │
│  DOMAIN EXPERT (in-process)             │
│  ├── Input: complexity level            │
│  └── Output: domain-specific input      │
└─────────────────────────────────────────┘
          │
          │ Returns input for tool chain
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR invokes Task tool for complex work                               │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          │ Run domain tool chain
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Task tool → ORCHESTRATOR (Claude Code + Domain MCP)                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Runs domain-specific tool chain                                        ││
│  │  Generates domain artifacts                                             ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│  └── Output: Generated artifacts                                            │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          │ Returns generated artifacts
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR invokes Reviewer                                                 │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          │ Validate before execution
          ▼
┌─────────────────────────────────────────┐
│  @tool("validate_artifacts")            │
│  REVIEWER (in-process)                  │
│  ├── Input: artifact paths              │
│  ├── Reads: Domain reference docs       │
│  ├── Checks: Domain DDs                 │
│  └── Output: APPROVE / REJECT + details │
└─────────────────────────────────────────┘
          │
          ├── REJECT ──→ STOP, Report Failure
          │
          │ APPROVE
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR → Execute / Test artifacts                                       │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR generates validation report                                      │
│  └── Pass/Fail, violations, artifacts, logs                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLAUDE AGENT SDK                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐       │
│  │  Built-in Tools  │    │  Custom Tools    │    │  MCP Servers     │       │
│  ├──────────────────┤    ├──────────────────┤    ├──────────────────┤       │
│  │  Read            │    │  @tool decorator │    │  External (stdio)│       │
│  │  Write           │    │  In-process MCP  │    │  domain-tools    │       │
│  │  Edit            │    │  Python functions│    │                  │       │
│  │  Bash            │    │                  │    │  In-process      │       │
│  │  Glob            │    │  get_scenario    │    │  validation      │       │
│  │  Grep            │    │  validate_artif. │    │                  │       │
│  │  Task (subagent) │    │                  │    │                  │       │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘       │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Failure Handling

```
FAILURE TYPES
─────────────

TYPE 1: VALIDATION FAILURE (Reviewer rejects)
    Artifacts ──→ Reviewer ──→ DD Violation ──→ STOP IMMEDIATELY

TYPE 2: EXECUTION FAILURE - GOOD (Validates system works)
    Artifacts ──→ Reviewer ──→ APPROVE ──→ Execute ──→ Finds real issue
    └── SUCCESS for validation (system correctly identified problem)

TYPE 3: EXECUTION FAILURE - BAD (System issue)
    Artifacts ──→ Reviewer ──→ APPROVE ──→ Execute ──→ Fails due to bug
    └── STOP IMMEDIATELY, investigate system

TYPE 4: AGENT FAILURE (Crash)
    Any Agent ──→ Exception ──→ STOP IMMEDIATELY, fix agent
```

---

## Design Decisions (Cross-Vertical)

These DDs apply to ALL vertical validation agent systems.

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-VA-01 | Use Claude Agent SDK | Official SDK, built-in tools, MCP support |
| DD-VA-02 | Supervisor is main agent | SDK native pattern, simpler than multi-process |
| DD-VA-03 | Domain Expert as custom tool | Simple output, in-process, fast |
| DD-VA-04 | Reviewer as custom tool | Reads files, checks patterns, in-process |
| DD-VA-05 | Orchestrator via Task tool | Needs full Claude Code + MCP capabilities |
| DD-VA-06 | Stop immediately on failure | Fail fast, investigate, fix, restart |
| DD-VA-07 | Pre-defined scenarios in YAML | Reproducible, version controlled |
| DD-VA-08 | Full validation report | Audit trail, debugging support |
| DD-VA-09 | Human escalation for complex | Some scenarios need human guidance |
| DD-VA-10 | Execution finds issue = SUCCESS | Validates the system works correctly |
| DD-VA-11 | Agent tests live WITH agents | Separation of concerns from domain tests |
| DD-VA-12 | Raw test functions for @tool | Decorator returns SdkMcpTool, not callable |
| DD-VA-13 | Separate pytest config for agents | Avoid conflicts with domain test framework |
| DD-VA-14 | DD severity mapping | CRITICAL/HIGH block, MEDIUM/LOW don't |
| DD-VA-15 | Regex-based validation checks | File type detection + pattern matching |
| DD-VA-16 | Post-module review mandatory | Update skill/PRD after each agent module |
| DD-VA-17 | Dataclasses for structured reports | ScenarioResult, ValidationReport with typed fields |
| DD-VA-18 | Fail-fast with scenario skipping | Stop on failure, mark remaining as SKIPPED |
| DD-VA-19 | Report aggregation pattern | Violations by severity, timing, pass/fail counts |

### DD-VA-01: Use Claude Agent SDK

**Decision:** Use Claude Agent SDK (Python) for all agent implementation.

**Applies to:** All verticals

**Rationale:**
- Official Anthropic SDK
- Same capabilities as Claude Code
- Built-in tools (Read, Write, Bash, etc.)
- MCP server support (external and in-process)
- Subagent support via Task tool
- Hooks for validation/logging

**Installation:**
```bash
pip install claude-agent-sdk
```

**Requires:** Python 3.10+, ANTHROPIC_API_KEY

### DD-VA-02: Supervisor as Main Agent

**Decision:** Supervisor is the main SDK agent; Domain Expert and Reviewer are custom tools.

**Applies to:** All verticals

**Pattern:**
```python
from claude_agent_sdk import query, ClaudeAgentOptions, tool, create_sdk_mcp_server

@tool("get_scenario", "Get test scenario", {"level": str})
async def get_scenario(args):
    # Domain Expert logic
    return {"content": [{"type": "text", "text": scenario_json}]}

@tool("validate_artifacts", "Validate against DDs", {"paths": list})
async def validate_artifacts(args):
    # Reviewer logic
    return {"content": [{"type": "text", "text": result_json}]}

server = create_sdk_mcp_server(name="validation", version="1.0.0",
                                tools=[get_scenario, validate_artifacts])

async for message in query(
    prompt="Run validation for [scenario]",
    options=ClaudeAgentOptions(
        system_prompt="You are a [vertical] validation supervisor...",
        mcp_servers={"validation": server},
        allowed_tools=["mcp__validation__get_scenario",
                       "mcp__validation__validate_artifacts",
                       "Task", "Bash", "Read"]
    )
):
    process(message)
```

### DD-VA-06: Stop Immediately on Failure

**Decision:** Stop validation run immediately on any failure (Type 1, 3, or 4).

**Applies to:** All verticals

**Rationale:**
- Fail fast principle
- Earlier failures may cause cascading issues
- Human needs to investigate and fix

**Exception:** Type 2 (execution finds real issue) is SUCCESS, not failure.

### DD-VA-11: Agent Tests Live WITH Agents

**Decision:** Agent tests live in `agents/tests/`, not in domain test folder.

**Applies to:** All verticals

**Rationale:**
- Agents are separate concern from domain (e.g., QA framework)
- Agent tests don't need domain fixtures (Selenium, browser)
- Can run agent tests independently and fast
- Clear separation: `tests/` = domain, `agents/tests/` = agents

**Directory Structure:**
```
agents/
├── __init__.py
├── tools/
│   └── domain_expert.py
├── tests/                    # Agent tests live HERE
│   ├── __init__.py
│   ├── conftest.py           # Path setup, async fixtures
│   ├── pytest.ini            # Agent-specific config
│   └── test_domain_expert.py
└── prototypes/
```

### DD-VA-12: Raw Test Functions for @tool

**Decision:** Create `_test_<function>()` raw functions for testing decorated tools.

**Applies to:** All custom tools

**Rationale:**
- `@tool` decorator returns `SdkMcpTool` object, not callable function
- Raw function allows direct testing without MCP overhead
- Same logic, testable in isolation

**Pattern:**
```python
@tool("get_scenario", "Get test scenario", {"level": str})
async def get_scenario(args: Dict[str, Any]) -> Dict[str, Any]:
    return await _test_get_scenario(args)  # Delegate to raw

async def _test_get_scenario(args: Dict[str, Any]) -> Dict[str, Any]:
    """Raw implementation for testing."""
    level = args.get("level", "easy")
    # ... actual logic ...
    return result

# In tests:
result = await _test_get_scenario({"level": "easy"})
assert result["complexity"] == "easy"
```

### DD-VA-13: Separate Pytest Config for Agents

**Decision:** Agent tests have their own `pytest.ini` with agent-specific settings.

**Applies to:** All verticals

**Required Settings:**
```ini
[pytest]
# Async support
asyncio_mode = auto

# Agent test markers
markers =
    unit: Fast unit tests (no external dependencies)
    integration: Tests requiring external services

# Console output with coverage and HTML
addopts = -v --tb=short --cov=agents --cov-report=html:agents/tests/_reports/coverage --html=agents/tests/_reports/report.html --self-contained-html
```

**conftest.py Pattern:**
```python
import sys
from pathlib import Path

# Add project root to path for agents module imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
```

### DD-VA-14: DD Severity Mapping Pattern

**Decision:** Map all domain DDs to severity levels for consistent blocking logic.

**Applies to:** All verticals with domain rules/DDs

**Severity Levels:**
| Level | Meaning | Blocks Execution? |
|-------|---------|-------------------|
| CRITICAL | Must fix before any execution | Yes |
| HIGH | Should fix, significant issue | Yes |
| MEDIUM | Should fix, minor issue | No |
| LOW | Nice to fix, cosmetic | No |

**Pattern:**
```python
from enum import Enum

class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

DD_SEVERITY: Dict[str, Severity] = {
    "DD-03": Severity.CRITICAL,  # Locators only in POM
    "DD-15": Severity.CRITICAL,  # Assertions use POM
    "DD-09": Severity.HIGH,      # No return values
    # ... map all domain DDs
}

# Blocking logic
blocking_count = sum(1 for v in violations
                     if v.severity in [Severity.CRITICAL, Severity.HIGH])
status = "REJECT" if blocking_count > 0 else "APPROVE"
```

### DD-VA-15: Reviewer Validation Pattern

**Decision:** Use regex-based checks with file type detection for automated DD validation.

**Applies to:** All verticals with code artifacts

**File Type Detection:**
```python
def detect_file_type(file_path: str, content: str) -> str:
    """Detect file type from path patterns."""
    path_lower = file_path.lower().replace("\\", "/")

    if "/pages/" in path_lower: return "page"
    if "/tasks/" in path_lower: return "task"
    if "/roles/" in path_lower: return "role"
    if "/tests/" in path_lower: return "test"
    return "unknown"
```

**Validation Check Pattern:**
```python
def check_dd_XX(file_path: str, content: str, file_type: str) -> List[Violation]:
    """Check DD-XX: <description>."""
    violations = []

    # Only check relevant file types
    if file_type != "task":
        return violations

    lines = content.split("\n")
    for i, line in enumerate(lines, 1):
        # Skip comments/docstrings
        stripped = line.strip()
        if stripped.startswith("#") or stripped.startswith('"""'):
            continue

        # Regex pattern check
        if re.search(r"<bad_pattern>", line):
            violations.append(Violation(
                dd_id="DD-XX",
                severity=Severity.HIGH.value,
                file_path=file_path,
                line_number=i,
                description="<violation description>",
                code_snippet=stripped[:100]
            ))

    return violations
```

**Review Result Format:**
```python
@dataclass
class ReviewResult:
    status: str           # "APPROVE" or "REJECT"
    violations: List[Violation]
    summary: str          # Human-readable summary
    files_reviewed: List[str]
    blocking_violations: int
    total_violations: int
```

### DD-VA-17: Dataclasses for Structured Reports

**Decision:** Use Python dataclasses for all structured agent output.

**Applies to:** All agent tools returning complex data

**Rationale:**
- Type safety with typed fields
- Easy conversion to dict via `asdict()`
- Default values with `field(default_factory=list)`
- Clear documentation of expected fields

**Pattern:**
```python
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from enum import Enum

class ScenarioStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"

@dataclass
class ScenarioResult:
    """Result of a single scenario execution."""
    scenario_id: str
    scenario_name: str
    complexity: str
    status: ScenarioStatus

    # Timing
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None

    # Review result
    review_status: Optional[str] = None
    violations: List[Dict[str, Any]] = field(default_factory=list)
    blocking_violations: int = 0

    # Failure info
    failure_type: Optional[str] = None
    failure_message: Optional[str] = None

@dataclass
class ValidationReport:
    """Complete validation report for all scenarios."""
    report_id: str
    created_at: str
    overall_status: str = "PENDING"
    total_scenarios: int = 0
    scenarios_passed: int = 0
    scenarios_failed: int = 0
    scenarios_skipped: int = 0
    scenario_results: List[ScenarioResult] = field(default_factory=list)
    total_dd_violations: int = 0
    violations_by_severity: Dict[str, int] = field(default_factory=dict)

# Usage in tests
result = await _test_run_scenario("QA-EASY-001")
assert result["status"] == ScenarioStatus.PASSED.value
```

### DD-VA-18: Fail-Fast with Scenario Skipping

**Decision:** Stop validation on first failure, mark remaining scenarios as SKIPPED.

**Applies to:** Supervisor validation suite

**Rationale:**
- Earlier failures may cause cascading issues
- No point running more if first fails
- Human needs to fix before continuing
- Clear audit trail showing what was skipped

**Pattern:**
```python
async def _run_validation_suite(scenarios: List[str]) -> ValidationReport:
    report = ValidationReport(total_scenarios=len(scenarios))

    for scenario_id in scenarios:
        result = await _run_scenario(scenario_id)
        report.scenario_results.append(result)

        if result.status == ScenarioStatus.PASSED:
            report.scenarios_passed += 1
        elif result.status == ScenarioStatus.FAILED:
            report.scenarios_failed += 1

            # FAIL-FAST: Skip remaining scenarios
            remaining = scenarios[scenarios.index(scenario_id) + 1:]
            for skip_id in remaining:
                report.scenario_results.append(ScenarioResult(
                    scenario_id=skip_id,
                    scenario_name="...",
                    complexity="...",
                    status=ScenarioStatus.SKIPPED,
                    failure_message="Skipped due to previous failure"
                ))
                report.scenarios_skipped += 1
            break  # Exit loop after skipping

    return report
```

### DD-VA-19: Report Aggregation Pattern

**Decision:** Aggregate violations, timing, and counts into comprehensive report.

**Applies to:** Supervisor validation report

**Key Aggregations:**
- Violations by severity (CRITICAL: 2, HIGH: 1, etc.)
- Total duration across all scenarios
- Pass/fail/skip counts
- Human intervention count

**Pattern:**
```python
def _finalize_report(report: ValidationReport) -> None:
    # Aggregate violations by severity
    for result in report.scenario_results:
        for violation in result.violations:
            severity = violation.get("severity", "UNKNOWN")
            report.violations_by_severity[severity] = \
                report.violations_by_severity.get(severity, 0) + 1
        report.total_dd_violations += len(result.violations)

    # Calculate overall status
    if report.scenarios_failed == 0 and report.scenarios_passed == report.total_scenarios:
        report.overall_status = "PASSED"
    elif report.scenarios_failed > 0:
        report.overall_status = "FAILED"
    elif report.scenarios_passed > 0:
        report.overall_status = "PARTIAL"
    else:
        report.overall_status = "NO_RESULTS"
```

**Formatted Report Output:**
```
======================================================================
QA VALIDATION REPORT: VAL-20251216-235254
======================================================================

Status: FAILED
Created: 2025-12-16T23:52:54
Duration: 1.54s

--- SUMMARY ---
Total Scenarios: 3
  Passed:  1
  Failed:  1
  Skipped: 1

--- DD VIOLATIONS ---
Total: 2
  CRITICAL: 1
  HIGH: 1

--- SCENARIO RESULTS ---
[PASS] QA-EASY-001: Valid login with correct credentials
       Duration: 0.12s
[FAIL] QA-MID-001: Browse products by category
       Failure: TYPE_1_REVIEW_REJECT
       Message: Review REJECTED: 2 blocking violations found
       Blocking Violations: 2
[SKIP] QA-HARD-001: Add product to cart via quick view modal

======================================================================
END OF REPORT
======================================================================
```

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
| Claude Agent SDK (Python) | https://github.com/anthropics/claude-agent-sdk-python |
| Agent SDK Docs | https://platform.claude.com/docs/en/api/agent-sdk/overview |
| Building Agents Guide | https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk |
| Claude Code Hooks | `.claude/settings.json` |

---

## Checklist: New Vertical Setup

- [ ] Domain context defined
- [ ] Domain Expert Agent designed
  - [ ] **Post-module review**: Update skill with learnings, add visual flows to PRD
- [ ] Reviewer Agent designed
  - [ ] **Post-module review**: Update skill with learnings, add visual flows to PRD
- [ ] Supervisor Agent designed
  - [ ] **Post-module review**: Update skill with learnings, add visual flows to PRD
- [ ] Domain DDs documented
- [ ] Test scenarios defined (3+ per level)
- [ ] Integration tested
- [ ] Final documentation review

### Post-Module Review Questions (MANDATORY after each agent)

After completing each agent module, ask:
1. **Learnings**: Did we learn anything that should be added to the vertical agent skill?
2. **Documentation**: Is anything missing from the skill that we discovered during implementation?
3. **Visual Flows**: Do we need visual flows for this module in the PRD?
4. **New DDs**: Should we add any new Design Decisions (DD-VA-XX)?

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.4 | 2025-12-16 | Added DD-VA-17/18/19: Dataclasses, fail-fast, report aggregation (Supervisor) |
| 1.3 | 2025-12-16 | Added DD-VA-14/15/16: Severity mapping, validation patterns, post-module review |
| 1.2 | 2025-12-16 | Added DD-VA-11/12/13: Agent test organization, tool testing pattern |
| 1.1 | 2025-12-16 | Added visual flows, DDs, SDK code patterns |
| 1.0 | 2025-12 | Initial template based on QA vertical |

---

*This skill is maintained as part of the DaaS project.*
