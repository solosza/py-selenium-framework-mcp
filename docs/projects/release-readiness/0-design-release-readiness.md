# Design Discussion: Release Readiness

**Version:** 1.0
**Created:** 2025-12-27
**Status:** In Progress (Phase 0 - Design)

---

## Purpose

Collaborative design discussion to close gaps before public release. We will go through each topic together.

---

## Topics to Design

| # | Topic | Status |
|---|-------|--------|
| 1 | MCP Code Generation Tools Off/On Flag | Pending |
| 2 | Audit Trail Improvements | Pending |
| 3 | Hard Cap Self-Heal Loop | Pending |
| 4 | Deterministic Artifact Layout | Pending |
| 5 | Adversarial Inputs Test Suite | Pending |
| 6 | Gate Drift Prevention | Pending |
| 7 | Smoke-Test Matrix | Pending |
| 8 | Packaging + Install Story | Pending |
| 9 | One-Page Positioning | Pending |

---

# Topic 1: MCP Code Generation Tools Off/On Flag

## Context

**Current Flow (Tools ON):**
```
Step 6: qg_page_object PRE → Tool 3 generates POM → qg_page_object POST
Step 7: qg_task PRE → Tool 4 generates Task → qg_task POST
Step 8: qg_role PRE → Tool 5 generates Role → qg_role POST
Step 9: qg_test_runner PRE → Tool 6 generates Test → qg_test_runner POST
```

**Problem:** Tools 3-6 sometimes generate skeleton code. AI self-heals anyway.

**User Insight:** If AI can generate correct code using skill patterns, why invoke tools at all?

## Proposed Flow (Tools OFF)

```
Step 6: qg_page_object PRE → AI generates POM → qg_page_object POST
Step 7: qg_task PRE → AI generates Task → qg_task POST
Step 8: qg_role PRE → AI generates Role → qg_role POST
Step 9: qg_test_runner PRE → AI generates Test → qg_test_runner POST
```

## Design Questions

1. Where does the flag live?
   - [ ] a) Workflow state (`tools_enabled: false`)
   - [ ] b) Environment variable
   - [ ] c) Skill configuration
   - [ ] d) Other: ___

2. When is the flag set?
   - [ ] a) Step 1 pre-flight (user chooses)
   - [ ] b) Project-level config (once per project)
   - [ ] c) Per-run CLI argument
   - [ ] d) Other: ___

3. What changes when tools OFF?
   - [ ] a) Skills instruct AI to generate directly
   - [ ] b) Gates skip tool invocation check
   - [ ] c) Both
   - [ ] d) Other: ___

## Decision

*(To be filled after discussion)*

---

# Topic 2: Audit Trail Improvements

## Current State

| Artifact | What It Tracks | Gap |
|----------|----------------|-----|
| SESSION.md | Session progress, files changed | Manual, not per-run |
| DEFECT_LOG.md | Defects found/fixed | Manual entry |
| workflow_state.json | Step data per run | No gate pass/fail history |
| Gate responses | pass/fail + error | Not persisted |

## Design Questions

1. What should the audit trail capture per run?
   - [ ] a) Gates called (which, when, pass/fail)
   - [ ] b) Tools called (which, input, output)
   - [ ] c) Files generated (path, hash)
   - [ ] d) Errors encountered
   - [ ] e) Retries attempted
   - [ ] f) All of the above
   - [ ] g) Other: ___

2. Where should the audit trail live?
   - [ ] a) Extended workflow_state.json
   - [ ] b) Separate audit_log.json per run
   - [ ] c) Append-only log file
   - [ ] d) Other: ___

3. What format?
   - [ ] a) JSON (machine-readable)
   - [ ] b) Markdown (human-readable)
   - [ ] c) Both (JSON + generated MD report)
   - [ ] d) Other: ___

4. Should audit trail be required or optional?
   - [ ] a) Always on (enforcement)
   - [ ] b) Opt-in via flag
   - [ ] c) Other: ___

## Decision

*(To be filled after discussion)*

---

# Topic 3: Hard Cap Self-Heal Loop

## Current State

- Skill documents max 3 retries
- No code enforcement
- AI could loop indefinitely

## Design Questions

1. Where should retry count be tracked?
   - [ ] a) Gate state (per step)
   - [ ] b) Workflow state (global)
   - [ ] c) Both
   - [ ] d) Other: ___

2. What happens after max retries?
   - [ ] a) Gate returns "blocked" status
   - [ ] b) Produce blocked report with details
   - [ ] c) Force user decision (DD-22)
   - [ ] d) All of the above
   - [ ] e) Other: ___

3. Is max retries configurable?
   - [ ] a) Hardcoded (3)
   - [ ] b) Configurable per project
   - [ ] c) Configurable per step
   - [ ] d) Other: ___

## Decision

*(To be filled after discussion)*

---

# Topic 4: Deterministic Artifact Layout

## Current State

- Folder structure is convention (`tests/cart/`, `framework/pages/`)
- Not enforced by gates
- AI might save files anywhere

## Design Questions

1. Should path validation happen in qg_save_run?
   - [ ] a) Yes, reject non-compliant paths
   - [ ] b) Yes, warn but allow
   - [ ] c) No, trust AI
   - [ ] d) Other: ___

2. What paths are valid?
   - [ ] a) Strict: `tests/{workflow}/test_*.py`, `framework/pages/{domain}/*.py`
   - [ ] b) Pattern-based: configurable regex
   - [ ] c) Directory whitelist
   - [ ] d) Other: ___

3. Who defines valid paths?
   - [ ] a) Hardcoded in gate
   - [ ] b) Skill configuration
   - [ ] c) Project-level config
   - [ ] d) Other: ___

## Decision

