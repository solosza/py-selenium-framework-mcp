# QA Framework Training Assistant - Complete Project Context

## Project Overview

A RAG-powered (Retrieval Augmented Generation) training assistant that helps manual testers and new team members learn and use the py-selenium-framework-mcp test automation framework. The assistant answers natural language questions about the framework by retrieving relevant documentation and generating contextual responses.

This project serves dual purposes:
1. **Learning vehicle** — Apply concepts from the DeepLearning.ai RAG Specialization course
2. **Portfolio piece** — Demonstrate RAG implementation skills in a QA/SDET context
3. **Practical tool** — Create actual onboarding documentation and make it interactive

---

## Design Philosophy and Core Principles

### Why This Project

**The Problem:**
- The py-selenium-framework-mcp project needs onboarding documentation
- Manual testers transitioning to automation need guidance
- New team members need to understand the 4-layer architecture quickly

**The Solution:**
- Create comprehensive documentation (needed anyway)
- Make it searchable and interactive via RAG
- Users ask questions in natural language, get contextual answers

**Portfolio Value:**
- Extends existing QA framework project (cohesive story)
- Shows RAG skills applied to QA domain
- Demonstrates: "I don't just automate tests, I build AI systems that make QA teams smarter"

### Core Principles

1. **Learn by building** — Apply each RAG course module to this project immediately
2. **Documentation-first** — The corpus is documentation you need to write anyway
3. **Start simple** — Begin with basic retrieval, add sophistication as course progresses
4. **Standalone interface** — Web app (Streamlit), not dependent on Claude Code/MCP

---

## Project Location and Structure

This project lives inside the existing py-selenium-framework-mcp repository:

```
py-selenium-framework-mcp/
├── framework/                    # Existing test framework
│   ├── interfaces/
│   ├── pages/
│   ├── tasks/
│   ├── roles/
│   └── resources/
├── tests/                        # Existing tests
├── mcp_server/                   # Existing MCP AI integration
│
└── training-assistant/           # NEW - RAG project
    ├── corpus/                   # Documentation files
    │   ├── getting-started/
    │   ├── architecture/
    │   ├── patterns/
    │   ├── examples/
    │   ├── troubleshooting/
    │   └── qa-pairs/
    ├── src/                      # RAG implementation
    │   ├── retrieval/            # Search/embedding logic
    │   ├── generation/           # LLM integration
    │   └── pipeline/             # RAG orchestration
    ├── app.py                    # Streamlit web interface
    ├── requirements.txt
    └── README.md
```

---

## The Corpus

### What Is a Corpus

The corpus is the collection of documents the RAG system searches through. When a user asks a question:
1. System searches corpus for relevant chunks
2. Passes those chunks + question to LLM
3. LLM generates answer using the retrieved context

### Corpus Structure

```
corpus/
├── getting-started/
│   ├── setup.md                  # Environment setup, installation
│   ├── first_test.md             # Writing your first test
│   ├── project_structure.md      # Directory layout explained
│   └── running_tests.md          # pytest commands, reports
│
├── architecture/
│   ├── four_layers_overview.md   # High-level architecture
│   ├── page_objects.md           # Page Object layer deep dive
│   ├── tasks.md                  # Task layer deep dive
│   ├── roles.md                  # Role layer deep dive
│   ├── web_interface.md          # WebInterface wrapper
│   └── golden_rules.md           # The 5 golden rules
│
├── patterns/
│   ├── adding_page_object.md     # Step-by-step guide
│   ├── writing_task.md           # Step-by-step guide
│   ├── creating_role.md          # Step-by-step guide
│   ├── locator_strategies.md     # How to write good locators
│   ├── common_mistakes.md        # Anti-patterns to avoid
│   └── decorator_usage.md        # @autologger and others
│
├── examples/
│   ├── login_flow.md             # Complete login example
│   ├── catalog_browse.md         # Catalog browsing example
│   ├── form_submission.md        # Form handling example
│   └── assertions.md             # State-check method examples
│
├── troubleshooting/
│   ├── element_not_found.md      # TimeoutException solutions
│   ├── flaky_tests.md            # Handling flakiness
│   ├── driver_issues.md          # ChromeDriver problems
│   └── common_errors.md          # Error message guide
│
└── qa-pairs/
    ├── beginner_questions.md     # FAQ for newcomers
    ├── architecture_questions.md # "Why" questions
    └── debugging_questions.md    # Troubleshooting Q&A
```

