# Defect Log - RAG Training Assistant

Tracking test failures and resolutions for the RAG Training Assistant project.

---

### DEF-001: Negative overlap not validated in chunker

**Date:** 2025-12-13
**Test:** `rag/ingestion/tests/test_chunker.py::TestChunkingNegative::test_overlap_negative_raises_error`
**Component:** Ingestion / Chunker

**Error:**
```
Failed: DID NOT RAISE <class 'ValueError'>
```

**Root Cause:**
`chunk_document()` validates `overlap >= chunk_size` but does not validate `overlap < 0`. Negative overlap is accepted silently, which could cause unexpected behavior (step size larger than chunk_size).

**Attempted Fixes:**
1. Option A: Raise ValueError (chosen) - PASSED

**Fix Options Analyzed:**
| Option | Approach | Verdict |
|--------|----------|---------|
| A | Raise ValueError | Chosen - fail fast, consistent |
| B | abs(overlap) | Rejected - hides user mistake |
| C | max(0, overlap) | Rejected - silently changes behavior |
| D | Dataclass validation | Rejected - overkill for learning |

**Solution:**
Added validation in `chunk_document()`:
```python
if overlap < 0:
    raise ValueError(f"overlap ({overlap}) must be non-negative")
```

**Status:** RESOLVED

**Resolution:** Added input validation for negative overlap
**Verified:** 2025-12-13

**Prevention:**
Add input validation tests (negative tests) for all numeric parameters when building new functions.

---
