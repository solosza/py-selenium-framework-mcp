# PRD: 7-Step Pair Programming Workflow v4.0

**Status:** Living Document (Iterative Development)
**Current Phase:** Step 1 Requirements
**Version:** 1.0
**Date:** 2026-01-23

---

## Implementation Strategy (Iterative, Not Waterfall)

This PRD uses an **iterative vertical slice approach** - each step is fully specified, implemented, and validated before moving to the next step.

**Workflow per Step:**
```
Step N: Design → PRD → Test Plan → Tasks → Implement → Validate → Ship
  ↓ (working code, lessons learned)
Step N+1: Repeat with learnings from previous step
```

**Living Document Pattern:**
- This PRD starts with Step 1 requirements only
- Each subsequent step is added AFTER the previous step is validated
- Prevents waterfall waste (designing all 7 steps, then realizing Step 1 assumptions were wrong)
- Enables course correction based on implementation learnings

**Current Status:**
- ✅ Step 1: COMPLETE (139 tests, 98% coverage)
- 📋 Step 2-7: To be added after Step 1 implementation

---

## Step Implementation Checklist (Phase 0)

Before implementing any step, run this assessment to avoid reinventing the wheel:

### 0.1 Check Existing Components

| Component | Location | Questions to Answer |
|-----------|----------|---------------------|
| Gate | `mcp_server/tools/gates/qg_*.py` | Exists? Implements POST validation? |
| Protocol | `.claude/skills/qa-management-layer/references/step-0X.md` | Exists? Up to date? |
| Archived Gates | `_archived/autonomous_workflow_v1/gates/` | Reusable validation logic? |
| Archived Tools | `_archived/autonomous_workflow_v1/tools/` | Patterns to adapt? |
| Tests | `mcp_server/_dev_tests/test_gates/test_qg_*.py` | Exist? Passing? Coverage? |
| Shared Utils | `mcp_server/utils/` (StateManager, AuditLogger, TranscriptWriter) | Already work for this step? |

### 0.2 Document Findings

| Component | Status | Tests? | Action Needed |
|-----------|--------|--------|---------------|
| Gate | EXISTS / MISSING | YES (X%) / NO | FIX / CREATE / GAP-FILL |
| Protocol | EXISTS / MISSING | N/A | UPDATE / CREATE |
| Archived Code | REUSABLE / N/A | N/A | ADAPT / SKIP |

### 0.3 Adjust Plan Based on Findings

| Finding | Action |
|---------|--------|
| Component EXISTS with passing tests | Verify coverage, gap-fill if < target |
| Component EXISTS with failing tests | Fix tests first, then gap-fill |
| Component EXISTS without tests | Test-After approach (not TDD) |
| Component MISSING but archived exists | Adapt archived code, then test |
| Component MISSING entirely | TDD from scratch |

### 0.4 Typical Phase Structure

```
Phase 0: Pre-Implementation Assessment (this checklist)
Phase 1: Test Infrastructure (fixtures, test data, directories)
Phase 2: Core Component Tests (gate 4-layer pyramid)
Phase 3: Integration Tests (state, audit, transcript)
Phase 4: Protocol Update (if needed)
Phase 5: Documentation & Commit
```

### 0.5 Required Task Coverage (6 Defense-in-Depth Layers)

**MANDATORY:** Every step implementation MUST include tasks covering all 6 layers:

| Layer | Component | Required Tasks | Test Target |
|-------|-----------|----------------|-------------|
| 1 | **Protocol** (`step-0X.md`) | Verify matches implementation, update if needed | Behavior verification |
| 2 | **Smart Gate** (`qg_*.py`) | 4-layer test pyramid + teach validation | 95% coverage |
| 3 | **Hook** (`audit-trail-writer.py`) | Integration tests (fires correctly, appends audit) | 85% coverage |
| 4 | **State** (`StateManager`) | Checkpoint saved, merge with previous steps | 90% coverage |
| 5 | **Audit** (`AuditLogger`) | Event logged, step field correct, metadata | 90% coverage |
| 6 | **Transcript** (`TranscriptWriter`) | Entry appended (not overwrite), format correct | 90% coverage |

