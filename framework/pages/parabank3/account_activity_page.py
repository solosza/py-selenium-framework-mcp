"""
AccountActivityPage - Page Object Model
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class AccountActivityPage:
    def __init__(self, web: WebInterface):
        self.web = web

    ACTIVITY_PERIOD_DROPDOWN = (By.CSS_SELECTOR, "#month")
    TRANSACTION_TYPE_DROPDOWN = (By.CSS_SELECTOR, "#transactionType")
    GO_BUTTON = (By.CSS_SELECTOR, "input[type='submit'][value='Go']")
    ACCOUNT_NUMBER = (By.CSS_SELECTOR, "#accountId")
    ACCOUNT_TYPE = (By.CSS_SELECTOR, "#accountType")
    BALANCE = (By.CSS_SELECTOR, "#balance")
    TRANSACTION_TABLE = (By.CSS_SELECTOR, "#transactionTable")
    TRANSACTION_AMOUNT = (By.CSS_SELECTOR, "#transactionTable tbody tr td:nth-child(4)")

    def navigate(self) -> "AccountActivityPage":
        self.web.navigate_to(self.web.config['url'] + '/parabank/overview.htm')
        return self

    def select_activity_period(self, period: str) -> "AccountActivityPage":
        self.web.select_dropdown_by_value(*self.ACTIVITY_PERIOD_DROPDOWN, period)
        return self

    def select_transaction_type(self, transaction_type: str) -> "AccountActivityPage":
        self.web.select_dropdown_by_value(*self.TRANSACTION_TYPE_DROPDOWN, transaction_type)
        return self

    def click_go(self) -> "AccountActivityPage":
        self.web.click(*self.GO_BUTTON)
        return self

    def is_transaction_visible(self) -> bool:
        try:
            return self.web.is_element_displayed(*self.TRANSACTION_TABLE, timeout=5)
        except Exception:
            return False

    def has_correct_amount(self, expected_amount: str) -> bool:
        try:
            amount_text = self.web.get_text(*self.TRANSACTION_AMOUNT)
            return expected_amount in amount_text
        except Exception:
            return False

    def get_account_number(self) -> str:
        return self.web.get_text(*self.ACCOUNT_NUMBER)

    def get_account_type(self) -> str:
        return self.web.get_text(*self.ACCOUNT_TYPE)

    def get_balance(self) -> str:
        return self.web.get_text(*self.BALANCE)
