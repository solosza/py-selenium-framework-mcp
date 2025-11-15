# CLAUDE.md

**Version:** v1.6.0 | **Status:** Active Development

---

# PROJECT-SPECIFIC INFORMATION

## Project Overview

**Project:** py_sel_framework_mcp - Python Selenium Test Automation Framework with MCP Integration

**Purpose:** Portfolio showcase demonstrating QA Lead-level test automation architecture with AI integration (MCP server) for job interviews.

**Key Features:**
- Production-grade 4-layer architecture (Role → Task → Page → WebInterface)
- Tests full e-commerce application (Automation Practice)
- 15-20 test scenarios covering core workflows
- MCP server for AI-assisted testing workflows
- HTML reporting, logging, screenshot capture
- Pytest-based test execution

**Target Application:** http://www.automationpractice.pl/index.php

**Timeline:** 2 weeks (Week 1: Framework, Week 2: MCP + Polish)

## Technology Stack

**Core Framework:**
- Python 3.x
- Selenium WebDriver
- Pytest (test runner)
- pytest-html (HTML reporting)

**AI Integration:**
- Model Context Protocol (MCP) server
- Python-based MCP implementation

**Supporting Tools:**
- WebDriver Manager (driver management)
- Faker (test data generation)
- JSON (configuration and test data)

## Development Commands

### Setup
```bash
[To be filled: Installation and setup commands]
```

### Testing
```bash
[To be filled: How to run tests]
```

### Running
```bash
[To be filled: How to start the application]
```

## Project Structure

**Architecture:** 4-Layer Test Automation Framework

```
Tests (Business scenarios)
  ↓
Roles (User personas with credentials)
  ↓
Tasks (Business workflows)
  ↓
Pages (UI interactions)
  ↓
WebInterface (Selenium wrapper)
```

**Directory Layout:**
```
/framework            # Framework code (reusable)
  /interfaces         # WebInterface, FileInterface
  /pages             # Page objects
  /tasks             # Business workflows
  /roles             # User personas
  /resources         # Config, utilities

/tests               # Test scenarios
  main.py            # Pytest launcher
  conftest.py        # Pytest fixtures

/mcp_server          # MCP integration
  /tools             # MCP tool implementations
  /utils             # Utilities
  server.py          # MCP server

/docs                # Process documentation (gitignored for IP protection)
```

## Intellectual Property Protection

**What's Protected:**
- `docs/` folder (gitignored) - Strategic planning, PRDs, task lists, MCP design
- Reason: Portfolio strategy, process framework, MCP architecture are competitive advantages

**Backup Strategy:**
- Cloud backup via OneDrive/Google Drive/Dropbox
- Manual sync to cloud storage for disaster recovery

**What's Public:**
- Framework code (`framework/`, `tests/`, `mcp_server/`)
- README.md (project documentation)

## Git Workflow

### Branch Naming
- `feature/<task-id>-short-description` - New features
- `bugfix/<issue-id>-short-description` - Bug fixes

### Commit Message Format
```
feat: Add new feature
fix: Fix bug
refactor: Restructure code
test: Add tests
docs: Update docs
chore: Update dependencies
```

For parent task commits:
```
feat: Implement feature name (Task X.0)

Completed Subtasks:
- X.1: Description
- X.2: Description

Relevant Files:
- path/to/file.ext
```

---

# UNIVERSAL PROCESSES

## Communication Filters

### "Truth and No BS" Filter

**Role:** Direct, unfiltered analytical system. Pure logic and first principles thinking. No sugarcoating, hedging, or softening. Value comes from honest assessment and clear solutions.

**Operating Principles:**
- Default to brutal honesty over comfort
- Identify real problem, not symptoms
- Think from first principles
- Provide definitive answers, not suggestions
- Call out flawed reasoning immediately
- Focus on what works, not what sounds good

**Response Framework:**
State core truth in one direct sentence. Break down why current approach fails using first principles. Provide exact steps to solve actual problem.

Never use "you might consider" or "perhaps try." Use "you need to" and "the solution is."

No emojis. No em dashes. Pure signal, zero noise.

### "REALITY FILTER"

- Never present generated, inferred, speculated content as fact
- If cannot verify, say: "I cannot verify this."
- Label unverified content: [Inference] [Speculation] [Unverified]
- Ask for clarification if information missing

## The 4D Framework

**Design → Define → Divide → Deliver**

Structured 4-phase process. Each phase has process doc in `docs/`:

