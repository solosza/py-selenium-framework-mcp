from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class TransferFundsPage:
    """Page Object for ParaBank transfer funds page."""

    # LOCATORS
    AMOUNT_INPUT = (By.CSS_SELECTOR, "#amount")
    FROM_ACCOUNT_SELECT = (By.CSS_SELECTOR, "#fromAccountId")
    TO_ACCOUNT_SELECT = (By.CSS_SELECTOR, "#toAccountId")
    TRANSFER_BTN = (By.CSS_SELECTOR, "input.button[value='Transfer']")
    PAGE_TITLE = (By.CSS_SELECTOR, "h1.title")

    def __init__(self, web: WebInterface):
        self.web = web

    def navigate(self) -> "TransferFundsPage":
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/transfer.htm")
        return self

    def enter_amount(self, text: str) -> "TransferFundsPage":
        self.web.type_text(*self.AMOUNT_INPUT, text)
        return self

    def select_from_account(self, account_id: str) -> "TransferFundsPage":
        self.web.select_dropdown_by_value(*self.FROM_ACCOUNT_SELECT, account_id)
        return self

    def select_to_account(self, account_id: str) -> "TransferFundsPage":
        self.web.select_dropdown_by_value(*self.TO_ACCOUNT_SELECT, account_id)
        return self

    def click_transfer(self) -> "TransferFundsPage":
        self.web.click(*self.TRANSFER_BTN)
        return self

    def is_page_loaded(self) -> bool:
        return self.web.is_element_displayed(*self.PAGE_TITLE, timeout=5)
