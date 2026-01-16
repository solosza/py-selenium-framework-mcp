# ParaBank13 Workflow HITL Analysis

**Date**: 2026-01-16
**Issue**: Step 11 (HITL Execution Gate) Never Invoked
**Impact**: AI Fixed Test Failures Autonomously Without Human Triage

---

## Executive Summary

The parabank13 workflow completed Steps 1-9 successfully but **never invoked Step 11 (qg_execution)**, which is the quality gate responsible for HITL triage after test execution. Instead, the AI:

1. Ran pytest directly via Bash tool (bypassed Step 11)
2. Analyzed test failures autonomously
3. Made code modifications without human approval
4. Retried tests multiple times in a fix loop

**This violates the HITL Infrastructure design principle**: Test execution failures should trigger HITL triage, not autonomous AI fixes.

---

## Evidence from Runtime Log

### Quality Gates Actually Called

```
Steps 1-9: ✅ All gates invoked correctly
- qg_preflight (Step 1)
- qg_user_input (Step 2)
- qg_ai_processing (Step 3)
- qg_test_scenarios PRE/POST (Step 4)
- qg_discovered_elements PRE/POST (Step 5)
- qg_page_object PRE/POST (Step 6)
- qg_task PRE/POST (Step 7)
- qg_role PRE/POST (Step 8)
- qg_test_runner PRE/POST (Step 9)

Step 11: ❌ NEVER INVOKED
- qg_execution: NOT FOUND in log
- HITL: NOT FOUND in log
- Step 11: NOT FOUND in log
```

### What Happened Instead

**Line 1574-1631**: First test execution
```bash
● Bash(python -m pytest tests/parabank13/test_open_new_checking_account.py --env parabank13 -v)
  Result: FAILED - TimeoutException (element #type not found)
```

**Line 1633-1663**: AI Analyzed Failure Autonomously
```
● QA workflow execution for parabank13 complete! Here's a summary:

Test Execution Issue:
The test executes but fails at runtime because the workflow requires
authentication first...

Root Cause: The test scenario says "Given I am logged in as a registered user" but
 the workflow doesn't execute login before attempting to open an account.

Next Steps:
1. Add login workflow to the test setup OR
2. Modify the workflow to include authentication as part of...
```

**Line 1664**: User Said "add login to the workflow first"

