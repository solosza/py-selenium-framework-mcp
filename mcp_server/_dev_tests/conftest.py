"""
Pytest configuration for MCP server dev tests.

Registers custom markers and shared fixtures.
"""

import pytest


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "unit: Unit tests (fast, isolated)")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests (> 1 second)")
    config.addinivalue_line("markers", "smoke: Critical path tests")

    # Component markers
    config.addinivalue_line("markers", "state_manager: StateManager component tests")
    config.addinivalue_line("markers", "gates: Quality gate tests")
    config.addinivalue_line("markers", "base_gate: BaseGate infrastructure tests")
