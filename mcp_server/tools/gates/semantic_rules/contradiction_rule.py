"""
FR-14.1: Parameter Value Contradiction Detection

Detects when parameters with opposite semantic meaning have the same value
(usually indicates meaningless operations).

Examples:
- transfer_funds(from_account="123", to_account="123")  # Meaningless
- migrate_data(source_db="prod", target_db="prod")      # Meaningless
- update_password(old_password="abc", new_password="abc")  # Meaningless
"""

import re
from typing import Dict, Any, Optional, List, Tuple
from .base import SemanticRule


class ParameterContradictionRule(SemanticRule):
    """
    Validates that opposite-semantic parameter pairs have different values.

    Detects patterns like:
    - (from, to) - transfers, movements
    - (source, dest/target) - migrations, copies
    - (old, new) - updates, changes
    - (sender, receiver) - messaging
    - etc.
    """

    # Opposite-semantic parameter pairs to check
    # Format: (prefix_a, prefix_b)
    OPPOSITE_PARAM_PAIRS = [
        ("from", "to"),         # from_X → to_X (transfers, movements)
        ("source", "dest"),     # source_X → dest_X (migrations, copies)
        ("source", "target"),   # source_X → target_X (operations)
        ("sender", "receiver"), # sender → receiver (messaging)
        ("old", "new"),         # old_X → new_X (updates, changes)
        ("before", "after"),    # before_X → after_X (state transitions)
        ("src", "dst"),         # src_X → dst_X (abbreviated form)
        ("origin", "destination") # origin_X → destination_X (movements)
    ]

    @property
    def name(self) -> str:
        return "parameter_contradiction"

    @property
    def description(self) -> str:
        return (
            "Detects opposite-semantic parameters with identical values "
            "(e.g., from_account==to_account, source==dest)"
        )

    def check(self, code: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check for parameter contradictions in workflow method calls.

        Args:
            code: Generated test code (from Tool 6)
            context: Not used for this rule (logic is code-only)

        Returns:
            NEEDS_RETRY response if contradiction found, None if valid
        """
        # Extract all method calls with parameters
        method_calls = self._extract_method_calls(code)

        # Check each method call for contradictions
        for call in method_calls:
            method_name = call["method"]
            params = call["params"]

            # Check each opposite-pair pattern
            for (prefix_a, prefix_b) in self.OPPOSITE_PARAM_PAIRS:
                contradiction = self._check_pair_contradiction(
                    params, prefix_a, prefix_b
                )
                if contradiction:
                    param_a, param_b, value = contradiction
                    return {
                        "status": "NEEDS_RETRY",
                        "fix_applied": "parameter_contradiction_detected",
                        "error": (
                            f"Semantic error in {method_name}(): "
                            f"'{param_a}'=='{value}' and '{param_b}'=='{value}' "
                            f"(meaningless operation)"
                        ),
                        "message": (
                            f"Parameters '{param_a}' and '{param_b}' should have "
                            f"DIFFERENT values for this operation to be meaningful. "
                            f"These are opposite-semantic parameters that represent "
                            f"source and destination of an operation."
                        )
                    }

        return None  # No contradictions found

    def _extract_method_calls(self, code: str) -> List[Dict[str, Any]]:
        """
        Extract method calls with parameters from code.

        Returns:
            List of dicts: [{"method": "transfer_funds", "params": {"from_account": "123", ...}}, ...]
        """
        method_calls = []

        # Pattern: object.method(param1=value1, param2=value2)
        # Matches: user.transfer_funds(from_account="123", to_account="456")
        pattern = r'(\w+)\.(\w+)\((.*?)\)'

        for match in re.finditer(pattern, code, re.DOTALL):
            obj_name = match.group(1)
            method_name = match.group(2)
            params_str = match.group(3)

            # Parse parameters
            params = self._parse_params(params_str)

            method_calls.append({
                "object": obj_name,
                "method": method_name,
                "params": params
            })

        return method_calls

    def _parse_params(self, params_str: str) -> Dict[str, str]:
        """
        Parse parameter string into dict.

        Args:
            params_str: "from_account='123', to_account='456'"

        Returns:
            {"from_account": "123", "to_account": "456"}
        """
        params = {}

        # Pattern: param_name=value (handles strings, numbers, vars)
        # Handles: param="value", param='value', param=value
        param_pattern = r'(\w+)\s*=\s*["\']?([^,\'"]+)["\']?'

        for match in re.finditer(param_pattern, params_str):
            param_name = match.group(1)
            param_value = match.group(2).strip().strip('"\'')
            params[param_name] = param_value

        return params

    def _check_pair_contradiction(
        self,
        params: Dict[str, str],
        prefix_a: str,
        prefix_b: str
    ) -> Optional[Tuple[str, str, str]]:
        """
        Check if a specific opposite-pair has contradicting values.

        Handles two patterns:
        1. Parameters with suffixes: from_account, to_account
        2. Parameters without suffixes (exact match): sender, receiver

        Args:
            params: Dict of parameter names to values
            prefix_a: First prefix (e.g., "from")
            prefix_b: Second prefix (e.g., "to")

        Returns:
            (param_a_name, param_b_name, shared_value) if contradiction found
            None otherwise

        Examples:
            params = {"from_account": "123", "to_account": "123", "amount": "100"}
            _check_pair_contradiction(params, "from", "to")
            → ("from_account", "to_account", "123")

            params = {"sender": "alice", "receiver": "alice", "text": "Hello"}
            _check_pair_contradiction(params, "sender", "receiver")
            → ("sender", "receiver", "alice")
        """
        # Pattern 1: Exact match (no underscore)
        # Check if both prefixes exist as exact parameter names
        if prefix_a in params and prefix_b in params:
            if params[prefix_a] == params[prefix_b]:
                return (prefix_a, prefix_b, params[prefix_a])

        # Pattern 2: Prefix with suffix (with underscore)
        # Find parameters matching each prefix
        matching_a = [k for k in params if k.startswith(f"{prefix_a}_")]
        matching_b = [k for k in params if k.startswith(f"{prefix_b}_")]

        # Check if both sides present
        for param_a in matching_a:
            for param_b in matching_b:
                # Extract suffix (e.g., "account" from "from_account")
                suffix_a = param_a.replace(f"{prefix_a}_", "")
                suffix_b = param_b.replace(f"{prefix_b}_", "")

                # If suffixes match (same entity type)
                if suffix_a == suffix_b:
                    # Check if values equal
                    if params[param_a] == params[param_b]:
                        return (param_a, param_b, params[param_a])

        return None
