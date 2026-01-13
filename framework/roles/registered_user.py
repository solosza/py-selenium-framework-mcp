
class RegisteredUser:
    @autologger.automation_logger("Role Constructor")
    def __init__(self, web, user_data, base_url):
        self.auth_tasks = AuthTasks(web, base_url)

    @autologger.automation_logger("Role")
    def login(self) -> None:
        self.auth_tasks.log_in(self.email, self.password)
