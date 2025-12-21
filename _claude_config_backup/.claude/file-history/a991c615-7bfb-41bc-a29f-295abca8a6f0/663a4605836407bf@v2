"""
Tests for Embedder module.

Run with:
    cd training-assistant
    python tests/_reports/run_tests.py test_embedder.py

Test Pyramid Layers:
1. DATA STRUCTURE     - Embedding dataclass
2. MODEL LOADING      - Model initialization
3. CORE EMBEDDING     - embed_text produces vectors
4. SEMANTIC CORRECT   - Similar text → similar vectors
5. DETERMINISM        - Same input → same output
6. BATCH OPERATIONS   - embed_chunks handles N items
7. EDGE CASES         - Empty, unicode, long text
8. ERROR HANDLING     - Invalid input fails gracefully
9. INTEGRATION        - Works with chunker output
"""

import pytest
import numpy as np

from rag.core import Document
from rag.ingestion import Chunk, load_documents
from rag.ingestion import Embedding, Embedder, cosine_similarity, get_embedder_stats


# =============================================================================
# Layer 1: DATA STRUCTURE - Embedding Dataclass
# =============================================================================

@pytest.mark.embedder
@pytest.mark.unit
class TestEmbeddingDataclass:
    """Tests for Embedding dataclass."""

    def test_embedding_creation(self):
        """P0: Create embedding with vector and text."""
        vector = np.array([0.1, 0.2, 0.3])
        embedding = Embedding(
            vector=vector,
            text="test text",
            metadata={"source": "test.txt"}
        )

        assert embedding.text == "test text"
        assert embedding.metadata["source"] == "test.txt"
        np.testing.assert_array_equal(embedding.vector, vector)

    def test_embedding_dimensions(self):
        """P0: dimensions property returns correct length."""
        vector = np.array([0.1, 0.2, 0.3, 0.4, 0.5])
        embedding = Embedding(vector=vector, text="test")

        assert embedding.dimensions == 5

    def test_embedding_to_list(self):
        """P0: to_list() converts numpy to Python list."""
        vector = np.array([0.1, 0.2, 0.3])
        embedding = Embedding(vector=vector, text="test")

        result = embedding.to_list()

        assert isinstance(result, list)
        assert result == [0.1, 0.2, 0.3]

    def test_embedding_repr(self):
        """P1: repr shows useful debug info."""
        vector = np.zeros(384)
        embedding = Embedding(
            vector=vector,
            text="hello world",
            metadata={"model_name": "test-model"}
        )

        repr_str = repr(embedding)

        assert "384" in repr_str  # dimensions
        assert "test-model" in repr_str
        assert "hello" in repr_str


# =============================================================================
# Layer 2: MODEL LOADING
# =============================================================================

@pytest.mark.embedder
@pytest.mark.slow
class TestModelLoading:
    """Tests for model initialization."""

    def test_embedder_initialization(self):
        """P0: Initialize embedder with default model."""
        embedder = Embedder()

        assert embedder.model_name == "all-MiniLM-L6-v2"

    def test_model_loads_successfully(self):
        """P0: Model loads and produces correct dimensions."""
        embedder = Embedder()

        # Access dimensions triggers model load
        dims = embedder.dimensions

        assert dims == 384  # all-MiniLM-L6-v2 has 384 dimensions

    def test_lazy_loading(self):
        """P1: Model not loaded until first use."""
        embedder = Embedder()

        # Model should not be loaded yet
        assert embedder._model is None

        # Trigger load
        _ = embedder.dimensions

        # Now model should be loaded
        assert embedder._model is not None


# =============================================================================
# Layer 3: CORE EMBEDDING
# =============================================================================

@pytest.mark.embedder
@pytest.mark.unit
class TestCoreEmbedding:
    """Tests for embed_text functionality."""
    # Uses session-scoped embedder fixture from conftest.py

    def test_embed_text_returns_vector(self, embedder):
        """P0: Embed normal text returns numpy array."""
        result = embedder.embed_text("Hello world")

        assert isinstance(result, np.ndarray)

    def test_embed_text_correct_dimensions(self, embedder):
        """P0: Vector has correct dimensions for model."""
        result = embedder.embed_text("Hello world")

        assert result.shape == (384,)

    def test_embed_text_values_are_floats(self, embedder):
        """P0: Vector contains float values."""
        result = embedder.embed_text("Hello world")

        assert result.dtype in [np.float32, np.float64]


