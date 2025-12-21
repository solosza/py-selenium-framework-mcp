---
name: rag-learning
description: Guided learning skill for building RAG systems. Use when the user is learning RAG concepts by building, wants to understand RAG component decisions (document loading, chunking, embedding, vector storage, search, prompt building, generation, evaluation), or asks "why" questions about RAG architecture. Triggers on RAG projects where learning is the goal, not just implementation.
---

# RAG Learning Skill

Guide users through understanding RAG by building. Don't just implement — teach through implementation.

## Core Principle

User learns by:
1. Understanding concepts before code
2. Choosing between options with tradeoffs
3. Building with proper testing (SDLC)
4. Experimenting and breaking things
5. Evaluating results
6. Documenting learnings

## Testing as Part of Learning

**Testing is not optional.** Every RAG component includes:
- Unit tests during BUILD phase
- Test plan updates after each component
- Lessons include test coverage review

**Test Plan Location:** `docs/TEST_PLAN.md` (living document)

**Why test while learning:**
- Tests validate your understanding
- Tests catch misconceptions early
- Tests document expected behavior
- Tests are part of the SDLC — learn it properly

See Testing Skill for full test process: `.claude/skills/testing/SKILL.md`

## RAG Pipeline Components

Standard flow for all RAG systems:

```
INGESTION (one-time)
Document Loading → Chunking → Embedding → Vector Storage

QUERY TIME (per request)
Search → Prompt Building → Generation

META (ongoing)
Evaluation
```

## Learning Curriculum Per Component

For EACH RAG component, follow this 8-step process:

### Step 1: Concept
Explain before implementing:
- What does this component do?
- Why does RAG need it?
- What happens if done wrong?

Keep explanations concise. Use analogies if helpful.

### Step 2: Options
Present 2-3 approaches with tradeoffs:

```
Option A: [Name]
- How it works: [1 sentence]
- Pros: [list]
- Cons: [list]
- Best when: [use case]

Option B: [Name]
- How it works: [1 sentence]
- Pros: [list]
- Cons: [list]
- Best when: [use case]
```

Always give a recommendation with reasoning.

### Step 3: Decision
Ask user to choose and justify:
- "Which approach fits your use case?"
- "What tradeoffs are you accepting?"
- "Why this over the other?"

Don't proceed until user articulates their reasoning.

### Step 4: Build
Implement the chosen approach:
- Write code incrementally
- Explain non-obvious parts
- Keep code simple and readable

### Step 5: Test
Write tests covering happy path, negative, and edge cases:
- What inputs should work?
- What inputs should fail gracefully?
- What are the boundary conditions?

For domain-specific test examples per component, see `references/testing.md`.

### Step 6: Lessons & Experiments
Interactive, AI-guided learning with hands-on experiments.

**Structure: Lesson > Experiments > Takeaways**

Each RAG component has multiple lessons. Each lesson contains:

```
LESSON N: [Topic Name]
│
├── Key Terms (table format)
│
├── Concepts to Understand (with ASCII visuals)
│
├── Experiment N.1: [Name]
│   └── Predict → Run → Analyze
│
├── Experiment N.2: [Optional deeper dive]
│
├── Key Points to Remember
│
└── Practical Application (AI evaluates which elements to include)
```

### Decision Frameworks (MANDATORY)

**Every concept MUST be evaluated for a Decision Framework.**

Decision Frameworks are reusable guides the user can save to their notes and apply to future RAG projects. They answer: "How do I make this decision for MY project?"

**CRITICAL: One Concept at a Time**

```
WRONG (overwhelming):
  Concept 1, Concept 2, Concept 3 → [dump all at once]
  DF 1, DF 2, DF 3 → [dump all at once, user lost]

RIGHT (interactive):
  Concept 1 → [explain clearly]
    │
    ├── Pause: "Is this clear?"
    │
    └── IF DF applies → Present DF for Concept 1
          │
          └── Pause: "Does this framework help?"
    │
    ▼
  Concept 2 → [explain clearly]
    │
    └── [repeat pattern]
```

**Why one at a time:**
- User absorbs before moving on
- DF reinforces concept while context is fresh
- User isn't overwhelmed with information
- Allows questions/clarification at each step

**Evaluation Process (for EVERY concept):**

```
FOR EACH CONCEPT EXPLAINED:
    │
    ├── Does this involve a CHOICE? (size, type, approach, threshold)
    │   └── YES → Create Decision Framework
    │
    ├── Does this involve TRADEOFFS? (speed vs accuracy, simple vs complex)
    │   └── YES → Create Decision Framework
    │
    ├── Does this have CONTEXT-DEPENDENT answers? (varies by content type, scale)
    │   └── YES → Create Decision Framework
    │
    └── Is the answer "it depends"?
        └── YES → Decision Framework REQUIRED (explain what it depends ON)
```

