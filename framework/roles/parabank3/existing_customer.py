"""
ExistingCustomer - Role for parabank3 workflow
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
from tasks.parabank3.parabank3_tasks import Parabank3Tasks


class ExistingCustomer:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        self.web = web_interface
        self.base_url = base_url
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')

        if not self.email or not self.password:
            raise ValueError(f"ExistingCustomer requires email and password in user_data")

        self.parabank3_tasks = Parabank3Tasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def open_new_account(self, account_type: str, from_account_id: str) -> None:
        self.parabank3_tasks.open_new_account(account_type, from_account_id)

    @autologger.automation_logger("Role")
    def transfer_funds(self, amount: str, from_account_id: str, to_account_id: str) -> None:
        self.parabank3_tasks.transfer_funds(amount, from_account_id, to_account_id)

    @autologger.automation_logger("Role")
    def navigate_to_account_activity(self) -> None:
        self.parabank3_tasks.navigate_to_account_activity()
