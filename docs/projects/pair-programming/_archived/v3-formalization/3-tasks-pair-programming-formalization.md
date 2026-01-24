# Tasks: Pair Programming Workflow Formalization

**Based on:** `2-prd-pair-programming-formalization.md`
**Date:** 2026-01-21
**Status:** Phase 3 (Divide) - Task Generation Complete

---

## Relevant Files

### Protocol Files (Layer 1)
- `.claude/skills/qa-management-layer/SKILL.md` - Main workflow definition (update for pair programming)
- `.claude/skills/qa-management-layer/references/step-01.md` - Pre-flight configuration (update)
- `.claude/skills/qa-management-layer/references/step-02.md` - User input (update)
- `.claude/skills/qa-management-layer/references/step-03.md` - AI processing (update)
- `.claude/skills/qa-management-layer/references/step-04.md` - Collaborative construction (NEW - replace old steps 4-10)
- `.claude/skills/qa-management-layer/references/collaboration-patterns.md` - NEW - Stop-when-blocked, build-as-you-go patterns
- `.claude/skills/qa-management-layer/references/protocol-environment.md` - Configuration requirements (headless, timeout)

### Smart Gates (Layer 2)
- `mcp_server/tools/gates/qg_test_runner.py` - Update to validate AND teach (not just block)
- `mcp_server/tools/gates/qg_page_object.py` - Update to provide fix data on DD violations
- `mcp_server/tools/gates/qg_task.py` - Update to provide fix data (DD-27 locators in Tasks)
- `mcp_server/tools/gates/gate_utils.py` - NEW - Common fix data generation utilities

### Hooks (Layer 3)
- `.claude/hooks/` - Claude Code hooks (PostToolUse pattern)
- Hook implementation: Monitor execution time, force HITL on threshold
- Hook implementation: Detect loops (3+ failures, same fix twice)

### Configuration
- `framework/resources/config/environment_config.json` - Add timeout_monitoring, enforce headless=false
- `framework/resources/config/pair_programming_config.json` - NEW - Pair programming specific config

### Audit System (Layer 5)
- `mcp_server/utils/audit_logger.py` - Enhance to log HITL interactions, timeout events, build-save-test cycles
- `mcp_server/utils/audit_reconstructor.py` - NEW - Replay session from audit log

### Tests
- `mcp_server/_dev_tests/test_gates/` - USE EXISTING - Add new gate tests here for teaching fixes
- `mcp_server/_dev_tests/test_workflow_integration/test_6_layer_defense.py` - NEW - Integration test for all 6 layers
- `tests/helios8/` (or target site) - NEW - E2E test via pair programming (follows production structure)
  - `framework/pages/helios8/` - Page objects
  - `framework/tasks/helios8/` - Task workflows
  - `framework/roles/helios8/` - Role orchestration
  - `tests/helios8/test_submit_inquiry.py` - Test runner

### Documentation
- `docs/projects/pair-programming/4-validation-report.md` - NEW - Validation results after implementation

### Notes
- Use `pytest` to run tests
- Commit after each completed parent task
- Use feature branch: `feature/pair-programming`
- Archive helios1-7 tests to `tests/archive/` before starting
- Hooks location: `.claude/hooks/` (Claude Code hooks, not mcp_server/)
- Test structure: Follow production pattern (helios8 or target site)

---

## Tasks

### 0.0 Project Setup [GLUE]
- [ ] 0.1 Create feature branch `feature/pair-programming`
- [ ] 0.2 Archive existing tests: move `tests/helios1-7/` to `tests/archive/`
- [ ] 0.3 Prepare directory structure
  - Create `tests/archive/` and move helios1-7 tests (and corresponding framework modules if desired)
  - NO new directories needed - use existing `.claude/hooks/` for Hook layer
  - NO new test structure - next test follows production pattern (helios8 or target site)
- [ ] 0.4 Run checks (ensure clean starting state)
- [ ] 0.5 Record results
- [ ] 0.6 Commit: `chore: Setup pair programming formalization (Task 0.0)`

**Done When:**
- Feature branch created from current stable point
- helios1-7 archived (preserve history)
- Directory structure validated (existing paths confirmed)
- Clean git status

---

### 1.0 Update Protocol Files (Layer 1 Defense) [CORE]

**CRITICAL:** Protocols MUST guide AI to write correct code patterns. This is Layer 1 defense - if this fails, everything downstream fails.

**EATING OUR DOGFOOD:** Use HITL pattern (assess+fix immediately, one file at a time). Fix while context is fresh.

**PATTERN:** Read file → Assess (Layer 1, Layer 2, HITL) → Fix immediately → Integration test → Next file

**SRP:** Data contracts (DD-26) separated into Phase 1.2 (separate responsibility from protocol assessment)

---

#### Phase 1.1: Protocol Files - Step-by-Step Assessment & Fix

**Pattern:** For each protocol file: Read → Assess → Fix → Test → HITL approval

---

##### 1.1.1 SKILL.md (Overview Protocol)

- [x] 1.1.1.1 Read & Assess SKILL.md

    **Assessment (COMPLETE):**
    - File location: `.claude/skills/qa-management-layer/SKILL.md`
    - Purpose: Entry point for 11-step QA workflow automation
    - Key contents:
      - Workflow overview diagram (Steps 1-11)
      - Gate enforcement rules (sequential execution, mandatory PASS before proceeding)
      - Step reference table mapping each step to protocol file and gate mode
      - Self-heal validation protocol (when tools generate skeleton code)
      - Smart escalation protocol (after 3 failures, provide actionable guidance)
      - Gate return format: success `{"status": "pass"}`, failure `{"status": "fail", "error": "...", "fix_hint": "..."}`
      - Gate modes: POST-only (Steps 1-3), PRE+POST (Steps 4-9), PRE-only (Step 10)
    - Critical rules documented:
      - SEQUENTIAL EXECUTION - Must complete Step N before Step N+1
      - GATE ENFORCEMENT - Each step has quality gate that must PASS
      - STATE PERSISTENCE - Each step saves state on success
      - STOP-AND-DISCUSS (DD-22) - On ANY blocker: STOP → REPORT → DISCUSS → PROCEED
      - NO INTERNAL REFERENCES - Never mention DD-XX references to users
    - Communication guidelines: DO NOT show internal gate status, DO show progress indicators

    **Gap Analysis:**
    - ❓ NEEDS_RETRY auto-recovery: Exists in `qg_save_run.py` (7 recovery actions, max 3 attempts, then escalate to DD-22)
    - ❓ Tool usage: SKILL.md documents Tools 1-6 workflow, but PRD says Tools 3-6 optional
    - ❓ Step structure: SKILL.md has 11 steps, PRD has 5 steps (Step 4 = Collaborative Construction replaces old Steps 4-10)

    **Decisions After PRD/Design Doc Review:**
    1. **NEEDS_RETRY Status: KEEP** ✅
       - NEEDS_RETRY = Smart Gates teaching (Layer 2 defense)
       - Auto-retry with fix data (up to 3 attempts)
       - HITL escalation after exhaustion (Layer 6 backstop)
       - Two blocker types: Construction blockers → immediate HITL, Validation blockers → Smart Gate retry first
       - No implementation needed (already exists in gates)

    2. **Tool Usage: RESOLVED** ✅
       - PRD FR-7.2: Tools 3-6 optional (on-demand)
       - AI defaults to Edit/Write tools for manual construction
       - Tools 3-6 available if user requests scaffolding
       - Not a contradiction, hybrid approach per PRD

    3. **Step Structure: REFACTOR NEEDED** ⚠️
       - PRD FR-9.1: New workflow is 5 steps (Steps 1-3, Step 4 Collaborative Construction, Step 5 Done)
       - Old Step 10 validation absorbed into Step 4's incremental validation
       - Task 1.2 will update SKILL.md to reflect new 5-step structure

    **Action Items:**
    - Update SKILL.md: Replace 11-step with 5-step collaborative construction workflow
    - Document Smart Gate + HITL escalation pattern
    - Verify NEEDS_RETRY pattern documented

- [ ] 1.1.1.2 Fix SKILL.md
  - Update: Replace 11-step workflow with 5-step (Steps 1-3, Step 4 Collaborative Construction, Step 5 Done)
  - Update: Document Tools 3-6 as optional (AI defaults to Edit/Write)
  - Verify: Smart Gate + HITL escalation pattern clear

- [ ] 1.1.1.3 Integration Test SKILL.md
  - Test: Read updated SKILL.md
  - Verify: 5-step structure documented correctly
  - Verify: No references to old 11-step workflow

- [ ] 1.1.1.4 HITL Approval - SKILL.md
  - Present: Changes made to SKILL.md
  - Wait: User approval before proceeding to step-01.md

---

##### 1.1.2 step-01.md (Pre-flight Configuration)

- [x] 1.1.2.1 Read & Assess step-01.md

    **Assessment (COMPLETE):**
    - File location: `.claude/skills/qa-management-layer/references/step-01.md`
    - Purpose: Establish configuration strategy before test generation (first step)
    - Input: None | Output: `credential_strategy`, `test_data_location`
    - Key features:
      - AI asks 2 questions: credential strategy (4 options), test data location (4 options)
      - User answers interactively → Gate validates → State saved
      - Gate: `qg_preflight` (POST-only)
      - NEEDS_RETRY: Auto-scaffolds `tests/data/` + `test_users.json` if missing (DEF-060)
      - Error handling: Re-ask if invalid, guide if user unsure
      - Transcript logging: Appends to workflow_transcript.md
    - Rules: DD-24 (credentials), DD-28 (test data)
    - Already interactive: ASK → WAIT → ASK → WAIT → VALIDATE → SAVE

    **Data Contract Check:**
    - **Output Schema (Section E, lines 80-90):**
      ```json
      {
        "step": 1,
        "status": "complete",
        "timestamp": "ISO-8601",
        "data": {
          "credential_strategy": "static | dynamic | self-contained | none",
          "test_data_location": "shared | workflow | both | none"
        }
      }
      ```
    - **Downstream Consumer:** Step 2 (User Input)
    - **Step 2 Dependencies (step-02.md lines 16, 36):**
      - Line 16: "Dependencies: Step 1 complete (credential_strategy, test_data_location exist)"
      - Line 36: "PRE-CHECK: Verify Step 1 complete (credential_strategy, test_data_location exist in state)"
    - **Contract Validation:**
      - ✅ Step 2 explicitly checks Step 1 complete (lines 16, 36)
      - ✅ Field names match exactly (credential_strategy, test_data_location)
      - ✅ PRE-CHECK enforces dependency
      - ✅ **State Accumulation (Design Intent):**
        - `qg_preflight.py` (lines 92-95): Saves Step 1 data via StateManager
        - `state_manager.py` (lines 72-86): Loads existing state, adds new step as `step_{N}`, preserves all
        - Each step saved separately: `step_1`, `step_2`, `step_3`, etc.
        - Downstream steps access via `state_manager.get_step(N)`
      - ⚠️ **NOT VERIFIED:** Contract testing needed (Phase 2) to confirm this actually works in practice

    **Gap Analysis (Layer 2 - Smart Gates):**
    - ✅ Already HITL by design (asks user, waits for answers)
    - ✅ NEEDS_RETRY for scaffolding (Smart Gate teaching pattern)
    - ⚠️ Missing: Browser visibility config (headless=false enforcement) - FR-8.1
    - ⚠️ Missing: Timeout monitoring config (threshold, enable/disable) - FR-8.2

    **Decisions:**
    1. **Add Browser/Timeout Config to Step 1** ✅
       - FR-8.1: Browser always visible (non-negotiable, inform user)
       - FR-8.2: Timeout monitoring configurable (default 30s, enable/disable)
       - Add to pre-flight questions (upfront configuration)

    2. **Keep NEEDS_RETRY pattern** ✅
       - Already aligns with Smart Gate teaching (Layer 2)

    3. **Keep as "Step 1"** ✅
       - Steps 1-3 remain (SKILL.md clarifies new 5-step workflow)

    **Action Items:**
    - Update step-01.md: Add browser visibility + timeout monitoring config
    - Update qg_preflight gate: Validate new fields

- [ ] 1.1.2.2 Fix step-01.md
  - Add: Section I - Browser Visibility Configuration (FR-8.1: headless=false, non-negotiable)
  - Add: Section J - Timeout Monitoring Configuration (FR-8.2: default 30s, enable/disable)
  - Update: Validation checks in Section F
  - Update: State schema in Section E

- [ ] 1.1.2.3 Fix qg_preflight.py gate
  - Add: Validation for browser_visibility field
  - Add: Validation for timeout_monitoring field
  - Update: State save to include new fields

- [ ] 1.1.2.4 Integration Test step-01
  - Test: Run qg_preflight with valid browser/timeout config
  - Verify: Gate validates and saves new fields correctly
  - Test: Run qg_preflight with invalid config
  - Verify: Gate rejects with clear error message

- [ ] 1.1.2.5 HITL Approval - step-01.md
  - Present: Changes to step-01.md and qg_preflight.py
  - Wait: User approval before proceeding to step-02.md

---

##### 1.1.3 step-02.md (User Input)

