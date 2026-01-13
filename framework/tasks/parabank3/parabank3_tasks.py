"""
Parabank3Tasks - Task module for parabank3 workflow
"""

from interfaces.web_interface import WebInterface
from pages.parabank3.open_new_account_page import OpenNewAccountPage
from pages.parabank3.transfer_funds_page import TransferFundsPage
from pages.parabank3.account_activity_page import AccountActivityPage
from resources.utilities import autologger


class Parabank3Tasks:
    def __init__(self, web: WebInterface):
        self.web = web
        self.open_new_account_page = OpenNewAccountPage(web)
        self.transfer_funds_page = TransferFundsPage(web)
        self.account_activity_page = AccountActivityPage(web)

    @autologger.automation_logger("Task")
    def open_new_account(self, account_type: str, from_account_id: str) -> None:
        (self.open_new_account_page
            .navigate()
            .select_account_type(account_type)
            .select_from_account(from_account_id)
            .click_open_account())

    @autologger.automation_logger("Task")
    def transfer_funds(self, amount: str, from_account_id: str, to_account_id: str) -> None:
        (self.transfer_funds_page
            .navigate()
            .enter_amount(amount)
            .select_from_account(from_account_id)
            .select_to_account(to_account_id)
            .click_transfer())

    @autologger.automation_logger("Task")
    def navigate_to_account_activity(self) -> None:
        self.account_activity_page.navigate()
