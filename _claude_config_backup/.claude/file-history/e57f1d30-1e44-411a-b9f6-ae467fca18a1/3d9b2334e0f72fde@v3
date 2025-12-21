# Research Notes: Claude Agent SDK

**Task:** 1.0 Research & Spike
**Date:** 2025-12-16
**Status:** Complete

---

## Visual Overview

### Agent Validation Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VALIDATION RUN                                     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR AGENT (Claude Agent SDK)                                         │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  system_prompt: "You are a QA validation supervisor..."                 ││
│  │  allowed_tools: [get_scenario, validate_artifacts, Task, Read, Glob]    ││
│  │  mcp_servers: {validation: in-process, qa-automation: external}         ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
          │
          │ Step 1: Get test input
          ▼
┌─────────────────────────────────────────┐
│  @tool("get_scenario")                  │
│  SR QA ENGINEER (in-process)            │
│  ├── Input: complexity level            │
│  └── Output: persona + requirement + URL│
└─────────────────────────────────────────┘
          │
          │ Returns Step 1 input
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR receives input, invokes Task tool                                │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          │ Step 2-8: Run tool chain
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  Task tool → ORCHESTRATOR (Claude Code + MCP)                                │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │  Step 2: AI Processing (extract role, domain, BDD, expected_states)     ││
│  │  Step 3: Tool 1 - generate_tests_from_user_story                        ││
│  │  Step 4: Tool 2 - discover_page_elements                                ││
│  │  Step 5: Tool 3 - generate_page_object                                  ││
│  │  Step 6: Tool 4 - generate_task                                         ││
│  │  Step 7: Tool 5 - generate_role                                         ││
│  │  Step 8: Tool 6 - generate_test_runner                                  ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│  └── Output: Generated artifacts (POM, Task, Role, Test files)              │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          │ Returns generated artifacts
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR receives artifacts, invokes Reviewer                             │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          │ Validate before Step 9
          ▼
┌─────────────────────────────────────────┐
│  @tool("validate_artifacts")            │
│  REVIEWER (in-process)                  │
│  ├── Input: artifact paths              │
│  ├── Reads: FRAMEWORK.md Section 4      │
│  ├── Checks: All 22 DDs                 │
│  └── Output: APPROVE / REJECT + details │
└─────────────────────────────────────────┘
          │
          ├── REJECT ──→ STOP, Report Failure
          │
          │ APPROVE
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR → Step 9: Execute test                                           │
│  └── Bash tool: pytest tests/...                                            │
└─────────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SUPERVISOR generates validation report                                      │
│  └── Pass/Fail, violations, artifacts, logs                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### SDK Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        CLAUDE AGENT SDK                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐       │
│  │  Built-in Tools  │    │  Custom Tools    │    │  MCP Servers     │       │
│  ├──────────────────┤    ├──────────────────┤    ├──────────────────┤       │
│  │  Read            │    │  @tool decorator │    │  External (stdio)│       │
│  │  Write           │    │  In-process MCP  │    │  qa-automation   │       │
│  │  Edit            │    │  Python functions│    │                  │       │
│  │  Bash            │    │                  │    │  In-process      │       │
│  │  Glob            │    │  get_scenario    │    │  validation      │       │
│  │  Grep            │    │  validate_artif. │    │                  │       │
│  │  Task (subagent) │    │                  │    │                  │       │
│  └──────────────────┘    └──────────────────┘    └──────────────────┘       │
│           │                       │                       │                  │
│           └───────────────────────┼───────────────────────┘                  │
│                                   │                                          │
│                                   ▼                                          │
│                    ┌──────────────────────────┐                              │
│                    │    ClaudeAgentOptions    │                              │
│                    │    ├── system_prompt     │                              │
│                    │    ├── allowed_tools     │                              │
│                    │    ├── mcp_servers       │                              │
│                    │    ├── hooks             │                              │
│                    │    └── permission_mode   │                              │
│                    └──────────────────────────┘                              │
│                                   │                                          │
│                                   ▼                                          │
│                    ┌──────────────────────────┐                              │
│                    │      query() / Client    │                              │
│                    │      Async streaming     │                              │
│                    └──────────────────────────┘                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Failure Handling Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FAILURE TYPES                                        │
└─────────────────────────────────────────────────────────────────────────────┘

