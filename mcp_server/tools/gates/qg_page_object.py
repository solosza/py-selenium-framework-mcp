"""
Quality Gate: Page Object (Step 6).

PRE+POST validation gate for Tool 3 (generate_page_object).

PRE Validation:
- Step 5 complete (discovered_elements, page_name exist in state)
- discovered_elements present and not empty
- page_name present and PascalCase
- expected_states present (optional but recommended)

POST Validation:
- code field present and not empty
- metadata field present with required structure
- No skeleton code (DD-25): pass, # Add..., NotImplementedError, # TODO:
- locators array present and not empty
- action_methods present and not empty when locators exist (IC-06-03)
- state_methods present and not empty
- state_methods match expected_states if provided (IC-06-01)
- class_name and import_path present (DD-26)

Enforces: DD-09, DD-25, DD-26, IC-06-01, IC-06-02, IC-06-03
"""

import re
from typing import Any, Dict, List, Optional

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGPageObject(BaseGate):
    """Quality gate for Step 6: Page Object Generation."""

    # PascalCase pattern (same as IC-05-02): starts with uppercase, alphanumeric
    PASCAL_CASE_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    # Skeleton code patterns (DD-25, IC-06-02)
    SKELETON_PATTERNS = [
        (r'^\s*pass\s*$', 'pass statement'),
        (r'#\s*[Aa]dd\s+.*\s+as\s+needed', 'placeholder comment'),
        (r'raise\s+NotImplementedError', 'NotImplementedError'),
        (r'#\s*TODO:', 'TODO comment'),
    ]

    # Layer violation patterns - POMs should NOT have these imports
    LAYER_VIOLATION_PATTERNS = [
        (r'from\s+tasks\.', 'Task import in POM'),
        (r'from\s+roles\.', 'Role import in POM'),
        (r'import\s+tasks\.', 'Task import in POM'),
        (r'import\s+roles\.', 'Role import in POM'),
    ]

    # Trivial state method pattern - returns True without checking element
    TRIVIAL_STATE_PATTERN = re.compile(
        r'def\s+(is_|has_)\w+\s*\([^)]*\)\s*->\s*bool:\s*\n\s*"""[^"]*"""\s*\n\s*return\s+True\s*$',
        re.MULTILINE
    )

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        return StateManager()

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation before Tool 3 operation.

        Validates:
        - Step 5 is complete
        - discovered_elements present and not empty
        - page_name present and PascalCase
        - expected_states present (optional)

        Args:
            input_data: Dict with discovered_elements, page_name, expected_states

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 5 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(5):
            return cls.fail_response(
                error="Step 5 is not complete. Cannot proceed to Step 6.",
                fix_hint="Complete Step 5 (Discover Elements) first. Ensure discovered_elements are generated."
            )

        # Validate discovered_elements
        discovered_elements = input_data.get("discovered_elements")

        if discovered_elements is None:
            return cls.fail_response(
                error="Missing required field: discovered_elements",
                fix_hint="Provide discovered_elements from Step 5 state."
            )

        if not isinstance(discovered_elements, list):
            return cls.fail_response(
                error="discovered_elements must be a list",
                fix_hint="Provide discovered_elements as an array from Tool 2 output."
            )

        if len(discovered_elements) == 0:
            return cls.fail_response(
                error="discovered_elements is empty. At least one element required.",
                fix_hint="Go back to Step 5 - ensure Tool 2 discovers elements."
            )

        # Validate page_name
        page_name = input_data.get("page_name")

        if page_name is None:
            return cls.fail_response(
                error="Missing required field: page_name",
                fix_hint="Provide page_name (e.g., 'LoginPage', 'CartPage')."
            )

        if not isinstance(page_name, str) or not page_name.strip():
            return cls.fail_response(
                error="page_name must be a non-empty string",
                fix_hint="Provide a descriptive page name like 'LoginPage'."
            )

        if not cls.PASCAL_CASE_PATTERN.match(page_name):
            return cls.fail_response(
                error=f"page_name '{page_name}' is not PascalCase",
                fix_hint="Use PascalCase format: 'LoginPage', 'CartModal', 'CheckoutForm'"
            )

        # expected_states is optional but recommended (don't fail if missing)

        return cls.pass_response()

    # Step number for this gate (used for attempt tracking)
    STEP_NUMBER = 6

    @classmethod
    def validate_post(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST validation after Tool 3 operation.

        Validates:
        - code field present and not empty
        - No skeleton code (DD-25, IC-06-02)
        - metadata present with required structure (DD-26)
        - locators, action_methods, state_methods arrays valid
        - state_methods match expected_states if provided (IC-06-01)

        Args:
            input_data: Dict with code, metadata, expected_states

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
                    errors=[]  # Error history not tracked in simple impl
                )

        # Run actual validation
        result = cls._validate_post_internal(input_data)

        # Task 2.0: Track attempts and log to audit
        if state_manager:
            if result.get("status") == "fail":
                state_manager.increment_attempt(cls.STEP_NUMBER)
                # Log failure to audit
                if cls._audit_logger:
                    cls._audit_logger.log_gate(
                        step=cls.STEP_NUMBER,
                        gate_name="qg_page_object",
                        mode="POST",
                        result="fail",
                        error=result.get("error")
                    )
            elif result.get("status") == "pass":
                state_manager.reset_attempts(cls.STEP_NUMBER)

        return result

    @classmethod
    def _validate_post_internal(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal validation logic (separated for attempt tracking)."""
        # Validate code field
        code = input_data.get("code")

        if code is None:
            return cls.fail_response(
                error="Missing required field: code",
                fix_hint="Tool 3 must return generated POM code."
            )

        if not isinstance(code, str) or not code.strip():
            return cls.fail_response(
                error="code is empty",
                fix_hint="Tool 3 must generate non-empty POM code."
            )

        # Check for skeleton code (DD-25, IC-06-02)
        skeleton_error = cls._detect_skeleton_code(code)
        if skeleton_error:
            return skeleton_error

        # Check for layer violations (POM should not import Task/Role)
        layer_error = cls._detect_layer_violations(code)
        if layer_error:
            return layer_error

        # Check for trivial state methods (skeleton variant)
        trivial_error = cls._detect_trivial_state_methods(code)
        if trivial_error:
            return trivial_error

        # Validate metadata field
        metadata = input_data.get("metadata")

        if metadata is None:
            return cls.fail_response(
                error="Missing required field: metadata",
                fix_hint="Tool 3 must return metadata for downstream tools."
            )

        if not isinstance(metadata, dict):
            return cls.fail_response(
                error="metadata must be a dictionary",
                fix_hint="Tool 3 should return metadata as an object."
            )

        # Validate metadata structure (DD-26)
        metadata_error = cls._validate_metadata_structure(metadata)
        if metadata_error:
            return metadata_error

        # Validate locators
        locators_error = cls._validate_locators(metadata)
        if locators_error:
            return locators_error

        # Validate action_methods (IC-06-03)
        action_error = cls._validate_action_methods(metadata)
        if action_error:
            return action_error

        # Validate state_methods (DD-09)
        state_error = cls._validate_state_methods(metadata)
        if state_error:
            return state_error

        # Validate state_methods match expected_states (IC-06-01)
        expected_states = input_data.get("expected_states")
        if expected_states:
            match_error = cls._validate_state_methods_match(metadata, expected_states)
            if match_error:
                return match_error

        # Save Step 6 state on POST-VALIDATE pass
        internal_state_manager = cls._get_state_manager()
        internal_state_manager.save(step=6, data={
            "pom_code": code,
            "pom_metadata": metadata
        })

        return cls.pass_response()

    @classmethod
    def _detect_skeleton_code(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect skeleton code patterns in generated code.

        Returns fail_response if skeleton detected, None otherwise.
        """
        for pattern, description in cls.SKELETON_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                return cls.fail_response(
                    error=f"Skeleton code detected: {description} (DD-25 violation)",
                    fix_hint="AI must complete the code. Remove placeholders, implement all methods."
                )
        return None

    @classmethod
    def _detect_layer_violations(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect layer violation patterns - POM should not import Task/Role.

        Returns fail_response if violation detected, None otherwise.
        """
        for pattern, description in cls.LAYER_VIOLATION_PATTERNS:
            if re.search(pattern, code):
                return cls.fail_response(
                    error=f"Layer violation detected: {description} (architecture violation)",
                    fix_hint="POMs should only import WebInterface. Tasks and Roles are higher layers that use POMs, not the other way around."
                )
        return None

    @classmethod
    def _detect_trivial_state_methods(cls, code: str) -> Optional[Dict[str, Any]]:
        """
        Detect trivial state methods that just return True without element check.

        A proper state method should check an actual element, not just return True.

        Returns fail_response if trivial state method detected, None otherwise.
        """
        if cls.TRIVIAL_STATE_PATTERN.search(code):
            return cls.fail_response(
                error="Trivial state method detected: returns True without checking element (DD-25 violation)",
                fix_hint="State methods must check actual elements. Replace 'return True' with 'return self.web.is_element_displayed(*self.LOCATOR)'."
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
                fix_hint="Tool 3 must include class_name in metadata."
            )

        # Check import_path
        import_path = metadata.get("import_path")
        if import_path is None or not isinstance(import_path, str) or not import_path.strip():
            return cls.fail_response(
                error="Missing or invalid import_path in metadata",
                fix_hint="Tool 3 must include import_path in metadata."
            )

        return None

    @classmethod
    def _validate_locators(cls, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate locators array in metadata.

        Returns fail_response if invalid, None otherwise.
        """
        locators = metadata.get("locators")

        if locators is None:
            return cls.fail_response(
                error="Missing locators in metadata",
                fix_hint="Tool 3 must include locators array in metadata."
            )

        if not isinstance(locators, list):
            return cls.fail_response(
                error="locators must be a list",
                fix_hint="Tool 3 should return locators as an array."
            )

        if len(locators) == 0:
            return cls.fail_response(
                error="locators is empty. At least one locator required.",
                fix_hint="Check that discovered_elements were processed correctly."
            )

        return None

    @classmethod
    def _validate_action_methods(cls, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate action_methods array in metadata (IC-06-03).

        Returns fail_response if invalid, None otherwise.
        """
        action_methods = metadata.get("action_methods")

        if action_methods is None:
            return cls.fail_response(
                error="Missing action_methods in metadata",
                fix_hint="Tool 3 must include action_methods array in metadata."
            )

        if not isinstance(action_methods, list):
            return cls.fail_response(
                error="action_methods must be a list",
                fix_hint="Tool 3 should return action_methods as an array."
            )

        # IC-06-03: If locators exist but action_methods is empty, it's a data quality issue
        locators = metadata.get("locators", [])
        if len(locators) > 0 and len(action_methods) == 0:
            return cls.fail_response(
                error="action_methods is empty but locators exist (IC-06-03 violation)",
                fix_hint="Element types from Tool 2 may be missing/invalid. Check element_type values."
            )

        return None

    @classmethod
    def _validate_state_methods(cls, metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate state_methods array in metadata (DD-09).

        Returns fail_response if invalid, None otherwise.
        """
        state_methods = metadata.get("state_methods")

        if state_methods is None:
            return cls.fail_response(
                error="Missing state_methods in metadata",
                fix_hint="Tool 3 must include state_methods array in metadata."
            )

        if not isinstance(state_methods, list):
            return cls.fail_response(
                error="state_methods must be a list",
                fix_hint="Tool 3 should return state_methods as an array."
            )

        if len(state_methods) == 0:
            return cls.fail_response(
                error="state_methods is empty. At least one state-check method required.",
                fix_hint="Provide expected_states from Step 3 to generate state-check methods."
            )

        return None

    @classmethod
    def _validate_state_methods_match(
        cls,
        metadata: Dict[str, Any],
        expected_states: List[Dict[str, str]]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate state_methods match expected_states (IC-06-01).

        Each expected_state must have a corresponding state_method.

        Returns fail_response if mismatch, None otherwise.
        """
        state_methods = metadata.get("state_methods", [])
        state_method_names = {m.get("name") for m in state_methods if isinstance(m, dict)}

        missing_methods = []
        for expected in expected_states:
            if isinstance(expected, dict):
                expected_name = expected.get("name")
                if expected_name and expected_name not in state_method_names:
                    missing_methods.append(expected_name)

        if missing_methods:
            return cls.fail_response(
                error=f"state_methods missing for expected_states: {', '.join(missing_methods)} (IC-06-01 violation)",
                fix_hint="Ensure Tool 3 receives expected_states and generates matching state-check methods."
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
        mode = input_data.get("mode", "").upper()

        if mode == "PRE":
            return cls.validate_pre(input_data)
        elif mode == "POST":
            return cls.validate_post(input_data)
        else:
            return cls.fail_response(
                error=f"Invalid mode: '{mode}'. Must be 'PRE' or 'POST'.",
                fix_hint="Specify mode='PRE' for input validation or mode='POST' for output validation."
            )
