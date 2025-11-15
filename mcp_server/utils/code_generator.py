"""
Code Generator Utility

Template-based code scaffolding for framework components.
Used by Tools 2-6 (test, role, task, POM generation).
"""

from typing import Dict, List, Optional, Tuple


def map_scenario_to_test_logic(
    workflow: str,
    scenario: Dict[str, str]
) -> Tuple[str, str, str]:
    """
    Map Given-When-Then scenario to actual test code (Arrange, Act, Assert).

    Args:
        workflow: Workflow type (auth, catalog, cart, checkout)
        scenario: Scenario dict with given/when/then

    Returns:
        Tuple of (test_data_code, action_code, assertion_code)
    """
    given = scenario.get("given", "").lower()
    when = scenario.get("when", "").lower()
    then = scenario.get("then", "").lower()

    test_data = ""
    actions = ""
    assertions = ""

    # ===== AUTH WORKFLOW MAPPINGS =====
    if workflow == "auth":
        # LOGIN scenarios (check when, given, and then for login keywords)
        full_scenario = f"{given} {when} {then}"
        if ("login" in when or "log in" in when or "sign in" in when or
            ("email" in when and "password" in when) or
            ("logged in" in then or "dashboard" in then)):
            # Determine if valid or invalid credentials
            if "valid" in given or "correct" in given or "registered" in given:
                test_data = '''test_email = "test@example.com"
    test_password = "Test123!"'''
                actions = f'''result = {workflow}_tasks.login(test_email, test_password)'''

                # Check what should happen (success vs failure)
                if "success" in then or "logged in" in then or "dashboard" in then:
                    assertions = '''assert result is True, "Login should succeed with valid credentials"'''
                else:
                    assertions = '''assert result is True, "Expected login to succeed"'''

            elif "invalid" in given or "incorrect" in given or "wrong" in given:
                test_data = '''test_email = "invalid@example.com"
    test_password = "WrongPassword123!"'''
                actions = f'''result = {workflow}_tasks.login(test_email, test_password)'''
                assertions = '''assert result is False, "Login should fail with invalid credentials"'''

            else:
                # Generic login
                test_data = '''test_email = "test@example.com"
    test_password = "Test123!"'''
                actions = f'''result = {workflow}_tasks.login(test_email, test_password)'''
                assertions = '''assert result is True, "Login should succeed"'''

        # LOGOUT scenarios
        elif "logout" in when or "log out" in when or "sign out" in when:
            test_data = '''# User must be logged in first
    test_email = "test@example.com"
    test_password = "Test123!"
    {workflow}_tasks.login(test_email, test_password)'''.format(workflow=workflow)
            actions = f'''result = {workflow}_tasks.logout()'''
            assertions = '''assert result is True, "Logout should succeed"'''

        # REGISTRATION scenarios
        elif "register" in when or "sign up" in when or "create account" in when:
            test_data = '''from faker import Faker
    fake = Faker()
    test_email = fake.email()
    test_password = "NewUser123!"
    test_first_name = fake.first_name()
    test_last_name = fake.last_name()'''
            actions = f'''result = {workflow}_tasks.register_new_user(
        email=test_email,
        password=test_password,
        first_name=test_first_name,
        last_name=test_last_name
    )'''
            assertions = '''assert result is True, "Registration should succeed"'''

    # ===== CATALOG WORKFLOW MAPPINGS =====
    elif workflow == "catalog":
        # BROWSE scenarios
        if "browse" in when or "view" in when or "navigate" in when:
            if "category" in when:
                test_data = '''category_name = "Women"'''
                actions = f'''result = {workflow}_tasks.browse_category(category_name)'''
                assertions = '''assert result is True, "Should successfully browse category"
    assert {workflow}_tasks.get_product_count() > 0, "Category should have products"'''.format(workflow=workflow)

        # FILTER scenarios
        elif "filter" in when:
            test_data = '''filter_criteria = {{"size": "M", "color": "Blue"}}'''
            actions = f'''result = {workflow}_tasks.filter_products(filter_criteria)'''
            assertions = '''assert result is True, "Filters should be applied successfully"'''

        # SORT scenarios
        elif "sort" in when:
            if "price" in when:
                test_data = '''sort_by = "price_low_to_high"'''
            else:
                test_data = '''sort_by = "name"'''
            actions = f'''result = {workflow}_tasks.sort_products(sort_by)'''
            assertions = '''assert result is True, "Products should be sorted successfully"'''

    # ===== CART WORKFLOW MAPPINGS =====
    elif workflow == "cart":
        # ADD TO CART scenarios
        if "add" in when and "cart" in when:
            test_data = '''product_name = "Faded Short Sleeve T-shirts"
    quantity = 1'''
            actions = f'''result = {workflow}_tasks.add_to_cart(product_name, quantity)'''
            assertions = '''assert result is True, "Product should be added to cart successfully"
    assert {workflow}_tasks.get_cart_count() > 0, "Cart should contain items"'''.format(workflow=workflow)

        # REMOVE FROM CART scenarios
        elif "remove" in when:
            test_data = '''# Add item first
    product_name = "Faded Short Sleeve T-shirts"
    {workflow}_tasks.add_to_cart(product_name, 1)'''.format(workflow=workflow)
            actions = f'''result = {workflow}_tasks.remove_from_cart(product_name)'''
            assertions = '''assert result is True, "Product should be removed from cart"'''

        # UPDATE QUANTITY scenarios
        elif "update" in when or "change quantity" in when:
            test_data = '''# Add item first
    product_name = "Faded Short Sleeve T-shirts"
    {workflow}_tasks.add_to_cart(product_name, 1)
    new_quantity = 3'''.format(workflow=workflow)
            actions = f'''result = {workflow}_tasks.update_quantity(product_name, new_quantity)'''
            assertions = '''assert result is True, "Quantity should be updated"'''

    # ===== CHECKOUT WORKFLOW MAPPINGS =====
    elif workflow == "checkout":
        if "checkout" in when or "place order" in when:
            test_data = '''# Add item to cart first
    catalog_tasks = CatalogTasks(web_interface, base_url)
    cart_tasks = CartTasks(web_interface, base_url)
    cart_tasks.add_to_cart("Faded Short Sleeve T-shirts", 1)

    # Prepare shipping info
    shipping_info = {{
        "address": "123 Test St",
        "city": "Test City",
        "state": "CA",
        "zip": "90001"
    }}'''
            actions = f'''result = {workflow}_tasks.complete_checkout(shipping_info)'''
            assertions = '''assert result is True, "Checkout should complete successfully"'''

    # ===== FALLBACK (Generic) =====
    if not test_data:
        test_data = f'''# TODO: Add test data for {workflow} workflow'''
    if not actions:
        actions = f'''# TODO: Implement {workflow} action based on scenario
    # result = {workflow}_tasks.some_action()'''
    if not assertions:
        assertions = f'''# TODO: Add assertions for {workflow} workflow
    # assert result is True, "Action should succeed"'''

    return test_data, actions, assertions


