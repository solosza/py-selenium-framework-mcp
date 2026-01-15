# Project Context: Claude Code Skills Implementation

**Project:** py_sel_framework_mcp
**Status:** Planning
**Priority:** Low (non-urgent improvement)

---

## Background

Anthropic's recommended pattern is **"Build Skills, Not Agents"**:
- Skills = prompts/instructions packaged as files
- Auto-triggered based on context (no manual invocation)
- Token-efficient via progressive disclosure
- Team-shareable via git

## Current State

Workflow instructions live in:
- `CLAUDE.md` (~500 lines, loaded every conversation)
- `FRAMEWORK.md` Section 8 (9-step workflow)
- Design Decisions DD-01 through DD-22

**Problem:** All loaded upfront, every time, regardless of task.

## Goal

Restructure into official Skills format:
- Auto-trigger when user mentions tests, page objects, user stories
- Load detailed docs only when needed
- Cleaner separation of concerns

---

## Proposed Structure

```
.claude/skills/
└── qa-automation/
    ├── SKILL.md              # Core workflow (condensed)
    ├── architecture.md       # 4-layer framework patterns
    ├── design-decisions.md   # DD-01 through DD-22
    └── defect-handling.md    # Stop-and-discuss protocol (DD-22)
```

## SKILL.md Template

```yaml
---
name: qa-automation
description: Generate Selenium test automation code using 4-layer framework
  (Role→Task→Page→WebInterface). Use when user provides user stories, wants
  to generate tests, create page objects, or work with MCP qa-automation tools.
allowed-tools:
  - Read
  - Grep
  - Glob
  - Write
  - Edit
  - Bash
  - mcp__qa-automation__generate_tests_from_user_story
  - mcp__qa-automation__discover_page_elements
  - mcp__qa-automation__generate_page_object
  - mcp__qa-automation__generate_task
  - mcp__qa-automation__generate_role
  - mcp__qa-automation__generate_test_runner
  - mcp__qa-automation__run_test
  - mcp__qa-automation__analyze_failure
---

# QA Test Automation Framework

## Quick Start

9-step workflow for generating tests from user stories:

1. **User Input** - Persona ("As a...") + URL required
2. **AI Processing** - Extract role, domain, BDD, expected_states
3. **Tool 1** - generate_tests_from_user_story
4. **Tool 2** - discover_page_elements
5. **Tool 3** - generate_page_object
6. **Tool 4** - generate_task (check existing first)
7. **Tool 5** - generate_role (check existing first)
8. **Tool 6** - generate_test_runner
9. **Save & Run** - Save files, execute test

## Critical Rules

| ID | Rule |
|----|------|
| DD-01 | User MUST specify persona - ASK if missing |
| DD-02 | URL required upfront - ASK if missing |
| DD-12 | Check existing classes BEFORE generating new |
| DD-22 | On ANY blocker: STOP → REPORT → DISCUSS |

## No Hallucinations Policy

- NEVER guess method names - use metadata from previous tool
- NEVER assume a class exists - scan framework/ first
- If unsure, ASK the user

## References

- See [architecture.md](architecture.md) for 4-layer patterns
- See [design-decisions.md](design-decisions.md) for full DD reference
- See [defect-handling.md](defect-handling.md) for stop-and-discuss protocol
```

---

## Implementation Tasks

- [ ] 1. Create `.claude/skills/qa-automation/` directory
- [ ] 2. Create `SKILL.md` with condensed workflow
- [ ] 3. Extract architecture docs to `architecture.md`
- [ ] 4. Extract DD-01 through DD-22 to `design-decisions.md`
- [ ] 5. Extract DD-22 protocol to `defect-handling.md`
- [ ] 6. Slim down `CLAUDE.md` to project overview only
- [ ] 7. Test auto-triggering with sample prompts
- [ ] 8. Remove redundant content from FRAMEWORK.md

## CLAUDE.md After Migration

Keep only:
- Project overview
- Technology stack
- Development commands
- Git workflow
- Directory structure
- Communication filters (Truth and No BS, Reality Filter)

Remove:
- 9-step workflow (moves to Skill)
- Design Decisions (moves to Skill)
- 4-layer architecture details (moves to Skill)
- MCP tool usage section (moves to Skill)

---

## Benefits

| Before | After |
|--------|-------|
| ~500 lines loaded always | ~100 lines (SKILL.md description only) |
| Manual `/skill` invocation | Auto-triggers on keywords |
| Monolithic CLAUDE.md | Modular, focused files |
| All context upfront | Progressive disclosure |

## Estimated Effort

~1-2 hours to restructure existing content.

---

## Notes

- Skills are filesystem-based, check into git
- Team members get Skills automatically on `git pull`
- Future Claude Code features will build on Skills format
- Good portfolio talking point for interviews