- [x] 1.1.3.1 Read & Assess step-02.md

    **Assessment (COMPLETE):**
    - File location: `.claude/skills/qa-management-layer/references/step-02.md`
    - Purpose: Collect and validate user's test requirement (persona + URL)
    - Input: User's natural language requirement | Output: `persona`, `URL`, `role_name`, `workflow`, `raw_requirement`, `detected_env_id`
    - Key features:
      - AI extracts persona, URL, role_name, workflow from user requirement
      - Gate: `qg_user_input` (POST-only validation)
      - NEEDS_RETRY: Environment auto-detection (DEF-062) with USER APPROVAL required
      - Error handling: ASK if requirement missing, re-ask on validation failure
      - Transcript logging: Appends to workflow_transcript.md
    - Rules: DD-01 (persona required), DD-02 (URL required)

    **Data Contract Check:**
    - **Upstream Dependency:** Step 1 (credential_strategy, test_data_location)
      - ✅ Line 16: "Dependencies: Step 1 complete"
      - ✅ Line 36: "PRE-CHECK: Verify Step 1 complete"
    - **Output Schema (Section E, lines 81-93):**
      ```json
      {
        "persona": "registered user",
        "URL": "http://automationpractice.pl/...",
        "role_name": "RegisteredUser",
        "workflow": "auth",
        "raw_requirement": "As a registered user...",
        "detected_env_id": "DEFAULT"
      }
      ```
    - **Downstream Consumer:** Step 3 (AI Processing)
    - **Step 3 Dependencies (step-03.md lines 16, 36, 39):**
      - Line 16: "Dependencies: Step 2 complete (persona, URL, role_name, **domain**, raw_requirement exist)"
      - Line 36: "PRE-CHECK: Verify Step 2 complete (persona, URL, role_name, **domain** exist in state)"
      - Line 39: "ACTION: READ raw_requirement from Step 2 state"
    - **Contract Validation:**
      - ✅ Step 3 explicitly checks Step 2 complete
      - ✅ persona → persona (match)
      - ✅ URL → URL (match)
      - ✅ role_name → role_name (match)
      - ✅ raw_requirement → raw_requirement (match)
      - ❌ **FIELD NAME MISMATCH:** Step 2 saves `workflow`, Step 3 expects `domain`
      - ⚠️ **Potential Issue:** Are `workflow` and `domain` synonyms, or is this a bug?
      - ⚠️ **NOT VERIFIED:** Contract testing needed to confirm if this causes runtime errors

    **Gap Analysis (Layer 2 - Smart Gates):**
    - ✅ NEEDS_RETRY for environment scaffolding (Section H, DEF-062)
    - ✅ Gate provides fix data (template with environment config)
    - ✅ **CRITICAL:** NEEDS_RETRY requires USER APPROVAL before scaffolding (line 228)
      - Layer 2 (Smart Gates) + Layer 6 (HITL) working together
      - AI must use AskUserQuestion to get approval before adding to config
    - ✅ Idempotent (if environment exists, no scaffolding needed)

    **Gap Analysis (HITL):**
    - ✅ ASK/WAIT pattern for missing requirement
    - ✅ Re-ask on validation failure
    - ✅ Environment approval required (Section H)

    **Decisions:**
    1. **Keep as-is** ✅ - Already integrates Layer 2 + Layer 6 correctly
    2. **Pattern confirmed:** NEEDS_RETRY → AskUserQuestion → Apply → Retry

    **Action Items:**
    - None (protocol already implements HITL + Smart Gates correctly)

- [x] 1.1.3.2 Fix step-02.md (Add Workflow Prompting) ✅ COMPLETE
  - ✅ Updated: Section C (Skill Instruction) - Added workflow identifier prompting with Option 3 explanation
  - ✅ Updated: Section G (Error Handling) - Added workflow missing error template
  - ✅ Updated: Section K (User Communication) - Shows workflow in output format
  - ✅ **BONUS:** File swap executed (step-01 ↔ step-02) to match logical workflow order
  - ✅ Updated: All internal references, gate code (qg_user_input step=1, qg_preflight step=2)
  - ✅ Updated: Audit hook (GATE_TO_STEP, get_audit_filename reads from step_1)
  - ✅ Updated: step-03.md dependencies (now checks Steps 1 AND 2)
  - ✅ Updated: SKILL.md workflow diagram (Step 1: User Input, Step 2: Pre-flight, also fixed "domain"→"workflow")

- [x] 1.1.3.3 Fix qg_user_input.py gate (Validate Workflow Field) ✅ COMPLETE
  - ✅ Verified: Gate already validates workflow field (lines 57, 90-95, 178-182)
  - ✅ No changes needed - workflow validation exists

- [x] 1.1.3.4 Integration Test step-02 (Step 1 in new workflow) ✅ COMPLETE
  - ✅ Test: Triggered workflow with requirement "As a customer, I want to search for a sales representative"
  - ✅ Verify: AI asked for workflow identifier with organizational context (test run/feature/sprint)
  - ✅ Test: Provided workflow="helios5"
  - ✅ Verify: Gate validated and saved workflow correctly
  - ✅ State verified: `tests/_state/2026-01-22T03:43:51.001333Z/workflow_state.json` created with step_1 data
  - ✅ Audit verified: `tests/_audit/audit_log_2026-01-22T03:43:51.001333Z.json` logged step 1 with gate "qg_user_input"
  - ⚠️ Transcript blocked: Gate enforcer blocks writes to `tests/_reports/` (Task 1.1.4 issue)
  - ⏸️ Environment auto-detection: Not tested (requires unknown URL, deferred)
  - **Result:** Protocol guidance verified, state/audit working, transcript deferred to 1.1.4

- [x] 1.1.3.5 HITL Approval - step-02.md (Step 1 Complete) ✅ COMPLETE
  - ✅ Present: Changes to step-02.md (workflow prompting added)
  - ✅ Present: Integration test results (5/6 checks passed, transcript deferred)
  - ✅ User approved: Proceed to Task 1.1.4 (gate enforcer fix)

---

##### 1.1.4 File Swap Aftermath: Gate Enforcer & Construction Gates (Step Number Alignment)

- [x] 1.1.4.1 Read & Assess Gate Enforcer + Construction Gates

    **Assessment (COMPLETE):**
    - File location: `.claude/hooks/qa-gate-enforcer.py`, `.claude/hooks/audit-trail-writer.py`
    - Related gates: `qg_page_object.py`, `qg_task.py`, `qg_role.py`, `qg_test_runner.py`
    - Purpose: Enforce defense-in-depth by blocking writes to framework files until gates pass
    - Current state:
      - **Gate Enforcer:** PROTECTED_PATHS maps framework paths to step numbers:
        ```python
        'framework/pages/': 'step_6',   # POM
        'framework/tasks/': 'step_7',   # Task
        'framework/roles/': 'step_8',   # Role
        'tests/': 'step_9',             # Test
        ```
      - **Audit Hook:** GATE_TO_STEP maps gates to step numbers:
        ```python
        'qg_user_input': 'step_1',      # ✅ Fixed (was step_2)
        'qg_preflight': 'step_2',       # ✅ Fixed (was step_1)
        'qg_page_object': 'step_6',     # ❌ Should be step_4
        'qg_task': 'step_7',            # ❌ Should be step_4
        'qg_role': 'step_8',            # ❌ Should be step_4
        'qg_test_runner': 'step_9',     # ❌ Should be step_4
        ```
      - **Construction Gates:** Save state as step_6/7/8/9:
        ```python
        qg_page_object.py: state_manager.save(step=6, ...)
        qg_task.py: state_manager.save(step=7, ...)
        qg_role.py: state_manager.save(step=8, ...)
        qg_test_runner.py: state_manager.save(step=9, ...)
        ```

    **Gap Analysis (Layer 3 - Hooks + Layer 2 - Gates):**
    - ❌ **11-step workflow assumption:** Gate enforcer references steps 6-9, but 5-step workflow has no steps 6-9
    - ❌ **State mismatch:** Construction gates save to step_6/7/8/9, but Step 4 "Collaborative Construction" should be single step
    - ❌ **Audit trail inconsistency:** Audit hook maps tools to wrong step numbers after file swap
    - ❌ **Enforcement gap:** Gate enforcer won't work (checks step_6-9 which don't exist in 5-step workflow)

    **Gap Analysis (Architecture):**
    - PRD FR-9.1: Step 4 = "Collaborative Construction" (HITL loop)
      - AI builds POMs/Tasks/Roles manually with Edit/Write
      - Gates validate each piece
      - Tools 3-6 available if user requests
    - Question: Should all construction gates save to step_4, or keep sub-steps within step_4?

    **Decisions:**
    1. **Option A (RECOMMENDED): All construction gates save as step_4** ✅
       - State structure: `step_4` with sub-keys:
         ```json
         {
           "step_4": {
             "pom_metadata": {...},     // qg_page_object writes this
             "task_metadata": {...},    // qg_task writes this
             "role_metadata": {...},    // qg_role writes this
             "test_metadata": {...}     // qg_test_runner writes this
           }
         }
         ```
       - **Why:** Clean 5-step architecture, StateManager already handles state accumulation (merges on save)
       - **Gate enforcer:** Check `step_4` exists, then check specific metadata keys
       - **Audit trail:** All construction gates → `step_4`
       - **Defense-in-depth intact:** Layer 3 hooks still enforce, just at correct step

    2. **Option B: Keep step_6/7/8/9 as sub-steps** ❌
       - State would have: `step_1`, `step_2`, `step_3`, `step_4`, `step_6`, `step_7`, `step_8`, `step_9`, `step_5`
       - **Why rejected:** Confusing step order, doesn't reflect 5-step architecture

    3. **Option C: Remove gate enforcer** ❌
       - Pair programming is supervised, no enforcement needed
       - **Why rejected:** Defense-in-depth is core to platform, Layer 3 is non-negotiable

    **Final Decision:** **Option A** - All construction gates save to `step_4` with metadata sub-keys

    **Action Items:**
    - Update 4 construction gates: qg_page_object (step=6→4), qg_task (step=7→4), qg_role (step=8→4), qg_test_runner (step=9→4)
    - Update gate enforcer: PROTECTED_PATHS → all map to 'step_4', update is_gate_passed() to check metadata sub-keys
    - Update audit hook: GATE_TO_STEP → all construction gates map to 'step_4'
    - Update REQUIRED_METADATA: Map to step_4 with sub-key checks

- [x] 1.1.4.2 Fix Construction Gates (Save to step_4) ✅ COMPLETE
  - ✅ Updated qg_page_object.py: Line 463, step=6→4, comment updated to "Step 4 state (POM metadata sub-key)"
  - ✅ Updated qg_task.py: Line 376, step=7→4, comment updated to "Step 4 state (Task metadata sub-key)"
  - ✅ Updated qg_role.py: Line 405, step=8→4, comment updated to "Step 4 state (Role metadata sub-key)"
  - ✅ Updated qg_test_runner.py: Line 407, step=9→4, comment updated to "Step 4 state (Test metadata sub-key)"
  - ✅ All gates now save to step=4 with their respective metadata keys
  - ✅ StateManager.save() merges data (state accumulation pattern preserved)

- [x] 1.1.4.3 Fix Gate Enforcer (Check step_4 with metadata sub-keys) ✅ COMPLETE
  - ✅ Updated PROTECTED_PATHS: All paths now map to 'step_4'
  - ✅ Created PATH_TO_METADATA: Maps file paths to their metadata sub-keys
  - ✅ Added get_required_metadata_key(): Helper function to determine metadata key from file path
  - ✅ Updated is_gate_passed(): Now accepts file_path parameter, checks step_4 with correct metadata sub-key
  - ✅ Updated is_step_10_required(): Changed from step_9 to step_4 with test_metadata check
  - ✅ Updated main() call site: Passes file_path to is_gate_passed()
  - ✅ Updated error messages: Shows correct metadata sub-key for step_4, updated "11-step" → "5-step"
  - ✅ Updated file docstring: Reflects 5-step workflow architecture

- [x] 1.1.4.3b Fix StateManager (State Accumulation Support) ✅ COMPLETE
  - **Issue Found:** StateManager.save() was overwriting step data instead of merging
  - **Impact:** Multiple construction gates saving to step_4 would lose previous metadata
  - ✅ Updated StateManager.save(): Now merges data using dict.update() when step exists
  - ✅ Updated docstring: Documented state accumulation feature
  - ✅ Unit tests created: `test_gate_enforcer_step4.py` (4/4 PASSED)
    - Test: StateManager merges metadata sub-keys ✅
    - Test: Gate enforcer blocks without metadata ✅
    - Test: Gate enforcer allows with correct metadata ✅
    - Test: Gate enforcer checks path-specific metadata ✅
  - ✅ Integration test created: `test_integration_step4.py` (PASSED)
    - Simulated full construction workflow (POM → Task → Role → Test)
    - Verified all 4 metadata keys coexist in step_4
    - Verified gate enforcer allows writes after step_4 complete
  - **Result:** State accumulation working, gate enforcer fully tested

- [x] 1.1.4.4 Fix Audit Hook (Map construction gates to step_4) ✅ COMPLETE
  - ✅ Updated GATE_TO_STEP: All construction gates now map to 'step_4'
    - qg_test_scenarios, qg_discovered_elements, qg_page_object, qg_task, qg_role, qg_test_runner → step_4
    - qg_save_run → step_5 (was step_10)
  - ✅ Updated session marker clearing: Changed from step_10 to step_5 (line 229)
  - ✅ State accumulation handled: Multiple gates write to step_4, audit records each gate separately

- [ ] 1.1.4.5 Full E2E Test (Construction Gates + Audit Hook)
  - ✅ Unit tests complete (4/4 PASSED) - see 1.1.4.3b
  - ✅ Mini integration test complete (PASSED) - see 1.1.4.3b
  - [ ] After 1.1.4.4 complete: Verify audit trail shows all construction gates as step_4
  - [ ] Full workflow test: Run `/qa-workflow-dev` through construction phase
  - [ ] Verify transcript writes work (no longer blocked by gate enforcer)

- [ ] 1.1.4.6 HITL Approval - Gate Enforcer & Construction Gates Aligned
  - Present: All construction gates now save to step_4
  - Present: Gate enforcer checks step_4 with metadata sub-keys
  - Present: Audit trail reflects 5-step workflow
  - Wait: User approval before proceeding to step-03.md

---

##### 1.1.5 step-03.md (AI Processing)

