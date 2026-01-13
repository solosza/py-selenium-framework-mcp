import pytest
from typing import Dict, Any
from roles.registered_user import RegisteredUser
from pages.parabank.transfer_confirmation_page import TransferConfirmationPage
from resources.utilities import autologger


class TestTransferFunds:
    """Test suite for ParaBank fund transfer scenarios."""

    @pytest.mark.parabank
    @pytest.mark.smoke
    @autologger.automation_logger("Test")
    def test_transfer_funds_between_accounts(
        self,
        web_interface,
        config: Dict[str, Any]
    ) -> None:
        """
        Verify that a registered user can transfer funds between accounts.
        """
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
            to_account="15564"
        )

        # ASSERT
        assert confirmation_page.is_transfer_confirmed(), "Transfer should be confirmed"
        assert confirmation_page.get_transfer_amount() == "$100.00", "Transfer amount should match"
