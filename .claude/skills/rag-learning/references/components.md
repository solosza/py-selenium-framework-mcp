<!-- LICENSE: Proprietary - Isagawa Corp -->
<!-- You may USE this skill with Claude Code. -->
<!-- You may NOT redistribute, modify, or create derivative works. -->
<!-- See LICENSE.md for full terms. -->

# RAG Component Deep Dive

Detailed reference for each RAG pipeline component. Load when user needs more depth on a specific component.

## Document Loading

### What It Does
Reads files from disk/source and extracts text content.

### Format Considerations

| Format | Complexity | Watch Out For |
|--------|------------|---------------|
| .txt | Simple | Encoding issues |
| .md | Simple | May want to preserve headers as metadata |
| .pdf | Complex | Tables, columns, images with text |
| .docx | Medium | Formatting, embedded objects |
| .html | Medium | Strip tags vs preserve structure |

### Metadata to Extract
- Filename (useful for source attribution)
- Section headers (useful for filtering)
- Date modified (useful for recency)
- Custom tags (if present)

### Manual Implementation Pattern
```python
import os
from pathlib import Path

def load_documents(folder_path):
    docs = []
    for file_path in Path(folder_path).glob("**/*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            docs.append({
                "content": content,
                "source": str(file_path),
                "filename": file_path.name
            })
    return docs
```

---

## Chunking

### What It Does
Splits documents into smaller pieces that fit in embedding model context and provide focused retrieval units.

### Size Guidelines
- **Too small (<100 tokens):** Loses context, fragments meaning
- **Sweet spot (200-500 tokens):** Balanced context and specificity  
- **Too large (>1000 tokens):** May exceed embedding limits, retrieves irrelevant content

### Overlap
- **Why overlap:** Prevents cutting sentences/ideas in half
- **Typical overlap:** 10-20% of chunk size
- **Example:** 500 token chunks with 50 token overlap

### Chunking Strategies

**Fixed Size**
```python
def chunk_fixed(text, size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
```

**Sentence-Based**
```python
import re

def chunk_sentences(text, max_sentences=5):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    for i in range(0, len(sentences), max_sentences):
        chunk = ' '.join(sentences[i:i+max_sentences])
        chunks.append(chunk)
    return chunks
```

**Recursive/Semantic (Framework Pattern)**
- Split by headers first
- Then paragraphs
- Then sentences
- Then characters (last resort)

### Common Mistakes
1. Chunking code without respecting function boundaries
2. Splitting markdown without preserving header context
3. No overlap causing mid-sentence breaks

---

## Embedding

### What It Does
Converts text into numerical vectors that capture semantic meaning.

### Key Concepts
- **Dimensions:** Length of vector (768, 1024, 1536 common)
- **Similarity:** Closer vectors = more similar meaning
- **Model consistency:** Same model for indexing AND querying

### Popular Models

| Model | Dimensions | Cost | Quality |
|-------|------------|------|---------|
| OpenAI text-embedding-3-small | 1536 | $0.02/1M tokens | High |
| OpenAI text-embedding-3-large | 3072 | $0.13/1M tokens | Higher |
| BAAI/bge-base-en-v1.5 | 768 | Free (local) | Good |
| all-MiniLM-L6-v2 | 384 | Free (local) | Decent |

### Manual Implementation Pattern
```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer('BAAI/bge-base-en-v1.5')

def embed_texts(texts):
    return model.encode(texts)

def embed_query(query):
    return model.encode(query)
```

### Token Limits
- Most models: 512 tokens max
- Longer text gets truncated (silently!)
- This is why chunking matters

---

## Vector Storage

### What It Does
Stores embeddings and enables fast similarity search.

### Options Comparison

**In-Memory (List)**
- Simplest possible
- Good for: Learning, <1000 chunks
- Bad for: Persistence, scale
```python
vectors = []  # Just a list of numpy arrays
```

**Chroma**
- Local, persistent
- Good for: Development, small-medium projects
- Bad for: Large scale
```python
import chromadb
client = chromadb.Client()
collection = client.create_collection("docs")
```

**FAISS**
- Facebook's library, very fast
- Good for: Speed, local, medium-large
- Bad for: Simplicity (steeper learning curve)

**Pinecone**
- Cloud hosted
- Good for: Production, scale, managed
- Bad for: Cost, data privacy concerns

### When to Upgrade
- Start with in-memory or Chroma
- Move to FAISS/Pinecone when: >100k chunks, need persistence, production deployment

---

## Search

### What It Does
Finds relevant chunks for a given query.

### Keyword Search (BM25/TF-IDF)

**How it works:** Matches exact/similar words, ranks by frequency and rarity

**Pros:**
- Fast
- Predictable
- Great for exact matches (error codes, names)

**Cons:**
- Misses synonyms
- Can't handle rephrased queries