**Gate-Specific Required Tasks:**

| Task Category | Description | PRD Reference |
|---------------|-------------|---------------|
| PRE-Check | Verify gate blocks if previous step incomplete | FR-X.5 |
| POST Validation | All input fields validated with fix hints | FR-X.1-X.4 |
| Teach Content | `teach` terminology used, hints are actionable | DD-50 |
| NEEDS_RETRY | Scaffolding templates for missing infrastructure | FR-X.8 |
| State Merge | Previous step state preserved, not overwritten | FR-X.6 |

**Parent Task Template (Copy for Each Step):**

```markdown
| # | Parent Task | Type | Component | Description |
|---|-------------|------|-----------|-------------|
| 0.0 | Pre-Implementation Assessment | GLUE | All | Check existing, run tests, document findings |
| 1.0 | Fix Existing Tests (if any) | CORE | Gate | Add mocks, fix broken tests |
| 2.0 | Gate 4-Layer Test Pyramid | CORE | Gate | L1 validators, L2 edge, L3 integration, L4 failures |
| 3.0 | Smart Gate Teach Validation | CORE | Gate | Verify teach content, not fix_hint |
| 4.0 | State Integration Tests | CORE | State | Checkpoint, merge, isolation |
| 5.0 | Audit Integration Tests | CORE | Audit | Event logged, step field, metadata |
| 6.0 | Hook Integration Tests | CORE | Hook | PostToolUse fires, audit appended |
| 7.0 | Transcript Integration | CORE | Transcript | Entry appended, format correct |
| 8.0 | PRE-Check Validation | CORE | Gate | Blocks if previous step incomplete |
| 9.0 | NEEDS_RETRY Scaffolding | CORE | Gate | Templates for missing infrastructure |
| 10.0 | Protocol Verification | GLUE | Protocol | Matches implementation, update if needed |
| 11.0 | Documentation & Ship | GLUE | All | Final tests, coverage, PRD/SESSION update |
```

**Acceptance Test Mapping (Required):**
- Every AT-X.Y from PRD MUST map to at least one test
- Document mapping in task results section

---

## Introduction/Overview

The 7-Step Pair Programming Workflow v4.0 transforms QA test automation from autonomous code generation to collaborative AI-human pair programming. This workflow implements Isagawa Corp's AI Management Layer vision: **protocols define correct execution, smart gates enforce compliance at every step.**

**Problem:** Current 4-step workflow (v3.1) has autonomous machinery in Step 4 (navigation tracking, RuntimeValidator, multi-page detection) - not designed for pair programming collaboration where AI and user iterate together to build working tests.

**Solution:** Expand to 7-step workflow with explicit HITL (Human-in-the-Loop) iteration:
1. User Input (data collection)
2. Pre-flight Config (test setup decisions)
3. AI Processing (BDD extraction, intent detection)
4. Discovery (navigate + reveal elements - simplified)
5. Generate Skeleton (AI writes all 4 layers FAST - runnable, bugs OK)
6. **HITL Iteration** (run → fail → triage → fix → repeat until green)
7. Framework Validation (final compliance check)

**Key Innovation:** Step 6 borrows proven HITL pattern from archived Step 11 - generate all 4 layers quickly, then collaborate on fixes. Faster than element-by-element construction.

---

## Goals

### Primary Goals
1. **Enable pair programming collaboration** - AI and user work together to fix broken tests, not autonomous generation
2. **Faster to working test** - Generate all 4 layers in 10 minutes, iterate via HITL until green
3. **Clear separation of concerns** - Each step has ONE job (discover → generate → iterate → validate)
4. **Maintain compliance** - All 28 Design Decisions enforced via gates, not lost in transition

