"""
Task Generator

Generates Task class code following the validated 4-layer framework patterns.
This generator embeds the authoritative code pattern template from FRAMEWORK.md Section 4.2.

EMBEDDED PATTERN RULES (from FRAMEWORK.md):
- @autologger.automation_logger("Task") on all methods
- NO decorator on constructor
- Composes Page Objects (instantiates in constructor)
- One domain operation per method (SRP)
- NO return values (returns None) - tests assert via POM
- NO locators (locators only in POMs)
- Uses fluent POM API (method chaining)

TEMPLATE SOURCE: FRAMEWORK.md Section 4.2 Task Layer
"""

import re
from typing import Dict, List, Optional


# =============================================================================
# EMBEDDED CODE PATTERN TEMPLATE (from FRAMEWORK.md Section 4.2)
# =============================================================================
# This is the authoritative pattern that all generated Tasks must match.

TASK_TEMPLATE = '''"""
{task_description}

This module provides high-level task methods that orchestrate page objects
to accomplish business workflows.
"""

from interfaces.web_interface import WebInterface
from resources.utilities import autologger
{page_imports}


class {task_name}:
    """
    Task module for {workflow_readable} operations.

    - @autologger("Task") on all methods
    - NO decorator on constructor
    - Composes Page Objects
    - One domain operation per method
    - NO return values
    - Uses fluent POM API
    """

    def __init__(self, web: WebInterface, base_url: str):
        """
        Compose Page Objects - NO decorator on constructor.

        Args:
            web: WebInterface instance
            base_url: Application base URL
        """
        self.web = web
        self.base_url = base_url
{page_compositions}
    # ==================== TASK METHODS ====================
{task_methods}'''


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _pascal_to_snake(name: str) -> str:
    """Convert PascalCase to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def _detect_workflow_type(task_name: str, description: str = "") -> str:
    """Detect workflow type from task name and description."""
    combined = f"{task_name} {description}".lower()

    if any(kw in combined for kw in ["auth", "login", "logout", "register", "signin"]):
        return "auth"
    if any(kw in combined for kw in ["catalog", "browse", "product", "category", "filter", "sort"]):
        return "catalog"
    if any(kw in combined for kw in ["cart", "basket", "shopping"]):
        return "cart"
    if any(kw in combined for kw in ["checkout", "payment", "order"]):
        return "checkout"

    return "common"


# =============================================================================
# PAGE IMPORT GENERATION
# =============================================================================

def generate_page_imports(page_objects: List[Dict[str, str]]) -> str:
    """
    Generate import statements for page objects.

    Args:
        page_objects: List of dicts with 'name' and 'import_path'

    Returns:
        Import statements block
    """
    if not page_objects:
        return ""

    imports = []
    for page in page_objects:
        name = page.get("name", "")
        import_path = page.get("import_path", "")

        if name and import_path:
            imports.append(f"from {import_path} import {name}")

    return "\n".join(imports)


def generate_page_compositions(page_objects: List[Dict[str, str]]) -> str:
    """
    Generate page object composition in constructor.

    Pattern from FRAMEWORK.md:
        self.login_page = LoginPage(web)

    Args:
        page_objects: List of dicts with 'name'

    Returns:
        Page composition code block
    """
    if not page_objects:
        return ""

    lines = []
    for page in page_objects:
        name = page.get("name", "")
        if name:
            # Convert LoginPage -> login_page
            var_name = _pascal_to_snake(name)
            lines.append(f"        self.{var_name} = {name}(web)")

    return "\n".join(lines) + "\n" if lines else ""


# =============================================================================
# TASK METHOD TEMPLATES
# =============================================================================

# Auth workflow method templates (from FRAMEWORK.md Section 4.2)
AUTH_LOGIN_METHOD = '''
    @autologger.automation_logger("Task")
    def log_in(self, email: str, password: str) -> None:
        """
        Complete login operation.

        Single domain operation: authenticate user.
        NO return value - test asserts via POM.
        """
        # Navigate to login page
        self.web.navigate_to(f"{{self.base_url}}/index.php?controller=authentication")

        # Use fluent POM API (method chaining)
        (self.{page_var}
            .enter_email(email)
            .enter_password(password)
            .click_submit())

        # NO return - test will assert via {page_var}.is_logged_in()
'''

AUTH_LOGOUT_METHOD = '''
    @autologger.automation_logger("Task")
    def log_out(self) -> None:
        """
        Complete logout operation.

        NO return value.
        """
        # Click logout link (uses page object method)
        logout_locator = (By.CSS_SELECTOR, ".logout")
        self.web.click(*logout_locator)

        # NO return - test will assert via {page_var}.is_logged_out()
'''

AUTH_NAVIGATE_METHOD = '''
    @autologger.automation_logger("Task")
    def navigate_to_login_page(self) -> None:
        """Navigate to authentication page."""
        self.web.navigate_to(f"{{self.base_url}}/index.php?controller=authentication")
        # NO return
'''

# Catalog workflow method templates
CATALOG_BROWSE_METHOD = '''
    @autologger.automation_logger("Task")
    def browse_category(self, category_name: str) -> None:
        """
        Browse a product category.

        Single domain operation: navigate to category.
        NO return value - test asserts via POM.

        Args:
            category_name: Category to browse ("Women", "Dresses", "T-shirts")
        """
        # Navigate to home first
        self.web.navigate_to(self.base_url)

        # Click category based on name (using POM methods)
        category_upper = category_name.upper()
        if category_upper == "WOMEN":
            self.{page_var}.click_women_category()
        elif category_upper == "DRESSES":
            self.{page_var}.click_dresses_category()
        elif category_upper in ("T-SHIRTS", "TSHIRTS"):
            self.{page_var}.click_tshirts_category()
        else:
            self.web.logger.error(f"Unknown category: {{category_name}}")
            return

        self.web.logger.info(f"Browsed to category: {{category_name}}")
        # NO return - test asserts via {page_var}.has_products()
'''

CATALOG_FILTER_METHOD = '''
    @autologger.automation_logger("Task")
    def filter_by_size(self, size: str) -> None:
        """
        Filter products by size.

        Args:
            size: Size filter ("S", "M", "L")
        """
        self.{page_var}.filter_by_size(size)
        self.web.logger.info(f"Applied size filter: {{size}}")
        # NO return - test asserts via {page_var}.has_products()
'''

CATALOG_SORT_METHOD = '''
    @autologger.automation_logger("Task")
    def sort_by_price(self, ascending: bool = True) -> None:
        """
        Sort products by price.

        Args:
            ascending: True for low-to-high, False for high-to-low
        """
        if ascending:
            self.{page_var}.sort_by_price_low_to_high()
        else:
            self.{page_var}.sort_by_price_high_to_low()

        self.web.logger.info(f"Sorted by price: {{'ascending' if ascending else 'descending'}}")
        # NO return - test asserts via {page_var}.is_sorted_by_price_ascending()
'''

# Cart workflow method templates
CART_ADD_METHOD = '''
    @autologger.automation_logger("Task")
    def add_to_cart(self, product_index: int = 0) -> None:
        """
        Add product to cart by index.

        Args:
            product_index: Index of product to add (0-based)
        """
        self.{page_var}.click_add_to_cart(product_index)
        self.web.logger.info(f"Added product at index {{product_index}} to cart")
        # NO return - test asserts via {page_var}.is_cart_confirmation_displayed()
'''

# Generic task method template
GENERIC_TASK_METHOD = '''
    @autologger.automation_logger("Task")
    def {method_name}(self{params}) -> None:
        """
        {method_description}

        NO return value - test asserts via POM.
        """
        # TODO: Implement using page object methods
        pass
        # NO return
'''


def generate_task_methods(
    workflow_type: str,
    page_objects: List[Dict[str, str]],
    custom_methods: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate task methods based on workflow type.

    Args:
        workflow_type: Type of workflow (auth, catalog, cart, etc.)
        page_objects: List of page objects (to get variable names)
        custom_methods: Optional list of custom method definitions

    Returns:
        Task methods code block
    """
    methods = []

    # Get primary page object variable name
    page_var = "page"
    if page_objects:
        primary_page = page_objects[0].get("name", "")
        if primary_page:
            page_var = _pascal_to_snake(primary_page)

    # Add workflow-specific methods
    if workflow_type == "auth":
        methods.append(AUTH_LOGIN_METHOD.format(page_var=page_var))
        methods.append(AUTH_LOGOUT_METHOD.format(page_var=page_var))
        methods.append(AUTH_NAVIGATE_METHOD)

    elif workflow_type == "catalog":
        methods.append(CATALOG_BROWSE_METHOD.format(page_var=page_var))
        methods.append(CATALOG_FILTER_METHOD.format(page_var=page_var))
        methods.append(CATALOG_SORT_METHOD.format(page_var=page_var))

    elif workflow_type == "cart":
        methods.append(CART_ADD_METHOD.format(page_var=page_var))

    # Add custom methods if provided
    if custom_methods:
        for method in custom_methods:
            name = method.get("name", "custom_method")
            description = method.get("description", "Custom task method.")
            params = method.get("params", "")

            if params and not params.startswith(", "):
                params = f", {params}"

            methods.append(GENERIC_TASK_METHOD.format(
                method_name=name,
                params=params,
                method_description=description
            ))

    # If no methods generated, add a placeholder
    if not methods:
        methods.append(GENERIC_TASK_METHOD.format(
            method_name="execute_workflow",
            params="",
            method_description="Execute the workflow."
        ))

    return "".join(methods)