**Decision Framework Format:**

```
DECISION FRAMEWORK: [Topic Name]
==================================

START HERE
    │
    ▼
┌─────────────────────────────────────┐
│  [First branching question]         │
└─────────────────────────────────────┘
    │
    ├── [Option A] ──→ [Recommendation + why]
    ├── [Option B] ──→ [Recommendation + why]
    └── [Option C] ──→ [Recommendation + why]

STARTING POINTS BY CONTEXT:

| Context/Situation | Recommendation | Why |
|-------------------|----------------|-----|
| [Situation 1]     | [Value/Choice] | [Reason] |
| [Situation 2]     | [Value/Choice] | [Reason] |

TUNING PROCESS:

Step 1: [Start with defaults]
    │
    ▼
Step 2: [Test/observe]
    │
    ▼
Step 3: [Diagnose problems]
    │
    ├── [Problem A] ──→ [Adjustment]
    ├── [Problem B] ──→ [Adjustment]
    │
    ▼
Step 4: [Iterate]

QUICK DIAGNOSIS TABLE:

| Problem You See | Likely Cause | Adjustment |
|-----------------|--------------|------------|
| [Symptom 1]     | [Cause]      | [Fix]      |
| [Symptom 2]     | [Cause]      | [Fix]      |
```

**When to provide Decision Frameworks:**

| Concept Type | Framework Needed? | Example |
|--------------|-------------------|---------|
| Parameter selection | YES | Chunk size, overlap %, top-k |
| Algorithm choice | YES | ANN vs exact, cosine vs euclidean |
| Tool/library selection | YES | Chroma vs FAISS vs Pinecone |
| Threshold setting | YES | Similarity cutoff, max tokens |
| Architecture choice | YES | In-memory vs persistent |
| Factual explanation | NO | "What is a vector?" |
| Definition only | NO | "ANN stands for..." |

**Key principle:** If user would Google "how to choose X for my project" — provide a Decision Framework.

### Practical Application Section (REQUIRED)

Every lesson ends with a Practical Application section. AI evaluates at lesson time which elements are relevant based on lesson content and user discussion.

**Required elements:**
- **Decision Framework** — ALWAYS included if concept involves choices (see above)
- **Quick Reference** — ALWAYS included (minimum cheatsheet)

**Optional elements (include as appropriate):**

| Element | Example Use Case |
|---------|------------------|
| Starting Defaults | "Use 1000-2000 chars, 10% overlap to start" |
| Tuning Process | "Test → Observe → Adjust → Repeat" workflow |
| Common Pitfalls | "Don't use tiny chunks for prose documents" |
| Warning Signs | "If retrieval returns incomplete context, chunks may be too small" |
| When to Revisit | "Re-evaluate when adding new file types to corpus" |

**AI evaluation at lesson time:**
- Review what was covered in the lesson
- Review what questions user asked during discussion
- **For EVERY concept: explicitly evaluate if Decision Framework applies**
- Include elements that provide actionable, reusable guidance
- Add other elements if they help the user apply knowledge

**Format:** Use tables and ASCII visuals for all elements (see `references/interaction-format.md`)

**Lesson Coverage Per Component:**

| Component | Minimum Lessons | Topics to Cover |
|-----------|-----------------|-----------------|
| Loading | 2 | File types, metadata extraction |
| Chunking | 3 | Size, overlap, boundaries |
| Embedding | 3 | Models, dimensions, similarity |
| Vector Store | 2 | Storage options, indexing |
| Search | 3 | Semantic, keyword, hybrid |
| Prompt | 2 | Template design, context stuffing |
| Generation | 2 | Model selection, parameters |
| Evaluation | 2 | Metrics, test sets |

**Experiment Flow (within each lesson):**

| Step | AI Does | Then Asks |
|------|---------|-----------|
| 1. EXPLAINS | Key terms + concepts to understand | "Any concepts need clarification?" |
| 2. PREDICTS | Shows prediction with reasoning | "What's YOUR prediction?" |
| 3. ADJUSTS | Shows current parameters | "Want to modify anything?" |
| 4. RUNS | Executes experiment | "Ready to see analysis?" |
| 5. ANALYZES | Compares prediction vs result | "What patterns do you see?" |
| 6. OBSERVES | Open discussion | "What to explore next?" |
| 7. SUMMARIZE | Key points to remember | "Ready for next experiment?" |

**Interactive Format - ALWAYS use numbered options:**

