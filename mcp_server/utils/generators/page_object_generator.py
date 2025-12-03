"""
Page Object Generator

Generates Page Object Model (POM) code following the validated 4-layer framework patterns.
This generator embeds the authoritative code pattern template from FRAMEWORK.md Section 4.1.

EMBEDDED PATTERN RULES (from FRAMEWORK.md):
- NO decorators on any methods
- Locators as class constants (UPPER_SNAKE_CASE)
- Atomic methods (one UI action per method)
- Return self for fluent chaining
- State-check methods for test assertions (return bool/value)
- Composes WebInterface (NO inheritance)

TEMPLATE SOURCE: FRAMEWORK.md Section 4.1 Page Object Layer
"""

import re
from typing import Dict, List, Optional


# =============================================================================
# EMBEDDED CODE PATTERN TEMPLATE (from FRAMEWORK.md Section 4.1)
# =============================================================================
# This is the authoritative pattern that all generated POMs must match.
# The template shows the exact structure, comments, and code style.

PAGE_OBJECT_TEMPLATE = '''"""
{page_description}

Page Object representing a single page in the application.
Provides atomic UI interactions via WebInterface composition.
"""

from selenium.webdriver.common.by import By
from interfaces.web_interface import WebInterface


class {page_name}:
    """
    Page Object for {page_name_readable}.

    - NO decorators
    - Locators as class constants
    - Atomic methods (one UI action)
    - Return self for chaining
    - State-check methods for assertions
    """

    def __init__(self, web: WebInterface):
        """Compose WebInterface - NO inheritance."""
        self.web = web

    # ==================== LOCATORS (Class Constants) ====================
{locators_block}
    # ==================== ATOMIC METHODS (One UI Action) ====================
{action_methods_block}
    # ==================== STATE-CHECK METHODS (For Assertions) ====================
{state_check_methods_block}'''


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _pascal_to_snake(name: str) -> str:
    """Convert PascalCase to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def _pascal_to_readable(name: str) -> str:
    """Convert PascalCase to readable string (e.g., ProductListPage -> Product List Page)."""
    return re.sub(r'(?<!^)(?=[A-Z])', ' ', name)


def _determine_by_type(locator: str) -> str:
    """
    Determine Selenium By type from selector syntax.

    Args:
        locator: CSS selector or XPath

    Returns:
        By type string (CSS_SELECTOR, XPATH, ID, etc.)
    """
    locator = locator.strip()

    if locator.startswith("//") or locator.startswith("(//"):
        return "XPATH"

    # Default to CSS_SELECTOR for consistency
    return "CSS_SELECTOR"


# =============================================================================
# LOCATOR GENERATION
# =============================================================================

def generate_locators_block(elements: List[Dict[str, str]]) -> str:
    """
    Generate locator constants block matching FRAMEWORK.md pattern.

    Pattern from FRAMEWORK.md:
        EMAIL_INPUT = (By.ID, "email")
        PASSWORD_INPUT = (By.ID, "password")
        SUBMIT_BUTTON = (By.ID, "submit-login")

    Args:
        elements: List of dicts with 'name'/'suggested_name' and 'locator'

    Returns:
        Locator code block with proper indentation
    """
    if not elements:
        return "    # Add locators as needed\n    pass\n"

    lines = []
    seen_names = set()  # Track unique locator names
    seen_locators = set()  # Track unique locator values

    for elem in elements:
        name = (elem.get("suggested_name") or elem.get("name", "")).upper()
        locator = elem.get("locator", "")

        if not name or not locator:
            continue

        # Skip duplicates - same name or same locator value
        if name in seen_names or locator in seen_locators:
            continue

        seen_names.add(name)
        seen_locators.add(locator)

        by_type = _determine_by_type(locator)
        lines.append(f'    {name} = (By.{by_type}, "{locator}")')

    return "\n".join(lines) + "\n" if lines else "    pass\n"


# =============================================================================
# ACTION METHOD GENERATION
# =============================================================================

# Method templates matching FRAMEWORK.md Section 4.1 style
INPUT_METHOD_TEMPLATE = '''
    def enter_{method_name}(self, {param_name}: str) -> "{page_name}":
        """Enter {readable_name}."""
        self.web.type_text(*self.{locator_name}, text={param_name})
        return self  # Fluent API
'''

BUTTON_METHOD_TEMPLATE = '''
    def click_{method_name}(self) -> "{page_name}":
        """Click {readable_name} button."""
        self.web.click(*self.{locator_name})
        return self
'''

LINK_METHOD_TEMPLATE = '''
    def click_{method_name}(self) -> "{page_name}":
        """Click {readable_name} link."""
        self.web.click(*self.{locator_name})
        return self
'''

SELECT_METHOD_TEMPLATE = '''
    def select_{method_name}(self, value: str) -> "{page_name}":
        """Select option from {readable_name} dropdown."""
        self.web.select_dropdown_by_value(*self.{locator_name}, option_value=value)
        return self
'''

CHECKBOX_METHOD_TEMPLATE = '''
    def check_{method_name}(self) -> "{page_name}":
        """Check {readable_name} checkbox."""
        if not self.web.is_element_selected(*self.{locator_name}):
            self.web.click(*self.{locator_name})
        return self

    def uncheck_{method_name}(self) -> "{page_name}":
        """Uncheck {readable_name} checkbox."""
        if self.web.is_element_selected(*self.{locator_name}):
            self.web.click(*self.{locator_name})
        return self
'''


def generate_action_methods_block(
    elements: List[Dict[str, str]],
    page_name: str
) -> str:
    """
    Generate action methods block matching FRAMEWORK.md pattern.

    Pattern from FRAMEWORK.md:
        def enter_email(self, email: str) -> "LoginPage":
            \"\"\"Enter email address.\"\"\"
            self.web.type_text(*self.EMAIL_INPUT, text=email)
            return self  # Fluent API

    Args:
        elements: List of element dicts with name, locator, element_type
        page_name: Page class name for type hints

    Returns:
        Action methods code block
    """
    if not elements:
        return ""

    methods = []
    seen_method_names = set()  # Track unique method names
    seen_locators = set()  # Track unique locator values

    for elem in elements:
        name = (elem.get("suggested_name") or elem.get("name", ""))
        elem_type = elem.get("element_type", "")
        locator = elem.get("locator", "")

        if not name or not elem_type:
            continue

        locator_name = name.upper()
        method_name = name.lower()
        readable_name = name.replace("_", " ").lower()

        # Skip duplicates - same method name or same locator value
        if method_name in seen_method_names or locator in seen_locators:
            continue

        seen_method_names.add(method_name)
        if locator:
            seen_locators.add(locator)

        # Determine appropriate parameter name for inputs
        param_name = method_name
        if "email" in method_name:
            param_name = "email"
        elif "password" in method_name or "passwd" in method_name:
            param_name = "password"
        elif "text" in method_name or "input" in method_name:
            param_name = "text"

        if elem_type == "inputs":
            methods.append(INPUT_METHOD_TEMPLATE.format(
                method_name=method_name,
                param_name=param_name,
                page_name=page_name,
                locator_name=locator_name,
                readable_name=readable_name
            ))

        elif elem_type == "buttons":
            methods.append(BUTTON_METHOD_TEMPLATE.format(
                method_name=method_name,
                page_name=page_name,
                locator_name=locator_name,
                readable_name=readable_name
            ))

        elif elem_type == "links":
            methods.append(LINK_METHOD_TEMPLATE.format(
                method_name=method_name,
                page_name=page_name,
                locator_name=locator_name,
                readable_name=readable_name
            ))

        elif elem_type == "selects":
            methods.append(SELECT_METHOD_TEMPLATE.format(
                method_name=method_name,
                page_name=page_name,
                locator_name=locator_name,
                readable_name=readable_name
            ))

        elif elem_type == "checkboxes":
            methods.append(CHECKBOX_METHOD_TEMPLATE.format(
                method_name=method_name,
                page_name=page_name,
                locator_name=locator_name,
                readable_name=readable_name
            ))

    return "".join(methods)


# =============================================================================
# STATE-CHECK METHOD GENERATION
# =============================================================================

# Base state-check methods (always included)
BASE_STATE_CHECK_TEMPLATE = '''
    def is_page_loaded(self) -> bool:
        """Check if page is loaded."""
        # TODO: Replace with page-specific element check
        return True
'''

# Auth workflow state-check methods (from FRAMEWORK.md Section 4.1)
# Uses inline locators for common elements not in user-provided elements
AUTH_STATE_CHECK_TEMPLATE = '''
    def is_logged_in(self) -> bool:
        """Check if user is logged in (logout link visible)."""
        logout_locator = (By.CSS_SELECTOR, ".logout")
        return self.web.is_element_displayed(*logout_locator, timeout=5)

    def is_logged_out(self) -> bool:
        """Check if user is logged out (sign in link visible)."""
        signin_locator = (By.CSS_SELECTOR, ".login")
        return self.web.is_element_displayed(*signin_locator, timeout=5)

    def has_error_message(self) -> bool:
        """Check if error message is displayed."""
        error_locator = (By.CSS_SELECTOR, ".alert-danger")
        return self.web.is_element_displayed(*error_locator, timeout=3)

    def get_error_message(self) -> str:
        """Get error message text."""
        error_locator = (By.CSS_SELECTOR, ".alert-danger")
        if not self.web.is_element_displayed(*error_locator, timeout=2):
            return ""
        return self.web.get_text(*error_locator)

    def is_page_loaded(self) -> bool:
        """Check if login page is loaded."""
        # Check for presence of email input field
        email_locator = (By.CSS_SELECTOR, "#email")
        return self.web.is_element_displayed(*email_locator, timeout=5)
'''

# Catalog workflow state-check methods
# Uses inline locators for Automation Practice site
CATALOG_STATE_CHECK_TEMPLATE = '''
    def is_page_loaded(self) -> bool:
        """Check if product list page is loaded."""
        product_list_locator = (By.CSS_SELECTOR, "ul.product_list")
        return self.web.is_element_displayed(*product_list_locator, timeout=10)

    def has_products(self) -> bool:
        """Check if any products are displayed."""
        return self.get_product_count() > 0

    def get_product_count(self) -> int:
        """Get number of products displayed."""
        product_items_locator = (By.CSS_SELECTOR, "ul.product_list li.ajax_block_product")
        products = self.web.find_elements(*product_items_locator)
        return len(products)

    def get_product_names(self) -> list:
        """Get all product names on the page."""
        product_items_locator = (By.CSS_SELECTOR, "ul.product_list li.ajax_block_product")
        product_name_locator = (By.CSS_SELECTOR, ".product-name")
        products = self.web.find_elements(*product_items_locator)
        names = []
        for product in products:
            name_elem = product.find_element(*product_name_locator)
            names.append(name_elem.text.strip())
        return names
'''

# Cart workflow state-check methods
# Uses inline locators for Automation Practice site
CART_STATE_CHECK_TEMPLATE = '''
    def is_page_loaded(self) -> bool:
        """Check if cart page is loaded."""
        cart_summary_locator = (By.CSS_SELECTOR, "#cart_summary")
        return self.web.is_element_displayed(*cart_summary_locator, timeout=10)

    def has_items(self) -> bool:
        """Check if cart has items."""
        return self.get_item_count() > 0

    def get_item_count(self) -> int:
        """Get number of items in cart."""
        cart_items_locator = (By.CSS_SELECTOR, "#cart_summary tbody tr")
        items = self.web.find_elements(*cart_items_locator)
        return len(items)

    def is_cart_empty(self) -> bool:
        """Check if cart is empty."""
        return self.get_item_count() == 0
'''


def generate_state_check_methods_block(workflow_type: Optional[str] = None) -> str:
    """
    Generate state-check methods block matching FRAMEWORK.md pattern.

    Pattern from FRAMEWORK.md Section 4.1:
        def is_logged_in(self) -> bool:
            \"\"\"Check if user is logged in (logout link visible).\"\"\"
            return self.web.is_element_displayed(*self.LOGOUT_LINK, timeout=5)

    Args:
        workflow_type: Optional workflow type (auth, catalog, cart)

    Returns:
        State-check methods code block
    """
    if workflow_type == "auth":
        return AUTH_STATE_CHECK_TEMPLATE
    elif workflow_type == "catalog":
        return CATALOG_STATE_CHECK_TEMPLATE
    elif workflow_type == "cart":
        return CART_STATE_CHECK_TEMPLATE
    else:
        return BASE_STATE_CHECK_TEMPLATE


# =============================================================================
# METADATA GENERATION
# =============================================================================

def _build_locator_metadata(elements: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """
    Build metadata for locators from elements.

    Returns:
        List of locator metadata dicts with {name, by, value}
    """
    locators = []
    seen_names = set()
    seen_values = set()

    for elem in elements:
        name = (elem.get("suggested_name") or elem.get("name", "")).upper()
        locator = elem.get("locator", "")

        if not name or not locator:
            continue
        if name in seen_names or locator in seen_values:
            continue

        seen_names.add(name)
        seen_values.add(locator)

        by_type = _determine_by_type(locator)
        locators.append({
            "name": name,
            "by": by_type,
            "value": locator
        })

    return locators


def _build_action_methods_metadata(
    elements: List[Dict[str, str]],
    page_name: str
) -> List[Dict[str, any]]:
    """
    Build metadata for action methods from elements.

    Returns:
        List of method metadata dicts with {name, params[], returns, element_type}
    """
    methods = []
    seen_method_names = set()
    seen_locators = set()

    for elem in elements:
        name = (elem.get("suggested_name") or elem.get("name", ""))
        elem_type = elem.get("element_type", "")
        locator = elem.get("locator", "")

        if not name or not elem_type:
            continue

        method_name_base = name.lower()

        # Skip duplicates
        if method_name_base in seen_method_names or locator in seen_locators:
            continue

        seen_method_names.add(method_name_base)
        if locator:
            seen_locators.add(locator)

        # Determine parameter name for inputs
        param_name = method_name_base
        if "email" in method_name_base:
            param_name = "email"
        elif "password" in method_name_base or "passwd" in method_name_base:
            param_name = "password"
        elif "text" in method_name_base or "input" in method_name_base:
            param_name = "text"

        if elem_type == "inputs":
            methods.append({
                "name": f"enter_{method_name_base}",
                "params": [f"{param_name}: str"],
                "returns": "self",
                "element_type": elem_type,
                "locator_name": name.upper()
            })

        elif elem_type == "buttons":
            methods.append({
                "name": f"click_{method_name_base}",
                "params": [],
                "returns": "self",
                "element_type": elem_type,
                "locator_name": name.upper()
            })

        elif elem_type == "links":
            methods.append({
                "name": f"click_{method_name_base}",
                "params": [],
                "returns": "self",
                "element_type": elem_type,
                "locator_name": name.upper()
            })

        elif elem_type == "selects":
            methods.append({
                "name": f"select_{method_name_base}",
                "params": ["value: str"],
                "returns": "self",
                "element_type": elem_type,
                "locator_name": name.upper()
            })

        elif elem_type == "checkboxes":
            methods.append({
                "name": f"check_{method_name_base}",
                "params": [],
                "returns": "self",
                "element_type": elem_type,
                "locator_name": name.upper()
            })
            methods.append({
                "name": f"uncheck_{method_name_base}",
                "params": [],
                "returns": "self",
                "element_type": elem_type,
                "locator_name": name.upper()
            })

    return methods


def _build_state_methods_metadata(workflow_type: Optional[str] = None) -> List[Dict[str, any]]:
    """
    Build metadata for state-check methods based on workflow type.

    Returns:
        List of state method metadata dicts with {name, params[], returns}
    """
    methods = []

    if workflow_type == "auth":
        methods = [
            {"name": "is_logged_in", "params": [], "returns": "bool"},
            {"name": "is_logged_out", "params": [], "returns": "bool"},
            {"name": "has_error_message", "params": [], "returns": "bool"},
            {"name": "get_error_message", "params": [], "returns": "str"},
            {"name": "is_page_loaded", "params": [], "returns": "bool"},
        ]
    elif workflow_type == "catalog":
        methods = [
            {"name": "is_page_loaded", "params": [], "returns": "bool"},
            {"name": "has_products", "params": [], "returns": "bool"},
            {"name": "get_product_count", "params": [], "returns": "int"},
            {"name": "get_product_names", "params": [], "returns": "list"},
        ]
    elif workflow_type == "cart":
        methods = [
            {"name": "is_page_loaded", "params": [], "returns": "bool"},
            {"name": "has_items", "params": [], "returns": "bool"},
            {"name": "get_item_count", "params": [], "returns": "int"},
            {"name": "is_cart_empty", "params": [], "returns": "bool"},
        ]
    else:
        methods = [
            {"name": "is_page_loaded", "params": [], "returns": "bool"},
        ]

    return methods


# =============================================================================
# MAIN GENERATOR FUNCTION
# =============================================================================

def generate_page_object(
    page_name: str,
    elements: Optional[List[Dict[str, str]]] = None,
    workflow_type: Optional[str] = None,
    page_description: Optional[str] = None
) -> str:
    """
    Generate complete Page Object class code matching FRAMEWORK.md patterns.

    This function uses the embedded PAGE_OBJECT_TEMPLATE to produce code that
    exactly matches the authoritative pattern from FRAMEWORK.md Section 4.1.

    Args:
        page_name: Page class name (e.g., ProductListPage, LoginPage)
        elements: List of element dicts with name, locator, element_type
        workflow_type: Optional workflow type (auth, catalog, cart, checkout)
        page_description: Optional description for docstring

    Returns:
        Complete Python page object code as string
    """
    elements = elements or []
    description = page_description or f"{page_name} - Page Object Model"
    readable_name = _pascal_to_readable(page_name)

    # Generate each block using embedded templates
    locators_block = generate_locators_block(elements)
    action_methods_block = generate_action_methods_block(elements, page_name)
    state_check_methods_block = generate_state_check_methods_block(workflow_type)

    # Assemble using the master template
    code = PAGE_OBJECT_TEMPLATE.format(
        page_description=description,
        page_name=page_name,
        page_name_readable=readable_name,
        locators_block=locators_block,
        action_methods_block=action_methods_block,
        state_check_methods_block=state_check_methods_block
    )

    return code


def generate_page_object_with_metadata(
    page_name: str,
    elements: Optional[List[Dict[str, str]]] = None,
    workflow_type: Optional[str] = None,
    page_description: Optional[str] = None,
    workflow: str = "common"
) -> Dict[str, any]:
    """
    Generate Page Object code AND metadata for downstream tools.

    This is the primary function for the metadata-passing architecture.
    It returns both the generated code and structured metadata that
    Tool 4 (Task generator) will use to know what POM methods exist.

    Args:
        page_name: Page class name (e.g., ProductListPage, LoginPage)
        elements: List of element dicts with name, locator, element_type
        workflow_type: Optional workflow type (auth, catalog, cart, checkout)
        page_description: Optional description for docstring
        workflow: Workflow folder for import path (e.g., "auth", "catalog")

    Returns:
        Dict with {code, metadata} where metadata has:
        - class_name: str
        - import_path: str
        - locators: List[{name, by, value}]
        - action_methods: List[{name, params[], returns, element_type, locator_name}]
        - state_methods: List[{name, params[], returns}]
    """
    elements = elements or []

    # Generate the code
    code = generate_page_object(
        page_name=page_name,
        elements=elements,
        workflow_type=workflow_type,
        page_description=page_description
    )

    # Build metadata
    snake_name = _pascal_to_snake(page_name)
    import_path = f"pages.{workflow}.{snake_name}"

    metadata = {
        "class_name": page_name,
        "import_path": import_path,
        "locators": _build_locator_metadata(elements),
        "action_methods": _build_action_methods_metadata(elements, page_name),
        "state_methods": _build_state_methods_metadata(workflow_type)
    }

    return {
        "code": code,
        "metadata": metadata
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_generated_method_names(elements: List[Dict[str, str]]) -> List[str]:
    """
    Get list of method names that will be generated for given elements.

    Useful for Task generator to know what POM methods are available.

    Args:
        elements: List of element dicts

    Returns:
        List of method names
    """
    methods = []

    for elem in elements:
        name = (elem.get("suggested_name") or elem.get("name", "")).lower()
        elem_type = elem.get("element_type", "")

        if not name or not elem_type:
            continue

        if elem_type == "inputs":
            methods.append(f"enter_{name}")
        elif elem_type in ("buttons", "links"):
            methods.append(f"click_{name}")
        elif elem_type == "selects":
            methods.append(f"select_{name}")
        elif elem_type == "checkboxes":
            methods.append(f"check_{name}")
            methods.append(f"uncheck_{name}")

    return methods


def get_file_path(page_name: str, workflow: str = "common") -> str:
    """
    Get suggested file path for the generated page object.

    Args:
        page_name: Page class name (PascalCase)
        workflow: Workflow/domain folder (auth, catalog, cart, etc.)

    Returns:
        Suggested file path (e.g., framework/pages/auth/login_page.py)
    """
    snake_name = _pascal_to_snake(page_name)
    return f"framework/pages/{workflow}/{snake_name}.py"
