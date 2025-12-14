# RAG Experiments

Hands-on experiments for each component. Run these to build intuition.

## Chunking Experiments

### Experiment C1: Chunk Size Impact
**Setup:** Same document, same query
**Variables:** Chunk sizes of 100, 300, 500, 1000 tokens
**Observe:** 
- Which returns most relevant chunks?
- Which includes too much noise?
- Which cuts off important context?

### Experiment C2: Overlap Impact
**Setup:** 500 token chunks, same query
**Variables:** 0%, 10%, 20%, 50% overlap
**Observe:**
- Do any chunks lose context at boundaries?
- Is there unnecessary duplication?

### Experiment C3: Split Strategy
**Setup:** Markdown document with headers
**Variables:** Fixed size vs split-by-header vs recursive
**Observe:**
- Does header context stay with content?
- Are code blocks kept intact?

---

## Embedding Experiments

### Experiment E1: Synonym Detection
**Setup:** Embed these pairs and check similarity
```
("car", "automobile")      # Should be high
("car", "vehicle")         # Should be high  
("car", "banana")          # Should be low
("happy", "joyful")        # Should be high
("happy", "sad")           # Should be low (opposites)
```
**Observe:** Does the model capture semantic relationships?

### Experiment E2: Sentence vs Words
**Setup:** Compare embeddings
```
"bank" (alone)
"river bank"
"bank account"
```
**Observe:** Does context change the embedding?

### Experiment E3: Truncation
**Setup:** Embed a 1000-word document
**Compare:** Full doc embedding vs first-500-words embedding
**Observe:** Are they identical? (They probably are — truncation!)

---

## Search Experiments

### Experiment S1: Keyword vs Semantic
**Setup:** Same corpus, these queries:
```
Query 1: "TimeoutException" (exact term)
Query 2: "test is taking too long" (semantic)
Query 3: "element not found error" (mix)
```
**Compare:** Keyword search results vs semantic search results
**Observe:** Which performs better for each query type?

### Experiment S2: Top-K Selection
**Setup:** Same query
**Variables:** top_k = 1, 3, 5, 10
**Observe:** 
- At what K do results become irrelevant?
- What's the tradeoff (more context vs noise)?

### Experiment S3: Query Formulation
**Setup:** Same intent, different phrasing
```
"How do I add a page object?"
"Adding page objects"
"Create new page object class"
"page object tutorial"
```
**Observe:** Do all retrieve the same chunks? Which works best?

---

## Prompt Experiments

### Experiment P1: Instruction Clarity
**Setup:** Same retrieved chunks, different prompts
```
Prompt A: "Answer this: {query}"
Prompt B: "Using only the context below, answer: {query}"
Prompt C: "You are an expert. Using the documentation provided, answer: {query}. If not found, say so."
```
**Observe:** Which produces most grounded answers?

### Experiment P2: Context Format
**Setup:** Same chunks, different formatting
```
Format A: Plain concatenation
Format B: Numbered sources
Format C: With source citations
```
**Observe:** Does formatting affect answer quality?

### Experiment P3: Context Order
**Setup:** Same 5 chunks, different orders
```
Order A: Most relevant first
Order B: Most relevant last
Order C: Random
```
**Observe:** Does position affect what LLM uses?

---

## Generation Experiments

### Experiment G1: Temperature
**Setup:** Same prompt, run 3 times each
**Variables:** temperature = 0, 0.3, 0.7, 1.0
**Observe:** 
- Consistency across runs?
- Creativity vs accuracy tradeoff?

### Experiment G2: Model Comparison
**Setup:** Same prompt
**Variables:** GPT-3.5 vs GPT-4 vs Claude vs local model
**Observe:** Quality, cost, speed differences

### Experiment G3: Hallucination Test
**Setup:** Ask about something NOT in context
**Observe:** Does model admit ignorance or make up answer?

---

## End-to-End Experiments

### Experiment E2E1: Full Pipeline Comparison
**Setup:** 10 test queries with known answers
**Compare:** 
- Keyword-only pipeline
- Semantic-only pipeline  
- Hybrid pipeline
**Observe:** Overall accuracy on test set

### Experiment E2E2: Failure Analysis
**Setup:** Find 3 queries where system fails
**Investigate:** At which stage did it fail?
- Wrong chunks retrieved?
- Right chunks, bad prompt?
- Right chunks, right prompt, bad generation?

### Experiment E2E3: Edge Cases
**Test these:**
- Empty query
- Very long query (1000+ words)
- Query in different language
- Query with typos
- Query about topic not in corpus
**Observe:** How does system handle each?

---

## Recording Results Template

For each experiment, record:

```markdown
## Experiment: [Name]

**Date:** 
**Component:** 

### Setup
- Corpus: 
- Query/Input: 
- Variables tested: 

### Results

| Variable | Result | Notes |
|----------|--------|-------|
| | | |

### Observations
- 

### What I Learned
- 

### Follow-up Questions
- 
```
