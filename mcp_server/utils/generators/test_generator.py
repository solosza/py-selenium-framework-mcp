"""
Test Generator

Generates Test class code following the validated 4-layer framework patterns.
This generator embeds the authoritative code pattern template from FRAMEWORK.md Section 4.4.

EMBEDDED PATTERN RULES (from FRAMEWORK.md):
- @autologger.automation_logger("Test") decorator on test methods
- @pytest.mark.<category> marker for categorization
- Arrange: Create role and POM instances
- Act: ONE role workflow method call (no return capture)
- Assert: Via POM state-check methods (NOT return values)
- NO orchestration (don't call multiple Role methods in one test)

TEMPLATE SOURCE: FRAMEWORK.md Section 4.4 Test Layer
"""

import re
from typing import Dict, List, Optional


# =============================================================================
# EMBEDDED CODE PATTERN TEMPLATE (from FRAMEWORK.md Section 4.4)
# =============================================================================
# This is the authoritative pattern that all generated Tests must match.

TEST_FILE_TEMPLATE = '''"""
{test_description}

Test suite for {workflow_readable} workflows.
Uses AAA pattern: Arrange, Act, Assert.
"""

import pytest
from resources.utilities import autologger
{role_imports}
{page_imports}


class {test_class_name}:
    """
    {test_class_name} - Test suite for {workflow_readable}.

    - @autologger("Test") decorator
    - Load data from fixtures
    - Call ONE workflow method per Role
    - Assert via Page Object state-check methods
    - NO orchestration (don't call multiple Role methods)
    """

    @pytest.fixture(autouse=True)
    def setup(self, web_interface, config):
        """Setup test fixtures."""
        self.web = web_interface
        self.config = config
        self.base_url = config.get("url", config.get("base_url", ""))
{page_instantiations}
    # ==================== TEST METHODS ====================
{test_methods}'''


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _pascal_to_snake(name: str) -> str:
    """Convert PascalCase to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def _detect_workflow_type(test_name: str, description: str = "") -> str:
    """Detect workflow type from test name and description."""
    combined = f"{test_name} {description}".lower()

    if any(kw in combined for kw in ["login", "logout", "auth", "register"]):
        return "auth"
    if any(kw in combined for kw in ["catalog", "browse", "product", "category", "filter"]):
        return "catalog"
    if any(kw in combined for kw in ["cart", "basket", "add"]):
        return "cart"
    if any(kw in combined for kw in ["checkout", "payment", "order"]):
        return "checkout"

    return "general"


# =============================================================================
# IMPORT GENERATION
# =============================================================================

def generate_role_imports(roles: List[Dict[str, str]]) -> str:
    """Generate import statements for roles."""
    if not roles:
        return ""

    imports = []
    for role in roles:
        name = role.get("name", "")
        import_path = role.get("import_path", "")

        if name and import_path:
            imports.append(f"from {import_path} import {name}")

    return "\n".join(imports)


def generate_page_imports(pages: List[Dict[str, str]]) -> str:
    """Generate import statements for pages."""
    if not pages:
        return ""

    imports = []
    for page in pages:
        name = page.get("name", "")
        import_path = page.get("import_path", "")

        if name and import_path:
            imports.append(f"from {import_path} import {name}")

    return "\n".join(imports)


def generate_page_instantiations(pages: List[Dict[str, str]]) -> str:
    """Generate page object instantiations in setup."""
    if not pages:
        return ""

    lines = []
    for page in pages:
        name = page.get("name", "")
        if name:
            var_name = _pascal_to_snake(name)
            lines.append(f"        self.{var_name} = {name}(web_interface)")

    return "\n".join(lines) + "\n" if lines else ""


# =============================================================================
# TEST METHOD TEMPLATES
# =============================================================================

# Auth workflow test templates
AUTH_LOGIN_TEST = '''
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_valid_login(self):
        """
        Test that user can login with valid credentials.

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check method
        """
        # Arrange
        user_data = {{"email": "testuser@example.com", "password": "TestPass123"}}
        user = {role_name}(self.web, user_data, self.base_url)

        # Act - ONE workflow call, NO return value
        user.login()

        # Assert - Via Page Object state-check method (NOT return value)
        assert self.{page_var}.is_logged_in(), "User should be logged in"
'''

AUTH_LOGOUT_TEST = '''
    @pytest.mark.auth
    @autologger.automation_logger("Test")
    def test_logout(self):
        """Test that user can logout."""
        # Arrange
        user_data = {{"email": "testuser@example.com", "password": "TestPass123"}}
        user = {role_name}(self.web, user_data, self.base_url)

        # Act - Login first, then logout
        user.login()
        user.logout()

        # Assert - Via Page Object state-check method
        assert self.{page_var}.is_logged_out(), "User should be logged out"
'''

# Catalog workflow test templates
CATALOG_BROWSE_TEST = '''
    @pytest.mark.catalog
    @autologger.automation_logger("Test")
    def test_browse_category(self):
        """
        Test that user can browse a product category.

        AAA Pattern:
        1. Arrange - Create role
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check method
        """
        # Arrange
        guest = {role_name}(self.web, self.base_url)

        # Act - ONE workflow call, NO return value
        guest.browse_category("Women")

        # Assert - Via Page Object state-check method (NOT return value)
        assert self.{page_var}.has_products(), "Products should be displayed"
'''

CATALOG_FILTER_TEST = '''
    @pytest.mark.catalog
    @autologger.automation_logger("Test")
    def test_browse_and_filter(self):
        """Test that user can browse and filter products."""
        # Arrange
        guest = {role_name}(self.web, self.base_url)

        # Act - ONE workflow call that orchestrates multiple tasks
        guest.browse_and_filter("Women", "M")

        # Assert - Via Page Object state-check method
        assert self.{page_var}.has_products(), "Filtered products should be displayed"
'''

# Generic test template
GENERIC_TEST = '''
    @pytest.mark.{workflow}
    @autologger.automation_logger("Test")
    def test_{test_name}(self):
        """
        {test_description}

        AAA Pattern: Arrange, Act, Assert
        """
        # Arrange
        # TODO: Create role with appropriate data

        # Act - ONE workflow call, NO return value
        # TODO: Call role workflow method

        # Assert - Via Page Object state-check method
        # TODO: assert page.state_check_method(), "Expected result"
        pass
'''


def generate_test_methods(
    workflow_type: str,
    roles: List[Dict[str, str]],
    pages: List[Dict[str, str]],
    custom_tests: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate test methods based on workflow type.

    Args:
        workflow_type: Type of workflow (auth, catalog, cart, etc.)
        roles: List of role modules
        pages: List of page objects
        custom_tests: Optional list of custom test definitions

    Returns:
        Test methods code block
    """
    methods = []

    # Get primary role and page variable names
    role_name = "Role"
    page_var = "page"

    if roles:
        role_name = roles[0].get("name", "Role")
    if pages:
        primary_page = pages[0].get("name", "")
        if primary_page:
            page_var = _pascal_to_snake(primary_page)

    # Add workflow-specific tests
    if workflow_type == "auth":
        methods.append(AUTH_LOGIN_TEST.format(role_name=role_name, page_var=page_var))
        methods.append(AUTH_LOGOUT_TEST.format(role_name=role_name, page_var=page_var))

    elif workflow_type == "catalog":
        methods.append(CATALOG_BROWSE_TEST.format(role_name=role_name, page_var=page_var))
        methods.append(CATALOG_FILTER_TEST.format(role_name=role_name, page_var=page_var))

    # Add custom tests if provided
    if custom_tests:
        for test in custom_tests:
            name = test.get("name", "custom_test")
            description = test.get("description", "Custom test case.")
            workflow = test.get("workflow", workflow_type)

            methods.append(GENERIC_TEST.format(
                workflow=workflow,
                test_name=name,
                test_description=description
            ))

    # If no methods generated, add a placeholder
    if not methods:
        methods.append(GENERIC_TEST.format(
            workflow=workflow_type or "general",
            test_name="placeholder",
            test_description="Placeholder test - implement specific tests."
        ))

    return "".join(methods)


