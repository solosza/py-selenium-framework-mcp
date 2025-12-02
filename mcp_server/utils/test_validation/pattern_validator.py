"""
Test Validation Script

Validates generated code matches FRAMEWORK.md architecture patterns.
Each layer has specific rules that must be followed.

Validation Rules (from FRAMEWORK.md):
- POM: NO decorators, returns self, locators as UPPER_SNAKE constants, has state-checks
- Task: HAS @autologger("Task") decorator, returns None, NO locators
- Role: HAS @autologger("Role") decorator, returns None, composes tasks
- Test: HAS @autologger("Test") decorator, asserts via POM, single role call

Usage:
    python mcp_server/utils/test_validation/pattern_validator.py [file_or_directory]
    python -m pytest mcp_server/utils/test_validation/pattern_validator.py -v
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Add parent paths for imports (mcp_server/ directory)
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


# =============================================================================
# AST HELPERS
# =============================================================================

def parse_file(file_path: str) -> Optional[ast.Module]:
    """Parse Python file to AST."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return ast.parse(f.read())
    except (SyntaxError, FileNotFoundError) as e:
        print(f"Error parsing {file_path}: {e}")
        return None


def get_classes(tree: ast.Module) -> List[ast.ClassDef]:
    """Get all class definitions from AST."""
    return [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]


def get_methods(class_def: ast.ClassDef) -> List[ast.FunctionDef]:
    """Get all method definitions from class."""
    return [node for node in class_def.body if isinstance(node, ast.FunctionDef)]


def has_decorator(func: ast.FunctionDef, decorator_name: str) -> bool:
    """Check if function has a specific decorator (partial match)."""
    for decorator in func.decorator_list:
        decorator_str = ast.unparse(decorator)
        if decorator_name in decorator_str:
            return True
    return False


def get_return_type(func: ast.FunctionDef) -> Optional[str]:
    """Get return type annotation if present."""
    if func.returns:
        return ast.unparse(func.returns)
    return None


def returns_self(func: ast.FunctionDef) -> bool:
    """Check if function returns self (for fluent chaining)."""
    for node in ast.walk(func):
        if isinstance(node, ast.Return) and node.value:
            if isinstance(node.value, ast.Name) and node.value.id == "self":
                return True
    return False


def returns_none_or_nothing(func: ast.FunctionDef) -> bool:
    """Check if function returns None or has no return statement."""
    has_return = False
    for node in ast.walk(func):
        if isinstance(node, ast.Return):
            has_return = True
            if node.value is not None:
                # Has return value (not None literal)
                if isinstance(node.value, ast.Constant) and node.value.value is None:
                    continue  # return None is ok
                return False
    return True  # No return or only return None


def has_locators(func: ast.FunctionDef) -> bool:
    """Check if function contains locator definitions (By.*)."""
    source = ast.unparse(func)
    return bool(re.search(r"By\.\w+", source))


def get_class_attributes(class_def: ast.ClassDef) -> List[str]:
    """Get class-level attribute names (for locator constants)."""
    attrs = []
    for node in class_def.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    attrs.append(target.id)
    return attrs


# =============================================================================
# PAGE OBJECT VALIDATION
# =============================================================================

