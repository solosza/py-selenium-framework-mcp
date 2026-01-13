from interfaces.web_interface import WebInterface
from pages.parabank5.login_page import LoginPage
from pages.parabank5.transfer_funds_page import TransferFundsPage
from pages.parabank5.transfer_confirmation_page import TransferConfirmationPage
from resources.utilities import autologger


class ParabankTasks:
    """Task module for ParaBank domain operations."""

    def __init__(self, web: WebInterface):
        self.web = web
        self.login_page = LoginPage(web)
        self.transfer_funds_page = TransferFundsPage(web)
        self.transfer_confirmation_page = TransferConfirmationPage(web)

    @autologger.automation_logger("Task")
    def log_in(self, username: str, password: str) -> None:
        (self.login_page
            .navigate()
            .enter_username(username)
            .enter_password(password)
            .click_login())

    @autologger.automation_logger("Task")
    def transfer_funds(self, amount: str, from_account: str, to_account: str) -> None:
        (self.transfer_funds_page
            .navigate()
            .enter_amount(amount)
            .select_from_account(from_account)
            .select_to_account(to_account)
            .click_transfer())
