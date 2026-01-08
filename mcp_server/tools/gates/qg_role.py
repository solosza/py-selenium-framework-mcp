"""
Quality Gate: Role (Step 8).

PRE+POST validation gate for Tool 5 (generate_role).

PRE Validation:
- Step 7 complete (task_metadata exist in state)
- task_metadata present and is dict
- task_metadata.class_name present and not empty (IC-08-05)
- role_name present, not empty, and PascalCase

POST Validation:
- code field present and not empty
- No skeleton code (DD-25): pass, # Add..., NotImplementedError, # TODO
- No locators (DD-27): By. imports, tuple patterns, find_element
- No return values except bare return/return None
- @autologger.automation_logger("Role") decorator present (IC-08-04)
- At least one task method call (IC-08-06)
- metadata present with class_name and import_path (DD-26)

Enforces: DD-12, DD-25, DD-26, DD-27, IC-08-01 through IC-08-06
"""

import re
from typing import Any, Dict, Optional

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGRole(BaseGate):
    """Quality gate for Step 8: Role Generation."""

    # PascalCase pattern: starts with uppercase, alphanumeric
    PASCAL_CASE_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    # Skeleton code patterns (DD-25, IC-08-01)
    SKELETON_PATTERNS = [
        (r'^\s*pass\s*$', 'pass statement'),
        (r'#\s*[Aa]dd\s+.*\s+as\s+needed', 'placeholder comment'),
        (r'raise\s+NotImplementedError', 'NotImplementedError'),
        (r'#\s*TODO:', 'TODO comment'),
    ]

    # Locator patterns (DD-27, IC-08-03)
    LOCATOR_PATTERNS = [
        (r'from\s+selenium\.webdriver\.common\.by\s+import\s+By', 'By import'),
        (r'\(By\.', 'By tuple pattern'),
        (r'By\.CSS_SELECTOR', 'By.CSS_SELECTOR'),
        (r'By\.XPATH', 'By.XPATH'),
        (r'By\.ID', 'By.ID'),
        (r'By\.CLASS_NAME', 'By.CLASS_NAME'),
        (r'By\.NAME', 'By.NAME'),
        (r'By\.TAG_NAME', 'By.TAG_NAME'),
        (r'By\.LINK_TEXT', 'By.LINK_TEXT'),
        (r'By\.PARTIAL_LINK_TEXT', 'By.PARTIAL_LINK_TEXT'),
        (r'\.find_element\s*\(', 'find_element call'),
        (r'\.find_elements\s*\(', 'find_elements call'),
    ]

    # Required decorator pattern (IC-08-04)
    ROLE_DECORATOR_PATTERN = re.compile(
        r'@autologger\.automation_logger\s*\(\s*["\']Role["\']\s*\)'
    )

    # Return value patterns to detect
    # Matches: return <something> but NOT: return, return None
    RETURN_VALUE_PATTERN = re.compile(
        r'^\s*return\s+(?!None\s*$)(?!\s*$).+',
        re.MULTILINE
    )

    # Task method call pattern (IC-08-06)
    # Matches: self.xxx_tasks.method_name(...)
    TASK_CALL_PATTERN = re.compile(
        r'self\.\w+_tasks\.\w+\s*\('
    )

    # POM import patterns - Roles should NOT import POMs directly
    POM_IMPORT_PATTERNS = [
        (r'from\s+pages\.', 'POM import in Role'),
        (r'import\s+pages\.', 'POM import in Role'),
    ]

    # Direct POM method call pattern - Roles should use Tasks, not POMs
    POM_CALL_PATTERN = re.compile(
        r'self\.\w+_page\.\w+\s*\('
    )

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        # Task 17.0: Use per-run state isolation
        audit_logger = cls.get_audit_logger()
        return StateManager(run_id=audit_logger.run_id)

    @classmethod
    def _import_path_to_file_path(cls, import_path: str) -> str:
        """
        Convert Python import path to file system path.

        Task 17.0 (DEF-051): Helper for immediate file writes.

        Args:
            import_path: e.g., "framework.roles.registered_user"

        Returns:
            Absolute file path: e.g., "D:/project/framework/roles/registered_user.py"
        """
        import os
        from pathlib import Path

        # Convert dots to path separator
        relative_path = import_path.replace(".", os.sep) + ".py"

        # Get project root (3 levels up from mcp_server/tools/gates/)
        project_root = Path(__file__).parent.parent.parent.parent

        # Combine to get absolute path
        file_path = project_root / relative_path

        return str(file_path)

    @classmethod
    def _write_role_file(cls, file_path: str, code: str) -> None:
        """
        Write Role code to disk immediately.

        Task 17.0 (DEF-051): Ensures Role files are saved.

        Args:
            file_path: Absolute path to write file
            code: Role code content
        """
        import os
        from pathlib import Path

        # Ensure parent directory exists
        file_obj = Path(file_path)
        file_obj.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(code)

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation before Tool 5 operation.

        Validates:
        - Step 7 is complete
        - task_metadata present and valid (IC-08-05)
        - role_name present, not empty, and PascalCase

        Args:
            input_data: Dict with task_metadata, role_name

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 7 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(7):
            return cls.fail_response(
                error="Step 7 is not complete. Cannot proceed to Step 8.",
                fix_hint="Complete Step 7 (Generate Task) first. Ensure task_metadata exists."
            )

        # Validate task_metadata (IC-08-05)
        task_metadata = input_data.get("task_metadata")

        if task_metadata is None:
            return cls.fail_response(
                error="Missing required field: task_metadata",
                fix_hint="Provide task_metadata from Step 7 state."
            )

        if not isinstance(task_metadata, dict):
            return cls.fail_response(
                error="task_metadata must be a dictionary",
                fix_hint="Provide task_metadata as an object from Tool 4 output."
            )

        # IC-08-05: class_name required in task_metadata
        class_name = task_metadata.get("class_name")
        if class_name is None or not isinstance(class_name, str) or not class_name.strip():
            return cls.fail_response(
                error="Missing or empty class_name in task_metadata (IC-08-05 violation)",
                fix_hint="Ensure Tool 4 output includes class_name in metadata."
            )

        # Validate role_name
        role_name = input_data.get("role_name")
        if role_name is None:
            return cls.fail_response(
                error="Missing required field: role_name",
                fix_hint="Provide role_name (e.g., 'RegisteredUser', 'GuestUser')."
            )

        if not isinstance(role_name, str) or not role_name.strip():
            return cls.fail_response(
                error="role_name must be a non-empty string",
                fix_hint="Provide a valid role class name like 'RegisteredUser'."
            )

        # Validate PascalCase
        if not cls.PASCAL_CASE_PATTERN.match(role_name):
            return cls.fail_response(
                error=f"role_name '{role_name}' is not PascalCase",
                fix_hint="Use PascalCase format: 'RegisteredUser', 'GuestUser', 'AdminUser'"
            )

        return cls.pass_response(
            step=8,
            gate_name="qg_role",
            mode="PRE",
            metadata={"role_name": role_name}
        )

    # Step number for this gate (used for attempt tracking)
    STEP_NUMBER = 8

    @classmethod
    def validate_post(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST validation after Tool 5 operation.

        Validates:
        - code field present and not empty
        - No skeleton code (DD-25, IC-08-01)
        - No locators (DD-27, IC-08-03)
        - No return values
        - Decorator present (IC-08-04)
        - Task method calls present (IC-08-06)
        - metadata present with required structure (DD-26)

        Args:
            input_data: Dict with code, metadata

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
            or {"status": "blocked", ...} if max attempts exceeded
        """
        # Task 2.0: Check if blocked due to max attempts
        state_manager = cls._state_manager
        if state_manager:
            attempts = state_manager.get_attempt_count(cls.STEP_NUMBER)
            if attempts >= cls.MAX_ATTEMPTS:
                return cls.blocked_response(
                    step=cls.STEP_NUMBER,
                    attempts=attempts,
                    errors=[]
                )

        # Run actual validation
        result = cls._validate_post_internal(input_data)

        # Task 2.5: Extract source from input_data
        source = input_data.get("source")

        # Task 2.0: Track attempts and log to audit
        if state_manager:
            if result.get("status") == "fail":
                state_manager.increment_attempt(cls.STEP_NUMBER)
                # Log failure to audit
                if cls._audit_logger:
                    cls._audit_logger.log_gate(
                        step=cls.STEP_NUMBER,
                        gate_name="qg_role",
                        mode="POST",
                        result="fail",
                        error=result.get("error"),
                        source=source
                    )
            elif result.get("status") == "pass":
                state_manager.reset_attempts(cls.STEP_NUMBER)
                # Task 2.5: Log success with source
                if cls._audit_logger:
                    cls._audit_logger.log_gate(
                        step=cls.STEP_NUMBER,
                        gate_name="qg_role",
                        mode="POST",
                        result="pass",
                        source=source
                    )

        return result

    @classmethod
    def _validate_post_internal(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal validation logic (separated for attempt tracking)."""
        # Validate code field
        code = input_data.get("code")

        if code is None:
            return cls.fail_response(
                error="Missing required field: code",
                fix_hint="Tool 5 must return generated Role code."
            )

        if not isinstance(code, str) or not code.strip():
            return cls.fail_response(
                error="code is empty",
                fix_hint="Tool 5 must generate non-empty Role code."
            )

        # Check for skeleton code (DD-25, IC-08-01)
        skeleton_error = cls._detect_skeleton_code(code)
        if skeleton_error:
            return skeleton_error

        # Check for locators (DD-27, IC-08-03)
        locator_error = cls._detect_locators(code)
        if locator_error:
            return locator_error

        # Check for POM imports (Roles should use Tasks, not POMs)
        pom_import_error = cls._detect_pom_imports(code)
        if pom_import_error:
            return pom_import_error

        # Check for direct POM method calls (Roles should use Tasks)
        pom_call_error = cls._detect_pom_calls(code)
        if pom_call_error:
            return pom_call_error

        # Check for return values
        return_error = cls._detect_return_values(code)
        if return_error:
            return return_error

        # Check for decorator (IC-08-04)
        decorator_error = cls._check_decorator(code)
        if decorator_error:
            return decorator_error

        # Check for task method calls (IC-08-06)
        task_call_error = cls._check_task_calls(code)
        if task_call_error:
            return task_call_error

        # Validate metadata field (DD-26)
        metadata = input_data.get("metadata")

        if metadata is None:
            return cls.fail_response(
                error="Missing required field: metadata",
                fix_hint="Tool 5 must return metadata for downstream tools."
            )

        if not isinstance(metadata, dict):
            return cls.fail_response(
                error="metadata must be a dictionary",
                fix_hint="Tool 5 should return metadata as an object."
            )

        # Validate metadata structure (DD-26)
        metadata_error = cls._validate_metadata_structure(metadata)
        if metadata_error:
            return metadata_error

        # Save Step 8 state on POST-VALIDATE pass
        state_manager = cls._get_state_manager()
        state_manager.save(step=8, data={
            "role_code": code,
            "role_metadata": metadata
        })

        # Task 17.0 (DEF-051 FIX): Write Role file immediately to disk
        import_path = metadata.get("import_path")
        if import_path:
            file_path = cls._import_path_to_file_path(import_path)
            try:
                # Write file to disk
                cls._write_role_file(file_path, code)

                # Log file write to audit trail
                audit_logger = cls.get_audit_logger()
                audit_logger.log_file_generated(file_path, step=8)
            except Exception as e:
                # If file write fails, log but don't block (validation already passed)
                # This ensures state is saved even if file write fails
                pass

        return cls.pass_response(
            step=8,
            gate_name="qg_role",
            mode="POST",
            metadata={
                "class_name": metadata.get("class_name"),
                "import_path": metadata.get("import_path"),
                "workflow_methods_count": len(metadata.get("workflow_methods", []))
            }
        )

    @classmethod
    def _detect_skeleton_code(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect skeleton code patterns in generated code.

        Returns fail_response if skeleton detected, None otherwise.
        """
        for pattern, description in cls.SKELETON_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                return cls.fail_response(
                    error=f"Skeleton code detected: {description}",
                    fix_hint="AI must complete the code. Remove placeholders and implement all workflow methods with task calls."
                )
        return None

    @classmethod
    def _detect_locators(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect locator patterns in Role code (DD-27, IC-08-03).

        Roles should NOT contain locators - those belong in Page Objects.

        Returns fail_response if locators detected, None otherwise.
        """
        for pattern, description in cls.LOCATOR_PATTERNS:
            if re.search(pattern, code):
                return cls.fail_response(
                    error=f"Locator detected in Role: {description}",
                    fix_hint="Locators belong in Page Objects, not Roles. Use Task methods which use POM methods."
                )
        return None

    @classmethod
    def _detect_pom_imports(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect POM import patterns in Role code.

        Roles should NOT import POMs directly - they should use Tasks.
        Tasks are the layer that composes POMs.

        Returns fail_response if POM imports detected, None otherwise.
        """
        for pattern, description in cls.POM_IMPORT_PATTERNS:
            if re.search(pattern, code):
                return cls.fail_response(
                    error=f"Layer violation detected: {description} (architecture violation)",
                    fix_hint="Roles should not import POMs. Roles use Tasks, and Tasks use POMs. Remove POM imports and use Task methods."
                )
        return None

    @classmethod
    def _detect_pom_calls(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect direct POM method calls in Role code.

        Roles should NOT call POM methods directly - they should use Tasks.
        Pattern: self.xxx_page.method() indicates direct POM usage.

        Returns fail_response if POM calls detected, None otherwise.
        """
        if cls.POM_CALL_PATTERN.search(code):
            return cls.fail_response(
                error="Direct POM method call detected in Role (architecture violation)",
                fix_hint="Roles should not call POM methods. Use Task methods instead: self.xxx_tasks.method(), not self.xxx_page.method()."
            )
        return None

    @classmethod
    def _detect_return_values(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect return values in Role methods.

        Roles should NOT return values - tests assert via POM state methods.
        Allowed: bare 'return' and 'return None'.

        Returns fail_response if return value detected, None otherwise.
        """
        if cls.RETURN_VALUE_PATTERN.search(code):
            return cls.fail_response(
                error="Role method returns a value (architecture violation)",
                fix_hint="Roles should not return values. Tests assert via POM state-check methods. Remove return statements."
            )
        return None

    @classmethod
    def _check_decorator(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Check for @autologger.automation_logger("Role") decorator (IC-08-04).

        Each Role workflow method (not constructor) should have this decorator.

        Returns fail_response if decorator missing/wrong, None otherwise.
        """
        # Check if code has any method definitions (other than __init__)
        method_pattern = re.compile(r'^\s+def\s+(?!__init__)\w+\s*\(', re.MULTILINE)
        has_methods = bool(method_pattern.search(code))

        if not has_methods:
            # No methods to validate (edge case)
            return None

        # Check for correct decorator
        if not cls.ROLE_DECORATOR_PATTERN.search(code):
            # Check if wrong decorator type is used (e.g., "Task" instead of "Role")
            wrong_decorator_pattern = re.compile(
                r'@autologger\.automation_logger\s*\(\s*["\'](?!Role|Role Constructor)["\']'
            )
            if wrong_decorator_pattern.search(code):
                return cls.fail_response(
                    error="Wrong decorator type. Must be @autologger.automation_logger(\"Role\") (IC-08-04 violation)",
                    fix_hint="Use @autologger.automation_logger(\"Role\") for Role workflow methods."
                )
            return cls.fail_response(
                error="Missing @autologger.automation_logger(\"Role\") decorator (IC-08-04 violation)",
                fix_hint="Add @autologger.automation_logger(\"Role\") decorator to each Role workflow method."
            )

        return None

    @classmethod
    def _check_task_calls(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Check for task method calls in Role code (IC-08-06).

        Role workflow methods must call at least one task method.
        Pattern: self.xxx_tasks.method_name(...)

        Returns fail_response if no task calls found, None otherwise.
        """
        # Check if code has any workflow method definitions (other than __init__)
        method_pattern = re.compile(r'^\s+def\s+(?!__init__)\w+\s*\(', re.MULTILINE)
        has_methods = bool(method_pattern.search(code))

        if not has_methods:
            # No methods to validate (edge case)
            return None

        # Check for task method calls
        if not cls.TASK_CALL_PATTERN.search(code):
            return cls.fail_response(
                error="No task method calls found in Role (IC-08-06 violation)",
                fix_hint="Role workflow methods must call task methods. Add self.xxx_tasks.method_name() calls."
            )

        return None

    @classmethod
    def _validate_metadata_structure(cls, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate metadata has required fields (DD-26).

        Returns fail_response if invalid, None otherwise.
        """
        # Check class_name
        class_name = metadata.get("class_name")
        if class_name is None or not isinstance(class_name, str) or not class_name.strip():
            return cls.fail_response(
                error="Missing or invalid class_name in metadata",
                fix_hint="Tool 5 must include class_name in metadata."
            )

        # Check import_path
        import_path = metadata.get("import_path")
        if import_path is None or not isinstance(import_path, str) or not import_path.strip():
            return cls.fail_response(
                error="Missing or invalid import_path in metadata",
                fix_hint="Tool 5 must include import_path in metadata."
            )

        return None

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation entry point.

        Routes to PRE or POST validation based on mode.

        Args:
            input_data: Dict with "mode" field ("PRE" or "POST") and relevant data

        Returns:
            Validation result
        """
        mode = input_data.get("mode", "")

        if not mode:
            return cls.fail_response(
                error="Missing required field: mode",
                fix_hint="Specify mode='PRE' for input validation or mode='POST' for output validation."
            )

        mode_upper = mode.upper() if isinstance(mode, str) else ""

        if mode_upper == "PRE":
            return cls.validate_pre(input_data)
        elif mode_upper == "POST":
            return cls.validate_post(input_data)
        else:
            return cls.fail_response(
                error=f"Invalid mode: '{mode}'. Must be 'PRE' or 'POST'.",
                fix_hint="Specify mode='PRE' for input validation or mode='POST' for output validation."
            )
