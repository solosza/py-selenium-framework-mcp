# Design Decisions - RAG Learning Project

This document records architectural decisions made while building the RAG system.

Format: Each DD includes context, decision, rationale, and alternatives considered.

---

## DD-RAG-001: Document Loading Approach

**Date:** 2024-12-13
**Component:** Ingestion / Document Loading

**Context:**
Need to load markdown and Python files into structured Document objects. Three options available: DIY (simple file reader), LangChain, or LlamaIndex.

**Decision:**
Use **Option A: Simple File Reader (DIY)** with Python's built-in `pathlib` and `open()`.

**Rationale:**
- Learn fundamentals before frameworks
- Understand every line of code (no magic)
- Files are markdown/Python only (no PDF parsing needed)
- Easy to extend as we learn
- Fewer dependencies

**Alternatives Considered:**
- LangChain DocumentLoaders: Battle-tested but heavy dependency, abstracts away details
- LlamaIndex SimpleDirectoryReader: Simple API but another ecosystem to learn

**Tradeoffs Accepted:**
- Must handle encoding/errors ourselves
- No built-in PDF/Word support (not needed for this corpus)

---

## DD-RAG-002: RAG Project Structure

**Date:** 2024-12-13
**Component:** Architecture

**Context:**
Need folder structure for RAG pipeline components. Three options: single file, by component, or by layer.

**Decision:**
Use **Option C: By layer** structure.

```
training-assistant/
  rag/
    ingestion/     # Load, chunk, embed, store
    retrieval/     # Search, rerank
    generation/    # Prompt building, LLM
```

**Rationale:**
- Matches user's existing framework architecture (pages/, tasks/, roles/)
- Clear separation of concerns
- Each layer owns its responsibility
- Scales well for larger systems

**Alternatives Considered:**
- Single file: Too messy as code grows
- By component: Less clear layer boundaries

**Framework Analogy:**
- `ingestion/` ≈ `pages/` (data layer)
- `retrieval/` ≈ `tasks/` (orchestration)
- `generation/` ≈ `roles/` (business logic)

---

## DD-RAG-003: Test File Location

**Date:** 2024-12-13
**Component:** Testing

**Context:**
Where to put test files? Options: sibling tests/ folder, inside rag/, or per-layer.

**Decision:**
Use **Option C: Per-layer tests**.

```
rag/
  ingestion/
    tests/
      test_loader.py
  retrieval/
    tests/
  generation/
    tests/
```

**Rationale:**
- Locality: Test is right next to what it tests
- Modularity: Delete a layer, delete its tests
- Ownership: Each layer maintains its own tests
- Scales better: No 500-file tests/ folder

**Alternatives Considered:**
- Sibling tests/: Common in Python but less modular
- Inside rag/tests/: Middle ground but still centralized

**Industry Context:**
- Go uses tests next to code (foo.go + foo_test.go)
- JavaScript Jest uses __tests__/ folders per module
- Microservices use tests per service

---

## DD-RAG-004: Document Corpus Sources

**Date:** 2024-12-13
**Component:** Ingestion / Data

**Context:**
What documents to load for learning RAG? Need enough to make retrieval meaningful.

**Decision:**
Use **two source locations**:
1. `D:/my_ai_projects/py_sel_framework_mcp/` - Current project docs (~100k tokens)
2. `C:/Users/solos/OneDrive/Documents/nakupuna/v2_04112025/v2/` - Production framework (~60k tokens)

**Rationale:**
- Combined ~160k tokens approaches 200k context limit
- Two real codebases provide variety for testing search
- Cross-framework queries possible ("how does login work in each?")
- Real content better than lorem ipsum

**Tradeoffs Accepted:**
- Still under 200k (RAG not strictly necessary but good for learning)
- Network drive for Nakupuna source (OneDrive)

---

## DD-RAG-005: Use of __init__.py Files

**Date:** 2024-12-13
**Component:** Architecture / Python Packaging

**Context:**
Modern Python (3.3+) doesn't require __init__.py for packages. Should we use them?

**Decision:**
**Keep __init__.py files** for clean imports.

**Rationale:**
- Enables `from rag.ingestion import Document` vs `from rag.ingestion.document import Document`
- Explicit public API control
- Tool/IDE compatibility
- Small overhead for cleaner usage

**Alternative Considered:**
- Skip them (namespace packages): Works but messier imports

---

## DD-RAG-006: Testing Framework

**Date:** 2024-12-13
**Component:** Testing

**Context:**
Need a testing framework for RAG components. Options: pytest, unittest, or simple scripts.

**Decision:**
Use **pytest** with HTML reporting.

**Rationale:**
- Industry standard for Python testing
- Already used in user's QA automation framework (familiar)
- `tmp_path` fixture simplifies temp file testing
- pytest-html plugin for visual reports
- Rich plugin ecosystem

