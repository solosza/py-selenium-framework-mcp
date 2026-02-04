"""
Integration tests for semantic validation with parabank5 scenarios.

These tests verify the full workflow:
1. AI generates code with semantic violations
2. Gate detects violation and returns NEEDS_RETRY
3. Fix guidance is provided (pattern_template or fix_applied)

Scenarios based on actual parabank5 issues discovered in production.
"""

import pytest
from unittest.mock import MagicMock, patch
from tools.gates.qg_test_runner import QGTestRunner
from tools.gates.qg_role import QGRole
from utils.state_manager import StateManager


class TestParabank5SameAccountTransfer:
    """
    Integration test for FR-14.1: Parameter Contradiction Rule

    Scenario: parabank5 test_transfer_funds has from_account == to_account
    Expected: qg_test_runner POST validation catches contradiction
    """

    def test_gate_catches_same_account_transfer(self):
        """Test qg_test_runner catches from_account == to_account in parabank5 test."""
        # ARRANGE: Reproduce actual parabank5 test code with semantic violation
        test_code = '''
import pytest
from typing import Dict, Any
from roles.parabank5.registered_user import RegisteredUser
from pages.parabank5.transfer_confirmation_page import TransferConfirmationPage
from resources.utilities import autologger


class TestTransferFunds:
    @pytest.mark.parabank
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_transfer_funds_between_accounts(
        self,
        web_interface,
        config: Dict[str, Any]
    ) -> None:
        # ARRANGE
        user_data = {
            "username": "testuser20260108",
            "password": "Test123!"
        }
        user = RegisteredUser(
            web=web_interface,
            user_data=user_data
        )
        confirmation_page = TransferConfirmationPage(web_interface)

        # ACT
        user.transfer_funds_between_accounts(
            amount="100",
            from_account="15564",
            to_account="15564"  # SEMANTIC VIOLATION: same account!
        )

        # ASSERT
        assert confirmation_page.is_transfer_confirmed(), "Transfer should be confirmed"
        assert confirmation_page.get_transfer_amount() == "$100.00", "Transfer amount should match"
'''

        input_data = {
            "mode": "POST",
            "test_name": "test_transfer_funds_between_accounts",
            "workflow": "parabank5",
            "role": "RegisteredUser",
            "code": test_code,  # Fixed: use "code" not "test_code"
            "pom_metadata": {"class_name": "TransferConfirmationPage"},
            "role_metadata": {"class_name": "RegisteredUser"},
        }

        # Mock state manager (no Step 1 config needed for FR-14.1)
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.return_value = None

        with patch.object(QGTestRunner, '_get_state_manager', return_value=state_manager):
            # ACT
            result = QGTestRunner.validate_post(input_data)

        # ASSERT
        assert result["status"] == "NEEDS_RETRY", f"Gate should catch semantic violation, got: {result}"
        # Error should mention both parameters and the conflicting value
        error_lower = result["error"].lower()
        assert "from_account" in error_lower, f"Should mention from_account in: {result['error']}"
        assert "to_account" in error_lower, f"Should mention to_account in: {result['error']}"
        assert "15564" in result["error"], f"Should show the conflicting value in: {result['error']}"

        # Verify fix guidance provided (various forms)
        has_guidance = ("fix_hint" in result or "pattern_template" in result or
                       "fix_applied" in result or "message" in result)
        assert has_guidance, f"Should provide fix guidance in: {result}"


