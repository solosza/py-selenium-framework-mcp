# Hooks System

**Status:** Idea
**Created:** 2026-01-16
**Target Version:** v1.2 (Hook Engine), v2.0 (Advanced Features)
**Effort:** v1.2: 12-15 hours, v2.0: 20-25 hours
**Impact:** Critical (enables all verticals, Layer 3 defense-in-depth)

---

## Context

Hooks are event-driven monitors that watch EVERY action in real-time. In the Isagawa defense-in-depth architecture, Hooks are Layer 3 (Continuous Detective) - they monitor continuously and auto-intervene on deviations.

Currently implemented as Claude Code hooks in `.claude/hooks/` (PostToolUse.js writes audit logs). Need to generalize hooks as a platform component that works across all verticals with event registry, hook composition, and intervention patterns.

**Defense-in-Depth Layer 3:**
- **What:** Event-driven monitors that watch EVERY action in real-time
- **Form:** JavaScript hooks triggered on PreToolUse, PostToolUse, PreSave, PostAgentEnd, etc.
- **Purpose:** Continuous surveillance, catch violations that slip through Protocols + Gates
- **Coverage:** Every tool call, every file save, every subagent execution

---

## Problem

**Current State:**

**Existing Hooks:**
- ✅ PostToolUse hook writes audit logs (`.claude/hooks/PostToolUse.js`)
- ✅ Captures tool calls, inputs, outputs, timestamps
- ✅ Works for QA vertical

**Missing Hooks:**
- ❌ PreToolUse (validate inputs before tool execution)
- ❌ PreSave (validate files before saving)
- ❌ PostAgentEnd (validate subagent output)
- ❌ PreCommit (validate before git commit)
- ❌ OnError (handle failures, suggest fixes)

