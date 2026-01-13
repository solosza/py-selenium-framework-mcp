# PRD: Release Readiness

**Version:** 1.0
**Created:** 2025-12-27
**Status:** In Progress (adding topics as designed)

---

## 1. Introduction/Overview

Prepare the Isagawa QA Execution Engine for public release by closing architectural gaps, improving observability, and ensuring the system demonstrates its core value proposition: **enforcement over generation**.

**Core Principle:**
> "Skills + Gates are the system. Tools are replaceable labor."

---

## 2. Goals

1. Demonstrate resilience under failure (tools fail, system recovers)
2. Provide clear audit trail of what happened per run
3. Prevent infinite self-heal loops
4. Ensure deterministic file output locations
5. Validate system handles edge cases gracefully
6. Track which gates ran per workflow
7. Validate across multiple apps/browsers
8. Provide simple install experience
9. Clear positioning for technical audiences

---

## 3. Design Decisions (Captured from Phase 0)

### Topic 1: Execution Modes

**Decision Date:** 2025-12-27

**Context:**
- Tools 3-6 sometimes generate skeleton code
- AI self-heals using skill patterns
- Gates validate and enforce

**Architectural Principle:**
> "Isagawa does not rely on generation. It relies on enforcement. Generation is replaceable."

**Key Insight:**
- Tools = untrusted execution primitives (cheap, fast, unreliable labor)
- Skills = knowledge + intent
- Gates = law
- "Even when tools fail, law wins" - this is the differentiator

**Decision:**

| Aspect | Decision |
|--------|----------|
| Modes supported | Two: **MIXED** and **SKILLS_ONLY** |
| MIXED | Tools generate, gates validate, AI self-heals on failure |
| SKILLS_ONLY | AI generates using skills, gates validate |
| TOOLS_ONLY | NOT supported (without skills/gates, no value) |
| MVP default | MIXED (hardcoded, not user-facing) |
| User experience | No execution mode question at Step 1 |
| Audit trail | Shows source per step (Tool / AI / Self-Heal) |
| Advanced config | `ISAGAWA_EXECUTION_MODE=skills_only` env var (documented, not prompted) |

**Rationale:**
- Removing tools loses evidence of resilience, not capability
- MIXED mode demonstrates "what happens when AI fails" - a key buyer question
- User doesn't need to understand modes - it's implementation detail
- Audit trail captures execution source for observability

**Implementation Scope:**

| Component | Change |
|-----------|--------|
| Workflow state | Add `execution_mode` field (default: "mixed") |
| Step skills (6-9) | Branch logic based on mode |
| Gates (6-9) | Track `source` in state (tool/ai/self-heal) |
| Audit report | New "Execution Summary" section |
| Docs | Explain architecture for technical audiences |

---

### Topic 2: Audit Trail Improvements

**Decision Date:** 2025-12-27
**Enhanced:** 2026-01-07 (Metadata Capture Added)

**Context:**
- No automatic record of what happened during a run
- Gate responses not persisted
- If workflow fails mid-way, no trace of which gates passed/failed
- **NEW (2026-01-07):** Need to capture actual validation data, not just pass/fail, to enable context reconstruction after context window overflow

**Decision:**

| Aspect | Decision |
|--------|----------|
| What to capture | All: gates, execution source, self-heal attempts, files generated, errors, **metadata** |
| Where to store | Separate file per run: `audit_log_{timestamp}.json` in `tests/_audit/` |
| Format | JSON (machine-readable), human summary generated on demand |
| Metadata | Each gate logs lightweight summary of validation data (counts, names, not full structures) |

**Audit Log Schema (Enhanced with Metadata):**

```json
{
  "run_id": "2026-01-07T10:19:17.493153Z",
  "execution_mode": "mixed",
  "steps": [
    {
      "step": 1,
      "gate": "qg_preflight",
      "mode": "POST",
      "result": "pass",
      "timestamp": "2026-01-07T10:39:22.126203Z",
      "metadata": {
        "credential_strategy": "static",
        "test_data_location": "shared"
      }
    },
    {
      "step": 2,
      "gate": "qg_user_input",
      "mode": "POST",
      "result": "pass",
      "timestamp": "2026-01-07T10:39:44.002427Z",
      "metadata": {
        "persona": "As a registered user",
        "URL": "https://example.com/login",
        "role_name": "RegisteredUser",
        "workflow": "auth"
      }
    },
    {
      "step": 6,
      "gate": "qg_page_object",
      "mode": "PRE",
      "result": "pass",
      "timestamp": "2026-01-07T10:40:10.000000Z",
      "metadata": {
        "page_name": "LoginPage",
        "elements_count": 15
      }
    },
    {
      "step": 6,
      "gate": "qg_page_object",
      "mode": "POST",
      "result": "fail",
      "error": "skeleton detected",
      "source": "tool",
      "timestamp": "2026-01-07T10:40:15.000000Z"
    },
    {
      "step": 6,
      "gate": "qg_page_object",
      "mode": "POST",
      "result": "pass",
      "source": "self-heal",
      "timestamp": "2026-01-07T10:40:37.305582Z",
      "metadata": {
        "page_name": "LoginPage",
        "class_name": "LoginPage",
        "import_path": "pages.auth.login_page",
        "action_methods_count": 4,
        "state_methods_count": 2
      }
    },
    {
      "step": 6,
      "gate": "qg_page_object",
      "mode": "POST",
      "result": "pass",
      "source": "tool",
      "timestamp": "2026-01-07T10:41:00.000000Z",
      "metadata": {
        "page_name": "AccountOverviewPage",
        "class_name": "AccountOverviewPage",
        "import_path": "pages.parabank.account_overview_page",
        "action_methods_count": 3,
        "state_methods_count": 3,
        "multi_page": {
          "poms_generated": 2,
          "total_poms": 4,
          "generation_complete": false,
          "page_index": 2
        }
      }
    }
  ],
  "files_generated": [
    {"path": "framework/pages/auth/login_page.py", "step": 6},
    {"path": "framework/pages/parabank/account_overview_page.py", "step": 6},
    {"path": "framework/tasks/auth/auth_tasks.py", "step": 7}
  ],
  "summary": {
    "total_steps": 10,
    "gates_passed": 18,
    "gates_failed": 2,
    "self_heals": 2,
    "final_result": "pass",
    "execution_mode": "mixed",
    "source_counts": {
      "tool": 12,
      "self-heal": 6
    }
  }
}
```

**Metadata Benefits:**
- **Context Reconstruction:** Can rebuild workflow state after context window overflow
- **Multi-Page Tracking:** Each POM POST creates separate entry with progress info
- **Debugging:** Know exact inputs/outputs at each step
- **Resume Capability:** Can resume from any completed step
- **Lightweight:** Counts instead of full structures (90% smaller than logging tool metadata)

**Implementation Scope:**

| Component | Change | Status |
|-----------|--------|--------|
| `tests/_audit/` | New `audit_log_{timestamp}.json` per run | ✅ DONE |
| `utils/audit_logger.py` | Added `metadata` parameter to `log_gate()` | ✅ DONE |
| `tools/gates/base_gate.py` | Added `metadata` parameter to `pass_response()`, `fail_response()`, `blocked_response()` | ✅ DONE |
| All gates (Steps 1-11) | Extract and pass metadata summaries to audit logger | ✅ DONE |
| `qg_save_run` | Write final summary, close audit log | ✅ DONE |
| `utils/context_reconstructor.py` | Utility to rebuild workflow state from audit metadata | ✅ DONE |
| CLI (future) | `isagawa audit --run <id>` to view/summarize | PENDING |

**Rationale:**
- Separate file per run = easy to compare runs, no data loss
- JSON = machine-readable, can generate human summary on demand
- Captures everything needed to debug failures or demonstrate resilience
- **Metadata enables context reconstruction** = can resume after context window overflow
- **Lightweight metadata** = audit files 90% smaller than logging full tool metadata