### Corpus Sources

**From existing project (expand/chunk these):**
- ARCHITECTURE.md → Split into 5-10 focused docs
- README.md → Split into 3-5 docs
- Actual test code → Extract as examples

**New content to create:**
- How-to guides (patterns/)
- Q&A pairs (qa-pairs/)
- Troubleshooting guides (troubleshooting/)

### Estimated Corpus Size

| Category | Docs | Creation Time (with LLM) |
|----------|------|--------------------------|
| Getting started | 4-5 | 1-2 hours |
| Architecture | 5-6 | 2-3 hours (expanding existing) |
| Patterns | 6-8 | 2-3 hours |
| Examples | 4-5 | 1-2 hours (extracting from code) |
| Troubleshooting | 4-5 | 1-2 hours |
| Q&A pairs | 20-30 pairs | 1-2 hours |

**Total: ~50-60 documents, 8-12 hours of content creation**

Note: You don't need all of this upfront. Start with 15-20 docs for initial modules, expand as you progress through the course.

---

## RAG Architecture

### How RAG Works (High Level)

```
┌──────────────────────────────────────────────────────────┐
│ User: "How do I add a page object?"                      │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 1: RETRIEVAL (always happens - hardcoded)           │
│                                                          │
│ Search corpus for relevant chunks                        │
│ Returns: page_objects.md, adding_page_object.md          │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 2: AUGMENT PROMPT                                   │
│                                                          │
│ """                                                      │
│ Use the following documentation to answer the question.  │
│                                                          │
│ [RETRIEVED DOCS INSERTED HERE]                           │
│                                                          │
│ Question: How do I add a page object?                    │
│ """                                                      │
└──────────────────────────────────────────────────────────┘
                          │
                          ▼
┌──────────────────────────────────────────────────────────┐
│ STEP 3: GENERATE                                         │
│                                                          │
│ LLM sees docs in prompt, answers based on them           │
│ Response grounded in YOUR framework's patterns           │
└──────────────────────────────────────────────────────────┘
```

### Key Insight

The LLM never "decides" to search. Your code forces retrieval on every query. This is what makes it RAG — retrieval is a hardcoded step in the pipeline, not an AI choice.

### Technical Components

**Module 2 (Basic Retrieval):**
- Load documents from files
- Chunk documents into smaller pieces
- Keyword/basic search

**Module 3 (Vector Database):**
- Embed documents using embedding model
- Store in vector database (Chroma, Pinecone, etc.)
- Semantic search (meaning-based, not just keywords)

**Module 4 (Generation):**
- Connect to LLM (OpenAI, Anthropic, Together.ai, etc.)
- Prompt engineering for good responses
- Handle context window limits

**Module 5 (Production):**
- Evaluation metrics
- Performance optimization
- Scaling considerations

---

## User Interface

### Primary Interface: Streamlit Web App

```
┌─────────────────────────────────────────────────────────┐
│  🤖 QA Framework Training Assistant                     │
│                                                         │
│  Ask a question about the test automation framework:    │
│  ┌─────────────────────────────────────────────────┐   │
│  │ How do I add a new page object?                 │   │
│  └─────────────────────────────────────────────────┘   │
│                                        [Ask]            │
│                                                         │
│  ───────────────────────────────────────────────────── │
│                                                         │
│  📄 Sources: page_objects.md, adding_page_object.md    │
│                                                         │
│  Page objects live in `framework/pages/`. Here's how   │
│  to add one:                                            │
│                                                         │
│  1. Create a new file in the appropriate subdirectory  │
│  2. Define locators as class constants                 │
│  3. Add atomic methods (click, type, select)           │
│  4. Use the @autologger decorator                      │
│                                                         │
│  Example from LoginPage:                               │
│  ```python                                             │
│  class LoginPage:                                      │
│      EMAIL_INPUT = (By.ID, "email")                    │
│      ...                                               │
│  ```                                                   │
└─────────────────────────────────────────────────────────┘
```

### How Users Access It

**Local development:**
```bash
cd training-assistant
pip install -r requirements.txt
streamlit run app.py
# Opens at http://localhost:8501
```

