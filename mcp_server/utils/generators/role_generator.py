"""
Role Generator

Generates Role class code following the validated 4-layer framework patterns.
This generator uses METADATA from Task generator to create dynamic Role methods.

METADATA-DRIVEN ARCHITECTURE:
- Accepts Task metadata (task_methods[])
- Generates Role methods that call actual Task methods
- No hardcoded method names - all derived from Task metadata
- Outputs Role metadata for Test generator

EMBEDDED PATTERN RULES (from FRAMEWORK.md):
- @autologger.automation_logger("Role") on workflow methods
- @autologger.automation_logger("Role Constructor") on __init__
- Composes Task modules (instantiates in constructor)
- Workflow methods call MULTIPLE tasks in sequence
- NO return values (returns None) - tests assert via POM
- NO locators (locators only in POMs)

TEMPLATE SOURCE: FRAMEWORK.md Section 4.3 Role Layer
"""

import re
from typing import Dict, List, Optional, Any


# =============================================================================
# EMBEDDED CODE PATTERN TEMPLATE (from FRAMEWORK.md Section 4.3)
# =============================================================================
# This is the authoritative pattern that all generated Roles must match.

ROLE_TEMPLATE = '''"""
{role_description}

Roles represent user personas (e.g., Admin, Customer, Guest).
This role orchestrates complete business workflows using Task modules.
"""

from typing import Dict, Any
from interfaces.web_interface import WebInterface
from resources.utilities import autologger
{task_imports}


class {role_name}:
    """
    {role_name} - orchestrates complete business workflows.

    - @autologger("Role") on workflow methods
    - @autologger("Role Constructor") on __init__
    - Composes Task modules
    - Workflow methods call MULTIPLE tasks
    - NO return values
    - NO locators
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, {constructor_params}base_url: str):
        """
        Initialize with credentials and compose Task modules.

        Args:
            web_interface: WebInterface instance
{param_docstrings}            base_url: Application base URL
        """
        self.web = web_interface
        self.base_url = base_url
{credential_assignments}
{task_compositions}
    # ==================== WORKFLOW METHODS ====================
{workflow_methods}'''


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _pascal_to_snake(name: str) -> str:
    """Convert PascalCase to snake_case."""
    return re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()


def _detect_role_type(role_name: str, description: str = "") -> str:
    """Detect role type from name and description."""
    combined = f"{role_name} {description}".lower()

    if any(kw in combined for kw in ["guest", "anonymous", "visitor"]):
        return "guest"
    if any(kw in combined for kw in ["auth", "registered", "logged", "customer", "user"]):
        return "authenticated"
    if any(kw in combined for kw in ["admin", "administrator"]):
        return "admin"

    return "generic"


# =============================================================================
# TASK IMPORT GENERATION
# =============================================================================

def generate_task_imports(task_modules: List[Dict[str, str]]) -> str:
    """
    Generate import statements for task modules.

    Args:
        task_modules: List of dicts with 'name' and 'import_path'

    Returns:
        Import statements block
    """
    if not task_modules:
        return ""

    imports = []
    for task in task_modules:
        name = task.get("name", "")
        import_path = task.get("import_path", "")

        if name and import_path:
            imports.append(f"from {import_path} import {name}")

    return "\n".join(imports)


def generate_task_compositions(task_modules: List[Dict[str, str]]) -> str:
    """
    Generate task module composition in constructor.

    Pattern from FRAMEWORK.md:
        self.auth_tasks = AuthTasks(web_interface, base_url)

    Args:
        task_modules: List of dicts with 'name'

    Returns:
        Task composition code block
    """
    if not task_modules:
        return ""

    lines = []
    for task in task_modules:
        name = task.get("name", "")
        if name:
            # Convert AuthTasks -> auth_tasks
            var_name = _pascal_to_snake(name)
            lines.append(f"        self.{var_name} = {name}(web_interface, base_url)")

    return "\n".join(lines) + "\n" if lines else ""


# =============================================================================
# WORKFLOW METHOD TEMPLATES
# =============================================================================