def validate_page_object(file_path: str) -> Dict[str, List[str]]:
    """
    Validate Page Object matches FRAMEWORK.md patterns.

    Rules:
    - NO decorators on any methods
    - Action methods return self
    - Locators defined as UPPER_SNAKE class constants
    - Has state-check methods (is_*, has_*, get_*)
    """
    errors = []
    warnings = []

    tree = parse_file(file_path)
    if not tree:
        return {"errors": [f"Could not parse {file_path}"], "warnings": []}

    classes = get_classes(tree)
    if not classes:
        return {"errors": ["No class found"], "warnings": []}

    for cls in classes:
        if cls.name.startswith("_"):
            continue

        methods = get_methods(cls)
        attrs = get_class_attributes(cls)

        # Check for UPPER_SNAKE locator constants
        upper_attrs = [a for a in attrs if a.isupper() or (a.upper() == a and "_" in a)]
        if not upper_attrs:
            warnings.append(f"No UPPER_SNAKE locator constants found in {cls.name}")

        has_state_check = False

        for method in methods:
            if method.name == "__init__":
                continue

            # Rule: NO decorators on POM methods
            if method.decorator_list:
                decorator_names = [ast.unparse(d) for d in method.decorator_list]
                errors.append(f"POM method '{method.name}' has decorators: {decorator_names}")

            # Check for state-check methods
            if method.name.startswith(("is_", "has_", "get_")):
                has_state_check = True
            else:
                # Action methods should return self
                if not returns_self(method):
                    # Skip if it's a state check or utility
                    if not method.name.startswith("_"):
                        warnings.append(f"Action method '{method.name}' doesn't return self")

        if not has_state_check:
            warnings.append(f"No state-check methods (is_*, has_*, get_*) found in {cls.name}")

    return {"errors": errors, "warnings": warnings}


# =============================================================================
# TASK VALIDATION
# =============================================================================

def validate_task(file_path: str) -> Dict[str, List[str]]:
    """
    Validate Task matches FRAMEWORK.md patterns.

    Rules:
    - HAS @autologger("Task") decorator on workflow methods
    - NO decorator on __init__
    - Returns None (no return values)
    - NO locators (By.*) in code
    """
    errors = []
    warnings = []

    tree = parse_file(file_path)
    if not tree:
        return {"errors": [f"Could not parse {file_path}"], "warnings": []}

    classes = get_classes(tree)
    if not classes:
        return {"errors": ["No class found"], "warnings": []}

    for cls in classes:
        if cls.name.startswith("_"):
            continue

        methods = get_methods(cls)

        for method in methods:
            if method.name.startswith("_") and method.name != "__init__":
                continue

            if method.name == "__init__":
                # Constructor should NOT have decorator
                if has_decorator(method, "autologger"):
                    errors.append("Task __init__ should NOT have @autologger decorator")
            else:
                # Workflow methods MUST have decorator
                if not has_decorator(method, "autologger"):
                    errors.append(f"Task method '{method.name}' missing @autologger decorator")
                elif not has_decorator(method, '"Task"') and not has_decorator(method, "'Task'"):
                    warnings.append(f"Task method '{method.name}' should use @autologger('Task')")

                # Must return None
                if not returns_none_or_nothing(method):
                    errors.append(f"Task method '{method.name}' should return None")

                # No locators
                if has_locators(method):
                    errors.append(f"Task method '{method.name}' contains locators (should be in POM)")

    return {"errors": errors, "warnings": warnings}


# =============================================================================
# ROLE VALIDATION
# =============================================================================

def validate_role(file_path: str) -> Dict[str, List[str]]:
    """
    Validate Role matches FRAMEWORK.md patterns.

    Rules:
    - HAS @autologger("Role Constructor") on __init__
    - HAS @autologger("Role") decorator on workflow methods
    - Returns None (no return values)
    - Composes Task modules (not inheritance)
    """
    errors = []
    warnings = []

    tree = parse_file(file_path)
    if not tree:
        return {"errors": [f"Could not parse {file_path}"], "warnings": []}

    classes = get_classes(tree)
    if not classes:
        return {"errors": ["No class found"], "warnings": []}

    for cls in classes:
        if cls.name.startswith("_"):
            continue

        # Check for inheritance (should use composition)
        if cls.bases:
            base_names = [ast.unparse(b) for b in cls.bases]
            if any(b not in ("object", "ABC") for b in base_names):
                warnings.append(f"Role {cls.name} inherits from {base_names} - prefer composition")

        methods = get_methods(cls)
        has_constructor = False

        for method in methods:
            if method.name.startswith("_") and method.name != "__init__":
                continue

            if method.name == "__init__":
                has_constructor = True
                # Constructor SHOULD have decorator
                if not has_decorator(method, "autologger"):
                    warnings.append("Role __init__ should have @autologger('Role Constructor')")
            else:
                # Workflow methods MUST have decorator
                if not has_decorator(method, "autologger"):
                    errors.append(f"Role method '{method.name}' missing @autologger decorator")
                elif not has_decorator(method, '"Role"') and not has_decorator(method, "'Role'"):
                    warnings.append(f"Role method '{method.name}' should use @autologger('Role')")

                # Must return None
                if not returns_none_or_nothing(method):
                    errors.append(f"Role method '{method.name}' should return None")

        if not has_constructor:
            errors.append(f"Role {cls.name} missing __init__ constructor")

    return {"errors": errors, "warnings": warnings}