**For others who clone the repo:**
Add instructions to main README:
```markdown
## Training Assistant

Interactive RAG-powered assistant for learning this framework.

### Setup
cd training-assistant
pip install -r requirements.txt

### Run
streamlit run app.py
```

### Why Not MCP?

MCP tools rely on AI judgment to decide when to call them. For learning RAG, you want:
- Deterministic behavior (retrieval always happens)
- Clear understanding of the pipeline
- Interface anyone can use (not just Claude Code users)

MCP integration could be a future enhancement, but the core RAG logic is the same.

---

## Course Alignment

### DeepLearning.ai RAG Specialization

| Module | What You Learn | What You Build |
|--------|----------------|----------------|
| Module 1 | RAG overview, LLM calls, augmented prompts | Basic prompt augmentation with framework docs |
| Module 2 | Information retrieval, keyword search | Document loading, chunking, basic search |
| Module 3 | Vector databases, embeddings | Semantic search for framework docs |
| Module 4 | LLM generation, prompt engineering | Quality responses from retrieved context |
| Module 5 | Production concerns, evaluation | Measure retrieval quality, optimize |

### Workflow

1. Complete course module (videos, labs in Coursera)
2. Come to Claude Code: "I just learned X, let's apply it"
3. Implement that concept in training-assistant
4. Repeat

### Note on Course Labs

The Coursera labs use a proxy server for API calls. Your project will use your own LLM provider (OpenAI, Anthropic, Together.ai, etc.). The concepts are identical, just different API setup.

---

## Development Phases

### Phase 1: Foundation (Module 1-2 alignment)
**Goal:** Basic working retrieval

- [ ] Set up training-assistant folder structure
- [ ] Create initial corpus (15-20 docs from existing content)
- [ ] Implement document loading
- [ ] Implement basic chunking
- [ ] Implement keyword search
- [ ] Create minimal Streamlit UI
- [ ] Test with sample questions

**Milestone:** Can ask a question, get relevant doc chunks back

### Phase 2: Semantic Search (Module 3 alignment)
**Goal:** Meaning-based retrieval

- [ ] Set up embedding model
- [ ] Set up vector database (Chroma for local)
- [ ] Embed all corpus documents
- [ ] Implement semantic search
- [ ] Compare results to keyword search

**Milestone:** Retrieval finds relevant docs even with different wording

### Phase 3: Generation (Module 4 alignment)
**Goal:** Quality LLM responses

- [ ] Integrate LLM provider
- [ ] Design prompt template
- [ ] Implement RAG pipeline (retrieve → augment → generate)
- [ ] Handle context window limits
- [ ] Add source attribution to responses

**Milestone:** Full RAG working — question in, grounded answer out

### Phase 4: Polish (Module 5 alignment)
**Goal:** Production-ready quality

- [ ] Add evaluation metrics
- [ ] Optimize retrieval parameters
- [ ] Expand corpus with more docs
- [ ] Improve UI (conversation history, etc.)
- [ ] Write comprehensive README

**Milestone:** Portfolio-ready project

### Phase 5: Expansion (Post-course)
**Goal:** Grow corpus and features

- [ ] Add external QA resources (Selenium docs, pytest docs)
- [ ] Add more Q&A pairs based on real questions
- [ ] Consider MCP integration as optional feature
- [ ] Consider deployment (Streamlit Cloud)

---

## Technical Decisions

### Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Location | Inside existing repo | Cohesive portfolio, shared context |
| Interface | Streamlit | Simple, Python-native, easy to demo |
| Corpus format | Markdown files | Easy to write, version control friendly |
| Initial vector DB | Chroma | Local, no setup, good for learning |
| LLM provider | TBD (OpenAI/Anthropic/Together) | Flexibility based on cost/preference |

### Decisions Deferred

| Decision | Options | Decide When |
|----------|---------|-------------|
| LLM provider | OpenAI, Anthropic, Together.ai | Phase 3 (when integrating generation) |
| Embedding model | OpenAI, Sentence Transformers, etc. | Phase 2 (when implementing semantic search) |
| Deployment | Local only vs Streamlit Cloud | Phase 5 (post-course) |
| MCP integration | Add as optional feature or skip | Phase 5 (post-course) |

---

## Example Queries the Assistant Should Handle

