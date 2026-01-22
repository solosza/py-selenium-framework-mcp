---
description: Start 5-step QA test generation workflow (Production mode - restricted permissions)
---

# QA Test Generation Workflow (Production)

You are starting the 5-step QA test generation workflow with collaborative construction.

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

## CRITICAL: Production Mode Restrictions (DD-29)

**You are in PRODUCTION mode. The following restrictions apply:**

### You CAN generate/modify:
- `tests/` - Test files
- `framework/pages/` - Page object files
- `framework/tasks/` - Task files
- `framework/roles/` - Role files
- `tests/data/` - Test data files

### You CANNOT modify:
- `mcp_server/` - MCP server code, tools, gates, generators
- `.claude/skills/` - Skill files
- `.claude/commands/` - Command files
- `framework/interfaces/` - WebInterface
- `framework/resources/` - Core utilities
- `CLAUDE.md`, `FRAMEWORK.md` - Configuration files

### On Failure Behavior:

If a quality gate fails or tool produces an error:

1. **STOP** - Do not attempt to fix framework code
2. **REPORT** - Show the user:
   ```
   Workflow stopped due to an issue.

   Step: [step number]
   Error: [error message]

   This appears to be a framework issue. Please contact support or report at:
   https://github.com/[repo]/issues
   ```
3. **DO NOT** attempt to modify any files in the restricted list above
4. **DO NOT** retry with workarounds that modify framework internals

---

Do NOT proceed to Step 2 until user provides their requirement.
