"""
Shared pytest configuration for RAG tests.

This file:
1. Adds training-assistant to sys.path for imports
2. Registers pytest markers
3. Provides shared fixtures (session-scoped embedder)
"""

import sys
from pathlib import Path

import pytest

# Add training-assistant to path for imports
training_assistant_path = Path(__file__).parent.parent
sys.path.insert(0, str(training_assistant_path))


# =============================================================================
# PYTEST MARKERS
# =============================================================================

def pytest_configure(config):
    """Register custom markers."""
    # Component markers
    config.addinivalue_line("markers", "loader: tests for document loader")
    config.addinivalue_line("markers", "chunker: tests for text chunker")
    config.addinivalue_line("markers", "embedder: tests for embedder")

    # Test type markers
    config.addinivalue_line("markers", "unit: fast, isolated unit tests")
    config.addinivalue_line("markers", "integration: tests multiple components together")
    config.addinivalue_line("markers", "slow: tests that take > 1 second")
    config.addinivalue_line("markers", "smoke: critical path tests")


# =============================================================================
# SHARED FIXTURES
# =============================================================================

@pytest.fixture(scope="session")
def embedder():
    """
    Session-scoped embedder fixture.

    Model loads once for all tests that need it.
    This is expensive (~2-3s first load) so we share across tests.
    """
    from rag.ingestion import Embedder
    return Embedder()