# Authenticated user workflow methods (from FRAMEWORK.md Section 4.3)
AUTH_LOGIN_METHOD = '''
    @autologger.automation_logger("Role")
    def login(self) -> None:
        """
        Login workflow.

        Orchestrates: navigate + enter credentials + submit
        NO return value - test asserts via POM.
        """
        self.auth_tasks.log_in(self.email, self.password)
        # NO return
'''

AUTH_LOGOUT_METHOD = '''
    @autologger.automation_logger("Role")
    def logout(self) -> None:
        """
        Logout workflow.

        NO return value.
        """
        self.auth_tasks.log_out()
        # NO return
'''

AUTH_LOGIN_AND_ACTION_METHOD = '''
    @autologger.automation_logger("Role")
    def login_and_browse(self, category_name: str) -> None:
        """
        Login and browse category workflow.

        Orchestrates MULTIPLE task calls - this is what makes
        Role different from Task. A Role method is a complete
        user journey/story.

        Args:
            category_name: Category to browse after login

        NO return value - test asserts via POM.
        """
        self.auth_tasks.log_in(self.email, self.password)
        self.catalog_tasks.browse_category(category_name)
        # NO return - test asserts via POM state-check methods
'''

# Guest user workflow methods
GUEST_BROWSE_PRODUCTS_METHOD = '''
    @autologger.automation_logger("Role")
    def browse_products(self) -> None:
        """
        Browse products workflow (no login required).

        Navigates to product catalog and displays products.
        NO return value - test asserts via POM.
        """
        self.catalog_tasks.navigate_to_category()
        # NO return - test asserts via POM state-check methods
'''

GUEST_BROWSE_CATEGORY_METHOD = '''
    @autologger.automation_logger("Role")
    def browse_category(self, category_name: str) -> None:
        """
        Browse specific category workflow (no login required).

        Args:
            category_name: Category to browse

        NO return value - test asserts via POM.
        """
        self.catalog_tasks.browse_category(category_name)
        # NO return - test asserts via POM state-check methods
'''

GUEST_FILTER_METHOD = '''
    @autologger.automation_logger("Role")
    def browse_and_filter(self, category_name: str, size: str) -> None:
        """
        Browse category and filter by size workflow.

        Orchestrates MULTIPLE task calls.

        Args:
            category_name: Category to browse
            size: Size to filter by ("S", "M", "L")

        NO return value - test asserts via POM.
        """
        self.catalog_tasks.browse_category(category_name)
        self.catalog_tasks.filter_by_size(size)
        # NO return - test asserts via POM state-check methods
'''

# Generic workflow method template
GENERIC_WORKFLOW_METHOD = '''
    @autologger.automation_logger("Role")
    def {method_name}(self{params}) -> None:
        """
        {method_description}

        Orchestrates task calls for complete user journey.
        NO return value - test asserts via POM.
        """
        # TODO: Implement workflow using task methods
        pass
        # NO return
'''


# =============================================================================
# DYNAMIC WORKFLOW METHOD GENERATION (from Task metadata)
# =============================================================================

def _generate_workflow_method_from_task(
    method_name: str,
    task_methods_to_call: List[Dict[str, Any]],
    task_var: str,
    description: str = "",
    credentials_params: List[str] = None
) -> str:
    """
    Generate a single Role workflow method that calls Task methods.

    Args:
        method_name: Role method name (e.g., "login")
        task_methods_to_call: List of Task method metadata to call
        task_var: Task object variable name (e.g., "auth_tasks")
        description: Method description
        credentials_params: List of credential params to use (e.g., ["self.email", "self.password"])

    Returns:
        Role workflow method code string
    """
    credentials_params = credentials_params or []

    # Build parameter list from Task methods that need params (excluding credentials)
    role_params = []
    for task_method in task_methods_to_call:
        for param in task_method.get("params", []):
            # Extract param name (before colon)
            param_name = param.split(":")[0].strip()
            # Skip if it's a credential that will be provided by self
            if param_name not in ["email", "password"] and param not in role_params:
                role_params.append(param)

    params_str = ", ".join(role_params)
    if params_str:
        params_str = ", " + params_str

    # Build Task method calls
    task_calls = []
    for task_method in task_methods_to_call:
        method_call = f"self.{task_var}.{task_method['name']}("

        # Add arguments - use credentials if params match
        if task_method.get("params"):
            args = []
            for p in task_method["params"]:
                param_name = p.split(":")[0].strip()
                if param_name == "email" and "self.email" in credentials_params:
                    args.append("self.email")
                elif param_name == "password" and "self.password" in credentials_params:
                    args.append("self.password")
                else:
                    args.append(param_name)
            method_call += ", ".join(args)

        method_call += ")"
        task_calls.append(method_call)

    # Format as sequential calls
    if task_calls:
        calls_block = "\n".join([f"        {call}" for call in task_calls])
    else:
        calls_block = "        pass  # TODO: Add Task method calls"

    desc = description or f"Execute {method_name.replace('_', ' ')} workflow."

    return f'''
    @autologger.automation_logger("Role")
    def {method_name}(self{params_str}) -> None:
        """
        {desc}

        NO return value - test asserts via POM state-check methods.
        """
{calls_block}
        # NO return - test asserts via POM
'''


