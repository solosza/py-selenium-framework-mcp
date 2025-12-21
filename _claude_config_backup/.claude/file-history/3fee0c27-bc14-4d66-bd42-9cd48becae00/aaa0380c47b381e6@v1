"""
Test Guest User Browses T-shirts Category

Scenario: Guest user browses T-shirts category
Given I am a guest user on the homepage
When I navigate to the T-shirts category
Then I should see T-shirt products displayed
"""

import pytest
from resources.utilities import autologger
from roles.auth.guest_user import GuestUser
from pages.catalog.product_list_page import ProductListPage


class TestGuestUserBrowsesTshirtsCategory:
    """Test suite for guest user browsing T-shirts category."""

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config
        self.base_url = config.get("url", config.get("base_url", ""))
        self.product_list_page = ProductListPage(self.web)

    @pytest.mark.catalog
    @autologger.automation_logger("Test")
    def test_guest_user_browses_tshirts_category(self):
        """
        Test that a guest user can browse T-shirts category and see products.

        Given I am a guest user on the homepage
        When I navigate to the T-shirts category
        Then I should see T-shirt products displayed
        """
        # Arrange
        guest = GuestUser(self.web, self.base_url)

        # Act - ONE workflow call
        guest.browse_tshirts_category()

        # Assert - Via POM state-check methods
        assert self.product_list_page.has_products(), "T-shirt products should be displayed"
        assert self.product_list_page.get_product_count() > 0, "Should have at least one product"
