# Protocol System

**Status:** Idea
**Created:** 2026-01-16
**Target Version:** v1.2 (Protocol Engine), v2.0 (Multi-Protocol Support)
**Effort:** v1.2: 10-12 hours, v2.0: 15-20 hours
**Impact:** Critical (enables all verticals, Layer 1 defense-in-depth)

---

## Context

Protocols define the correct way AI must perform work. In the Isagawa defense-in-depth architecture, Protocols are Layer 1 (Preventive) - they teach AI the correct behavior BEFORE execution begins.

Currently implemented as Claude Skills in `.claude/skills/qa-management-layer/` for QA vertical. Need to generalize protocols as a platform component that works across all verticals (QA, Consumer, Intel, Agent Management, Enterprise).

**Defense-in-Depth Layer 1:**
- **What:** Structured definitions of correct execution workflows
- **Form:** YAML files, markdown references, skill files
- **Purpose:** Teach AI correct behavior BEFORE execution
- **Coverage:** Initial guidance, reduces likelihood of errors

---

## Problem

**Current State:**

**QA Vertical:**
- ✅ Protocols exist as Claude Skills (`.claude/skills/qa-management-layer/`)
- ✅ 11-step workflow documented (step-01.md through step-11.md)
- ✅ Per-step guidance with examples
- ✅ Skill loader (`/qa-workflow` slash command)

**Other Verticals:**
- ❌ No protocol system for Consumer vertical
- ❌ No protocol system for Intel vertical (`/intel` command lacks protocol)
- ❌ No protocol system for Agent Management
- ❌ Each vertical reinvents guidance mechanism