### Secondary Goals
5. **Reuse proven patterns** - 60% of archived gate validation logic, Step 11 HITL triage pattern
6. **Shippable increments** - Each step implementation is independently valuable
7. **Teaching through enforcement** - Gates provide fix hints, not just blocks

---

## User Stories

**As a QA engineer,** I want to describe a test requirement and collaborate with AI to build it, so that I can leverage AI assistance without losing control of the process.

**As a QA engineer,** I want the AI to generate a working test skeleton quickly, so that I can spend time iterating on fixes rather than waiting for perfect upfront generation.

**As a QA engineer,** I want structured triage options when tests fail, so that I can guide AI fixes efficiently (locator vs flow vs logic issues).

**As a framework maintainer,** I want gates to teach framework patterns through fix hints, so that AI learns correct patterns without manual intervention.

**As a product manager,** I want each step to be independently shippable, so that we can validate assumptions before building the entire workflow.

---

## Step 1: User Input

### Functional Requirements

**FR-1.1: User Input Collection**
- System MUST ask user for test requirement in "As a [persona], I want to [action]" format
- System MUST ask user for target URL (HTTP/HTTPS format)
- System MUST ask user for workflow identifier (organizes tests by feature/sprint/run)

**FR-1.2: Data Extraction**
- System MUST extract `persona` from "As a [X]" pattern
- System MUST convert persona to PascalCase `role_name` (e.g., "registered user" → "RegisteredUser")
- System MUST store full user requirement verbatim as `raw_requirement`

**FR-1.3: Environment Auto-Detection**
- System MUST check URL against `framework/resources/config/environment_config.json`
- System MUST return `detected_env_id` if domain matches existing environment
- System MUST offer scaffolding if domain is unknown (NEEDS_RETRY pattern with template)

**FR-1.4: Gate Validation (POST-only)**
- System MUST validate `persona` is non-empty string
- System MUST validate `URL` is valid HTTP/HTTPS format (regex + urlparse)
- System MUST validate `role_name` is PascalCase (regex: `^[A-Z][a-zA-Z0-9]*$`)
- System MUST validate `workflow` is non-empty string (dynamic, not hardcoded list)
- System MUST validate `raw_requirement` is non-empty
- System MUST provide fix hints for all validation failures

**FR-1.5: State Checkpoint**
- On gate PASS, system MUST save checkpoint to `tests/_state/{run_id}/workflow_state.json`
- State MUST include: `persona`, `URL`, `role_name`, `workflow`, `raw_requirement`, `detected_env_id`
- State MUST include step number (1) and status ("complete")
- State MUST include ISO-8601 timestamp

**FR-1.6: Audit Logging**
- System MUST log gate validation event to `tests/_audit/audit_log_{run_id}.json`
- Audit entry MUST include: type, step, gate, mode, result, timestamp, metadata
- Audit log MUST use atomic writes (crash-safe, no data loss - DEF-040)
- Audit log MUST use existing v1.0 schema (compliance upgrades deferred to post-MVP)

