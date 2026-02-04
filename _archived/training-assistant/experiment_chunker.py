"""
Chunker Experiments - Interactive learning through experimentation.

This script supports the EXPERIMENT phase of RAG learning.
Run different chunking configurations and observe results.
"""

import sys
from pathlib import Path

# Add training-assistant to path
sys.path.insert(0, str(Path(__file__).parent))

from rag.ingestion import load_documents, chunk_documents, get_loader_stats


def load_sample_corpus():
    """Load a sample of documents for experimentation."""
    # Use current project as corpus
    corpus_path = Path(__file__).parent.parent

    # Load just framework docs for faster experimentation
    docs = load_documents([
        corpus_path / "framework",
        corpus_path / "CLAUDE.md",
        corpus_path / "FRAMEWORK.md",
    ])
    return docs


def experiment_chunk_sizes(docs, sizes=[500, 1000, 2000, 4000]):
    """Compare different chunk sizes."""
    print("\n" + "="*60)
    print("EXPERIMENT: Chunk Size Comparison")
    print("="*60)

    results = []
    for size in sizes:
        chunks = chunk_documents(docs, chunk_size=size, overlap=int(size * 0.1))

        # Calculate stats
        chunk_lengths = [len(c.text) for c in chunks]
        avg_len = sum(chunk_lengths) / len(chunk_lengths) if chunks else 0

        result = {
            "size": size,
            "overlap": int(size * 0.1),
            "chunk_count": len(chunks),
            "avg_chars": int(avg_len),
            "avg_tokens": int(avg_len / 4),
        }
        results.append(result)

        print(f"\nchunk_size={size}, overlap={int(size*0.1)}:")
        print(f"  Chunks: {len(chunks)}")
        print(f"  Avg chars: {int(avg_len)}")
        print(f"  Avg tokens: ~{int(avg_len/4)}")

    return results


def experiment_overlap_ratios(docs, chunk_size=1000, ratios=[0, 0.1, 0.2, 0.3]):
    """Compare different overlap ratios."""
    print("\n" + "="*60)
    print(f"EXPERIMENT: Overlap Ratio Comparison (chunk_size={chunk_size})")
    print("="*60)

    results = []
    for ratio in ratios:
        overlap = int(chunk_size * ratio)
        chunks = chunk_documents(docs, chunk_size=chunk_size, overlap=overlap)

        result = {
            "ratio": f"{int(ratio*100)}%",
            "overlap": overlap,
            "chunk_count": len(chunks),
        }
        results.append(result)

        print(f"\noverlap={ratio*100:.0f}% ({overlap} chars):")
        print(f"  Chunks: {len(chunks)}")

    return results


def show_chunk_samples(docs, chunk_size=1000, overlap=100, n_samples=3):
    """Show sample chunks to inspect quality."""
    print("\n" + "="*60)
    print(f"EXPERIMENT: Sample Chunks (size={chunk_size}, overlap={overlap})")
    print("="*60)

    chunks = chunk_documents(docs, chunk_size=chunk_size, overlap=overlap)

    for i, chunk in enumerate(chunks[:n_samples]):
        print(f"\n--- Chunk {i+1}/{len(chunks)} ---")
        print(f"Source: {chunk.metadata.get('source', 'unknown')}")
        print(f"Chars: {len(chunk.text)}, Tokens: ~{chunk.token_estimate}")
        print(f"Content preview:")
        print("-" * 40)
        # Show first 300 chars
        preview = chunk.text[:300].replace('\n', '\n  ')
        print(f"  {preview}...")
        print("-" * 40)

    return chunks


def show_chunk_boundaries(docs, chunk_size=500, overlap=50):
    """Show where chunks are cut to identify boundary issues."""
    print("\n" + "="*60)
    print(f"EXPERIMENT: Chunk Boundaries (size={chunk_size}, overlap={overlap})")
    print("="*60)

    # Get first document with enough content
    large_docs = [d for d in docs if len(d.text) > chunk_size * 2]
    if not large_docs:
        print("No documents large enough for this experiment")
        return

    doc = large_docs[0]
    chunks = chunk_documents([doc], chunk_size=chunk_size, overlap=overlap)

    print(f"\nDocument: {doc.metadata.get('source', 'unknown')}")
    print(f"Total chars: {len(doc.text)}")
    print(f"Chunks created: {len(chunks)}")

    for i, chunk in enumerate(chunks[:4]):  # Show first 4 chunks
        print(f"\n--- Chunk {i+1} boundary ---")
        # Show last 50 chars of this chunk
        end_preview = chunk.text[-50:].replace('\n', '\\n')
        print(f"  ENDS WITH: ...{end_preview}")

        if i < len(chunks) - 1:
            # Show first 50 chars of next chunk
            next_chunk = chunks[i + 1]
            start_preview = next_chunk.text[:50].replace('\n', '\\n')
            print(f"  NEXT STARTS: {start_preview}...")

    return chunks


def compare_file_types(docs, chunk_size=1000, overlap=100):
    """Compare chunking results across different file types."""
    print("\n" + "="*60)
    print(f"EXPERIMENT: File Type Comparison")
    print("="*60)

    # Group by file type
    by_type = {}
    for doc in docs:
        file_type = doc.metadata.get("file_type", "unknown")
        if file_type not in by_type:
            by_type[file_type] = []
        by_type[file_type].append(doc)

    for file_type, type_docs in by_type.items():
        chunks = chunk_documents(type_docs, chunk_size=chunk_size, overlap=overlap)
        total_chars = sum(len(d.text) for d in type_docs)

        print(f"\n{file_type}:")
        print(f"  Documents: {len(type_docs)}")
        print(f"  Total chars: {total_chars:,}")
        print(f"  Chunks created: {len(chunks)}")
        print(f"  Avg chunk size: {total_chars // len(chunks) if chunks else 0}")


if __name__ == "__main__":
    print("Loading sample corpus...")
    docs = load_sample_corpus()
    stats = get_loader_stats(docs)

    print(f"\nCorpus loaded:")
    print(f"  Documents: {stats['total_documents']}")
    print(f"  Total chars: {stats['total_characters']:,}")
    print(f"  Est. tokens: ~{stats['estimated_tokens']:,}")

    # Run all experiments
    experiment_chunk_sizes(docs)
    experiment_overlap_ratios(docs)
    show_chunk_samples(docs)
    show_chunk_boundaries(docs)
    compare_file_types(docs)