---

### Topic 3: Hard Cap Self-Heal Loop

**Decision Date:** 2025-12-27

**Context:**
- Skills document "max 3 retries" but no code enforcement
- AI could loop indefinitely on persistent failures
- Risk: token burn, user frustration, never stops

**Decision:**

| Aspect | Decision |
|--------|----------|
| Retry tracking | Per step - each step gets its own counter |
| Max retries | Hardcoded: 3 (MVP simplicity) |
| On max reached | Blocked status + report + DD-22 user decision |

**Behavior:**

```
Step 6: POM generation
  Attempt 1: Tool generates → Gate FAIL (skeleton)
  Attempt 2: AI self-heals → Gate FAIL (missing method)
  Attempt 3: AI self-heals → Gate FAIL (wrong pattern)

  MAX RETRIES REACHED

  Gate returns: {
    "status": "blocked",
    "step": 6,
    "attempts": 3,
    "errors": ["skeleton", "missing method", "wrong pattern"],
    "action_required": "user_decision"
  }

  Audit log captures all attempts.
  Workflow STOPS. User must decide (DD-22).
```

**User Decision Options (DD-22):**
1. Retry with different approach
2. Skip step (manual implementation)
3. Abort workflow

**Implementation Scope:**

| Component | Change |
|-----------|--------|
| Gate base class | Add `attempt_count` tracking per step |
| All POST gates | Check attempt count before validation |
| Gate response | New `blocked` status + `attempts` field |
| Audit log | Record each attempt with error details |
| Skills | Reference gate enforcement (not just documentation) |

**Rationale:**
- Per-step tracking: Step 6 failing 3x doesn't affect Step 7's budget
- Hardcoded 3: Simple, matches existing docs, can add config later
- DD-22 integration: System stops, user decides - enforcement over automation

---

### Topic 4: Deterministic Artifact Layout

**Decision Date:** 2025-12-27

**Decision:** DEFERRED (not MVP)

**Rationale:**
- Skills already teach correct file paths
- Step 1 validates test DATA location (different concern)
- Path enforcement is low priority vs other topics
- Can add to qg_save_run later if needed

**Future Implementation (if needed):**
- Add path pattern validation to qg_save_run
- Patterns: `framework/pages/{domain}/*.py`, `framework/tasks/{domain}/*.py`, `tests/{workflow}/test_*.py`

---

### Topic 5: Adversarial Inputs Test Suite

**Decision Date:** 2025-12-27

**Decision:** NOT A DESIGN TOPIC - moved to QA task list

**Rationale:**
- Adversarial inputs go through same 11-step workflow
- Existing gates already validate each step
- This is a testing task, not a design decision

**QA Task (for task list):**
> Run 5 adversarial inputs through 11-step workflow, verify gates block with helpful errors

**Example inputs to test:**
1. Ambiguous: "register user" (no details)
2. Missing URL: persona only, no page specified
3. Contradictory: "login without credentials"
4. Multi-step: "login, browse, checkout" in one prompt
5. Malformed BDD: requirement with no clear action

---

### Topic 6: Gate Drift Prevention

**Decision Date:** 2025-12-27

**Decision:** NOT NEEDED - already enforced by architecture

**Rationale:**
- Each PRE gate checks `state_manager.is_step_complete(N-1)`
- State is only saved when gate passes
- Skipping steps is architecturally impossible
- Example: Step 6 PRE fails if Step 5 state doesn't exist

**Evidence:**
```python
# qg_page_object.validate_pre()
if not state_manager.is_step_complete(5):
    return cls.fail_response(
        error="Step 5 is not complete. Cannot proceed to Step 6."
    )
```

No implementation needed.

---

### Topic 7: Smoke-Test Matrix

**Decision Date:** 2025-12-27

**Context:**
- Goal is to prove AI Management Layer works, not comprehensive test coverage
- Currently validated: automationpractice.pl (Registration, Add to Cart)
- Need robustness proof across sites and complexity levels
- Then pivot to new non-tech vertical

**Decision:**

