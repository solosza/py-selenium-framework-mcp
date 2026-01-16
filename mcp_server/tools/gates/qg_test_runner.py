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
- No test orchestration: tests call ONE workflow method (Pattern-based Smart Gate)
- POM state assertions used, no return value assertions (IC-09-04, DD-15)
- @autologger.automation_logger("Test") decorator present (IC-09-05)
- Semantic validation (FR-14.1, FR-14.3): via pluggable semantic rules
- Import paths match metadata (DD-18): validates Role and POM imports
- No redundant tests (DEF-046): one test's role calls cannot be subset of another
- metadata present with class_name and file_path

Enforces: DD-15, DD-18, DD-25, DEF-046, FR-14.1, FR-14.3, IC-09-01 through IC-09-05
"""

import re
from typing import Any, Dict, Optional

from .base_gate import BaseGate
from utils.state_manager import StateManager
from .semantic_rules.registry import SEMANTIC_RULES


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
        # Task 18.0: Use per-run state isolation
        audit_logger = cls.get_audit_logger()
        return StateManager(run_id=audit_logger.run_id)

    @classmethod
    def _import_path_to_file_path(cls, import_path: str) -> str:
        """
        Convert Python import path to file system path.

        Task 18.0 (DEF-051): Helper for immediate file writes.

        Args:
            import_path: e.g., "tests.auth.test_login"

        Returns:
            Absolute file path: e.g., "D:/project/tests/auth/test_login.py"
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
    def _write_test_file(cls, file_path: str, code: str) -> None:
        """
        Write test code to disk immediately.

        Task 18.0 (DEF-051): Ensures test files are saved.

        Args:
            file_path: Absolute path to write file
            code: Test code content
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

        return cls.pass_response(
            step=9,
            gate_name="qg_test_runner",
            mode="PRE",
            metadata={"scenarios_count": len(test_scenarios)}
        )

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

        # DEF-046: Check for redundant tests FIRST (more specific than orchestration)
        redundancy_error = cls._detect_redundant_tests(code)
        if redundancy_error:
            return redundancy_error

        # Check for test orchestration (Pattern-based Smart Gate)
        # Runs after redundancy to avoid flagging redundancy test scenarios
        orchestration_response = cls._check_test_orchestration(code, input_data)
        if orchestration_response:
            return orchestration_response

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

        # FR-14.1, FR-14.3: Run pluggable semantic rules
        semantic_error = cls._check_semantic_rules(code, input_data)
        if semantic_error:
            return semantic_error

        # DD-18: Validate import paths match metadata
        import_error = cls._check_imports(code, input_data)
        if import_error:
            return import_error

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

        # Task 18.0 (DEF-051 FIX): Write test file immediately to disk
        file_path = metadata.get("file_path")
        if file_path:
            try:
                # Ensure absolute path
                from pathlib import Path
                path_obj = Path(file_path)
                if not path_obj.is_absolute():
                    # Get project root (3 levels up from mcp_server/tools/gates/)
                    project_root = Path(__file__).parent.parent.parent.parent
                    file_path = str(project_root / file_path)

                # Write file to disk
                cls._write_test_file(file_path, code)

                # Log file write to audit trail
                audit_logger = cls.get_audit_logger()
                audit_logger.log_file_generated(file_path, step=9)
            except Exception as e:
                # DEF-055b FIX: Log file write failure instead of silently swallowing
                # Don't block (validation already passed) but DO log the error
                audit_logger = cls.get_audit_logger()
                audit_logger.log_gate(
                    step=9,
                    gate_name="qg_test_runner",
                    mode="POST",
                    result="warning",
                    error=f"FILE_WRITE_FAILED: {file_path} - {str(e)}"
                )

        return cls.pass_response(
            step=9,
            gate_name="qg_test_runner",
            mode="POST",
            metadata={
                "test_name": metadata.get("test_name"),
                "file_path": metadata.get("file_path")
            }
        )

    @classmethod
    def _detect_skeleton_code(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect skeleton code patterns in generated code (DD-25, IC-09-02).

        Returns fail_response if skeleton detected, None otherwise.
        """
        for pattern, description in cls.SKELETON_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                return cls.fail_response(
                    error=f"Skeleton code detected: {description}",
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
    def _check_test_orchestration(cls, code: str, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check for test orchestration - tests should call ONE workflow method (Pattern-based Smart Gate).

        Architecture rule (step-09.md lines 509-515):
        - Tests should call ONE Role workflow method
        - Tests should NOT orchestrate by calling multiple Role methods on SAME persona
        - Exception: Multi-persona scenarios (different roles) are valid

        Pattern-based Smart Gate (Layer 2):
        - Detects multiple Role method calls on same persona
        - Provides correct pattern from step-09.md
        - AI generates fix from pattern

        Returns NEEDS_RETRY response with pattern if orchestration detected, None otherwise.
        """
        # Extract role class name from metadata for pattern
        metadata = input_data.get("metadata", {})
        role_used = metadata.get("role_used", "RoleClass")

        # Find all test methods
        test_methods = re.findall(
            r'def\s+(test_\w+)\s*\([^)]*\):(.*?)(?=\n    def\s+|\n\nclass\s+|\Z)',
            code,
            re.DOTALL
        )

        for test_name, test_body in test_methods:
            # Find all Role instantiations (variable = RoleClass(...))
            role_instances = re.findall(
                r'(\w+)\s*=\s*(\w+)\s*\(',
                test_body
            )

            # Count Role method calls per instance variable
            role_calls_by_instance = {}
            for var_name, _ in role_instances:
                # Find calls like: var_name.method_name(...)
                calls = re.findall(
                    rf'{var_name}\.(\w+)\s*\(',
                    test_body
                )
                if calls:
                    role_calls_by_instance[var_name] = calls

            # Check for orchestration: SINGLE persona with MULTIPLE method calls
            for var_name, method_calls in role_calls_by_instance.items():
                if len(method_calls) > 1:
                    # Check if this is multi-persona scenario (valid exception)
                    # If there are multiple different role variables, it's multi-persona
                    if len(role_calls_by_instance) > 1:
                        # Multi-persona: multiple different roles - VALID
                        continue

                    # Single persona orchestration detected
                    # Provide pattern from step-09.md (lines 529-540)
                    pattern = f"""# ❌ WRONG: Orchestrating workflow in test
def {test_name}(self):
    {var_name}.{method_calls[0]}()  # Multiple calls that should be
    {var_name}.{method_calls[1]}()  # ONE Role method like
    ...                             # {var_name}.complete_workflow()

# ✅ CORRECT PATTERN (from step-09.md):

# IN ROLE: Create workflow method
class {role_used}:
    @autologger.automation_logger("Role")
    def complete_workflow(self, ...params...) -> None:
        \"\"\"Complete workflow: orchestrates MULTIPLE tasks.\"\"\"
        self.task1()
        self.task2()
        self.task3()
        # NO return - test asserts via POM

# IN TEST: Call ONE workflow method (DD-49: no base_url)
@autologger.automation_logger("Test")
def {test_name}(self):
    # Arrange
    {var_name} = {role_used}(self.web, data)

    # Act - ONE Role call
    {var_name}.complete_workflow(params)

    # Assert - Via POM state methods
    assert self.page.is_success()
"""

                    return {
                        "status": "NEEDS_RETRY",
                        "pattern": pattern,
                        "error": f"Test orchestration detected: {len(method_calls)} Role method calls on single persona (violates architecture)",
                        "message": f"Tests should call ONE workflow method, not orchestrate multiple calls. Create workflow method in Role that orchestrates these operations."
                    }

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
                error="Return value assertion detected",
                fix_hint="Tests must assert via POM state methods. Replace 'result = role.method(); assert result' with 'role.method(); assert page.is_state()'."
            )

        # Check for weak assertions
        for pattern, description in cls.WEAK_ASSERTION_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                return cls.fail_response(
                    error=f"Weak assertion detected: {description}",
                    fix_hint="Tests must assert via POM state methods. Replace 'assert True' with 'assert page.is_logged_in()' etc."
                )

        # Check for POM state assertions
        if not cls.POM_ASSERTION_PATTERN.search(code):
            return cls.fail_response(
                error="No POM state assertions found",
                fix_hint="Tests must assert via POM state methods. Add assertions like 'assert self.page.is_logged_in()'."
            )

        return None

    @classmethod
    def _check_semantic_rules(cls, code: str, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Run pluggable semantic validation rules (FR-14.1, FR-14.3).

        Semantic rules validate MEANING and LOGIC in generated code,
        not just structure (syntax, imports, patterns).

        Examples:
        - Parameter contradictions (from_account == to_account)
        - Test data location violations (imports from wrong location)
        - Strategy violations (Role uses wrong credential strategy)

        Returns NEEDS_RETRY response if any semantic rule fails, None otherwise.
        """
        # Build context for semantic rules
        state_manager = cls._get_state_manager()
        step_1_data = state_manager.get_step(1) or {}

        context = {
            "step_1_config": step_1_data,
            "role_metadata": input_data.get("role_metadata"),
            "pom_metadata": input_data.get("pom_metadata"),
            "test_scenarios": input_data.get("test_scenarios"),
        }

        # Run all registered semantic rules
        result = SEMANTIC_RULES.check_all(code, context)
        if result:
            # Semantic rule failed - propagate error
            return result

        return None

    @classmethod
    def _check_imports(cls, code: str, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate import paths match metadata (DD-18) - Smart Gate Layer 2.

        Checks that:
        - Role imports match role_metadata.import_path
        - POM imports match pom_metadata.*.import_path

        Smart Gate Pattern:
        - Detects wrong imports
        - Automatically fixes them
        - Returns corrected code for retry

        Returns NEEDS_RETRY response with corrected code if mismatch detected, None otherwise.
        """
        # Extract role_metadata and pom_metadata from input_data
        role_metadata = input_data.get("role_metadata", {})
        pom_metadata = input_data.get("pom_metadata", {})

        # Extract all import statements from code
        import_pattern = re.compile(r'^from\s+([\w.]+)\s+import\s+(\w+)', re.MULTILINE)
        imports = import_pattern.findall(code)

        # Build expected imports map
        expected_imports = {}

        # Add expected role import
        if role_metadata and isinstance(role_metadata, dict):
            role_class = role_metadata.get("class_name")
            role_import_path = role_metadata.get("import_path")
            if role_class and role_import_path:
                expected_imports[role_class] = role_import_path

        # Add expected POM imports
        if pom_metadata and isinstance(pom_metadata, dict):
            for pom_key, pom_data in pom_metadata.items():
                if isinstance(pom_data, dict):
                    pom_class = pom_data.get("class_name")
                    pom_import_path = pom_data.get("import_path")
                    if pom_class and pom_import_path:
                        expected_imports[pom_class] = pom_import_path

        # Check each import in code against expected
        for import_path, class_name in imports:
            if class_name in expected_imports:
                expected_path = expected_imports[class_name]
                if import_path != expected_path:
                    # Smart Gate Layer 2: Fix the import and provide corrected code
                    wrong_import = f"from {import_path} import {class_name}"
                    correct_import = f"from {expected_path} import {class_name}"
                    fixed_code = code.replace(wrong_import, correct_import)

                    return {
                        "status": "NEEDS_RETRY",
                        "fix_applied": "import_path_corrected",
                        "corrected_code": fixed_code,
                        "error": f"DD-18: Wrong import path for {class_name}",
                        "message": f"Import path corrected from '{import_path}' to '{expected_path}'. Retry with corrected code."
                    }

        return None

    @classmethod
    def _detect_redundant_tests(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect redundant tests (DEF-046).

        Checks if one test's role calls are a subset of another test's role calls.
        This indicates redundancy: one user story should map to ONE E2E test.

        Returns fail_response if redundancy detected, None otherwise.
        """
        # Extract all test methods
        test_methods = cls._extract_test_methods(code)

        if len(test_methods) <= 1:
            # Only one test or no tests - no redundancy possible
            return None

        # For each pair of tests, check if one is a subset of another
        for i, test_a in enumerate(test_methods):
            for j, test_b in enumerate(test_methods):
                if i >= j:
                    continue  # Skip self-comparison and already compared pairs

                # Extract role calls from both tests
                calls_a = set(test_a['role_calls'])
                calls_b = set(test_b['role_calls'])

                # Check if one is a subset of the other
                if calls_a.issubset(calls_b) and calls_a != calls_b:
                    return cls.fail_response(
                        error=f"Redundant test detected: '{test_a['name']}' is a subset of '{test_b['name']}'",
                        fix_hint=f"One user story should map to ONE E2E test (MVP constraint). Merge '{test_a['name']}' into '{test_b['name']}' or split user story."
                    )
                elif calls_b.issubset(calls_a) and calls_a != calls_b:
                    return cls.fail_response(
                        error=f"Redundant test detected: '{test_b['name']}' is a subset of '{test_a['name']}'",
                        fix_hint=f"One user story should map to ONE E2E test (MVP constraint). Merge '{test_b['name']}' into '{test_a['name']}' or split user story."
                    )

        return None

    @classmethod
    def _extract_test_methods(cls, code: str) -> list:
        """
        Extract all test methods with their role calls.

        Returns:
            List of dicts with 'name' and 'role_calls' keys.
        """
        # Find all test method definitions
        # Match from 'def test_*' to the next 'def ' or end of file
        test_pattern = re.compile(
            r'def\s+(test_\w+)\s*\([^)]*\):(.*?)(?=\n\s*(?:def\s+|\Z))',
            re.DOTALL
        )

        test_methods = []
        for match in test_pattern.finditer(code):
            method_name = match.group(1)
            method_body = match.group(2)

            # Extract role method calls from this test
            role_calls = cls._extract_role_calls(method_body)

            test_methods.append({
                'name': method_name,
                'role_calls': role_calls
            })

        return test_methods

    @classmethod
    def _extract_role_calls(cls, method_body: str) -> list:
        """
        Extract role method calls from a test method body.

        Matches patterns like: user.login(), admin.create_user(), guest.browse()
        Excludes POM method calls like: self.page.is_logged_in(), page.has_error()

        Returns:
            List of role method names (e.g., ['login', 'browse_category'])
        """
        role_calls = []

        # Use the existing ROLE_CALL_PATTERN
        for match in cls.ROLE_CALL_PATTERN.finditer(method_body):
            full_match = match.group(0)

            # Exclude calls that start with 'self.' (those are POM calls)
            # Look back to see if there's 'self.' before the match
            match_start = match.start()
            if match_start >= 5:  # len('self.') = 5
                prefix = method_body[match_start-5:match_start]
                if prefix == 'self.':
                    continue  # Skip POM calls

            # Exclude POM state method calls (is_, has_, get_)
            method_name = full_match.split('.')[-1].rstrip('(').strip()
            if method_name.startswith(('is_', 'has_', 'get_')):
                continue  # Skip POM state methods

            role_calls.append(method_name)

        return role_calls

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