# =============================================================================
# Layer 4: SEMANTIC CORRECTNESS
# =============================================================================

@pytest.mark.embedder
@pytest.mark.unit
class TestSemanticCorrectness:
    """Tests for semantic meaning preservation."""
    # Uses session-scoped embedder fixture from conftest.py

    def test_same_text_similarity_one(self, embedder):
        """P0: Same text has similarity ~1.0."""
        vec = embedder.embed_text("user authentication")

        similarity = cosine_similarity(vec, vec)

        assert similarity > 0.999  # Allow tiny floating point variance

    def test_synonyms_high_similarity(self, embedder):
        """P0: Synonyms have high similarity."""
        vec1 = embedder.embed_text("login")
        vec2 = embedder.embed_text("sign in")

        similarity = cosine_similarity(vec1, vec2)

        assert similarity > 0.5  # Should be reasonably similar

    def test_unrelated_low_similarity(self, embedder):
        """P0: Unrelated texts have lower similarity."""
        vec1 = embedder.embed_text("user authentication login")
        vec2 = embedder.embed_text("weather forecast sunny")

        similarity = cosine_similarity(vec1, vec2)

        assert similarity < 0.5  # Should be dissimilar

    def test_related_higher_than_unrelated(self, embedder):
        """P0: Related text more similar than unrelated."""
        vec_query = embedder.embed_text("how to log in")
        vec_related = embedder.embed_text("enter your username and password")
        vec_unrelated = embedder.embed_text("the weather is nice today")

        sim_related = cosine_similarity(vec_query, vec_related)
        sim_unrelated = cosine_similarity(vec_query, vec_unrelated)

        assert sim_related > sim_unrelated


# =============================================================================
# Layer 5: DETERMINISM
# =============================================================================

@pytest.mark.embedder
@pytest.mark.unit
class TestDeterminism:
    """Tests for consistent output."""
    # Uses session-scoped embedder fixture from conftest.py

    def test_same_input_same_output(self, embedder):
        """P0: Same text produces identical vector."""
        text = "test determinism"

        vec1 = embedder.embed_text(text)
        vec2 = embedder.embed_text(text)

        np.testing.assert_array_equal(vec1, vec2)

    def test_batch_matches_single(self, embedder):
        """P1: Same text in batch produces same as single."""
        text = "batch test"

        single = embedder.embed_text(text)
        batch = embedder.embed_texts([text])[0]

        np.testing.assert_array_almost_equal(single, batch, decimal=5)


# =============================================================================
# Layer 6: BATCH OPERATIONS
# =============================================================================

@pytest.mark.embedder
@pytest.mark.unit
class TestBatchOperations:
    """Tests for batch embedding."""
    # Uses session-scoped embedder fixture from conftest.py

    def test_embed_multiple_chunks(self, embedder):
        """P0: Embed multiple chunks returns list of embeddings."""
        chunks = [
            Chunk(text="First chunk", metadata={"source": "test.txt"}),
            Chunk(text="Second chunk", metadata={"source": "test.txt"}),
        ]

        embeddings = embedder.embed_chunks(chunks)

        assert len(embeddings) == 2
        assert all(isinstance(e, Embedding) for e in embeddings)

    def test_metadata_preserved(self, embedder):
        """P0: Metadata from chunks preserved in embeddings."""
        chunk = Chunk(
            text="Test chunk",
            metadata={"source": "test.txt", "chunk_index": 0}
        )

        embeddings = embedder.embed_chunks([chunk])

        assert embeddings[0].metadata["source"] == "test.txt"
        assert embeddings[0].metadata["chunk_index"] == 0

    def test_model_name_added_to_metadata(self, embedder):
        """P0: Model name added to embedding metadata."""
        chunk = Chunk(text="Test", metadata={})

        embeddings = embedder.embed_chunks([chunk])

        assert embeddings[0].metadata["model_name"] == "all-MiniLM-L6-v2"
        assert embeddings[0].metadata["dimensions"] == 384

    def test_empty_list_returns_empty(self, embedder):
        """P0: Empty chunk list returns empty embedding list."""
        embeddings = embedder.embed_chunks([])

        assert embeddings == []

    def test_batch_ten_chunks(self, embedder):
        """P1: Handle 10+ chunks in batch."""
        chunks = [
            Chunk(text=f"Chunk number {i}", metadata={"index": i})
            for i in range(10)
        ]

        embeddings = embedder.embed_chunks(chunks)

        assert len(embeddings) == 10