# =============================================================================
# TEST VALIDATION
# =============================================================================

def validate_test(file_path: str) -> Dict[str, List[str]]:
    """
    Validate Test matches FRAMEWORK.md patterns.

    Rules:
    - HAS @autologger("Test") decorator
    - HAS @pytest.mark.<category> marker
    - Asserts via POM state-check methods (not return values)
    - Single role method call per test
    """
    errors = []
    warnings = []

    tree = parse_file(file_path)
    if not tree:
        return {"errors": [f"Could not parse {file_path}"], "warnings": []}

    classes = get_classes(tree)
    if not classes:
        # Could be function-based tests
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                _validate_test_method(node, errors, warnings)
        return {"errors": errors, "warnings": warnings}

    for cls in classes:
        if not cls.name.startswith("Test"):
            continue

        methods = get_methods(cls)

        for method in methods:
            if not method.name.startswith("test_"):
                continue
            _validate_test_method(method, errors, warnings)

    return {"errors": errors, "warnings": warnings}


def _validate_test_method(method: ast.FunctionDef, errors: List[str], warnings: List[str]):
    """Validate a single test method."""
    # Must have autologger decorator
    if not has_decorator(method, "autologger"):
        errors.append(f"Test method '{method.name}' missing @autologger decorator")

    # Should have pytest.mark
    if not has_decorator(method, "pytest.mark"):
        warnings.append(f"Test method '{method.name}' missing @pytest.mark.<category>")

    # Check for assertion patterns
    source = ast.unparse(method)

    # Good: assert self.page.is_logged_in(), assert page.has_products()
    pom_assertions = len(re.findall(r"assert\s+\w+\.\w+\.(is_|has_|get_)", source))

    # Bad: assert result, assert user.login()
    return_assertions = len(re.findall(r"assert\s+\w+\s*[,)]", source))
    return_assertions += len(re.findall(r"assert\s+\w+\.\w+\(\)\s*[,\n]", source))

    if pom_assertions == 0 and "assert" in source:
        warnings.append(f"Test '{method.name}' may not be asserting via POM state-check methods")


# =============================================================================
# MAIN VALIDATION DISPATCHER
# =============================================================================

def detect_layer(file_path: str) -> str:
    """Detect which layer a file belongs to based on path and content."""
    path_lower = file_path.lower()

    if "/pages/" in path_lower or "\\pages\\" in path_lower:
        return "page"
    if "/tasks/" in path_lower or "\\tasks\\" in path_lower:
        return "task"
    if "/roles/" in path_lower or "\\roles\\" in path_lower:
        return "role"
    if "/tests/" in path_lower or "\\tests\\" in path_lower or "test_" in Path(file_path).name:
        return "test"

    # Try to detect from content
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "WebInterface" in content and "def enter_" in content:
                return "page"
            if "Tasks" in content and "@autologger" in content:
                return "task"
            if "User" in content and "tasks" in content.lower():
                return "role"
            if "pytest" in content and "def test_" in content:
                return "test"
    except:
        pass

    return "unknown"


