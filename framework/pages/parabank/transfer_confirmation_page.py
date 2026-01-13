from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface
import re


class TransferConfirmationPage:
    """Page Object for ParaBank Transfer Confirmation page."""

    # LOCATORS
    TRANSFER_COMPLETE_HEADING = (By.CSS_SELECTOR, "h1.title")
    TRANSFER_MESSAGE = (By.CSS_SELECTOR, "#showResult p:first-of-type")

    def __init__(self, web: WebInterface):
        self.web = web

    def navigate(self) -> "TransferConfirmationPage":
        url = self.web.config["url"]
        self.web.navigate_to(f"{url}/transfer.htm")
        return self

    def is_transfer_confirmed(self) -> bool:
        if not self.web.is_element_displayed(*self.TRANSFER_COMPLETE_HEADING, timeout=5):
            return False
        heading_text = self.web.get_text(*self.TRANSFER_COMPLETE_HEADING)
        return "Transfer Complete" in heading_text

    def get_transfer_amount(self) -> str:
        message = self.web.get_text(*self.TRANSFER_MESSAGE)
        match = re.search(r'\$[\d,]+\.?\d*', message)
        return match.group(0) if match else ""