class TestParabank5CredentialStrategy:
    """
    Integration test for FR-14.2: Credential Strategy Rule

    Scenario: Step 1 says static, but Role uses self-contained pattern
    Expected: qg_role POST validation catches strategy mismatch
    """

    def test_gate_catches_credential_strategy_mismatch(self):
        """Test qg_role catches credential strategy mismatch for parabank5."""
        # ARRANGE: Role code using self-contained pattern when static was configured
        role_code = '''
from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.parabank5.parabank_tasks import ParaBankTasks
from resources.utilities import autologger


class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web: WebInterface):
        self.web = web
        # Self-contained: credentials hardcoded in __init__ (WRONG for static strategy!)
        self.username = "testuser20260108"
        self.password = "Test123!"
        self.parabank_tasks = ParaBankTasks(web)

    @autologger.automation_logger("Role")
    def transfer_funds_between_accounts(self, amount: str, from_account: str, to_account: str):
        self.parabank_tasks.login(self.username, self.password)
        self.parabank_tasks.transfer_funds(amount, from_account, to_account)
'''

        input_data = {
            "mode": "POST",
            "role_name": "RegisteredUser",
            "workflow": "parabank5",
            "code": role_code,
            "task_metadata": {
                "class_name": "ParaBankTasks",
                "import_path": "tasks.parabank5.parabank_tasks",
                "task_methods": ["login", "transfer_funds"]
            },
        }

        # Mock state manager: Step 1 configured static strategy
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.side_effect = lambda step: {
            1: {"credential_strategy": "static", "test_data_location": "shared"}
        }.get(step, None)

        with patch.object(QGRole, '_get_state_manager', return_value=state_manager):
            # ACT
            result = QGRole.validate_post(input_data)

        # ASSERT
        assert result["status"] == "NEEDS_RETRY", \
            f"Gate should catch strategy mismatch, got status={result.get('status')}, error={result.get('error')}"
        error_lower = result["error"].lower()
        assert "credential" in error_lower or "strategy" in error_lower, \
            f"Error should identify strategy issue in: {result['error']}"
        assert "static" in error_lower or "user_data" in error_lower, \
            f"Should mention expected strategy in: {result['error']}"

        # Verify pattern_template provided
        assert "pattern_template" in result or "fix_hint" in result, \
            f"Should provide fix guidance in: {result}"


class TestParabank5TestDataLocation:
    """
    Integration test for FR-14.3: Test Data Location Rule

    Scenario: Step 1 says workflow-specific, but test imports from shared
    Expected: qg_test_runner POST validation catches location mismatch
    """

    def test_gate_catches_test_data_location_mismatch(self):
        """Test qg_test_runner catches test data location mismatch."""
        # ARRANGE: Test code importing from shared when workflow-specific was configured
        test_code = '''
import pytest
from typing import Dict, Any
from roles.parabank5.registered_user import RegisteredUser
from pages.parabank5.transfer_confirmation_page import TransferConfirmationPage
from tests.data import transfer_data  # WRONG: importing from shared
from resources.utilities import autologger


class TestTransferFunds:
    @pytest.mark.parabank
    @autologger.automation_logger("Test")
    def test_transfer_funds_between_accounts(
        self,
        web_interface,
        config: Dict[str, Any]
    ) -> None:
        # ARRANGE
        user = RegisteredUser(web_interface, transfer_data["user"])
        confirmation_page = TransferConfirmationPage(web_interface)

        # ACT
        user.transfer_funds_between_accounts(**transfer_data["transfer"])

        # ASSERT
        assert confirmation_page.is_transfer_confirmed()
'''

        input_data = {
            "mode": "POST",
            "test_name": "test_transfer_funds_between_accounts",
            "workflow": "parabank5",
            "role": "RegisteredUser",
            "code": test_code,  # Fixed: use "code" not "test_code"
            "pom_metadata": {"class_name": "TransferConfirmationPage"},
            "role_metadata": {"class_name": "RegisteredUser"},
        }

        # Mock state manager: Step 1 configured workflow-specific location
        state_manager = MagicMock(spec=StateManager)
        state_manager.get_step.side_effect = lambda step: {
            1: {"credential_strategy": "none", "test_data_location": "workflow"}
        }.get(step, None)

        with patch.object(QGTestRunner, '_get_state_manager', return_value=state_manager):
            # ACT
            result = QGTestRunner.validate_post(input_data)

        # ASSERT
        assert result["status"] == "NEEDS_RETRY", \
            f"Gate should catch location mismatch, got status={result.get('status')}, error={result.get('error')}"
        error_lower = result["error"].lower()
        assert "test data" in error_lower or "import" in error_lower or "location" in error_lower, \
            f"Error should identify import location issue in: {result['error']}"
        assert "workflow" in error_lower or "parabank5" in error_lower, \
            f"Should mention expected workflow-specific location in: {result['error']}"

        # Verify fix guidance provided (various forms)
        has_guidance = ("fix_hint" in result or "pattern_template" in result or
                       "fix_applied" in result or "message" in result)
        assert has_guidance, f"Should provide fix guidance in: {result}"

        # If pattern provided, should show correct import path
        if "pattern_template" in result:
            assert "parabank5" in result["pattern_template"], \
                f"Template should show workflow-specific import path in: {result['pattern_template']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