def validate_file(file_path: str, layer: Optional[str] = None) -> Dict[str, any]:
    """
    Validate a single file against FRAMEWORK.md patterns.

    Args:
        file_path: Path to Python file
        layer: Optional layer type (page, task, role, test)

    Returns:
        Dict with layer, errors, warnings
    """
    if not layer:
        layer = detect_layer(file_path)

    result = {
        "file": file_path,
        "layer": layer,
        "errors": [],
        "warnings": []
    }

    if layer == "page":
        validation = validate_page_object(file_path)
    elif layer == "task":
        validation = validate_task(file_path)
    elif layer == "role":
        validation = validate_role(file_path)
    elif layer == "test":
        validation = validate_test(file_path)
    else:
        result["warnings"].append(f"Unknown layer type for {file_path}")
        return result

    result["errors"] = validation["errors"]
    result["warnings"] = validation["warnings"]
    result["valid"] = len(validation["errors"]) == 0

    return result


def validate_directory(directory: str) -> List[Dict]:
    """Validate all Python files in a directory."""
    results = []
    path = Path(directory)

    for py_file in path.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        if py_file.name == "__init__.py":
            continue
        if py_file.name.startswith("conftest"):
            continue

        result = validate_file(str(py_file))
        results.append(result)

    return results


# =============================================================================
# PYTEST INTEGRATION
# =============================================================================

import pytest


class TestPageObjectValidation:
    """Tests for Page Object validation rules."""

    def test_pom_no_decorators(self):
        """POM methods should have NO decorators."""
        from utils.generators import generate_page_object

        code = generate_page_object("TestPage", workflow_type="auth")

        # Parse and check
        tree = ast.parse(code)
        classes = get_classes(tree)
        assert classes, "Should have a class"

        for cls in classes:
            for method in get_methods(cls):
                if method.name == "__init__":
                    continue
                assert not method.decorator_list, f"Method {method.name} should have no decorators"

    def test_pom_returns_self(self):
        """POM action methods should return self."""
        from utils.generators import generate_page_object

        code = generate_page_object(
            "TestPage",
            elements=[{"name": "username", "type": "input", "locator": "#user"}],
            workflow_type="auth"
        )

        tree = ast.parse(code)
        classes = get_classes(tree)

        for cls in classes:
            for method in get_methods(cls):
                if method.name.startswith(("__", "is_", "has_", "get_")):
                    continue
                assert returns_self(method), f"Method {method.name} should return self"

    def test_pom_has_state_checks(self):
        """POM should have state-check methods."""
        from utils.generators import generate_page_object

        code = generate_page_object("LoginPage", workflow_type="auth")

        assert "def is_" in code or "def has_" in code, "POM should have state-check methods"


class TestTaskValidation:
    """Tests for Task validation rules."""

    def test_task_has_decorator(self):
        """Task methods should have @autologger('Task') decorator."""
        from utils.generators import generate_task

        code = generate_task("AuthTasks", workflow_type="auth")

        assert '@autologger.automation_logger("Task")' in code, "Task methods need decorator"

    def test_task_constructor_no_decorator(self):
        """Task constructor should NOT have decorator."""
        from utils.generators import generate_task

        code = generate_task("AuthTasks", workflow_type="auth")

        # Find __init__ and check it doesn't have decorator
        tree = ast.parse(code)
        classes = get_classes(tree)

        for cls in classes:
            for method in get_methods(cls):
                if method.name == "__init__":
                    assert not has_decorator(method, "autologger"), "Constructor should not have decorator"

    def test_task_returns_none(self):
        """Task methods should return None."""
        from utils.generators import generate_task

        code = generate_task("AuthTasks", workflow_type="auth")

        tree = ast.parse(code)
        classes = get_classes(tree)

        for cls in classes:
            for method in get_methods(cls):
                if method.name.startswith("_"):
                    continue
                assert returns_none_or_nothing(method), f"Method {method.name} should return None"


