"""
Test Navigation Tracking for Multi-Page Detection (Task 26.0).

Tests the navigation-first scope detection with BDD fallback.

TDD Approach: Write failing tests FIRST (RED), then implement (GREEN).
"""

import json
import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from tools.gates.qg_discovered_elements import QGDiscoveredElements
from utils.state_manager import StateManager
from utils.audit_logger import AuditLogger


class TestNavigationTracking:
    """Test navigation-based scope detection (FR-14.8)."""

    def test_navigation_based_scope_detection(self):
        """
        Test that navigation calls are read from audit log and converted to scope_result.

        Scenario:
        - Audit log contains 2 browser_navigate calls (LoginPage, TransferFundsPage)
        - _calculate_scope_from_navigation() reads audit log
        - Returns scope_result with 2 PageInfo objects
        """
        # Create temporary audit log with navigation calls
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create audit logger with temp directory
            audit_logger = AuditLogger(
                run_id="test_navigation_001",
                output_dir=tmpdir
            )

            # Simulate navigation calls by writing to audit file
            audit_file = Path(tmpdir) / "audit_log_test_navigation_001.json"
            audit_data = {
                "run_id": "test_navigation_001",
                "execution_mode": "mixed",
                "steps": [
                    {
                        "step": 5,
                        "type": "mcp_tool",
                        "tool_name": "browser_navigate",
                        "args": {"url": "https://parabank.parasoft.com/parabank/login.htm"},
                        "timestamp": "2026-01-10T12:00:00Z"
                    },
                    {
                        "step": 5,
                        "type": "mcp_tool",
                        "tool_name": "browser_navigate",
                        "args": {"url": "https://parabank.parasoft.com/parabank/transfer.htm"},
                        "timestamp": "2026-01-10T12:01:00Z"
                    }
                ],
                "files_generated": []
            }

            with open(audit_file, 'w') as f:
                json.dump(audit_data, f)

            # Mock state manager
            state_manager = MagicMock(spec=StateManager)
            state_manager.get_step.return_value = None

            # Inject dependencies
            with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=state_manager), \
                 patch.object(QGDiscoveredElements, 'get_audit_logger', return_value=audit_logger):

                # Call _calculate_scope_from_navigation()
                scope_result = QGDiscoveredElements._calculate_scope_from_navigation()

                # Assertions
                assert scope_result is not None, "Should detect navigation-based scope"
                assert scope_result["page_count"] == 2, "Should detect 2 pages"
                assert len(scope_result["pages"]) == 2, "Should have 2 PageInfo objects"

                # Verify PageInfo structure
                page_names = [p["page_name"] for p in scope_result["pages"]]
                assert "ParabankLoginPage" in page_names, "Should detect ParabankLoginPage from /parabank/login.htm"
                assert "ParabankTransferPage" in page_names, "Should detect ParabankTransferPage from /parabank/transfer.htm"

                # Verify URLs are preserved
                urls = [p["url"] for p in scope_result["pages"]]
                assert "https://parabank.parasoft.com/parabank/login.htm" in urls
                assert "https://parabank.parasoft.com/parabank/transfer.htm" in urls

                # Verify reason field
                assert all(p.get("reason") == "navigation detected" for p in scope_result["pages"])

    def test_navigation_fallback_to_bdd(self):
        """
        Test that BDD fallback works when no navigation calls exist.

        Scenario:
        - Audit log has NO browser_navigate calls (or audit log missing)
        - _calculate_scope_from_navigation() returns None
        - PRE validation falls back to _calculate_scope_result_from_bdd()
        """
        # Create temporary audit log WITHOUT navigation calls
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_logger = AuditLogger(
                run_id="test_navigation_002",
                output_dir=tmpdir
            )

            # Audit log with NO navigation calls
            audit_file = Path(tmpdir) / "audit_log_test_navigation_002.json"
            audit_data = {
                "run_id": "test_navigation_002",
                "execution_mode": "mixed",
                "steps": [
                    {
                        "step": 4,
                        "type": "gate",
                        "gate_name": "qg_test_scenarios",
                        "result": "pass"
                    }
                ],
                "files_generated": []
            }

            with open(audit_file, 'w') as f:
                json.dump(audit_data, f)

            # Mock state manager with BDD scenarios
            state_manager = MagicMock(spec=StateManager)
            state_manager.get_step.side_effect = lambda step: {
                4: {
                    "test_scenarios": [
                        {
                            "name": "User logs in and transfers funds",
                            "given": "A registered user on LoginPage",
                            "when": "User logs in with valid credentials",
                            "then": "User is redirected to AccountsOverviewPage"
                        }
                    ]
                }
            }.get(step, None)

            # Inject dependencies
            with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=state_manager), \
                 patch.object(QGDiscoveredElements, 'get_audit_logger', return_value=audit_logger):

                # Call _calculate_scope_from_navigation() - should return None
                navigation_scope = QGDiscoveredElements._calculate_scope_from_navigation()
                assert navigation_scope is None, "Should return None when no navigation calls"

                # Call _calculate_scope_result_from_bdd() - should succeed
                bdd_scope = QGDiscoveredElements._calculate_scope_result_from_bdd(state_manager)
                assert bdd_scope is not None, "BDD fallback should work"
                assert bdd_scope["page_count"] >= 1, "Should detect at least 1 page from BDD"

    def test_navigation_url_deduplication(self):
        """
        Test that duplicate navigation URLs are deduplicated.

        Scenario:
        - Audit log contains 3 navigate calls: login, transfer, login (duplicate)
        - _calculate_scope_from_navigation() deduplicates URLs
        - Returns scope_result with only 2 unique pages
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_logger = AuditLogger(
                run_id="test_navigation_003",
                output_dir=tmpdir
            )

            # Audit log with DUPLICATE navigation calls
            audit_file = Path(tmpdir) / "audit_log_test_navigation_003.json"
            audit_data = {
                "run_id": "test_navigation_003",
                "execution_mode": "mixed",
                "steps": [
                    {
                        "step": 5,
                        "type": "mcp_tool",
                        "tool_name": "browser_navigate",
                        "args": {"url": "https://parabank.parasoft.com/parabank/login.htm"},
                        "timestamp": "2026-01-10T12:00:00Z"
                    },
                    {
                        "step": 5,
                        "type": "mcp_tool",
                        "tool_name": "browser_navigate",
                        "args": {"url": "https://parabank.parasoft.com/parabank/transfer.htm"},
                        "timestamp": "2026-01-10T12:01:00Z"
                    },
                    {
                        "step": 5,
                        "type": "mcp_tool",
                        "tool_name": "browser_navigate",
                        "args": {"url": "https://parabank.parasoft.com/parabank/login.htm"},  # DUPLICATE
                        "timestamp": "2026-01-10T12:02:00Z"
                    }
                ],
                "files_generated": []
            }

            with open(audit_file, 'w') as f:
                json.dump(audit_data, f)

            # Mock state manager
            state_manager = MagicMock(spec=StateManager)
            state_manager.get_step.return_value = None

            # Inject dependencies
            with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=state_manager), \
                 patch.object(QGDiscoveredElements, 'get_audit_logger', return_value=audit_logger):

                # Call _calculate_scope_from_navigation()
                scope_result = QGDiscoveredElements._calculate_scope_from_navigation()

                # Assertions
                assert scope_result is not None, "Should detect navigation-based scope"
                assert scope_result["page_count"] == 2, "Should deduplicate to 2 unique pages"
                assert len(scope_result["pages"]) == 2, "Should have 2 unique PageInfo objects"

                # Verify no duplicate URLs
                urls = [p["url"] for p in scope_result["pages"]]
                assert len(urls) == len(set(urls)), "URLs should be unique (no duplicates)"

    def test_read_audit_log_entries(self):
        """
        Test _read_audit_log_entries() helper method.

        Verifies that audit log JSON is read and parsed correctly.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            audit_logger = AuditLogger(
                run_id="test_navigation_004",
                output_dir=tmpdir
            )

            # Create audit log with mixed entry types
            audit_file = Path(tmpdir) / "audit_log_test_navigation_004.json"
            audit_data = {
                "run_id": "test_navigation_004",
                "execution_mode": "mixed",
                "steps": [
                    {"step": 4, "type": "gate", "gate_name": "qg_test_scenarios", "result": "pass"},
                    {"step": 5, "type": "mcp_tool", "tool_name": "browser_navigate", "args": {"url": "https://example.com/page1"}},
                    {"step": 5, "type": "mcp_tool", "tool_name": "browser_click", "args": {"element": "button"}},
                    {"step": 5, "type": "mcp_tool", "tool_name": "browser_navigate", "args": {"url": "https://example.com/page2"}}
                ],
                "files_generated": []
            }

            with open(audit_file, 'w') as f:
                json.dump(audit_data, f)

            # Mock state manager
            state_manager = MagicMock(spec=StateManager)

            # Inject dependencies
            with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=state_manager), \
                 patch.object(QGDiscoveredElements, 'get_audit_logger', return_value=audit_logger):

                # Call _read_audit_log_entries()
                entries = QGDiscoveredElements._read_audit_log_entries()

                # Assertions
                assert entries is not None, "Should read audit log entries"
                assert len(entries) == 4, "Should read all 4 entries"
                assert entries[0]["type"] == "gate", "First entry is gate"
                assert entries[1]["tool_name"] == "browser_navigate", "Second entry is browser_navigate"

    def test_infer_page_name_from_url(self):
        """
        Test _infer_page_name_from_url() helper method.

        Verifies URL → PascalCase page name conversion.
        Note: Multi-segment paths combine last 2 segments for context.
        """
        test_cases = [
            ("https://parabank.parasoft.com/parabank/login.htm", "ParabankLoginPage"),  # parabank + login
            ("https://parabank.parasoft.com/parabank/transfer.htm", "ParabankTransferPage"),  # parabank + transfer
            ("https://example.com/accounts/overview", "AccountsOverviewPage"),  # accounts + overview
            ("https://example.com/checkout", "CheckoutPage"),  # Single segment
            ("https://example.com/", "HomePage"),  # Root path
        ]

        for url, expected_name in test_cases:
            page_name = QGDiscoveredElements._infer_page_name_from_url(url)
            assert page_name == expected_name, f"URL '{url}' should infer '{expected_name}', got '{page_name}'"


