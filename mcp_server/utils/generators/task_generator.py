"""
Task Generator

Generates Task class code following the validated 4-layer framework patterns.
This generator uses METADATA from POM generator to create dynamic Task methods.

METADATA-DRIVEN ARCHITECTURE:
- Accepts POM metadata (action_methods[], state_methods[])
- Generates Task methods that call actual POM methods
- No hardcoded method names - all derived from POM metadata
- Outputs Task metadata for Role generator

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
from typing import Dict, List, Optional, Any


# =============================================================================
# EMBEDDED CODE PATTERN TEMPLATE (from FRAMEWORK.md Section 4.2)
# =============================================================================

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


# =============================================================================
# DYNAMIC TASK METHOD GENERATION (from POM metadata)
# =============================================================================

def _generate_task_method_from_pom(
    method_name: str,
    pom_methods_to_call: List[Dict[str, Any]],
    page_var: str,
    description: str = ""
) -> str:
    """
    Generate a single Task method that calls POM methods.

    Args:
        method_name: Task method name (e.g., "log_in")
        pom_methods_to_call: List of POM method metadata to call
        page_var: Page object variable name (e.g., "login_page")
        description: Method description

    Returns:
        Task method code string
    """
    # Build parameter list from POM methods that need params
    task_params = []
    for pom_method in pom_methods_to_call:
        for param in pom_method.get("params", []):
            # Extract param name (before colon)
            param_name = param.split(":")[0].strip()
            if param_name and param not in task_params:
                task_params.append(param)

    params_str = ", ".join(task_params)
    if params_str:
        params_str = ", " + params_str

    # Build fluent chain of POM method calls
    pom_calls = []
    for pom_method in pom_methods_to_call:
        method_call = f".{pom_method['name']}("
        # Add arguments if method has params
        if pom_method.get("params"):
            args = [p.split(":")[0].strip() for p in pom_method["params"]]
            method_call += ", ".join(args)
        method_call += ")"
        pom_calls.append(method_call)

    # Format as fluent chain
    if pom_calls:
        fluent_chain = f"        (self.{page_var}\n"
        for i, call in enumerate(pom_calls):
            fluent_chain += f"            {call}"
            if i < len(pom_calls) - 1:
                fluent_chain += "\n"
            else:
                fluent_chain += ")\n"
    else:
        fluent_chain = f"        pass  # TODO: Add POM method calls\n"

    desc = description or f"Execute {method_name.replace('_', ' ')} operation."

    return f'''
    @autologger.automation_logger("Task")
    def {method_name}(self{params_str}) -> None:
        """
        {desc}

        NO return value - test asserts via POM state-check methods.
        """
{fluent_chain}        # NO return - test asserts via POM
'''


def generate_task_methods_from_metadata(
    pom_metadata: Dict[str, Any],
    base_url_path: str = ""
) -> tuple:
    """
    Generate Task methods dynamically from POM metadata.

    This is the key function for metadata-driven generation.
    It analyzes what POM methods exist and creates appropriate Task methods.

    Args:
        pom_metadata: Metadata from POM generator with action_methods[], state_methods[]
        base_url_path: URL path for navigation (e.g., "/index.php?controller=authentication")

    Returns:
        Tuple of (methods_code: str, task_methods_metadata: List[Dict])
    """
    methods_code = []
    task_methods_metadata = []

    page_name = pom_metadata.get("class_name", "Page")
    page_var = _pascal_to_snake(page_name)
    action_methods = pom_metadata.get("action_methods", [])
    state_methods = pom_metadata.get("state_methods", [])

    # Group action methods by type for intelligent task creation
    input_methods = [m for m in action_methods if m["name"].startswith("enter_")]
    click_methods = [m for m in action_methods if m["name"].startswith("click_")]
    select_methods = [m for m in action_methods if m["name"].startswith("select_")]

    # Generate navigate method if we have a URL path
    if base_url_path:
        nav_method = f'''
    @autologger.automation_logger("Task")
    def navigate_to_page(self) -> None:
        """Navigate to the page."""
        self.web.navigate_to(f"{{self.base_url}}{base_url_path}")
        # NO return - test asserts via POM
'''
        methods_code.append(nav_method)
        task_methods_metadata.append({
            "name": "navigate_to_page",
            "params": [],
            "calls": []
        })

    # Strategy: Create a main workflow method that chains all inputs + a submit click
    # This is the typical "fill form and submit" pattern
    if input_methods:
        # Find submit/login button if exists
        submit_methods = [m for m in click_methods if any(
            kw in m["name"].lower() for kw in ["submit", "login", "signin", "register", "save", "send"]
        )]

        # Create main form submission task
        methods_to_call = input_methods.copy()
        if submit_methods:
            methods_to_call.append(submit_methods[0])

        if methods_to_call:
            # Determine task name based on page
            if "login" in page_name.lower():
                task_name = "log_in"
                description = "Complete login operation. Single domain operation: authenticate user."
            elif "register" in page_name.lower():
                task_name = "register"
                description = "Complete registration operation."
            else:
                task_name = "submit_form"
                description = "Fill and submit the form."

            method_code = _generate_task_method_from_pom(
                method_name=task_name,
                pom_methods_to_call=methods_to_call,
                page_var=page_var,
                description=description
            )
            methods_code.append(method_code)

            # Build metadata
            task_methods_metadata.append({
                "name": task_name,
                "params": [p for m in methods_to_call for p in m.get("params", [])],
                "calls": [m["name"] for m in methods_to_call]
            })

    # Generate individual click methods for non-submit buttons
    for click_method in click_methods:
        # Skip if already used in form submission
        if any(kw in click_method["name"].lower() for kw in ["submit", "login", "signin", "register"]):
            continue

        # Create a task method for this click
        task_method_name = click_method["name"].replace("click_", "do_")
        method_code = _generate_task_method_from_pom(
            method_name=task_method_name,
            pom_methods_to_call=[click_method],
            page_var=page_var,
            description=f"Click {click_method['name'].replace('click_', '').replace('_', ' ')}."
        )
        methods_code.append(method_code)
        task_methods_metadata.append({
            "name": task_method_name,
            "params": [],
            "calls": [click_method["name"]]
        })

    # If no methods generated, create a placeholder
    if not methods_code:
        placeholder = f'''
    @autologger.automation_logger("Task")
    def execute_workflow(self) -> None:
        """
        Execute the primary workflow.

        TODO: Implement using page object methods.
        NO return value - test asserts via POM.
        """
        pass
        # NO return
'''
        methods_code.append(placeholder)
        task_methods_metadata.append({
            "name": "execute_workflow",
            "params": [],
            "calls": []
        })

    return "".join(methods_code), task_methods_metadata


# =============================================================================
# IMPORT AND COMPOSITION GENERATION
# =============================================================================

def generate_page_imports(pom_metadata_list: List[Dict[str, Any]]) -> str:
    """Generate import statements for page objects from metadata."""
    imports = []
    for pom in pom_metadata_list:
        class_name = pom.get("class_name", "")
        import_path = pom.get("import_path", "")
        if class_name and import_path:
            imports.append(f"from {import_path} import {class_name}")
    return "\n".join(imports)


def generate_page_compositions(pom_metadata_list: List[Dict[str, Any]]) -> str:
    """Generate page object composition in constructor."""
    lines = []
    for pom in pom_metadata_list:
        class_name = pom.get("class_name", "")
        if class_name:
            var_name = _pascal_to_snake(class_name)
            lines.append(f"        self.{var_name} = {class_name}(web)")
    return "\n".join(lines) + "\n" if lines else ""


# =============================================================================
# MAIN GENERATOR FUNCTIONS
# =============================================================================

def generate_task(
    task_name: str,
    pom_metadata_list: Optional[List[Dict[str, Any]]] = None,
    task_description: Optional[str] = None,
    base_url_path: str = ""
) -> str:
    """
    Generate Task class code using POM metadata (legacy interface).

    Args:
        task_name: Task class name (e.g., AuthTasks, CatalogTasks)
        pom_metadata_list: List of POM metadata dicts from Tool 3
        task_description: Optional description for docstring
        base_url_path: URL path for navigation

    Returns:
        Complete Python task class code as string
    """
    result = generate_task_with_metadata(
        task_name=task_name,
        pom_metadata_list=pom_metadata_list,
        task_description=task_description,
        base_url_path=base_url_path
    )
    return result["code"]


def generate_task_with_metadata(
    task_name: str,
    pom_metadata_list: Optional[List[Dict[str, Any]]] = None,
    task_description: Optional[str] = None,
    base_url_path: str = "",
    workflow: str = "common"
) -> Dict[str, Any]:
    """
    Generate Task class code AND metadata for downstream tools.

    This is the primary function for the metadata-passing architecture.
    It uses POM metadata to generate dynamic Task methods and outputs
    Task metadata for the Role generator.

    Args:
        task_name: Task class name (e.g., AuthTasks, CatalogTasks)
        pom_metadata_list: List of POM metadata dicts from Tool 3
        task_description: Optional description for docstring
        base_url_path: URL path for navigation
        workflow: Workflow folder for import path

    Returns:
        Dict with {code, metadata} where metadata has:
        - class_name: str
        - import_path: str
        - composed_pages: List[str]
        - task_methods: List[{name, params[], calls[]}]
    """
    pom_metadata_list = pom_metadata_list or []

    # Detect workflow type from task name
    workflow_readable = "General"
    if "auth" in task_name.lower():
        workflow_readable = "Authentication"
    elif "catalog" in task_name.lower():
        workflow_readable = "Catalog"
    elif "cart" in task_name.lower():
        workflow_readable = "Cart"

    description = task_description or f"{task_name} - Task module for {workflow_readable} workflows."

    # Generate imports and compositions from POM metadata
    page_imports = generate_page_imports(pom_metadata_list)
    page_compositions = generate_page_compositions(pom_metadata_list)

    # Generate task methods from POM metadata
    all_task_methods_code = []
    all_task_methods_metadata = []

    for pom_metadata in pom_metadata_list:
        methods_code, methods_metadata = generate_task_methods_from_metadata(
            pom_metadata=pom_metadata,
            base_url_path=base_url_path
        )
        all_task_methods_code.append(methods_code)
        all_task_methods_metadata.extend(methods_metadata)

    task_methods = "".join(all_task_methods_code) if all_task_methods_code else '''
    @autologger.automation_logger("Task")
    def execute_workflow(self) -> None:
        """Execute the workflow. TODO: Implement."""
        pass
'''

    # Assemble code using template
    code = TASK_TEMPLATE.format(
        task_description=description,
        task_name=task_name,
        workflow_readable=workflow_readable,
        page_imports=page_imports,
        page_compositions=page_compositions,
        task_methods=task_methods
    )

    # Build metadata for Role generator
    snake_name = _pascal_to_snake(task_name)
    import_path = f"tasks.{workflow}.{snake_name}"

    metadata = {
        "class_name": task_name,
        "import_path": import_path,
        "composed_pages": [p.get("class_name", "") for p in pom_metadata_list],
        "task_methods": all_task_methods_metadata
    }

    return {
        "code": code,
        "metadata": metadata
    }


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
