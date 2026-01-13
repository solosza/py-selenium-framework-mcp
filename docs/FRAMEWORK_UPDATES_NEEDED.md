# FRAMEWORK.md Updates Needed

**Date:** 2026-01-07

## Changes Implemented (Need Documentation)

### 1. Audit Trail Metadata Capture (All Steps 1-10)
- **What Changed:** All quality gates now log lightweight metadata summaries to audit trail
- **Where to Document:** FRAMEWORK.md Section 9 (10-Step Workflow)
- **What to Add:**
  - Add "Audit Metadata" column to each step's table showing what metadata is captured
  - Update audit log schema examples to show metadata field
  - Reference `docs/CONTEXT_RECONSTRUCTION.md` for full details

**Example Addition (Step 6):**
```markdown
**Audit Metadata (POST):**
- page_name
- class_name
- import_path
- action_methods_count
- state_methods_count
- multi_page progress (if applicable)
```

### 2. Context Reconstruction Capability
- **What Changed:** New utility `utils/context_reconstructor.py` can rebuild workflow state from audit trail
- **Where to Document:**
  - FRAMEWORK.md Section 9 introduction (benefits)
  - New subsection: "9.11 Context Reconstruction"
- **What to Add:**
  ```markdown
  ### 9.11 Context Reconstruction from Audit Trail

  When context window overflows, use audit trail metadata to reconstruct workflow state.

  **Utility:** `utils/context_reconstructor.py`

  **Key Functions:**
  - `get_completed_steps()` - List of steps that passed
  - `get_step_metadata(step)` - All metadata for a step
  - `get_workflow_summary()` - Human-readable progress
  - `can_resume_from_step(step)` - Check if resumable
  - `reconstruct_state()` - Rebuild workflow_state.json

  **Benefits:**
  - Unlimited workflow length (no context window limits)
  - Resume from any completed step
  - Multi-page workflows fully tracked

  **Full Details:** See `docs/CONTEXT_RECONSTRUCTION.md`
  ```

### 3. Smart Gate Enforcement Patterns
- **What Changed:** Three new enforcement patterns implemented
  1. Navigate method enforcement (qg_page_object)
  2. Code reconstruction detection (qg_save_run)
  3. Audit write validation (BaseGate)
- **Where to Document:** FRAMEWORK.md Section 9 - add to each relevant step
- **What to Add:**

**Step 6 (qg_page_object POST):**
```markdown
**Smart Enforcement:**
- ✅ Navigate method required (DD-49)
  - Validates `navigate()` in action_methods
  - Validates `navigate_to()` only called inside navigate()
  - Self-teaching error with pattern + example if missing
```

**Step 10 (qg_save_run PRE):**
```markdown
**Smart Enforcement:**
- ✅ Code reconstruction detection (DEF-048)
  - Compares code against state
  - Requires POST gate validation proof if code differs
  - Prevents saving reconstructed code without quality gate
```

**All Gates (BaseGate.pass_response):**
```markdown
**Smart Enforcement:**
- ✅ Audit write validation (DD-30)
  - Validates audit directory exists
  - Validates audit file created
  - Validates JSON valid
  - Validates entry logged
```

### 4. Multi-Page POM Audit Tracking
- **What Changed:** Each POM POST creates separate audit entry with progress info
- **Where to Document:** FRAMEWORK.md Section 9.6 (Step 6)
- **What to Add:**
  ```markdown
  **Multi-Page Audit Trail:**
  For workflows with multiple POMs, each POST creates a separate audit entry:

  ```json
  {
    "step": 6,
    "gate": "qg_page_object",
    "mode": "POST",
    "result": "pass",
    "timestamp": "...",
    "metadata": {
      "page_name": "LoginPage",
      "class_name": "LoginPage",
      "import_path": "pages.auth.login_page",
      "action_methods_count": 4,
      "state_methods_count": 2,
      "multi_page": {
        "poms_generated": 1,
        "total_poms": 4,
        "generation_complete": false,
        "page_index": 1
      }
    }
  }
  ```

  This enables context reconstruction even if workflow is interrupted mid-POM generation.
  ```

## Recommended Update Order

1. ✅ Update FRAMEWORK.md Section 9 introduction to mention context reconstruction benefit
2. ✅ Add audit metadata to each step (Steps 1-10) in existing tables
3. ✅ Add smart enforcement notes to Steps 6, 10, and base gate description
4. ✅ Add new Section 9.11: Context Reconstruction
5. ✅ Update audit log schema example to show metadata field
6. ✅ Add reference to `docs/CONTEXT_RECONSTRUCTION.md` at top of Section 9

## Files That Need Updates

- `FRAMEWORK.md` - Section 9 (10-Step Workflow)
  - Add metadata column to step tables
  - Add smart enforcement callouts
  - Add Section 9.11 (Context Reconstruction)
  - Update audit schema examples

## Documentation Already Created

- ✅ `docs/CONTEXT_RECONSTRUCTION.md` - Complete context reconstruction guide
- ✅ `docs/projects/release-readiness/1-prd-release-readiness.md` - Topics 10-11 added
- ✅ `mcp_server/_dev_tests/test_context_reconstruction.py` - Demonstration test

## Related Design Decisions

- **DD-30:** Progressive Audit Trail - now includes metadata
- **DD-49:** Navigation responsibility - now enforced by smart gate
- **DEF-048:** Code reconstruction gap - now detected and blocked

---

**Status:** PRD fully updated ✅ | FRAMEWORK.md updates pending ⏳
