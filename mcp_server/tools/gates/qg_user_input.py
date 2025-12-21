"""
QGUserInput - Step 2 User Input Quality Gate.

Task 5.0 - PD-005: Validates user input before AI processing.

Validates:
- DD-01: persona (must be present and non-empty)
- DD-02: URL (must be valid HTTP/HTTPS format)
- role_name: must be present (PascalCase, derived from persona)
- domain: must be one of auth, catalog, cart, checkout
- raw_requirement: must be present

Saves state on PASS via StateManager.
"""

import re
from typing import Dict, Any
from urllib.parse import urlparse

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGUserInput(BaseGate):
    """Step 2 quality gate for user input validation."""

    # Valid domain values
    VALID_DOMAINS = ["auth", "catalog", "cart", "checkout"]

    # URL pattern - must start with http:// or https://
    URL_PATTERN = re.compile(r'^https?://\S+$')

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input fields.

        Args:
            input_data: Dict with persona, URL, role_name, domain, raw_requirement

        Returns:
            {"status": "pass"} on success
            {"status": "fail", "error": "...", "fix_hint": "..."} on failure
        """
        # Check required fields
        required_fields = ["persona", "URL", "role_name", "domain", "raw_requirement"]
        missing = cls.validate_required_fields(input_data, required_fields)

        if missing:
            return cls.fail_response(
                error=f"Missing required field(s): {', '.join(missing)}",
                fix_hint=cls._get_fix_hint_for_missing(missing)
            )

        # Validate persona (DD-01) - must be non-empty
        persona = input_data.get("persona")
        if not cls._is_valid_persona(persona):
            return cls.fail_response(
                error="Invalid persona: must be non-empty",
                fix_hint=cls._get_persona_hint()
            )

        # Validate URL (DD-02) - must be valid HTTP/HTTPS format
        url = input_data.get("URL")
        if not cls._is_valid_url(url):
            return cls.fail_response(
                error=f"Invalid URL format: '{url}'",
                fix_hint=cls._get_url_hint()
            )

        # Validate role_name - must be non-empty
        role_name = input_data.get("role_name")
        if not cls._is_valid_role_name(role_name):
            return cls.fail_response(
                error="Invalid role_name: must be non-empty",
                fix_hint=cls._get_role_name_hint()
            )

        # Validate domain - must be one of valid domains
        domain = input_data.get("domain")
        if not cls._is_valid_domain(domain):
            return cls.fail_response(
                error=f"Invalid domain: '{domain}'",
                fix_hint=cls._get_domain_hint()
            )

        # Validate raw_requirement - must be non-empty
        raw_requirement = input_data.get("raw_requirement")
        if not cls._is_valid_raw_requirement(raw_requirement):
            return cls.fail_response(
                error="Invalid raw_requirement: must be non-empty",
                fix_hint=cls._get_raw_requirement_hint()
            )

        # All valid - save state and return pass
        state_manager = StateManager()
        state_manager.save(step=2, data={
            "persona": persona,
            "URL": url,
            "role_name": role_name,
            "domain": domain,
            "raw_requirement": raw_requirement
        })

        return cls.pass_response()

    @classmethod
    def _is_valid_persona(cls, value: Any) -> bool:
        """Check if persona is valid (non-empty string)."""
        if value is None or value == "":
            return False
        return isinstance(value, str) and len(value.strip()) > 0

    @classmethod
    def _is_valid_url(cls, value: Any) -> bool:
        """Check if URL is valid HTTP/HTTPS format."""
        if value is None or value == "":
            return False
        if not isinstance(value, str):
            return False

        # Must match http:// or https:// pattern
        if not cls.URL_PATTERN.match(value):
            return False

        # Use urlparse to validate basic structure
        try:
            result = urlparse(value)
            return all([result.scheme in ('http', 'https'), result.netloc])
        except Exception:
            return False

    @classmethod
    def _is_valid_role_name(cls, value: Any) -> bool:
        """Check if role_name is valid (non-empty string)."""
        if value is None or value == "":
            return False
        return isinstance(value, str) and len(value.strip()) > 0

    @classmethod
    def _is_valid_domain(cls, value: Any) -> bool:
        """Check if domain is one of the valid values."""
        if value is None or value == "":
            return False
        return value in cls.VALID_DOMAINS

    @classmethod
    def _is_valid_raw_requirement(cls, value: Any) -> bool:
        """Check if raw_requirement is valid (non-empty string)."""
        if value is None or value == "":
            return False
        return isinstance(value, str) and len(value.strip()) > 0

    @staticmethod
    def _get_fix_hint_for_missing(missing_fields: list) -> str:
        """Get fix hint for missing fields."""
        hints = []

        if "persona" in missing_fields:
            hints.append(
                "Provide persona: the user role (e.g., 'registered user', 'guest')"
            )

        if "URL" in missing_fields:
            hints.append(
                "Provide URL: target page (e.g., 'http://example.com/login')"
            )

        if "role_name" in missing_fields:
            hints.append(
                "Provide role_name: PascalCase role (e.g., 'RegisteredUser')"
            )

        if "domain" in missing_fields:
            hints.append(
                "Provide domain: one of 'auth', 'catalog', 'cart', 'checkout'"
            )

        if "raw_requirement" in missing_fields:
            hints.append(
                "Provide raw_requirement: the full user requirement text"
            )

        return " | ".join(hints)

    @staticmethod
    def _get_persona_hint() -> str:
        """Get fix hint for invalid persona."""
        return (
            "Persona must be a non-empty string describing the user role. "
            "Example: 'registered user', 'guest', 'admin'"
        )

    @staticmethod
    def _get_url_hint() -> str:
        """Get fix hint for invalid URL."""
        return (
            "URL must be a valid HTTP or HTTPS URL. "
            "Example: 'http://automationpractice.pl/index.php?controller=authentication'"
        )

    @staticmethod
    def _get_role_name_hint() -> str:
        """Get fix hint for invalid role_name."""
        return (
            "role_name must be a PascalCase identifier derived from persona. "
            "Example: 'RegisteredUser', 'GuestUser', 'AdminUser'"
        )

    @staticmethod
    def _get_domain_hint() -> str:
        """Get fix hint for invalid domain."""
        return (
            "domain must be one of: 'auth' (login/register), "
            "'catalog' (browse products), 'cart' (shopping cart), "
            "'checkout' (payment/order)"
        )

    @staticmethod
    def _get_raw_requirement_hint() -> str:
        """Get fix hint for invalid raw_requirement."""
        return (
            "raw_requirement must be the full user requirement text. "
            "Example: 'As a registered user, I want to login with email and password'"
        )
