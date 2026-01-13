from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.parabank5.parabank_tasks import ParabankTasks
from resources.utilities import autologger


class RegisteredUser:
    """Role representing an authenticated ParaBank user persona."""

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web: WebInterface, user_data: Dict[str, Any]):
        self.web = web
        self.user_data = user_data
        self.username = user_data.get("username")
        self.password = user_data.get("password")
        self.parabank_tasks = ParabankTasks(web)

    @autologger.automation_logger("Role")
    def transfer_funds_between_accounts(self, amount: str, from_account: str, to_account: str) -> None:
        self.parabank_tasks.log_in(self.username, self.password)
        self.parabank_tasks.transfer_funds(amount, from_account, to_account)
