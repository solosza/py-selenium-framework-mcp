---
name: documentation
description: Create and maintain project documentation. Use WHEN writing docs, READMEs, API references, or explaining WHAT something does and HOW to use it.
---

# Documentation Skill

Create and maintain project documentation. Capture WHAT something does and HOW to use it.

## Purpose

Documentation explains:
- What the project/component does
- How to install and configure
- How to use (with examples)
- API reference

This is different from Design Decisions:
- **Design Decisions (DD):** WHY we chose something
- **Documentation:** WHAT it does and HOW to use it

## When to Invoke This Skill

Invoke when:
- A component is complete and ready for use
- API/interface is stable
- User needs usage instructions
- README needs creation or update

Do NOT invoke for:
- Recording architectural decisions (use design-decisions skill)
- In-progress work
- Internal implementation details

## Documentation Types

| Type | Purpose | Location |
|------|---------|----------|
| README | Project overview, quick start | `{project_root}/README.md` |
| API Docs | Function/class reference | `{project_root}/docs/API.md` or inline |
| Guides | How-to tutorials | `{project_root}/docs/guides/` |
| Architecture | System overview | `{project_root}/docs/ARCHITECTURE.md` |

## README Structure

Every project README should include:

```markdown
# Project Name

One-line description.

## Overview

2-3 sentences explaining what this does and why.

## Installation

Step-by-step setup instructions.

## Quick Start

Minimal example to get running.

## Usage

Common use cases with code examples.

## Configuration

Available options and how to set them.

## Project Structure

Folder layout explanation.

## Contributing

How to contribute (if applicable).

## License

License information (if applicable).
```

## API Documentation Format

For each public function/class:

```markdown
### function_name

Brief description.

**Parameters:**
- `param1` (type): Description
- `param2` (type, optional): Description. Default: value

**Returns:**
- (type): Description

**Raises:**
- `ErrorType`: When this happens

**Example:**
\`\`\`python
result = function_name(arg1, arg2)
\`\`\`
```

## Documentation Principles

1. **Audience-first**
   - Who is reading this?
   - What do they need to know?
   - What do they already know?

2. **Examples over explanations**
   - Show, don't just tell
   - Working code > prose
   - Cover common use cases

3. **Keep it current**
   - Outdated docs are worse than no docs
   - Update when code changes
   - Delete obsolete sections

4. **Progressive disclosure**
   - Quick start first (get running in 2 minutes)
   - Details later (for those who need them)
   - Reference at the end (for lookup)

## Linking to Design Decisions

When documenting a design choice, link to the DD:

```markdown
## Project Structure

Tests are organized per-layer, with each component owning its tests.
See [DD-RAG-003](docs/DESIGN_DECISIONS.md#dd-rag-003-test-file-location) for rationale.
```

## Process

1. **Identify what needs documenting**
   - New component? → README section or dedicated doc
   - API change? → Update API docs
   - New feature? → Usage guide

2. **Start with an example**
   - Write the code the user will run
   - Then explain it

3. **Test your docs**
   - Follow your own instructions
   - Do they work?

4. **Review for completeness**
   - Installation covered?
   - Common errors addressed?
   - Examples runnable?

## Framework Analogy

In QA automation frameworks:
- **Page Object docstrings:** Document element interactions
- **Task docstrings:** Document business operations
- **README:** Document how to run tests

Same principle: Document at the level users interact with.

## Anti-Patterns

- **No examples:** Explanations without code → Always include examples
- **Outdated:** Docs don't match code → Update or delete
- **Verbose:** 10 paragraphs for simple concept → Be concise
- **Assumptions:** "Obviously you'll..." → State prerequisites
- **Implementation focus:** Describing internals → Focus on usage
- **No quick start:** Forcing users to read everything → Start simple

## Integration with Other Skills

- After **rag-learning** completes a component → Document usage
- Reference **design-decisions** for architectural rationale
- Agent invokes based on context (component complete, user requests)

This skill does NOT invoke other skills. It only documents.
