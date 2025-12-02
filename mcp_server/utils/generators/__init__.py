"""
MCP Code Generators Package

Dedicated generators for each framework layer.
Each generator embeds its layer's patterns and produces code
matching the validated 4-layer architecture from FRAMEWORK.md.

Generators:
- page_object_generator: POMs with NO decorators, returns self
- task_generator: Tasks with @autologger("Task"), returns None
- role_generator: Roles with @autologger("Role"), returns None
- test_generator: Tests that assert via POM state-check methods
"""

# Page Object Generator (Task B.2)
from .page_object_generator import (
    generate_page_object,
    get_file_path as get_page_file_path,
    get_generated_method_names
)

# Task Generator (Task B.3)
from .task_generator import (
    generate_task,
    get_file_path as get_task_file_path,
    get_available_workflows
)

# Role Generator (Task B.4)
from .role_generator import (
    generate_role,
    get_file_path as get_role_file_path,
    get_available_role_types
)

# Test Generator (Task B.5)
from .test_generator import (
    generate_test,
    get_file_path as get_test_file_path,
    get_pytest_markers
)

__all__ = [
    "generate_page_object",
    "get_page_file_path",
    "get_generated_method_names",
    "generate_task",
    "get_task_file_path",
    "get_available_workflows",
    "generate_role",
    "get_role_file_path",
    "get_available_role_types",
    "generate_test",
    "get_test_file_path",
    "get_pytest_markers",
]
