"""ParaBank Open New Account Page."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from framework.interfaces.web_interface import WebInterface


class OpenAccountPage:
    """Page object for ParaBank open new account form."""

    # Locators - Input elements
    ACCOUNT_TYPE_SELECT = (By.ID, "type")
    FROM_ACCOUNT_SELECT = (By.ID, "fromAccountId")
    OPEN_ACCOUNT_BUTTON = (By.CSS_SELECTOR, "input[value='Open New Account']")

    # Locators - Output elements (result shown in #openAccountResult div)
    ACCOUNT_OPENED_HEADING = (By.CSS_SELECTOR, "#openAccountResult h1")
    SUCCESS_MESSAGE = (By.CSS_SELECTOR, "#openAccountResult p")
    NEW_ACCOUNT_ID_LINK = (By.ID, "newAccountId")

    # Navigation link - specifically in the left panel account services menu
    OPEN_NEW_ACCOUNT_LINK = (By.XPATH, "//div[@id='leftPanel']//a[contains(@href,'openaccount.htm')]")

    def __init__(self, web: WebInterface):
        self.web = web

    def navigate(self, base_url: str) -> "OpenAccountPage":
        """Navigate to the open account page."""
        self.web.navigate_to(f"{base_url}/parabank/openaccount.htm")
        return self

    def click_open_new_account_link(self) -> "OpenAccountPage":
        """Click the Open New Account link from account services menu."""
        self.web.click(*self.OPEN_NEW_ACCOUNT_LINK)
        return self

    # Atomic action methods - return self for chaining
    def select_account_type(self, account_type: str) -> "OpenAccountPage":
        """Select account type (CHECKING or SAVINGS)."""
        element = self.web.find_element(*self.ACCOUNT_TYPE_SELECT)
        select = Select(element)
        select.select_by_visible_text(account_type)
        return self

    def select_from_account(self, account_id: str) -> "OpenAccountPage":
        """Select the account to fund from."""
        element = self.web.find_element(*self.FROM_ACCOUNT_SELECT)
        select = Select(element)
        select.select_by_visible_text(account_id)
        return self

    def click_open_account(self) -> "OpenAccountPage":
        """Click the Open New Account button."""
        self.web.click(*self.OPEN_ACCOUNT_BUTTON)
        return self

    # State-check methods for assertions
    def is_account_opened(self) -> bool:
        """Check if account was opened successfully."""
        return self.web.is_element_displayed(*self.ACCOUNT_OPENED_HEADING, timeout=10)

    def get_account_opened_heading(self) -> str:
        """Get the account opened heading text."""
        return self.web.get_text(*self.ACCOUNT_OPENED_HEADING)

    def is_success_message_displayed(self) -> bool:
        """Check if success message is displayed."""
        return self.web.is_element_displayed(*self.SUCCESS_MESSAGE, timeout=5)

    def get_new_account_id(self) -> str:
        """Get the new account ID."""
        return self.web.get_text(*self.NEW_ACCOUNT_ID_LINK)

    def has_new_account_number(self) -> bool:
        """Check if new account number is displayed."""
        return self.web.is_element_displayed(*self.NEW_ACCOUNT_ID_LINK, timeout=5)