TYPE 1: VALIDATION FAILURE (Reviewer rejects)
─────────────────────────────────────────────
    Generated Code ──→ Reviewer ──→ DD Violation Found
                                          │
                                          ▼
                              ┌─────────────────────┐
                              │  STOP IMMEDIATELY   │
                              │  Report: REJECT     │
                              │  Details: DD-XX     │
                              │  File: path:line    │
                              └─────────────────────┘

TYPE 2: EXECUTION FAILURE - GOOD (Test finds app bug)
─────────────────────────────────────────────────────
    Generated Code ──→ Reviewer ──→ APPROVE ──→ Execute ──→ Test Fails
                                                               │
                                                               ▼
                                               ┌─────────────────────────┐
                                               │  SUCCESS (for us)       │
                                               │  Test correctly found   │
                                               │  bug in target app      │
                                               └─────────────────────────┘

TYPE 3: EXECUTION FAILURE - BAD (Framework issue)
─────────────────────────────────────────────────
    Generated Code ──→ Reviewer ──→ APPROVE ──→ Execute ──→ Test Fails
                                                               │
                                                     (bad locator, timing)
                                                               │
                                                               ▼
                                               ┌─────────────────────────┐
                                               │  STOP IMMEDIATELY       │
                                               │  Report: FAIL           │
                                               │  Type: Framework Issue  │
                                               └─────────────────────────┘

TYPE 4: AGENT FAILURE (System crash)
────────────────────────────────────
    Any Agent ──→ Exception/Crash
                        │
                        ▼
         ┌─────────────────────────┐
         │  STOP IMMEDIATELY       │
         │  Report: SYSTEM ERROR   │
         │  Fix agent, restart     │
         └─────────────────────────┘
```

---

## Design Decisions (Agent Validation)

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-AVS-01 | Use Claude Agent SDK for all agents | Official SDK, built-in tools, MCP support |
| DD-AVS-02 | Supervisor is main agent, others are tools | Simpler than multi-process, SDK native pattern |
| DD-AVS-03 | SR QA Engineer as in-process custom tool | Simple output, no external dependencies |
| DD-AVS-04 | Reviewer as in-process custom tool | Can read files directly, check patterns |
| DD-AVS-05 | Orchestrator via Task tool | Needs full Claude Code + MCP capabilities |
| DD-AVS-06 | Stop immediately on any failure | Fail fast, investigate, fix, restart |
| DD-AVS-07 | Pre-defined scenarios in YAML | Reproducible, version controlled |
| DD-AVS-08 | Full validation report on completion | Audit trail, debugging support |
| DD-AVS-09 | Human escalation for DD-21/DD-22 | Complex scenarios need human guidance |
| DD-AVS-10 | Test finds app bug = SUCCESS | Validates test generation works |

### DD-AVS-01: Use Claude Agent SDK

**Decision:** Use Claude Agent SDK (Python) for all agent implementation.

**Rationale:**
- Official Anthropic SDK
- Same capabilities as Claude Code
- Built-in tools (Read, Write, Bash, etc.)
- MCP server support (external and in-process)
- Subagent support via Task tool
- Hooks for validation/logging

**Alternatives Considered:**
- Raw Anthropic API + custom tool loop → More work, reinvent wheel
- LangChain/LangGraph → Different ecosystem, less Claude-native
- Custom framework → No benefit over official SDK

### DD-AVS-02: Supervisor as Main Agent

**Decision:** Supervisor is the main SDK agent; others are tools/subagents.

**Rationale:**
- SDK's native pattern (one main agent, delegate via tools/Task)
- Simpler than multi-process coordination
- Built-in context management
- Single entry point for validation runs

**Pattern:**
```python
# Supervisor is the main agent
async for message in query(
    prompt="Run validation for easy scenario",
    options=ClaudeAgentOptions(
        system_prompt="You are a QA validation supervisor...",
        allowed_tools=["get_scenario", "validate_artifacts", "Task", "Bash"]
    )
):
    process(message)
