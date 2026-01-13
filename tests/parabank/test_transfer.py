
import pytest
from framework.roles.parabank.registered_user import RegisteredUser
from framework.pages.parabank.account_overview_page import AccountOverviewPage
from framework.resources.utilities import autologger

@pytest.mark.parabank
@autologger.automation_logger("Test")
def test_transfer_between_accounts(web_interface, config, test_users):
    """Test that a registered user can transfer money between accounts."""
    # Arrange
    user = RegisteredUser(web_interface, test_users["registered_user"], config["url"])
    overview_page = AccountOverviewPage(web_interface)

    # Act - Transfer from account 12345 to account 67890 (DIFFERENT accounts - valid!)
    user.transfer_funds(
        from_account="12345",
        to_account="67890",  # Different account - no contradiction
        amount="100.00"
    )

    # Assert
    assert overview_page.is_transfer_complete(), "Transfer should complete"