def generate_workflow_methods_from_metadata(
    task_metadata_list: List[Dict[str, Any]],
    role_type: str = "authenticated"
) -> tuple:
    """
    Generate Role workflow methods dynamically from Task metadata.

    This is the key function for metadata-driven generation.
    It analyzes what Task methods exist and creates appropriate Role workflows.

    Args:
        task_metadata_list: List of Task metadata dicts with task_methods[]
        role_type: Type of role (authenticated, guest, etc.)

    Returns:
        Tuple of (methods_code: str, workflow_methods_metadata: List[Dict])
    """
    methods_code = []
    workflow_methods_metadata = []

    # Use credentials for authenticated roles
    has_credentials = role_type == "authenticated"
    credentials_params = ["self.email", "self.password"] if has_credentials else []

    for task_metadata in task_metadata_list:
        task_name = task_metadata.get("class_name", "Task")
        task_var = _pascal_to_snake(task_name)
        task_methods = task_metadata.get("task_methods", [])

        # Strategy: Create a Role workflow for each Task method
        # For auth: create "login" workflow from "log_in" task
        for task_method in task_methods:
            task_method_name = task_method.get("name", "")

            # Skip navigation methods - they're internal
            if task_method_name in ["navigate_to_page"]:
                continue

            # Determine Role method name (may be different from Task)
            if task_method_name == "log_in":
                role_method_name = "login"
                description = "Login workflow. Orchestrates: navigate + enter credentials + submit."
            elif task_method_name == "log_out":
                role_method_name = "logout"
                description = "Logout workflow."
            elif task_method_name.startswith("do_"):
                role_method_name = task_method_name.replace("do_", "perform_")
                description = f"Execute {task_method_name.replace('do_', '').replace('_', ' ')} action."
            else:
                role_method_name = task_method_name
                description = f"Execute {task_method_name.replace('_', ' ')} workflow."

            method_code = _generate_workflow_method_from_task(
                method_name=role_method_name,
                task_methods_to_call=[task_method],
                task_var=task_var,
                description=description,
                credentials_params=credentials_params
            )
            methods_code.append(method_code)

            # Build metadata
            workflow_methods_metadata.append({
                "name": role_method_name,
                "params": [p for p in task_method.get("params", [])
                          if p.split(":")[0].strip() not in ["email", "password"]],
                "calls": [f"{task_var}.{task_method_name}"]
            })

    # If no methods generated, add a placeholder
    if not methods_code:
        placeholder = '''
    @autologger.automation_logger("Role")
    def execute_workflow(self) -> None:
        """
        Execute the primary workflow for this role.

        TODO: Implement using task methods.
        NO return value - test asserts via POM.
        """
        pass
        # NO return
'''
        methods_code.append(placeholder)
        workflow_methods_metadata.append({
            "name": "execute_workflow",
            "params": [],
            "calls": []
        })

    return "".join(methods_code), workflow_methods_metadata