```python
from rank_bm25 import BM25Okapi

def keyword_search(query, documents, top_k=5):
    tokenized_docs = [doc.split() for doc in documents]
    bm25 = BM25Okapi(tokenized_docs)
    scores = bm25.get_scores(query.split())
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [documents[i] for i in top_indices]
```

### Semantic Search (Vector)

**How it works:** Compares embedding similarity (cosine or euclidean)

**Pros:**
- Understands meaning
- Handles varied phrasing

**Cons:**
- Can miss exact terms
- Slower, costs more

```python
import numpy as np

def cosine_similarity(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def semantic_search(query_embedding, doc_embeddings, documents, top_k=5):
    scores = [cosine_similarity(query_embedding, doc_emb) for doc_emb in doc_embeddings]
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [documents[i] for i in top_indices]
```

### Hybrid Search

**How it works:** Combines keyword and semantic scores

**Approach:**
1. Get top N from keyword search
2. Get top N from semantic search
3. Combine with weighted scores or reciprocal rank fusion

```python
def hybrid_search(query, documents, doc_embeddings, query_embedding, top_k=5, alpha=0.5):
    # Get keyword scores
    keyword_scores = get_bm25_scores(query, documents)
    # Get semantic scores  
    semantic_scores = get_cosine_scores(query_embedding, doc_embeddings)
    # Normalize both to 0-1
    keyword_norm = normalize(keyword_scores)
    semantic_norm = normalize(semantic_scores)
    # Combine
    combined = alpha * keyword_norm + (1 - alpha) * semantic_norm
    # Return top k
    top_indices = sorted(range(len(combined)), key=lambda i: combined[i], reverse=True)[:top_k]
    return [documents[i] for i in top_indices]
```

---

## Prompt Building

### What It Does
Formats retrieved context + query into prompt for LLM.

### Basic Template
```
Use the following context to answer the question.

Context:
{retrieved_chunks}

Question: {user_query}

Answer:
```

### Better Template
```
You are a helpful assistant that answers questions based on the provided documentation.

Instructions:
- Only use information from the context below
- If the context doesn't contain the answer, say "I don't have information about that"
- Cite which section the information comes from

Context:
{retrieved_chunks}

Question: {user_query}
```

### Formatting Retrieved Chunks
```python
def format_context(chunks):
    formatted = []
    for i, chunk in enumerate(chunks):
        formatted.append(f"[Source {i+1}: {chunk['source']}]\n{chunk['content']}")
    return "\n\n---\n\n".join(formatted)
```

### Context Window Management
- Count tokens before sending
- Truncate oldest/lowest-scored chunks if over limit
- Leave room for response

---

## Generation

### What It Does
LLM generates answer using retrieved context.

### Key Parameters

| Parameter | What It Does | Typical Values |
|-----------|--------------|----------------|
| temperature | Randomness | 0 (deterministic) to 1 (creative) |
| max_tokens | Response length limit | 256-1024 |
| top_p | Nucleus sampling | 0.9-1.0 |

### For RAG, prefer low temperature (0-0.3) for factual consistency.

### Basic Implementation
```python
from openai import OpenAI

client = OpenAI()

def generate(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=500
    )
    return response.choices[0].message.content
```

### Common Issues
- **Hallucination:** Model adds info not in context → Lower temperature, stronger prompt
- **Ignores context:** Model uses training data instead → Add explicit instruction
- **Too verbose:** Wastes tokens → Set max_tokens, ask for concise response

---

## Evaluation

### What It Does
Measures how well your RAG system performs.

### Retrieval Metrics

**Precision@K:** Of top K retrieved, how many are relevant?
```
Precision@5 = (relevant in top 5) / 5
```

**Recall@K:** Of all relevant docs, how many are in top K?
```
Recall@5 = (relevant in top 5) / (total relevant)
```

**MRR (Mean Reciprocal Rank):** Where does first relevant result appear?
```
MRR = 1 / rank_of_first_relevant
```

### Generation Metrics

**Faithfulness:** Does answer only use retrieved context?
**Relevance:** Does answer address the question?
**Completeness:** Does answer cover all relevant info?

### Creating Test Set
1. Write 10-20 test queries
2. For each, identify which chunks SHOULD be retrieved
3. Write expected answer (or key points)
4. Run system, compare results

### Simple Evaluation Pattern
```python
test_cases = [
    {
        "query": "How do I add a page object?",
        "expected_chunks": ["page_objects.md", "adding_page_object.md"],
        "expected_keywords": ["framework/pages", "locators", "class constants"]
    },
    # ... more cases
]

def evaluate(rag_system, test_cases):
    results = []
    for case in test_cases:
        retrieved = rag_system.retrieve(case["query"])
        retrieved_sources = [c["source"] for c in retrieved]
        
        # Check chunk retrieval
        hits = len(set(case["expected_chunks"]) & set(retrieved_sources))
        precision = hits / len(retrieved_sources)
        recall = hits / len(case["expected_chunks"])
        
        results.append({"query": case["query"], "precision": precision, "recall": recall})
    
    return results
```
