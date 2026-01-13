"""
OpenAccountPage - Page Object Model for ParaBank new account creation
"""
from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class OpenAccountPage:
    def __init__(self, web: WebInterface):
        self.web = web


    def navigate(self) -> "OpenAccountPage":
        """Navigate to OpenAccount page."""
        self.web.navigate_to(self.web.config['url'] + '/parabank/openaccount.htm')
        return self

    # Locators
    ACCOUNT_TYPE_SELECT = (By.ID, "type")
    FROM_ACCOUNT_SELECT = (By.ID, "fromAccountId")
    OPEN_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "input[value='Open New Account']")
    NEW_ACCOUNT_ID = (By.ID, "newAccountId")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "div.ng-scope p")
    ACCOUNT_DETAILS_TABLE = (By.ID, "accountTable")

    # Atomic methods (return self)
    def select_account_type(self, account_type: str) -> "OpenAccountPage":
        self.web.select_dropdown_by_visible_text(*self.ACCOUNT_TYPE_SELECT, account_type)
        return self

    def select_from_account(self, account_id: str) -> "OpenAccountPage":
        self.web.select_dropdown_by_value(*self.FROM_ACCOUNT_SELECT, account_id)
        return self

    def click_open_account(self) -> "OpenAccountPage":
        self.web.click(*self.OPEN_ACCOUNT_BUTTON)
        return self

    # State-check methods (for assertions)
    def is_account_created(self) -> bool:
        return self.web.is_element_displayed(*self.NEW_ACCOUNT_ID, timeout=5)

    def has_success_message(self) -> bool:
        return self.web.is_element_displayed(*self.SUCCESS_MESSAGE, timeout=5)