**Getting started:**
- "How do I set up the project?"
- "How do I run my first test?"
- "What's the project structure?"

**Architecture:**
- "What are the 4 layers?"
- "What's the difference between tasks and roles?"
- "Where do locators go?"
- "What are the golden rules?"

**How-to:**
- "How do I add a new page object?"
- "How do I write a task?"
- "How do I create a new role?"
- "Show me an example of a login test"

**Troubleshooting:**
- "I'm getting TimeoutException"
- "My test is flaky"
- "Element not found error"
- "ChromeDriver version mismatch"

**Best practices:**
- "What are common mistakes to avoid?"
- "When should I use a task vs putting logic in the test?"
- "How should I name my page object methods?"

---

## Where We Left Off

### Last Discussion Topic
Finalizing project choice and understanding how RAG works vs MCP tools.

### Key Decisions Made
1. **Project:** QA Framework Training Assistant (RAG-powered)
2. **Location:** Inside py-selenium-framework-mcp repo as training-assistant/
3. **Interface:** Streamlit web app (standalone, not MCP-dependent)
4. **Corpus:** Framework documentation, patterns, examples, Q&A pairs
5. **Purpose:** Learning RAG + portfolio piece + actual useful tool

### Key Clarifications
- RAG retrieval is hardcoded in the pipeline, not an AI decision
- Corpus = the documents RAG searches through
- MCP tools are AI-chosen; RAG retrieval is deterministic
- Corpus size is fine for learning (can expand later)
- 8-12 hours estimated for initial corpus creation with LLM help

### What You Should Do Next

**Option 1: Start with Phase 0 Design Discussion**
Use your 4-phase dev framework. Begin Phase 0 to discuss:
- Corpus structure decisions
- UI/UX for the Streamlit app
- Document chunking strategy

**Option 2: Start Building Foundation**
Skip to implementation:
- Create folder structure
- Chunk existing ARCHITECTURE.md and README.md
- Follow Module 1-2 as you build

**Option 3: Create Corpus First**
Focus on content:
- Expand existing docs into chunked files
- Write initial how-to guides
- Create Q&A pairs

### Recommendation for Claude Code

When you start your Claude Code session, share this document and say:

"I'm building a RAG-powered training assistant for my QA automation framework. This document contains all our planning discussions. I want to use my 4-phase dev framework (Phase 0 → PRD → Tasks → Execute).

Let's start with Phase 0 design discussion for the training-assistant module. Key areas to discuss:
1. Corpus structure and chunking strategy
2. Streamlit UI layout and features
3. RAG pipeline components

I'll be learning RAG through the DeepLearning.ai course and applying concepts here as I go."

---

## Resources

### Course
- DeepLearning.ai RAG Specialization (Coursera)

### Existing Project Assets
- py-selenium-framework-mcp repository
- ARCHITECTURE.md (expand into multiple docs)
- README.md (expand into multiple docs)
- Existing test code (extract as examples)

### RAG Tools (to explore during course)
- LangChain (popular RAG framework)
- LlamaIndex (alternative RAG framework)
- Chroma (local vector database)
- FAISS (Facebook's vector search)
- Pinecone (cloud vector database)

### LLM Providers
- OpenAI API
- Anthropic API
- Together.ai (used in course labs)

---

## Final Notes

### Why This Project Will Work

**Clear value:**
- Documentation you need to write anyway
- Interactive tool that actually helps onboarding
- Portfolio piece showing RAG + QA expertise

**Right scope:**
- Small enough to complete alongside course
- Large enough to exercise real RAG concepts
- Natural growth path (expand corpus over time)

**Motivated learning:**
- Applies directly to your existing project
- Builds on your QA background
- Creates something you'll actually use

### Potential Challenges

**Corpus creation:** Takes time, but LLM can help draft content
**Evaluation:** Hard to measure "good" retrieval — course Module 5 helps
**Scope creep:** Resist adding features until core RAG works

### This Is Incremental

You don't need everything working on day one:
- Week 1-2: Basic retrieval with 15-20 docs
- Week 3-4: Semantic search
- Week 5-6: LLM generation
- Week 7+: Polish and expand

Build alongside the course. Each module adds capability.

---

*End of project context document. Ready for Phase 0 design discussion in Claude Code.*