- [x] 1.1.4.1 Read & Assess step-03.md

    **Assessment (COMPLETE):**
    - File location: `.claude/skills/qa-management-layer/references/step-03.md`
    - Purpose: Transform user requirement into structured metadata (BDD scenarios, expected_states, intent)
    - Input: Step 2 output + raw requirement | Output: `bdd_scenarios`, `expected_states`, `intent`
    - Key features:
      - AI creates BDD scenario (Given/When/Then)
      - AI extracts expected_states from "Then" clauses (DD-09)
      - AI determines intent (action verb)
      - Gate: `qg_ai_processing` (POST-only validation)
      - Retry: AI auto-retries on FAIL (max 3 attempts), then HITL escalation
      - Transcript logging: Appends to workflow_transcript.md
    - Rules: DD-03 (metadata context), DD-09 (expected_states from "Then")

    **Data Contract Check:**
    (To be re-assessed)

    **Gap Analysis (Layer 2 - Smart Gates):**
    - ❌ **No NEEDS_RETRY pattern** - Gate only returns PASS/FAIL
    - ❌ **No fix data provided** when validation fails
    - ❌ AI retries blind (gate says "invalid" but doesn't teach how to fix)
    - After 3 failures: escalates to user (HITL backstop)

    **Potential Layer 2 Enhancement:**
    If gate could provide fix data on FAIL:
    - "Missing expected_states → Extract from 'Then' clauses"
    - "Invalid BDD structure → Given/When/Then required"
    - "Missing intent → Extract action verb from requirement"
    This would help AI succeed before exhausting retries.

    **Gap Analysis (HITL):**
    - ✅ After 3 failures, user decides (lines 125-143)
    - ✅ Two options: clarify requirement OR abort
    - ✅ No "proceed with incomplete" option (line 145)

    **Decisions:**
    1. **Layer 2 Gap Identified** ⚠️ - Gate could teach instead of just rejecting
    2. **Pattern difference:** Auto-retry (step-03) vs User approval (step-02 NEEDS_RETRY)

    **Action Items:**
    - Consider: Add NEEDS_RETRY to `qg_ai_processing` for fix guidance (Layer 2 enhancement)

- [ ] 1.1.4.2 Decide: Add NEEDS_RETRY to step-03?
  - **HITL Decision Point:** Should qg_ai_processing provide fix data instead of blind retry?
  - Option 1: Add NEEDS_RETRY (Smart Gate teaches how to fix BDD/expected_states/intent)
  - Option 2: Keep as-is (3 blind retries, then user escalation)
  - Wait: User decision

- [ ] 1.1.4.3 Fix qg_ai_processing.py (if Option 1 chosen)
  - Add: NEEDS_RETRY response with fix data for common failures
  - Add: Fix hints for missing expected_states, invalid BDD structure, missing intent
  - Update: Protocol step-03.md to document new NEEDS_RETRY behavior

- [ ] 1.1.4.4 Integration Test step-03
  - Test: Run step-03 with valid requirement
  - Verify: BDD scenarios, expected_states, intent generated correctly
  - Test: Run step-03 with invalid/missing data
  - Verify: Gate provides fix guidance (if NEEDS_RETRY added) or rejects cleanly

- [ ] 1.1.4.5 HITL Approval - step-03.md
  - Present: Changes (or validation if no changes)
  - Wait: User approval before proceeding to step-04.md

---

##### 1.1.5 step-04.md through step-11.md (Remaining Protocol Files)

**Pattern:** For each remaining file: Read → Assess → Fix → Test → HITL approval

- [ ] 1.1.5.1 Read & Assess step-04.md (Generate Tests - Tool 1)
- [ ] 1.1.5.2 Fix step-04.md (if needed)
- [ ] 1.1.5.3 Integration Test step-04
- [ ] 1.1.5.4 HITL Approval - step-04.md

- [ ] 1.1.5.5 Read & Assess step-05.md (Discover Elements - Tool 2)
- [ ] 1.1.5.6 Fix step-05.md (if needed)
- [ ] 1.1.5.7 Integration Test step-05
- [ ] 1.1.5.8 HITL Approval - step-05.md

- [ ] 1.1.5.9 Read & Assess step-06.md (Generate POM - Tool 3)
- [ ] 1.1.5.10 Fix step-06.md (if needed)
- [ ] 1.1.5.11 Integration Test step-06
- [ ] 1.1.5.12 HITL Approval - step-06.md

- [ ] 1.1.5.13 Read & Assess step-07.md (Generate Task - Tool 4)
- [ ] 1.1.5.14 Fix step-07.md (if needed)
- [ ] 1.1.5.15 Integration Test step-07
- [ ] 1.1.5.16 HITL Approval - step-07.md

- [ ] 1.1.5.17 Read & Assess step-08.md (Generate Role - Tool 5)
- [ ] 1.1.5.18 Fix step-08.md (if needed)
- [ ] 1.1.5.19 Integration Test step-08
- [ ] 1.1.5.20 HITL Approval - step-08.md

- [ ] 1.1.5.21 Read & Assess step-09.md (Generate Test Runner - Tool 6)
- [ ] 1.1.5.22 Fix step-09.md (if needed)
- [ ] 1.1.5.23 Integration Test step-09
- [ ] 1.1.5.24 HITL Approval - step-09.md

- [ ] 1.1.5.25 Read & Assess step-10.md (Validation)
- [ ] 1.1.5.26 Fix step-10.md (if needed)
- [ ] 1.1.5.27 Integration Test step-10
- [ ] 1.1.5.28 HITL Approval - step-10.md

- [ ] 1.1.5.29 Read & Assess step-11.md (Execution & Validation)
- [ ] 1.1.5.30 Fix step-11.md (if needed)
- [ ] 1.1.5.31 Integration Test step-11
- [ ] 1.1.5.32 HITL Approval - step-11.md

##### 1.1.6 protocol-environment.md

- [ ] 1.1.6.1 Read & Assess protocol-environment.md
- [ ] 1.1.6.2 Fix protocol-environment.md (if needed)
- [ ] 1.1.6.3 Integration Test protocol-environment
- [ ] 1.1.6.4 HITL Approval - protocol-environment.md

##### 1.1.7 user-communication-protocol.md

- [ ] 1.1.7.1 Read & Assess user-communication-protocol.md
- [ ] 1.1.7.2 Fix user-communication-protocol.md (if needed)
- [ ] 1.1.7.3 Integration Test user-communication
- [ ] 1.1.7.4 HITL Approval - user-communication-protocol.md

---

#### Phase 1.2: Data Contract Validation (DD-26) - SEPARATE TASK FOR SRP

**Purpose:** Validate schema consistency across steps (Step N output → Step N+1 input contracts)

**Pattern:** Validate contract → Fix if broken → Integration test → HITL approval

##### 1.2.1 Step 1→2 Contract

- [ ] 1.2.1.1 Validate Step 1→2 contract
  - Check: Step 1 outputs credential_strategy, test_data_location
  - Check: Step 2 expects credential_strategy, test_data_location (PRE-CHECK)
  - Check: StateManager preserves Step 1 data in `step_1` key
  - Check: Step 2 can access Step 1 data via `state_manager.get_step(1)`
  - Result: ✅ Valid / ❌ Broken

- [ ] 1.2.1.2 Fix Step 1→2 contract (if broken)
- [ ] 1.2.1.3 Integration Test Step 1→2
- [ ] 1.2.1.4 HITL Approval - Step 1→2 contract

##### 1.2.2 Step 2→3 Contract

- [ ] 1.2.2.1 Validate Step 2→3 contract
  - Check: Step 2 outputs persona, URL, role_name, **workflow**, raw_requirement
  - Check: Step 3 expects persona, URL, role_name, **domain**, raw_requirement
  - **ISSUE FOUND:** Field name mismatch (workflow vs domain)
  - Result: ❌ Broken - Field name inconsistency

- [ ] 1.2.2.2 Fix Step 2→3 contract
  - Option 1: Rename Step 2 output from `workflow` to `domain`
  - Option 2: Rename Step 3 input from `domain` to `workflow`
  - Option 3: Verify they are synonyms and document in both protocols
  - **HITL Decision Point:** Choose fix approach

- [ ] 1.2.2.3 Integration Test Step 2→3
- [ ] 1.2.2.4 HITL Approval - Step 2→3 contract

##### 1.2.3 Step 3→4 through Step 10→11 Contracts

- [ ] 1.2.3.1 Validate Step 3→4 contract
- [ ] 1.2.3.2 Fix Step 3→4 (if broken)
- [ ] 1.2.3.3 Integration Test Step 3→4
- [ ] 1.2.3.4 HITL Approval - Step 3→4

- [ ] 1.2.3.5 Validate Step 4→5 contract
- [ ] 1.2.3.6 Fix Step 4→5 (if broken)
- [ ] 1.2.3.7 Integration Test Step 4→5
- [ ] 1.2.3.8 HITL Approval - Step 4→5

- [ ] 1.2.3.9 Validate Step 5→6 contract
- [ ] 1.2.3.10 Fix Step 5→6 (if broken)
- [ ] 1.2.3.11 Integration Test Step 5→6
- [ ] 1.2.3.12 HITL Approval - Step 5→6

- [ ] 1.2.3.13 Validate Step 6→7 contract
- [ ] 1.2.3.14 Fix Step 6→7 (if broken)
- [ ] 1.2.3.15 Integration Test Step 6→7
- [ ] 1.2.3.16 HITL Approval - Step 6→7

- [ ] 1.2.3.17 Validate Step 7→8 contract
- [ ] 1.2.3.18 Fix Step 7→8 (if broken)
- [ ] 1.2.3.19 Integration Test Step 7→8
- [ ] 1.2.3.20 HITL Approval - Step 7→8

- [ ] 1.2.3.21 Validate Step 8→9 contract
- [ ] 1.2.3.22 Fix Step 8→9 (if broken)
- [ ] 1.2.3.23 Integration Test Step 8→9
- [ ] 1.2.3.24 HITL Approval - Step 8→9

- [ ] 1.2.3.25 Validate Step 9→10 contract
- [ ] 1.2.3.26 Fix Step 9→10 (if broken)
- [ ] 1.2.3.27 Integration Test Step 9→10
- [ ] 1.2.3.28 HITL Approval - Step 9→10

- [ ] 1.2.3.29 Validate Step 10→11 contract
- [ ] 1.2.3.30 Fix Step 10→11 (if broken)
- [ ] 1.2.3.31 Integration Test Step 10→11
- [ ] 1.2.3.32 HITL Approval - Step 10→11

---

#### Phase 1.3: New Protocol Files (Gap-Fill)

**Purpose:** Create new protocol files based on gaps identified in Phase 1.1

**NOTE:** This phase only executes if gaps are found. If protocols are complete, skip to Phase 2.

- [ ] 1.3.1 Create collaboration-patterns.md (if needed based on Phase 1.1 gaps)
  - Add: Stop-When-Blocked patterns
  - Add: Build-As-You-Go patterns
  - Add: HITL trigger patterns
  - Add: Code pattern requirements (reference FRAMEWORK.md)
  - Add: Configuration requirements

- [ ] 1.3.2 HITL Approval - Phase 1 Complete
  - Present: All protocol fixes + data contract fixes + new files (if any)
  - Wait: User approval before proceeding to Phase 2 (Smart Gates)

---

### 2.0 Enhance Smart Gates to Teach Fixes (Layer 2 Defense) [CORE]

- [ ] 2.1.1 Read all existing gate implementations (SEQUENTIAL with HITL checkpoints)
  - [ ] 2.1.1.1 Read qg_page_object.py → STOP for approval

    **Assessment:**
    (To be filled)

    **Gap Analysis:**
    (To be filled)

    **Decisions:**
    (To be filled)

    **Action Items:**
    (To be filled)

  - [ ] 2.1.1.2 Read qg_task.py → STOP for approval

    **Assessment:**
    (To be filled)

    **Gap Analysis:**
    (To be filled)

    **Decisions:**
    (To be filled)

    **Action Items:**
    (To be filled)

  - [ ] 2.1.1.3 Read qg_role.py → STOP for approval

    **Assessment:**
    (To be filled)

    **Gap Analysis:**
    (To be filled)

    **Decisions:**
    (To be filled)

    **Action Items:**
    (To be filled)

  - [ ] 2.1.1.4 Read qg_test_runner.py → STOP for approval

    **Assessment:**
    (To be filled)

    **Gap Analysis:**
    (To be filled)

    **Decisions:**
    (To be filled)

    **Action Items:**
    (To be filled)

  - [ ] 2.1.1.5 Read qg_save_run.py → STOP for approval

    **Assessment:**
    (To be filled)

    **Gap Analysis:**
    (To be filled)

    **Decisions:**
    (To be filled)

    **Action Items:**
    (To be filled)

  - [ ] 2.1.1.6 Read other gates (qg_preflight, qg_user_input, qg_discovered_elements) → STOP for approval

    **Assessment:**
    (To be filled)

    **Gap Analysis:**
    (To be filled)

    **Decisions:**
    (To be filled)

    **Action Items:**
    (To be filled)

  - [ ] 2.1.1.7 Compile complete gate inventory

- [ ] 2.1.2 **HITL CHECKPOINT:** Review gate inventory
  - Present: List of all gates found + brief summary of each
  - Ask: "Gates read. Proceed to code pattern validation?"

- [ ] 2.1.3 Validate code pattern validation against FRAMEWORK.md
  - Check POM validation: Locators as class constants? Atomic methods return self? NO decorators? Composition?
  - Check Task validation: Composes POMs? @autologger? Returns None? NO locators (DD-27)?
  - Check Role validation: Composes Tasks? @autologger? Returns None (not values)?
  - Check Test validation: Calls ONE role method? Asserts via POM state-checks? NOT return values?
  - Check Cross-layer validation: No inheritance? No locators outside POMs?
  - Document: Each gate's coverage (what's validated, what's missed)

- [ ] 2.1.4 **HITL CHECKPOINT:** Review pattern validation coverage
  - Present: Pattern validation findings (what each gate checks, gaps identified)
  - Ask: "Pattern validation analysis complete. Proceed to teach vs block analysis?"

- [ ] 2.1.5 Identify TEACH vs BLOCK gaps
  - Which gates BLOCK but don't TEACH?
  - Which violations provide error message but no fix guidance?
  - Which gates catch violations but don't reference FRAMEWORK.md patterns?
  - Document: Complete list of teaching gaps

- [ ] 2.1.6 **HITL CHECKPOINT:** Review teaching gaps
  - Present: Teaching capability gaps (gates that need enhancement)
  - Ask: "Teaching gaps identified. Proceed to create assessment report?"

- [ ] 2.1.7 Create assessment report
  - Create: `docs/projects/pair-programming/assessment-layer2-gates.md`
  - Section 1: Current validation coverage (what's checked, what's missed)
  - Section 2: Code pattern validation gaps
  - Section 3: Teaching capability gaps (block-only vs teach fixes)
  - Section 4: Recommended enhancements (prioritized)

- [ ] 2.1.8 **HITL CHECKPOINT:** Review assessment report
  - Present: Complete assessment report
  - Ask: "Assessment complete. Approve recommended enhancements and proceed to implementation?"

---

#### Phase 2.2: IMPLEMENT - Create gate_utils.py

- [ ] 2.2.1 Create gate_utils.py structure
  - Create file: `mcp_server/tools/gates/gate_utils.py`
  - Define function signature: `generate_fix_data(violation_type, context) -> dict`
  - Add docstring explaining purpose

- [ ] 2.2.2 **HITL CHECKPOINT:** Review gate_utils.py structure
  - Present: File structure and function signature
  - Ask: "gate_utils.py structure created. Proceed to implement DD-27 fix generator?"

- [ ] 2.2.3 Implement DD-27 violation fix data generator
  - Add logic for DD-27 (locators in Task)
  - Returns: Error message + fix guidance + code example + FRAMEWORK.md reference
  - Code example shows moving locators to POM as class constants

- [ ] 2.2.4 **HITL CHECKPOINT:** Review DD-27 fix generator
  - Present: DD-27 fix generator code
  - Ask: "DD-27 fix generator complete. Proceed to DD-25?"

- [ ] 2.2.5 Implement DD-25 violation fix data generator
  - Add logic for DD-25 (skeleton code)
  - Returns: Complete method signatures from FRAMEWORK.md

- [ ] 2.2.6 **HITL CHECKPOINT:** Review DD-25 fix generator
  - Present: DD-25 fix generator code
  - Ask: "DD-25 fix generator complete. Proceed to return pattern violations?"

- [ ] 2.2.7 Implement return pattern violation fix generator
  - Add logic for Task/Role returning values (should return None)
  - Returns: Correct pattern + FRAMEWORK.md reference

- [ ] 2.2.8 **HITL CHECKPOINT:** Review return pattern fix generator
  - Present: Return pattern fix generator code
  - Ask: "Return pattern fix generator complete. Proceed to composition violations?"

- [ ] 2.2.9 Implement composition violation fix generator
  - Add logic for inheritance detection (should use composition)
  - Returns: Composition pattern example

- [ ] 2.2.10 **HITL CHECKPOINT:** Review composition fix generator
  - Present: Composition fix generator code
  - Ask: "Composition fix generator complete. Proceed to decorator violations?"

- [ ] 2.2.11 Implement decorator violation fix generator
  - Add logic for decorator placement violations
  - Returns: Correct decorator usage pattern

- [ ] 2.2.12 **HITL CHECKPOINT:** Review complete gate_utils.py
  - Present: Full gate_utils.py code
  - Ask: "gate_utils.py complete with all fix generators. Proceed to gate enhancement phase?"

---

#### Phase 2.3: ENHANCE - Update Each Gate

- [ ] 2.3.1 Update qg_page_object.py
  - Add validation: Locators as class constants
  - Add validation: Atomic methods return self
  - Add validation: NO @autologger decorators
  - Add validation: Composition (no inheritance)
  - Add: Call gate_utils.generate_fix_data() on violations
  - Add: HITL trigger with fix data

- [ ] 2.3.2 **HITL CHECKPOINT:** Review qg_page_object.py changes
  - Present: Diff of qg_page_object.py changes
  - Ask: "qg_page_object.py enhanced. Proceed to qg_task.py?"

- [ ] 2.3.3 Update qg_task.py (DD-27 CRITICAL)
  - **CRITICAL: Add validation for NO locators in Task code (DD-27)**
  - Add validation: Composes POMs in __init__
  - Add validation: @autologger decorator on methods (NOT __init__)
  - Add validation: Methods return None (not values)
  - Add: Call generate_fix_data() with code examples
  - Add: HITL trigger

- [ ] 2.3.4 **HITL CHECKPOINT:** Review qg_task.py changes (CRITICAL)
  - Present: Diff of qg_task.py changes
  - Emphasize: DD-27 locator detection is CRITICAL
  - Ask: "qg_task.py enhanced with DD-27 enforcement. Proceed to qg_role.py?"

- [ ] 2.3.5 Update qg_role.py
  - Add validation: Composes Tasks in __init__
  - Add validation: @autologger decorator on methods
  - Add validation: Methods return None (orchestrate, don't return)
  - Add: Call generate_fix_data() on violations
  - Add: HITL trigger with pattern references

- [ ] 2.3.6 **HITL CHECKPOINT:** Review qg_role.py changes
  - Present: Diff of qg_role.py changes
  - Ask: "qg_role.py enhanced. Proceed to qg_test_runner.py?"

- [ ] 2.3.7 Update qg_test_runner.py
  - Add validation: Test calls ONE role workflow method
  - Add validation: Test asserts via POM state-check methods (NOT return values)
  - Add validation: AAA pattern (Arrange, Act, Assert)
  - Add: Call generate_fix_data() with test pattern examples
  - Add: HITL trigger

- [ ] 2.3.8 **HITL CHECKPOINT:** Review qg_test_runner.py changes
  - Present: Diff of qg_test_runner.py changes
  - Ask: "qg_test_runner.py enhanced. Proceed to qg_save_run.py?"

- [ ] 2.3.9 Update qg_save_run.py
  - Add validation: All code follows patterns (final check before save)
  - Add: Block save on violations
  - Add: Force HITL with comprehensive fix data

- [ ] 2.3.10 **HITL CHECKPOINT:** Review qg_save_run.py changes
  - Present: Diff of qg_save_run.py changes
  - Ask: "qg_save_run.py enhanced. All gates updated. Proceed to validation phase?"

---

#### Phase 2.4: VALIDATION - Test Gate Teaching

- [ ] 2.4.1 Write unit tests
  - Create: `mcp_server/_dev_tests/test_gates/test_smart_gates_teach.py`
  - Test: DD-27 violation (locator in Task) → Fix data with code example
  - Test: Return pattern violation → Fix data references FRAMEWORK.md
  - Test: Composition violation → Fix data shows correct composition
  - Test: Decorator violation → Fix data shows correct placement
  - Test: Gate signals HITL with fix data
  - Test: Fix data is actionable
  - Test: Fix data references FRAMEWORK.md section

- [ ] 2.4.2 **HITL CHECKPOINT:** Review unit test code
  - Present: Unit test code
  - Ask: "Unit tests written. Run tests?"

- [ ] 2.4.3 Run unit tests
  - Execute: `pytest mcp_server/_dev_tests/test_gates/test_smart_gates_teach.py -v`
  - Capture results

- [ ] 2.4.4 **HITL CHECKPOINT:** Review unit test results
  - Present: Test output (pass/fail + details)
  - If FAIL: Fix issues, re-run, get approval
  - If PASS: Ask "Unit tests pass. Proceed to integration tests?"

- [ ] 2.4.5 Write integration test
  - Create: `mcp_server/_dev_tests/test_workflow_integration/test_gate_protocol_integration.py`
  - Test: Protocol guides (Layer 1) → Gate validates (Layer 2)
  - Test: Gate catches pattern violation Protocol didn't prevent
  - Test: Gate teaches correct fix to AI (with code example)

- [ ] 2.4.6 **HITL CHECKPOINT:** Review integration test code
  - Present: Integration test code
  - Ask: "Integration test written. Run test?"

- [ ] 2.4.7 Run integration test
  - Execute: `pytest mcp_server/_dev_tests/test_workflow_integration/test_gate_protocol_integration.py -v`
  - Capture results

- [ ] 2.4.8 **HITL CHECKPOINT:** Review integration test results
  - Present: Test output
  - If FAIL: Fix issues, re-run, get approval
  - If PASS: Ask "Integration test passes. Proceed to final audit?"

- [ ] 2.4.9 Final audit
  - **Audit: Gates validate ALL code patterns (4-layer architecture)**
  - **Audit: Gates teach correct fixes (actionable + FRAMEWORK.md references)**
  - **Audit: Gates signal HITL reliably (Layer 6 integration)**
  - Record results in assessment report

- [ ] 2.4.10 **HITL CHECKPOINT:** Review audit results
  - Present: Audit findings
  - Ask: "Layer 2 audit complete. Approve and proceed to commit?"

---

#### Phase 2.5: COMMIT

- [ ] 2.5.1 Prepare commit
  - Stage all changes
  - Review git diff

- [ ] 2.5.2 **HITL CHECKPOINT:** Review commit diff
  - Present: Complete diff of all changes
  - Ask: "Review changes. Approve commit?"

- [ ] 2.5.3 Commit changes
  - Commit message: `feat: Smart Gates validate patterns and teach fixes (Task 2.0)`
  - Body: Include assessment report summary, list all enhanced gates
  - Note: Code pattern validation + teaching fixes + HITL integration

**Done When:**
- ✅ Assessment report created (validation coverage + teaching gaps identified)
- ✅ gate_utils.py created with fix generators for all pattern violations
- ✅ All gates enhanced (qg_page_object, qg_task, qg_role, qg_test_runner, qg_save_run)
- ✅ **Smart Gates validate ALL code pattern correctness (4-layer architecture, composition, returns, locators, decorators)**
- ✅ **Smart Gates teach correct fixes (actionable guidance + code examples from FRAMEWORK.md)**
- ✅ Tests pass (unit + integration)
- ✅ Gates signal HITL with fix data (not just block)
- ✅ Integration test shows Protocol + Gate working together (Layers 1 + 2 defense)
- ✅ Fix data references FRAMEWORK.md (traceability)
- ✅ Committed with user approval

---

### 3.0 Implement Timeout Monitoring (Layer 3 Defense) [CORE]

**EATING OUR DOGFOOD:** Use HITL pattern (stop-when-blocked) while building timeout monitoring. After each step, STOP and get user approval before proceeding.

---

#### Phase 3.1: ASSESSMENT - Audit Existing Hooks

- [ ] 3.1.1 List all existing hooks

  **Assessment:**
  - Check directory: `.claude/hooks/`
  - List: All existing hook files (PreToolUse, PostToolUse, etc.)
  - Document: What each hook currently does
  (To be filled after reading)

  **Gap Analysis:**
  (To be filled - what's missing for pair programming?)

  **Decisions:**
  (To be filled - how to resolve gaps?)

  **Action Items:**
  (To be filled - what to do in Phase 3.2/3.3?)

- [ ] 3.1.2 **HITL CHECKPOINT:** Review hook inventory
  - Present: List of existing hooks + brief summary
  - Ask: "Hooks inventoried. Proceed to capabilities analysis?"

- [ ] 3.1.3 Document current monitoring capabilities
  - Check: What execution monitoring exists?
  - Check: What failure tracking exists?
  - Check: What HITL trigger mechanisms exist?
  - Document: Current capabilities

- [ ] 3.1.4 **HITL CHECKPOINT:** Review current capabilities
  - Present: Current monitoring capabilities
  - Ask: "Current capabilities documented. Proceed to gap identification?"

- [ ] 3.1.5 Identify gaps for timeout/loop detection
  - Missing: Timeout monitoring for tool execution?
  - Missing: Rambling detection (3+ failures, same fix twice)?
  - Missing: Configurable threshold support?
  - Missing: HITL trigger integration?
  - Document: Complete list of gaps

- [ ] 3.1.6 **HITL CHECKPOINT:** Review monitoring gaps
  - Present: Timeout/loop detection gaps
  - Ask: "Gaps identified. Proceed to create assessment report?"

- [ ] 3.1.7 Create assessment report
  - Create: `docs/projects/pair-programming/assessment-layer3-hooks.md`
  - Section 1: Existing hooks inventory
  - Section 2: Current monitoring capabilities
  - Section 3: Monitoring gaps (timeout, loop detection)
  - Section 4: HITL trigger integration requirements
  - Section 5: Recommended implementations

- [ ] 3.1.8 **HITL CHECKPOINT:** Review assessment report
  - Present: Complete assessment report
  - Ask: "Assessment complete. Approve recommended implementations and proceed to timeout monitoring?"

---

#### Phase 3.2: IMPLEMENT - Timeout Monitoring Hook

- [ ] 3.2.1 Create timeout monitoring hook file
  - Create: `.claude/hooks/timeout_monitor.sh` (or appropriate format)
  - Hook type: PostToolUse
  - Add: Read config from environment_config.json

- [ ] 3.2.2 **HITL CHECKPOINT:** Review hook structure
  - Present: Hook file structure
  - Ask: "Hook file created. Proceed to implement timeout logic?"

- [ ] 3.2.3 Implement timeout detection logic
  - Add: Track tool execution duration
  - Add: Read threshold from config (default 30s)
  - Add: Compare actual duration vs threshold
  - Add: If exceeded → prepare HITL trigger

- [ ] 3.2.4 **HITL CHECKPOINT:** Review timeout detection
  - Present: Timeout detection code
  - Ask: "Timeout detection implemented. Proceed to HITL trigger integration?"

- [ ] 3.2.5 Implement HITL trigger on timeout
  - Add: Force HITL trigger when threshold exceeded
  - Add: Return blocker signal: "Timeout at Xs. Continue or change approach?"
  - Add: Provide context (which action, how long)

- [ ] 3.2.6 **HITL CHECKPOINT:** Review complete timeout monitoring hook
  - Present: Complete timeout monitoring hook code
  - Ask: "Timeout monitoring hook complete. Proceed to rambling detection?"

---

#### Phase 3.3: IMPLEMENT - Rambling Detection Hook

- [ ] 3.3.1 Create rambling detection hook file
  - Create: `.claude/hooks/rambling_detector.sh` (or appropriate format)
  - Hook type: PostToolUse
  - Add: Initialize failure tracking

- [ ] 3.3.2 **HITL CHECKPOINT:** Review hook structure
  - Present: Hook file structure
  - Ask: "Rambling detection hook created. Proceed to failure tracking?"

- [ ] 3.3.3 Implement failure tracking logic
  - Add: Track consecutive failures
  - Add: Track fix attempts (detect same fix twice)
  - Add: Increment counters

- [ ] 3.3.4 **HITL CHECKPOINT:** Review failure tracking
  - Present: Failure tracking code
  - Ask: "Failure tracking implemented. Proceed to loop detection?"

- [ ] 3.3.5 Implement loop detection and HITL trigger
  - Add: If 3+ sequential failures → Force HITL trigger
  - Add: If same fix attempted twice → Force HITL trigger
  - Add: Return blocker signal: "Loop detected. User guidance needed."

- [ ] 3.3.6 **HITL CHECKPOINT:** Review complete rambling detection hook
  - Present: Complete rambling detection hook code
  - Ask: "Rambling detection hook complete. Proceed to configuration?"

---

#### Phase 3.4: CONFIGURE - Update Environment Config

- [ ] 3.4.1 Update environment_config.json
  - Open: `framework/resources/config/environment_config.json`
  - Add timeout_monitoring section:
    ```json
    "timeout_monitoring": {
      "enabled": true,
      "threshold_seconds": 30,
      "actions": ["browser_navigate", "element_wait", "ajax_call"]
    }
    ```

- [ ] 3.4.2 **HITL CHECKPOINT:** Review configuration
  - Present: Configuration changes
  - Ask: "Configuration updated. Proceed to validation phase?"

---

#### Phase 3.5: VALIDATION - Test Timeout/Loop Detection

- [ ] 3.5.1 Write unit tests
  - Create: `mcp_server/_dev_tests/test_workflow_integration/test_timeout_monitoring.py`
  - Test: Action exceeds threshold → HITL triggered
  - Test: 3+ sequential failures → HITL triggered
  - Test: Same fix twice → HITL triggered
  - Test: Configurable threshold works
  - Test: Enable/disable toggle works

- [ ] 3.5.2 **HITL CHECKPOINT:** Review unit test code
  - Present: Unit test code
  - Ask: "Unit tests written. Run tests?"

- [ ] 3.5.3 Run unit tests
  - Execute: `pytest mcp_server/_dev_tests/test_workflow_integration/test_timeout_monitoring.py -v`
  - Capture results

- [ ] 3.5.4 **HITL CHECKPOINT:** Review unit test results
  - Present: Test output
  - If FAIL: Fix issues, re-run, get approval
  - If PASS: Ask "Unit tests pass. Proceed to integration tests?"

- [ ] 3.5.5 Write integration test
  - Create: `test_hook_gate_integration.py`
  - Test: Protocol guides → Gate validates → Hook monitors (3-layer defense)
  - Test: Gate misses violation → Hook catches (timeout/loop)
  - Test: Hook forces HITL trigger reliably

- [ ] 3.5.6 **HITL CHECKPOINT:** Review integration test code
  - Present: Integration test code
  - Ask: "Integration test written. Run test?"

- [ ] 3.5.7 Run integration test
  - Execute test
  - Capture results

- [ ] 3.5.8 **HITL CHECKPOINT:** Review integration test results
  - Present: Test output
  - If FAIL: Fix issues, re-run, get approval
  - If PASS: Ask "Integration test passes. Proceed to final audit?"

- [ ] 3.5.9 Final audit
  - **Audit: Hooks monitor execution and force HITL (Layer 3 defense)**
  - **Audit: Timeout monitoring works with configurable threshold**
  - **Audit: Rambling detection catches loops**
  - Record results in assessment report

- [ ] 3.5.10 **HITL CHECKPOINT:** Review audit results
  - Present: Audit findings
  - Ask: "Layer 3 audit complete. Approve and proceed to commit?"

---

#### Phase 3.6: COMMIT

- [ ] 3.6.1 Prepare commit
  - Stage all changes
  - Review git diff

- [ ] 3.6.2 **HITL CHECKPOINT:** Review commit diff
  - Present: Complete diff
  - Ask: "Review changes. Approve commit?"

- [ ] 3.6.3 Commit changes
  - Commit message: `feat: Implement timeout monitoring and rambling detection (Task 3.0)`
  - Body: Include assessment report summary, note Layer 3 defense operational

**Done When:**
- ✅ Assessment report created (existing hooks + gaps identified)
- ✅ Timeout monitoring hook implemented (configurable threshold, HITL trigger)
- ✅ Rambling detection hook implemented (3+ failures, same fix twice detection)
- ✅ Configuration updated (timeout_monitoring section)
- ✅ Tests pass (unit + integration)
- ✅ Integration test shows Protocol + Gate + Hook working together (3-layer defense)
- ✅ Committed with user approval
  - Create `mcp_server/tools/gates/gate_utils.py`
  - Function: `generate_fix_data(violation_type, context) -> dict`
    - **DD-27 violation (locators in Task):**
      - Returns: "Move locators to POM as class constants: `self.pom.LOCATOR_NAME = (By.CSS_SELECTOR, 'selector')`"
      - Include: Code example from FRAMEWORK.md
    - **DD-25 violation (skeleton code):**
      - Returns: "Complete skeleton code: [specific methods needed with signatures]"
      - Include: Method signatures from FRAMEWORK.md
    - **Return pattern violation (Task/Role returns value):**
      - Returns: "Task/Role methods MUST return None. Tests assert via POM state-check methods. See FRAMEWORK.md Section 4."
      - Include: Correct pattern example
    - **Composition violation (inheritance used):**
      - Returns: "Use composition, not inheritance. Compose POMs in Task __init__, compose Tasks in Role __init__."
      - Include: Correct pattern example
    - **Decorator violation (missing @autologger or wrong layer):**
      - Returns: "Tasks/Roles need @autologger decorator. POMs do NOT use decorators."
      - Include: Correct pattern example
  - Returns structured fix data with:
    - `violation_type`: str
    - `error_message`: str (what's wrong)
    - `fix_guidance`: str (how to fix)
    - `code_example`: str (correct pattern from FRAMEWORK.md)
    - `reference`: str (FRAMEWORK.md section or DD number)

- [ ] 2.3 ENHANCE: Update all gates to validate code patterns AND teach fixes
  - Update `qg_page_object.py` (PRE/POST validation)
    - Validate: Locators as class constants
    - Validate: Atomic methods return self
    - Validate: NO @autologger decorators
    - Validate: Composition (no inheritance from BasePage)
    - On violation: Call `gate_utils.generate_fix_data()` → Return fix data + HITL trigger
  - Update `qg_task.py` (PRE/POST validation)
    - **CRITICAL: Validate NO locators in Task code (DD-27)**
    - Validate: Composes POMs in __init__
    - Validate: @autologger decorator on methods (NOT on __init__)
    - Validate: Methods return None (not values)
    - On violation: Call `generate_fix_data()` → Return actionable fix + code example
  - Update `qg_role.py` (PRE/POST validation)
    - Validate: Composes Tasks in __init__
    - Validate: @autologger decorator on methods
    - Validate: Methods return None (orchestrate, don't return)
    - On violation: Call `generate_fix_data()` → Return fix + pattern reference
  - Update `qg_test_runner.py` (PRE/POST validation)
    - Validate: Test calls ONE role workflow method
    - Validate: Test asserts via POM state-check methods (NOT role.method() return values)
    - Validate: AAA pattern (Arrange, Act, Assert)
    - On violation: Call `generate_fix_data()` → Return correct test pattern
  - Update `qg_save_run.py` (Step 10 PRE validation)
    - Validate: All code follows patterns (final check before save)
    - On violation: Block save, force HITL with comprehensive fix data

- [ ] 2.4 VALIDATION: Write comprehensive tests for gate validation AND teaching
  - Write unit tests: `test_smart_gates_teach.py` in `mcp_server/_dev_tests/test_gates/`
    - **Test: DD-27 violation (locator in Task) → Fix data with code example**
    - **Test: Return pattern violation (Task returns value) → Fix data references FRAMEWORK.md**
    - **Test: Composition violation (inheritance used) → Fix data shows correct composition**
    - **Test: Decorator violation → Fix data shows correct decorator placement**
    - Test: Gate signals HITL with fix data (not just error)
    - Test: Fix data is actionable (contains specific guidance + code example)
    - **Test: Fix data references FRAMEWORK.md section (traceability)**
  - Write integration test: `test_gate_protocol_integration.py`
    - Test: Protocol guides (Layer 1) → Gate validates (Layer 2)
    - Test: Gate catches pattern violation Protocol didn't prevent
    - Test: Gate teaches correct fix to AI (with code example)
  - Run checks (lint, tests)
  - **Audit: Verify gates validate ALL code patterns (4-layer architecture)**
  - **Audit: Verify gates teach correct fixes (actionable + references FRAMEWORK.md)**
  - **Audit: Verify gates signal HITL reliably (Layer 6 integration)**
  - Record results

- [ ] 2.5 Commit: `feat: Smart Gates validate patterns and teach fixes (Task 2.0)`
  - Include assessment report in commit
  - List all enhanced gates
  - Note: Code pattern validation + teaching fixes

**Done When:**
- ✅ Assessment report created (validation coverage + teaching gaps identified)
- ✅ **Smart Gates validate ALL code pattern correctness (4-layer architecture, composition, returns, locators, decorators)**
- ✅ **Smart Gates teach correct fixes (actionable guidance + code examples from FRAMEWORK.md)**
- ✅ Gates signal HITL with fix data (not just block)
- ✅ Tests pass (validation + teaching behavior confirmed)
- ✅ Integration test shows Protocol + Gate working together (Layers 1 + 2 defense)
- ✅ Fix data references FRAMEWORK.md (traceability to authoritative source)

---

### 3.0 Implement Timeout Monitoring (Layer 3 Defense) [CORE]

- [ ] 3.1 ASSESSMENT: Audit existing hooks and identify monitoring gaps
  - **Check existing hooks in `.claude/hooks/`:**
    - List all existing hooks (PreToolUse, PostToolUse, etc.)
    - Document current monitoring capabilities
  - **Identify gaps for timeout/loop detection:**
    - Missing timeout monitoring for tool execution?
    - Missing rambling detection (3+ failures, same fix twice)?
    - Missing HITL trigger mechanism?
  - **Document assessment:** Create `docs/projects/pair-programming/assessment-layer3-hooks.md`
    - Section 1: Existing hooks inventory
    - Section 2: Monitoring gaps
    - Section 3: HITL trigger integration requirements

- [ ] 3.2 IMPLEMENT: Timeout monitoring hook
  - Create timeout monitoring hook in `.claude/hooks/`
  - Hook type: PostToolUse (monitors tool execution duration)
  - Read config from `environment_config.json` (threshold_seconds, enabled, actions)
  - If action exceeds threshold → Force HITL trigger
  - Return blocker signal: "Timeout at Xs. Continue or change approach?"

- [ ] 3.3 IMPLEMENT: Rambling detection hook
  - Create rambling detection hook in `.claude/hooks/`
  - Hook type: PostToolUse (tracks failures)
  - Track consecutive failures, detect same fix attempted twice
  - If 3+ sequential failures → Force HITL trigger
  - If same fix twice → Force HITL trigger
  - Return blocker signal: "Loop detected. User guidance needed."

- [ ] 3.4 CONFIGURE: Update environment config
  - Update `framework/resources/config/environment_config.json`
  - Add section:
    ```json
    "timeout_monitoring": {
      "enabled": true,
      "threshold_seconds": 30,
      "actions": ["browser_navigate", "element_wait", "ajax_call"]
    }
    ```

- [ ] 3.5 VALIDATION: Write comprehensive tests
  - Write unit tests: `test_timeout_monitoring.py` in `mcp_server/_dev_tests/test_workflow_integration/`
    - Test: Action exceeds threshold → HITL triggered
    - Test: 3+ sequential failures → HITL triggered
    - Test: Same fix twice → HITL triggered
    - Test: Configurable threshold works
    - Test: Enable/disable toggle works
  - Write integration test: `test_hook_gate_integration.py`
    - Test: Protocol guides → Gate validates → Hook monitors (3-layer defense)
    - Test: Gate misses violation → Hook catches (timeout/loop)
    - Test: Hook forces HITL trigger reliably
  - Run checks (lint, tests)
  - **Audit: Verify hooks monitor and force HITL (Layer 3 defense)**
  - Record results

- [ ] 3.6 Commit: `feat: Implement timeout monitoring and rambling detection (Task 3.0)`
  - Include assessment report
  - Note: Layer 3 defense operational

**Done When:**
- ✅ Assessment report created (existing hooks + gaps identified)
- ✅ Timeout monitoring works (configurable threshold, force HITL)
- ✅ Rambling detection works (3+ failures, same fix twice)
- ✅ Tests pass (monitoring behavior validated)
- ✅ Integration test shows Protocol + Gate + Hook working together (3-layer defense)

---

### 4.0 Enhance Audit System for Full Session Reconstruction (Layer 5 Defense) [CORE]

**EATING OUR DOGFOOD:** Use HITL pattern (stop-when-blocked) while building audit system. After each step, STOP and get user approval before proceeding.

---

#### Phase 4.1: ASSESSMENT - Audit Existing Audit System

- [ ] 4.1.1 Read existing audit implementation

  **Assessment:**
  - Read: `mcp_server/utils/audit_logger.py`
  - Document: What events are currently logged?
  - Document: What's the current log format?
  - Document: Where are logs written?
  (To be filled after reading)

  **Gap Analysis:**
  (To be filled - what's missing for pair programming?)

  **Decisions:**
  (To be filled - how to resolve gaps?)

  **Action Items:**
  (To be filled - what to do in Phase 4.2/4.3?)

- [ ] 4.1.2 **HITL CHECKPOINT:** Review audit system inventory
  - Present: Current audit_logger.py capabilities
  - Ask: "Audit system read. Proceed to event coverage analysis?"

- [ ] 4.1.3 Analyze current event coverage
  - Check: HITL interaction logging exists?
  - Check: Timeout event logging exists?
  - Check: Build-save-test cycle logging exists?
  - Check: Gate validation logging exists (with fix data)?
  - Check: Hook intervention logging exists?
  - Check: Tool call logging exists?
  - Document: Coverage matrix (exists vs missing)

- [ ] 4.1.4 **HITL CHECKPOINT:** Review event coverage
  - Present: Event coverage matrix
  - Ask: "Event coverage analyzed. Proceed to reconstruction capability analysis?"

- [ ] 4.1.5 Analyze session reconstruction capability
  - Check: Can we reconstruct timeline from current logs?
  - Check: Are all required data points captured?
  - Check: Is log format machine-parseable?
  - Document: Reconstruction gaps

- [ ] 4.1.6 **HITL CHECKPOINT:** Review reconstruction gaps
  - Present: Reconstruction capability gaps
  - Ask: "Reconstruction gaps identified. Proceed to create assessment report?"

- [ ] 4.1.7 Create assessment report
  - Create: `docs/projects/pair-programming/assessment-layer5-audit.md`
  - Section 1: Current logging capabilities (what's logged, format, location)
  - Section 2: Event coverage gaps (missing event types)
  - Section 3: Reconstruction capability gaps (what's needed for full replay)
  - Section 4: Required enhancements (prioritized)

- [ ] 4.1.8 **HITL CHECKPOINT:** Review assessment report
  - Present: Complete assessment report
  - Ask: "Assessment complete. Approve enhancements and proceed to implementation?"

---

#### Phase 4.2: ENHANCE - Update audit_logger.py

- [ ] 4.2.1 Add log_hitl_interaction method
  - Update: `mcp_server/utils/audit_logger.py`
  - Add method: `log_hitl_interaction(timestamp, reason, user_response, ai_action)`
  - Logs: When HITL triggered, why, what user said, what AI did after

- [ ] 4.2.2 **HITL CHECKPOINT:** Review log_hitl_interaction
  - Present: log_hitl_interaction method code
  - Ask: "HITL interaction logging added. Proceed to timeout logging?"

- [ ] 4.2.3 Add log_timeout_event method
  - Add method: `log_timeout_event(threshold, actual_duration, user_decision)`
  - Logs: Threshold setting, actual time waited, user's decision (continue/change)

- [ ] 4.2.4 **HITL CHECKPOINT:** Review log_timeout_event
  - Present: log_timeout_event method code
  - Ask: "Timeout logging added. Proceed to build-save-test cycle logging?"

- [ ] 4.2.5 Add log_build_save_test_cycle method
  - Add method: `log_build_save_test_cycle(file_created, test_result, duration)`
  - Logs: File path, content hash, test outcome, time taken

- [ ] 4.2.6 **HITL CHECKPOINT:** Review log_build_save_test_cycle
  - Present: log_build_save_test_cycle method code
  - Ask: "Build-save-test logging added. Proceed to gate validation logging?"

- [ ] 4.2.7 Add log_gate_validation method
  - Add method: `log_gate_validation(rule, pass_fail, fix_data)`
  - Logs: Which rule checked, pass/fail status, fix data provided (if failed)

- [ ] 4.2.8 **HITL CHECKPOINT:** Review log_gate_validation
  - Present: log_gate_validation method code
  - Ask: "Gate validation logging added. Proceed to hook intervention logging?"

- [ ] 4.2.9 Add log_hook_intervention method
  - Add method: `log_hook_intervention(pattern, action_taken)`
  - Logs: Pattern detected (timeout/loop), action taken (force HITL)

- [ ] 4.2.10 **HITL CHECKPOINT:** Review log_hook_intervention
  - Present: log_hook_intervention method code
  - Ask: "Hook intervention logging added. Proceed to tool call logging?"

- [ ] 4.2.11 Add log_tool_call method
  - Add method: `log_tool_call(tool_name, input_params, output_metadata)`
  - Logs: Which tool, input parameters, output metadata

- [ ] 4.2.12 **HITL CHECKPOINT:** Review log_tool_call
  - Present: log_tool_call method code
  - Ask: "Tool call logging added. Proceed to verify log destination?"

- [ ] 4.2.13 Verify log destination
  - Ensure: All logs write to `tests/_audit/audit_log_[timestamp].json`
  - Verify: JSON format is consistent

- [ ] 4.2.14 **HITL CHECKPOINT:** Review complete audit_logger.py
  - Present: Full updated audit_logger.py
  - Ask: "audit_logger.py enhanced with all log methods. Proceed to audit reconstructor?"

---

#### Phase 4.3: IMPLEMENT - Create Audit Reconstructor

- [ ] 4.3.1 Create audit_reconstructor.py file
  - Create: `mcp_server/utils/audit_reconstructor.py`
  - Create class: `AuditReconstructor`
  - Add docstring explaining purpose

- [ ] 4.3.2 **HITL CHECKPOINT:** Review file structure
  - Present: File structure and class definition
  - Ask: "audit_reconstructor.py created. Proceed to implement parsing logic?"

- [ ] 4.3.3 Implement audit log parsing
  - Add method: `_parse_audit_log(audit_log_path) -> list[dict]`
  - Reads JSON file, returns list of events

- [ ] 4.3.4 **HITL CHECKPOINT:** Review parsing logic
  - Present: Parsing logic code
  - Ask: "Parsing logic implemented. Proceed to timeline building?"

- [ ] 4.3.5 Implement timeline building
  - Add method: `_build_timeline(events) -> Timeline`
  - Constructs timeline: what AI built, when HITL triggered, what user said, how AI responded
  - Returns structured Timeline object

- [ ] 4.3.6 **HITL CHECKPOINT:** Review timeline building
  - Present: Timeline building code
  - Ask: "Timeline building implemented. Proceed to main reconstruct method?"

- [ ] 4.3.7 Implement reconstruct_session method
  - Add method: `reconstruct_session(audit_log_path) -> Timeline`
  - Orchestrates: parse → build timeline → return

- [ ] 4.3.8 **HITL CHECKPOINT:** Review complete audit_reconstructor.py
  - Present: Complete audit_reconstructor.py code
  - Ask: "audit_reconstructor.py complete. Proceed to integration phase?"

---

#### Phase 4.4: INTEGRATE - Connect Audit Logger

- [ ] 4.4.1 Integrate with PostToolUse hook
  - Update: PostToolUse hook to call `audit_logger.log_tool_call()`
  - Add: Tool name, input params, output metadata

- [ ] 4.4.2 **HITL CHECKPOINT:** Review PostToolUse integration
  - Present: Hook integration code
  - Ask: "PostToolUse hook integrated. Proceed to TimeoutMonitor integration?"

- [ ] 4.4.3 Integrate with TimeoutMonitor hook
  - Update: TimeoutMonitor hook to call `audit_logger.log_timeout_event()`
  - Add: Threshold, actual duration, user decision

- [ ] 4.4.4 **HITL CHECKPOINT:** Review TimeoutMonitor integration
  - Present: Integration code
  - Ask: "TimeoutMonitor integrated. Proceed to gate integration?"

- [ ] 4.4.5 Integrate with gate validations
  - Update: All gates to call `audit_logger.log_gate_validation()`
  - Add: Rule checked, pass/fail, fix data

- [ ] 4.4.6 **HITL CHECKPOINT:** Review gate integration
  - Present: Gate integration code
  - Ask: "Gates integrated. Proceed to HITL trigger integration?"

- [ ] 4.4.7 Integrate with HITL triggers
  - Update: HITL system to call `audit_logger.log_hitl_interaction()`
  - Add: Timestamp, reason, user response, AI action

- [ ] 4.4.8 **HITL CHECKPOINT:** Review HITL integration
  - Present: HITL integration code
  - Ask: "All components integrated. Proceed to validation phase?"

---

#### Phase 4.5: VALIDATION - Test Audit System

- [ ] 4.5.1 **HITL CHECKPOINT:** Ready to start testing
  - Ask: "Ready to write and run all audit system tests. Proceed?"

- [ ] 4.5.2 Write unit tests for audit_logger.py
  - Create: `mcp_server/_dev_tests/test_workflow_integration/test_audit_logging.py`
  - Test: log_hitl_interaction logs correctly
  - Test: log_timeout_event logs correctly
  - Test: log_build_save_test_cycle logs correctly
  - Test: log_gate_validation logs correctly (with fix data)
  - Test: log_hook_intervention logs correctly
  - Test: log_tool_call logs correctly
  - Test: All log methods write to correct file

- [ ] 4.5.3 Run unit tests for audit_logger
  - Execute: `pytest mcp_server/_dev_tests/test_workflow_integration/test_audit_logging.py -v`
  - Capture results
  - Fix any failures, re-run

- [ ] 4.5.4 Write unit tests for audit_reconstructor.py
  - Create: `mcp_server/_dev_tests/test_workflow_integration/test_audit_reconstructor.py`
  - Test: Given audit log → Reconstruct timeline
  - Test: Timeline shows correct sequence of events
  - Test: HITL triggers appear in timeline
  - Test: User responses captured in timeline
  - Test: All event types represented

- [ ] 4.5.5 Run unit tests for audit_reconstructor
  - Execute: `pytest mcp_server/_dev_tests/test_workflow_integration/test_audit_reconstructor.py -v`
  - Capture results
  - Fix any failures, re-run

- [ ] 4.5.6 Write integration test
  - Create: `test_full_audit_trail.py`
  - Test: Complete workflow → Full audit logged
  - Test: Audit log contains all required events
  - Test: Session can be reconstructed from log
  - Test: Reconstruction matches actual session flow

- [ ] 4.5.7 Run integration test
  - Execute integration test
  - Capture results
  - Fix any failures, re-run

- [ ] 4.5.8 Run all checks
  - Run: lint, tests
  - Verify: All pass

- [ ] 4.5.9 Final audit
  - **Audit: Full session reconstruction works (Layer 5 defense)**
  - **Audit: All event types logged**
  - **Audit: Timeline reconstruction accurate**
  - Record results in assessment report

- [ ] 4.5.10 **HITL CHECKPOINT:** Review audit results
  - Present: Test results + audit findings
  - Ask: "Layer 5 audit complete. All tests pass. Approve and proceed to commit?"

---

#### Phase 4.6: COMMIT

- [ ] 4.6.1 Prepare commit
  - Stage all changes
  - Review git diff

- [ ] 4.6.2 **HITL CHECKPOINT:** Review commit diff
  - Present: Complete diff
  - Ask: "Review changes. Approve commit?"

- [ ] 4.6.3 Commit changes
  - Commit message: `feat: Enhance audit system for full session reconstruction (Task 4.0)`
  - Body: Include assessment report summary, note Layer 5 defense operational

**Done When:**
- ✅ Assessment report created (current logging + event coverage gaps + reconstruction gaps)
- ✅ audit_logger.py enhanced with all log methods (HITL, timeout, build-save-test, gates, hooks, tools)
- ✅ audit_reconstructor.py created (Timeline reconstruction capability)
- ✅ All components integrated (PostToolUse, TimeoutMonitor, Gates, HITL)
- ✅ Tests pass (unit + integration)
- ✅ Integration test shows full audit trail working (Layer 5 defense)
- ✅ Committed with user approval

---

### 5.0 Configuration Updates (headless=false, timeout thresholds) [GLUE]

**EATING OUR DOGFOOD:** Use HITL pattern (stop-when-blocked) while updating configuration. After each step, STOP and get user approval before proceeding.

---

#### Phase 5.1: ASSESSMENT - Audit Existing Configuration

- [ ] 5.1.1 Read environment_config.json

  **Assessment:**
  - Read: `framework/resources/config/environment_config.json`
  - Document: Current headless setting
  - Document: Current timeout settings
  - Document: All configuration options
  (To be filled after reading)

  **Gap Analysis:**
  (To be filled - what's missing for pair programming?)

  **Decisions:**
  (To be filled - how to resolve gaps?)

  **Action Items:**
  (To be filled - what to do in Phase 5.2/5.3?)

- [ ] 5.1.2 **HITL CHECKPOINT:** Review config inventory
  - Present: Current configuration settings
  - Ask: "Configuration read. Proceed to browser initialization analysis?"

- [ ] 5.1.3 Find and analyze browser initialization code
  - Search: Where is browser initialized? (WebInterface or conftest)
  - Read: Browser initialization code
  - Document: How headless is currently set
  - Document: Any override mechanisms

- [ ] 5.1.4 **HITL CHECKPOINT:** Review initialization code
  - Present: Browser initialization code + override mechanisms
  - Ask: "Initialization analyzed. Proceed to gap identification?"

- [ ] 5.1.5 Identify enforcement gaps
  - Gap: headless=false enforcement missing?
  - Gap: Override prevention missing?
  - Gap: timeout_monitoring section missing?
  - Gap: Validation on attempted override missing?
  - Document: Complete list of gaps

- [ ] 5.1.6 **HITL CHECKPOINT:** Review enforcement gaps
  - Present: Configuration enforcement gaps
  - Ask: "Gaps identified. Proceed to create assessment report?"

- [ ] 5.1.7 Create assessment report
  - Create: `docs/projects/pair-programming/assessment-config.md`
  - Section 1: Current configuration state (settings + initialization code)
  - Section 2: Enforcement gaps (headless, override, timeout)
  - Section 3: Required updates (prioritized)

- [ ] 5.1.8 **HITL CHECKPOINT:** Review assessment report
  - Present: Complete assessment report
  - Ask: "Assessment complete. Approve updates and proceed to configuration phase?"

---

#### Phase 5.2: UPDATE - Enforce Visual Browser Configuration

- [ ] 5.2.1 Update environment_config.json
  - Open: `framework/resources/config/environment_config.json`
  - Add: `"headless": false` (enforce visual browser - CRITICAL)
  - Add: `"headless_override": false` (prevent override - CRITICAL)
  - Verify: timeout_monitoring section exists (added in Task 3.0) or add if missing

- [ ] 5.2.2 **HITL CHECKPOINT:** Review environment_config.json changes
  - Present: Diff of environment_config.json
  - Ask: "environment_config.json updated. Proceed to pair_programming_config.json?"

- [ ] 5.2.3 Create pair_programming_config.json (if needed)
  - Create: `framework/resources/config/pair_programming_config.json`
  - Document: Tool usage (1-2 core, 3-6 optional)
  - Document: HITL settings (trigger conditions)
  - Document: Checkpoint settings (auto-save at blockers)
  - Document: Configuration options

- [ ] 5.2.4 **HITL CHECKPOINT:** Review pair_programming_config.json
  - Present: pair_programming_config.json content
  - Ask: "pair_programming_config.json created. Proceed to browser initialization enforcement?"

---

#### Phase 5.3: ENFORCE - Update Browser Initialization Code

- [ ] 5.3.1 Locate browser initialization code
  - Find: Where browser is initialized (WebInterface __init__ or conftest.py)
  - Document: Current headless logic

- [ ] 5.3.2 **HITL CHECKPOINT:** Review current initialization
  - Present: Current browser initialization code
  - Ask: "Initialization code located. Proceed to add enforcement?"

- [ ] 5.3.3 Add configuration reading logic
  - Add: Read config file at initialization
  - Add: `headless = config.get('headless', False)` (default False)
  - Add: `headless_override = config.get('headless_override', False)`

- [ ] 5.3.4 **HITL CHECKPOINT:** Review config reading
  - Present: Config reading code
  - Ask: "Config reading added. Proceed to add override prevention?"

- [ ] 5.3.5 Add override prevention logic
  - Add: Check if headless_override is False
  - Add: If user attempts headless=True → Raise error
  - Error message: "headless=True not allowed in pair programming mode. Visual browser required."

- [ ] 5.3.6 **HITL CHECKPOINT:** Review complete enforcement code
  - Present: Complete browser initialization code with enforcement
  - Ask: "Enforcement complete. Proceed to validation phase?"

---

#### Phase 5.4: VALIDATION - Test Configuration Enforcement

- [ ] 5.4.1 **HITL CHECKPOINT:** Ready to start testing
  - Ask: "Ready to write and run all configuration tests. Proceed?"

- [ ] 5.4.2 Write unit tests
  - Create: `mcp_server/_dev_tests/test_workflow_integration/test_configuration.py`
  - Test: headless=false enforced (default behavior)
  - Test: headless override blocked (raises error when attempted)
  - Test: timeout threshold configurable (can change from default 30s)
  - Test: enable/disable toggle works (can disable timeout monitoring)
  - Test: Error message clear when override attempted

- [ ] 5.4.3 Run unit tests
  - Execute: `pytest mcp_server/_dev_tests/test_workflow_integration/test_configuration.py -v`
  - Capture results
  - Fix any failures, re-run

- [ ] 5.4.4 Run all checks
  - Run: lint, tests
  - Verify: All pass

- [ ] 5.4.5 Final audit
  - **Audit: Configuration enforces visual browser (CRITICAL - no override allowed)**
  - **Audit: Timeout monitoring configurable**
  - **Audit: Error handling clear when violations attempted**
  - Record results in assessment report

- [ ] 5.4.6 **HITL CHECKPOINT:** Review audit results
  - Present: Test results + audit findings
  - Ask: "Configuration audit complete. All tests pass. Approve and proceed to commit?"

---

#### Phase 5.5: COMMIT

- [ ] 5.5.1 Prepare commit
  - Stage all changes
  - Review git diff

- [ ] 5.5.2 **HITL CHECKPOINT:** Review commit diff
  - Present: Complete diff
  - Ask: "Review changes. Approve commit?"

- [ ] 5.5.3 Commit changes
  - Commit message: `feat: Enforce visual browser and timeout configuration (Task 5.0)`
  - Body: Include assessment report summary, note configuration enforcement operational

**Done When:**
- ✅ Assessment report created (current config + enforcement gaps)
- ✅ environment_config.json updated (headless=false, headless_override=false, timeout_monitoring)
- ✅ pair_programming_config.json created (if needed)
- ✅ Browser initialization code enforces visual browser (CRITICAL)
- ✅ Override prevention implemented (raises error on headless=True attempt)
- ✅ Tests pass (configuration validated)
- ✅ Committed with user approval

---

### 6.0 Validate with Test Generation (E2E - All 6 Layers) [CORE]

**THIS IS IT:** We're eating our own dogfood by USING pair programming to validate the pair programming system. This is the real test.

**EATING OUR DOGFOOD:** Use the FULL pair programming pattern we just built. Stop-when-blocked, HITL at every step, build-save-test cycle.

---

#### Phase 6.1: PREPARE - Ready E2E Environment

- [ ] 6.1.1 Create branch checkpoint (if needed)

- [ ] 6.1.2 **HITL CHECKPOINT:** Choose test site and requirement
  - Ask user: "Which site for E2E test? helios8 (demo) or real target site?"
  - Ask user: "What's the test requirement?" (suggest: "As a dealership staff member, I want to submit a new customer inquiry")
  - Document: Site URL, test requirement

- [ ] 6.1.3 Prepare production structure directories
  - Create: `framework/pages/{site_name}/`
  - Create: `framework/tasks/{site_name}/`
  - Create: `framework/roles/{site_name}/`
  - Create: `tests/{site_name}/`

- [ ] 6.1.4 **HITL CHECKPOINT:** Review structure
  - Present: Directory structure created
  - Ask: "Directories ready. Proceed to Step 1 (Pre-flight)?"

---

#### Phase 6.2: EXECUTE - Pair Programming Workflow

**Steps 1-3: Pre-flight, Input, Intent**

- [ ] 6.2.1 Step 1: Pre-flight Configuration
  - Execute: qg_preflight with credential_strategy and test_data_location
  - HITL if needed: User specifies strategy

- [ ] 6.2.2 **HITL CHECKPOINT:** Review pre-flight
  - Present: Pre-flight configuration
  - Ask: "Pre-flight complete. Proceed to Step 2 (User Input)?"

- [ ] 6.2.3 Step 2: User Input
  - Capture: persona, URL, requirement
  - Execute: qg_user_input validation

- [ ] 6.2.4 **HITL CHECKPOINT:** Review user input
  - Present: Validated user input
  - Ask: "User input captured. Proceed to Step 3 (AI Processing)?"

- [ ] 6.2.5 Step 3: AI Processing
  - Extract: role_name, workflow, intent
  - Execute: qg_ai_processing validation
  - Prepare: For collaborative construction

- [ ] 6.2.6 **HITL CHECKPOINT:** Review AI processing
  - Present: role_name, workflow, intent extracted
  - Ask: "AI processing complete. Proceed to Step 4 (Collaborative Construction)?"

**Step 4: Collaborative Construction (THE CORE - Build-Save-Test Cycle)**

- [ ] 6.2.7 Tool 1: Generate BDD scenarios
  - Execute: generate_tests_from_user_story
  - Get: BDD scenarios with Given/When/Then
  - Execute: qg_test_scenarios POST validation

- [ ] 6.2.8 **HITL CHECKPOINT:** Review BDD scenarios
  - Present: Generated BDD scenarios
  - Ask: "BDD scenarios generated. Proceed to Tool 2 (Element Discovery)?"

- [ ] 6.2.9 Tool 2: Discover page elements
  - Navigate: To target page (visible browser - headless=false)
  - Execute: discover_page_elements (Playwright snapshot)
  - Get: Discovered elements list
  - Execute: qg_discovered_elements POST validation

- [ ] 6.2.10 **HITL CHECKPOINT:** Review discovered elements
  - Present: Discovered elements
  - Ask: "Elements discovered. Proceed to build first POM?"

**BUILD-SAVE-TEST CYCLE STARTS HERE**

- [ ] 6.2.11 Build first POM (e.g., CustomerSearchPage)
  - AI: Use Edit/Write tools to create POM
  - Add: Locators as class constants
  - Add: Atomic methods (return self)
  - NO decorators
  - Save immediately

- [ ] 6.2.12 **HITL CHECKPOINT:** Review first POM
  - Present: CustomerSearchPage code
  - Execute: qg_page_object POST validation (gate checks patterns)
  - If gate violation: Present fix data, get user guidance
  - Ask: "First POM created. Gate validation passed. Proceed to test?"

- [ ] 6.2.13 Test first POM (quick smoke test)
  - Write: Quick test to verify POM works
  - Run: pytest on quick test
  - If fail: HITL trigger (DD-22 - stop-when-blocked)

- [ ] 6.2.14 **HITL CHECKPOINT:** Review test result
  - Present: Test result
  - If pass: Ask "First POM works. Build more POMs or proceed to Task?"
  - If fail: Present error, ask for guidance

- [ ] 6.2.15 Repeat build-save-test for remaining POMs
  - Build → Save → Gate validates → Test → HITL at each completion
  - (Repeat 6.2.11-6.2.14 for each POM needed)

- [ ] 6.2.16 **HITL CHECKPOINT:** All POMs complete
  - Present: List of all POMs created
  - Ask: "All POMs complete and tested. Proceed to build Task?"

- [ ] 6.2.17 Build Task (e.g., Helios8Tasks)
  - AI: Use Edit/Write tools to create Task
  - Compose: POMs in __init__
  - Add: @autologger decorator on methods
  - Methods: Return None (NOT values)
  - **CRITICAL: NO locators in Task (DD-27)**
  - Save immediately

- [ ] 6.2.18 **HITL CHECKPOINT:** Review Task
  - Present: Task code
  - Execute: qg_task POST validation (gate checks DD-27, patterns)
  - If gate violation: Present fix data, get user guidance
  - Ask: "Task created. Gate validation passed. Proceed to test?"

- [ ] 6.2.19 Test Task
  - Write: Quick test to verify Task works
  - Run: pytest on quick test
  - If fail: HITL trigger (DD-22)

- [ ] 6.2.20 **HITL CHECKPOINT:** Review Task test result
  - Present: Test result
  - If pass: Ask "Task works. Proceed to build Role?"
  - If fail: Present error, ask for guidance

- [ ] 6.2.21 Build Role (e.g., DealershipStaff)
  - AI: Use Edit/Write tools to create Role
  - Compose: Tasks in __init__
  - Add: @autologger decorator on methods
  - Methods: Return None (orchestrate workflow)
  - Save immediately

- [ ] 6.2.22 **HITL CHECKPOINT:** Review Role
  - Present: Role code
  - Execute: qg_role POST validation (gate checks patterns)
  - If gate violation: Present fix data, get user guidance
  - Ask: "Role created. Gate validation passed. Proceed to test?"

- [ ] 6.2.23 Test Role
  - Write: Quick test to verify Role works
  - Run: pytest on quick test
  - If fail: HITL trigger (DD-22)

- [ ] 6.2.24 **HITL CHECKPOINT:** Review Role test result
  - Present: Test result
  - If pass: Ask "Role works. Proceed to build final Test?"
  - If fail: Present error, ask for guidance

- [ ] 6.2.25 Build Test runner (e.g., test_submit_inquiry.py)
  - AI: Use Edit/Write tools to create Test
  - Calls: ONE role workflow method
  - Asserts: Via POM state-check methods (NOT return values)
  - AAA pattern: Arrange, Act, Assert
  - Save immediately

- [ ] 6.2.26 **HITL CHECKPOINT:** Review Test
  - Present: Test code
  - Execute: qg_test_runner POST validation (gate checks patterns)
  - If gate violation: Present fix data, get user guidance
  - Ask: "Test created. Gate validation passed. Proceed to final run?"

- [ ] 6.2.27 Run final test (THE MOMENT OF TRUTH)
  - Execute: pytest tests/{site_name}/test_submit_inquiry.py -v
  - Capture: Full output
  - If fail: HITL trigger (DD-22 - stop, report, discuss)

- [ ] 6.2.28 **HITL CHECKPOINT:** Review final test result (CRITICAL)
  - Present: Test output (pass/fail)
  - If PASS: "TEST PASSED ON FIRST ATTEMPT! Success metric 1 achieved."
  - If FAIL: Present error, ask for guidance, fix, re-run
  - Ask: "Test result reviewed. Proceed to validate success metrics?"

---

#### Phase 6.3: VALIDATE - Success Metrics

- [ ] 6.3.1 Validate Success Metric 1: Test passes on first attempt
  - Check: Did test pass without Step 11 manual fixes?
  - Document: YES/NO + evidence

- [ ] 6.3.2 Validate Success Metric 2: HITL triggered reliably
  - Check: Did HITL trigger at every blocker (no AI rambling)?
  - Review: Audit log for HITL events
  - Document: YES/NO + count of HITL triggers

- [ ] 6.3.3 Validate Success Metric 3: Full session audit logged
  - Check: Can session be reconstructed from audit log?
  - Execute: AuditReconstructor on session audit log
  - Review: Timeline shows what AI built, when HITL triggered, what user said
  - Document: YES/NO + timeline excerpt

- [ ] 6.3.4 **HITL CHECKPOINT:** Review success metrics
  - Present: All 3 success metrics results
  - Ask: "Success metrics validated. Proceed to audit reconstruction?"

---

#### Phase 6.4: AUDIT - Session Reconstruction

- [ ] 6.4.1 Run audit reconstruction
  - Execute: `python mcp_server/utils/audit_reconstructor.py tests/_audit/audit_log_[timestamp].json`
  - Capture: Timeline output

- [ ] 6.4.2 **HITL CHECKPOINT:** Review reconstruction
  - Present: Full session timeline
  - Verify: Timeline shows complete session flow
  - Ask: "Audit reconstruction complete. Proceed to write validation report?"

---

#### Phase 6.5: DOCUMENT - Validation Report

- [ ] 6.5.1 Write validation report
  - Create: `docs/projects/pair-programming/4-validation-report.md`
  - Section 1: Test generation process (Step 1-4 flow)
  - Section 2: Success metrics results (3 metrics)
  - Section 3: 6-layer defense evidence (Protocol guided, Gates validated, Hooks monitored, etc.)
  - Section 4: Code pattern compliance (all 4 layers followed FRAMEWORK.md)
  - Section 5: Lessons learned, improvements needed
  - Section 6: Audit log excerpt, timeline reconstruction

- [ ] 6.5.2 **HITL CHECKPOINT:** Review validation report
  - Present: Complete validation report
  - Ask: "Validation report complete. Proceed to write integration test?"

---

#### Phase 6.6: TEST - 6-Layer Defense Integration

- [ ] 6.6.1 **HITL CHECKPOINT:** Ready to write integration test
  - Ask: "Ready to write 6-layer defense integration test. Proceed?"

- [ ] 6.6.2 Write integration test
  - Create: `mcp_server/_dev_tests/test_workflow_integration/test_6_layer_defense.py`
  - Test: All 6 layers coordinate correctly
  - Test: Protocol guides → Gate validates → Hook monitors → Checkpoint saves → Audit logs → HITL provides escape
  - Test: If Layer 1 fails → Layer 2 catches
  - Test: If Layer 2 fails → Layer 3 catches
  - Test: If Layer 3 fails → Layer 6 catches (user interrupt)

- [ ] 6.6.3 Run integration test
  - Execute: `pytest mcp_server/_dev_tests/test_workflow_integration/test_6_layer_defense.py -v`
  - Capture results
  - Fix any failures, re-run

- [ ] 6.6.4 Run all checks
  - Run: All unit tests, all integration tests, E2E test
  - Run: Framework validation (`/framework-check`)
  - Verify: 0 violations

- [ ] 6.6.5 Final audit
  - **Audit: Pair programming produces working test on first attempt (Success Metric 1)**
  - **Audit: HITL triggered reliably (Success Metric 2)**
  - **Audit: Full session audit logged (Success Metric 3)**
  - **Audit: 6-layer defense operational**
  - **Audit: Code follows correct patterns (4-layer architecture)**
  - Record results

- [ ] 6.6.6 **HITL CHECKPOINT:** Review final audit
  - Present: Audit findings + all test results
  - Ask: "E2E validation complete. All audits pass. Approve and proceed to commit?"

---

#### Phase 6.7: COMMIT

- [ ] 6.7.1 Prepare commit
  - Stage all changes
  - Review git diff

- [ ] 6.7.2 **HITL CHECKPOINT:** Review commit diff
  - Present: Complete diff (POMs, Tasks, Roles, Tests, validation report)
  - Ask: "Review changes. Approve commit?"

- [ ] 6.7.3 Commit changes
  - Commit message: `feat: Validate pair programming with test generation (Task 6.0)`
  - Body: Include validation report summary, success metrics results

**Done When:**
- ✅ One test generated via pair programming (production structure)
- ✅ **Test passes on first attempt (Success Metric 1 - no Step 11 fixes)**
- ✅ **HITL triggered reliably (Success Metric 2 - no AI rambling)**
- ✅ **Full session audit logged (Success Metric 3 - reconstruction possible)**
- ✅ **All code follows correct patterns (validated by gates)**
- ✅ Validation report documents complete evidence
- ✅ Integration test validates 6-layer defense working together
- ✅ Committed with user approval

---

### 7.0 Documentation & Merge [GLUE]

**EATING OUR DOGFOOD:** Final step - document what we built, validate everything, merge to main.

---

#### Phase 7.1: DOCUMENT - Update Project Documentation

- [ ] 7.1.1 **HITL CHECKPOINT:** Review documentation needs
  - Ask: "Review which docs need updating: README.md, FRAMEWORK.md, SESSION.md. Proceed?"

- [ ] 7.1.2 Update README.md (if needed)
  - Read: Current README.md
  - Add: High-level pair programming workflow description
  - Add: Link to Protocol files for details
  - Save

- [ ] 7.1.3 **HITL CHECKPOINT:** Review README.md changes
  - Present: Diff of README.md
  - Ask: "README.md updated. Proceed to FRAMEWORK.md?"

- [ ] 7.1.4 Update FRAMEWORK.md (if needed)
  - Read: Current FRAMEWORK.md
  - Add: Section on pair programming workflow
  - Add: Reference to 6-layer defense architecture
  - Add: Reference to code pattern correctness (Layers 1+2)
  - Save

- [ ] 7.1.5 **HITL CHECKPOINT:** Review FRAMEWORK.md changes
  - Present: Diff of FRAMEWORK.md
  - Ask: "FRAMEWORK.md updated. Proceed to SESSION.md?"

- [ ] 7.1.6 Update SESSION.md
  - Document: Phase 1-4 complete (Design → Define → Divide → Deliver)
  - Document: Pair programming formalization complete
  - Archive: workflow refactor project status to "completed"

- [ ] 7.1.7 **HITL CHECKPOINT:** Review SESSION.md changes
  - Present: Diff of SESSION.md
  - Ask: "SESSION.md updated. Proceed to final validation phase?"

---

#### Phase 7.2: VALIDATE - Run All Checks

- [ ] 7.2.1 **HITL CHECKPOINT:** Ready for complete validation
  - Ask: "Ready to run complete test suite (unit, integration, e2e, framework check). Proceed?"

- [ ] 7.2.2 Run all unit tests
  - Execute: `pytest mcp_server/_dev_tests/test_gates/ -v`
  - Execute: `pytest mcp_server/_dev_tests/test_workflow_integration/ -v`
  - Capture: Results
  - Fix: Any failures, re-run

- [ ] 7.2.3 Run E2E test
  - Execute: `pytest tests/{site_name}/ -v`
  - Capture: Results
  - Verify: Test passes (no Step 11 fixes)

- [ ] 7.2.4 Run framework validation
  - Execute: `/framework-check` or equivalent
  - Verify: 0 violations
  - Verify: All code follows 4-layer architecture

- [ ] 7.2.5 Review validation report from Task 6.0
  - Read: `docs/projects/pair-programming/4-validation-report.md`
  - Confirm: Test passes on first attempt (Success Metric 1)
  - Confirm: HITL triggered reliably (Success Metric 2)
  - Confirm: Full audit trail logged (Success Metric 3)

- [ ] 7.2.6 **HITL CHECKPOINT:** Review all validation results
  - Present: All test results + framework validation + validation report summary
  - Ask: "All validation complete. Proceed to acceptance test verification?"

---

#### Phase 7.3: VERIFY - Acceptance Tests

- [ ] 7.3.1 Verify 10 Acceptance Tests from PRD
  - AT-1: Test passes on first attempt ✓ (validated in Task 6.0)
  - AT-2: HITL triggers on timeout ✓ (tested in Task 3.0)
  - AT-3: HITL triggers on test failure ✓ (validated in Task 6.0)
  - AT-4: User interrupt works ✓ (tested throughout)
  - AT-5: Full audit trail logged ✓ (tested in Task 4.0)
  - AT-6: Visual browser enforced ✓ (tested in Task 5.0)
  - AT-7: Stop-when-blocked (no rambling) ✓ (validated throughout)
  - AT-8: Build-save-test cycle ✓ (validated in Task 6.0)
  - AT-9: Smart Gates teach fixes ✓ (tested in Task 2.0)
  - AT-10: 6-layer defense works together ✓ (integration test in Task 6.0)

- [ ] 7.3.2 **HITL CHECKPOINT:** Review acceptance test status
  - Present: All 10 acceptance tests status
  - Ask: "All acceptance tests verified. Proceed to final audit?"

---

#### Phase 7.4: AUDIT - Final System Validation

- [ ] 7.4.1 Final audit checklist
  - **Audit: All protocol files document code pattern correctness (Layer 1)**
  - **Audit: All gates validate and teach correct patterns (Layer 2)**
  - **Audit: Timeout monitoring operational (Layer 3)**
  - **Audit: Checkpointing auto-saves (Layer 4 - existing, validated)**
  - **Audit: Full audit trail logged (Layer 5)**
  - **Audit: HITL triggers reliably (Layer 6)**
  - **Audit: Configuration enforces headless=false**
  - **Audit: Test generated via pair programming passes on first attempt**
  - **Audit: All code follows FRAMEWORK.md patterns**
  - Record: All audit results

- [ ] 7.4.2 **HITL CHECKPOINT:** Review final audit
  - Present: Complete audit results
  - Ask: "Final audit complete. All criteria met. Proceed to commit documentation?"

---

#### Phase 7.5: COMMIT - Documentation

- [ ] 7.5.1 Prepare commit
  - Stage: All documentation changes
  - Review: git diff

- [ ] 7.5.2 **HITL CHECKPOINT:** Review documentation commit
  - Present: Diff of documentation changes
  - Ask: "Review documentation changes. Approve commit?"

- [ ] 7.5.3 Commit documentation
  - Commit message: `docs: Update documentation for pair programming (Task 7.0)`
  - Body: Document changes made (README, FRAMEWORK, SESSION)

---

#### Phase 7.6: MERGE - Feature Branch to Main

- [ ] 7.6.1 **HITL CHECKPOINT:** Ready to merge
  - Present: Summary of all 7 tasks completed
  - Present: All success criteria met
  - Ask: "Ready to merge feature/pair-programming to main. Approve?"

- [ ] 7.6.2 Push feature branch to remote
  - Execute: `git push origin feature/pair-programming`

- [ ] 7.6.3 **HITL CHECKPOINT:** Review push result
  - Present: Push result
  - Ask: "Feature branch pushed. Proceed to merge?"

- [ ] 7.6.4 Merge to main
  - Execute: `git checkout main`
  - Execute: `git merge feature/pair-programming`
  - Resolve: Any conflicts (HITL if conflicts occur)

- [ ] 7.6.5 **HITL CHECKPOINT:** Review merge result
  - Present: Merge result
  - Ask: "Merge complete. Proceed to push main?"

- [ ] 7.6.6 Push main to remote
  - Execute: `git push origin main`

- [ ] 7.6.7 **HITL CHECKPOINT:** Review final push
  - Present: Push result
  - Ask: "Main branch updated. Proceed to archive project?"

---

#### Phase 7.7: ARCHIVE - Complete Project

- [ ] 7.7.1 Archive project documentation
  - Create: `docs/projects/completed/` directory (if doesn't exist)
  - Move: `docs/projects/pair-programming/` to `docs/projects/completed/pair-programming/`

- [ ] 7.7.2 **HITL CHECKPOINT:** Confirm project complete
  - Present: Project summary
    - Tasks 1.0-7.0 complete
    - Pair programming formalized
    - 6-layer defense operational
    - Test passes on first attempt
    - Autonomous workflow replaced
  - Ask: "Project complete. Pair programming is now the PRIMARY workflow. Confirmed?"

**Done When:**
- ✅ Documentation updated (README, FRAMEWORK, SESSION)
- ✅ All tests pass (unit, integration, e2e)
- ✅ Framework validation: 0 violations
- ✅ All 10 acceptance tests verified
- ✅ Final audit confirms all criteria met
- ✅ Feature branch merged to main
- ✅ Project archived to completed
- ✅ **Autonomous workflow replaced with pair programming**
- ✅ **QA v1.0 shipped with pair programming as PRIMARY workflow**

---

## Command Reference

### Testing
```bash
# Gate tests (unit tests for teaching fixes)
pytest mcp_server/_dev_tests/test_gates/ -v

# Integration tests (6-layer defense)
pytest mcp_server/_dev_tests/test_workflow_integration/ -v

# E2E test (production structure - helios8 or target site)
pytest tests/helios8/ -v

# All tests
pytest -v

# With coverage
pytest --cov=mcp_server --cov-report=html
```

### Framework Validation
```bash
# Check framework compliance
/framework-check
```

### Audit Reconstruction
```bash
# Reconstruct session from audit log
python mcp_server/utils/audit_reconstructor.py tests/_audit/audit_log_[timestamp].json
```

---

## Success Criteria (Definition of Done)

**CRITICAL: Code Pattern Correctness (Non-Negotiable)**
- ✅ **Protocols (Layer 1) enforce correct code patterns for all 4 layers**
  - POM patterns: Locators as class constants, atomic methods return self, NO decorators, composition
  - Task patterns: Compose POMs, @autologger, return None, NO locators (DD-27)
  - Role patterns: Compose Tasks, @autologger, return None (orchestrate)
  - Test patterns: Call ONE role method, assert via POM state-checks (NOT return values)
  - All patterns reference FRAMEWORK.md (authoritative source)
- ✅ **Smart Gates (Layer 2) validate ALL code patterns AND teach correct fixes**
  - Validate 4-layer architecture, composition, returns, locators, decorators
  - Teach correct fixes with actionable guidance + code examples from FRAMEWORK.md
  - Fix data references DD numbers and FRAMEWORK.md sections (traceability)

**All tasks complete when:**
- ✅ Assessment reports created for Layers 1-5 (current state + gaps identified)
- ✅ Protocol files document sufficient guidance (Layer 1)
- ✅ Smart Gates validate AND teach (Layer 2)
- ✅ Timeout monitoring works (Layer 3)
- ✅ Checkpointing auto-saves (Layer 4 - existing, validated)
- ✅ Full audit trail logged (Layer 5)
- ✅ HITL triggers reliably (Layer 6 - existing, validated)
- ✅ Configuration enforces headless=false (no override)
- ✅ One test generated via pair programming (follows production structure)
- ✅ **Generated test follows correct code patterns (4-layer architecture, validated by gates)**
- ✅ Test passes on first attempt (no Step 11 fixes)
- ✅ HITL triggered reliably (no AI rambling)
- ✅ Full session audit logged (reconstruction possible)
- ✅ Validation report documents evidence (code pattern compliance + success metrics)
- ✅ All tests pass (unit, integration, e2e)
- ✅ Documentation updated
- ✅ Feature branch merged to main

---

**Next Phase:** Phase 4 (Deliver) - Execute tasks sequentially, commit after each parent task complete.