# =============================================================================
# Layer 7: EDGE CASES
# =============================================================================

@pytest.mark.embedder
@pytest.mark.unit
class TestEdgeCases:
    """Tests for unusual but valid inputs."""
    # Uses session-scoped embedder fixture from conftest.py

    def test_empty_string_returns_zero_vector(self, embedder):
        """P0: Empty string returns zero vector."""
        result = embedder.embed_text("")

        assert result.shape == (384,)
        np.testing.assert_array_equal(result, np.zeros(384))

    def test_whitespace_only(self, embedder):
        """P1: Whitespace-only text handled."""
        result = embedder.embed_text("   ")

        assert result.shape == (384,)

    def test_unicode_text(self, embedder):
        """P1: Unicode text embeds correctly."""
        result = embedder.embed_text("Hello 世界 🌍")

        assert result.shape == (384,)
        assert not np.all(result == 0)  # Should produce non-zero embedding


# =============================================================================
# Layer 8: ERROR HANDLING
# =============================================================================

@pytest.mark.embedder
@pytest.mark.unit
class TestErrorHandling:
    """Tests for error conditions."""

    def test_cosine_similarity_dimension_mismatch(self):
        """P0: Mismatched dimensions raises error."""
        vec1 = np.array([0.1, 0.2, 0.3])
        vec2 = np.array([0.1, 0.2])

        with pytest.raises(ValueError) as exc_info:
            cosine_similarity(vec1, vec2)

        assert "shape" in str(exc_info.value).lower()

    def test_cosine_similarity_zero_vector(self):
        """P1: Zero vector returns 0.0 similarity."""
        vec1 = np.zeros(5)
        vec2 = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

        result = cosine_similarity(vec1, vec2)

        assert result == 0.0


# =============================================================================
# Layer 9: INTEGRATION
# =============================================================================

@pytest.mark.embedder
@pytest.mark.integration
class TestIntegration:
    """Tests for integration with other components."""
    # Uses session-scoped embedder fixture from conftest.py

    def test_embed_chunk_from_document(self, embedder):
        """P0: Embed chunk created from Document."""
        doc = Document(text="Test document content", metadata={"source": "test.md"})
        chunk = Chunk(
            text=doc.text,
            metadata={**doc.metadata, "chunk_index": 0}
        )

        embedding = embedder.embed_chunk(chunk)

        assert embedding.metadata["source"] == "test.md"
        assert embedding.metadata["chunk_index"] == 0
        assert embedding.dimensions == 384

    def test_metadata_flows_through_pipeline(self, embedder):
        """P0: Metadata preserved from document through chunk to embedding."""
        # Simulate pipeline: Document -> Chunk -> Embedding
        original_metadata = {
            "source": "pipeline_test.txt",
            "file_type": ".txt",
            "custom_field": "custom_value"
        }

        chunk = Chunk(
            text="Pipeline test content",
            metadata={**original_metadata, "chunk_index": 0, "chunk_total": 1}
        )

        embedding = embedder.embed_chunk(chunk)

        # All original metadata should be preserved
        assert embedding.metadata["source"] == "pipeline_test.txt"
        assert embedding.metadata["file_type"] == ".txt"
        assert embedding.metadata["custom_field"] == "custom_value"
        # Plus chunk metadata
        assert embedding.metadata["chunk_index"] == 0
        # Plus embedding metadata
        assert embedding.metadata["model_name"] == "all-MiniLM-L6-v2"


# =============================================================================
# Layer 10: STATS FUNCTION
# =============================================================================

@pytest.mark.embedder
@pytest.mark.unit
class TestStatsFunction:
    """Tests for get_embedder_stats."""

    def test_empty_embeddings_stats(self):
        """P0: Stats for empty list."""
        stats = get_embedder_stats([])

        assert stats["total_embeddings"] == 0
        assert stats["model_name"] is None

    def test_stats_counts(self):
        """P0: Stats returns correct counts."""
        embeddings = [
            Embedding(
                vector=np.zeros(384),
                text="test",
                metadata={"source": "a.txt", "model_name": "test-model", "dimensions": 384}
            ),
            Embedding(
                vector=np.zeros(384),
                text="test2",
                metadata={"source": "b.txt", "model_name": "test-model", "dimensions": 384}
            ),
        ]

        stats = get_embedder_stats(embeddings)

        assert stats["total_embeddings"] == 2
        assert stats["model_name"] == "test-model"
        assert set(stats["sources"]) == {"a.txt", "b.txt"}
