"""
TestStructureValidator - Validates test structure against testing skill conventions.

Task 3.0 - PD-003: Runs automatically as pytest plugin on test collection.

Validates:
- AAA pattern (# Arrange, # Act, # Assert comments)
- Pytest markers (@pytest.mark.unit, etc.)
- Assertion messages (assert x, "message")
- Docstring priority (P0/P1/P2)
"""

import re


class TestStructureValidator:
    """Validates test structure against testing skill conventions."""

    # Valid type markers
    TYPE_MARKERS = ["unit", "integration", "slow", "smoke"]

    # AAA comment patterns
    AAA_PATTERNS = [
        r'#\s*Arrange',
        r'#\s*Act',
        r'#\s*Assert',
    ]

    @classmethod
    def validate_aaa_pattern(cls, test_source: str) -> bool:
        """
        Validate that test has AAA comments.

        Returns True if # Arrange, # Act, # Assert are all present.
        """
        if not test_source:
            return False

        for pattern in cls.AAA_PATTERNS:
            if not re.search(pattern, test_source, re.IGNORECASE):
                return False

        return True

    @classmethod
    def validate_markers(cls, markers: list) -> bool:
        """
        Validate that test has at least one type marker.

        Returns True if unit, integration, slow, or smoke marker present.
        """
        if not markers:
            return False

        for marker in markers:
            if marker in cls.TYPE_MARKERS:
                return True

        return False

    @staticmethod
    def validate_assertion_messages(test_source: str) -> bool:
        """
        Validate that all assertions have error messages.

        Returns True if no assertions are missing messages.
        """
        if not test_source:
            return True

        # Find all assert statements
        # Pattern: assert <condition> without a comma (missing message)
        # We need to match assert statements that don't have a message

        # Split by lines and check each assert
        lines = test_source.split('\n')

        for line in lines:
            stripped = line.strip()
            if stripped.startswith('assert '):
                # Check if there's a comma after the condition (indicating message)
                # Simple heuristic: if no comma in the assert line, it lacks a message
                # This handles single-line asserts
                if ',' not in stripped:
                    return False

        return True

    @staticmethod
    def validate_docstring_priority(docstring: str) -> bool:
        """
        Validate that docstring starts with P0/P1/P2 priority.

        Returns True if priority indicator is present.
        """
        if not docstring:
            return False

        # Check if docstring contains P0:, P1:, or P2: priority marker
        priority_pattern = r'P[012]:'

        return bool(re.search(priority_pattern, docstring))
