"""ParaBank Transfer Funds Page."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from framework.interfaces.web_interface import WebInterface


class TransferFundsPage:
    """Page object for ParaBank transfer funds form."""

    # Locators - Input elements
    AMOUNT_INPUT = (By.ID, "amount")
    FROM_ACCOUNT_SELECT = (By.ID, "fromAccountId")
    TO_ACCOUNT_SELECT = (By.ID, "toAccountId")
    TRANSFER_BUTTON = (By.CSS_SELECTOR, "input[value='Transfer']")

    # Locators - Output elements (result shown in #showResult div)
    TRANSFER_COMPLETE_HEADING = (By.CSS_SELECTOR, "#showResult h1")
    TRANSFER_MESSAGE = (By.CSS_SELECTOR, "#showResult p")

    # Navigation link - specifically in the left panel account services menu
    TRANSFER_FUNDS_LINK = (By.XPATH, "//div[@id='leftPanel']//a[contains(@href,'transfer.htm')]")

    def __init__(self, web: WebInterface):
        self.web = web

    def navigate(self, base_url: str) -> "TransferFundsPage":
        """Navigate to the transfer funds page."""
        self.web.navigate_to(f"{base_url}/parabank/transfer.htm")
        return self

    def click_transfer_funds_link(self) -> "TransferFundsPage":
        """Click the Transfer Funds link from account services menu."""
        self.web.click(*self.TRANSFER_FUNDS_LINK)
        return self

    # Atomic action methods - return self for chaining
    def enter_amount(self, amount: str) -> "TransferFundsPage":
        """Enter transfer amount."""
        self.web.type_text(*self.AMOUNT_INPUT, amount)
        return self

    def select_from_account(self, account_id: str) -> "TransferFundsPage":
        """Select the source account."""
        element = self.web.find_element(*self.FROM_ACCOUNT_SELECT)
        select = Select(element)
        select.select_by_visible_text(account_id)
        return self

    def select_to_account(self, account_id: str) -> "TransferFundsPage":
        """Select the destination account."""
        element = self.web.find_element(*self.TO_ACCOUNT_SELECT)
        select = Select(element)
        select.select_by_visible_text(account_id)
        return self

    def click_transfer(self) -> "TransferFundsPage":
        """Click the Transfer button."""
        self.web.click(*self.TRANSFER_BUTTON)
        return self

    # State-check methods for assertions
    def is_transfer_complete(self) -> bool:
        """Check if transfer was completed successfully."""
        return self.web.is_element_displayed(*self.TRANSFER_COMPLETE_HEADING, timeout=10)

    def get_transfer_complete_heading(self) -> str:
        """Get the transfer complete heading text."""
        return self.web.get_text(*self.TRANSFER_COMPLETE_HEADING)

    def get_transfer_message(self) -> str:
        """Get the transfer confirmation message."""
        return self.web.get_text(*self.TRANSFER_MESSAGE)

    def get_transferred_amount(self) -> str:
        """Extract the transferred amount from the confirmation message."""
        message = self.get_transfer_message()
        # Message format: "$100.00 has been transferred from account #X to account #Y"
        if message and "$" in message:
            amount = message.split("$")[1].split(" ")[0]
            return amount
        return ""