def generate_test_template(
    test_name: str,
    workflow: str,
    scenario: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate pytest test template following framework patterns.

    Args:
        test_name: Test function name (e.g., test_add_to_cart)
        workflow: Workflow category (auth, catalog, cart, checkout)
        scenario: Optional scenario dict with given/when/then

    Returns:
        Python test code as string
    """
    # Extract scenario details
    given = scenario.get("given", "") if scenario else ""
    when = scenario.get("when", "") if scenario else ""
    then = scenario.get("then", "") if scenario else ""
    description = scenario.get("description", "") if scenario else ""

    # Capitalize task class name
    task_class = f"{workflow.capitalize()}Tasks"

    # Generate docstring
    docstring = f'"""\n    {description or test_name}\n\n'
    if given or when or then:
        docstring += '    Scenario:\n'
        if given:
            docstring += f'        Given: {given}\n'
        if when:
            docstring += f'        When: {when}\n'
        if then:
            docstring += f'        Then: {then}\n'
    docstring += '    """'

    # Map scenario to actual test logic (NEW!)
    test_data_code = ""
    action_code = ""
    assertion_code = ""

    if scenario:
        test_data_code, action_code, assertion_code = map_scenario_to_test_logic(workflow, scenario)

    # If no scenario provided, use generic placeholders
    if not test_data_code:
        test_data_code = f"# TODO: Add test data for {workflow} workflow"
    if not action_code:
        action_code = f"# TODO: Implement {workflow} action\n    # result = {workflow}_tasks.some_action()"
    if not assertion_code:
        assertion_code = f"# TODO: Add assertions\n    # assert result is True"

    # Generate test code
    code = f'''"""
{workflow.capitalize()} Tests - {test_name.replace("test_", "").replace("_", " ").title()}.

Test generated from user story scenario.
"""

import pytest
from pathlib import Path
import sys

# Add framework to path
FRAMEWORK_PATH = str(Path(__file__).parent.parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from tasks.{workflow}_tasks import {task_class}
from resources.utilities import autologger


@pytest.mark.{workflow}
@autologger.automation_logger("Test")
def {test_name}(web_interface, config):
    {docstring}
    # Arrange
    base_url = config["url"]
    {workflow}_tasks = {task_class}(web_interface, base_url)

    {test_data_code}

    # Act
    {action_code}

    # Assert
    {assertion_code}
'''

    return code


def generate_role_template(
    role_name: str,
    capabilities: Optional[List[str]] = None,
    credentials: Optional[Dict[str, str]] = None
) -> str:
    """
    Generate role class template matching framework patterns.

    Args:
        role_name: Role class name (e.g., RegisteredUser)
        capabilities: List of capabilities (e.g., ["can_login"])
        credentials: Optional credentials dict

    Returns:
        Python role class code as string
    """
    capabilities = capabilities or []

    # Generate capability methods
    capability_methods = ""
    if "can_login" in capabilities:
        capability_methods += '''
    # ==================== AUTHENTICATION WORKFLOWS ====================

    def login(self) -> bool:
        """
        Log in to the application.

        High-level business workflow that orchestrates authentication.

        Returns:
            True if login successful, False otherwise
        """
        return self.common_tasks.log_in(self.email, self.password)

    def logout(self) -> bool:
        """
        Log out from the application.

        Returns:
            True if logout successful, False otherwise
        """
        return self.common_tasks.log_out()

    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in.

        Returns:
            True if logged in, False otherwise
        """
        return self.common_tasks.verify_logged_in()
'''

    code = f'''"""
{role_name} Role.

This role represents a user with specific capabilities and permissions.
"""

from typing import Dict, Any
from framework.roles.role import Role
from framework.interfaces.web_interface import WebInterface
from framework.tasks.common_tasks import CommonTasks


class {role_name}(Role):
    """
    {role_name} role with workflow capabilities.

    Capabilities: {', '.join(capabilities) if capabilities else 'None specified'}
    """

    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        """
        Initialize {role_name}.

        Args:
            web_interface: WebInterface instance for browser interactions
            user_data: Dictionary containing user credentials and profile data
            base_url: Application base URL for navigation
        """
        super().__init__(web_interface, user_data)

        # Validate required credentials
        if not self.has_credentials():
            raise ValueError("{role_name} requires email and password in user_data")

        # Compose task modules
        self.common_tasks = CommonTasks(web_interface, base_url)

        # TODO: Add additional task modules as needed
{capability_methods}
    # TODO: Add role-specific workflow methods
'''

    return code


def generate_task_workflows(
    workflow_type: str,
    page_name: str,
    page_methods: List[str]
) -> str:
    """
    Generate complete workflow methods based on workflow type and available POM methods.

    Args:
        workflow_type: Type of workflow (auth, catalog, cart, checkout)
        page_name: Page object class name (e.g., LoginPage)
        page_methods: List of method names from the POM (e.g., ['enter_email', 'click_submitlogin'])

    Returns:
        Python workflow method code as string
    """
    page_var = f"{page_name[0].lower()}{page_name[1:]}"  # LoginPage -> loginPage
    page_var = page_var.replace("Page", "_page")  # loginPage -> login_page

    workflows = []
    workflows.append("\n    # ==================== WORKFLOW METHODS ====================\n")

    if workflow_type == "auth":
        # Generate login workflow if we have the required methods
        has_email = any("email" in m and "enter" in m for m in page_methods)
        has_password = any("pass" in m and "enter" in m for m in page_methods)
        has_submit = any("submit" in m and "login" in m and "click" in m for m in page_methods)

        if has_email and has_password and has_submit:
            # Find exact method names
            email_method = next((m for m in page_methods if "email" in m and "enter" in m), "enter_email")
            password_method = next((m for m in page_methods if "pass" in m and "enter" in m), "enter_passwd")
            submit_method = next((m for m in page_methods if "submit" in m and "login" in m and "click" in m), "click_submitlogin")

            workflows.append(f'''
    def login(self, email: str, password: str) -> bool:
        """
        Execute login workflow.

        Complete workflow:
        1. Navigate to login page
        2. Enter email and password
        3. Click submit button
        4. Verify login success

        Args:
            email: User email address
            password: User password

        Returns:
            True if login successful, False otherwise
        """
        # Navigate to authentication page
        self.web.navigate_to(f"{{self.base_url}}/index.php?controller=authentication")

        # Enter credentials
        self.{page_var}.{email_method}(email)
        self.{page_var}.{password_method}(password)

        # Submit login
        self.{page_var}.{submit_method}()

        # Verify login success (check for account menu or logout link)
        from selenium.webdriver.common.by import By
        return self.web.is_element_displayed(By.CSS_SELECTOR, ".account, .logout")

    def logout(self) -> bool:
        """
        Execute logout workflow.

        Complete workflow:
        1. Click logout link
        2. Verify logout success

        Returns:
            True if logout successful, False otherwise
        """
        from selenium.webdriver.common.by import By

        # Click logout if visible
        if self.web.is_element_displayed(By.CSS_SELECTOR, ".logout"):
            self.web.click(By.CSS_SELECTOR, ".logout")

        # Verify logout (login link should be visible)
        return self.web.is_element_displayed(By.CSS_SELECTOR, ".login")
''')

    elif workflow_type == "catalog":
        # Generate catalog browsing workflows
        has_category_links = any("category" in m or "link" in m for m in page_methods)

        workflows.append(f'''
    def browse_category(self, category_name: str) -> bool:
        """
        Browse to a specific product category.

        Args:
            category_name: Name of category to browse

        Returns:
            True if category page loaded, False otherwise
        """
        from selenium.webdriver.common.by import By

        # Navigate to homepage
        self.web.navigate_to(self.base_url)

        # Click category link
        category_locator = (By.XPATH, f"//a[contains(text(), '{{category_name}}')]")
        if self.web.is_element_displayed(*category_locator):
            self.web.click(*category_locator)

            # Verify category page loaded
            return self.web.is_element_displayed(By.CSS_SELECTOR, ".product-container, .product_list")

        return False

    def get_product_count(self) -> int:
        """
        Get count of products displayed on page.

        Returns:
            Number of products found
        """
        from selenium.webdriver.common.by import By
        products = self.web.find_elements(By.CSS_SELECTOR, ".product-container")
        return len(products)
''')

    elif workflow_type == "cart":
        # Generate cart management workflows
        workflows.append(f'''
    def add_to_cart(self, product_name: str) -> bool:
        """
        Add product to shopping cart.

        Args:
            product_name: Name of product to add

        Returns:
            True if product added successfully, False otherwise
        """
        from selenium.webdriver.common.by import By

        # Find and click product
        product_locator = (By.XPATH, f"//a[contains(@title, '{{product_name}}')]")
        if self.web.is_element_displayed(*product_locator):
            self.web.click(*product_locator)

            # Click add to cart button
            add_to_cart_btn = (By.CSS_SELECTOR, ".add-to-cart, button[name='Submit']")
            if self.web.is_element_displayed(*add_to_cart_btn):
                self.web.click(*add_to_cart_btn)

                # Verify cart confirmation
                return self.web.is_element_displayed(By.CSS_SELECTOR, ".layer_cart_product, #layer_cart")

        return False

    def view_cart(self) -> bool:
        """
        Navigate to shopping cart page.

        Returns:
            True if cart page loaded, False otherwise
        """
        from selenium.webdriver.common.by import By

        # Click cart link
        cart_link = (By.CSS_SELECTOR, ".shopping_cart a, a[title='View my shopping cart']")
        if self.web.is_element_displayed(*cart_link):
            self.web.click(*cart_link)

            # Verify cart page loaded
            return self.web.is_element_displayed(By.CSS_SELECTOR, "#cart_summary, .cart_navigation")

        return False
''')

    else:
        # Generic workflow template for unknown types
        workflows.append(f'''
    def example_workflow(self, param: str) -> bool:
        """
        Execute example workflow.

        Args:
            param: Workflow parameter

        Returns:
            True if workflow successful, False otherwise
        """
        # TODO: Implement workflow using page object methods
        # Available methods: {', '.join(page_methods[:5])}{'...' if len(page_methods) > 5 else ''}

        raise NotImplementedError("Workflow not yet implemented")
''')

    return "".join(workflows)


def generate_task_template(
    task_name: str,
    workflow_description: Optional[str] = None,
    page_objects: Optional[List[Dict[str, any]]] = None
) -> str:
    """
    Generate task class template matching framework patterns.

    Args:
        task_name: Task class name (e.g., CatalogTasks)
        workflow_description: Optional workflow description
        page_objects: Optional list of page object dicts with name, file_path, methods

    Returns:
        Python task class code as string
    """
    # Extract workflow name from task name (e.g., CatalogTasks -> catalog)
    workflow_lower = task_name.replace("Tasks", "").lower()

    # Generate page object imports and initialization
    page_imports = ""
    page_inits = ""
    workflow_methods = ""

    if page_objects:
        # Generate imports for each page object
        for page_obj in page_objects:
            page_name = page_obj.get("name", "")
            page_file = page_obj.get("file_path", "")
            page_methods = page_obj.get("methods", [])

            if page_name and page_file:
                # Convert file path to import path
                # e.g., "framework/pages/auth/loginpage.py" -> "framework.pages.auth.loginpage"
                import_path = page_file.replace(".py", "").replace("/", ".").replace("\\", ".")
                page_imports += f"from {import_path} import {page_name}\n"

                # Generate page object instance variable name
                page_var = f"{page_name[0].lower()}{page_name[1:]}"
                page_var = page_var.replace("Page", "_page")

                page_inits += f"        self.{page_var} = {page_name}(web)\n"

        # Generate workflow methods using page object methods
        if page_objects:
            first_page = page_objects[0]
            page_name = first_page.get("name", "")
            page_methods = first_page.get("methods", [])

            workflow_methods = generate_task_workflows(workflow_lower, page_name, page_methods)
    else:
        # No page objects provided - use placeholder
        page_imports = f"# TODO: Import required page objects\n# from pages.{workflow_lower}.some_page import SomePage"
        page_inits = "        # TODO: Initialize page objects\n        # self.some_page = SomePage(web)"
        workflow_methods = '''

    # ==================== WORKFLOW METHODS ====================

    def example_workflow(self, param1: str) -> bool:
        """
        Execute example workflow.

        Complete workflow: describe the steps here.

        Args:
            param1: Description of parameter

        Returns:
            True if workflow successful, False otherwise
        """
        # TODO: Implement workflow
        # Example:
        # self.some_page.perform_action(param1)
        # return self.some_page.verify_result()

        raise NotImplementedError("Workflow not yet implemented")

    # TODO: Add more workflow methods
'''

    code = f'''"""
{task_name} - Reusable workflow methods.

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.

{workflow_description or 'TODO: Add workflow description'}
"""

from typing import Optional
from framework.interfaces.web_interface import WebInterface
{page_imports}


class {task_name}:
    """{task_name} workflows."""

    def __init__(self, web: WebInterface, base_url: str):
        """
        Initialize {task_name}.

        Args:
            web: WebInterface instance
            base_url: Application base URL
        """
        self.web = web
        self.base_url = base_url

{page_inits}
{workflow_methods}'''

    return code


def generate_pom_methods(elements: List[Dict[str, str]]) -> str:
    """
    Generate interaction methods for page object based on element types.

    Args:
        elements: List of element dicts with name, locator, type

    Returns:
        Python method code as string
    """
    if not elements:
        return ""

    methods = []
    methods.append("\n    # ==================== INTERACTION METHODS ====================\n")

    for elem in elements:
        # Tool 5 provides "suggested_name", Tool 6 test data might use "name"
        name = (elem.get("suggested_name") or elem.get("name", "")).upper()
        elem_type = elem.get("element_type", "")

        if not name or not elem_type:
            continue

        # Generate method based on element type
        if elem_type == "inputs":
            # Input field - generate enter_X method
            method_name = f"enter_{name.lower()}"
            methods.append(f'''
    def {method_name}(self, text: str) -> None:
        """
        Enter text into {name} field.

        Args:
            text: Text to enter
        """
        self.web.type_text(*self.{name}, text)
''')

        elif elem_type == "buttons":
            # Button - generate click_X method
            method_name = f"click_{name.lower()}"
            methods.append(f'''
    def {method_name}(self) -> None:
        """Click {name} button."""
        self.web.click(*self.{name})
''')

        elif elem_type == "links":
            # Link - generate click_X method
            method_name = f"click_{name.lower()}"
            methods.append(f'''
    def {method_name}(self) -> None:
        """Click {name} link."""
        self.web.click(*self.{name})
''')

        elif elem_type == "selects":
            # Select dropdown - generate select_X method
            method_name = f"select_{name.lower()}"
            methods.append(f'''
    def {method_name}(self, value: str) -> None:
        """
        Select option from {name} dropdown.

        Args:
            value: Option value to select
        """
        self.web.select_dropdown_by_value(*self.{name}, option_value=value)
''')

        elif elem_type == "checkboxes":
            # Checkbox - generate check_X and uncheck_X methods
            check_method = f"check_{name.lower()}"
            uncheck_method = f"uncheck_{name.lower()}"
            methods.append(f'''
    def {check_method}(self) -> None:
        """Check {name} checkbox."""
        if not self.web.is_element_selected(*self.{name}):
            self.web.click(*self.{name})

    def {uncheck_method}(self) -> None:
        """Uncheck {name} checkbox."""
        if self.web.is_element_selected(*self.{name}):
            self.web.click(*self.{name})
''')

    return "".join(methods)


def generate_page_object_template(
    page_name: str,
    elements: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate page object template.

    Args:
        page_name: Page class name (e.g., ProductListPage)
        elements: List of element dicts with locator/name

    Returns:
        Python page object code as string
    """
    elements = elements or []

    # Generate locators section
    locators = ""
    for elem in elements:
        locator = elem.get("locator", "")
        name = elem.get("name", "").upper()
        if locator and name:
            # Determine By locator type from selector syntax
            by_type = _determine_by_type(locator)
            locators += f'    {name} = (By.{by_type}, "{locator}")\n'

    if not locators:
        locators = "    # TODO: Add locators\n"

    # Generate methods section (COMPLETE implementation)
    methods = generate_pom_methods(elements) if elements else ""

    code = f'''from selenium.webdriver.common.by import By
from framework.pages.base_page import BasePage
from framework.interfaces.web_interface import WebInterface


class {page_name}(BasePage):
    """
    {page_name} - Page Object Model

    Represents the page and provides methods for interaction.
    """

    def __init__(self, web: WebInterface):
        """
        Initialize {page_name}.

        Args:
            web: WebInterface instance
        """
        super().__init__(web)

    # ==================== LOCATORS ====================

{locators}
{methods}
'''

    return code


def _determine_by_type(locator: str) -> str:
    """
    Determine Selenium By locator type from selector syntax.

    Args:
        locator: Locator string (e.g., "#id", ".class", "//xpath")

    Returns:
        By type as string (e.g., "ID", "CSS_SELECTOR", "XPATH")
    """
    locator = locator.strip()

    # ID selector
    if locator.startswith("#") and " " not in locator:
        return "CSS_SELECTOR"

    # XPath
    if locator.startswith("//") or locator.startswith("(//"):
        return "XPATH"

    # CSS Selector (default)
    return "CSS_SELECTOR"


def get_file_path_for_component(component_type: str, name: str, workflow: str = None) -> str:
    """
    Get suggested file path for generated component.

    Args:
        component_type: Type (test, role, task, page)
        name: Component name (PascalCase)
        workflow: Optional workflow for categorization

    Returns:
        Suggested file path (snake_case)
    """
    import re

    # Convert PascalCase to snake_case
    # LoginPage -> login_page, AuthTasks -> auth_tasks
    snake_name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()

    if component_type == "test":
        return f"tests/{workflow}/{snake_name}.py"
    elif component_type == "role":
        return f"framework/roles/{snake_name}.py"
    elif component_type == "task":
        return f"framework/tasks/{snake_name}.py"
    elif component_type == "page":
        # Always use common/ directory for pages
        return f"framework/pages/common/{snake_name}.py"
    else:
        return f"{snake_name}.py"
