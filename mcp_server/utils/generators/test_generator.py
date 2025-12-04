"""
Test Generator

Generates Test class code following the validated 4-layer framework patterns.
This generator uses METADATA from Role and POM generators to create dynamic Tests.

METADATA-DRIVEN ARCHITECTURE:
- Accepts Role metadata (workflow_methods[])
- Accepts POM metadata (state_methods[])
- Generates Test methods that call actual Role methods
- Generates assertions using actual POM state methods
- No hardcoded method names - all derived from metadata

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
from typing import Dict, List, Optional, Any


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


def _detect_workflow_type(test_name: str, description: str = "", role_name: str = "") -> str:
    """
    Detect workflow type from test name, description, and role name.

    Args:
        test_name: Test class or function name
        description: Test description
        role_name: Role class name (e.g., GuestUser, RegisteredUser)

    Returns:
        Workflow type string (auth, catalog, cart, checkout, general)
    """
    combined = f"{test_name} {description} {role_name}".lower()

    if any(kw in combined for kw in ["login", "logout", "auth", "register", "registered"]):
        return "auth"
    if any(kw in combined for kw in ["catalog", "browse", "product", "category", "filter", "guest"]):
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
        guest = {role_name}(self.web, {{}}, self.base_url)

        # Act - ONE workflow call, NO return value
        guest.browse_products()

        # Assert - Via Page Object state-check method (NOT return value)
        assert self.{page_var}.is_page_loaded(), "Category page should be loaded"
'''

CATALOG_VERIFY_TEST = '''
    @pytest.mark.catalog
    @autologger.automation_logger("Test")
    def test_verify_products_displayed(self):
        """Test that products are displayed on category page."""
        # Arrange
        guest = {role_name}(self.web, {{}}, self.base_url)

        # Act - ONE workflow call, NO return value
        guest.browse_products()

        # Assert - Via Page Object state-check method
        assert self.{page_var}.has_products(), "Products should be displayed"
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


# =============================================================================
# DYNAMIC TEST METHOD GENERATION (from Role + POM metadata)
# =============================================================================

def _generate_test_method_from_metadata(
    role_method: Dict[str, Any],
    role_name: str,
    role_var: str,
    pom_state_methods: List[Dict[str, Any]],
    page_var: str,
    workflow: str,
    requires_credentials: bool = True
) -> str:
    """
    Generate a single Test method that calls a Role workflow method.

    Args:
        role_method: Role method metadata with name, params[], calls[]
        role_name: Role class name (e.g., RegisteredUser)
        role_var: Role variable name (e.g., user)
        pom_state_methods: List of POM state methods for assertions
        page_var: Page object variable name (e.g., login_page)
        workflow: Workflow type for pytest marker
        requires_credentials: Whether role needs user_data

    Returns:
        Test method code string
    """
    method_name = role_method.get("name", "workflow")
    method_params = role_method.get("params", [])

    # Build test function name
    test_func_name = f"test_{method_name}"

    # Build role instantiation
    if requires_credentials:
        role_instantiation = f'''user_data = {{"email": "testuser@example.com", "password": "TestPass123"}}
        {role_var} = {role_name}(self.web, user_data, self.base_url)'''
    else:
        role_instantiation = f'''{role_var} = {role_name}(self.web, self.base_url)'''

    # Build method call
    if method_params:
        # Build params with sample values
        param_values = []
        for param in method_params:
            param_name = param.split(":")[0].strip()
            # Skip email/password as they come from user_data
            if param_name not in ["email", "password"]:
                param_values.append(f'"{param_name}_value"')
        call_args = ", ".join(param_values)
        method_call = f"{role_var}.{method_name}({call_args})"
    else:
        method_call = f"{role_var}.{method_name}()"

    # Build assertions from POM state methods
    assertions = []
    for state_method in pom_state_methods[:2]:  # Use up to 2 state methods
        state_name = state_method.get("name", "")
        if state_name:
            # Generate assertion based on method type
            if state_name.startswith("is_") or state_name.startswith("has_"):
                assertions.append(
                    f'assert self.{page_var}.{state_name}(), "{state_name.replace("_", " ").title()}"'
                )
            elif state_name.startswith("get_"):
                # For get_ methods, check it returns something
                assertions.append(
                    f'assert self.{page_var}.{state_name}() is not None, "{state_name} should return a value"'
                )

    if not assertions:
        assertions.append(f'assert self.{page_var}.is_page_loaded(), "Page should be loaded"')

    assertions_code = "\n        ".join(assertions)

    # Build docstring
    description = f"Test {method_name.replace('_', ' ')} workflow."

    return f'''
    @pytest.mark.{workflow}
    @autologger.automation_logger("Test")
    def {test_func_name}(self):
        """
        {description}

        AAA Pattern:
        1. Arrange - Create role with test data
        2. Act - Call ONE workflow method (no return value)
        3. Assert - Use POM state-check methods
        """
        # Arrange
        {role_instantiation}

        # Act - ONE workflow call, NO return value
        {method_call}

        # Assert - Via Page Object state-check methods (NOT return value)
        {assertions_code}
'''


def generate_test_methods_from_metadata(
    role_metadata: Dict[str, Any],
    pom_metadata: Dict[str, Any],
    workflow: str = "general"
) -> tuple:
    """
    Generate Test methods dynamically from Role and POM metadata.

    This is the key function for metadata-driven generation.
    It uses Role workflow_methods and POM state_methods to create tests.

    Args:
        role_metadata: Role metadata with class_name, workflow_methods[]
        pom_metadata: POM metadata with class_name, state_methods[]
        workflow: Workflow type for pytest marker

    Returns:
        Tuple of (methods_code: str, test_methods_metadata: List[Dict])
    """
    methods_code = []
    test_methods_metadata = []

    role_name = role_metadata.get("class_name", "Role")
    role_var = "user" if "user" in role_name.lower() else _pascal_to_snake(role_name)
    workflow_methods = role_metadata.get("workflow_methods", [])

    page_name = pom_metadata.get("class_name", "Page")
    page_var = _pascal_to_snake(page_name)
    state_methods = pom_metadata.get("state_methods", [])

    # Determine if role requires credentials
    requires_credentials = "guest" not in role_name.lower()

    # Generate a test for each workflow method
    for workflow_method in workflow_methods:
        method_code = _generate_test_method_from_metadata(
            role_method=workflow_method,
            role_name=role_name,
            role_var=role_var,
            pom_state_methods=state_methods,
            page_var=page_var,
            workflow=workflow,
            requires_credentials=requires_credentials
        )
        methods_code.append(method_code)

        # Build metadata
        test_methods_metadata.append({
            "name": f"test_{workflow_method.get('name', 'workflow')}",
            "workflow_method_called": workflow_method.get("name", ""),
            "assertions": [m.get("name", "") for m in state_methods[:2]]
        })

    # If no methods generated, add a placeholder
    if not methods_code:
        placeholder = GENERIC_TEST.format(
            workflow=workflow,
            test_name="placeholder",
            test_description="Placeholder test - implement specific tests."
        )
        methods_code.append(placeholder)
        test_methods_metadata.append({
            "name": "test_placeholder",
            "workflow_method_called": "",
            "assertions": []
        })

    return "".join(methods_code), test_methods_metadata


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
        methods.append(CATALOG_VERIFY_TEST.format(role_name=role_name, page_var=page_var))

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

    # Get primary role name for detection
    primary_role_name = roles[0].get("name", "") if roles else ""

    # Auto-detect workflow type if not provided or if custom folder name
    # Use role name as additional context for detection
    detected_workflow = _detect_workflow_type(test_class_name, test_description or "", primary_role_name)

    # If explicit workflow_type is a standard type, use it; otherwise use detection
    if workflow_type in ("auth", "catalog", "cart", "checkout"):
        detected_workflow = workflow_type

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


def generate_test_with_metadata(
    test_class_name: str,
    role_metadata: Dict[str, Any],
    pom_metadata: Dict[str, Any],
    workflow: str = "general",
    test_description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate Test class code AND metadata using Role + POM metadata.

    This is the primary function for the metadata-passing architecture.
    It uses Role and POM metadata to generate dynamic Test methods.

    Args:
        test_class_name: Test class name (e.g., TestLogin, TestCatalog)
        role_metadata: Role metadata from Tool 5 with workflow_methods[]
        pom_metadata: POM metadata from Tool 3 with state_methods[]
        workflow: Workflow type for pytest marker and file path
        test_description: Optional description for docstring

    Returns:
        Dict with {code, metadata} where metadata has:
        - class_name: str
        - file_path: str
        - test_methods: List[{name, workflow_method_called, assertions[]}]
    """
    role_name = role_metadata.get("class_name", "Role")
    role_import_path = role_metadata.get("import_path", "")

    page_name = pom_metadata.get("class_name", "Page")
    page_import_path = pom_metadata.get("import_path", "")
    page_var = _pascal_to_snake(page_name)

    workflow_readable = workflow.replace("_", " ").title()

    # Generate description
    description = test_description or f"{test_class_name} - Test suite for {workflow_readable} workflows."

    # Build role and page configs for imports
    roles = [{"name": role_name, "import_path": role_import_path}] if role_import_path else []
    pages = [{"name": page_name, "import_path": page_import_path}] if page_import_path else []

    # Generate imports
    role_imports = generate_role_imports(roles)
    page_imports = generate_page_imports(pages)

    # Generate page instantiation in setup
    page_instantiations = ""
    if page_name:
        page_instantiations = f"        self.{page_var} = {page_name}(self.web)\n"

    # Generate test methods from metadata
    test_methods_code, test_methods_metadata = generate_test_methods_from_metadata(
        role_metadata=role_metadata,
        pom_metadata=pom_metadata,
        workflow=workflow
    )

    # Assemble code using template
    code = TEST_FILE_TEMPLATE.format(
        test_description=description,
        test_class_name=test_class_name,
        workflow_readable=workflow_readable,
        role_imports=role_imports,
        page_imports=page_imports,
        page_instantiations=page_instantiations,
        test_methods=test_methods_code
    )

    # Get file path
    file_path = get_file_path(test_class_name, workflow)

    # Build metadata
    metadata = {
        "class_name": test_class_name,
        "file_path": file_path,
        "role_used": role_name,
        "page_used": page_name,
        "test_methods": test_methods_metadata
    }

    return {
        "code": code,
        "metadata": metadata
    }


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
