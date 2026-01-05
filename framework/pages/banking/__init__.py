"""Banking workflow page objects."""
from pages.banking.registration_page import RegistrationPage
from pages.banking.open_new_account_page import OpenNewAccountPage
from pages.banking.transfer_funds_page import TransferFundsPage
from pages.banking.accounts_overview_page import AccountsOverviewPage

__all__ = [
    "RegistrationPage",
    "OpenNewAccountPage",
    "TransferFundsPage",
    "AccountsOverviewPage",
]