class TestNavigationTrackingIntegration:
    """Integration tests for navigation tracking in PRE validation."""

    def test_pre_validation_with_navigation_self_healing(self):
        """
        Integration test: PRE validation uses navigation-first, provides scope_result.

        Simplified scenario:
        - Step 4 complete (simple single-page BDD to avoid complexity)
        - Audit log has navigation calls (2 pages detected via navigation)
        - Manually call _calculate_scope_from_navigation() to verify it works
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create audit logger
            audit_logger = AuditLogger(
                run_id="test_navigation_integration",
                output_dir=tmpdir
            )

            # Audit log with navigation calls
            audit_file = Path(tmpdir) / "audit_log_test_navigation_integration.json"
            audit_data = {
                "run_id": "test_navigation_integration",
                "execution_mode": "mixed",
                "steps": [
                    {"step": 5, "type": "mcp_tool", "tool_name": "browser_navigate", "args": {"url": "https://parabank.parasoft.com/parabank/login.htm"}},
                    {"step": 5, "type": "mcp_tool", "tool_name": "browser_navigate", "args": {"url": "https://parabank.parasoft.com/parabank/transfer.htm"}}
                ],
                "files_generated": []
            }

            with open(audit_file, 'w') as f:
                json.dump(audit_data, f)

            # Mock state manager with simple BDD (single page)
            state_manager = MagicMock(spec=StateManager)
            state_manager.is_step_complete.side_effect = lambda step: step == 4
            state_manager.get_step.side_effect = lambda step: {
                4: {
                    "test_scenarios": [
                        {
                            "name": "User logs in",
                            "given": "A user on LoginPage",
                            "when": "User enters credentials",
                            "then": "User is logged in"
                        }
                    ]
                }
            }.get(step, None)

            # Inject dependencies
            with patch.object(QGDiscoveredElements, '_get_state_manager', return_value=state_manager), \
                 patch.object(QGDiscoveredElements, 'get_audit_logger', return_value=audit_logger):

                # Directly call _calculate_scope_from_navigation() to verify it works
                scope_result = QGDiscoveredElements._calculate_scope_from_navigation()

                # Assertions
                assert scope_result is not None, "Navigation tracking should detect pages"
                assert scope_result["page_count"] == 2, "Navigation detected 2 pages"
                assert len(scope_result["pages"]) == 2, "Should have 2 PageInfo objects"

                # Verify navigation-based detection
                page_names = [p["page_name"] for p in scope_result["pages"]]
                assert "ParabankLoginPage" in page_names
                assert "ParabankTransferPage" in page_names

                # Verify reason shows navigation source
                assert all(p.get("reason") == "navigation detected" for p in scope_result["pages"])

                # Verify navigation tracking works even when BDD shows single page
                # This proves navigation-first detection is independent of BDD