# =============================================================================
# MAIN GENERATOR FUNCTION
# =============================================================================

def generate_task(
    task_name: str,
    page_objects: Optional[List[Dict[str, str]]] = None,
    workflow_type: Optional[str] = None,
    task_description: Optional[str] = None,
    custom_methods: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate complete Task class code matching FRAMEWORK.md patterns.

    This function uses the embedded TASK_TEMPLATE to produce code that
    exactly matches the authoritative pattern from FRAMEWORK.md Section 4.2.

    Args:
        task_name: Task class name (e.g., AuthTasks, CatalogTasks)
        page_objects: List of page object dicts with 'name' and 'import_path'
        workflow_type: Optional workflow type (auto-detected if not provided)
        task_description: Optional description for docstring
        custom_methods: Optional list of custom method definitions

    Returns:
        Complete Python task class code as string
    """
    page_objects = page_objects or []

    # Auto-detect workflow type if not provided
    detected_workflow = workflow_type or _detect_workflow_type(task_name, task_description or "")
    workflow_readable = detected_workflow.replace("_", " ").title()

    # Generate description
    description = task_description or f"{task_name} - Task module for {workflow_readable} workflows."

    # Generate each section
    page_imports = generate_page_imports(page_objects)
    page_compositions = generate_page_compositions(page_objects)
    task_methods = generate_task_methods(detected_workflow, page_objects, custom_methods)

    # Add By import if auth workflow (for logout locator)
    extra_import = ""
    if detected_workflow == "auth":
        extra_import = "\nfrom selenium.webdriver.common.by import By"

    # Assemble using the master template
    code = TASK_TEMPLATE.format(
        task_description=description,
        task_name=task_name,
        workflow_readable=workflow_readable,
        page_imports=page_imports + extra_import,
        page_compositions=page_compositions,
        task_methods=task_methods
    )

    return code


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_file_path(task_name: str, workflow: str = "common") -> str:
    """
    Get suggested file path for the generated task.

    Args:
        task_name: Task class name (PascalCase)
        workflow: Workflow/domain folder (auth, catalog, cart, etc.)

    Returns:
        Suggested file path (e.g., framework/tasks/auth/auth_tasks.py)
    """
    snake_name = _pascal_to_snake(task_name)
    return f"framework/tasks/{workflow}/{snake_name}.py"


def get_available_workflows() -> List[str]:
    """Get list of available workflow types."""
    return ["auth", "catalog", "cart", "checkout", "common"]
