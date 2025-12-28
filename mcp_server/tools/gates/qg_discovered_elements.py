"""
Quality Gate: Discovered Elements (Step 5).

PRE+POST validation gate for Tool 2 (discover_page_elements) or DD-33 (Playwright snapshot).

PRE Validation:
- Step 4 complete (test_scenarios exist in state)
- URL present and valid format (http/https)
- page_name present
- credential_strategy present and valid (IC-05-01)
- discovery_method present and valid ("tool2" or "playwright") (DD-33)

POST Validation:
- elements array present and not empty
- Each element has: suggested_name, element_type, at least one non-empty locator (IC-05-03)
- page_name is PascalCase (IC-05-02)

Enforces: DD-19, DD-20, DD-21, DD-24, DD-33, IC-05-01, IC-05-02, IC-05-03
"""

import re
from typing import Any, Dict

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGDiscoveredElements(BaseGate):
    """Quality gate for Step 5: Discovered Elements."""

    # Step number for this gate (used for attempt tracking)
    STEP_NUMBER = 5

    # Valid credential strategies (from DD-24)
    VALID_CREDENTIAL_STRATEGIES = {"none", "static", "dynamic", "self-contained"}

    # Valid discovery methods (from DD-33)
    VALID_DISCOVERY_METHODS = {"tool2", "playwright"}

    # PascalCase pattern (IC-05-02): starts with uppercase, alphanumeric
    PASCAL_CASE_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        return StateManager()

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation before Tool 2 operation or DD-33 snapshot extraction.

        Validates:
        - Step 4 is complete
        - URL is present and valid format
        - page_name is present
        - credential_strategy is present and valid (IC-05-01)
        - discovery_method is present and valid (DD-33)

        Args:
            input_data: Dict with url, page_name, credential_strategy, discovery_method

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 4 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(4):
            return cls.fail_response(
                error="Step 4 is not complete. Cannot proceed to Step 5.",
                fix_hint="Complete Step 4 (Test Scenarios) first. Ensure test_scenarios are generated."
            )

        # Validate URL
        url = input_data.get("url")
        if url is None:
            return cls.fail_response(
                error="Missing required field: url",
                fix_hint="Provide the target URL from Step 2 state."
            )

        if not isinstance(url, str) or not url.strip():
            return cls.fail_response(
                error="url must be a non-empty string",
                fix_hint="Provide a valid URL like 'http://example.com/page'"
            )

        if not url.startswith("http://") and not url.startswith("https://"):
            return cls.fail_response(
                error="url must start with http:// or https://",
                fix_hint="Use full URL format: http://example.com or https://example.com"
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

        # Validate credential_strategy (IC-05-01)
        credential_strategy = input_data.get("credential_strategy")
        if credential_strategy is None:
            return cls.fail_response(
                error="Missing required field: credential_strategy (IC-05-01)",
                fix_hint=f"Provide credential_strategy from Step 1. Valid options: {', '.join(sorted(cls.VALID_CREDENTIAL_STRATEGIES))}"
            )

        if credential_strategy not in cls.VALID_CREDENTIAL_STRATEGIES:
            return cls.fail_response(
                error=f"Invalid credential_strategy: '{credential_strategy}'",
                fix_hint=f"Use one of: {', '.join(sorted(cls.VALID_CREDENTIAL_STRATEGIES))}"
            )

        # Validate discovery_method (DD-33)
        discovery_method = input_data.get("discovery_method")
        if discovery_method is None:
            return cls.fail_response(
                error="Missing required field: discovery_method (DD-33)",
                fix_hint=f"Declare discovery_method. Use 'playwright' if Playwright prepared page state, 'tool2' for static pages. Valid options: {', '.join(sorted(cls.VALID_DISCOVERY_METHODS))}"
            )

        if discovery_method not in cls.VALID_DISCOVERY_METHODS:
            return cls.fail_response(
                error=f"Invalid discovery_method: '{discovery_method}'",
                fix_hint=f"Use one of: {', '.join(sorted(cls.VALID_DISCOVERY_METHODS))}. Use 'playwright' if Playwright prepared page state."
            )

        return cls.pass_response()

    @classmethod
    def validate_post(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST validation after Tool 2 operation or DD-33 snapshot extraction.

        Validates:
        - elements array is present and not empty
        - Each element has: suggested_name, element_type, at least one non-empty locator (IC-05-03)
        - page_name is PascalCase (IC-05-02)

        On PASS: Saves Step 5 state (enables DD-33 flow where Tool 2 is skipped).

        Args:
            input_data: Dict with elements array and page_name

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
            or {"status": "blocked", ...} if max attempts exceeded
        """
        # P1: Check if blocked due to max attempts
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

        # P2: Extract source from input_data for audit logging
        source = input_data.get("source")

        # P1: Track attempts and log to audit
        if state_manager:
            if result.get("status") == "fail":
                state_manager.increment_attempt(cls.STEP_NUMBER)
                if cls._audit_logger:
                    cls._audit_logger.log_gate(
                        step=cls.STEP_NUMBER,
                        gate_name="qg_discovered_elements",
                        mode="POST",
                        result="fail",
                        error=result.get("error"),
                        source=source
                    )
            elif result.get("status") == "pass":
                state_manager.reset_attempts(cls.STEP_NUMBER)
                if cls._audit_logger:
                    cls._audit_logger.log_gate(
                        step=cls.STEP_NUMBER,
                        gate_name="qg_discovered_elements",
                        mode="POST",
                        result="pass",
                        source=source
                    )

        return result

    @classmethod
    def _validate_post_internal(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Internal validation logic (separated for attempt tracking)."""
        # Validate elements array
        elements = input_data.get("elements")

        if elements is None:
            return cls.fail_response(
                error="Missing required field: elements",
                fix_hint="Tool 2 must return elements array."
            )

        if not isinstance(elements, list):
            return cls.fail_response(
                error="elements must be a list",
                fix_hint="Tool 2 should return elements as an array."
            )

        if len(elements) == 0:
            return cls.fail_response(
                error="elements is empty. At least one interactive element required.",
                fix_hint="Retry Tool 2 - ensure page has interactive elements or prepare page state (DD-20)."
            )

        # Validate each element
        for i, element in enumerate(elements):
            element_error = cls._validate_element(element, i)
            if element_error:
                return element_error

        # Validate page_name PascalCase (IC-05-02)
        page_name = input_data.get("page_name")
        if page_name is None:
            return cls.fail_response(
                error="Missing required field: page_name",
                fix_hint="Provide page_name for the discovered elements."
            )

        if not isinstance(page_name, str) or not page_name.strip():
            return cls.fail_response(
                error="page_name must be a non-empty string",
                fix_hint="Provide a descriptive page name."
            )

        if not cls.PASCAL_CASE_PATTERN.match(page_name):
            return cls.fail_response(
                error=f"page_name '{page_name}' is not PascalCase (IC-05-02)",
                fix_hint="Use PascalCase format: 'LoginPage', 'CartModal', 'CheckoutForm'"
            )

        # Save Step 5 state on POST-VALIDATE pass (enables DD-33 flow)
        state_manager = cls._get_state_manager()
        state_manager.save(5, {
            "discovered_elements": elements,
            "page_name": page_name
        })

        return cls.pass_response()

    @classmethod
    def _validate_element(cls, element: Any, index: int) -> Dict[str, Any] | None:
        """
        Validate a single element structure.

        Returns fail_response dict if invalid, None if valid.
        """
        if not isinstance(element, dict):
            return cls.fail_response(
                error=f"Element {index} is not a valid object",
                fix_hint="Each element must be a dictionary with suggested_name, element_type, and locators."
            )

        # Check suggested_name
        suggested_name = element.get("suggested_name")
        if suggested_name is None:
            return cls.fail_response(
                error=f"Element {index} missing required field: suggested_name",
                fix_hint="Each element must have a suggested_name."
            )

        if not isinstance(suggested_name, str) or not suggested_name.strip():
            return cls.fail_response(
                error=f"Element {index} suggested_name must be a non-empty string",
                fix_hint="Provide a descriptive name like 'EMAIL_INPUT', 'SUBMIT_BUTTON'."
            )

        # Check element_type
        element_type = element.get("element_type")
        if element_type is None:
            return cls.fail_response(
                error=f"Element {index} missing required field: element_type",
                fix_hint="Each element must have an element_type (e.g., 'textbox', 'button')."
            )

        if not isinstance(element_type, str) or not element_type.strip():
            return cls.fail_response(
                error=f"Element {index} element_type must be a non-empty string",
                fix_hint="Provide element type like 'textbox', 'button', 'link'."
            )

        # Check locators (IC-05-03): at least one non-empty locator required
        locator_id = element.get("locator_id", "")
        locator_css = element.get("locator_css", "")
        locator_xpath = element.get("locator_xpath", "")

        # Check if at least one locator is non-empty
        has_valid_locator = (
            (isinstance(locator_id, str) and locator_id.strip()) or
            (isinstance(locator_css, str) and locator_css.strip()) or
            (isinstance(locator_xpath, str) and locator_xpath.strip())
        )

        if not has_valid_locator:
            return cls.fail_response(
                error=f"Element {index} has no valid locator (IC-05-03)",
                fix_hint="At least one of locator_id, locator_css, or locator_xpath must be non-empty."
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