```

### DD-AVS-06: Stop Immediately on Failure

**Decision:** Stop validation run immediately on any failure (Type 1, 3, or 4).

**Rationale:**
- Fail fast principle
- Earlier failures may cause cascading issues
- Human needs to investigate and fix
- No point continuing with broken state

**Exception:** Type 2 (test finds app bug) is NOT a failure for us.

---

## Summary

The Claude Agent SDK is the official way to build AI agents using Claude Code capabilities. It provides everything we need for the QA validation agent system.

**Key Finding:** We can build all 3 agents (Supervisor, SR QA Engineer, Reviewer) using the Claude Agent SDK with full MCP tool support.

---

## SDK Overview

### What It Is

The Claude Agent SDK gives you the same tools, agent loop, and context management that power Claude Code, programmable in Python and TypeScript.

### Installation

```bash
pip install claude-agent-sdk
```

**Requirements:**
- Python 3.10+
- Claude Code CLI (bundled with SDK, or install separately)
- `ANTHROPIC_API_KEY` environment variable

---

## Key Capabilities (Relevant to Our Project)

### 1. Built-in Tools

Same tools as Claude Code, available out of the box:

| Tool | What it does | Our Use Case |
|------|--------------|--------------|
| **Read** | Read any file | Reviewer reads generated artifacts |
| **Write** | Create new files | - |
| **Edit** | Make precise edits | - |
| **Bash** | Run terminal commands | Execute tests |
| **Glob** | Find files by pattern | Find generated files |
| **Grep** | Search file contents | Search for DD violations |
| **WebSearch** | Search the web | - |
| **WebFetch** | Fetch web content | - |
| **Task** | Spawn subagents | Supervisor delegates to workers |

### 2. MCP Server Support

**Critical for our project:** Can connect to external MCP servers.

```python
options = ClaudeAgentOptions(
    mcp_servers={
        "qa-automation": {
            "command": "python",
            "args": ["mcp_server/server.py"]
        }
    }
)
```

This means the Orchestrator (Claude Code + SDK) can invoke our existing MCP tools (Tool 1-6).

### 3. Subagents (Task Tool)

Enable the `Task` tool to let Claude spawn subagents for complex tasks.

```python
options = ClaudeAgentOptions(
    allowed_tools=["Read", "Glob", "Grep", "Task"]
)
```

**Our Use Case:** Supervisor can use Task to delegate to SR QA Engineer and Reviewer.

### 4. Custom Tools (In-Process MCP)

Can create custom Python functions as tools:

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("validate_dd", "Validate code against Design Decisions", {"code": str, "dd_id": str})
async def validate_dd(args):
    # Custom validation logic
    return {"content": [{"type": "text", "text": f"DD-{args['dd_id']}: PASS"}]}

server = create_sdk_mcp_server(
    name="reviewer-tools",
    version="1.0.0",
    tools=[validate_dd]
)
```

**Our Use Case:** Reviewer agent can have custom DD validation tools.

### 5. Hooks

Run custom code at key points in the agent lifecycle:

- `PreToolUse` - Before tool execution
- `PostToolUse` - After tool execution
- `Stop` - When agent completes
- `SessionStart` / `SessionEnd`

**Our Use Case:**
- Log all tool invocations for audit
- Block certain operations
- Inject validation at key points

### 6. Sessions

Maintain context across multiple exchanges:

```python
# First query - capture session ID
async for message in query(prompt="Read the authentication module"):
    if hasattr(message, 'subtype') and message.subtype == 'init':
        session_id = message.data.get('session_id')

# Resume with context
async for message in query(prompt="Now validate it", options=ClaudeAgentOptions(resume=session_id)):
    pass
```

**Our Use Case:** Maintain context through the 9-step process.

---

## Architecture Decision

### Option A: Single Agent with Subagents (Recommended)

Use the SDK's built-in `Task` tool for subagent delegation:

```
Supervisor Agent (SDK)
├── Uses Task tool to spawn SR QA Engineer
├── Uses Task tool to invoke Orchestrator (Claude Code)
├── Uses Task tool to spawn Reviewer
└── Aggregates results
```

**Pros:**
- Uses SDK's native subagent pattern
- Simpler implementation
- Built-in context management

**Cons:**
- All agents share same SDK instance
- Less isolation between agents

### Option B: Separate Agent Processes

Each agent is a separate Python process:

```
Supervisor (SDK Process 1)
├── Spawns SR QA Engineer (SDK Process 2)
├── Invokes Orchestrator (Claude Code CLI)
├── Spawns Reviewer (SDK Process 3)
└── Aggregates results via IPC
```

