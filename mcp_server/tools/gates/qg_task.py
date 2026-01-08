"""
Quality Gate: Task (Step 7).

PRE+POST validation gate for Tool 4 (generate_task).

PRE Validation:
- Step 6 complete (pom_metadata exist in state)
- pom_metadata present and is dict
- pom_metadata.class_name present and not empty (IC-07-05)
- workflow present and not empty (dynamic, not hardcoded)
- task_name present and not empty

POST Validation:
- code field present and not empty
- No skeleton code (DD-25): pass, # Add..., NotImplementedError, # TODO
- No locators (DD-27): By. imports, tuple patterns, find_element
- No direct navigation (DD-49): self.web.navigate_to() - must use POM navigate()
- No return values except bare return/return None (IC-07-02)
- @autologger.automation_logger("Task") decorator present (IC-07-04)
- metadata present with class_name and import_path (DD-26)

Enforces: DD-12, DD-25, DD-26, DD-27, DD-49, IC-07-01 through IC-07-05

Note: workflow (formerly domain) is now dynamic - any non-empty string is valid.
"""

import re
from typing import Any, Dict, Optional

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGTask(BaseGate):
    """Quality gate for Step 7: Task Generation."""

    # Skeleton code patterns (DD-25, IC-07-01)
    SKELETON_PATTERNS = [
        (r'^\s*pass\s*$', 'pass statement'),
        (r'#\s*[Aa]dd\s+.*\s+as\s+needed', 'placeholder comment'),
        (r'raise\s+NotImplementedError', 'NotImplementedError'),
        (r'#\s*TODO:', 'TODO comment'),
    ]

    # Locator patterns (DD-27, IC-07-03)
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

    # Navigation patterns (DD-49) - Tasks must NOT call WebInterface.navigate_to directly
    NAVIGATION_PATTERNS = [
        (r'self\.web\.navigate_to\s*\(', 'self.web.navigate_to() call'),
        (r'\.navigate_to\s*\(\s*["\']https?://', 'navigate_to with hardcoded URL'),
    ]

    # Required decorator pattern (IC-07-04)
    TASK_DECORATOR_PATTERN = re.compile(
        r'@autologger\.automation_logger\s*\(\s*["\']Task["\']\s*\)'
    )

    # Return value patterns to detect (IC-07-02)
    # Matches: return <something> but NOT: return, return None
    RETURN_VALUE_PATTERN = re.compile(
        r'^\s*return\s+(?!None\s*$)(?!\s*$).+',
        re.MULTILINE
    )

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        # Task 16.0: Use per-run state isolation
        audit_logger = cls.get_audit_logger()
        return StateManager(run_id=audit_logger.run_id)

    @classmethod
    def _import_path_to_file_path(cls, import_path: str) -> str:
        """
        Convert Python import path to file system path.

        Task 16.0 (DEF-051): Helper for immediate file writes.

        Args:
            import_path: e.g., "framework.tasks.auth.auth_tasks"

        Returns:
            Absolute file path: e.g., "D:/project/framework/tasks/auth/auth_tasks.py"
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
    def _write_task_file(cls, file_path: str, code: str) -> None:
        """
        Write Task code to disk immediately.

        Task 16.0 (DEF-051): Ensures Task files are saved.

        Args:
            file_path: Absolute path to write file
            code: Task code content
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
        PRE validation before Tool 4 operation.

        Validates:
        - Step 6 is complete
        - pom_metadata present and valid (IC-07-05)
        - domain is valid (auth, catalog, cart, checkout)
        - task_name present and not empty

        Args:
            input_data: Dict with pom_metadata, domain, task_name

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 6 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(6):
            return cls.fail_response(
                error="Step 6 is not complete. Cannot proceed to Step 7.",
                fix_hint="Complete Step 6 (Generate Page Object) first. Ensure pom_metadata exists."
            )

        # Validate pom_metadata (IC-07-05)
        pom_metadata = input_data.get("pom_metadata")

        if pom_metadata is None:
            return cls.fail_response(
                error="Missing required field: pom_metadata",
                fix_hint="Provide pom_metadata from Step 6 state."
            )

        if not isinstance(pom_metadata, dict):
            return cls.fail_response(
                error="pom_metadata must be a dictionary",
                fix_hint="Provide pom_metadata as an object from Tool 3 output."
            )

        # IC-07-05: class_name required in pom_metadata
        class_name = pom_metadata.get("class_name")
        if class_name is None or not isinstance(class_name, str) or not class_name.strip():
            return cls.fail_response(
                error="Missing or empty class_name in pom_metadata (IC-07-05 violation)",
                fix_hint="Ensure Tool 3 output includes class_name in metadata."
            )

        # Validate workflow (supports 'domain' for backwards compatibility)
        workflow = input_data.get("workflow") or input_data.get("domain")
        if workflow is None:
            return cls.fail_response(
                error="Missing required field: workflow",
                fix_hint="Provide workflow (e.g., 'auth', 'catalog', 'checkout', or any custom name)."
            )

        if not isinstance(workflow, str) or not workflow.strip():
            return cls.fail_response(
                error=f"Invalid workflow: '{workflow}'. Must be a non-empty string.",
                fix_hint="Provide a valid workflow name (e.g., 'auth', 'catalog', or custom)."
            )

        # Validate task_name
        task_name = input_data.get("task_name")
        if task_name is None:
            return cls.fail_response(
                error="Missing required field: task_name",
                fix_hint="Provide task_name (e.g., 'AuthTasks', 'CatalogTasks')."
            )

        if not isinstance(task_name, str) or not task_name.strip():
            return cls.fail_response(
                error="task_name must be a non-empty string",
                fix_hint="Provide a valid task class name like 'AuthTasks'."
            )

        return cls.pass_response(
            step=7,
            gate_name="qg_task",
            mode="PRE",
            metadata={"task_name": task_name}
        )

    # Step number for this gate (used for attempt tracking)
    STEP_NUMBER = 7

    @classmethod
    def validate_post(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST validation after Tool 4 operation.

        Validates:
        - code field present and not empty
        - No skeleton code (DD-25, IC-07-01)
        - No locators (DD-27, IC-07-03)
        - No return values (IC-07-02)
        - Decorator present (IC-07-04)
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
                        gate_name="qg_task",
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
                        gate_name="qg_task",
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
                fix_hint="Tool 4 must return generated Task code."
            )

        if not isinstance(code, str) or not code.strip():
            return cls.fail_response(
                error="code is empty",
                fix_hint="Tool 4 must generate non-empty Task code."
            )

        # Check for skeleton code (DD-25, IC-07-01)
        skeleton_error = cls._detect_skeleton_code(code)
        if skeleton_error:
            return skeleton_error

        # Check for locators (DD-27, IC-07-03)
        locator_error = cls._detect_locators(code)
        if locator_error:
            return locator_error

        # Check for direct navigation (DD-49)
        navigation_error = cls._detect_navigation(code)
        if navigation_error:
            return navigation_error

        # Check for return values (IC-07-02)
        return_error = cls._detect_return_values(code)
        if return_error:
            return return_error

        # Check for decorator (IC-07-04)
        decorator_error = cls._check_decorator(code)
        if decorator_error:
            return decorator_error

        # Validate metadata field (DD-26)
        metadata = input_data.get("metadata")

        if metadata is None:
            return cls.fail_response(
                error="Missing required field: metadata",
                fix_hint="Tool 4 must return metadata for downstream tools."
            )

        if not isinstance(metadata, dict):
            return cls.fail_response(
                error="metadata must be a dictionary",
                fix_hint="Tool 4 should return metadata as an object."
            )

        # Validate metadata structure (DD-26)
        metadata_error = cls._validate_metadata_structure(metadata)
        if metadata_error:
            return metadata_error

        # Save Step 7 state (basic - Tasks are per-domain, not per-page)
        # Note: Multi-page loop tracking only applies to Step 6 (POMs)
        # Tasks are per-domain (e.g., AuthTasks, CatalogTasks), not per-page
        state_manager = cls._get_state_manager()
        state_manager.save(step=7, data={
            "task_code": code,
            "task_metadata": metadata
        })

        # Task 16.0 (DEF-051 FIX): Write Task file immediately to disk
        import_path = metadata.get("import_path")
        if import_path:
            file_path = cls._import_path_to_file_path(import_path)
            try:
                # Write file to disk
                cls._write_task_file(file_path, code)

                # Log file write to audit trail
                audit_logger = cls.get_audit_logger()
                audit_logger.log_file_generated(file_path, step=7)
            except Exception as e:
                # If file write fails, log but don't block (validation already passed)
                # This ensures state is saved even if file write fails
                pass

        return cls.pass_response(
            step=7,
            gate_name="qg_task",
            mode="POST",
            metadata={
                "class_name": metadata.get("class_name"),
                "import_path": metadata.get("import_path"),
                "task_methods_count": len(metadata.get("task_methods", []))
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
                    fix_hint="AI must complete the code. Remove placeholders and implement all method bodies with POM calls."
                )
        return None

    @classmethod
    def _detect_locators(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect locator patterns in Task code (DD-27, IC-07-03).

        Tasks should NOT contain locators - those belong in Page Objects.

        Returns fail_response if locators detected, None otherwise.
        """
        for pattern, description in cls.LOCATOR_PATTERNS:
            if re.search(pattern, code):
                return cls.fail_response(
                    error=f"Locator detected in Task: {description}",
                    fix_hint="Locators belong in Page Objects, not Tasks. Use POM methods instead."
                )
        return None

    @classmethod
    def _detect_navigation(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect direct navigation calls in Task code (DD-49).

        Tasks should NOT call self.web.navigate_to() directly.
        Instead, Tasks should call POM navigate() methods.

        Returns fail_response if navigation detected, None otherwise.
        """
        for pattern, description in cls.NAVIGATION_PATTERNS:
            if re.search(pattern, code):
                return cls.fail_response(
                    error=f"Direct navigation in Task: {description}",
                    fix_hint="Tasks must call POM navigate() methods, not self.web.navigate_to() directly. Move navigation to POM."
                )
        return None

    @classmethod
    def _detect_return_values(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect return values in Task methods (IC-07-02).

        Tasks should NOT return values - tests assert via POM state methods.
        Allowed: bare 'return' and 'return None'.

        Returns fail_response if return value detected, None otherwise.
        """
        if cls.RETURN_VALUE_PATTERN.search(code):
            return cls.fail_response(
                error="Task method returns a value (IC-07-02 violation)",
                fix_hint="Tasks should not return values. Tests assert via POM state-check methods. Remove return statements."
            )
        return None

    @classmethod
    def _check_decorator(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Check for @autologger.automation_logger("Task") decorator (IC-07-04).

        Each Task method (not constructor) should have this decorator.

        Returns fail_response if decorator missing/wrong, None otherwise.
        """
        # Check if code has any method definitions (other than __init__)
        method_pattern = re.compile(r'^\s+def\s+(?!__init__)\w+\s*\(', re.MULTILINE)
        has_methods = bool(method_pattern.search(code))

        if not has_methods:
            # No methods to validate (edge case)
            return None

        # Check for correct decorator
        if not cls.TASK_DECORATOR_PATTERN.search(code):
            # Check if wrong decorator type is used (e.g., "Role" instead of "Task")
            wrong_decorator_pattern = re.compile(
                r'@autologger\.automation_logger\s*\(\s*["\'](?!Task)["\']'
            )
            if wrong_decorator_pattern.search(code):
                return cls.fail_response(
                    error="Wrong decorator type. Must be @autologger.automation_logger(\"Task\") (IC-07-04 violation)",
                    fix_hint="Use @autologger.automation_logger(\"Task\") for Task methods."
                )
            return cls.fail_response(
                error="Missing @autologger.automation_logger(\"Task\") decorator (IC-07-04 violation)",
                fix_hint="Add @autologger.automation_logger(\"Task\") decorator to each Task method."
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
                fix_hint="Tool 4 must include class_name in metadata."
            )

        # Check import_path
        import_path = metadata.get("import_path")
        if import_path is None or not isinstance(import_path, str) or not import_path.strip():
            return cls.fail_response(
                error="Missing or invalid import_path in metadata",
                fix_hint="Tool 4 must include import_path in metadata."
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
