"""Banking Tasks - Domain operations for ParaBank banking workflows."""
import uuid
import time
from framework.interfaces.web_interface import WebInterface
from framework.pages.test10.parabank_home_page import ParabankHomePage
from framework.pages.test10.registration_page import RegistrationPage
from framework.pages.test10.open_account_page import OpenAccountPage
from framework.pages.test10.transfer_funds_page import TransferFundsPage
from framework.resources.utilities import autologger


class BankingTasks:
    """Task module for ParaBank banking operations."""

    def __init__(self, web: WebInterface, base_url: str):
        self.web = web
        self.base_url = base_url
        # Compose page objects
        self.home_page = ParabankHomePage(web)
        self.registration_page = RegistrationPage(web)
        self.open_account_page = OpenAccountPage(web)
        self.transfer_funds_page = TransferFundsPage(web)
        # Store credentials for self-contained workflow
        self._username = None
        self._password = None
        self._new_account_id = None

    @autologger.automation_logger("Task")
    def register_new_user(self, user_data: dict) -> None:
        """
        Register a new user with the provided data.

        Args:
            user_data: Dictionary containing registration fields
                - first_name, last_name, address, city, state, zip_code
                - phone, ssn, username, password
        """
        # Generate unique username if not provided
        username = user_data.get("username", f"user_{uuid.uuid4().hex[:8]}")
        password = user_data.get("password", "TestPass123!")

        self.home_page.navigate(self.base_url)
        self.home_page.click_register()

        (self.registration_page
            .enter_first_name(user_data.get("first_name", "Test"))
            .enter_last_name(user_data.get("last_name", "User"))
            .enter_address(user_data.get("address", "123 Main St"))
            .enter_city(user_data.get("city", "Springfield"))
            .enter_state(user_data.get("state", "IL"))
            .enter_zip_code(user_data.get("zip_code", "62701"))
            .enter_phone(user_data.get("phone", "555-123-4567"))
            .enter_ssn(user_data.get("ssn", "123-45-6789"))
            .enter_username(username)
            .enter_password(password)
            .enter_confirm_password(password)
            .click_register())

        # Store credentials for later use
        self._username = username
        self._password = password

    @autologger.automation_logger("Task")
    def login(self, username: str = None, password: str = None) -> None:
        """
        Log in with credentials.

        Args:
            username: Username (uses stored if not provided)
            password: Password (uses stored if not provided)
        """
        use_username = username or self._username
        use_password = password or self._password

        self.home_page.navigate(self.base_url)
        (self.home_page
            .enter_username(use_username)
            .enter_password(use_password)
            .click_login())

    @autologger.automation_logger("Task")
    def open_checking_account(self) -> None:
        """Open a new checking account."""
        self.open_account_page.click_open_new_account_link()

        # Wait for form to load
        time.sleep(1)

        (self.open_account_page
            .select_account_type("CHECKING")
            .click_open_account())

        # Wait for result to load
        time.sleep(1)

        # Store new account ID for later use
        if self.open_account_page.has_new_account_number():
            self._new_account_id = self.open_account_page.get_new_account_id()

    @autologger.automation_logger("Task")
    def transfer_funds(self, amount: str, from_account: str = None, to_account: str = None) -> None:
        """
        Transfer funds between accounts.

        Args:
            amount: Amount to transfer
            from_account: Source account ID (optional)
            to_account: Destination account ID (uses new account if not provided)
        """
        self.transfer_funds_page.click_transfer_funds_link()

        # Wait for dropdowns to populate via AJAX
        time.sleep(1)

        self.transfer_funds_page.enter_amount(amount)

        if from_account:
            self.transfer_funds_page.select_from_account(from_account)

        if to_account:
            self.transfer_funds_page.select_to_account(to_account)
        elif self._new_account_id:
            self.transfer_funds_page.select_to_account(self._new_account_id)

        self.transfer_funds_page.click_transfer()

        # Wait for transfer result to load
        time.sleep(1)

    def get_stored_username(self) -> str:
        """Get the stored username from registration."""
        return self._username

    def get_stored_password(self) -> str:
        """Get the stored password from registration."""
        return self._password

    def get_new_account_id(self) -> str:
        """Get the new account ID from account opening."""
        return self._new_account_id