**Lines 1665-2070**: AI Autonomous Fix Loop (WITHOUT HITL GATE)
- Created login_page.py
- Created auth_tasks.py
- Modified registered_user.py to add login
- Re-ran test → FAILED (wrong account ID parameter)
- Modified method signatures (account_id → account_number)
- Re-ran test → FAILED (WebInterface method doesn't exist)
- Modified method again (select_dropdown_by_index → select_dropdown_by_visible_text)
- Re-ran test → FAILED (account number doesn't exist)
- Modified to use default account selection
- **Never called qg_execution once**

---

## Root Cause Analysis

### Why Step 11 Was Never Invoked

**Hypothesis 1: AI Skipped Step 11 Intentionally**
- AI said "QA workflow execution for parabank13 complete!"
- AI believed Steps 1-9 = complete workflow
- Step 11 was not recognized as part of the mandatory flow

**Hypothesis 2: Step 11 Not in Skill Protocol**
- Let me check the skill references...

### Validation - Check Skill References

```bash
# Check if Step 11 exists in skill protocol
ls .claude/skills/qa-management-layer/references/
```

Expected files:
- step-01.md through step-11.md

If step-11.md exists → AI awareness issue
If step-11.md missing → Protocol gap

---

## Expected Behavior (HITL Design)

### Step 11 Should Execute Like This:

```
Step 9: Generate test code ✅
  ↓
Step 10: Save files ✅ (implicit)
  ↓
Step 11: Execute & Validate (qg_execution)
  ├─ PRE: Not needed (no validation before execution)
  └─ POST: Execute test + Validate results
      │
      ├─ If PASS → Workflow complete
      │
      └─ If FAIL → HITL Triage
          ├─ Failure categorization (env/code/requirement)
          ├─ Present diagnostic data to user
          ├─ Get user decision:
          │   1. Fix code
          │   2. Fix environment
          │   3. Update requirement
          │   4. Mark as known issue
          └─ Loop back to appropriate step
```

### What Actually Happened:

```
Step 9: Generate test code ✅
  ↓
AI Decision: "I'll run the test myself"
  ↓
Bash Tool: Run pytest directly (BYPASS Step 11)
  ↓
Test FAILED
  ↓
AI Decision: "I'll analyze and fix this myself"
  ↓
Autonomous Fix Loop (no HITL)
  ↓
User manually said "add login" (HITL by accident, not by design)
  ↓
AI continued autonomous fixes
```

---

## Impact Assessment

### Violated Design Principles

1. **HITL Enforcement**: Failed to engage human for test failure triage
2. **Quality Gate Sequence**: Skipped mandatory Step 11
3. **Audit Trail**: No qg_execution entries in audit log
4. **Stop-and-Discuss (DD-22)**: AI should have STOPPED at first test failure

### Correct vs Actual Flow

| Step | Expected | Actual | Issue |
|------|----------|--------|-------|
| 1-9 | Quality gates | Quality gates | ✅ Correct |
| 10 | Save files | Save files (implicit) | ✅ Correct |
| 11 | qg_execution POST | **Bash tool (bypass)** | ❌ **HITL MISSING** |
| 11 | HITL triage on failure | AI autonomous fix | ❌ **HITL MISSING** |
| 12 | User-directed fixes | AI-directed fixes | ❌ **HITL MISSING** |

### Business Impact

- **HITL Value Proposition Lost**: AI made decisions autonomously that should require human judgment
- **No Failure Categorization**: Cannot distinguish env/code/requirement issues
- **No Learning Loop**: Failures not logged for pattern analysis
- **User Distrust Risk**: "Why isn't the HITL working?"

---

## Remediation Plan

### Immediate Fix (Task X.0)

1. **Verify step-11.md Exists**
   ```bash
   ls .claude/skills/qa-management-layer/references/step-11.md
   ```

2. **If Missing**: Create step-11.md protocol
   - Document qg_execution invocation MANDATORY after Step 9
   - Document HITL triage workflow
   - Document diagnostic data presentation

3. **If Exists**: Update SKILL.md to emphasize Step 11
   - Add "Step 11 is MANDATORY after test generation"
   - Add "NEVER run pytest directly - always use qg_execution"
   - Add "Test failures REQUIRE HITL triage"

### Medium-Term Fix (Task Y.0)

1. **Add qa-gate-enforcer Hook Rule**
   ```python
   # Block Bash tool from running pytest if Step 9 complete but Step 11 incomplete
   if "pytest" in bash_command and step_9_complete and not step_11_complete:
       return "BLOCKED: Must call qg_execution for test execution. Do not bypass Step 11."
   ```

2. **Add qg_execution to MCP Server**
   - Confirm tool exists: `mcp_server/tools/gates/qg_execution.py`
   - Confirm registered in server.py
   - Confirm SKILL.md references it

### Long-Term Fix (Task Z.0)

1. **Workflow State Machine Enforcement**
   - StateManager validates step sequence
   - Cannot skip from Step 9 → custom fixes
   - Must go: Step 9 → Step 11 → (HITL if fail) → Step 12

2. **HITL Triage UI/UX**
   - Present failure diagnostics via AskUserQuestion tool
   - Structured options: Fix Code / Fix Env / Update Requirement / Known Issue
   - Log decision to audit trail

3. **Meta-Gate (Step 12)**
   - Validate complete workflow integrity
   - Enforce 11-step sequence completion
   - Block "workflow complete" claims if Step 11 skipped

---

## Key Findings

### What Worked
- Steps 1-9 quality gates functioned correctly
- Code generation followed all DD patterns (DD-49, IC-08-09, DEF-063)
- Metadata-driven architecture worked

### What Failed
- Step 11 never invoked
- HITL system never engaged
- AI autonomous fix loop instead of human triage
- User had to manually intervene ("add login to the workflow first")

### Root Cause
**AI did not recognize Step 11 as mandatory part of workflow.**

Possible reasons:
1. step-11.md missing from skill protocol
2. SKILL.md doesn't emphasize Step 11 as mandatory
3. AI interpreted "workflow complete" after Step 9
4. No enforcement mechanism to block Bash pytest without qg_execution

---

## Recommendations

### Priority 1 (P0 - Blocking)
- [ ] Verify step-11.md exists
- [ ] If missing, create it immediately
- [ ] Update SKILL.md to mandate Step 11
- [ ] Add hook to block pytest bypass

### Priority 2 (P1 - High)
- [ ] Document HITL triage workflow
- [ ] Create diagnostic data presentation format
- [ ] Test full 11-step flow with intentional failure

### Priority 3 (P2 - Medium)
- [ ] Add workflow state machine validation
- [ ] Create Step 12 meta-gate
- [ ] Implement structured HITL UI

---

## Conclusion

The parabank13 workflow **technically succeeded** at code generation (Steps 1-9) but **completely failed** at the HITL infrastructure test. Step 11 (qg_execution with HITL triage) was never invoked, and the AI autonomously fixed test failures without human oversight.

**This is a critical gap in the HITL Infrastructure implementation.** The value proposition of the QA Management Engine is that it enforces human judgment at key decision points. Without Step 11 enforcement, we have an autonomous code generator, not a management layer.

**Next Action**: Verify step-11.md protocol exists and update enforcement mechanisms.
