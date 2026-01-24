"""
Pytest configuration for MCP server dev tests.

Registers custom markers and shared fixtures.
"""

import sys
from pathlib import Path

import pytest

# Add mcp_server directory to Python path for imports
MCP_SERVER_DIR = Path(__file__).parent.parent
if str(MCP_SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(MCP_SERVER_DIR))


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
    config.addinivalue_line("markers", "qg_preflight: Step 1 preflight gate tests")
    config.addinivalue_line("markers", "qg_user_input: Step 2 user input gate tests")
    config.addinivalue_line("markers", "qg_ai_processing: Step 3 AI processing gate tests")
    config.addinivalue_line("markers", "qg_test_scenarios: Step 4 test scenarios gate tests")

    # Component markers - Step 1 v4.0
    config.addinivalue_line("markers", "transcript: TranscriptWriter component tests")
    config.addinivalue_line("markers", "protocol: Protocol adherence tests")
    config.addinivalue_line("markers", "gate: Gate validation tests")
    config.addinivalue_line("markers", "state: StateManager tests")
    config.addinivalue_line("markers", "audit: AuditLogger tests")
    config.addinivalue_line("markers", "hook: PostToolUse hook tests")
    config.addinivalue_line("markers", "layer1: Test pyramid layer 1 (basic operations)")
    config.addinivalue_line("markers", "layer2: Test pyramid layer 2 (formatting/edge cases)")
    config.addinivalue_line("markers", "layer3: Test pyramid layer 3 (integration)")
    config.addinivalue_line("markers", "layer4: Test pyramid layer 4 (production failures)")
    config.addinivalue_line("markers", "security: Security validation tests")
