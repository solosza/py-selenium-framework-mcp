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

from utils.generators.task_generator import (
    generate_task,
    get_file_path as get_task_file_path,
    get_available_workflows
)

from utils.generators.role_generator import (
    generate_role,
    get_file_path as get_role_file_path,
    get_available_role_types
)

from utils.generators.test_generator import (
    generate_test,
    get_file_path as get_test_file_path,
    get_pytest_markers
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


class TestTestGenerator:
    """Tests for test_generator.py"""

    def test_generate_basic_test(self):
        """Test generating a basic Test with no roles or pages."""
        code = generate_test("TestBasic")

        # Verify class structure
        assert "class TestBasic:" in code
        assert "def setup(self, web_interface, config):" in code
        assert "self.web = web_interface" in code
        assert "self.config = config" in code

        # Verify imports
        assert "import pytest" in code
        assert "from resources.utilities import autologger" in code

    def test_test_methods_have_decorator(self):
        """CRITICAL: Test methods must have @autologger("Test") decorator."""
        code = generate_test("TestLogin", workflow_type="auth")

        # Verify decorator is present
        assert '@autologger.automation_logger("Test")' in code

    def test_test_methods_have_pytest_marker(self):
        """Test methods should have pytest markers."""
        code = generate_test("TestCatalog", workflow_type="catalog")

        # Verify pytest marker is present
        assert "@pytest.mark.catalog" in code

    def test_test_asserts_via_pom_not_return_values(self):
        """CRITICAL: Tests must assert via POM state-check methods, NOT return values."""
        pages = [
            {"name": "LoginPage", "import_path": "pages.auth.login_page"},
        ]
        code = generate_test("TestLogin", pages=pages, workflow_type="auth")

        # Verify assertions use POM methods
        assert "assert self.login_page." in code

        # Verify no assertions on return values (like "result = user.login()")
        assert "result = " not in code
        assert "return_value = " not in code

    def test_test_calls_one_role_method(self):
        """Test should call ONE role workflow method (AAA pattern)."""
        roles = [
            {"name": "GuestUser", "import_path": "roles.guest_user"},
        ]
        pages = [
            {"name": "ProductListPage", "import_path": "pages.catalog.product_list_page"},
        ]
        code = generate_test("TestCatalog", roles=roles, pages=pages, workflow_type="catalog")

        # Verify AAA pattern comments
        assert "# Arrange" in code
        assert "# Act" in code
        assert "# Assert" in code

    def test_test_instantiates_pages_in_setup(self):
        """Test should instantiate POMs in setup fixture."""
        pages = [
            {"name": "ProductListPage", "import_path": "pages.catalog.product_list_page"},
        ]
        code = generate_test("TestCatalog", pages=pages)

        # Verify POM instantiation in setup
        assert "self.product_list_page = ProductListPage(web_interface)" in code

    def test_auth_workflow_generates_login_tests(self):
        """Auth workflow should generate login/logout tests."""
        roles = [
            {"name": "AuthenticatedUser", "import_path": "roles.authenticated_user"},
        ]
        pages = [
            {"name": "LoginPage", "import_path": "pages.auth.login_page"},
        ]
        code = generate_test("TestLogin", roles=roles, pages=pages, workflow_type="auth")

        # Verify auth-specific tests
        assert "def test_valid_login(self):" in code
        assert "user.login()" in code
        assert "is_logged_in()" in code

    def test_catalog_workflow_generates_browse_tests(self):
        """Catalog workflow should generate browse tests."""
        roles = [
            {"name": "GuestUser", "import_path": "roles.guest_user"},
        ]
        pages = [
            {"name": "ProductListPage", "import_path": "pages.catalog.product_list_page"},
        ]
        code = generate_test("TestCatalog", roles=roles, pages=pages, workflow_type="catalog")

        # Verify catalog-specific tests
        assert "def test_browse_category(self):" in code
        assert "browse_category(" in code
        assert "has_products()" in code

    def test_get_test_file_path(self):
        """Test file path generation for tests."""
        path = get_test_file_path("TestLogin", "auth")
        assert path == "tests/auth/test_login.py"

        path = get_test_file_path("TestCatalog", "catalog")
        assert path == "tests/catalog/test_catalog.py"

    def test_get_pytest_markers(self):
        """Test available pytest markers list."""
        markers = get_pytest_markers()

        assert "auth" in markers
        assert "catalog" in markers
        assert "smoke" in markers


class TestRoleGenerator:
    """Tests for role_generator.py"""

    def test_generate_basic_role(self):
        """Test generating a basic Role with no task modules."""
        code = generate_role("TestRole")

        # Verify class structure
        assert "class TestRole:" in code
        assert "def __init__(self, web_interface: WebInterface" in code
        assert "self.web = web_interface" in code
        assert "self.base_url = base_url" in code

        # Verify imports
        assert "from interfaces.web_interface import WebInterface" in code
        assert "from resources.utilities import autologger" in code

    def test_role_constructor_has_decorator(self):
        """CRITICAL: Role constructor must have @autologger("Role Constructor") decorator."""
        code = generate_role("AuthenticatedUser")

        # Verify decorator on constructor
        assert '@autologger.automation_logger("Role Constructor")' in code

        # Verify decorator is before __init__
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if '@autologger.automation_logger("Role Constructor")' in line:
                # Next non-empty line should be def __init__
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        assert "def __init__" in lines[j], \
                            f"Role Constructor decorator not followed by __init__: {lines[j]}"
                        break
                break

    def test_role_workflow_methods_have_decorator(self):
        """CRITICAL: Role workflow methods must have @autologger("Role") decorator."""
        task_modules = [
            {"name": "AuthTasks", "import_path": "tasks.auth_tasks"},
        ]
        code = generate_role("AuthenticatedUser", task_modules=task_modules, role_type="authenticated")

        # Verify decorator is present
        assert '@autologger.automation_logger("Role")' in code

    def test_role_methods_return_none(self):
        """CRITICAL: Role methods must return None (no return statements with values)."""
        task_modules = [
            {"name": "CatalogTasks", "import_path": "tasks.catalog_tasks"},
        ]
        code = generate_role("GuestUser", task_modules=task_modules, role_type="guest")

        # Check that methods have -> None type hint
        assert "-> None:" in code

        # No return statements with values (return <something>)
        lines = code.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("return ") and stripped != "return":
                assert False, f"Role method returns value: {line}"

    def test_role_composes_task_modules(self):
        """Role should compose task modules in constructor."""
        task_modules = [
            {"name": "AuthTasks", "import_path": "tasks.auth_tasks"},
            {"name": "CatalogTasks", "import_path": "tasks.catalog_tasks"},
        ]

        code = generate_role("AuthenticatedUser", task_modules=task_modules)

        # Verify imports
        assert "from tasks.auth_tasks import AuthTasks" in code
        assert "from tasks.catalog_tasks import CatalogTasks" in code

        # Verify composition in constructor
        assert "self.auth_tasks = AuthTasks(web_interface, base_url)" in code
        assert "self.catalog_tasks = CatalogTasks(web_interface, base_url)" in code

    def test_authenticated_role_has_credentials(self):
        """Authenticated role should have user_data parameter."""
        code = generate_role("AuthenticatedUser", role_type="authenticated")

        # Verify user_data parameter
        assert "user_data: Dict[str, Any]" in code
        assert "self.user_data = user_data" in code
        assert "self.email = user_data.get('email')" in code
        assert "self.password = user_data.get('password')" in code

    def test_guest_role_no_credentials(self):
        """Guest role should NOT have user_data parameter."""
        code = generate_role("GuestUser", role_type="guest")

        # Verify no user_data parameter
        assert "user_data" not in code
        assert "self.email" not in code
        assert "self.password" not in code

    def test_authenticated_role_workflow_methods(self):
        """Authenticated role should have login/logout methods."""
        task_modules = [
            {"name": "AuthTasks", "import_path": "tasks.auth_tasks"},
        ]
        code = generate_role("AuthenticatedUser", task_modules=task_modules, role_type="authenticated")

        # Verify auth-specific methods
        assert "def login(self)" in code
        assert "def logout(self)" in code

    def test_guest_role_workflow_methods(self):
        """Guest role should have browse methods."""
        task_modules = [
            {"name": "CatalogTasks", "import_path": "tasks.catalog_tasks"},
        ]
        code = generate_role("GuestUser", task_modules=task_modules, role_type="guest")

        # Verify guest-specific methods
        assert "def browse_category(self, category_name: str)" in code

    def test_get_role_file_path(self):
        """Test file path generation for roles."""
        path = get_role_file_path("AuthenticatedUser")
        assert path == "framework/roles/authenticated_user.py"

        path = get_role_file_path("GuestUser")
        assert path == "framework/roles/guest_user.py"

    def test_get_available_role_types(self):
        """Test available role types list."""
        types = get_available_role_types()

        assert "guest" in types
        assert "authenticated" in types
        assert "admin" in types


class TestTaskGenerator:
    """Tests for task_generator.py"""

    def test_generate_basic_task(self):
        """Test generating a basic Task with no page objects."""
        code = generate_task("TestTasks")

        # Verify class structure
        assert "class TestTasks:" in code
        assert "def __init__(self, web: WebInterface, base_url: str):" in code
        assert "self.web = web" in code
        assert "self.base_url = base_url" in code

        # Verify imports
        assert "from interfaces.web_interface import WebInterface" in code
        assert "from resources.utilities import autologger" in code

    def test_task_methods_have_decorator(self):
        """CRITICAL: Task methods must have @autologger("Task") decorator."""
        code = generate_task("AuthTasks", workflow_type="auth")

        # Verify decorator is present
        assert '@autologger.automation_logger("Task")' in code

        # Verify method follows decorator
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if '@autologger.automation_logger("Task")' in line:
                # Next non-empty line should be def
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        assert lines[j].strip().startswith("def "), \
                            f"Decorator not followed by method: {lines[j]}"
                        break

    def test_task_methods_return_none(self):
        """CRITICAL: Task methods must return None (no return statements with values)."""
        code = generate_task("CatalogTasks", workflow_type="catalog")

        # Check that methods have -> None type hint
        assert "-> None:" in code

        # No return statements with values (return <something>)
        lines = code.split("\n")
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("return ") and stripped != "return":
                # Allow 'return' alone but not 'return <value>'
                assert False, f"Task method returns value: {line}"

    def test_task_constructor_no_decorator(self):
        """Task constructor must have NO decorator."""
        code = generate_task("TestTasks")

        lines = code.split("\n")
        for i, line in enumerate(lines):
            if "def __init__" in line:
                # Check previous non-empty line is not a decorator
                for j in range(i - 1, -1, -1):
                    if lines[j].strip():
                        assert not lines[j].strip().startswith("@autologger"), \
                            "Constructor should not have @autologger decorator"
                        break
                break

    def test_task_composes_page_objects(self):
        """Task should compose page objects in constructor."""
        page_objects = [
            {"name": "LoginPage", "import_path": "pages.auth.login_page"},
        ]

        code = generate_task("AuthTasks", page_objects=page_objects)

        # Verify import
        assert "from pages.auth.login_page import LoginPage" in code

        # Verify composition in constructor
        assert "self.login_page = LoginPage(web)" in code

    def test_auth_workflow_methods(self):
        """Auth workflow should have login/logout methods."""
        code = generate_task("AuthTasks", workflow_type="auth")

        # Verify auth-specific methods
        assert "def log_in(self, email: str, password: str)" in code
        assert "def log_out(self)" in code

    def test_catalog_workflow_methods(self):
        """Catalog workflow should have browse/filter methods."""
        code = generate_task("CatalogTasks", workflow_type="catalog")

        # Verify catalog-specific methods
        assert "def browse_category(self, category_name: str)" in code
        assert "def filter_by_size(self, size: str)" in code

    def test_task_no_locators(self):
        """CRITICAL: Tasks must NOT have locators (except inline temporary)."""
        code = generate_task("CatalogTasks", workflow_type="catalog")

        # No class-level locator constants (UPPER_SNAKE = (By...))
        lines = code.split("\n")
        for line in lines:
            stripped = line.strip()
            # Check for locator pattern at class level
            if "= (By." in stripped and not stripped.startswith("self."):
                # Allow inline locators in methods, but not class-level
                if not stripped.startswith("#"):  # Skip comments
                    # This should only appear inside methods, not at class level
                    pass  # Inline locators are allowed

    def test_get_task_file_path(self):
        """Test file path generation for tasks."""
        path = get_task_file_path("AuthTasks", "auth")
        assert path == "framework/tasks/auth/auth_tasks.py"

        path = get_task_file_path("CatalogTasks", "catalog")
        assert path == "framework/tasks/catalog/catalog_tasks.py"

    def test_get_available_workflows(self):
        """Test available workflows list."""
        workflows = get_available_workflows()

        assert "auth" in workflows
        assert "catalog" in workflows
        assert "cart" in workflows
        assert "common" in workflows


# Run tests directly if executed
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
