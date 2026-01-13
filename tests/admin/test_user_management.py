"""Multi-persona workflow test."""
import pytest
from resources.utilities import autologger
from roles.admin_user import AdminUser
from roles.registered_user import RegisteredUser
from pages.user.profile_page import ProfilePage


class TestUserManagement:
    @pytest.mark.admin
    @autologger.automation_logger("Test")
    def test_admin_creates_user_and_user_logs_in(self):
        """Test admin creates user, then new user logs in."""
        # Arrange
        admin = AdminUser(self.web, admin_data, self.base_url)
        new_user = RegisteredUser(self.web, user_data, self.base_url)
        profile_page = ProfilePage(self.web)

        # Act - Multiple calls across DIFFERENT personas (VALID multi-persona)
        admin.create_user(user_data)
        admin.logout()
        new_user.login()

        # Assert
        assert profile_page.is_logged_in()
