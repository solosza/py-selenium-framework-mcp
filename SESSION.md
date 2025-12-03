# Session State - 2025-12-02 (Current)

## Current Phase
**Phase:** Phase B - MCP Tool Refactor (B.6.5 Metadata Architecture)
**Status:** Documentation Complete, Ready for Testing
**Resume Word:** METADATA-TEST

## What We're Working On
**Active Task:** B.6.5 - Implement Metadata-Passing Architecture
**Task Status:** In Progress (60%)

## Progress This Session

### Completed
- [x] Documented complete MCP workflow in FRAMEWORK.md Section 8
- [x] Added Steps 1-9 with visual diagrams
- [x] Added AI prompting rules for ALL steps (Step 2 + Tools 1-6)
- [x] Added 15 Design Decisions (DD-01 through DD-15)
- [x] Deleted TOOL_ORDER.md (consolidated into FRAMEWORK.md)
- [x] Clarified: domain vs workflow vs intent terminology
- [x] Clarified: expected_states extraction from BDD "Then" clause
- [x] Clarified: check existing before creating new pattern
- [x] Clarified: one test file per scenario pattern

### Key Design Decisions Made This Session
| ID | Decision |
|----|----------|
| DD-01 | User must specify persona in requirement ("As a...") |
| DD-02 | URL required upfront with requirement |
| DD-03 | Metadata context accumulated through tool chain |
| DD-04 | Single documentation source (FRAMEWORK.md) |
| DD-05 | Exact method names emerge from tool chain, not upfront |
| DD-06 | AI extracts intent, not exact method names |
| DD-07 | Domain determined by AI in Step 2, passed through metadata |
| DD-08 | AI orchestrates tool chain, tools don't call other tools |
| DD-09 | AI extracts expected_states from BDD "Then" clause |
| DD-10 | Action methods derived from element types |
| DD-11 | State method naming: is_*/has_* for bool, get_* for values |
| DD-12 | Check existing classes/methods before generating new |
| DD-13 | Each tool has specific AI prompting rules |
| DD-14 | One test file per scenario, grouped by domain folder |
| DD-15 | Test assertions use POM state methods from metadata |

## Files Changed This Session
- `FRAMEWORK.md` - Added Section 8: MCP Tool Chain & AI Workflow (Steps 1-9, Design Decisions, Prompting Rules)
- `CLAUDE.md` - Added MCP Tool Usage section with mandatory rules and NO HALLUCINATIONS policy
- `mcp_server/tools/TOOL_ORDER.md` - DELETED (consolidated into FRAMEWORK.md)

## Remaining Work (in order)
1. **Test Tool 3 → Tool 4 metadata flow** ← NEXT
2. Refactor `role_generator.py` to accept Task metadata
3. Update `tool_05_generate_role.py`
4. Refactor `test_generator.py` to accept Role + POM metadata
5. Update `tool_06_generate_test_runner.py`
6. Test full metadata chain with E2E test
7. Run E2E test with visible browser
8. If passes, mark DEF-021/022/023/024 as RESOLVED
9. Continue to B.7, B.8, B.9

## Context for Next Session

**Resume Word:** METADATA-TEST

**Resume Point:** Test Tool 3 → Tool 4 metadata flow before continuing to refactor Role and Test generators.

**Key Files:**
- `FRAMEWORK.md` Section 8 - Complete MCP workflow documentation
- `mcp_server/utils/generators/page_object_generator.py` - Has `generate_page_object_with_metadata()`
- `mcp_server/utils/generators/task_generator.py` - Has `generate_task_with_metadata()`
- `mcp_server/tools/tool_03_generate_page_object.py` - Returns metadata
- `mcp_server/tools/tool_04_generate_task.py` - Accepts POM metadata

**Test Location:** `mcp_server/_dev_tests/`

**What to Test:**
1. Call Tool 3 with elements → get POM code + metadata
2. Pass POM metadata to Tool 4 → get Task code + metadata
3. Verify Task methods call actual POM methods (no hardcoded names)

## Defects Status
| ID | Description | Status |
|----|-------------|--------|
| DEF-021 | Invalid import syntax | IN_PROGRESS |
| DEF-022 | Duplicate locator names | IN_PROGRESS |
| DEF-023 | Duplicate method names | IN_PROGRESS |
| DEF-024 | Placeholder test logic | IN_PROGRESS |

Note: All marked IN_PROGRESS - cannot mark RESOLVED until E2E test passes.

## Todo List State
```
[x] Update tool_04_generate_task.py to use metadata-driven generator
[x] Document MCP workflow Step 1 & 2 in FRAMEWORK.md
[x] Document MCP workflow Step 3 (Tool 1) in FRAMEWORK.md
[x] Document MCP workflow Step 4 (Tool 2) in FRAMEWORK.md
[x] Document MCP workflow Step 5 (Tool 3) in FRAMEWORK.md
[x] Document MCP workflow Steps 6-9 (Tools 4-6 + Save)
[x] Delete TOOL_ORDER.md (consolidated into FRAMEWORK.md)
[ ] Test Tool 3 → Tool 4 metadata flow ← NEXT
[ ] Refactor role_generator.py to accept Task metadata
[ ] Refactor test_generator.py to accept Role + POM metadata
[ ] Test full metadata chain with E2E test
```

---
**Last Updated:** 2025-12-02