def generate_workflow_methods(
    role_type: str,
    task_modules: List[Dict[str, str]],
    custom_workflows: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate workflow methods based on role type.

    Args:
        role_type: Type of role (guest, authenticated, admin)
        task_modules: List of task modules (to determine available tasks)
        custom_workflows: Optional list of custom workflow definitions

    Returns:
        Workflow methods code block
    """
    methods = []

    # Determine available task types from modules
    has_auth_tasks = any("auth" in t.get("name", "").lower() for t in task_modules)
    has_catalog_tasks = any("catalog" in t.get("name", "").lower() for t in task_modules)

    # Add role-specific methods
    if role_type == "authenticated":
        if has_auth_tasks:
            methods.append(AUTH_LOGIN_METHOD)
            methods.append(AUTH_LOGOUT_METHOD)

        if has_auth_tasks and has_catalog_tasks:
            methods.append(AUTH_LOGIN_AND_ACTION_METHOD)

    elif role_type == "guest":
        if has_catalog_tasks:
            methods.append(GUEST_BROWSE_PRODUCTS_METHOD)
            methods.append(GUEST_BROWSE_CATEGORY_METHOD)
            methods.append(GUEST_FILTER_METHOD)

    # Add custom workflows if provided
    if custom_workflows:
        for workflow in custom_workflows:
            name = workflow.get("name", "custom_workflow")
            description = workflow.get("description", "Custom workflow method.")
            params = workflow.get("params", "")

            if params and not params.startswith(", "):
                params = f", {params}"

            methods.append(GENERIC_WORKFLOW_METHOD.format(
                method_name=name,
                params=params,
                method_description=description
            ))

    # If no methods generated, add a placeholder
    if not methods:
        methods.append(GENERIC_WORKFLOW_METHOD.format(
            method_name="execute_workflow",
            params="",
            method_description="Execute the primary workflow for this role."
        ))

    return "".join(methods)


# =============================================================================
# TASK IMPORT/COMPOSITION FROM METADATA
# =============================================================================

def generate_task_imports_from_metadata(task_metadata_list: List[Dict[str, Any]]) -> str:
    """Generate import statements for Task modules from metadata."""
    imports = []
    for task in task_metadata_list:
        class_name = task.get("class_name", "")
        import_path = task.get("import_path", "")
        if class_name and import_path:
            imports.append(f"from {import_path} import {class_name}")
    return "\n".join(imports)


def generate_task_compositions_from_metadata(task_metadata_list: List[Dict[str, Any]]) -> str:
    """Generate Task module composition in constructor from metadata."""
    lines = []
    for task in task_metadata_list:
        class_name = task.get("class_name", "")
        if class_name:
            var_name = _pascal_to_snake(class_name)
            lines.append(f"        self.{var_name} = {class_name}(web_interface, base_url)")
    return "\n".join(lines) + "\n" if lines else ""


# =============================================================================
# MAIN GENERATOR FUNCTIONS
# =============================================================================

def generate_role(
    role_name: str,
    task_modules: Optional[List[Dict[str, str]]] = None,
    role_type: Optional[str] = None,
    role_description: Optional[str] = None,
    requires_credentials: bool = True,
    custom_workflows: Optional[List[Dict[str, str]]] = None
) -> str:
    """
    Generate complete Role class code matching FRAMEWORK.md patterns (legacy interface).

    This function uses the embedded ROLE_TEMPLATE to produce code that
    exactly matches the authoritative pattern from FRAMEWORK.md Section 4.3.

    Args:
        role_name: Role class name (e.g., AuthenticatedUser, GuestUser)
        task_modules: List of task module dicts with 'name' and 'import_path'
        role_type: Optional role type (auto-detected if not provided)
        role_description: Optional description for docstring
        requires_credentials: Whether role needs user_data with credentials (default: True)
        custom_workflows: Optional list of custom workflow definitions

    Returns:
        Complete Python role class code as string
    """
    task_modules = task_modules or []

    # Auto-detect role type if not provided
    detected_type = role_type or _detect_role_type(role_name, role_description or "")

    # Guest roles don't need credentials
    if detected_type == "guest":
        requires_credentials = False

    # Generate description
    description = role_description or f"{role_name} - Role for orchestrating business workflows."

    # Generate constructor parameters and assignments
    if requires_credentials:
        constructor_params = "user_data: Dict[str, Any], "
        param_docstrings = "            user_data: User data dict with email/password\n"
        credential_assignments = '''        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')

        # Validate required credentials
        if not self.email or not self.password:
            raise ValueError(f"{role_name} requires email and password in user_data")
'''
    else:
        constructor_params = ""
        param_docstrings = ""
        credential_assignments = ""

    # Generate each section
    task_imports = generate_task_imports(task_modules)
    task_compositions = generate_task_compositions(task_modules)
    workflow_methods = generate_workflow_methods(detected_type, task_modules, custom_workflows)

    # Fix the f-string in credential assignments
    credential_assignments = credential_assignments.replace("{role_name}", role_name)

    # Assemble using the master template
    code = ROLE_TEMPLATE.format(
        role_description=description,
        role_name=role_name,
        task_imports=task_imports,
        constructor_params=constructor_params,
        param_docstrings=param_docstrings,
        credential_assignments=credential_assignments,
        task_compositions=task_compositions,
        workflow_methods=workflow_methods
    )

    return code


def generate_role_with_metadata(
    role_name: str,
    task_metadata_list: Optional[List[Dict[str, Any]]] = None,
    role_type: Optional[str] = None,
    role_description: Optional[str] = None,
    requires_credentials: bool = True
) -> Dict[str, Any]:
    """
    Generate Role class code AND metadata for downstream tools.

    This is the primary function for the metadata-passing architecture.
    It uses Task metadata to generate dynamic Role methods and outputs
    Role metadata for the Test generator.

    Args:
        role_name: Role class name (e.g., RegisteredUser, GuestUser)
        task_metadata_list: List of Task metadata dicts from Tool 4
        role_type: Optional role type (auto-detected if not provided)
        role_description: Optional description for docstring
        requires_credentials: Whether role needs user_data with credentials

    Returns:
        Dict with {code, metadata} where metadata has:
        - class_name: str
        - import_path: str
        - composed_tasks: List[str]
        - workflow_methods: List[{name, params[], calls[]}]
    """
    task_metadata_list = task_metadata_list or []

    # Auto-detect role type if not provided
    detected_type = role_type or _detect_role_type(role_name, role_description or "")

    # Guest roles don't need credentials
    if detected_type == "guest":
        requires_credentials = False

    # Generate description
    description = role_description or f"{role_name} - Role for orchestrating business workflows."

    # Generate constructor parameters and assignments
    if requires_credentials:
        constructor_params = "user_data: Dict[str, Any], "
        param_docstrings = "            user_data: User data dict with email/password\n"
        credential_assignments = '''        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')

        # Validate required credentials
        if not self.email or not self.password:
            raise ValueError(f"{role_name} requires email and password in user_data")
'''
    else:
        constructor_params = ""
        param_docstrings = ""
        credential_assignments = ""

    # Fix the f-string in credential assignments
    credential_assignments = credential_assignments.replace("{role_name}", role_name)

    # Generate imports and compositions from Task metadata
    task_imports = generate_task_imports_from_metadata(task_metadata_list)
    task_compositions = generate_task_compositions_from_metadata(task_metadata_list)

    # Generate workflow methods from Task metadata
    workflow_methods_code, workflow_methods_metadata = generate_workflow_methods_from_metadata(
        task_metadata_list=task_metadata_list,
        role_type=detected_type
    )

    # Assemble code using template
    code = ROLE_TEMPLATE.format(
        role_description=description,
        role_name=role_name,
        task_imports=task_imports,
        constructor_params=constructor_params,
        param_docstrings=param_docstrings,
        credential_assignments=credential_assignments,
        task_compositions=task_compositions,
        workflow_methods=workflow_methods_code
    )

    # Build metadata for Test generator
    snake_name = _pascal_to_snake(role_name)
    import_path = f"roles.{snake_name}"

    metadata = {
        "class_name": role_name,
        "import_path": import_path,
        "composed_tasks": [t.get("class_name", "") for t in task_metadata_list],
        "workflow_methods": workflow_methods_metadata
    }

    return {
        "code": code,
        "metadata": metadata
    }


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_file_path(role_name: str) -> str:
    """
    Get suggested file path for the generated role.

    Args:
        role_name: Role class name (PascalCase)

    Returns:
        Suggested file path (e.g., framework/roles/authenticated_user.py)
    """
    snake_name = _pascal_to_snake(role_name)
    return f"framework/roles/{snake_name}.py"


def get_available_role_types() -> List[str]:
    """Get list of available role types."""
    return ["guest", "authenticated", "admin", "generic"]
