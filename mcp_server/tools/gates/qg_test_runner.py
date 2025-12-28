"""
Quality Gate: Test Runner (Step 9).

PRE+POST validation gate for Tool 6 (generate_test_runner).

PRE Validation:
- Step 8 complete (role_metadata exists in state)
- role_metadata present and valid (class_name required)
- pom_metadata present and valid (class_name required)
- test_scenarios present and not empty

POST Validation:
- code field present and not empty
- No skeleton code (DD-25): pass, # TODO, placeholder, NotImplementedError
- At least one role method call (IC-09-03)
- POM state assertions used, no return value assertions (IC-09-04, DD-15)
- @autologger.automation_logger("Test") decorator present (IC-09-05)
- metadata present with class_name and file_path

Enforces: DD-15, DD-25, IC-09-01 through IC-09-05
"""

import re
from typing import Any, Dict, Optional

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGTestRunner(BaseGate):
    """Quality gate for Step 9: Test Runner Generation."""

    # Skeleton code patterns (DD-25, IC-09-02)
    SKELETON_PATTERNS = [
        (r'^\s*pass\s*$', 'pass statement'),
        (r'#\s*TODO:', 'TODO comment'),
        (r'#\s*[Aa]dd\s+.*\s+as\s+needed', 'placeholder comment'),
        (r'raise\s+NotImplementedError', 'NotImplementedError'),
    ]

    # Required decorator pattern (IC-09-05)
    TEST_DECORATOR_PATTERN = re.compile(
        r'@autologger\.automation_logger\s*\(\s*["\']Test["\']\s*\)'
    )

    # Role method call pattern (IC-09-03)
    # Matches: variable.method_name( where variable is likely a role instance
    # Common patterns: user.login(), admin.create_user(), guest.browse()
    ROLE_CALL_PATTERN = re.compile(
        r'\b(user|admin|guest|buyer|seller|manager|customer|visitor|member)\w*\.\w+\s*\('
    )

    # Return value assertion pattern (IC-09-04, DD-15)
    # Matches: result = user.method() followed by assert result
    RETURN_ASSERTION_PATTERN = re.compile(
        r'(\w+)\s*=\s*\w+\.\w+\s*\([^)]*\)\s*\n.*assert\s+\1',
        re.MULTILINE
    )

    # Generic weak assertions (IC-09-04)
    WEAK_ASSERTION_PATTERNS = [
        (r'^\s*assert\s+True\s*$', 'assert True'),
        (r'^\s*assert\s+1\s*$', 'assert 1'),
    ]

    # POM state assertion pattern (IC-09-04)
    # Matches: assert self.page.is_xxx() or assert page_var.has_xxx()
    POM_ASSERTION_PATTERN = re.compile(
        r'assert\s+(?:self\.)?\w+\.(is_|has_|get_)\w+\s*\('
    )

    # Task method call pattern - Tests should NOT call Tasks directly
    TASK_CALL_PATTERN = re.compile(
        r'\w+_tasks\.\w+\s*\('
    )

    # POM action method call patterns - Tests should NOT call POM action methods
    # Action methods: enter_, click_, select_, type_, submit_, etc.
    POM_ACTION_PATTERN = re.compile(
        r'\w+_page\.(enter_|click_|select_|type_|submit_|fill_|check_|clear_)\w*\s*\('
    )

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        return StateManager()

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation before Tool 6 operation.

        Validates:
        - Step 8 is complete
        - role_metadata present and valid
        - pom_metadata present and valid
        - test_scenarios present and not empty

        Args:
            input_data: Dict with role_metadata, pom_metadata, test_scenarios

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 8 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(8):
            return cls.fail_response(
                error="Step 8 is not complete. Cannot proceed to Step 9.",
                fix_hint="Complete Step 8 (Generate Role) first. Ensure role_metadata exists."
            )

        # Validate role_metadata (IC-09-01)
        role_metadata = input_data.get("role_metadata")

        if role_metadata is None:
            return cls.fail_response(
                error="Missing required field: role_metadata",
                fix_hint="Provide role_metadata from Step 8 state."
            )

        if not isinstance(role_metadata, dict):
            return cls.fail_response(
                error="role_metadata must be a dictionary",
                fix_hint="Provide role_metadata as an object from Tool 5 output."
            )

        # Check role_metadata has class_name
        role_class = role_metadata.get("class_name")
        if role_class is None or not isinstance(role_class, str) or not role_class.strip():
            return cls.fail_response(
                error="Missing or empty class_name in role_metadata",
                fix_hint="Ensure Tool 5 output includes class_name in metadata."
            )

        # Validate pom_metadata (IC-09-01)
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

        # Check pom_metadata has class_name
        pom_class = pom_metadata.get("class_name")
        if pom_class is None or not isinstance(pom_class, str) or not pom_class.strip():
            return cls.fail_response(
                error="Missing or empty class_name in pom_metadata",
                fix_hint="Ensure Tool 3 output includes class_name in metadata."
            )

        # Validate test_scenarios (IC-09-01)
        test_scenarios = input_data.get("test_scenarios")

        if test_scenarios is None:
            return cls.fail_response(
                error="Missing required field: test_scenarios",
                fix_hint="Provide test_scenarios from Step 4 (Tool 1 output)."
            )

        if not isinstance(test_scenarios, list):
            return cls.fail_response(
                error="test_scenarios must be a list",
                fix_hint="Provide test_scenarios as a list from Tool 1 output."
            )

        if len(test_scenarios) == 0:
            return cls.fail_response(
                error="test_scenarios is empty",
                fix_hint="At least one test scenario required from Tool 1."
            )

        return cls.pass_response()

    # Step number for this gate (used for attempt tracking)
    STEP_NUMBER = 9

    @classmethod
    def validate_post(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST validation after Tool 6 operation.

        Validates:
        - code field present and not empty
        - No skeleton code (DD-25, IC-09-02)
        - At least one role method call (IC-09-03)
        - POM state assertions used (IC-09-04, DD-15)
        - Decorator present (IC-09-05)
        - metadata present with required structure

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
                        gate_name="qg_test_runner",
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
                        gate_name="qg_test_runner",
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
                fix_hint="Tool 6 must return generated test code."
            )

        if not isinstance(code, str) or not code.strip():
            return cls.fail_response(
                error="code is empty",
                fix_hint="Tool 6 must generate non-empty test code."
            )

        # Check for skeleton code (DD-25, IC-09-02)
        skeleton_error = cls._detect_skeleton_code(code)
        if skeleton_error:
            return skeleton_error

        # Check for test decorator (IC-09-05)
        decorator_error = cls._check_decorator(code)
        if decorator_error:
            return decorator_error

        # Check for role method calls (IC-09-03)
        role_call_error = cls._check_role_calls(code)
        if role_call_error:
            return role_call_error

        # Check for Task method calls (bypasses Role layer)
        task_call_error = cls._check_task_calls(code)
        if task_call_error:
            return task_call_error

        # Check for POM action method calls (bypasses Role+Task layers)
        pom_action_error = cls._check_pom_actions(code)
        if pom_action_error:
            return pom_action_error

        # Check for POM assertions (IC-09-04, DD-15)
        assertion_error = cls._check_assertions(code)
        if assertion_error:
            return assertion_error

        # Validate metadata field
        metadata = input_data.get("metadata")

        if metadata is None:
            return cls.fail_response(
                error="Missing required field: metadata",
                fix_hint="Tool 6 must return metadata for downstream tools."
            )

        if not isinstance(metadata, dict):
            return cls.fail_response(
                error="metadata must be a dictionary",
                fix_hint="Tool 6 should return metadata as an object."
            )

        # Validate metadata structure
        metadata_error = cls._validate_metadata_structure(metadata)
        if metadata_error:
            return metadata_error

        # Save Step 9 state on POST-VALIDATE pass
        state_manager = cls._get_state_manager()
        state_manager.save(step=9, data={
            "test_code": code,
            "test_metadata": metadata
        })

        return cls.pass_response()

    @classmethod
    def _detect_skeleton_code(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect skeleton code patterns in generated code (DD-25, IC-09-02).

        Returns fail_response if skeleton detected, None otherwise.
        """
        for pattern, description in cls.SKELETON_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                return cls.fail_response(
                    error=f"Skeleton code detected: {description} (DD-25 violation)",
                    fix_hint="AI must complete the test code. Remove placeholders and implement all test methods with real assertions."
                )
        return None

    @classmethod
    def _check_decorator(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Check for @autologger.automation_logger("Test") decorator (IC-09-05).

        Returns fail_response if decorator missing/wrong, None otherwise.
        """
        # Check if code has any test method definitions
        test_method_pattern = re.compile(r'^\s+def\s+test_\w+\s*\(', re.MULTILINE)
        has_test_methods = bool(test_method_pattern.search(code))

        if not has_test_methods:
            # No test methods to validate (edge case)
            return None

        # Check for correct decorator
        if not cls.TEST_DECORATOR_PATTERN.search(code):
            # Check if wrong decorator type is used
            wrong_decorator_pattern = re.compile(
                r'@autologger\.automation_logger\s*\(\s*["\'](?!Test)["\']'
            )
            if wrong_decorator_pattern.search(code):
                return cls.fail_response(
                    error="Wrong decorator type. Must be @autologger.automation_logger(\"Test\") (IC-09-05 violation)",
                    fix_hint="Use @autologger.automation_logger(\"Test\") for test methods, not Role or Task."
                )
            return cls.fail_response(
                error="Missing @autologger.automation_logger(\"Test\") decorator (IC-09-05 violation)",
                fix_hint="Add @autologger.automation_logger(\"Test\") decorator to each test method."
            )

        return None

    @classmethod
    def _check_role_calls(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Check for at least one role method call (IC-09-03).

        Returns fail_response if no role calls found, None otherwise.
        """
        # Check if code has any test method definitions
        test_method_pattern = re.compile(r'^\s+def\s+test_\w+\s*\(', re.MULTILINE)
        has_test_methods = bool(test_method_pattern.search(code))

        if not has_test_methods:
            # No test methods to validate (edge case)
            return None

        # Check for role method calls
        if not cls.ROLE_CALL_PATTERN.search(code):
            return cls.fail_response(
                error="No role method calls found in test (IC-09-03 violation)",
                fix_hint="Test must call at least one role method. Add user.login(), user.browse(), etc."
            )

        return None

    @classmethod
    def _check_task_calls(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Check for Task method calls in test code (architecture violation).

        Tests should NOT call Task methods directly - they should use Roles.
        Tasks are the layer that Roles compose.

        Returns fail_response if Task calls detected, None otherwise.
        """
        if cls.TASK_CALL_PATTERN.search(code):
            return cls.fail_response(
                error="Task method call detected in test (architecture violation)",
                fix_hint="Tests should not call Task methods directly. Use Role methods: user.login(), not auth_tasks.log_in()."
            )
        return None

    @classmethod
    def _check_pom_actions(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Check for POM action method calls in test code (architecture violation).

        Tests should NOT call POM action methods directly - they should use Roles.
        POM action methods: enter_, click_, select_, type_, submit_, etc.
        POM state methods (is_, has_, get_) ARE allowed for assertions.

        Returns fail_response if POM action calls detected, None otherwise.
        """
        if cls.POM_ACTION_PATTERN.search(code):
            return cls.fail_response(
                error="POM action method call detected in test (architecture violation)",
                fix_hint="Tests should not call POM action methods. Use Role methods: user.login(), not login_page.enter_email()."
            )
        return None

    @classmethod
    def _check_assertions(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Check for proper POM state assertions (IC-09-04, DD-15).

        Returns fail_response if:
        - Return value assertion detected
        - Only weak assertions (assert True)
        - No POM state assertions

        Returns None if assertions are valid.
        """
        # Check for return value assertion pattern
        if cls.RETURN_ASSERTION_PATTERN.search(code):
            return cls.fail_response(
                error="Return value assertion detected (DD-15 violation)",
                fix_hint="Tests must assert via POM state methods. Replace 'result = role.method(); assert result' with 'role.method(); assert page.is_state()'."
            )

        # Check for weak assertions
        for pattern, description in cls.WEAK_ASSERTION_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                return cls.fail_response(
                    error=f"Weak assertion detected: {description} (IC-09-04 violation)",
                    fix_hint="Tests must assert via POM state methods. Replace 'assert True' with 'assert page.is_logged_in()' etc."
                )

        # Check for POM state assertions
        if not cls.POM_ASSERTION_PATTERN.search(code):
            return cls.fail_response(
                error="No POM state assertions found (DD-15 violation)",
                fix_hint="Tests must assert via POM state methods. Add assertions like 'assert self.page.is_logged_in()'."
            )

        return None

    @classmethod
    def _validate_metadata_structure(cls, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate metadata has required fields.

        Returns fail_response if invalid, None otherwise.
        """
        # Check class_name
        class_name = metadata.get("class_name")
        if class_name is None or not isinstance(class_name, str) or not class_name.strip():
            return cls.fail_response(
                error="Missing or invalid class_name in metadata",
                fix_hint="Tool 6 must include class_name in metadata."
            )

        # Check file_path
        file_path = metadata.get("file_path")
        if file_path is None or not isinstance(file_path, str) or not file_path.strip():
            return cls.fail_response(
                error="Missing or invalid file_path in metadata",
                fix_hint="Tool 6 must include file_path in metadata."
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
