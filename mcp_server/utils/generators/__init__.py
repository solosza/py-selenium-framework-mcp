"""
MCP Code Generators Package

Dedicated generators for each framework layer.
Each generator embeds its layer's patterns and produces code
matching the validated 4-layer architecture.

Generators:
- page_object_generator: POMs with NO decorators, returns self
- task_generator: Tasks with @autologger("Task"), returns None
- role_generator: Roles with @autologger("Role"), returns None
- test_generator: Tests that assert via POM state-check methods
"""

# Placeholder exports - will be populated as generators are created
# from .page_object_generator import generate_page_object
# from .task_generator import generate_task
# from .role_generator import generate_role
# from .test_generator import generate_test

__all__ = [
    # "generate_page_object",
    # "generate_task",
    # "generate_role",
    # "generate_test",
]