**Cross-Cutting Issues:**
- ❌ No hook registry (can't enable/disable hooks per vertical)
- ❌ No hook composition (can't chain multiple hooks per event)
- ❌ No hook configuration (hard-coded logic in .js files)
- ❌ No hook testing (can't unit test hook logic)
- ❌ Hooks tied to Claude Code (not tool-agnostic)

**Example Gaps:**

**Gap 1: Gate Bypass Detection**
```javascript
// MISSING: PostToolUse hook should detect gate skips
if (toolName === "generate_page_object") {
  // Check: Did qg_page_object gate run?
  const gateRun = checkAuditLog("qg_page_object", last_5_minutes);
  if (!gateRun) {
    alert("WARNING: Gate bypassed - qg_page_object never invoked");
  }
}
```

**Gap 2: Coverage Tracking**
```javascript
// MISSING: PostToolUse hook should track intel scan coverage
if (toolName === "WebSearch") {
  const category = classifyCategory(query);
  coverageTracker[category] = true;

  if (stepCount > 50 && Object.keys(coverageTracker).length < 8) {
    alert(`Coverage gap: ${Object.keys(coverageTracker).length}/8 categories`);
  }
}
```

**Gap 3: File Validation**
```javascript
// MISSING: PreSave hook should validate file format
if (filePath.endsWith(".md") && filePath.includes("intel_reports")) {
  const content = readFile(filePath);

  if (!content.includes("PART 1") || !content.includes("PART 5")) {
    block("INVALID FORMAT: Intel report must have PART 1-5 structure");
  }
}
```

---

## Proposed Solution

### v1.2: Hook Engine (Claude Code Implementation)

**Vision:** Centralized hook system accessible by any vertical.

**Proposed Architecture:**
```
mcp_server/
├── hooks/                          ← New hook system
│   ├── __init__.py
│   ├── hook_engine.py              ← Core event dispatcher
│   ├── hook_registry.py            ← Available hooks
│   └── handlers/                   ← Hook handler implementations
│       ├── audit_logger.py         ← PostToolUse audit logging
│       ├── gate_monitor.py         ← PostToolUse gate bypass detection
│       ├── coverage_tracker.py     ← PostToolUse intel scan coverage
│       ├── file_validator.py       ← PreSave file format validation
│       ├── subagent_validator.py   ← PostAgentEnd output validation
│       └── error_handler.py        ← OnError failure handling
│
.claude/
├── hooks/                          ← Claude Code hook wrappers
│   ├── PreToolUse.js               ← Calls hook_engine.dispatch("pre_tool_use", context)
│   ├── PostToolUse.js              ← Calls hook_engine.dispatch("post_tool_use", context)
│   ├── PreSave.js                  ← Calls hook_engine.dispatch("pre_save", context)
│   ├── PostAgentEnd.js             ← Calls hook_engine.dispatch("post_agent_end", context)
│   ├── PreCommit.js                ← Calls hook_engine.dispatch("pre_commit", context)
│   └── OnError.js                  ← Calls hook_engine.dispatch("on_error", context)
```

**Hook Engine Implementation:**
```python
# mcp_server/hooks/hook_engine.py
class HookEngine:
    def __init__(self):
        self.registry = HookRegistry()

    def dispatch(self, event: str, context: dict) -> dict:
        """Dispatch event to all registered handlers."""
        handlers = self.registry.get_handlers(event)

        results = []
        for handler in handlers:
            try:
                result = handler.handle(context)
                results.append(result)

                # Check for interventions
                if result.get("block"):
                    return {"action": "block", "message": result["message"]}
                if result.get("alert"):
                    return {"action": "alert", "message": result["message"]}

            except Exception as e:
                log_error(f"Hook handler failed: {handler.__class__.__name__}", e)

        return {"action": "allow", "results": results}

    def register_handler(self, event: str, handler: "HookHandler"):
        """Register handler for event."""
        self.registry.add_handler(event, handler)

    def unregister_handler(self, event: str, handler_name: str):
        """Unregister handler for event."""
        self.registry.remove_handler(event, handler_name)
```

**Hook Handler Base Class:**
```python
# mcp_server/hooks/handler_base.py
class HookHandler:
    def __init__(self, config: dict = None):
        self.config = config or {}

    def handle(self, context: dict) -> dict:
        """
        Handle event.

        Returns:
            {
                "block": bool,      # Block action (PreToolUse, PreSave)
                "alert": bool,      # Alert user (PostToolUse)
                "message": str,     # Message to display
                "data": dict        # Additional data
            }
        """
        raise NotImplementedError
```

**Example Handler: Gate Monitor**
```python
# mcp_server/hooks/handlers/gate_monitor.py
class GateMonitorHandler(HookHandler):
    """Monitor PostToolUse for gate bypasses."""

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.expected_gates = {
            "generate_page_object": "qg_page_object",
            "generate_task": "qg_task",
            "generate_role": "qg_role",
            "generate_test_runner": "qg_test_runner"
        }

    def handle(self, context: dict) -> dict:
        tool_name = context.get("tool_name")

        # Check if this tool requires a gate
        if tool_name not in self.expected_gates:
            return {"alert": False}

        expected_gate = self.expected_gates[tool_name]

        # Check if gate ran recently (last 2 minutes)
        gate_ran = self._check_audit_log(expected_gate, minutes=2)

        if not gate_ran:
            return {
                "alert": True,
                "message": f"WARNING: Gate bypassed - {expected_gate} never invoked after {tool_name}"
            }

        return {"alert": False}

    def _check_audit_log(self, gate_name: str, minutes: int) -> bool:
        """Check if gate ran in last N minutes."""
        audit_log = load_audit_log()
        cutoff = datetime.now() - timedelta(minutes=minutes)

        for entry in audit_log:
            if entry["tool_name"] == gate_name and entry["timestamp"] > cutoff:
                return True

        return False
```

**Example Handler: Coverage Tracker**
```python
# mcp_server/hooks/handlers/coverage_tracker.py
class CoverageTrackerHandler(HookHandler):
    """Track intel scan category coverage."""

    CATEGORIES = [
        "Direct Competitors",
        "Feature Convergence",
        "Enterprise Adoption",
        "Regulatory & Standards",
        "Developer & Open Source",
        "Pricing & Packaging",
        "Investment & Funding",
        "Product Roadmaps"
    ]

    def __init__(self, config: dict = None):
        super().__init__(config)
        self.coverage = {}  # {category: bool}

    def handle(self, context: dict) -> dict:
        tool_name = context.get("tool_name")

        if tool_name != "WebSearch":
            return {"alert": False}

        query = context.get("args", {}).get("query", "")
        category = self._classify_category(query)

        if category:
            self.coverage[category] = True

        # Check coverage
        step_count = context.get("step_count", 0)
        coverage_count = len(self.coverage)

        if step_count > 50 and coverage_count < 8:
            missing = [c for c in self.CATEGORIES if c not in self.coverage]
            return {
                "alert": True,
                "message": f"Coverage gap: {coverage_count}/8 categories. Missing: {', '.join(missing)}"
            }

        return {"alert": False}

    def _classify_category(self, query: str) -> str:
        """Classify search query into category."""
        query_lower = query.lower()

        if "competitor" in query_lower or "rival" in query_lower:
            return "Direct Competitors"
        if "feature" in query_lower or "convergence" in query_lower:
            return "Feature Convergence"
        # ... more classification logic

        return None
```

**Example Handler: File Validator**
```python
# mcp_server/hooks/handlers/file_validator.py
class FileValidatorHandler(HookHandler):
    """Validate files before saving (PreSave)."""

    def handle(self, context: dict) -> dict:
        file_path = context.get("file_path")
        content = context.get("content")

        # Intel report validation
        if "intel_reports" in file_path and file_path.endswith(".md"):
            return self._validate_intel_report(content)

        # POM validation
        if "pages" in file_path and file_path.endswith(".py"):
            return self._validate_pom(content)

        return {"block": False}

    def _validate_intel_report(self, content: str) -> dict:
        """Validate intel report has PART 1-5 structure."""
        required_parts = ["PART 1", "PART 2", "PART 3", "PART 4", "PART 5"]
        missing_parts = [p for p in required_parts if p not in content]

        if missing_parts:
            return {
                "block": True,
                "message": f"INVALID FORMAT: Intel report missing {', '.join(missing_parts)}"
            }

        return {"block": False}

    def _validate_pom(self, content: str) -> dict:
        """Validate POM has no skeleton code."""
        if "pass  #" in content or "# TODO" in content:
            return {
                "block": True,
                "message": "SKELETON CODE: POM contains incomplete methods (pass statements or TODOs)"
            }

        return {"block": False}
```

**Hook Registry Configuration:**
```yaml
# mcp_server/hooks/hook_config.yaml
hooks:
  post_tool_use:
    - handler: audit_logger
      enabled: true
      config:
        log_path: "tests/_audit/"

    - handler: gate_monitor
      enabled: true
      config:
        alert_on_bypass: true

    - handler: coverage_tracker
      enabled: true
      verticals: ["intel"]  # Only for intel vertical

  pre_save:
    - handler: file_validator
      enabled: true
      config:
        validate_intel_reports: true
        validate_poms: true

  post_agent_end:
    - handler: subagent_validator
      enabled: true
      config:
        check_gate_invocations: true
```

**Claude Hook Wrapper:**
```javascript
// .claude/hooks/PostToolUse.js
const { execSync } = require('child_process');

module.exports = async (context) => {
  // Call Python hook engine
  const result = execSync(
    `python -m mcp_server.hooks.hook_engine dispatch post_tool_use '${JSON.stringify(context)}'`,
    { encoding: 'utf-8' }
  );

  const response = JSON.parse(result);

  // Handle interventions
  if (response.action === "alert") {
    console.warn(`[HOOK ALERT] ${response.message}`);
  }

  return response;
};
```

---

### v2.0: Advanced Hook Features

**Features:**
- **Hook composition:** Chain multiple handlers per event
- **Conditional hooks:** Enable hooks based on workflow/vertical/context
- **Hook priorities:** Execute handlers in priority order
- **Hook testing:** Unit test framework for hook handlers
- **Hook analytics:** Track hook invocations, alerts, blocks
- **Hook learning:** ML-based pattern detection (anomaly detection)

**Example Composition:**
```yaml
# Hook composition: Multiple handlers per event
hooks:
  post_tool_use:
    - handler: audit_logger         # Priority 1 (always runs)
      priority: 1

    - handler: gate_monitor         # Priority 2
      priority: 2
      condition:
        vertical: ["qa", "consumer"]  # Only for specific verticals

    - handler: coverage_tracker     # Priority 3
      priority: 3
      condition:
        vertical: ["intel"]
        workflow: ["intel_scan"]
```

**Example Testing:**
```python
# tests/hooks/test_gate_monitor.py
def test_gate_monitor_detects_bypass():
    handler = GateMonitorHandler()

    context = {
        "tool_name": "generate_page_object",
        "timestamp": datetime.now()
    }

    result = handler.handle(context)

    assert result["alert"] is True
    assert "qg_page_object" in result["message"]
```

---

## Value

**Benefits:**

**v1.2 (Hook Engine):**
- ✅ Single hook system across all verticals
- ✅ Event-driven architecture (extensible)
- ✅ Hook handlers in Python (testable, maintainable)
- ✅ Claude hooks become thin wrappers (call Python engine)
- ✅ Hook registry (enable/disable per vertical)
- ✅ Standard intervention patterns (alert, block, auto-fix)

**v2.0 (Advanced Features):**
- ✅ Hook composition (multiple handlers per event)
- ✅ Conditional hooks (enable based on context)
- ✅ Hook priorities (execution order)
- ✅ Hook testing (unit test framework)
- ✅ Hook analytics (track invocations)
- ✅ Hook learning (ML-based anomaly detection)

**Platform Impact:**
- **QA Vertical:** Gate monitoring, POM validation, test execution alerts
- **Intel Vertical:** Coverage tracking, report format validation
- **Consumer Vertical:** User rule enforcement, task validation
- **Agent Management:** Protocol adherence monitoring
- **Enterprise:** Compliance validation (EU AI Act)

**Defense-in-Depth Impact:**
- **Layer 1 (Protocols):** Hooks validate protocol step execution
- **Layer 2 (Gates):** Hooks detect gate bypasses
- **Layer 3 (Hooks):** PRIMARY DEFENSE - Continuous monitoring
- **Layer 4 (Checkpointing):** Hooks trigger checkpoints

---

## Implementation Plan

**v1.2 Goals (Hook Engine):**
1. Create `hook_engine.py` with event dispatcher
2. Implement `HookHandler` base class
3. Port PostToolUse audit logging to handler
4. Add gate monitor handler (detect bypasses)
5. Add coverage tracker handler (intel vertical)
6. Add file validator handler (PreSave)
7. Add hook registry with YAML config
8. Update Claude hooks to call Python engine
9. Add hook testing framework

**Effort:** 12-15 hours

**v2.0 Goals (Advanced Features):**
1. Implement hook composition (multiple handlers per event)
2. Add conditional hooks (enable based on context)
3. Add hook priorities (execution order)
4. Build hook analytics (track invocations, alerts, blocks)
5. Add hook learning (ML anomaly detection)
6. Create hook debugging CLI tool
7. Add hook performance monitoring

**Effort:** 20-25 hours

---

## Tool-Agnostic Adaptation

### Core Abstraction

**What's Tool-Agnostic:**
- Hook engine (event dispatcher)
- Hook handlers (Python implementations)
- Hook registry (YAML configuration)
- Hook testing framework (pytest)
- Event types (pre_tool_use, post_tool_use, pre_save, etc.)

**What's Tool-Specific:**
- Event sources (Claude Code hooks vs GPT callbacks vs API webhooks)
- Hook invocation mechanism (JavaScript wrapper vs HTTP POST vs direct call)
- Event context structure (Claude Code provides tool_name, args, result)

### Portability Guide

**For GPT-4/OpenAI:**
```python
# GPT callback adapter
class GPTHookAdapter:
    def __init__(self):
        self.engine = HookEngine()  # Same engine

    def on_function_call(self, function_name: str, args: dict, result: dict):
        """Called by GPT after function execution."""
        context = {
            "tool_name": function_name,
            "args": args,
            "result": result,
            "timestamp": datetime.now()
        }

        # Dispatch to hook engine
        return self.engine.dispatch("post_tool_use", context)
```

**For REST API:**
```python
# FastAPI webhook endpoint
@app.post("/hooks/{event}")
def dispatch_hook(event: str, context: dict):
    """Webhook for external systems to trigger hooks."""
    engine = HookEngine()
    return engine.dispatch(event, context)

# Example: External system calls webhook
requests.post("http://api/hooks/post_tool_use", json={
    "tool_name": "generate_page_object",
    "args": {...},
    "result": {...}
})
```

**For Local Scripts:**
```python
# Direct Python import
from mcp_server.hooks import HookEngine

engine = HookEngine()

# Manually dispatch events
context = {
    "tool_name": "generate_page_object",
    "args": {...},
    "result": {...}
}

result = engine.dispatch("post_tool_use", context)

if result["action"] == "alert":
    print(f"WARNING: {result['message']}")
```

### What Stays the Same

1. **Hook engine** - Same event dispatcher logic
2. **Hook handlers** - Same Python implementations
3. **Hook registry** - Same YAML configuration
4. **Hook testing** - Same pytest tests
5. **Intervention patterns** - Same alert/block/auto-fix logic

### What Changes

1. **Event sources:**
   - Claude Code: JavaScript hooks (`.claude/hooks/*.js`)
   - GPT-4: Function callbacks (`on_function_call`)
   - API: Webhooks (`POST /hooks/{event}`)
   - Scripts: Direct calls (`engine.dispatch()`)

2. **Event context structure:**
   - Claude Code: `{tool_name, args, result, timestamp}`
   - GPT-4: `{function_name, parameters, response, timestamp}`
   - API: Custom context (application-specific)
   - Scripts: Manual context construction

3. **Intervention delivery:**
   - Claude Code: Console output (`console.warn()`)
   - GPT-4: System messages (added to conversation)
   - API: HTTP response codes (200, 400, 403)
   - Scripts: Return values or exceptions

### Example: Same Hook, Three Tools

**Hook Handler (Tool-Agnostic):**
```python
# mcp_server/hooks/handlers/gate_monitor.py
class GateMonitorHandler(HookHandler):
    def handle(self, context: dict) -> dict:
        tool_name = context.get("tool_name")
        if tool_name == "generate_page_object":
            gate_ran = self._check_audit_log("qg_page_object")
            if not gate_ran:
                return {"alert": True, "message": "Gate bypassed"}
        return {"alert": False}
```

**Claude Code Invocation:**
```javascript
// .claude/hooks/PostToolUse.js
const result = execSync(
  `python -m mcp_server.hooks.hook_engine dispatch post_tool_use '${JSON.stringify(context)}'`
);
if (result.alert) console.warn(result.message);
```

**GPT-4 Invocation:**
```python
# GPT callback
def on_function_call(function_name, args, result):
    context = {"tool_name": function_name, "args": args, "result": result}
    response = hook_engine.dispatch("post_tool_use", context)
    if response["alert"]:
        add_system_message(response["message"])
```

**API Invocation:**
```python
# Webhook call
@app.post("/tools/{tool_name}/execute")
def execute_tool(tool_name: str, args: dict):
    result = execute_tool_internal(tool_name, args)

    # Dispatch hook
    hook_response = hook_engine.dispatch("post_tool_use", {
        "tool_name": tool_name,
        "args": args,
        "result": result
    })

    if hook_response["action"] == "block":
        raise HTTPException(403, hook_response["message"])

    return result
```

Same hook handler, three different event sources.

---

## Hook Event Types

**Standard Events:**

| Event | When | Use Case |
|-------|------|----------|
| `pre_tool_use` | Before tool execution | Validate inputs, check permissions |
| `post_tool_use` | After tool execution | Audit logging, gate monitoring, coverage tracking |
| `pre_save` | Before file save | File format validation, skeleton detection |
| `post_save` | After file save | Backup, notify user, trigger downstream |
| `pre_commit` | Before git commit | Lint checks, test requirements |
| `post_commit` | After git commit | CI/CD trigger, notify team |
| `pre_agent_start` | Before subagent starts | Validate subagent config, set expectations |
| `post_agent_end` | After subagent completes | Validate subagent output, check gate invocations |
| `on_error` | When error occurs | Error handling, suggest fixes, retry logic |

---

## Related Items

- **Protocol System:** Hooks validate protocol step execution
- **Smart Gates:** Hooks detect gate bypasses
- **Audit System:** Hooks write audit logs (PostToolUse)
- **State Management:** Hooks trigger checkpoints
- **HITL System:** Hooks request user confirmation when needed

---

## Next Steps

1. Move to production roadmap when ready to implement
2. Create PRD for v1.2 (Hook Engine)
3. Start with PostToolUse handlers (audit, gate monitor)
4. Add PreSave handlers (file validation)
5. Add PostAgentEnd handlers (subagent validation)
6. Build hook testing framework
7. Test with all verticals
