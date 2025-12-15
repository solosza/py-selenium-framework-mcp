"""
Embedder: Converts text chunks into numerical vectors for similarity search.

Framework analogy:
    Like converting test requirements into comparable metrics.
    Each embedding captures the "meaning" of text as numbers.

Design Decision: DD-RAG-008
    Sentence Transformers with all-MiniLM-L6-v2 model.
    Free, local execution for learning fundamentals.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import numpy as np

from .chunker import Chunk


@dataclass
class Embedding:
    """
    A vector representation of text, ready for similarity search.

    Attributes:
        vector: The numerical embedding (list of floats)
        text: Original text that was embedded
        metadata: Inherited from parent chunk + embedding-specific info

    Embedding-specific metadata:
        - model_name: Which model created this embedding
        - dimensions: Vector length
    """
    vector: np.ndarray
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def dimensions(self) -> int:
        """Return vector dimensionality."""
        return len(self.vector)

    def __repr__(self) -> str:
        """Short representation for debugging."""
        source = self.metadata.get("source", "unknown")
        model = self.metadata.get("model_name", "unknown")
        preview = self.text[:30].replace("\n", " ")
        return f"Embedding(dims={self.dimensions}, model={model}, '{preview}...')"

    def to_list(self) -> List[float]:
        """Convert vector to Python list (for JSON serialization)."""
        return self.vector.tolist()


class Embedder:
    """
    Wrapper around sentence-transformers for creating embeddings.

    Usage:
        embedder = Embedder()  # Uses default model
        embedding = embedder.embed_text("Hello world")
        embeddings = embedder.embed_chunks([chunk1, chunk2])
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedder with a specific model.

        Args:
            model_name: Sentence transformer model name
                        Default: all-MiniLM-L6-v2 (384 dims, fast, good quality)

        Common models:
            - all-MiniLM-L6-v2: 384 dims, fast, good for general use
            - all-mpnet-base-v2: 768 dims, slower, higher quality
            - BAAI/bge-small-en-v1.5: 384 dims, good for retrieval
        """
        self.model_name = model_name
        self._model = None  # Lazy loading

    @property
    def model(self):
        """Lazy load the model on first use."""
        if self._model is None:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
        return self._model

    @property
    def dimensions(self) -> int:
        """Return the embedding dimensions for this model."""
        return self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single text string.

        Args:
            text: The text to embed

        Returns:
            numpy array of shape (dimensions,)
        """
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.dimensions)

        return self.model.encode(text, convert_to_numpy=True)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed multiple texts in batch (more efficient).

        Args:
            texts: List of text strings

        Returns:
            numpy array of shape (n_texts, dimensions)
        """
        if not texts:
            return np.array([])

        # Handle empty strings
        processed = [t if t and t.strip() else " " for t in texts]
        return self.model.encode(processed, convert_to_numpy=True)

    def embed_chunk(self, chunk: Chunk) -> Embedding:
        """
        Embed a single chunk, preserving metadata.

        Args:
            chunk: Chunk object with text and metadata

        Returns:
            Embedding object with vector and combined metadata
        """
        vector = self.embed_text(chunk.text)

        return Embedding(
            vector=vector,
            text=chunk.text,
            metadata={
                **chunk.metadata,
                "model_name": self.model_name,
                "dimensions": self.dimensions
            }
        )

    def embed_chunks(self, chunks: List[Chunk]) -> List[Embedding]:
        """
        Embed multiple chunks in batch.

        Args:
            chunks: List of Chunk objects

        Returns:
            List of Embedding objects with preserved metadata
        """
        if not chunks:
            return []

        # Batch embed all texts
        texts = [chunk.text for chunk in chunks]
        vectors = self.embed_texts(texts)

        # Create Embedding objects with metadata
        embeddings = []
        for i, chunk in enumerate(chunks):
            embedding = Embedding(
                vector=vectors[i],
                text=chunk.text,
                metadata={
                    **chunk.metadata,
                    "model_name": self.model_name,
                    "dimensions": self.dimensions
                }
            )
            embeddings.append(embedding)

        return embeddings


def cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Calculate cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Similarity score between -1 and 1 (1 = identical, 0 = orthogonal)

    Why cosine similarity?
        - Measures angle between vectors, not magnitude
        - Works well for text embeddings
        - Standard metric for semantic similarity
    """
    if vec1.shape != vec2.shape:
        raise ValueError(f"Vector shapes must match: {vec1.shape} vs {vec2.shape}")

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def get_embedder_stats(embeddings: List[Embedding]) -> Dict[str, Any]:
    """
    Get statistics about a collection of embeddings.

    Args:
        embeddings: List of Embedding objects

    Returns:
        Dictionary with statistics
    """
    if not embeddings:
        return {
            "total_embeddings": 0,
            "model_name": None,
            "dimensions": None,
            "sources": []
        }

    sources = set()
    for emb in embeddings:
        source = emb.metadata.get("source", "unknown")
        sources.add(source)

    return {
        "total_embeddings": len(embeddings),
        "model_name": embeddings[0].metadata.get("model_name"),
        "dimensions": embeddings[0].dimensions,
        "sources": list(sources)
    }