*(To be filled after discussion)*

---

# Topic 5: Adversarial Inputs Test Suite

## Current State

- No tests for edge cases
- Only happy path validated

## Test Categories Needed

| Category | Example |
|----------|---------|
| Ambiguous requirements | "register user" (no details) |
| Contradictory requirements | "login without credentials" |
| Multi-step in one prompt | "login, browse, checkout" |
| Missing selectors | Dynamic UI, shadow DOM |
| Malformed user stories | No Given/When/Then |

## Design Questions

1. Where should adversarial tests live?
   - [ ] a) `mcp_server/_dev_tests/test_adversarial/`
   - [ ] b) Separate repo (adversarial test pack)
   - [ ] c) Other: ___

2. What should tests validate?
   - [ ] a) Gates block bad input
   - [ ] b) AI handles gracefully (asks for clarification)
   - [ ] c) Error messages are helpful
   - [ ] d) All of the above
   - [ ] e) Other: ___

3. How many test cases minimum?
   - [ ] a) 5 per category
   - [ ] b) 10 total
   - [ ] c) 20 total
   - [ ] d) Other: ___

## Decision

*(To be filled after discussion)*

---

# Topic 6: Gate Drift Prevention

## Current State

- No visibility into which gates ran per workflow
- If workflow stops mid-way, no record of what was enforced

## Design Questions

1. What should gate coverage summary include?
   - [ ] a) Gates called: qg_preflight ✓, qg_user_input ✓, ...
   - [ ] b) Gates skipped/not reached
   - [ ] c) Pass/fail per gate
   - [ ] d) All of the above
   - [ ] e) Other: ___

2. When should summary be generated?
   - [ ] a) After each gate call
   - [ ] b) At workflow end
   - [ ] c) On demand
   - [ ] d) Other: ___

3. Should missing gates be a warning or error?
   - [ ] a) Warning (log but continue)
   - [ ] b) Error (block final save)
   - [ ] c) Configurable
   - [ ] d) Other: ___

## Decision

*(To be filled after discussion)*

---

# Topic 7: Smoke-Test Matrix

## Current State

- Only tested: automationpractice.pl + Chrome
- Unknown: Other apps, browsers, UI frameworks

## Design Questions

1. Which additional web apps?
   - [ ] a) saucedemo.com (simpler)
   - [ ] b) demoqa.com (more complex)
   - [ ] c) User-provided app
   - [ ] d) Other: ___

2. Which browsers?
   - [ ] a) Chrome + Firefox
   - [ ] b) Chrome + Firefox + Edge
   - [ ] c) Just Chrome (MVP)
   - [ ] d) Other: ___

3. UI framework coverage?
   - [ ] a) Basic HTML only (MVP)
   - [ ] b) Basic HTML + one React app
   - [ ] c) Not needed for MVP
   - [ ] d) Other: ___

4. What constitutes "passing"?
   - [ ] a) E2E workflow completes
   - [ ] b) All gates pass
   - [ ] c) Generated test runs successfully
   - [ ] d) All of the above
   - [ ] e) Other: ___

## Decision

*(To be filled after discussion)*

---

# Topic 8: Packaging + Install Story

## Current State

- pip install works for dependencies
- Skills require manual copy to `.claude/skills/`
- No one-command setup

## Design Questions

1. Target install experience?
   - [ ] a) `pip install isagawa-qa && isagawa init`
   - [ ] b) `npx create-isagawa-project`
   - [ ] c) Docker: `docker run isagawa/qa`
   - [ ] d) Other: ___

2. What should `init` do?
   - [ ] a) Copy skills to project
   - [ ] b) Create config files
   - [ ] c) Verify dependencies
   - [ ] d) All of the above
   - [ ] e) Other: ___

3. Priority for MVP?
   - [ ] a) Just document manual steps clearly
   - [ ] b) Basic CLI tool
   - [ ] c) Full pip package
   - [ ] d) Other: ___

## Decision

*(To be filled after discussion)*

---

# Topic 9: One-Page Positioning

## Current State

- No clear "what it is / what it isn't" doc
- Risk: labeled as "another agent" or "test generator"

## Core Message

> "You are the AI Management Layer. Everything else is implementation detail."

## Design Questions

1. Primary audience?
   - [ ] a) Technical decision makers (CTOs, VPs Eng)
   - [ ] b) Developers/QA engineers
   - [ ] c) Both (different sections)
   - [ ] d) Other: ___

2. Key differentiators to highlight?
   - [ ] a) Enforcement, not generation
   - [ ] b) Gates are non-bypassable
   - [ ] c) Audit trail built-in
   - [ ] d) Platform approach (packs on top)
   - [ ] e) All of the above
   - [ ] f) Other: ___

3. What it ISN'T (to explicitly state)?
   - [ ] a) Not an AI agent
   - [ ] b) Not a test generator
   - [ ] c) Not an automation framework
   - [ ] d) All of the above
   - [ ] e) Other: ___

4. Format?
   - [ ] a) One-page PDF
   - [ ] b) README section
   - [ ] c) Landing page copy
   - [ ] d) Other: ___

## Decision

*(To be filled after discussion)*

---

# Summary of Decisions

| Topic | Decision | Status |
|-------|----------|--------|
| 1. Tools Off/On Flag | | Pending |
| 2. Audit Trail | | Pending |
| 3. Self-Heal Cap | | Pending |
| 4. Artifact Layout | | Pending |
| 5. Adversarial Suite | | Pending |
| 6. Gate Drift | | Pending |
| 7. Smoke Matrix | | Pending |
| 8. Packaging | | Pending |
| 9. Positioning | | Pending |

---

*Ready to discuss Topic 1. Which topic would you like to start with?*