| Aspect | Decision |
|--------|----------|
| Purpose | Prove AI Management Layer works robustly |
| Sites | 2-3 different sites (proves not overfitted) |
| Complexity | Must include at least one complex multi-page workflow |
| Browser | Chrome only (browser compat is Selenium's job, not ours) |
| Pass criteria | 11-step workflow completes with all gates passing |

**MVP Validation Bar:**

| Complexity | Definition | Required |
|------------|------------|----------|
| Simple | Single page, 1-2 actions (login, register) | 1+ per site |
| Medium | Multi-element, same page (add to cart) | 1+ per site |
| Complex | Multi-page, conditional logic (checkout) | 1+ total |

**What This Proves:**
> "The AI Management Layer enforces correct execution across sites and complexity levels. Ready to apply to next vertical."

**No Implementation Needed:**
- This is a validation activity, not code change
- Run 11-step workflow on additional sites
- Document pass/fail in SESSION.md

---

### Topic 8: Packaging + Install Story

**Decision Date:** 2025-12-27

**Context:**
- Distribution strategy defined in thesis: `pip install isagawa-qa`
- MVP goal is proving system works, not polish
- Skills contain domain expertise (IP concern)

**Decision:**

| Aspect | Decision |
|--------|----------|
| Install method | Manual clone + `pip install -r requirements.txt` |
| Skills distribution | Manual copy (documented in README) |
| Skills protection | License protection (readable but legally protected) |
| Priority | Prove system works first, polish install in Phase 2 |

**Skills License Header:**

Each skill file will include:
```
# LICENSE: Proprietary - Isagawa Corp
# You may USE this skill with Claude Code.
# You may NOT redistribute, modify, or create derivative works.
# See LICENSE.md for full terms.
```

**MVP Install Steps (documented in README):**

```bash
# 1. Clone repository
git clone https://github.com/isagawa/qa-execution-engine.git

# 2. Install dependencies
pip install -r requirements.txt
pip install -r mcp_server/requirements.txt

# 3. Copy skills to your project
cp -r .claude/skills/qa-management-layer /your-project/.claude/skills/

# 4. Configure Claude Code to use MCP server
# (instructions in README)
```

**Future (Phase 2):**
- `pip install isagawa-qa` (PyPI package)
- `isagawa init` CLI command for skills setup
- Server-side skills for stronger IP protection

---

### Topic 9: One-Page Positioning

**Decision Date:** 2025-12-27

**Context:**
- Isagawa is an AI Management Layer (internal thesis)
- QA Execution Engine is first product on the platform
- Risk: saying "AI Management Layer" explicitly invites fast followers
- Goal: own the category without handing competitors the playbook

**Strategic Insight:**

> Don't CLAIM the category. DEMONSTRATE it.

| Approach | Risk |
|----------|------|
| "We are the AI Management Layer" | Competitors copy the term, race to define it |
| "Isagawa enforces how AI executes work" | Competitors see behavior, can't copy implementation |

**Decision: Controlled Hybrid Positioning**

Categories are not owned by naming them. They're owned by enforcing a structure no one else has.

| Audience | What They See | What They Don't See |
|----------|---------------|---------------------|
| **Public MVP** | "Isagawa QA - Enforced AI Execution" | "AI Management Layer" |
| **Power users** | "Sits between humans and AI execution" | Category claim |
| **Internal/investors** | Full thesis: AI Management Layer | Nothing hidden |

---

**MVP Public Positioning:**

```
ISAGAWA QA
Enforced AI Execution for Test Automation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

What it does:
→ AI generates tests
→ Isagawa enforces they're correct
→ Nothing ships without passing gates

What makes it different:
→ Enforcement, not suggestions
→ Quality gates that cannot be bypassed
→ Domain expertise encoded as rules

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

First Pack: UI Automation
More packs coming.
```

---

**Language Rules:**

| USE publicly | DO NOT use publicly |
|--------------|---------------------|
| "Enforced execution" | "AI Management Layer" |
| "Non-bypassable quality gates" | "Category" |
| "Standards encoded as rules" | "Governance platform" |
| "AI that can't skip steps" | |

---

**Semi-Public Hints (power users, GitHub, talks):**

Dog-whistle to the right people without naming the category:
- "There's nothing above this except intent"
- "This sits between humans and AI execution"
- "Management logic encoded in software"

---

**Category Reveal Sequencing:**

1. **MVP:** Ship QA with enforcement messaging
2. **Validation:** Users say "first AI tool that forces correctness"
3. **Vertical #2:** Launch next domain
4. **Reveal:** "This is the AI Management Layer. QA was just the first engine."

---

**Why This Wins:**

1. **Copycats can't replicate enforcement speed**
   - They won't have the 11-step workflow
   - They won't have the quality gate architecture
   - They won't have the domain-encoding discipline
   - Words don't matter without machinery

2. **QA adoption creates proof, not dilution**
   - Categories are named after proof, not before it

3. **Category claim lands harder later**
   - After validation, the reveal is inevitable and credible

---

**What This Positioning Does:**
- Establishes ENFORCEMENT as the differentiator
- Doesn't hand competitors the category name
- Lets the category emerge from what you DO
- Positions QA as first vertical, with packs as expansion

**The category gets named later** - by analysts, press, users - based on what they experience. You own the behavior, they name the category.

---

### Topic 10: Context Reconstruction from Audit Trail

**Decision Date:** 2026-01-07

**Context:**
- Claude's context window has limits (200K tokens)
- Long workflows can exceed context window, causing conversation summarization
- When context is lost, detailed workflow data (personas, URLs, page names, method signatures) is gone
- Previously required restarting workflow from Step 1
- **Problem:** Limits maximum workflow complexity to what fits in context window

**Solution: Audit Trail as State Reconstruction Source**

| Aspect | Decision |
|--------|----------|
| **Metadata Capture** | Each gate logs lightweight summary of validation data to audit trail |
| **Metadata Format** | Counts + key identifiers, not full structures (90% smaller) |
| **Reconstruction Utility** | `utils/context_reconstructor.py` rebuilds workflow state from audit metadata |
| **Resume Capability** | Can resume from any completed step after context loss |

**Metadata Captured by Step:**

| Step | PRE Metadata | POST Metadata |
|------|-------------|---------------|
| **1** | - | credential_strategy, test_data_location |
| **2** | - | persona, URL, role_name, workflow |
| **3** | - | intent, scenarios_count, expected_states_count |
| **4** | workflow | scenarios_count |
| **5** | page_name, url, multi_page, total_pages | page_name, elements_count, pages_discovered, discovery_complete |
| **6** | page_name, elements_count | page_name, class_name, import_path, action_methods_count, state_methods_count, multi_page progress |
| **7** | task_name | class_name, import_path, task_methods_count |
| **8** | role_name | class_name, import_path, workflow_methods_count |
| **9** | scenarios_count | test_name, file_path |
| **10** | validated_layers, ready_for_save | - |

**Context Reconstruction Features:**
- `get_completed_steps()` - List of steps that passed
- `get_step_metadata(step)` - All metadata for a step (supports multi-page)
- `get_workflow_summary()` - Human-readable workflow progress
- `can_resume_from_step(step)` - Check if we have enough data to resume
- `reconstruct_state()` - Rebuild workflow_state.json structure

**Benefits:**
- **Unlimited workflow length** - No longer limited by context window
- **Resume from interruption** - Don't restart from Step 1
- **Multi-page support** - Each POM POST creates separate audit entry
- **Solves DEF-048** - Code reconstruction after context loss possible

**Implementation:**
- ✅ Enhanced `AuditLogger.log_gate()` with metadata parameter
- ✅ Updated `BaseGate.pass_response/fail_response/blocked_response()` with metadata parameter
- ✅ All gates (Steps 1-11) extract and pass metadata summaries
- ✅ Created `utils/context_reconstructor.py` utility
- ✅ Created `docs/CONTEXT_RECONSTRUCTION.md` documentation
- ✅ Demonstration test: `_dev_tests/test_context_reconstruction.py`

**Rationale:**
- Separates concerns: tool metadata (for generation) vs audit metadata (for tracking)
- Lightweight summaries keep audit files small (~2KB vs ~50KB for full metadata)
- Enables context-independent workflow execution
- Audit trail becomes authoritative source of truth

---

### Topic 11: Smart Gate Enforcement Patterns

**Decision Date:** 2026-01-07

**Context:**
- Traditional quality gates just validate inputs/outputs
- When gates fail, error messages don't teach AI how to fix the issue
- Three enforcement gaps discovered:
  1. Navigate method missing from POMs (DD-49 violation)
  2. Code reconstruction without POST validation (DEF-048)
  3. Audit write success not validated (DD-30 compliance)

**Decision: Smart Gates with Self-Teaching Errors**

| Aspect | Decision |
|--------|----------|
| **Pattern** | Minimal docs + smart enforcement + self-teaching error messages |
| **Error Format** | Violation + Pattern + Example + Fix |
| **Documentation Strategy** | Don't document every rule - enforce it in code with teaching errors |

**Smart Gate Implementations:**

**1. Navigate Method Enforcement (DEF-048 Resolution)**
- **Gate:** qg_page_object POST
- **Validates:** All POMs must have `navigate()` method (DD-49 compliance)
- **Enforcement:** Checks metadata.action_methods for "navigate", validates code doesn't call navigate_to() outside navigate()
- **Self-Teaching Error:**
  ```
  Pattern:
  def navigate(self) -> "LoginPage":
      '''Navigate to this page.'''
      self.web.navigate_to(self.web.config['url'] + '/path')
      return self

  Fix: Add navigate() method to the POM.
  ```

**2. Code Reconstruction Detection (DEF-048 Resolution)**
- **Gate:** qg_save_run PRE
- **Validates:** Reconstructed code must pass POST gate before saving
- **Enforcement:** Compares code against state, requires metadata proof if differs
- **Self-Teaching Error:**
  ```
  Pattern:
  1. Call qg_page_object POST validation with modified code
  2. If validation passes, provide metadata proof
  3. Then proceed to Step 10 save

  Fix: Validate reconstructed POM code through POST gate first.
  ```

**3. Audit Write Validation (DD-30 Enforcement)**
- **Gate:** BaseGate.pass_response (all gates)
- **Validates:** Audit file exists, writable, contains expected entry
- **Enforcement:** Checks directory exists, file exists, JSON valid, entry logged
- **Self-Teaching Error:**
  ```
  Pattern:
  1. Create tests/_audit/ directory
  2. Ensure write permissions
  3. Verify AuditLogger configuration

  Audit enforcement ensures DD-30 (Progressive Audit Trail) compliance.
  ```

**Benefits:**
- **Self-correcting system** - AI learns from error messages
- **Minimal documentation** - Rules are enforced, not just documented
- **Faster debugging** - Errors include fix patterns
- **Consistent enforcement** - Code enforces what docs describe

**Implementation:**
- ✅ `_validate_navigate_method()` in qg_page_object.py
- ✅ `_check_code_reconstruction()` in qg_save_run.py
- ✅ `_enforce_audit_write()` in base_gate.py
- ✅ All validation methods follow pattern: detect + explain + teach

**Rationale:**
- Gates become active teachers, not passive validators
- Reduces documentation burden (code IS documentation)
- Scales better than writing rules in markdown

---

### Topic 12: Production Test Findings - Critical Architecture Fixes

**Decision Date:** 2026-01-07

**Context:**
- Ran first production E2E test (ParaBank multi-page workflow)
- Discovered 3 critical failures that blocked test completion:
  1. Audit file reuse across runs (losing history)
  2. State not persisted per-run (context recovery impossible)
  3. Only 1 of 6 POMs saved to disk (multi-page workflow broken)

**Problem Analysis:**

**Failure #1: Audit File Overwriting**
```python
# base_gate.py:96-105 - BUG
existing_run_id = step_0_data.get("audit_run_id")  # Gets old run_id
if existing_run_id:
    cls._audit_logger = AuditLogger(run_id=existing_run_id)  # REUSES same file!
```
- Evidence: Only 1 audit file exists, last modified 13:38, but run_id from 10:19
- Root Cause: `workflow_state.json` never clears `step_0.audit_run_id`, so each new test run overwrites previous audit file
- Impact: Losing audit history, can't compare runs

**Failure #2: State Persistence Architecture Gap**
- Expected: `tests/_state/{run_id}/step_N.json` (per-run, per-step files)
- Actual: `mcp_server/state/workflow_state.json` (single monolithic file)
- Root Cause: Documentation described per-run state architecture, but StateManager was never updated to implement it
- Impact: No context recovery after compaction, no run isolation

**Failure #3: Multi-POM File Saving Bug**
- Expected: All 6 POMs saved to disk (LoginPage, OpenAccountPage, TransferFundsPage, AccountActivityPage, TestPage, ParabankRegistrationPage)
- Actual: Only ParabankRegistrationPage saved
- Evidence: `workflow_state.json` step_6.generated_poms has all 6 POMs with full code (577-4473 chars each)
- Root Cause: Step 10 didn't iterate through `generated_poms` dict, only saved last POM
- Impact: Multi-page workflows completely broken

**Decision: Immediate Write + Per-Run State Architecture**

| Aspect | Decision |
|--------|----------|
| **State Strategy** | One state file per run: `tests/_state/{run_id}/workflow_state.json` |
| **File Writing** | Write files IMMEDIATELY after generation (Steps 6-9), not in Step 10 |
| **Audit Run ID** | Always generate NEW run_id per workflow (never reuse from state) |
| **Step 10 Role** | Validation/verification step, not file writing step |
| **Recovery Mode** | Backup capability, not primary workflow |

**Rationale:**

**Why one file per run (not per step)?**
- ✅ Simpler implementation
- ✅ Atomic reads/writes
- ✅ Complete state snapshot in one place
- ✅ JSON size not an issue (<50KB typical)
- ✅ Easier to inspect and debug

**Why immediate file writes (not Step 10)?**
```
BEFORE (broken):
Step 6: Generate POM → Save to state (memory only)
Step 7: Generate Task → Save to state (memory only)
Step 8: Generate Role → Save to state (memory only)
Step 9: Generate Test → Save to state (memory only)
Step 10: Loop state → Write files ← CONTEXT LOSS HERE ❌

AFTER (fixed):
Step 6: Generate POM → Write file IMMEDIATELY → Save metadata to state ✅
Step 7: Generate Task → Write file IMMEDIATELY → Save metadata to state ✅
Step 8: Generate Role → Write file IMMEDIATELY → Save metadata to state ✅
Step 9: Generate Test → Write file IMMEDIATELY → Save metadata to state ✅
Step 10: Validate all files exist + run test ✅
```

**Benefits:**
- Files persisted immediately (crash-safe)
- Context loss doesn't matter (files already on disk)
- Step 10 becomes validation, not I/O
- Smart gates can verify files were written
- Eliminates entire class of "lost files due to context compaction" bugs

**Implementation Scope:**

| Component | Change | Priority |
|-----------|--------|----------|
| StateManager | Accept run_id, write to `tests/_state/{run_id}/workflow_state.json` | CRITICAL |
| BaseGate.get_audit_logger() | Always create NEW run_id (don't reuse from state) | CRITICAL |
| qg_page_object POST | Write POM file immediately after validation passes | CRITICAL |
| qg_task POST | Write Task file immediately after validation passes | CRITICAL |
| qg_role POST | Write Role file immediately after validation passes | CRITICAL |
| qg_test_runner POST | Write Test file immediately after validation passes | CRITICAL |
| qg_save_run PRE | Validate all expected files exist on disk | HIGH |
| Step skill references | Update Step 6-9 to write files, Step 10 to validate | HIGH |

**Smart Gate Enhancement:**

Step 10 PRE gate validates:
1. All expected files exist on disk (read from step metadata)
2. File contents match state metadata (checksums)
3. No missing POMs from multi-page workflows
4. Import paths are valid

**Defects Created:**
- DEF-049: Audit run_id reuse causes audit history loss
- DEF-050: State not persisted per-run (no context recovery)
- DEF-051: Multi-POM workflows only save 1 file (Step 10 bug)

---

### Topic 13: Smart Gate Unified Design - Dynamic Pattern Templates

**Decision Date:** 2026-01-10

**Context:**
- Smart Gate pattern defined in `execution_patterns.md` Pattern 3 has TWO layers
- Current state: Only 3 of 10 gates implement Gate Orchestration layer
- Current state: Code Generation layer NOT implemented
- Issue #5 (LoginPage failure): Tool complexity causes "existing_found" errors
- Issue #26 (self-heal masking): AI works around broken tools
- **Critical requirement:** Every user tests different sites - patterns must be domain-agnostic

**Smart Gate Two-Layer Pattern:**

| Layer | Pattern | Current Status | Target |
|-------|---------|----------------|--------|
| **Gate Orchestration** | Gate detects missing data → Provides fix → AI retries | ✅ Partial (3/10) | ✅ All 10 gates |
| **Code Generation** | Tool generates skeleton → Gate provides pattern → AI fills → Gate validates | ❌ Not implemented | ✅ Steps 6-9 |

**Decision: ALL Gates Use Dynamic Pattern Templates**

**Core Principle:**
> **Patterns are templates + dynamic data, NEVER hardcoded to specific sites/pages/elements.**

Every Smart Gate must provide:
1. **Pattern template** (generic structure)
2. **Dynamic data** (from discovery/state/metadata)
3. AI combines template + data for ANY site

**❌ WRONG - Hardcoded Patterns:**
```python
# Step 6 gate returns:
{
    "pattern": "Add LoginPage.navigate() method",  # Hardcoded "LoginPage"
    "fix": "Add EMAIL = (By.CSS_SELECTOR, '#email')"  # Hardcoded selector
}
```

**✅ CORRECT - Dynamic Pattern Templates:**
```python
# Step 6 gate returns:
{
    "pattern_template": "Add {page_name}.navigate() method",
    "dynamic_data": {
        "page_name": "LoginPage"  # From Step 5 state
    },
    "fill_instructions": {
        "locator_template": "{NAME} = (By.{BY_TYPE}, \"{locator}\")",
        "method_template": "def {action}_{element}(self, {params}): ...",
        "discovered_elements": [...]  # From Step 5, works for ANY site
    }
}
```

**Why Dynamic Templates:**
- User tests automationpractice.pl, ParaBank, Udemy, healthcare site, etc.
- Each site has different page names, elements, locators
- Gates cannot assume "LoginPage", "email", "#username", etc.
- Templates work for ALL sites, data comes from discovery

**Implementation Per Layer:**

**Layer 1: Gate Orchestration (All 10 Gates)**

Pattern provision format:
```python
{
    "status": "NEEDS_RETRY",
    "pattern_template": "...",  # Generic structure
    "dynamic_data": {...},       # Site-specific data
    "example": "..."             # Rendered example for this site
}
```

**Example - Step 5 (Multi-Page Detection):**
```python
# Dynamic scope_result provision:
{
    "status": "NEEDS_RETRY",
    "fix_applied": "scope_result",
    "scope_result": {
        "page_count": detected_page_count,  # Dynamic
        "pages": [
            {"name": inferred_page_name, "url": discovered_url}  # From BDD/nav
            for each discovered page
        ]
    }
}
```

**Layer 2: Code Generation (Steps 6-9)**

Skeleton + fill instructions format:
```python
{
    "status": "skeleton_ready",
    "skeleton_code": "...",  # Class structure only
    "fill_instructions": {
        "templates": {
            "locator": "{NAME} = (By.{BY_TYPE}, \"{locator}\")",
            "action_method": "def {action}_{element}(self, {params}) -> \"{class_name}\": ..."
        },
        "data": {
            "class_name": metadata.get("page_name"),  # Dynamic
            "elements": discovered_elements           # From Step 5
        }
    }
}
```

**Example - Step 6 (POM Generation):**

Tool 3 generates skeleton:
```python
class {page_name}:  # Placeholder, AI fills
    def __init__(self, web: WebInterface):
        self.web = web

    # LOCATORS - AI fills using template + data
    # METHODS - AI fills using template + data
```

Gate provides fill instructions:
```python
{
    "fill_instructions": {
        "templates": {
            "locator": "{NAME} = (By.CSS_SELECTOR, \"{selector}\")",
            "input_method": "def enter_{name}(self, text: str) -> \"{page_name}\":\n    self.web.type_text(*self.{NAME}, text=text)\n    return self",
            "click_method": "def click_{name}(self) -> \"{page_name}\":\n    self.web.click(*self.{NAME})\n    return self"
        },
        "data": {
            "page_name": "LoginPage",  # From Step 5
            "elements": [
                {"name": "email", "locator": "#email", "type": "input"},
                {"name": "submit", "locator": "#submit-btn", "type": "button"}
            ]
        }
    }
}
```

AI fills:
```python
class LoginPage:  # From data.page_name
    def __init__(self, web: WebInterface):
        self.web = web

    # Locators from template + data
    EMAIL = (By.CSS_SELECTOR, "#email")
    SUBMIT = (By.CSS_SELECTOR, "#submit-btn")

    # Methods from template + data
    def enter_email(self, text: str) -> "LoginPage":
        self.web.type_text(*self.EMAIL, text=text)
        return self

    def click_submit(self) -> "LoginPage":
        self.web.click(*self.SUBMIT)
        return self
```

**Gates Already Implementing Dynamic Patterns:**

| Gate | Step | Dynamic Pattern | Status |
|------|------|-----------------|--------|
| qg_discovered_elements | 5 | Calculates scope_result from BDD (any workflow) | ✅ Done |
| qg_task | 7 | Provides base_url pattern (any task class) | ✅ Done |
| qg_test_runner | 9 | Provides orchestration pattern (any role/workflow) | ✅ Done |

**Gates Need Dynamic Pattern Implementation:**

| Gate | Step | Dynamic Pattern Needed |
|------|------|------------------------|
| qg_preflight | 1 | Default strategies if missing (any project) |
| qg_user_input | 2 | Infer persona from URL (any site) |
| qg_ai_processing | 3 | Suggest expected_states from BDD (any workflow) |
| qg_test_scenarios | 4 | Provide scenario template if malformed (any domain) |
| qg_page_object | 6 | **Skeleton + fill instructions (any site/page)** |
| qg_role | 8 | **Skeleton + fill instructions (any role)** |
| qg_save_run | 10 | Regenerate missing code (any layer) |

**Implementation Phases:**

**Phase 0: Foundation (Task 26.0 - 4 hours)**
- Navigation tracking (validates dynamic scope_result)
- Test with parabank5

**Phase 1: Extend Dynamic Patterns to All Gates (Tasks 27.0-27.3 - 12 hours)**
- Add dynamic pattern provision to Steps 1-4, 6, 8, 10
- Verify no hardcoded page names, element names, selectors
- Outcome: All 10 gates use templates + dynamic data

**Phase 2: Skeleton-Only with Dynamic Fill Instructions (Tasks 28.0-35.0 - 56-70 hours)**
- Task 28.0: Protocol docs (skeleton + dynamic fill pattern)
- Task 29.0: Gates 6-9 PRE - Provide dynamic fill_instructions
- Tasks 30-33: Tools 3-6 skeleton-only (no hardcoded examples)
- Task 34.0: Gates 6-9 POST - Validate filled code
- Task 35.0: E2E test with multiple sites (automationpractice.pl + ParaBank)

**Total Effort:** 72-86 hours

**Success Criteria:**

Phase 1 (Dynamic Gate Orchestration):
- ✅ All 10 gates provide patterns as templates + data
- ✅ Zero hardcoded page names, element names, selectors in gate responses
- ✅ Test same workflow on 2 different sites → gates work for both

Phase 2 (Dynamic Code Generation):
- ✅ Tools 3-6 generate skeleton with placeholders
- ✅ Gates provide fill_instructions with templates + discovered data
- ✅ AI fills skeleton → works for ANY site
- ✅ Test parabank5 → Test automationpractice.pl → Both work with same gates
- ✅ Issue #5 eliminated (no existing check, skeleton always fresh)
- ✅ Self-heal eliminated (AI filling skeleton IS the design)

**Validation Test:**
```
Run same workflow (registration) on 3 different sites:
1. automationpractice.pl
2. ParaBank
3. New site never tested before

Expected: Gates provide dynamic templates + site-specific data
Result: All 3 workflows complete without gate code changes
```

**Rationale:**
- Every user tests different sites with different element names
- Hardcoded patterns fail on new sites
- Templates + dynamic data scale infinitely
- Proves Isagawa is domain-agnostic AI Management Layer
- Demonstrates platform applies to ANY vertical

**Mandatory Validation Loop (NO BYPASS):**

**CRITICAL ENFORCEMENT RULE:**
> Every time AI generates or modifies code (including self-heal), it MUST go through POST gate validation. NO EXCEPTIONS.

**The Loop (Steps 6-9):**
```
1. Code generated (Tool or AI) → POST gate validates → FAIL/PASS
2. If FAIL: Gate returns NEEDS_RETRY with pattern
3. AI fixes code → **MUST call POST gate again** (not optional!)
4. Repeat until POST gate returns "pass"
5. Only after "pass" → Save code → Proceed to next step
```

**Example - Step 6 (POM Generation):**
```
Attempt 1:
  Tool 3 generates skeleton → qg_page_object POST → FAIL (skeleton detected)
  Gate returns: NEEDS_RETRY with fill_instructions

Attempt 2:
  AI fills skeleton → **qg_page_object POST called again** → FAIL (missing navigate)
  Gate returns: NEEDS_RETRY with navigate pattern

Attempt 3:
  AI adds navigate() → **qg_page_object POST called again** → PASS
  Code saved → Proceed to Step 7
```

**Applies To:**
- Step 6: Every POM modification → qg_page_object POST
- Step 7: Every Task modification → qg_task POST
- Step 8: Every Role modification → qg_role POST
- Step 9: Every Test modification → qg_test_runner POST

**What Counts as "Code Generation/Modification":**
- Tool generates code
- AI self-heals tool output
- AI fills skeleton
- AI fixes gate validation errors
- AI reconstructs code from state
- **ALL of the above → POST gate validates**

**Blocked by Max Attempts:**
If 3 attempts fail (per Topic 3 self-heal cap), gate returns `"status": "blocked"` → User decision required (DD-22).

---

**Comprehensive Bypass Gap Analysis (All 10 Steps):**

**GOAL:** Identify EVERY scenario where data/code could bypass quality gates.

**Enforcement Principle:**
> Nothing proceeds to next step without gate validation. State saved AFTER gate passes. Files written AFTER gate passes.

**Step 1 (Preflight Configuration) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Missing strategy** | AI proceeds without credential_strategy or test_data_location | PRE gate blocks if missing |
| **Invalid strategy** | AI provides invalid strategy value | PRE gate validates against allowed values |
| **State saved early** | State saved before validation | State saves AFTER POST gate passes |

**Checkpoint:** qg_preflight POST validates → State saves → Step 2 allowed

---

**Step 2 (User Input) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Missing persona** | AI proceeds without persona | PRE gate blocks if missing |
| **Invalid URL** | AI provides malformed URL | PRE gate validates URL format |
| **Inferred data** | AI infers role_name without validation | POST gate validates inferred values |
| **State saved early** | State saved before validation | State saves AFTER POST gate passes |

**Checkpoint:** qg_user_input POST validates → State saves → Step 3 allowed

---

**Step 3 (AI Processing) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Missing BDD** | AI proceeds without proper Given/When/Then | POST gate validates BDD structure |
| **Missing expected_states** | AI skips expected_states extraction | POST gate requires expected_states array |
| **Malformed intent** | AI provides vague intent | POST gate validates intent clarity |
| **State saved early** | State saved before validation | State saves AFTER POST gate passes |

**Checkpoint:** qg_ai_processing POST validates → State saves → Step 4 allowed

---

**Step 4 (Test Scenarios) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Tool 1 not called** | AI skips Tool 1, generates scenarios directly | PRE gate checks Tool 1 was called |
| **Malformed scenarios** | Tool 1 returns incomplete scenarios | POST gate validates scenario structure |
| **Missing Given/When/Then** | Scenarios lack proper BDD format | POST gate validates all three sections present |
| **State saved early** | State saved before validation | State saves AFTER POST gate passes |

**Checkpoint:** qg_test_scenarios POST validates → State saves → Step 5 allowed

---

**Step 5 (Discovered Elements) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Tool 2 not called** | AI skips discovery, guesses elements | PRE gate checks discovery method used |
| **Empty elements** | No elements discovered for page | POST gate blocks if elements array empty |
| **Incomplete multi-page** | Only 2 of 4 pages discovered | PRE gate requires all pages in scope |
| **Missing locators** | Elements missing locator values | POST gate validates each element has locator |
| **State saved early** | State saved before validation | State saves AFTER POST gate passes for EACH page |

**Checkpoint:** qg_discovered_elements POST validates (PER PAGE) → State saves → Step 6 allowed

---

**Step 6 (POM Generation) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Tool 3 not called** | AI generates POM directly without tool | PRE gate checks tool was called OR skeleton ready |
| **Skeleton saved without fill** | Skeleton saved to disk without AI filling | POST gate blocks skeleton code |
| **File written before validation** | File written before POST gate passes | File write ONLY after POST gate "pass" |
| **Metadata saved without code** | Metadata saved but code invalid | POST gate validates code matches metadata |
| **Multi-page: only last validated** | 6 POMs generated but only last one goes through POST | Each POM must pass POST gate individually |
| **State saved early** | State saved before validation | State saves AFTER POST gate passes for EACH POM |
| **Code reconstruction skip** | AI reads POM from state, skips revalidation | Reconstructed code must pass POST gate |

**Checkpoint:** qg_page_object POST validates (PER POM) → File written → State saves → Step 7 allowed

---

**Step 7 (Task Generation) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Tool 4 not called** | AI generates Task directly without tool | PRE gate checks tool was called OR skeleton ready |
| **Skeleton saved without fill** | Skeleton saved to disk without AI filling | POST gate blocks skeleton code |
| **File written before validation** | File written before POST gate passes | File write ONLY after POST gate "pass" |
| **Locators in Task code** | Task contains locators (DD-27 violation) | POST gate detects and blocks locators |
| **State saved early** | State saved before validation | State saves AFTER POST gate passes |
| **Code reconstruction skip** | AI reads Task from state, skips revalidation | Reconstructed code must pass POST gate |

**Checkpoint:** qg_task POST validates → File written → State saves → Step 8 allowed

---

**Step 8 (Role Generation) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Tool 5 not called** | AI generates Role directly without tool | PRE gate checks tool was called OR skeleton ready |
| **Skeleton saved without fill** | Skeleton saved to disk without AI filling | POST gate blocks skeleton code |
| **File written before validation** | File written before POST gate passes | File write ONLY after POST gate "pass" |
| **State saved early** | State saved before validation | State saves AFTER POST gate passes |
| **Code reconstruction skip** | AI reads Role from state, skips revalidation | Reconstructed code must pass POST gate |

**Checkpoint:** qg_role POST validates → File written → State saves → Step 9 allowed

---

**Step 9 (Test Generation) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Tool 6 not called** | AI generates Test directly without tool | PRE gate checks tool was called OR skeleton ready |
| **Skeleton saved without fill** | Skeleton saved to disk without AI filling | POST gate blocks skeleton code |
| **File written before validation** | File written before POST gate passes | File write ONLY after POST gate "pass" |
| **Orchestration in test** | Test calls multiple role methods (architecture violation) | POST gate detects and provides pattern |
| **POM action calls in test** | Test calls POM methods directly | POST gate detects and blocks |
| **State saved early** | State saved before validation | State saves AFTER POST gate passes |
| **Code reconstruction skip** | AI reads Test from state, skips revalidation | Reconstructed code must pass POST gate |

**Checkpoint:** qg_test_runner POST validates → File written → State saves → Step 10 allowed

---

**Step 10 (Save & Run) - Bypass Gaps:**

| Gap | Scenario | Enforcement |
|-----|----------|-------------|
| **Files missing** | Not all expected files exist on disk | PRE gate validates all files present |
| **Files never validated** | Files exist but never passed POST gates | PRE gate checks audit log for POST passes |
| **State inconsistent with files** | State metadata doesn't match file contents | PRE gate validates checksums/signatures |
| **Multi-page POMs missing** | Only 2 of 4 POMs saved | PRE gate counts files vs scope_result |

**Checkpoint:** qg_save_run PRE validates all files exist and passed gates → Test execution allowed

---

**Cross-Cutting Enforcement Rules:**

| Rule | Enforcement |
|------|-------------|
| **State saves AFTER gate passes** | StateManager.save() only called after gate returns "pass" |
| **Files written AFTER gate passes** | File write operations only after POST gate "pass" |
| **Every code modification revalidated** | Tool output, AI fill, AI fix, reconstruction → all go through POST gate |
| **PRE gate before POST gate** | Cannot call POST without calling PRE first (validates prerequisites) |
| **Multi-page: validate each individually** | Step 6 with 4 pages → 4 separate POST gate calls |
| **No tool bypass** | AI cannot skip calling tool (PRE gate checks) |
| **Audit trail required** | Every gate call logged to audit trail (validates enforcement) |

---

**Implementation in Subtasks:**

Each task implementation must include comprehensive audit subtask:

**Subtask X.N: Audit - Verify No Bypass Gaps + Code Logic + Protocol + Smart Gate Compliance**

**Bypass Gap Checks:**
- ✓ State saves only after gate passes
- ✓ Files written only after gate passes
- ✓ All code goes through POST gate (no exceptions)
- ✓ PRE gate called before POST gate (no skip)
- ✓ Multi-page: Each item validated individually
- ✓ Audit trail logs all gate calls
- ✓ No tool bypass (AI cannot skip calling tool)
- ✓ No reconstruction bypass (read from state → revalidate)

**Code Logic Gaps:**
- ✓ Edge cases handled (empty arrays, null values, missing keys)
- ✓ Error handling present (try/catch, validation)
- ✓ No hardcoded values (page names, element names, selectors)
- ✓ Dynamic templates used (works for ANY site)
- ✓ Metadata matches code (action_methods_count accurate)
- ✓ File paths correct (framework/pages/, framework/tasks/, tests/)
- ✓ Import paths valid (can be imported without errors)
- ✓ No race conditions (sequential operations enforced)

**Protocol Compliance:**
- ✓ Follows step protocol in `.claude/skills/qa-management-layer/references/step-XX.md`
- ✓ Calls tools in correct order (Tool → PRE gate → AI fill → POST gate)
- ✓ Uses correct metadata contract (DD-26)
- ✓ Respects architecture rules (DD-27, DD-49, etc.)
- ✓ Credential strategy enforced (from Step 1)
- ✓ Test data location enforced (from Step 1)
- ✓ Multi-page workflow handled correctly (DD-44)
- ✓ Navigation tracking used (Task 26.0)

**Smart Gate Compliance (Both Layers):**
- ✓ **Layer 1 (Orchestration):** Gate provides data/pattern when missing
- ✓ **Layer 1:** Returns NEEDS_RETRY with fix_applied or pattern_template
- ✓ **Layer 1:** Dynamic templates + dynamic data (not hardcoded)
- ✓ **Layer 2 (Code Gen - Steps 6-9):** Tool generates skeleton
- ✓ **Layer 2:** Gate PRE provides fill_instructions with templates
- ✓ **Layer 2:** AI fills skeleton using patterns
- ✓ **Layer 2:** Gate POST validates filled code
- ✓ **Layer 2:** NEEDS_RETRY returns corrected pattern if wrong
- ✓ Validation loop enforced (fix → POST gate → fix → POST gate)
- ✓ Max attempts tracked (3 max per step)
- ✓ Blocked status returned after max attempts

**Execution Validation:**
- ✓ Test with parabank5 (multi-page workflow)
- ✓ Test with automationpractice.pl (different site)
- ✓ Verify no bypass scenarios occur
- ✓ Verify audit trail complete
- ✓ Verify all files saved correctly

**Design Decisions:**
- **DD-NEW-01:** All gates implement Smart Gate pattern (both layers)
- **DD-NEW-02:** Skeleton-only IS Smart Gate for code generation
- **DD-NEW-03:** NEEDS_RETRY status distinguishes fixable from fatal
- **DD-NEW-04:** Gates provide patterns, AI generates code
- **DD-NEW-05:** All patterns are templates + dynamic data, never hardcoded
- **DD-NEW-06:** Every code generation/modification MUST go through POST gate (no bypass allowed)

---

### Topic 14: Parabank5 Production Scrutiny - Semantic Validation Gaps

**Decision Date:** 2026-01-09

**Context:**
- Ran comprehensive scrutiny of parabank5 E2E test workflow
- Generated full test successfully (proves framework works end-to-end)
- Found 34 issues across 6 severity levels showing **what passes gates but shouldn't**
- **Critical Discovery:** Gates validate STRUCTURE (syntax, imports, patterns) but not SEMANTICS (business logic, strategy adherence)

**Issue Breakdown:**
- 4 CRITICAL: Business logic errors (same account transfer, credential violations, missing test data)
- 5 HIGH: Discovery isolation, missing field validation, LoginPage detection failure
- 8 MEDIUM: Code quality (unused methods, wrong patterns, duplicate locators)
- 9 LOW: Polish issues (better error messages, URL validation)
- 4 GATE FAILURES: Gates didn't catch semantic errors
- 4 ARCHITECTURAL: Missing rollback, transaction support

**Root Cause Analysis:**

**Problem #1: Business Logic Not Validated**
```python
# Test generates (PASSES all gates but WRONG):
user.transfer_funds_between_accounts(
    amount="100",
    from_account="15564",  # ❌ SAME ACCOUNT!
    to_account="15564"     # ❌ SAME ACCOUNT!
)

# qg_test_runner POST validates:
✓ AAA pattern correct
✓ POM state methods used for assertions
✓ Imports correct
✓ Orchestration correct (ONE workflow method call)
❌ Does NOT validate: from_account != to_account (semantic error)
```

**Why This Passed:** Gate checks **structure** (AAA pattern, assertions, imports) but not **semantics** (do parameters make business sense?).

**Problem #2: Step 1 Strategies Not Enforced**
```python
# Step 1: User selects
state.save(1, {
    "credential_strategy": "self-contained",  # Test should register user
    "test_data_location": "workflow"          # Data should be in tests/parabank5/data/
})

# Step 8: Role generated with HARDCODED credentials
self.email = "testuser20260108@example.com"  # ❌ From discovery, not self-contained
self.password = "Test123!"                    # ❌ Hardcoded, not registered in test

# Step 9: Test validation
✓ Test has AAA pattern
✓ Test uses fixtures correctly
❌ Does NOT check: credentials match strategy
❌ Does NOT check: test data files created in workflow location
```

**Why This Passed:** Gates don't read Step 1 state to validate downstream code honors user's strategy choices.

**Problem #3: Discovery Creates Real Accounts**
```python
# Step 5: AI uses Playwright to discover elements
mcp__playwright__browser_navigate("https://parabank.parasoft.com/parabank/register.htm")
mcp__playwright__browser_fill_form([
    {"name": "First Name", "value": "Test"},
    {"name": "Username", "value": "testuser20260108"},  # Creates REAL account!
    {"name": "Password", "value": "Test123!"}
])
mcp__playwright__browser_click("Register")

# Result: User account CREATED in ParaBank
# Test then hardcodes these credentials (not portable to other environments)
```

**Why This Happened:** No guidance that discovery should be read-only. AI defaulted to "create test data" during discovery.

**Problem #4: LoginPage Detection Failure (Issue #5)**
```python
# Parabank5 workflow has 2 pages:
# 1. LoginPage (initial entry point)
# 2. TransferFundsPage (after login)

# Expected: Step 5 discovers both pages → generates 2 POMs
# Actual: Step 5 only discovered TransferFundsPage → generated 1 POM

# Root Cause: BDD-based detection missed LoginPage
# Fix: Task 26.0 (Navigation Tracking) uses browser_navigate audit log instead
```

**Decision: Semantic Validation Layer**

| Aspect | Decision |
|--------|----------|
| **Business Logic Validation** | Gates detect semantic errors (same account transfer, unrealistic parameter values) |
| **Strategy Enforcement** | Gates validate code honors Step 1 strategies (credentials, test data location) |
| **Discovery Isolation** | Step 5 uses read-only mode (snapshots/existing accounts, no account creation) |
| **PRE Gate Fix Provision** | All PRE gates provide fix data on first failure (no retry loops) |
| **Navigation-Based Detection** | Step 5 uses audit log browser_navigate calls (not just BDD) for multi-page detection |

**Functional Requirements:**

### From Topic 14: Semantic Validation
- **FR-14.1:** qg_test_runner detects same-account transfers (validates from_account != to_account) **[Task 36.0]**
- **FR-14.2:** qg_role enforces credential_strategy from Step 1 (self-contained, static, dynamic) **[Task 36.0]**
- **FR-14.3:** qg_test_runner enforces test_data_location from Step 1 (shared, workflow, both) **[Task 36.0]**
- **FR-14.4:** qg_save_run PRE validates expected data files exist based on strategies **[Task 36.0]**
- **FR-14.5:** Step 5 discovery operates in read-only mode (no account creation in target app) **[Task 37.0]**
- **FR-14.6:** Playwright browser lifecycle managed (cleanup, no "already in use" errors) **[Task 37.0]**
- **FR-14.7:** All PRE gates provide fix_applied or pattern_template on first validation failure **[Task 39.0]**
- **FR-14.8:** qg_discovered_elements uses browser_navigate audit log for multi-page detection **[Task 26.0]**

**Implementation Scope:**

| Gap | FR | Task | Priority | v0.2 MVP? |
|-----|----|----|----------|-----------|
| Business logic + strategy enforcement | FR-14.1 to FR-14.4 | Task 36.0 | CRITICAL | ✅ YES |
| Discovery isolation | FR-14.5, FR-14.6 | Task 37.0 | CRITICAL | ✅ YES |
| Navigation-based detection | FR-14.8 | Task 26.0 | CRITICAL | ✅ YES |
| PRE gate fix provision | FR-14.7 | Task 39.0 | HIGH | ✅ YES |
| URL path validation | - | Task 40.0 | MEDIUM | ⬜ NO (defer v0.3) |
| Business assertion enforcement | - | Task 41.0 | MEDIUM | ⬜ NO (defer v0.3) |
| Rollback mechanism | - | Task 51.0 | ARCH | ⬜ NO (defer v0.3) |

**v0.2 MVP Scope (MUST HAVE):**
- ✅ Task 26.0: Navigation Tracking (fixes LoginPage detection Issue #5)
- ✅ Task 36.0: Semantic Validation (fixes Issues #1-4: business logic, strategies)
- ✅ Task 37.0: Discovery Isolation (fixes Issues #7, #11: account creation)
- ✅ Task 39.0: PRE Gate Enhancement (fixes Issue #6: retry loops)

**Test-in-Production Strategy:**
Complete one task → Re-run parabank5 workflow → Verify gates catch errors → Fix → Next task

**Estimated Effort:**
- Task 26.0: 4 hours (implementation + testing)
- Task 36.0: 10 hours (complex, 4 gates affected)
- Task 37.0: 6 hours (Playwright isolation + cleanup)
- Task 39.0: 5 hours (extends existing Smart Gate pattern)
- **Total:** ~25 hours for v0.2 MVP

**Success Criteria:**
- Parabank5 re-run with Task 36.0: Gates FAIL on same-account transfer, credential violations, missing data files
- Parabank5 re-run with Task 37.0: No new accounts created during Step 5 discovery
- Parabank5 re-run with Task 26.0: Both LoginPage + TransferFundsPage detected (2 POMs generated)
- Parabank5 re-run with Task 39.0: No retry loops for missing fields (gates provide fix data immediately)

---

---

## Summary of All Design Decisions

| Topic | Decision | Implementation |
|-------|----------|----------------|
| **1. Execution Modes** | Two modes: MIXED (default) and SKILLS_ONLY. No TOOLS_ONLY. | Hardcoded MIXED for MVP, env var for advanced users |
| **2. Audit Trail** | JSON per run: gates, sources, self-heals, files, errors, **metadata** | `audit_log_{timestamp}.json` in `tests/_audit/` ✅ |
| **3. Self-Heal Cap** | 3 retries per step, then blocked + DD-22 user decision | Gate tracks attempt count, returns `blocked` status |
| **4. Artifact Layout** | DEFERRED | Skills teach paths, no gate enforcement for MVP |
| **5. Adversarial Tests** | NOT A DESIGN TOPIC | QA task: run 5 edge cases through workflow |
| **6. Gate Drift** | NOT NEEDED | PRE gates already check previous step complete |
| **7. Smoke Matrix** | 2-3 sites, simple+medium+complex, Chrome only | Validation activity, not code change |
| **8. Packaging** | Manual clone + pip install, license-protected skills | README docs, license headers on skills |
| **9. Positioning** | Controlled hybrid: demonstrate, don't claim category | "Isagawa QA - Enforced AI Execution" |
| **10. Context Reconstruction** | Audit metadata enables state rebuild after context loss | `utils/context_reconstructor.py` ✅ |
| **11. Smart Gates** | Self-teaching error messages with patterns + examples | Navigate enforcement, code reconstruction detection, audit validation ✅ |
| **12. Production Fixes** | Immediate file writes + per-run state + fresh audit run_ids | StateManager refactor, gates write files immediately, Step 10 validates |
| **13. Smart Gate Unified Design** | ALL gates implement BOTH layers (orchestration + code gen) with dynamic templates | Phase 0: Task 26.0, Phase 1: Tasks 27.x (12h), Phase 2: Tasks 28-35 (56-70h) |
| **14. Parabank5 Scrutiny** | Gates must validate SEMANTICS (business logic, strategies), not just structure | v0.2 MVP: Tasks 26, 36, 37, 39 (25h total) |

---

## Core Architectural Principles (from Design Discussion)

### Principle 1: Generation is Replaceable, Enforcement is Not

> "Isagawa does not rely on generation. It relies on enforcement. Generation is replaceable."

- Tools = untrusted execution primitives (cheap, fast, unreliable labor)
- Skills = knowledge + intent
- Gates = law
- "Even when tools fail, law wins"

### Principle 2: Don't Claim the Category, Demonstrate It

> Categories are not owned by naming them. They're owned by enforcing a structure no one else has.

- Lead with ENFORCEMENT as differentiator
- Let "AI Management Layer" emerge from behavior
- Category reveal after validation, not before

### Principle 3: Platform + Packs Model

```
ISAGAWA CORE PLATFORM
├── Quality Gates Engine
├── Enforcement runtime
├── Audit & traceability
└── Pack runtime

PACKS (Domain-specific)
├── QA: UI Automation Pack (first)
├── Future: More QA packs
└── Future: Other verticals
```

---

## 4. Functional Requirements

### From Topic 1: Execution Modes
- FR-1.1: System supports MIXED execution mode (tools generate, AI self-heals)
- FR-1.2: System supports SKILLS_ONLY execution mode (AI generates directly)
- FR-1.3: Default mode is MIXED, configurable via `ISAGAWA_EXECUTION_MODE` env var
- FR-1.4: Audit trail captures execution source per step (Tool / AI / Self-Heal)

### From Topic 2: Audit Trail
- FR-2.1: Each workflow run creates `audit_log_{timestamp}.json`
- FR-2.2: Audit log captures: gates called, pass/fail, execution source, self-heal attempts
- FR-2.3: Audit log captures: files generated with paths
- FR-2.4: Audit log includes summary: total steps, gates passed/failed, self-heals count

### From Topic 3: Self-Heal Cap
- FR-3.1: Each step tracks retry count independently
- FR-3.2: Maximum 3 retries per step before blocking
- FR-3.3: On max retries, gate returns `blocked` status with attempt history
- FR-3.4: Blocked state triggers DD-22 (user decision required)

### From Topic 8: Packaging
- FR-8.1: All skill files include license header
- FR-8.2: README includes complete installation steps
- FR-8.3: LICENSE.md defines terms of use for skills

### From Topic 10: Context Reconstruction
- FR-10.1: Each gate logs metadata summary to audit trail (not full tool metadata)
- FR-10.2: Metadata includes counts, names, identifiers (not full structures)
- FR-10.3: ContextReconstructor utility can rebuild workflow state from audit metadata
- FR-10.4: Multi-page workflows create separate audit entries per POM
- FR-10.5: Can resume workflow from any completed step after context loss

### From Topic 11: Smart Gates
- FR-11.1: All POMs must have navigate() method (enforced by qg_page_object POST)
- FR-11.2: Reconstructed code must pass POST gate before saving (enforced by qg_save_run PRE)
- FR-11.3: Audit write success validated (enforced by BaseGate.pass_response)
- FR-11.4: Gate error messages include: violation + pattern + example + fix
- FR-11.5: Gates are self-teaching (AI learns from error messages)

### From Topic 12: Production Fixes
- FR-12.1: StateManager creates per-run directories: `tests/_state/{run_id}/workflow_state.json`
- FR-12.2: Each workflow run gets fresh audit run_id (never reused from state)
- FR-12.3: Quality gates write files immediately after validation (Steps 6-9)
- FR-12.4: Step 10 validates all expected files exist on disk
- FR-12.5: Multi-page workflows save ALL generated POMs to disk
- FR-12.6: File writes are crash-safe (files persisted before state saved)

---

## 5. Non-Goals (Out of Scope)

- TOOLS_ONLY execution mode (no value without skills/gates)
- User-facing execution mode selection (MVP keeps it simple)
- Multi-tenant support
- Cloud deployment

---

## 6. Success Metrics

1. Audit trail shows execution source for every code-generation step
2. Self-heal events are visible in run report
3. All 10 gates callable via MCP
4. E2E workflow completes with MIXED mode
5. Technical documentation explains architecture clearly

---

## 7. Open Questions

1. ~~Should we support TOOLS_ONLY mode?~~ **No** - decided Topic 1
2. Audit trail format: JSON, Markdown, or both? (Topic 2)
3. Max self-heal retries before stop? (Topic 3)
4. Path validation strictness? (Topic 4)

---

*This PRD is updated incrementally as design decisions are made.*
