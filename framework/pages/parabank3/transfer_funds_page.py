"""
TransferFundsPage - Page Object Model
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class TransferFundsPage:
    def __init__(self, web: WebInterface):
        self.web = web

    AMOUNT_TEXTBOX = (By.CSS_SELECTOR, "#amount")
    FROM_ACCOUNT_DROPDOWN = (By.CSS_SELECTOR, "#fromAccountId")
    TO_ACCOUNT_DROPDOWN = (By.CSS_SELECTOR, "#toAccountId")
    TRANSFER_BUTTON = (By.CSS_SELECTOR, "input[type='submit'][value='Transfer']")
    SUCCESS_HEADING = (By.CSS_SELECTOR, "#rightPanel h1")
    CONFIRMATION_MESSAGE = (By.CSS_SELECTOR, "#rightPanel p")

    def navigate(self) -> "TransferFundsPage":
        self.web.navigate_to(self.web.config['url'] + '/parabank/transfer.htm')
        return self

    def enter_amount(self, amount: str) -> "TransferFundsPage":
        self.web.type_text(*self.AMOUNT_TEXTBOX, amount)
        return self

    def select_from_account(self, account_id: str) -> "TransferFundsPage":
        self.web.select_dropdown_by_value(*self.FROM_ACCOUNT_DROPDOWN, account_id)
        return self

    def select_to_account(self, account_id: str) -> "TransferFundsPage":
        self.web.select_dropdown_by_value(*self.TO_ACCOUNT_DROPDOWN, account_id)
        return self

    def click_transfer(self) -> "TransferFundsPage":
        self.web.click(*self.TRANSFER_BUTTON)
        return self

    def is_transfer_complete(self) -> bool:
        try:
            heading_text = self.web.get_text(*self.SUCCESS_HEADING)
            return "Transfer Complete!" in heading_text
        except Exception:
            return False

    def get_confirmation_message(self) -> str:
        return self.web.get_text(*self.CONFIRMATION_MESSAGE)
