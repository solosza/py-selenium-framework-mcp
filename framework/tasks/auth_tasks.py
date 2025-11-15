"""
AuthTasks - Reusable workflow methods.

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.

TODO: Add workflow description
"""

from typing import Optional
from framework.interfaces.web_interface import WebInterface
from framework.pages.common.login_page import LoginPage



class AuthTasks:
    """AuthTasks workflows."""

    def __init__(self, web: WebInterface, base_url: str):
        """
        Initialize AuthTasks.

        Args:
            web: WebInterface instance
            base_url: Application base URL
        """
        self.web = web
        self.base_url = base_url

        self.login_page = LoginPage(web)


    # ==================== WORKFLOW METHODS ====================

    def login(self, email: str, password: str) -> bool:
        """
        Execute login workflow.

        Complete workflow:
        1. Navigate to login page
        2. Enter email and password
        3. Click submit button
        4. Verify login success

        Args:
            email: User email address
            password: User password

        Returns:
            True if login successful, False otherwise
        """
        # Navigate to authentication page
        self.web.navigate(f"{self.base_url}/index.php?controller=authentication")

        # Enter credentials
        self.login_page.enter_email(email)
        self.login_page.enter_passwd(password)

        # Submit login
        self.login_page.click_submitlogin()

        # Verify login success (check for account menu or logout link)
        from selenium.webdriver.common.by import By
        return self.web.is_element_visible(By.CSS_SELECTOR, ".account, .logout")

    def logout(self) -> bool:
        """
        Execute logout workflow.

        Complete workflow:
        1. Click logout link
        2. Verify logout success

        Returns:
            True if logout successful, False otherwise
        """
        from selenium.webdriver.common.by import By

        # Click logout if visible
        if self.web.is_element_visible(By.CSS_SELECTOR, ".logout"):
            self.web.click(By.CSS_SELECTOR, ".logout")

        # Verify logout (login link should be visible)
        return self.web.is_element_visible(By.CSS_SELECTOR, ".login")