# =============================================================================
# MAIN GENERATOR FUNCTION
# =============================================================================

def generate_test(
    test_class_name: str,
    roles: Optional[List[Dict[str, str]]] = None,
    pages: Optional[List[Dict[str, str]]] = None,
    workflow_type: Optional[str] = None,
    test_description: Optional[str] = None,
    custom_tests: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate complete Test class code matching FRAMEWORK.md patterns.

    This function uses the embedded TEST_FILE_TEMPLATE to produce code that
    exactly matches the authoritative pattern from FRAMEWORK.md Section 4.4.

    Args:
        test_class_name: Test class name (e.g., TestLogin, TestCatalog)
        roles: List of role dicts with 'name' and 'import_path'
        pages: List of page object dicts with 'name' and 'import_path'
        workflow_type: Optional workflow type (auto-detected if not provided)
        test_description: Optional description for docstring
        custom_tests: Optional list of custom test definitions

    Returns:
        Complete Python test class code as string
    """
    roles = roles or []
    pages = pages or []

    # Auto-detect workflow type if not provided
    detected_workflow = workflow_type or _detect_workflow_type(test_class_name, test_description or "")
    workflow_readable = detected_workflow.replace("_", " ").title()

    # Generate description
    description = test_description or f"{test_class_name} - Test suite for {workflow_readable} workflows."

    # Generate each section
    role_imports = generate_role_imports(roles)
    page_imports = generate_page_imports(pages)
    page_instantiations = generate_page_instantiations(pages)
    test_methods = generate_test_methods(detected_workflow, roles, pages, custom_tests)

    # Assemble using the master template
    code = TEST_FILE_TEMPLATE.format(
        test_description=description,
        test_class_name=test_class_name,
        workflow_readable=workflow_readable,
        role_imports=role_imports,
        page_imports=page_imports,
        page_instantiations=page_instantiations,
        test_methods=test_methods
    )

    return code


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_file_path(test_class_name: str, workflow: str = "general") -> str:
    """
    Get suggested file path for the generated test.

    Args:
        test_class_name: Test class name (PascalCase)
        workflow: Workflow/domain folder

    Returns:
        Suggested file path (e.g., tests/auth/test_login.py)
    """
    # Convert TestLogin -> test_login
    snake_name = _pascal_to_snake(test_class_name)
    return f"tests/{workflow}/{snake_name}.py"


def get_pytest_markers() -> List[str]:
    """Get list of common pytest markers."""
    return ["auth", "catalog", "cart", "checkout", "smoke", "regression"]
