"""
AuthTasks - Reusable workflow methods.

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.

Authentication workflows (login, logout)
"""

from typing import Optional
from interfaces.web_interface import WebInterface
from pages.auth.loginpage import LoginPage



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
