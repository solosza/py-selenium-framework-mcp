"""
BaseGate - Base class with shared validation utilities for quality gates.

Task 3.0 - Provides common functionality for all quality gates:
- Response formatting (pass/fail)
- Skeleton code detection (DD-25)
- Locator detection (DD-27)
- POM assertion validation (DD-15)
- Required field validation
"""

import re
from typing import List


class BaseGate:
    """Base class with shared validation utilities for quality gates."""

    # DD-25: Skeleton code patterns to detect
    SKELETON_PATTERNS = [
        (r'^\s*pass\s*$', "Empty 'pass' statement"),
        (r'#\s*Add\s+.*\s+as needed', "Placeholder comment '# Add ... as needed'"),
        (r'#\s*TODO', "TODO comment"),
        (r'#\s*FIXME', "FIXME comment"),
        (r'#\s*XXX', "XXX comment"),
    ]

    # DD-27: Locator patterns to detect
    LOCATOR_PATTERNS = [
        r'from selenium\.webdriver\.common\.by import By',
        r'By\.ID',
        r'By\.CSS_SELECTOR',
        r'By\.XPATH',
        r'By\.CLASS_NAME',
        r'By\.NAME',
        r'By\.TAG_NAME',
        r'By\.LINK_TEXT',
        r'By\.PARTIAL_LINK_TEXT',
    ]

    @staticmethod
    def pass_response() -> dict:
        """Return standard pass response."""
        return {"status": "pass"}

    @staticmethod
    def fail_response(error: str, fix_hint: str) -> dict:
        """Return standard fail response with error and fix hint."""
        return {
            "status": "fail",
            "error": error,
            "fix_hint": fix_hint
        }

    @classmethod
    def detect_skeleton_code(cls, code: str) -> List[str]:
        """
        DD-25: Detect skeleton code indicators.

        Returns list of detected skeleton patterns (empty if clean).
        """
        if not code or not code.strip():
            return []

        detected = []
        for pattern, description in cls.SKELETON_PATTERNS:
            if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
                detected.append(description)

        return detected

    @staticmethod
    def validate_required_fields(data: dict, required: List[str]) -> List[str]:
        """
        Validate that all required fields are present in data.

        Returns list of missing field names (empty if all present).
        """
        if not required:
            return []

        missing = []
        for field in required:
            if field not in data:
                missing.append(field)

        return missing

    @classmethod
    def has_locators(cls, code: str) -> bool:
        """
        DD-27: Detect locator usage in code.

        Returns True if locators (By.*, etc.) are found.
        """
        if not code:
            return False

        for pattern in cls.LOCATOR_PATTERNS:
            if re.search(pattern, code):
                return True

        return False

    @staticmethod
    def validate_pom_assertions(test_code: str) -> bool:
        """
        DD-15: Validate test assertions use POM state methods.

        Returns True if assertions follow pattern: page.is_*, page.has_*, page.get_*
        Returns False if assertions are on return values.
        """
        if not test_code:
            return True

        # Pattern for valid POM assertions: assert <obj>.is_*(), assert <obj>.has_*(), assert <obj>.get_*()
        pom_assertion_pattern = r'assert\s+\w+\.(is_|has_|get_)\w+\('

        # Pattern for invalid assertions on return values: result = ...; assert result
        # or: assert <var> is True/False
        invalid_patterns = [
            r'assert\s+\w+\s+is\s+(True|False)',  # assert result is True
            r'assert\s+\w+\s*==\s*(True|False)',  # assert result == True
        ]

        # Check if there are any assertions in the code
        has_assertions = bool(re.search(r'\bassert\b', test_code))
        if not has_assertions:
            return True  # No assertions to validate

        # Check for invalid patterns first
        for pattern in invalid_patterns:
            if re.search(pattern, test_code):
                return False

        # Check if valid POM assertions exist
        has_valid_pom_assertions = bool(re.search(pom_assertion_pattern, test_code))

        # If code has assertions but none are valid POM assertions, check if
        # it's asserting on a return value stored in a variable
        if not has_valid_pom_assertions:
            # Pattern: result = something(); assert result
            result_assign = re.search(r'(\w+)\s*=\s*\w+\.\w+\(\)', test_code)
            if result_assign:
                var_name = result_assign.group(1)
                if re.search(rf'assert\s+{var_name}\b', test_code):
                    return False

        return True
