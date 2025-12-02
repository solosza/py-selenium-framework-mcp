"""
Unit Tests for MCP Code Generators

Tests that generated code matches the validated 4-layer framework patterns
from FRAMEWORK.md.

Run: python -m pytest mcp_server/_dev_tests/test_generators.py -v
"""

import sys
from pathlib import Path

# Add mcp_server to path
MCP_SERVER_PATH = str(Path(__file__).parent.parent)
sys.path.insert(0, MCP_SERVER_PATH)

from utils.generators.page_object_generator import (
    generate_page_object,
    generate_locators_block,
    generate_action_methods_block,
    get_generated_method_names,
    get_file_path
)


class TestPageObjectGenerator:
    """Tests for page_object_generator.py"""

    def test_generate_basic_page_object(self):
        """Test generating a basic POM with no elements."""
        code = generate_page_object("TestPage")

        # Verify class structure
        assert "class TestPage:" in code
        assert "def __init__(self, web: WebInterface):" in code
        assert "self.web = web" in code

        # Verify NO decorators (critical rule)
        assert "@autologger" not in code
        assert "@automation_logger" not in code

        # Verify imports
        assert "from selenium.webdriver.common.by import By" in code
        assert "from interfaces.web_interface import WebInterface" in code

    def test_generate_page_object_with_elements(self):
        """Test generating POM with various element types."""
        elements = [
            {"suggested_name": "email", "locator": "#email", "element_type": "inputs"},
            {"suggested_name": "password", "locator": "#passwd", "element_type": "inputs"},
            {"suggested_name": "submit_login", "locator": "#SubmitLogin", "element_type": "buttons"},
        ]

        code = generate_page_object("LoginPage", elements=elements, workflow_type="auth")

        # Verify locators as class constants (UPPER_SNAKE)
        assert "EMAIL = (By.CSS_SELECTOR, \"#email\")" in code
        assert "PASSWORD = (By.CSS_SELECTOR, \"#passwd\")" in code
        assert "SUBMIT_LOGIN = (By.CSS_SELECTOR, \"#SubmitLogin\")" in code

        # Verify action methods generated
        assert "def enter_email(self, email: str) -> \"LoginPage\":" in code
        assert "def enter_password(self, password: str) -> \"LoginPage\":" in code
        assert "def click_submit_login(self) -> \"LoginPage\":" in code

        # Verify fluent API (return self)
        assert "return self" in code

    def test_no_decorators_on_pom_methods(self):
        """CRITICAL: POM methods must have NO decorators."""
        elements = [
            {"suggested_name": "button", "locator": "#btn", "element_type": "buttons"},
        ]

        code = generate_page_object("TestPage", elements=elements)

        # Split into lines and check each method definition
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if "def " in line and "self" in line:
                # Check previous line is not a decorator
                if i > 0:
                    prev_line = lines[i-1].strip()
                    assert not prev_line.startswith("@"), \
                        f"Method has decorator: {prev_line} before {line}"

    def test_action_methods_return_self(self):
        """Action methods must return self for fluent chaining."""
        elements = [
            {"suggested_name": "email", "locator": "#email", "element_type": "inputs"},
            {"suggested_name": "submit", "locator": "#submit", "element_type": "buttons"},
        ]

        code = generate_page_object("TestPage", elements=elements)

        # Count return self statements (should match number of action methods)
        action_method_count = code.count("def enter_") + code.count("def click_")
        return_self_count = code.count("return self")

        assert return_self_count >= action_method_count, \
            "Each action method should return self"

    def test_auth_workflow_state_checks(self):
        """Auth workflow should have login-related state-check methods."""
        code = generate_page_object("LoginPage", workflow_type="auth")

        # Verify state-check methods present
        assert "def is_logged_in(self) -> bool:" in code
        assert "def is_logged_out(self) -> bool:" in code
        assert "def has_error_message(self) -> bool:" in code
        assert "def get_error_message(self) -> str:" in code

    def test_catalog_workflow_state_checks(self):
        """Catalog workflow should have product-related state-check methods."""
        code = generate_page_object("ProductListPage", workflow_type="catalog")

        # Verify state-check methods present
        assert "def has_products(self) -> bool:" in code
        assert "def get_product_count(self) -> int:" in code
        assert "def is_page_loaded(self) -> bool:" in code

    def test_locators_block_generation(self):
        """Test locator block generation."""
        elements = [
            {"suggested_name": "email_input", "locator": "#email", "element_type": "inputs"},
            {"suggested_name": "xpath_element", "locator": "//div[@id='test']", "element_type": "buttons"},
        ]

        block = generate_locators_block(elements)

        assert "EMAIL_INPUT = (By.CSS_SELECTOR, \"#email\")" in block
        assert "XPATH_ELEMENT = (By.XPATH, \"//div[@id='test']\")" in block

    def test_get_generated_method_names(self):
        """Test utility to get method names for given elements."""
        elements = [
            {"suggested_name": "email", "locator": "#email", "element_type": "inputs"},
            {"suggested_name": "submit", "locator": "#submit", "element_type": "buttons"},
            {"suggested_name": "remember_me", "locator": "#remember", "element_type": "checkboxes"},
        ]

        methods = get_generated_method_names(elements)

        assert "enter_email" in methods
        assert "click_submit" in methods
        assert "check_remember_me" in methods
        assert "uncheck_remember_me" in methods

    def test_get_file_path(self):
        """Test file path generation."""
        path = get_file_path("LoginPage", "auth")
        assert path == "framework/pages/auth/login_page.py"

        path = get_file_path("ProductListPage", "catalog")
        assert path == "framework/pages/catalog/product_list_page.py"

    def test_checkbox_generates_check_and_uncheck(self):
        """Checkbox elements should generate both check and uncheck methods."""
        elements = [
            {"suggested_name": "newsletter", "locator": "#newsletter", "element_type": "checkboxes"},
        ]

        code = generate_page_object("SettingsPage", elements=elements)

        assert "def check_newsletter(self) -> \"SettingsPage\":" in code
        assert "def uncheck_newsletter(self) -> \"SettingsPage\":" in code

    def test_select_generates_select_method(self):
        """Select elements should generate select method with value param."""
        elements = [
            {"suggested_name": "country", "locator": "#country", "element_type": "selects"},
        ]

        code = generate_page_object("AddressPage", elements=elements)

        assert "def select_country(self, value: str) -> \"AddressPage\":" in code
        assert "select_dropdown_by_value" in code


# Run tests directly if executed
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