**Alternatives Considered:**
- unittest: Built-in but more verbose, fewer features
- Simple scripts: No test discovery, manual assertions

**Configuration:**
- Verbose output: `-v`
- HTML reports: `--html=report.html --self-contained-html`
- Per-layer test location (see DD-RAG-003)

---

## DD-RAG-007: Chunking Strategy

**Date:** 2025-12-13
**Component:** Ingestion / Chunking

**Context:**
Need to split documents into smaller pieces for embedding. Corpus is code-heavy (Python + Markdown). Three options: fixed-size, sentence-based, or semantic chunking.

**Decision:**
Use **Option A: Fixed-Size Chunking** with overlap.

**Configuration:**
- Chunk size: ~500 tokens (adjustable)
- Overlap: ~50 tokens (10%)
- Token estimation: chars / 4

**Rationale:**
- Consistent with DD-RAG-001: Learn fundamentals before complexity
- Simple to implement and debug
- No additional dependencies
- Predictable chunk sizes for embedding
- Can observe failures and understand WHY semantic chunking would help

**Alternatives Considered:**
- Sentence/Paragraph-based: Better for prose, but corpus is code-heavy (no natural paragraph breaks)
- Semantic chunking: Best quality but adds embedding dependency during ingestion, hides mechanics

**Tradeoffs Accepted:**
- May cut mid-function or mid-sentence
- Less "intelligent" splits
- Will revisit if retrieval quality suffers

**Learning Goal:**
See where fixed-size fails → understand the problem → appreciate semantic chunking later.

**Framework Analogy:**
Like splitting a Page Object every N lines vs at method boundaries. We start simple to learn why boundaries matter.

---

## DD-RAG-008: Embedding Strategy

**Date:** 2025-12-14
**Component:** Ingestion / Embedding

**Context:**
Need to convert text chunks to vectors for semantic search. Three options: OpenAI API, Sentence Transformers (local), or other cloud APIs.

**Decision:**
Use **Option B: Sentence Transformers** with `all-MiniLM-L6-v2` model.

**Configuration:**
- Model: `all-MiniLM-L6-v2`
- Dimensions: 384
- Loading: Lazy (on first use)

**Rationale:**
- Consistent with DD-RAG-001: Learn fundamentals, no API dependencies
- Free and offline (no API costs or rate limits)
- Fast enough for learning (~2-3s model load, then instant)
- Industry standard model for semantic search
- Can switch to OpenAI later if needed

**Alternatives Considered:**
- OpenAI text-embedding-3-small: Best quality but costs money, requires API key, adds network dependency
- Cohere/Voyage: Similar API concerns

**Tradeoffs Accepted:**
- Slower first call (model download/load)
- Slightly lower quality than OpenAI
- Local compute required

---

## DD-RAG-009: Test Folder Structure (Supersedes DD-RAG-003)

**Date:** 2025-12-14
**Component:** Testing / Architecture
**Supersedes:** DD-RAG-003

**Context:**
DD-RAG-003 chose per-layer tests (tests inside each module). After reflection, this doesn't match the QA perspective or the parent framework structure.

**Previous Decision (DD-RAG-003):**
```
rag/
  ingestion/
    tests/           ← Tests inside module
      test_loader.py
```

**New Decision:**
Use **separate tests folder** matching the Selenium framework pattern.

```
training-assistant/
├── rag/                    ← Source only
│   ├── core/               ← Shared (Document)
│   ├── ingestion/          ← No tests/ subfolder
│   ├── storage/
│   ├── retrieval/
│   └── generation/
│
└── tests/                  ← All tests here
    ├── _reports/           ← Test runner
    │   └── run_tests.py
    ├── conftest.py         ← Shared fixtures, markers
    ├── core/
    ├── ingestion/
    ├── storage/
    ├── retrieval/
    └── generation/
```

**Rationale:**
- **QA perspective:** Most RAG developers are ML engineers, not testers. They scatter tests. QA discipline means organized, discoverable test structure.
- **Consistency:** Matches parent project (`framework/` + `tests/` separate)
- **Test runner location:** Easy to find `tests/_reports/run_tests.py`
- **Clear separation:** Source code vs test code obvious at a glance
- **Portfolio value:** Demonstrates QA discipline applied to ML/AI domain

**Industry Context:**
- RAG projects (LangChain, LlamaIndex): Tests inside modules
- Web frameworks (Django, Flask): Tests separate
- QA automation frameworks: Tests separate

**Why Change?**
This is a QA learning project. Applying QA best practices to RAG is the differentiator, not following ML conventions blindly.

**Tradeoffs Accepted:**
- Different from typical RAG project structure
- More folders to maintain
- Import paths slightly longer in tests
