"""
Home Page - Main landing page object.

URL: http://www.automationpractice.pl/index.php
"""

from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from interfaces.web_interface import WebInterface


class HomePage(BasePage):
    """
    Page Object for the Home/Landing page.

    This page contains:
    - Header with navigation
    - Login/Logout links in header
    - Main content area
    - Footer
    """

    def __init__(self, web: WebInterface):
        """
        Initialize HomePage.

        Args:
            web: WebInterface instance
        """
        super().__init__(web)

    # ==================== LOCATORS ====================

    # Header navigation
    LOGO = (By.CSS_SELECTOR, ".logo.img-responsive")
    SEARCH_BOX = (By.ID, "search_query_top")
    CART_LINK = (By.CSS_SELECTOR, ".shopping_cart")

    # Authentication links (in header)
    LOGIN_LINK = (By.CSS_SELECTOR, ".login")
    LOGOUT_LINK = (By.CSS_SELECTOR, ".logout")
    ACCOUNT_LINK = (By.CSS_SELECTOR, ".account")

    # User account info (when logged in)
    USER_INFO = (By.CSS_SELECTOR, ".account span")

    # ==================== PAGE METHODS ====================

    def is_page_loaded(self) -> bool:
        """
        Verify home page is loaded.

        Returns:
            True if logo is visible
        """
        return self.web.is_element_displayed(*self.LOGO, timeout=5)

    # ==================== AUTHENTICATION LINKS ====================

    def is_login_link_visible(self) -> bool:
        """
        Check if login link is visible in header.

        Returns:
            True if login link is displayed (user not logged in)
        """
        return self.web.is_element_displayed(*self.LOGIN_LINK, timeout=3)

    def is_logout_link_visible(self) -> bool:
        """
        Check if logout link is visible in header.

        Returns:
            True if logout link is displayed (user logged in)
        """
        return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=3)

    def is_account_link_visible(self) -> bool:
        """
        Check if account link is visible in header.

        Returns:
            True if account link is displayed (user logged in)
        """
        return self.web.is_element_displayed(*self.ACCOUNT_LINK, timeout=3)

    def click_login_link(self):
        """
        Click the login link in header.

        Returns:
            self for method chaining
        """
        self.web.click(*self.LOGIN_LINK)
        return self

    def click_logout_link(self):
        """
        Click the logout link in header.

        Returns:
            self for method chaining
        """
        self.web.click(*self.LOGOUT_LINK)
        return self

    def click_account_link(self):
        """
        Click the account link in header.

        Returns:
            self for method chaining
        """
        self.web.click(*self.ACCOUNT_LINK)
        return self

    def get_logged_in_user_name(self) -> str:
        """
        Get the logged-in user's name displayed in header.

        Returns:
            User name text, or empty string if not logged in
        """
        if not self.is_account_link_visible():
            return ""

        try:
            return self.web.get_text(*self.USER_INFO)
        except Exception:
            return ""

    # ==================== NAVIGATION ====================

    def click_logo(self):
        """
        Click the site logo to return to home page.

        Returns:
            self for method chaining
        """
        self.web.click(*self.LOGO)
        return self

    def click_cart(self):
        """
        Click the shopping cart link.

        Returns:
            self for method chaining
        """
        self.web.click(*self.CART_LINK)
        return self

    # ==================== SEARCH ====================

    def search_for(self, search_term: str):
        """
        Enter search term and submit search.

        Args:
            search_term: Text to search for

        Returns:
            self for method chaining
        """
        from selenium.webdriver.common.keys import Keys
        self.web.type_text(*self.SEARCH_BOX, text=search_term)
        # Submit search by pressing Enter
        element = self.web.find_element(*self.SEARCH_BOX)
        element.send_keys(Keys.RETURN)
        return self

    def is_search_box_visible(self) -> bool:
        """
        Check if search box is visible.

        Returns:
            True if search box is displayed
        """
        return self.web.is_element_displayed(*self.SEARCH_BOX, timeout=3)
