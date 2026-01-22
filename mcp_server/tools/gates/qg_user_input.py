"""
QGUserInput - Step 1 User Input Quality Gate.

Task 5.0 - PD-005: Validates user input before AI processing.

Validates:
- DD-01: persona (must be present and non-empty)
- DD-02: URL (must be valid HTTP/HTTPS format)
- role_name: must be present (PascalCase, derived from persona)
- workflow: must be present and non-empty (dynamic, not hardcoded)
- raw_requirement: must be present

Saves state on PASS via StateManager.

Note: workflow (formerly domain) is now dynamic - any non-empty string is valid.
This allows the framework to work with any website, not just e-commerce.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any
from urllib.parse import urlparse

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGUserInput(BaseGate):
    """Step 1 quality gate for user input validation."""

    # URL pattern - must start with http:// or https://
    URL_PATTERN = re.compile(r'^https?://\S+$')

    # PascalCase pattern: starts with uppercase, alphanumeric only
    PASCAL_CASE_PATTERN = re.compile(r'^[A-Z][a-zA-Z0-9]*$')

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input fields.

        Args:
            input_data: Dict with persona, URL, role_name, workflow, raw_requirement
                        (also accepts 'domain' for backwards compatibility)

        Returns:
            {"status": "pass"} on success
            {"status": "fail", "error": "...", "fix_hint": "..."} on failure
        """
        # Support both 'workflow' and 'domain' (backwards compatibility)
        workflow = input_data.get("workflow") or input_data.get("domain")
        if workflow:
            input_data["workflow"] = workflow

        # Check required fields
        required_fields = ["persona", "URL", "role_name", "workflow", "raw_requirement"]
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

        # Validate role_name - must be PascalCase
        role_name = input_data.get("role_name")
        if not cls._is_valid_role_name(role_name):
            return cls.fail_response(
                error=f"Invalid role_name: '{role_name}' must be PascalCase (e.g., RegisteredUser, GuestUser)",
                fix_hint=cls._get_role_name_hint()
            )

        # Validate workflow - must be non-empty (dynamic, not hardcoded)
        if not cls._is_valid_workflow(workflow):
            return cls.fail_response(
                error="Invalid workflow: must be non-empty",
                fix_hint=cls._get_workflow_hint()
            )

        # Validate raw_requirement - must be non-empty
        raw_requirement = input_data.get("raw_requirement")
        if not cls._is_valid_raw_requirement(raw_requirement):
            return cls.fail_response(
                error="Invalid raw_requirement: must be non-empty",
                fix_hint=cls._get_raw_requirement_hint()
            )

        # All valid - detect environment and save state
        # Task 10.0: Use per-run state isolation
        # DEF-062: Auto-detect environment from URL (NEEDS_RETRY pattern)
        detection_result = cls._detect_environment_from_url(url, workflow)

        # Check if unknown domain (NEEDS_RETRY)
        if "needs_retry" in detection_result:
            return detection_result["needs_retry"]

        # Known domain - save state
        detected_env_id = detection_result["env_id"]

        audit_logger = cls.get_audit_logger()
        state_manager = StateManager(run_id=audit_logger.run_id)
        state_manager.save(step=1, data={
            "persona": persona,
            "URL": url,
            "role_name": role_name,
            "workflow": workflow,
            "raw_requirement": raw_requirement,
            "detected_env_id": detected_env_id
        })

        return cls.pass_response(
            step=1,
            gate_name="qg_user_input",
            mode="POST",
            metadata={
                "persona": persona,
                "URL": url,
                "role_name": role_name,
                "workflow": workflow,
                "detected_env_id": detected_env_id
            }
        )

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
        """Check if role_name is valid (non-empty PascalCase string)."""
        if value is None or value == "":
            return False
        if not isinstance(value, str) or not value.strip():
            return False
        # Must be PascalCase (starts with uppercase, alphanumeric)
        return bool(cls.PASCAL_CASE_PATTERN.match(value))

    @classmethod
    def _is_valid_workflow(cls, value: Any) -> bool:
        """Check if workflow is valid (non-empty string - dynamic, not hardcoded)."""
        if value is None or value == "":
            return False
        return isinstance(value, str) and len(value.strip()) > 0

    @classmethod
    def _is_valid_raw_requirement(cls, value: Any) -> bool:
        """Check if raw_requirement is valid (non-empty string)."""
        if value is None or value == "":
            return False
        return isinstance(value, str) and len(value.strip()) > 0

    @classmethod
    def _detect_environment_from_url(cls, url: str, workflow: str) -> Dict[str, Any]:
        """
        Detect environment ID by matching URL domain against environment_config.json.

        DEF-062 REFACTOR: Now returns NEEDS_RETRY for unknown domains instead of
        silently falling back to "DEFAULT".

        Args:
            url: User-provided URL (validated by _is_valid_url)
            workflow: Workflow name for scaffolding template

        Returns:
            Dict with:
            - If known: {"env_id": "parabank", "is_known": True}
            - If DEFAULT URL: {"env_id": "DEFAULT", "is_known": True}
            - If unknown: {"needs_retry": {...NEEDS_RETRY response...}}
        """
        config_path = Path(__file__).parent.parent.parent.parent / "framework" / "resources" / "config" / "environment_config.json"

        # Read environment config
        try:
            with open(config_path, 'r') as f:
                environments = json.load(f)
        except Exception:
            # Config read failed - can't scaffold, use DEFAULT
            return {"env_id": "DEFAULT", "is_known": True}

        # Extract domain from URL
        parsed_url = urlparse(url)
        url_domain = parsed_url.netloc.lower()
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

        # Check if this is the DEFAULT environment URL
        default_url = environments.get("DEFAULT", {}).get("url", "")
        default_parsed = urlparse(default_url)
        default_domain = default_parsed.netloc.lower()

        if url_domain == default_domain or url_domain.endswith(f".{default_domain}"):
            return {"env_id": "DEFAULT", "is_known": True}

        # Match against each environment's URL domain (excluding DEFAULT)
        for env_id, config in environments.items():
            if env_id == "DEFAULT":
                continue  # Already checked above

            env_url = config.get('url', '')
            env_parsed = urlparse(env_url)
            env_domain = env_parsed.netloc.lower()

            if url_domain == env_domain or url_domain.endswith(f".{env_domain}"):
                return {"env_id": env_id, "is_known": True}

        # Unknown domain - return NEEDS_RETRY with scaffolding instructions
        template = json.dumps({
            workflow: {
                "url": base_url
            }
        }, indent=2)

        return {
            "needs_retry": {
                "status": "NEEDS_RETRY",
                "fix_applied": "environment_added_to_config",
                "error": f"Unknown environment: {url_domain}",
                "message": f"Unknown environment detected. What should I do?\n\n1. Create new environment config ({workflow})\n2. Skip environment detection (proceed without config)\n3. Cancel workflow",
                "scaffolding_needed": [{
                    "type": "config_entry",
                    "path": "framework/resources/config/environment_config.json",
                    "template": template,
                    "reason": f"Environment config for {workflow} workflow at {base_url}"
                }]
            }
        }

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

        if "workflow" in missing_fields:
            hints.append(
                "Provide workflow: the workflow/domain name (e.g., 'auth', 'catalog', 'checkout', or any custom name)"
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
    def _get_workflow_hint() -> str:
        """Get fix hint for invalid workflow."""
        return (
            "workflow must be a non-empty string describing the workflow/domain. "
            "Examples: 'auth', 'catalog', 'cart', 'checkout', 'dashboard', 'admin', "
            "or any custom workflow name for your application."
        )

    @staticmethod
    def _get_raw_requirement_hint() -> str:
        """Get fix hint for invalid raw_requirement."""
        return (
            "raw_requirement must be the full user requirement text. "
            "Example: 'As a registered user, I want to login with email and password'"
        )
