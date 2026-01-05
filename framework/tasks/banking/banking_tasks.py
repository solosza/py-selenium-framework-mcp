"""
BankingTasks - Task Module

Banking operations: register user, open savings account, transfer funds, view account activity.
Orchestrates page objects to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from pages.banking.registration_page import RegistrationPage
from pages.banking.open_new_account_page import OpenNewAccountPage
from pages.banking.transfer_funds_page import TransferFundsPage
from pages.banking.accounts_overview_page import AccountsOverviewPage


class BankingTasks:
    """
    Task module for Banking domain operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    def __init__(self, web: WebInterface):
        """
        Compose Page Objects - NO decorator on constructor.

        Args:
            web: WebInterface instance
        """
        self.web = web
        self.registration_page = RegistrationPage(web)
        self.open_new_account_page = OpenNewAccountPage(web)
        self.transfer_funds_page = TransferFundsPage(web)
        self.accounts_overview_page = AccountsOverviewPage(web)

    # ==================== TASK METHODS ====================

    @autologger.automation_logger("Task")
    def register_user(self, user_data: dict) -> None:
        """
        Register a new user account.

        Args:
            user_data: Dict with first_name, last_name, address, city, state,
                      zip_code, phone, ssn, username, password

        NO return value - test asserts via registration_page.is_registration_confirmed()
        """
        (self.registration_page
            .navigate()
            .enter_first_name(user_data["first_name"])
            .enter_last_name(user_data["last_name"])
            .enter_address(user_data["address"])
            .enter_city(user_data["city"])
            .enter_state(user_data["state"])
            .enter_zip_code(user_data["zip_code"])
            .enter_phone(user_data["phone"])
            .enter_ssn(user_data["ssn"])
            .enter_username(user_data["username"])
            .enter_password(user_data["password"])
            .enter_confirm_password(user_data["password"])
            .click_register())

    @autologger.automation_logger("Task")
    def open_savings_account(self) -> None:
        """
        Open a new savings account.

        NO return value - test asserts via open_new_account_page.is_account_created()
        """
        (self.open_new_account_page
            .navigate()
            .select_account_type("SAVINGS")
            .click_open_account())

    @autologger.automation_logger("Task")
    def transfer_funds(self, amount: str, from_account: str, to_account: str) -> None:
        """
        Transfer funds between accounts.

        Args:
            amount: Transfer amount as string
            from_account: Source account ID
            to_account: Destination account ID

        NO return value - test asserts via transfer_funds_page.is_transfer_confirmed()
        """
        (self.transfer_funds_page
            .navigate()
            .enter_amount(amount)
            .select_from_account(from_account)
            .select_to_account(to_account)
            .click_transfer())

    @autologger.automation_logger("Task")
    def view_account_activity(self, account_id: str) -> None:
        """
        View transaction history for an account.

        Args:
            account_id: Account ID to view activity for

        NO return value - test asserts via accounts_overview_page.has_transaction_in_history()
        """
        (self.accounts_overview_page
            .navigate()
            .click_account(account_id))
