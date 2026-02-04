# Prove It Works - Pre-Ship Verification

Concrete evidence that changes work. Use before PR, merge, or deploy.

## Instructions

Gather evidence from the work done in this session.

**Execute:**
```
PROVE IT WORKS

Demonstrating changes work...

═══════════════════════════════════════════════════════
1. DIFF ANALYSIS
═══════════════════════════════════════════════════════

BEHAVIOR BEFORE:
- [How it worked before]

BEHAVIOR AFTER:
- [How it works now]

FILES CHANGED:
- [file1.py]: [what changed]
- [file2.py]: [what changed]

═══════════════════════════════════════════════════════
2. TEST EVIDENCE
═══════════════════════════════════════════════════════

TESTS RUN:
- [test name]: [PASS/FAIL]
- [test name]: [PASS/FAIL]

COVERAGE: [X% if applicable]

NEW TESTS ADDED:
- [test name]: [what it covers]

═══════════════════════════════════════════════════════
3. MANUAL VERIFICATION
═══════════════════════════════════════════════════════

TO VERIFY MANUALLY:
1. [Step 1]
2. [Step 2]
3. [Step 3]

EXPECTED OUTCOME:
[What you should see]

═══════════════════════════════════════════════════════
4. RISK ASSESSMENT
═══════════════════════════════════════════════════════

COULD THIS BREAK ANYTHING?
- [Area 1]: [Risk level - Low/Med/High]
- [Area 2]: [Risk level - Low/Med/High]

ROLLBACK PLAN:
[How to revert if something goes wrong]
```

**HITL (if destructive operation follows):**
```
READY TO SHIP

Next operation: [git push / deploy / sync / etc.]

1. Proceed with operation
2. Run dry-run first
3. Abort

Select (1-3):
```

If dry-run selected, show preview then re-prompt.
