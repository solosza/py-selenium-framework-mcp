"""Multi-persona tests."""
import pytest
from resources.utilities import autologger
from roles.admin_user import AdminUser
from roles.registered_user import RegisteredUser
from pages.admin.user_management_page import UserManagementPage
from pages.auth.login_page import LoginPage


class TestMultiPersona:
    @pytest.mark.admin
    @autologger.automation_logger("Test")
    def test_admin_login(self):
        """Test admin login."""
        admin = AdminUser(self.web, admin_data, self.base_url)
        admin.login()
        assert self.admin_page.is_logged_in()

    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_user_login(self):
        """Test user login."""
        user = RegisteredUser(self.web, user_data, self.base_url)
        user.login()
        assert self.login_page.is_logged_in()