class TestRoleValidation:
    """Tests for Role validation rules."""

    def test_role_has_decorator(self):
        """Role workflow methods should have @autologger('Role') decorator."""
        from utils.generators import generate_role

        code = generate_role("TestUser", role_type="authenticated")

        assert '@autologger.automation_logger("Role")' in code, "Role methods need decorator"

    def test_role_constructor_has_decorator(self):
        """Role constructor should have @autologger('Role Constructor') decorator."""
        from utils.generators import generate_role

        code = generate_role("TestUser", role_type="authenticated")

        assert '@autologger.automation_logger("Role Constructor")' in code, "Constructor needs decorator"

    def test_role_returns_none(self):
        """Role workflow methods should return None."""
        from utils.generators import generate_role

        code = generate_role("TestUser", role_type="authenticated")

        tree = ast.parse(code)
        classes = get_classes(tree)

        for cls in classes:
            for method in get_methods(cls):
                if method.name.startswith("_"):
                    continue
                assert returns_none_or_nothing(method), f"Method {method.name} should return None"


class TestTestValidation:
    """Tests for Test validation rules."""

    def test_test_has_decorator(self):
        """Test methods should have @autologger('Test') decorator."""
        from utils.generators import generate_test

        code = generate_test("TestLogin", workflow_type="auth")

        assert '@autologger.automation_logger("Test")' in code, "Test methods need decorator"

    def test_test_has_pytest_mark(self):
        """Test methods should have @pytest.mark.<category>."""
        from utils.generators import generate_test

        code = generate_test("TestLogin", workflow_type="auth")

        assert "@pytest.mark." in code, "Test methods need pytest marker"

    def test_test_asserts_via_pom(self):
        """Tests should assert via POM state-check methods."""
        from utils.generators import generate_test

        code = generate_test(
            "TestLogin",
            workflow_type="auth",
            pages=[{"name": "LoginPage", "import_path": "pages.login_page"}]
        )

        # Should have assertions that use POM methods
        assert "assert self." in code or "assert page." in code, "Should assert via POM"


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI entry point for validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate generated code against FRAMEWORK.md patterns")
    parser.add_argument("path", nargs="?", help="File or directory to validate")
    parser.add_argument("--layer", choices=["page", "task", "role", "test"], help="Force layer type")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show warnings")

    args = parser.parse_args()

    if not args.path:
        print("Usage: python test_validation.py <file_or_directory>")
        print("       python test_validation.py framework/pages/test1/")
        print("       python -m pytest mcp_server/_dev_tests/test_validation.py -v")
        return

    path = Path(args.path)

    if path.is_file():
        results = [validate_file(str(path), args.layer)]
    elif path.is_dir():
        results = validate_directory(str(path))
    else:
        print(f"Path not found: {args.path}")
        return

    # Print results
    total_errors = 0
    total_warnings = 0

    for result in results:
        if result["errors"] or (args.verbose and result["warnings"]):
            print(f"\n{'='*60}")
            print(f"File: {result['file']}")
            print(f"Layer: {result['layer']}")
            print(f"Valid: {'YES' if result.get('valid', False) else 'NO'}")

            if result["errors"]:
                print("\nERRORS:")
                for err in result["errors"]:
                    print(f"  - {err}")
                total_errors += len(result["errors"])

            if args.verbose and result["warnings"]:
                print("\nWARNINGS:")
                for warn in result["warnings"]:
                    print(f"  - {warn}")
                total_warnings += len(result["warnings"])

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(results)} files checked")
    print(f"  Errors: {total_errors}")
    print(f"  Warnings: {total_warnings}")

    if total_errors == 0:
        print("\nAll validations PASSED!")
    else:
        print(f"\nValidation FAILED with {total_errors} errors")
        sys.exit(1)


if __name__ == "__main__":
    main()
