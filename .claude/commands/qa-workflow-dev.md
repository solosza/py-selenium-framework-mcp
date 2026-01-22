---
description: Start 5-step QA test generation workflow (Development mode - full access with approval)
---

# QA Test Generation Workflow (Development)

You are starting the 5-step QA test generation workflow in **DEVELOPMENT** mode with collaborative construction.

## Instructions

1. **Read the skill first:**
   - Read `.claude/skills/qa-management-layer/SKILL.md` completely
   - Read `.claude/skills/qa-management-layer/references/step-01.md` for Step 1 guidance

2. **Prompt user for requirement:**

   Ask the user:
   ```
   What test do you want to generate?

   Please provide:
   - Persona (e.g., "guest", "registered user", "admin")
   - Target URL (e.g., "https://example.com/login")
   - What they want to do (e.g., "login with valid credentials")

   Example: "As a guest, I want to browse products on https://saucedemo.com"
   ```

3. **Execute the 5-step workflow** following the skill guidance:
   - Steps 1-3: Setup (User Input, Pre-flight, AI Processing)
   - Step 4: Collaborative Construction (Tool 1, Tool 2, then manual building with Edit/Write)
   - Step 5: Done (test execution and triage)

---

## Development Mode Permissions (DD-29)

**You are in DEVELOPMENT mode. Full access granted WITH USER APPROVAL.**

### You CAN modify (with user approval):
- `tests/` - Test files
- `framework/` - All framework code (pages, tasks, roles, interfaces)
- `mcp_server/` - MCP server code, tools, gates, generators
- `.claude/skills/` - Skill files
- `.claude/commands/` - Command files
- `docs/` - Documentation
- `CLAUDE.md`, `FRAMEWORK.md` - Configuration files

### CRITICAL: Approval Required for ALL Changes

**Before modifying ANY file, you MUST:**
1. Show the user what you intend to change (file path, summary of change)
2. Wait for explicit approval ("yes", "ok", "approved", "do it", etc.)
3. Only then make the change

**Never auto-commit, auto-fix, or auto-modify without user consent.**

### On Failure Behavior:

If a quality gate fails or tool produces an error:

1. **STOP** - Pause workflow
2. **ANALYZE** - Identify root cause (tool bug, gate bug, AI behavior, etc.)
3. **DISCUSS** - Report to user with options:
   ```
   Issue detected at Step [X].

   Error: [error message]
   Root cause: [analysis]

   Options:
   1. Fix the tool/gate code and retry (requires approval)
   2. I will fix manually - continue workflow
   3. Log defect and abort
   ```
4. **WAIT FOR APPROVAL** - Do not proceed until user chooses an option
5. **FIX** - Only if user approves option 1, fix the framework code
6. **LOG DEFECT** - Add entry to `docs/DEFECT_LOG.md` using standard format
7. **RESTART** - After fix, restart from Step 1 to verify clean run

### Defect Logging Format:

```markdown
### [DEF-XXX] Brief Description
**Severity:** CRITICAL | HIGH | MEDIUM | LOW
**Status:** OPEN
**Run ID:** YYYY-MM-DD-RX
**Caught By:** Step X (workflow name)
**Layer:** MCP Tool | Quality Gate | AI Orchestration | Skill
**File:** `path/to/file.py`

**Error Message:**
[exact error]

**Description:**
[what went wrong]

**Fix Required:**
[proposed fix]
```

---

Do NOT proceed to Step 2 until user provides their requirement.