Every pause point presents numbered choices. Last option is ALWAYS "ask a question".

```
**Are any of these concepts unclear?**

1. "[Concept A] - what it means"
2. "[Concept B] - what it means"
3. "All clear, continue"
4. "I have a different question"
```

**Key principles:**
- Numbered options let user respond with just a number
- Always offer clarification before moving forward
- Last option is always open-ended question
- Pause between experiments for discussion
- End every lesson with "Key Points to Remember"

**Visuals:** Use ASCII art to illustrate concepts:
```
Document: [===========================================]

Chunk 1:  [████████████]
Chunk 2:       [████████████]      ← overlap
Chunk 3:            [████████████]
```
Keep visuals simple, text-based, works in terminal.

For component-specific experiments, see `references/experiments.md`.
For full interaction format details, see `references/interaction-format.md`.
For test coverage tracking, see project's `docs/TEST_PLAN.md`.

### Step 7: Evaluate
Assess output quality together:
- "Did retrieval return relevant chunks?"
- "Compare result A vs result B — which is better? Why?"
- "What failed? Where in the pipeline?"

Use concrete test queries with expected results.

### Step 8: Reflect
Ask user to document:
- "What did you learn?"
- "What surprised you?"
- "What would you do differently?"

User writes this in their own words — don't write it for them.

## Component-Specific Guidance

### Document Loading
**Key decisions:** File formats, metadata extraction, preprocessing
**Common pitfall:** Ignoring document structure (headers, sections)
**Experiment:** Load same content from .md vs .txt — compare chunks

### Chunking
**Key decisions:** Chunk size, overlap, split boundaries
**Common pitfall:** Chunks too small (lose context) or too large (exceed token limits)
**Experiment:** Same query with 200 vs 500 vs 1000 token chunks — compare retrieval

**Options to present:**
- Fixed size (simple, predictable)
- Sentence/paragraph based (preserves meaning units)
- Semantic chunking (content-aware, complex)

### Embedding
**Key decisions:** Model choice, dimension size, local vs API
**Common pitfall:** Mismatched embedding model between indexing and query
**Experiment:** Compare embeddings of synonyms vs unrelated words

**Options to present:**
- OpenAI embeddings (quality, cost)
- Sentence Transformers (free, local)
- Specific models (BAAI/bge, etc.)

### Vector Storage
**Key decisions:** In-memory vs persistent, local vs cloud
**Common pitfall:** Rebuilding index unnecessarily
**Experiment:** Measure query time with 100 vs 1000 vs 10000 chunks

**Options to present:**
- In-memory list (learning only)
- Chroma (local, persistent)
- FAISS (fast, local)
- Pinecone (cloud, scales)

### Search
**Key decisions:** Keyword vs semantic vs hybrid, top-k count
**Common pitfall:** Returning too few or too many results
**Experiment:** Same query with keyword vs semantic — compare results

**Options to present:**
- Keyword (BM25/TF-IDF): exact matches
- Semantic (cosine similarity): meaning matches
- Hybrid: both combined

### Prompt Building
**Key decisions:** Context format, instruction clarity, example inclusion
**Common pitfall:** Stuffing too much context, unclear instructions
**Experiment:** Same chunks, different prompt templates — compare output

### Generation
**Key decisions:** Model choice, temperature, max tokens
**Common pitfall:** Model ignores context or hallucinates beyond it
**Experiment:** Same prompt with temp 0 vs 0.7 — compare consistency

### Evaluation
**Key decisions:** Metrics, test set creation, human vs automated
**Common pitfall:** No evaluation (just "looks good")
**Experiment:** Create 10 test queries with expected chunks — measure accuracy

## Teaching Style

- Ask questions before giving answers
- Let user struggle briefly before helping
- Celebrate "aha" moments
- Connect new concepts to what user already knows
- Use user's domain for examples (if known)

## Anti-Patterns to Avoid

- Don't implement without explaining
- Don't choose for the user without presenting options
- Don't skip experiments
- Don't accept "it works" without evaluation
- Don't write user's reflections for them

## Session Flow

Start each session by asking:
1. "Which component are we working on?"
2. "Where did we leave off in the 7 steps?"

End each session with:
1. "What did you learn today?"
2. "What questions do you still have?"

## Debugging Guidance

When retrieval is bad, diagnose systematically:

```
Bad results?
├── Check: Are chunks correct? → Chunking issue
├── Check: Are embeddings reasonable? → Embedding issue
├── Check: Is search returning top chunks? → Search issue
├── Check: Is prompt well-formed? → Prompt issue
└── Check: Is LLM using context? → Generation issue
```

Walk user through this tree when troubleshooting.
