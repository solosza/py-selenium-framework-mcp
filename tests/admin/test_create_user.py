"""Multi-role test."""
import pytest
from resources.utilities import autologger
from roles.admin_user import AdminUser
from roles.registered_user import RegisteredUser
from pages.admin.user_management_page import UserManagementPage


class TestAdminCreatesUser:
    @pytest.mark.admin
    @autologger.automation_logger("Test")
    def test_admin_created_user_can_login(self):
        """Test admin creates user, user can login."""
        # Arrange
        admin = AdminUser(self.web, admin_data, self.base_url)
        user = RegisteredUser(self.web, user_data, self.base_url)

        # Act
        admin.create_user(user_data)
        admin.logout()
        user.login()

        # Assert
        assert self.user_page.is_logged_in()
