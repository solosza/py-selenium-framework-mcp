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
3. Experimenting and breaking things
4. Evaluating results
5. Documenting learnings

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

For EACH RAG component, follow this 7-step process:

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

### Step 5: Experiment
Prompt user to modify and observe:
- "Change X to Y, run again — what changed?"
- "Try this edge case: [example]"
- "What happens with a very long/short input?"

Provide specific experiments, not vague suggestions.

### Step 6: Evaluate
Assess output quality together:
- "Did retrieval return relevant chunks?"
- "Compare result A vs result B — which is better? Why?"
- "What failed? Where in the pipeline?"

Use concrete test queries with expected results.

### Step 7: Reflect
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
