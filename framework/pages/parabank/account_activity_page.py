"""
AccountActivityPage - Page Object Model for ParaBank account activity/transaction history
"""
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class AccountActivityPage:
    def __init__(self, web: WebInterface):
        self.web = web


    def navigate(self) -> "AccountActivityPage":
        """Navigate to AccountActivity page."""
        self.web.navigate_to(self.web.config['url'] + '/parabank/activity.htm')
        return self

    # Locators
    ACCOUNT_SELECT = (By.ID, "accountId")
    ACTIVITY_PERIOD_SELECT = (By.ID, "month")
    TRANSACTION_TYPE_SELECT = (By.ID, "transactionType")
    GO_BUTTON = (By.CSS_SELECTOR, "input[value='Go']")
    TRANSACTION_TABLE = (By.ID, "transactionTable")
    TRANSACTION_DETAILS = (By.CSS_SELECTOR, "table#transactionTable tbody tr")

    # Atomic methods (return self)
    def select_account(self, account_id: str) -> "AccountActivityPage":
        self.web.select_dropdown_by_value(*self.ACCOUNT_SELECT, account_id)
        return self

    def select_activity_period(self, period: str) -> "AccountActivityPage":
        self.web.select_dropdown_by_visible_text(*self.ACTIVITY_PERIOD_SELECT, period)
        return self

    def click_go(self) -> "AccountActivityPage":
        self.web.click(*self.GO_BUTTON)
        return self

    # State-check methods (for assertions)
    def is_transaction_visible(self) -> bool:
        return self.web.is_element_displayed(*self.TRANSACTION_TABLE, timeout=5)

    def has_recent_transaction(self) -> bool:
        return self.web.is_element_displayed(*self.TRANSACTION_DETAILS, timeout=5)

    def get_transaction_amount(self) -> str:
        elements = self.web.find_elements(*self.TRANSACTION_DETAILS)
        if elements:
            return elements[0].text
        return ""
