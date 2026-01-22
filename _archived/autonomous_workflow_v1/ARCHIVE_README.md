# Autonomous Workflow v1 - ARCHIVED

**Archived Date:** 2026-01-22
**Reason:** Replaced by pair programming workflow (5 steps)
**Success Rate:** 4% (96% required Step 11 manual fixes)

---

## What's Here

### Protocols (Steps 6-11)
- `step-06.md` - Generate POM (Tool 3)
- `step-07.md` - Generate Task (Tool 4)
- `step-08.md` - Generate Role (Tool 5)
- `step-09.md` - Generate Test Runner (Tool 6)
- `step-10.md` - Save & Run validation
- `step-11.md` - Execution & HITL triage

### Construction Gates
- `qg_page_object.py` - Validates Tool 3 output
- `qg_task.py` - Validates Tool 4 output
- `qg_role.py` - Validates Tool 5 output
- `qg_test_runner.py` - Validates Tool 6 output
- `qg_save_run.py` - Pre-save validation
- `qg_execution.py` - Test execution validation
- `qg_workflow_complete.py` - Meta-gate for workflow integrity

### Tools (Autonomous Generators)
- `tool_03_generate_page_object.py` - POM code generator
- `tool_04_generate_task.py` - Task code generator
- `tool_05_generate_role.py` - Role code generator
- `tool_06_generate_test_runner.py` - Test code generator

---

## Why Archived

**Problem with Autonomous Workflow:**
- AI generated code optimistically (Steps 1-10)
- 96% of tests failed on first run (Step 11)
- Required manual fixes to make tests pass
- High cost, low value - wasted time fixing AI mistakes

**New Approach (Pair Programming):**
- Human guides, AI builds incrementally
- Real-time validation at each step
- No Step 11 manual fixes needed
- Tests pass on first attempt

**Evidence:** Helios7 test demonstrated pair programming produces working code without rework.

---

## What Remains Active

**Steps 1-3 (Setup):** Retained and refined
- Step 1: User Input (`qg_user_input.py`)
- Step 2: Pre-flight Config (`qg_preflight.py`)
- Step 3: AI Processing (`qg_ai_processing.py`)

**Step 4 (Discovery):** Retained
- Tool 1: Generate BDD scenarios (`tool_01_generate_tests_from_user_story.py`)
- Tool 2: Discover elements (`tool_02_discover_page_elements.py`)
- Gates: `qg_test_scenarios.py`, `qg_discovered_elements.py`

**Step 5 (Construction):** NEW - Pair programming HITL loop
- AI builds code manually with Edit/Write tools
- Gates validate framework compliance
- No autonomous generation

---

## If You Need This Code

**Reinstatement:**
1. Identify specific file needed
2. Copy from `_archived/autonomous_workflow_v1/` back to original location
3. Update imports in `mcp_server/server.py`
4. Document why reinstated (in commit message)

**Do NOT:**
- Use as-is without understanding why it failed
- Reinstate entire workflow (defeats purpose of new approach)
- Assume autonomous generation is viable without evidence

---

## Migration Path

**For existing tests (helios1-7):**
- Archive to `tests/archive/`
- Reference as examples only
- Do NOT attempt to regenerate via autonomous workflow

**For new tests:**
- Use pair programming workflow (5 steps)
- Follow protocols in `.claude/skills/qa-management-layer/`
- Build incrementally, validate in real-time

---

**Last Updated:** 2026-01-22