**Cross-Cutting Issues:**
- ❌ No protocol versioning (breaking changes require manual updates)
- ❌ No protocol validation (can't verify protocol completeness)
- ❌ No protocol composition (can't reuse common patterns across verticals)
- ❌ Protocol format tied to Claude Skills (not tool-agnostic)

**Example Gap:**
```
Intel Vertical: /intel command
- Has slash command (.claude/commands/intel.md)
- Has 8-category scan definition
- Missing: Step-by-step protocol for AI to follow
- Missing: Validation that all 8 categories executed
- Missing: Pattern provision when AI skips categories
```

---

## Proposed Solution

### v1.2: Protocol Engine (Claude Code Implementation)

**Vision:** Centralized protocol system accessible by any vertical.

**Proposed Architecture:**
```
mcp_server/
├── protocols/                      ← New protocol system
│   ├── __init__.py
│   ├── protocol_engine.py          ← Core loader/validator
│   ├── protocol_registry.py        ← Available protocols
│   └── definitions/                ← Protocol YAML files
│       ├── qa_execution.yaml       ← QA vertical 11-step workflow
│       ├── intel_scan.yaml         ← Intel vertical 8-category scan
│       ├── consumer_task.yaml      ← Consumer vertical task execution
│       └── agent_management.yaml   ← Agent management workflow
│
.claude/
├── skills/                         ← Skill wrappers (load from YAML)
│   ├── qa-management-layer/
│   │   ├── SKILL.md                ← Loads protocols/definitions/qa_execution.yaml
│   │   └── references/             ← Markdown guides per step
│   ├── intel-management/
│   │   ├── SKILL.md                ← Loads protocols/definitions/intel_scan.yaml
│   │   └── references/             ← Markdown guides per category
│   └── consumer-execution/
│       ├── SKILL.md                ← Loads protocols/definitions/consumer_task.yaml
│       └── references/             ← Markdown guides per task type
```

**Protocol YAML Structure:**
```yaml
# protocols/definitions/intel_scan.yaml
protocol:
  name: "Intel Scan"
  version: "1.0"
  vertical: "intel"
  description: "8-category competitive intelligence scan"

workflow:
  - step: "Scope Validation"
    step_id: "preflight"
    required_inputs:
      - "products"        # List of products to scan
      - "categories"      # List of categories (default: all 8)
    actions:
      - "Parse user input"
      - "Confirm scope with user"
      - "Invoke eg_preflight gate"
    outputs:
      - "validated_scope"
    next_step: "category_execution"

  - step: "Category Execution"
    step_id: "execution"
    required_inputs:
      - "validated_scope"
    actions:
      - "Execute WebSearch for each category"
      - "Categories: Direct Competitors, Feature Convergence, Enterprise Adoption, Regulatory & Standards, Developer & Open Source, Pricing & Packaging, Investment & Funding, Product Roadmaps"
    outputs:
      - "category_results"   # 8 category results
    next_step: "aggregation"

  - step: "Aggregation"
    step_id: "coverage"
    required_inputs:
      - "category_results"
    actions:
      - "Invoke eg_coverage gate"
      - "Validate all 8 categories present"
      - "If missing, gate provides explicit search queries"
    outputs:
      - "coverage_validation"
    next_step: "report_generation"

  - step: "Report Generation"
    step_id: "format"
    required_inputs:
      - "coverage_validation"
    actions:
      - "Generate consolidated report"
      - "5-part structure: Executive Summary, Category Analysis, Competitive Positioning, Strategic Recommendations, Appendices"
      - "Invoke eg_format gate"
    outputs:
      - "report"
    next_step: null   # Workflow complete

gates:
  - gate_id: "eg_preflight"
    step: "preflight"
    validation:
      - "products list not empty"
      - "categories list valid (subset of 8 categories)"

  - gate_id: "eg_coverage"
    step: "coverage"
    validation:
      - "all 8 categories present in results"
      - "each category has at least 3 search results"
    teach_on_fail:
      missing_categories: "List of missing categories"
      search_queries: "Explicit queries for missing categories"

  - gate_id: "eg_format"
    step: "format"
    validation:
      - "report has 5-part structure"
      - "each section non-empty"
      - "all 8 categories covered in Category Analysis"
    teach_on_fail:
      expected_format: "PART 1-5 structure template"
      example: "Load example report template"
```

**Protocol Engine Implementation:**
```python
# mcp_server/protocols/protocol_engine.py
class ProtocolEngine:
    def __init__(self):
        self.registry = ProtocolRegistry()

    def load_protocol(self, vertical: str) -> dict:
        """Load protocol definition for vertical."""
        protocol_path = f"protocols/definitions/{vertical}.yaml"
        protocol = load_yaml(protocol_path)
        self._validate_protocol(protocol)
        return protocol

    def _validate_protocol(self, protocol: dict):
        """Validate protocol structure."""
        required_fields = ["protocol", "workflow", "gates"]
        for field in required_fields:
            if field not in protocol:
                raise ProtocolError(f"Missing required field: {field}")

        # Validate workflow steps
        for step in protocol["workflow"]:
            if "step_id" not in step or "actions" not in step:
                raise ProtocolError(f"Invalid step: {step}")

    def get_step(self, vertical: str, step_id: str) -> dict:
        """Get specific step from protocol."""
        protocol = self.load_protocol(vertical)
        for step in protocol["workflow"]:
            if step["step_id"] == step_id:
                return step
        raise ProtocolError(f"Step not found: {step_id}")

    def get_gates(self, vertical: str, step_id: str) -> List[dict]:
        """Get gates for specific step."""
        protocol = self.load_protocol(vertical)
        gates = [g for g in protocol["gates"] if g["step"] == step_id]
        return gates
```

**Claude Skill Wrapper:**
```markdown
<!-- .claude/skills/intel-management/SKILL.md -->
# Intel Management Skill

Loads protocol from: `protocols/definitions/intel_scan.yaml`

## Protocol Overview

{{ protocol_engine.load_protocol("intel_scan").description }}

## Workflow Steps

{{ protocol_engine.load_protocol("intel_scan").workflow }}

## Per-Step Guidance

See references/ for detailed step-by-step guidance:
- references/preflight.md
- references/execution.md
- references/coverage.md
- references/format.md
```

---

### v2.0: Multi-Protocol Support + Composition

**Features:**
- **Protocol composition:** Reuse common patterns across verticals
- **Protocol inheritance:** Base protocol + vertical-specific overrides
- **Protocol versioning:** Schema evolution, migrations
- **Protocol validation:** CLI tool to validate protocol completeness

**Example Composition:**
```yaml
# protocols/definitions/base_workflow.yaml (reusable)
protocol:
  name: "Base Workflow"
  version: "1.0"

common_steps:
  - step: "Preflight"
    actions: ["Validate inputs", "Invoke gate"]

  - step: "Execution"
    actions: ["Execute main work", "Track progress"]

  - step: "Validation"
    actions: ["Invoke completion gate", "Check quality"]

---

# protocols/definitions/intel_scan.yaml (extends base)
protocol:
  name: "Intel Scan"
  extends: "base_workflow"

workflow:
  - step: "Preflight"
    extends: "common_steps.preflight"
    required_inputs: ["products", "categories"]  # Override

  - step: "Category Execution"
    extends: "common_steps.execution"
    actions:
      - "Execute WebSearch for 8 categories"  # Specific to intel
```

---

## Value

**Benefits:**

**v1.2 (Protocol Engine):**
- ✅ Single protocol system across all verticals
- ✅ YAML definitions (versioned, auditable)
- ✅ Protocol validation (completeness checks)
- ✅ Claude Skills become thin wrappers (load from YAML)
- ✅ Consistent protocol format (QA, Intel, Consumer, Agent Management)

**v2.0 (Multi-Protocol Support):**
- ✅ Protocol composition (reuse common patterns)
- ✅ Protocol inheritance (base + overrides)
- ✅ Protocol versioning (schema evolution)
- ✅ Reduced duplication (common steps defined once)

**Platform Impact:**
- **QA Vertical:** Port existing 11-step workflow to YAML
- **Intel Vertical:** Add missing 4-step protocol
- **Consumer Vertical:** Define task execution protocol
- **Agent Management:** Define agent workflow protocol
- **Enterprise:** Compliance workflow protocols (EU AI Act)

**Defense-in-Depth Impact:**
- **Layer 1 (Protocols):** Standardized across all verticals
- **Layer 2 (Gates):** Reference protocol YAML for validation rules
- **Layer 3 (Hooks):** Monitor protocol adherence in real-time
- **Layer 4 (Checkpointing):** Save state at protocol step boundaries

---

## Implementation Plan

**v1.2 Goals (Protocol Engine):**
1. Create `protocol_engine.py` with YAML loader/validator
2. Define `intel_scan.yaml` protocol (4 steps)
3. Port QA workflow to `qa_execution.yaml` (11 steps)
4. Update Claude Skills to load from YAML
5. Add protocol validation CLI tool
6. Test protocol loading in all verticals

**Effort:** 10-12 hours

**v2.0 Goals (Multi-Protocol Support):**
1. Implement protocol composition (extends, overrides)
2. Add protocol inheritance (base + vertical-specific)
3. Add protocol versioning + migrations
4. Create common patterns library (base_workflow.yaml)
5. Refactor verticals to use composition
6. Add protocol diff tool (compare versions)

**Effort:** 15-20 hours

---

## Tool-Agnostic Adaptation

### Core Abstraction

**What's Tool-Agnostic:**
- Protocol definitions (YAML files)
- Protocol structure (workflow, gates, steps)
- Protocol validation logic (schema checks)
- Protocol engine (loader, registry)

**What's Tool-Specific:**
- Delivery mechanism (Claude Skills vs GPT Functions vs API endpoints)
- Markdown references (Claude Skills use `.md` files)
- Slash commands (Claude Code specific)

### Portability Guide

**For GPT-4/OpenAI:**
```python
# GPT Plugin adapter
class GPTProtocolAdapter:
    def __init__(self):
        self.engine = ProtocolEngine()  # Same engine

    def to_function_schema(self, vertical: str) -> dict:
        """Convert protocol to OpenAI function calling schema."""
        protocol = self.engine.load_protocol(vertical)

        return {
            "name": f"execute_{vertical}_workflow",
            "description": protocol["protocol"]["description"],
            "parameters": self._extract_parameters(protocol)
        }
```

**For REST API:**
```python
# FastAPI endpoint
@app.get("/protocols/{vertical}")
def get_protocol(vertical: str):
    """Return protocol definition as JSON."""
    engine = ProtocolEngine()
    return engine.load_protocol(vertical)

@app.get("/protocols/{vertical}/step/{step_id}")
def get_step(vertical: str, step_id: str):
    """Return specific step guidance."""
    engine = ProtocolEngine()
    return engine.get_step(vertical, step_id)
```

**For Local Scripts:**
```python
# Direct Python import
from mcp_server.protocols import ProtocolEngine

engine = ProtocolEngine()
protocol = engine.load_protocol("intel_scan")

for step in protocol["workflow"]:
    print(f"Step: {step['step_id']}")
    print(f"Actions: {step['actions']}")
```

### What Stays the Same

1. **Protocol YAML files** - Same structure across all tools
2. **Protocol engine** - Same loader/validator logic
3. **Protocol validation** - Same schema checks
4. **Protocol versioning** - Same migration approach

### What Changes

1. **Delivery mechanism:**
   - Claude Code: Skills + references
   - GPT-4: Function calling schemas
   - API: REST endpoints
   - Scripts: Direct import

2. **Per-step guidance:**
   - Claude Code: Markdown files in `references/`
   - GPT-4: System prompts per function
   - API: JSON responses with guidance
   - Scripts: Docstrings or help text

3. **Invocation:**
   - Claude Code: Slash commands (`/qa-workflow`)
   - GPT-4: Function calls (`execute_qa_workflow()`)
   - API: HTTP requests (`POST /workflows/qa/execute`)
   - Scripts: Direct function calls (`engine.execute("qa")`)

### Example: Same Protocol, Three Tools

**Protocol Definition (Tool-Agnostic):**
```yaml
# protocols/definitions/intel_scan.yaml
workflow:
  - step: "Category Execution"
    actions: ["Execute WebSearch for 8 categories"]
```

**Claude Code Delivery:**
```markdown
<!-- .claude/skills/intel-management/references/execution.md -->
# Step 2: Category Execution

Execute WebSearch for 8 categories:
1. Direct Competitors
2. Feature Convergence
...
```

**GPT-4 Delivery:**
```python
{
  "name": "execute_category_search",
  "description": "Execute WebSearch for 8 categories",
  "parameters": {
    "categories": {
      "type": "array",
      "items": {"enum": ["Direct Competitors", "Feature Convergence", ...]}
    }
  }
}
```

**API Delivery:**
```json
{
  "step": "Category Execution",
  "actions": ["Execute WebSearch for 8 categories"],
  "guidance": "Search all 8 categories: Direct Competitors, Feature Convergence, ..."
}
```

Same protocol YAML, three different delivery mechanisms.

---

## Related Items

- **Smart Gates:** Reference protocol YAML for validation rules
- **Hooks System:** Monitor protocol step execution
- **State Management:** Save state at protocol step boundaries
- **Audit System:** Log protocol step completion

---

## Next Steps

1. Move to production roadmap when ready to implement
2. Create PRD for v1.2 (Protocol Engine)
3. Start with intel_scan.yaml (simplest protocol)
4. Port QA workflow to qa_execution.yaml
5. Add protocol validation CLI tool
6. Test with all verticals