**FR-1.7: Workflow Transcript**
- System MUST write transcript entry to `tests/_reports/{run_id}/workflow_transcript.md`
- Transcript MUST be append-only (don't overwrite existing content)
- Transcript MUST include: step name, user inputs, extracted data, gate result, timestamp
- Transcript MUST use markdown format (readable without tools)

**FR-1.8: Gate Retry Pattern**
- On gate FAIL, system MUST present fix hint to user
- System MUST allow user to correct invalid input
- System MUST retry validation (no max retry limit - user corrects, not AI)
- System MUST NOT use HITL pattern (gate retry is corrective, HITL is choice between valid options)

### Non-Goals (Out of Scope)

**NG-1.1:** PRE gate validation (POST-only is sufficient for Step 1 - first step has no prerequisites)

**NG-1.2:** Audit v2.0 compliance features (actor tracking, decision rationale, integrity hash, retention metadata) - deferred to post-MVP, feature flag approach designed but not implemented

**NG-1.3:** Multi-persona support (one persona per test run)

**NG-1.4:** Requirement editing after gate PASS (must restart workflow to change requirement)

**NG-1.5:** Credential strategy or test data location questions (handled in Step 2: Pre-flight Config)

### Design Considerations

**Protocol Reference:** `.claude/skills/qa-management-layer/references/step-01.md`

**Design Decisions Applied:**
- DD-01: Persona required (ASK if missing)
- DD-02: URL required upfront (ASK if missing)
- DD-07: Workflow determined by AI from user input, passed through metadata
- DD-22: On ANY blocker, STOP → REPORT → DISCUSS with user

**Gate Retry vs HITL Distinction:**
- **Gate Retry (Step 1):** User provides invalid input → Gate FAIL → Fix hint → User corrects → Retry
- **HITL (Step 6):** Test fails → AI presents 3 triage options (locator/flow/logic) → User chooses → AI fixes
- Step 1 uses gate retry (corrective action), NOT HITL (choice between valid options)

**Workflow Transcript Format:**
```markdown
## Step 1: User Input ✓
**Completed:** 2026-01-23 10:30:52 UTC
**Duration:** 7 seconds

### User Inputs
- **Requirement:** "As a registered user, I want to login with email and password"
- **URL:** https://staging.example.com/login
- **Workflow:** helios7

### Extracted Data
- **Persona:** registered user
- **Role Name:** RegisteredUser
- **Environment Detected:** staging

### Gate Result
✓ **PASS** - qg_user_input (POST)
```

### Technical Considerations

**Existing Components (Reuse):**
- ✅ `qg_user_input.py` gate - already implements POST validation
- ✅ `AuditLogger` (v1.0) - already implements atomic persist (DEF-040)
- ✅ `StateManager` - already implements per-run isolation
- ✅ PostToolUse hook (`.claude/hooks/audit-trail-writer.py`) - already logs gate calls

**New Components Needed:**
- ⬜ Workflow transcript writer (markdown append logic)
- ⬜ Protocol update - add transcript write step

**Dependencies:**
- `mcp_server/tools/gates/base_gate.py` (BaseGate.validate_and_pass())
- `mcp_server/utils/state_manager.py` (StateManager.save_step())
- `mcp_server/utils/audit_logger.py` (AuditLogger.log_gate())
- `framework/resources/config/environment_config.json` (environment detection)

**Design Constraints:**
- Transcript must be human-readable (simple markdown, no JSON)
- Audit log must be machine-readable (JSON, immutable)
- State must be recoverable (atomic writes, per-run isolation)
- Gate validation must be deterministic (same input = same result)

---

## Success Metrics

### Step 1 Success Criteria

**Immediate Metrics:**
- Gate validation accuracy: 100% (no false positives/negatives)
- State save success rate: 100% (atomic writes, no data loss)
- Audit log completeness: 100% (every gate call logged)
- Transcript readability: User can understand progress without reading code

**Quality Metrics:**
- Gate retry rate: <20% (most users provide valid input on first try)
- Average retries per invalid input: <2 (fix hints are clear)
- Environment detection accuracy: >90% (most URLs match existing environments)

**Performance Metrics:**
- Step 1 completion time: <30 seconds (including user interaction)
- Gate validation time: <100ms (validation is fast, no blocking I/O)

**Validation Criteria:**
- ✅ Unit tests pass (gate validation logic, state save, audit log)
- ✅ Integration tests pass (E2E Step 1 flow)
- ✅ Manual testing: User completes Step 1 without confusion
- ✅ Transcript is readable in any text editor

---

## Test Strategy (MVP)

### Testing Approach

**TDD for Core Logic (Gates, State, Audit):**
- Write failing tests → Implement minimal code → Refactor
- Target coverage: 95%+ for gates, 90%+ for state/audit

**Test-After for Protocols:**
- Implement protocol → Test behavior end-to-end
- Target coverage: 80%+ (protocol adherence, not line coverage)

**Test Pyramid (Step 1 Components):**

| Component | Test Layers | Tools | Coverage Target |
|-----------|-------------|-------|-----------------|
| **Protocol** | Behavior verification (does AI follow steps?) | Integration tests | 80% |
| **Gate** | Pattern detection, validation logic, fix hints | Unit tests (TDD) | 95% |
| **State** | Save/load, isolation, recovery | Unit tests (TDD) | 90% |
| **Audit** | Format, immutability, completeness | Unit tests (TDD) | 90% |
| **Hook** | Trigger verification, non-blocking | Integration tests | 85% |
| **Transcript** | Format, append behavior, readability | Integration tests | 80% |

### Acceptance Tests (GIVEN/WHEN/THEN)

**AT-1.1: Valid user input (happy path)**
```gherkin
GIVEN user provides valid persona "As a registered user, I want to login"
  AND user provides valid URL "https://example.com/login"
  AND user provides workflow "auth"
WHEN system validates inputs via qg_user_input (POST)
THEN gate returns PASS
  AND state saved with persona="registered user", role_name="RegisteredUser", workflow="auth"
  AND audit log contains gate_validation event with result="pass"
  AND transcript contains Step 1 ✓ entry
```

**AT-1.2: Invalid persona (fix hint provided)**
```gherkin
GIVEN user provides empty persona ""
  AND user provides valid URL
WHEN system validates inputs
THEN gate returns FAIL with error "Invalid persona: must be non-empty"
  AND fix hint contains "Persona must be a non-empty string describing the user role"
  AND user is prompted to re-enter persona
```

**AT-1.3: Invalid URL format**
```gherkin
GIVEN user provides valid persona
  AND user provides malformed URL "htp://broken-url"
WHEN system validates inputs
THEN gate returns FAIL with error "Invalid URL format: 'htp://broken-url'"
  AND fix hint contains example "http://automationpractice.pl/index.php?controller=authentication"
```

**AT-1.4: Environment auto-detection (known domain)**
```gherkin
GIVEN user provides URL "https://parabank.parasoft.com/parabank/index.htm"
  AND environment_config.json contains entry for "parabank.parasoft.com"
WHEN system auto-detects environment
THEN detected_env_id = "parabank"
  AND state saved with detected_env_id="parabank"
```

**AT-1.5: Environment auto-detection (unknown domain - scaffolding)**
```gherkin
GIVEN user provides URL "https://unknown-site.com/page"
  AND environment_config.json does NOT contain entry for "unknown-site.com"
WHEN system auto-detects environment
THEN gate returns NEEDS_RETRY with scaffolding_needed
  AND scaffolding template contains JSON config for "unknown-site.com"
  AND user is asked "Unknown environment. Should I create config for 'unknown-site.com'?"
```

**AT-1.6: Role name extraction (PascalCase conversion)**
```gherkin
GIVEN user provides persona "As a sales representative, I want to submit inquiry"
WHEN system extracts role_name
THEN role_name = "SalesRepresentative"
  AND state saved with role_name="SalesRepresentative"
```

**AT-1.7: Audit log atomic write (crash safety)**
```gherkin
GIVEN Step 1 in progress
  AND gate validation event logged
WHEN system crashes before workflow completion
THEN audit log file contains partial events
  AND audit log is valid JSON (atomic write completed)
  AND no data loss occurred
```

**AT-1.8: Workflow transcript append (multiple steps)**
```gherkin
GIVEN Step 1 completed (transcript exists)
WHEN Step 2 writes transcript entry
THEN transcript contains BOTH Step 1 and Step 2 entries
  AND Step 1 entry is NOT overwritten
  AND transcript is valid markdown
```

**AT-1.9: Gate retry (user corrects invalid input)**
```gherkin
GIVEN user provides invalid role_name "lowercase-role"
WHEN gate validation fails
  AND user corrects to "LowercaseRole"
  AND gate validation retries
THEN gate returns PASS
  AND state saved with corrected role_name
```

**AT-1.10: State isolation (per-run)**
```gherkin
GIVEN two workflow runs: run_A and run_B
WHEN both runs complete Step 1
THEN state saved to tests/_state/{run_A}/workflow_state.json
  AND state saved to tests/_state/{run_B}/workflow_state.json
  AND run_A state does NOT overwrite run_B state
```

### Non-Functional SLAs

**Performance:**
- Gate validation latency: p50 < 50ms, p95 < 100ms, p99 < 200ms
- State save latency: p50 < 10ms, p95 < 50ms (atomic write to disk)
- Audit log persist latency: p50 < 20ms, p95 < 100ms
- Transcript write latency: p50 < 50ms, p95 < 200ms
- End-to-end Step 1 latency: <30 seconds (including user interaction)

**Error Handling:**
- Gate validation failures: Provide fix hint in <200ms
- State save failures: Raise exception, do NOT silently fail
- Audit log failures: Raise exception, workflow MUST NOT proceed without audit
- File I/O errors: Retry once, then raise exception with clear error message

**Reliability:**
- State save success rate: 99.9% (atomic writes, crash-safe)
- Audit log completeness: 100% (every gate call logged, no data loss)
- Environment detection accuracy: >90% (known domains matched correctly)

### Observability/Telemetry

**Events to Log:**

| Event Type | When | Fields | Purpose |
|------------|------|--------|---------|
| `gate_validation` | After qg_user_input call | step, gate, mode, result, timestamp, metadata | Audit trail, debugging |
| `state_checkpoint_saved` | After state save | step, timestamp, file_path | Recovery, debugging |
| `transcript_updated` | After transcript write | step, timestamp, file_path | User visibility |
| `environment_detected` | After environment detection | detected_env_id, url, is_known | Environment management |
| `gate_retry` | After gate FAIL with retry | step, gate, attempt, error | Error analysis |

**Log Assertions (Tests):**
- Test that gate_validation event is logged on PASS
- Test that gate_validation event is logged on FAIL (with error field)
- Test that state_checkpoint_saved event is logged after state save
- Test that transcript_updated event is logged after transcript write

### Security & Privacy

**Threat Model:**
- ✅ No PHI/PII in Step 1 (test automation metadata only)
- ✅ No secrets in Step 1 (credentials handled in Step 2)
- ⚠️ URL may contain sensitive paths (audit log stored locally, not transmitted)

**Secrets Policy:**
- ❌ NO secrets in audit log (URLs may contain paths but not credentials)
- ❌ NO secrets in state (credentials handled in Step 2)
- ❌ NO secrets in transcript (user-facing, markdown format)

**Data Handling:**
- Audit logs: Local storage (`tests/_audit/`), not transmitted
- State files: Local storage (`tests/_state/`), per-run isolation
- Transcript: Local storage (`tests/_reports/`), human-readable

**Abuse Cases:**
- Malicious URL injection: Validate URL format (regex + urlparse)
- Path traversal in workflow identifier: Validate alphanumeric + hyphen/underscore only
- Audit log tampering: Use atomic writes (DEF-040), integrity hash deferred to post-MVP

### Rollout & Rollback

**Feature Flags:**
- None for Step 1 (first step, always enabled)

**Rollout Plan:**
1. Implement Step 1 (this PRD)
2. Test Step 1 E2E (acceptance tests)
3. Validate Step 1 with manual testing
4. Ship Step 1 as v4.0-step1 (shippable increment)
5. Move to Step 2 design (repeat cycle)

**Rollback:**
- If Step 1 fails in production, revert to v3.1 workflow (4-step)
- No data loss (Step 1 isolated, no side effects beyond Step 1)

**Smoke Test:**
```gherkin
GIVEN user starts new workflow run
WHEN user completes Step 1 with valid inputs
THEN state saved, audit logged, transcript written
  AND Step 2 can read Step 1 state successfully
```

---

## Open Questions

1. **Workflow transcript location:** Should transcripts be in `tests/_reports/{run_id}/` or `tests/_state/{run_id}/`?
   - **Decision needed:** Reports (user-facing) vs State (system-facing)?

2. **Environment scaffolding:** Should AI automatically create environment config, or always ask user first?
   - **Current:** Ask user first (NEEDS_RETRY pattern)
   - **Alternative:** Auto-create with confirmation after

3. **Gate retry limit:** Should there be a max retry limit (e.g., 3 attempts) to prevent infinite loops?
   - **Current:** No limit (user corrects, not AI - no risk of infinite loop)
   - **Alternative:** 5 retry limit, then escalate to user

4. **Transcript format:** Should transcript use emoji status indicators (✓ ⏳ ❌)?
   - **Current:** Yes (readable, visual feedback)
   - **Alternative:** Text-only (accessible, screen reader friendly)

---

## Definition of Ready (Lightweight Gate)

Step 1 PRD is ready for task generation when:

- ✅ Functional requirements defined (FR-1.1 through FR-1.8)
- ✅ Test strategy defined (test pyramid, acceptance tests, SLAs)
- ✅ Acceptance tests written (10 scenarios covering happy/negative/edge cases)
- ✅ Non-functional requirements defined (performance, error handling, reliability)
- ✅ Observability/telemetry defined (events to log, assertions)
- ✅ Security & privacy reviewed (no secrets, threat model documented)
- ✅ Rollout & rollback plan defined (smoke test, revert plan)

**Status:** ✅ COMPLETE (139 tests, 98% coverage)

---

## Step 2: Pre-flight Configuration

### Phase 0 Assessment (Don't Reinvent the Wheel)

| Component | Status | Location | Tests | Action |
|-----------|--------|----------|-------|--------|
| **Gate** | ✅ EXISTS | `mcp_server/tools/gates/qg_preflight.py` (11KB) | 26 tests (15 failing) | **FIX TESTS** |
| **Protocol** | ✅ EXISTS | `.claude/skills/qa-management-layer/references/step-02.md` (15KB) | N/A | Verify current |
| **Archived** | N/A | No preflight in `_archived/` | N/A | Skip |
| **Shared Utils** | ✅ Reuse | StateManager, AuditLogger, TranscriptWriter | Already tested | Reuse |

**Root Cause of Failing Tests:** Tests missing transcript check mock (same issue as Step 1).

**Effort Adjustment:**
- Original: Full TDD from scratch
- Revised: Fix 15 failing tests + gap-fill to 95% coverage

---

### Functional Requirements

**FR-2.1: Credential Strategy Configuration (DD-24)**
- System MUST ask user which credential strategy to use
- Valid options: `static`, `dynamic`, `self-contained`, `none`
- System MUST validate selection is one of valid options
- System MUST provide fix hint if invalid selection

**FR-2.2: Test Data Location Configuration (DD-28)**
- System MUST ask user where test data should live
- Valid options: `shared`, `workflow`, `both`, `none`
- System MUST validate selection is one of valid options
- System MUST provide fix hint if invalid selection

**FR-2.3: Browser Configuration**
- System MUST configure browser settings for pair programming
- `headless: false` REQUIRED for pair programming (user sees browser)
- System MUST validate headless is boolean
- System MUST provide fix hint if invalid

**FR-2.4: Timeout Configuration**
- System MUST configure timeout settings
- `enabled: true/false` - whether timeout monitoring active
- `threshold_seconds: N` - timeout threshold (required if enabled=true)
- System MUST validate configuration structure

**FR-2.5: Gate Validation (POST-only)**
- System MUST validate all 4 configuration fields
- System MUST check Step 1 transcript exists (PRE-check)
- System MUST provide fix hints for all validation failures
- System MUST use `teach` terminology (not `fix_hint`)

**FR-2.6: State Checkpoint**
- On gate PASS, save to `tests/_state/{run_id}/workflow_state.json`
- State MUST include: credential_strategy, test_data_location, browser_config, timeout_config
- State MUST merge with Step 1 state (not overwrite)

**FR-2.7: Audit Logging**
- System MUST log gate validation event to audit log
- Audit entry MUST include: step=2, gate=qg_preflight, result, metadata

**FR-2.8: Infrastructure Scaffolding (NEEDS_RETRY Pattern)**
- If credential strategy requires files that don't exist, return NEEDS_RETRY
- Provide scaffolding template for missing files
- Allow AI to create files and retry

---

### Non-Goals (Out of Scope)

**NG-2.1:** Actual credential file content (user provides credentials, not system)
**NG-2.2:** Browser driver installation (handled by webdriver-manager)
**NG-2.3:** Timeout enforcement (configured here, enforced in Step 6)

---

### Design Considerations

**Protocol Reference:** `.claude/skills/qa-management-layer/references/step-02.md`

**Design Decisions Applied:**
- DD-24: Credential strategy (static/dynamic/self-contained/none)
- DD-28: Test data organization (shared/workflow/both/none)

**Existing Gate Implementation:**
- `qg_preflight.py` already implements validation logic
- PRE-check for Step 1 transcript already implemented
- NEEDS_RETRY scaffolding pattern already implemented

---

### Acceptance Tests (GIVEN/WHEN/THEN)

**AT-2.1: Valid Configuration Passes**
```
GIVEN Step 1 completed (transcript exists)
  AND user provides valid credential_strategy (static)
  AND user provides valid test_data_location (shared)
  AND user provides valid browser_config (headless: false)
  AND user provides valid timeout_config (enabled: true, threshold_seconds: 30)
WHEN AI calls qg_preflight gate
THEN gate returns status: pass
  AND state saved with all 4 configuration fields
  AND audit log contains Step 2 event
```

**AT-2.2: Invalid Credential Strategy Fails**
```
GIVEN Step 1 completed
  AND user provides invalid credential_strategy ("invalid")
WHEN AI calls qg_preflight gate
THEN gate returns status: fail
  AND error mentions invalid credential_strategy
  AND teach provides valid options
```

**AT-2.3: Missing Step 1 Transcript Fails**
```
GIVEN Step 1 NOT completed (no transcript)
WHEN AI calls qg_preflight gate
THEN gate returns status: fail
  AND error mentions Step 1 transcript required
```

**AT-2.4: Scaffolding for Missing Credential File**
```
GIVEN Step 1 completed
  AND user provides credential_strategy: static
  AND tests/data/test_users.json does NOT exist
WHEN AI calls qg_preflight gate
THEN gate returns status: NEEDS_RETRY
  AND scaffolding_needed contains credential file template
```

**AT-2.5: Pass When Infrastructure Exists**
```
GIVEN Step 1 completed
  AND user provides valid configuration
  AND all required infrastructure files exist
WHEN AI calls qg_preflight gate
THEN gate returns status: pass
```

---

### Test Strategy

**Test Pyramid (Target: 95% coverage for gate):**
- Layer 1: 20-30 tests (validation helpers, regex patterns)
- Layer 2: 10-15 tests (edge cases, invalid inputs)
- Layer 3: 3-5 tests (integration with state, PRE-check)
- Layer 4: 2-3 tests (production failures, scaffolding)

**Existing Tests:** 26 tests exist (15 failing due to missing mock)
**Action:** Fix failing tests first, then gap-fill to 95% coverage

---

### Definition of Ready

Step 2 PRD is ready for task generation when:
- ✅ Functional requirements defined (FR-2.1 through FR-2.8)
- ✅ Phase 0 assessment completed (existing components documented)
- ✅ Acceptance tests written (5 scenarios)
- ✅ Test strategy defined (fix existing + gap-fill)

**Status:** ✅ Ready for task generation

---

**Next:** Generate tasks for Step 2 implementation
