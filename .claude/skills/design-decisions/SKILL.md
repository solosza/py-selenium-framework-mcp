<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

---
name: design-decisions
description: Record architectural decisions with rationale. Use WHEN making design choices, documenting WHY behind decisions, or creating DD-XX entries. Triggers on "design decision", "DD-", "architecture choice".
---

# Design Decisions Skill

Record architectural decisions with rationale. Capture the WHY behind choices.

## Purpose

Design decisions document:
- What was decided
- Why it was chosen
- What alternatives were considered
- What tradeoffs were accepted

This creates a decision log that:
- Explains architecture to future developers
- Prevents re-debating settled decisions
- Captures context that would otherwise be lost
- Serves as input for skills/documentation later

## Scope

**Record ONLY project/feature-specific decisions:**
- Architecture of the thing being built
- Technology choices for the project
- Patterns selected for implementation

**Do NOT record:**
- Meta decisions (how skills work, process choices)
- General preferences (coding style, naming conventions)
- Decisions that don't affect the project artifact

## When to Invoke This Skill

Invoke when:
- An architectural choice is made between options
- A pattern or structure is selected
- A technology/library is chosen
- A tradeoff is explicitly accepted

Do NOT invoke for:
- Implementation details (how a function works)
- Bug fixes
- Routine code changes
- Process/meta decisions about how to work

## DD File Location

Create `DESIGN_DECISIONS.md` in the project's docs folder:

```
{project_root}/docs/DESIGN_DECISIONS.md
```

If no docs folder exists, create one.

## DD Format

Each design decision follows this structure:

```markdown
## DD-{PROJECT}-{NUMBER}: {Title}

**Date:** YYYY-MM-DD
**Component:** {Which part of system this affects}

**Context:**
{What situation or problem led to this decision?}

**Decision:**
{What was decided? Be specific.}

**Rationale:**
{Why this choice? List the reasons.}

**Alternatives Considered:**
{What other options were evaluated? Why rejected?}

**Tradeoffs Accepted:**
{What downsides are we accepting?}
```

## ID Convention

- `DD-{PROJECT}-{NUMBER}`
- PROJECT: Short project identifier (e.g., RAG, MCP, AUTH)
- NUMBER: Sequential, three digits (001, 002, ...)

Examples:
- `DD-RAG-001`: First decision for RAG project
- `DD-MCP-015`: 15th decision for MCP project

## Recording Process

**CRITICAL: Never auto-add DDs. Always prompt user first.**

1. **Identify the decision point**
   - Options were presented
   - User made a choice
   - Rationale was discussed

2. **Prompt user for confirmation**
   - Ask: "Should I record this as a design decision (DD-{PROJECT}-{NUMBER})?"
   - Wait for user approval before adding to DD file
   - User may decline or request modifications

3. **Capture immediately (after approval)**
   - Don't wait until later
   - Context is fresh now

4. **Be specific**
   - Name the options explicitly
   - Quote the rationale given
   - List actual tradeoffs

5. **Link to analogies if used**
   - If decision was explained via analogy, include it
   - Future readers benefit from the same mental model

## Example Entry

```markdown
## DD-RAG-001: Document Loading Approach

**Date:** 2024-12-13
**Component:** Ingestion / Document Loading

**Context:**
Need to load markdown and Python files into structured Document objects.
Three options available: DIY, LangChain, or LlamaIndex.

**Decision:**
Use **Option A: Simple File Reader (DIY)** with Python's pathlib.

**Rationale:**
- Learn fundamentals before frameworks
- Understand every line of code
- Files are markdown/Python only (no PDF needed)
- Fewer dependencies

**Alternatives Considered:**
- LangChain: Heavy dependency, abstracts details
- LlamaIndex: Another ecosystem to learn

**Tradeoffs Accepted:**
- Must handle encoding/errors ourselves
- No PDF/Word support
```

## Referencing DDs

In code comments:
```python
# See DD-RAG-003 for test structure rationale
```

In documentation:
```markdown
Tests are organized per-layer (see DD-RAG-003).
```

In conversations:
```
"As decided in DD-RAG-001, we're using DIY loading."
```

## Updating DDs

DDs are generally immutable. If a decision changes:

1. Do NOT edit the original DD
2. Create a new DD that supersedes it
3. Reference the old DD

```markdown
## DD-RAG-010: Switch to LangChain Loaders

**Context:**
DD-RAG-001 chose DIY loading. Now need PDF support.

**Decision:**
Switch to LangChain DocumentLoaders.

**Supersedes:** DD-RAG-001
```

## Integration with Other Skills

This skill is invoked by the agent when:
- Learning skills (rag-learning) lead to architectural choices
- Implementation reveals design decisions
- User explicitly asks to record a decision

This skill does NOT invoke other skills. It only records.

## Decision Dialogue

**Good decisions come from honest challenge, not agreement.**

### The Dynamic

1. Either party questions a decision
2. The other defends with reasoning
3. If reasoning is solid → accept
4. If reasoning is weak → push back harder

### AI Responsibility

- **Second-guess decisions** - Ask "is this over-engineered?" or "is this too simple?"
- **Be open to correction** - When user provides solid reasoning, accept it
- **Push back on weak reasoning** - Don't just agree because user said so

### User Responsibility

- **Challenge AI suggestions** - Ask "why this approach?"
- **Defend with reasoning** - Not "because I want it" but "because production systems need X"
- **Accept valid pushback** - AI might be right

### Example Dialogue

```
AI: "This script might be over-engineered for a learning project."
User: "Production systems need organized artifacts in one place."
AI: "Valid point. The script stays."
```

```
User: "Let's add caching here."
AI: "What problem does caching solve? We have 43 tests running in 0.4s."
User: "Good point. Skip it."
```

**Neither party should be a yes-person. Both should be open to being wrong.**

## Anti-Patterns

- **Vague decisions:** "We'll use a good approach" → Be specific
- **Missing rationale:** Listing decision without WHY → Always explain
- **Skipping alternatives:** Only showing chosen option → Show what was rejected
- **Delayed recording:** Writing DDs days later → Capture immediately
- **Over-documenting:** Recording every tiny choice → Only architectural decisions
- **Yes-person behavior:** Agreeing without reasoning → Challenge and defend
