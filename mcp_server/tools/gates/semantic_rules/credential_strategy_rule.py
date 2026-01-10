"""
FR-14.2: Credential Strategy Enforcement

Validates that Role code matches the credential_strategy chosen in Step 1.

Strategies:
- self-contained: Role creates/registers own credentials within test
- static: Role reads from pre-existing test_users fixture
- dynamic: Role reads from config after registration workflow
- none: No credentials expected in Role
"""

import re
from typing import Dict, Any, Optional
from .base import SemanticRule


class CredentialStrategyRule(SemanticRule):
    """
    Validates that Role code matches credential_strategy from Step 1.

    Enforces consistency between Step 1 strategy choice and
    actual Role implementation.
    """

    @property
    def name(self) -> str:
        return "credential_strategy"

    @property
    def description(self) -> str:
        return (
            "Validates that Role code matches credential_strategy from Step 1 "
            "(self-contained, static, dynamic, none)"
        )

    def check(self, code: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Check Role code against credential_strategy from Step 1.

        Args:
            code: Generated Role code (from Tool 5)
            context: Must contain step_1_config with credential_strategy

        Returns:
            NEEDS_RETRY response if strategy mismatch, None if valid
        """
        # Extract Step 1 config
        step_1_config = context.get("step_1_config", {})
        credential_strategy = step_1_config.get("credential_strategy", "")

        # If no strategy specified, skip validation
        if not credential_strategy:
            return None

        # Normalize strategy
        strategy = credential_strategy.lower().strip()

        # Detect actual pattern in code
        detected_patterns = self._detect_credential_patterns(code)

        # Validate based on strategy
        if strategy == "self-contained":
            return self._validate_self_contained(code, detected_patterns)
        elif strategy == "static":
            return self._validate_static(code, detected_patterns)
        elif strategy == "dynamic":
            return self._validate_dynamic(code, detected_patterns)
        elif strategy == "none":
            return self._validate_none(code, detected_patterns)
        else:
            # Unknown strategy - skip validation
            return None

    def _detect_credential_patterns(self, code: str) -> Dict[str, bool]:
        """
        Detect credential patterns in Role code.

        Returns:
            Dict with detected patterns:
            {
                "has_uuid": bool,
                "has_faker": bool,
                "has_test_users_fixture": bool,
                "has_config_read": bool,
                "has_hardcoded_credentials": bool,
                "has_registration_call": bool
            }
        """
        # Static fixture pattern: __init__ accepts user_data parameter (from test_users fixture)
        # Look for: def __init__(self, ..., user_data, ...)
        has_user_data_param = bool(re.search(r'def\s+__init__\s*\([^)]*user_data[^)]*\)', code))

        patterns = {
            "has_uuid": bool(re.search(r'import uuid|uuid\.|uuid4\(\)', code)),
            "has_faker": bool(re.search(r'from faker import|Faker\(\)', code)),
            "has_test_users_fixture": has_user_data_param or bool(re.search(r'test_users\[', code)),
            "has_config_read": bool(re.search(r'json\.load|open\(.*test_users\.json|open\(.*\.json', code)),
            "has_hardcoded_credentials": bool(re.search(r'(email|password)\s*=\s*["\'][^"\']+["\']', code)),
            "has_registration_call": bool(re.search(r'\.(register|sign_up|create_account)\s*\(', code)),
        }

        return patterns

    def _validate_self_contained(
        self,
        code: str,
        patterns: Dict[str, bool]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate self-contained strategy.

        Expected: Role creates credentials (uuid/faker), registers user.
        Not expected: test_users fixture usage.
        """
        # Check for violation: using test_users fixture
        if patterns["has_test_users_fixture"]:
            return {
                "status": "NEEDS_RETRY",
                "pattern_template": self._get_self_contained_template(),
                "error": "Credential strategy mismatch: Role uses 'static' pattern but Step 1 specified 'self-contained'",
                "message": (
                    "Update Role to match 'self-contained' strategy: "
                    "Role should create its own credentials using uuid/faker and register user. "
                    "Remove test_users fixture usage."
                )
            }

        # Check for expected pattern: credential generation
        if not (patterns["has_uuid"] or patterns["has_faker"] or patterns["has_hardcoded_credentials"]):
            return {
                "status": "NEEDS_RETRY",
                "pattern_template": self._get_self_contained_template(),
                "error": "Self-contained strategy requires credential generation",
                "message": (
                    "Role should generate credentials using uuid or faker. "
                    "Add code like: email = f'test_{uuid.uuid4().hex[:8]}@example.com'"
                )
            }

        return None

    def _validate_static(
        self,
        code: str,
        patterns: Dict[str, bool]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate static strategy.

        Expected: Role reads from test_users fixture.
        Not expected: uuid/faker generation.
        """
        # Check for violation: dynamic generation
        if patterns["has_uuid"] or patterns["has_faker"]:
            return {
                "status": "NEEDS_RETRY",
                "pattern_template": self._get_static_template(),
                "error": "Credential strategy mismatch: Role generates credentials but Step 1 specified 'static'",
                "message": (
                    "Update Role to match 'static' strategy: "
                    "Role should read from test_users fixture. "
                    "Remove uuid/faker generation."
                )
            }

        # Check for expected pattern: test_users fixture usage
        if not patterns["has_test_users_fixture"]:
            return {
                "status": "NEEDS_RETRY",
                "pattern_template": self._get_static_template(),
                "error": "Static strategy requires test_users fixture usage",
                "message": (
                    "Role should read credentials from test_users fixture. "
                    "Add code like: self.user_data = user_data (from test_users fixture)"
                )
            }

        return None

    def _validate_dynamic(
        self,
        code: str,
        patterns: Dict[str, bool]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate dynamic strategy.

        Expected: Role reads from config file + registration.
        Not expected: hardcoded credentials or test_users fixture.
        """
        # Check for violation: static fixture usage
        if patterns["has_test_users_fixture"]:
            return {
                "status": "NEEDS_RETRY",
                "pattern_template": self._get_dynamic_template(),
                "error": "Credential strategy mismatch: Role uses 'static' pattern but Step 1 specified 'dynamic'",
                "message": (
                    "Update Role to match 'dynamic' strategy: "
                    "Role should read from config file after registration. "
                    "Remove test_users fixture usage."
                )
            }

        # Check for expected pattern: config read or registration
        if not (patterns["has_config_read"] or patterns["has_registration_call"]):
            return {
                "status": "NEEDS_RETRY",
                "pattern_template": self._get_dynamic_template(),
                "error": "Dynamic strategy requires config read or registration workflow",
                "message": (
                    "Role should read from config file or call registration method. "
                    "Add code like: with open('tests/data/test_users.json') as f: ..."
                )
            }

        return None

    def _validate_none(
        self,
        code: str,
        patterns: Dict[str, bool]
    ) -> Optional[Dict[str, Any]]:
        """
        Validate none strategy.

        Expected: No credential handling in Role.
        Not expected: any credential patterns.
        """
        # Check for any credential patterns
        if any([
            patterns["has_uuid"],
            patterns["has_faker"],
            patterns["has_test_users_fixture"],
            patterns["has_config_read"],
            patterns["has_hardcoded_credentials"]
        ]):
            return {
                "status": "NEEDS_RETRY",
                "pattern_template": "# Role should not handle credentials",
                "error": "Credential strategy mismatch: Role handles credentials but Step 1 specified 'none'",
                "message": (
                    "Update Role to match 'none' strategy: "
                    "Remove all credential handling code from Role."
                )
            }

        return None

    def _get_self_contained_template(self) -> str:
        """Pattern template for self-contained strategy."""
        return """
# Self-contained strategy example
import uuid

class RegisteredUser:
    def __init__(self, web_interface: WebInterface, base_url: str):
        self.web = web_interface
        # Generate unique credentials
        self.email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "TestPass123!"
        # Compose tasks
        self.auth_tasks = AuthTasks(web_interface, base_url)
"""

    def _get_static_template(self) -> str:
        """Pattern template for static strategy."""
        return """
# Static strategy example
class RegisteredUser:
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        self.web = web_interface
        # Read from test_users fixture
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        # Compose tasks
        self.auth_tasks = AuthTasks(web_interface, base_url)
"""

    def _get_dynamic_template(self) -> str:
        """Pattern template for dynamic strategy."""
        return """
# Dynamic strategy example
import json

class RegisteredUser:
    def __init__(self, web_interface: WebInterface, base_url: str):
        self.web = web_interface
        # Read from config file (after registration)
        with open('tests/data/test_users.json') as f:
            users = json.load(f)
            self.user_data = users.get('registered_user')
        # Compose tasks
        self.auth_tasks = AuthTasks(web_interface, base_url)
"""
