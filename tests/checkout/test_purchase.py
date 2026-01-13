"""Complex workflow test."""
import pytest
from resources.utilities import autologger
from roles.registered_user import RegisteredUser
from pages.checkout.confirmation_page import ConfirmationPage


class TestPurchaseFlow:
    @pytest.mark.checkout
    @autologger.automation_logger("Test")
    def test_complete_purchase(self):
        """Test complete purchase flow."""
        # Arrange
        user = RegisteredUser(self.web, user_data, self.base_url)

        # Act - Multiple method calls allowed
        user.login()
        user.add_to_cart(product)
        user.checkout()

        # Assert
        assert self.confirmation_page.is_order_confirmed()
