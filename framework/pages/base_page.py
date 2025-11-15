"""
Base Page - Parent class for all page objects.

Contains common elements (header, footer) and shared methods that all pages inherit.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class BasePage:
    """
    Base Page Object that all page objects inherit from.

    Provides:
    - Common header navigation elements (sign in, logout, my account)
    - Common footer elements (if needed)
    - Shared utility methods
    """

    def __init__(self, web: WebInterface):
        """
        Initialize BasePage.

        Args:
            web: WebInterface instance
        """
        self.web = web

    # ==================== HEADER NAVIGATION LOCATORS ====================

    # Authentication links
    SIGN_IN_LINK = (By.CSS_SELECTOR, ".login")
    LOGOUT_LINK = (By.CSS_SELECTOR, ".logout")
    MY_ACCOUNT_LINK = (By.CSS_SELECTOR, ".account")

    # Shopping cart
    SHOPPING_CART_LINK = (By.CSS_SELECTOR, ".shopping_cart")

    # Logo
    SITE_LOGO = (By.CSS_SELECTOR, ".logo")

    # Search
    SEARCH_INPUT = (By.ID, "search_query_top")
    SEARCH_BUTTON = (By.NAME, "submit_search")

    # Contact
    CONTACT_US_LINK = (By.CSS_SELECTOR, "[title='Contact Us']")

    # ==================== HEADER NAVIGATION METHODS ====================

    def click_sign_in(self) -> None:
        """Click Sign In link in header."""
        self.web.click(*self.SIGN_IN_LINK)

    def click_logout(self) -> None:
        """Click Logout link in header."""
        self.web.click(*self.LOGOUT_LINK)

    def click_my_account(self) -> None:
        """Click My Account link in header."""
        self.web.click(*self.MY_ACCOUNT_LINK)

    def click_shopping_cart(self) -> None:
        """Click Shopping Cart link in header."""
        self.web.click(*self.SHOPPING_CART_LINK)

    def click_logo(self) -> None:
        """Click site logo to return to homepage."""
        self.web.click(*self.SITE_LOGO)

    def click_contact_us(self) -> None:
        """Click Contact Us link in header."""
        self.web.click(*self.CONTACT_US_LINK)

    # ==================== SEARCH METHODS ====================

    def enter_search_query(self, query: str) -> None:
        """
        Enter search query in search box.

        Args:
            query: Search term
        """
        self.web.type_text(*self.SEARCH_INPUT, text=query)

    def click_search_button(self) -> None:
        """Click search submit button."""
        self.web.click(*self.SEARCH_BUTTON)

    def search(self, query: str) -> None:
        """
        Perform search.

        Args:
            query: Search term
        """
        self.enter_search_query(query)
        self.click_search_button()

    # ==================== HEADER STATE VERIFICATION ====================

    def is_signed_in(self) -> bool:
        """
        Check if user is signed in.

        Returns:
            True if logout link is visible (user is logged in)
        """
        return self.web.element_exists(*self.LOGOUT_LINK, timeout=3)

    def is_signed_out(self) -> bool:
        """
        Check if user is signed out.

        Returns:
            True if sign in link is visible (user is logged out)
        """
        return self.web.element_exists(*self.SIGN_IN_LINK, timeout=3)

    def is_my_account_visible(self) -> bool:
        """
        Check if My Account link is visible.

        Returns:
            True if my account link is present
        """
        return self.web.element_exists(*self.MY_ACCOUNT_LINK, timeout=3)

    def wait_for_sign_in_link_visible(self, timeout: int = 10) -> None:
        """
        Wait for sign in link to become visible.

        Args:
            timeout: Maximum time to wait in seconds

        Raises:
            TimeoutException: If sign in link not visible within timeout
        """
        self.web.wait_for_element_visible(*self.SIGN_IN_LINK, timeout=timeout)

    # ==================== COMMON UTILITY METHODS ====================

    def get_page_url(self) -> str:
        """
        Get current page URL.

        Returns:
            Current URL
        """
        return self.web.get_current_url()

    def get_page_title(self) -> str:
        """
        Get current page title.

        Returns:
            Page title
        """
        return self.web.get_page_title()

    def refresh_page(self) -> None:
        """Refresh the current page."""
        self.web.refresh_page()

    def take_screenshot(self, name: str) -> str:
        """
        Take screenshot of current page.

        Args:
            name: Screenshot name

        Returns:
            Path to saved screenshot
        """
        return self.web.take_screenshot(name)

    def scroll_to_top(self) -> None:
        """Scroll to top of page."""
        self.web.scroll_to_top()

    def scroll_to_bottom(self) -> None:
        """Scroll to bottom of page."""
        self.web.scroll_to_bottom()
