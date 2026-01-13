"""
Handle ParaBank account registration, opening accounts, transfers, and transaction viewing

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.parabank2.parabank_registration_page import ParabankRegistrationPage


class Parabank2Tasks:
    """
    Task module for General operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    def __init__(self, web: WebInterface, base_url: str):
        """
        Compose Page Objects - NO decorator on constructor.

        Args:
            web: WebInterface instance
            base_url: Application base URL
        """
        self.web = web
        self.base_url = base_url
        self.parabank_registration_page = ParabankRegistrationPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def submit_form(self) -> None:
        """
        Fill and submit the form.

        NO return value - test asserts via POM state-check methods.
        """
        (self.parabank_registration_page
            .enter_first_name()
            .enter_last_name()
            .enter_address()
            .enter_city()
            .enter_state()
            .enter_zip_code()
            .enter_phone()
            .enter_ssn()
            .enter_username()
            .enter_password()
            .enter_confirm_password()
            .click_register_btn())
        # NO return - test asserts via POM
