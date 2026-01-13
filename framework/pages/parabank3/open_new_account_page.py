"""
OpenNewAccountPage - Page Object Model
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class OpenNewAccountPage:
    def __init__(self, web: WebInterface):
        self.web = web

    ACCOUNT_TYPE_DROPDOWN = (By.CSS_SELECTOR, "#type")
    FROM_ACCOUNT_DROPDOWN = (By.CSS_SELECTOR, "#fromAccountId")
    OPEN_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "input[type='submit'][value='Open New Account']")
    SUCCESS_HEADING = (By.CSS_SELECTOR, "#rightPanel h1")
    NEW_ACCOUNT_ID_LINK = (By.CSS_SELECTOR, "#newAccountId")

    def navigate(self) -> "OpenNewAccountPage":
        self.web.navigate_to(self.web.config['url'] + '/parabank/openaccount.htm')
        return self

    def select_account_type(self, account_type: str) -> "OpenNewAccountPage":
        self.web.select_dropdown_by_value(*self.ACCOUNT_TYPE_DROPDOWN, account_type)
        return self

    def select_from_account(self, account_id: str) -> "OpenNewAccountPage":
        self.web.select_dropdown_by_value(*self.FROM_ACCOUNT_DROPDOWN, account_id)
        return self

    def click_open_account(self) -> "OpenNewAccountPage":
        self.web.click(*self.OPEN_ACCOUNT_BUTTON)
        return self

    def is_account_opened(self) -> bool:
        try:
            heading_text = self.web.get_text(*self.SUCCESS_HEADING)
            return "Account Opened!" in heading_text
        except Exception:
            return False

    def get_new_account_id(self) -> str:
        return self.web.get_text(*self.NEW_ACCOUNT_ID_LINK)