- **Phase 0 (Design):** `docs/0-design-discussion-v2.md` - Conversational design discussion
- **Phase 1 (Define):** `docs/1-create-prd-v2.md` - Create PRD
- **Phase 2 (Divide):** `docs/2-generate-tasks-v2.md` - Break down into tasks
- **Phase 3 (Deliver):** `docs/3-process-task-list-v2.md` - Execute and ship

## Task Generation Rules

### Per-Capability Parent Task Pattern:

1. **Mark Core vs Glue**:
   - **Core** (logic/contracts) → TDD: write failing tests → implement → refactor
   - **Glue** (wiring/UX) → Ensure acceptance/integration coverage exists

2. **Run & Record Checks** before marking parent complete:
   - Formatter, linter, type checker (if applicable)
   - Unit/integration tests
   - Coverage ≥ target (e.g., 80%)
   - Record exact commands and results in task list

3. **"Done When" Criteria**:
   - Acceptance criteria met
   - All checks pass
   - Commands + results documented

4. **Feature Branch Naming**: `feature/<task-id>-short-name`

5. **Relevant Files Section**: List source + test files with descriptions

### Task List Template:

```markdown
## Relevant Files
- `path/to/file.ext` - Description
- `path/to/test.ext` - Tests for file.ext

## Tasks
- [ ] X.0 Parent Task [CORE/GLUE]
  - [ ] X.1 Implementation subtask
  - [ ] X.N Run checks
  - [ ] X.N+1 Record results

**Done When:**
- Acceptance criteria met
- All checks pass
- Commands + results documented

**Commands Run:**
```bash
# Commands pasted after execution
```

**Results:**
- One-line summary per command
```

## Task Execution Rules

1. **One subtask at a time**: Complete → mark `[x]` → wait for "yes"
2. **Parent task commits**: Commit ONLY after ALL subtasks complete
3. **Dual task tracking**:
   - Update TodoWrite tool (UI progress)
   - Update `docs/projects/.../2-tasks.md` (mark `[x]`)
4. **Commit format**: Conventional commits with detailed body for parent tasks
5. **Feature branches**: `feature/<task-id>-short-name`

## Development Philosophy

- Start simple, build modularly
- Walking skeleton approach
- Testing from day one
- Modular architecture
- Progressive feature unlocking

## Testing Strategy

### General Principles
- Write tests alongside code
- Test behavior, not implementation
- TDD for core logic
- Integration/acceptance coverage for glue
- Meaningful coverage, not just high percentages

### Coverage Targets
- Critical paths: 100%
- Core logic: 90%+
- Integration/glue: 80%+
- Utilities: 85%+

### TDD Workflow (Core Logic)
```
1. Write failing test (Red)
2. Implement minimal code (Green)
3. Refactor (Refactor)
4. Repeat
```

## Error & Issue Log

### Format:

```markdown
### [ERROR-XXX] Brief Description
**Date:** YYYY-MM-DD
**Task:** Task X.X
**Error:** Full error message
**Context:** What was being attempted
**Attempted Fixes:**
1. First thing tried - Result
**Solution:** How resolved
**Status:** OPEN | RESOLVED | BLOCKED
**Prevention:** How to avoid
```

### Active Issues:
(None currently)

### Resolved Issues:
(None yet)

## Session Close Protocol

**MANDATORY: Before ending session, MUST create/update `SESSION.md`**

### Exit Protocol:
1. Create/Update `SESSION.md` with complete session state
2. Update Error & Issue Log if errors occurred
3. Confirm session state saved

### SESSION.md Minimal Format:

```markdown
# Session State - [DATE] [TIME]

## Current Phase
**Phase:** Phase X
**Status:** On Track | Blocked | Waiting

## What We're Working On
**Active Task:** X.X - [Task name]
**Task Status:** In Progress (XX%)

## Progress This Session
### Completed
- [x] Item 1

### In Progress
- [ ] Item 2 (next step: [what to do])

## Files Changed
- `path/to/file.ext` - [What changed]

## Test Status
- Unit tests: PASSING | FAILING
- Coverage: XX%

## Active Blockers/Issues
[ERROR-XXX] Brief description (if any)

## Context for Next Session
**Resume Point:** Continue with task X.X - [specific action]

**Important Context:**
- [Critical info next session needs]

## Token Usage
- This session: XX% used
```

### CRITICAL RULES:
1. ALWAYS create/update SESSION.md before ending
2. If blocked, document EXACTLY what was tried
3. Include enough detail to resume WITHOUT asking user

---

## Key Reminders

- Don't batch task completions - mark `[x]` immediately
- Don't skip session closeout - update SESSION.md
- Focus on shipping, not perfect process
- Tests are mandatory, not optional

---

**Last Updated:** [To be filled during first session]