**Pros:**
- Full isolation
- Independent failure handling

**Cons:**
- More complex
- IPC overhead
- Harder to manage context

### Option C: Hybrid (Custom Tools + Subagents)

Supervisor uses custom tools for simple operations, Task for complex:

```python
# Custom tool for SR QA Engineer (simple, in-process)
@tool("generate_step1_input", "Generate Step 1 input", {"complexity": str})
async def generate_step1_input(args):
    # Generate persona + requirement + URL
    return {"content": [{"type": "text", "text": json.dumps(input_data)}]}

# Task tool for Orchestrator (complex, needs full Claude Code)
# Let SDK handle via Task tool

# Custom tool for Reviewer (can be in-process)
@tool("validate_artifacts", "Validate against DDs", {"artifacts": list})
async def validate_artifacts(args):
    # Check against FRAMEWORK.md patterns and 22 DDs
    return {"content": [{"type": "text", "text": json.dumps(results)}]}
```

**Pros:**
- Best of both worlds
- Simple agents are fast (in-process)
- Complex tasks use full Claude Code power

**Cons:**
- Mixed patterns
- Need to decide what's "simple" vs "complex"

---

## Recommendation

**Option C: Hybrid** - Best fit for our use case.

| Agent | Implementation | Rationale |
|-------|---------------|-----------|
| **SR QA Engineer** | Custom Tool (in-process) | Simple: just generates formatted text |
| **Orchestrator** | Claude Code + MCP | Complex: runs full 9-step with tools |
| **Reviewer** | Custom Tool (in-process) | Medium: reads files, checks patterns |
| **Supervisor** | SDK main agent | Coordinates everything |

---

## Prototype Plan

### Minimal Proof of Concept

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, tool, create_sdk_mcp_server

# Simple custom tool
@tool("get_scenario", "Get test scenario", {"level": str})
async def get_scenario(args):
    scenarios = {
        "easy": {
            "persona": "registered user",
            "requirement": "As a registered user, I want to login with valid credentials",
            "url": "http://www.automationpractice.pl/index.php?controller=authentication"
        }
    }
    return {"content": [{"type": "text", "text": str(scenarios.get(args["level"], {}))}]}

server = create_sdk_mcp_server(name="qa-validation", version="1.0.0", tools=[get_scenario])

async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are a QA validation supervisor.",
        mcp_servers={"validation": server},
        allowed_tools=["mcp__validation__get_scenario", "Read", "Glob"]
    )

    async for message in query(
        prompt="Get the easy test scenario and describe what it tests",
        options=options
    ):
        print(message)

asyncio.run(main())
```

---

## Open Questions Resolved

| Question | Answer |
|----------|--------|
| Can SDK invoke MCP tools? | **Yes** - via `mcp_servers` option |
| How to trigger Claude Code? | **SDK wraps Claude Code** - same capabilities |
| Agent-to-agent communication? | **Task tool** for subagents, or custom tools for simple |
| Where to store artifacts? | **Working directory** - SDK uses `cwd` option |

---

## Next Steps

1. [x] Research SDK capabilities
2. [x] Document findings
3. [x] Prototype minimal agent with custom tool (`agents/prototypes/minimal_agent_poc.py`)
4. [x] Test SDK imports (working)
5. [x] Choose final architecture: **Option C (Hybrid)** - CONFIRMED

## Final Decision: Option C (Hybrid)

**Confirmed Architecture:**

| Agent | Implementation | Rationale |
|-------|---------------|-----------|
| **Supervisor** | SDK main agent | Coordinates workflow, single entry point |
| **SR QA Engineer** | Custom tool (in-process) | Simple output generation |
| **Reviewer** | Custom tool (in-process) | Reads files, checks patterns |
| **Orchestrator** | Task tool → Claude Code + MCP | Needs full 9-step capability |

**Prototype Location:** `agents/prototypes/minimal_agent_poc.py`

**To run prototype:**
```bash
export ANTHROPIC_API_KEY=your-key
python agents/prototypes/minimal_agent_poc.py
```

---

## Sources

- [GitHub - anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python)
- [Agent SDK Overview - Claude Docs](https://platform.claude.com/docs/en/api/agent-sdk/overview)
- [Building Agents with Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)

---

*Research completed as part of Task 1.0*
