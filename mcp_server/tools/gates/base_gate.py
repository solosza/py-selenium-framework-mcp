"""
BaseGate - Base class with shared validation utilities for quality gates.

Task 3.0 - Provides common functionality for all quality gates:
- Response formatting (pass/fail)
- Skeleton code detection (DD-25)
- Locator detection (DD-27)
- POM assertion validation (DD-15)
- Required field validation

Task 1.0 - Added audit logging integration:
- Audit logger instance (class-level)
- Automatic logging on pass/fail responses

Task 2.0 - Added self-heal cap enforcement:
- MAX_ATTEMPTS constant (3)
- blocked_response() for capped steps
- State manager integration for attempt tracking
"""

import re
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from utils.audit_logger import AuditLogger
    from utils.state_manager import StateManager


class BaseGate:
    """Base class with shared validation utilities for quality gates."""

    # Task 2.0: Self-heal cap (DD-22)
    MAX_ATTEMPTS = 3

    # Audit logger instance (shared across all gates for a workflow run)
    _audit_logger: Optional["AuditLogger"] = None

    # State manager for attempt tracking (Task 2.0)
    _state_manager: Optional["StateManager"] = None

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

    @classmethod
    def set_audit_logger(cls, logger: Optional["AuditLogger"]) -> None:
        """
        Set the audit logger for all gates.

        Args:
            logger: AuditLogger instance, or None to disable logging.
        """
        cls._audit_logger = logger

    @classmethod
    def get_audit_logger(cls) -> "AuditLogger":
        """
        Get the audit logger, creating one if needed (lazy init).

        DEF-040: Ensures audit logger is always available. Creates one
        with auto-generated run_id if not already set.

        DEF-043: Persists run_id in workflow_state.json to continue same
        audit session across separate MCP tool calls (separate Python processes).

        Returns:
            AuditLogger instance (never None).
        """
        if cls._audit_logger is None:
            from utils.audit_logger import AuditLogger

            # DEF-049 FIX: Always create fresh audit logger (never reuse)
            # Each workflow gets its own audit trail
            cls._audit_logger = AuditLogger()

        return cls._audit_logger

    @classmethod
    def _enforce_audit_write(
        cls,
        step: int,
        gate_name: str,
        mode: Optional[str]
    ) -> Optional[dict]:
        """
        Smart gate enforcement: Validate audit trail write succeeded (DD-30).

        Checks that:
        1. Audit file exists and is writable
        2. Recent audit entry was written successfully
        3. Audit directory structure is correct

        Args:
            step: Step number that was logged
            gate_name: Gate name that was logged
            mode: Gate mode (PRE/POST)

        Returns:
            fail_response dict if audit write failed, None if successful
        """
        import os
        from pathlib import Path

        try:
            audit_logger = cls.get_audit_logger()

            # Check 1: Audit directory exists (use audit logger's actual path)
            audit_file_path = Path(audit_logger._audit_file)
            audit_dir = audit_file_path.parent

            if not audit_dir.exists():
                return {
                    "status": "fail",
                    "error": "Audit directory missing (DD-30 violation)",
                    "fix_hint": """
Audit trail directory does not exist.

Pattern:
1. Create tests/_audit/ directory
2. Ensure write permissions
3. Verify AuditLogger configuration

Fix:
mkdir -p tests/_audit
# Or in Python:
from pathlib import Path
Path("tests/_audit").mkdir(parents=True, exist_ok=True)

Audit enforcement ensures DD-30 (Progressive Audit Trail) compliance.
                    """
                }

            # Check 2: Audit file exists (use audit logger's actual file path)
            audit_file = audit_file_path
            if not audit_file.exists():
                return {
                    "status": "fail",
                    "error": f"Audit file not created: {audit_file.name} (DD-30 violation)",
                    "fix_hint": f"""
Audit file was not created after gate passed.

Expected file: {audit_file}
Run ID: {audit_logger.run_id}

Pattern:
1. Check AuditLogger.log_gate() is writing to correct path
2. Verify file permissions in tests/_audit/
3. Ensure disk space available

Debug:
import json
from pathlib import Path
audit_path = Path("{audit_file}")
print(f"Exists: {{audit_path.exists()}}")
print(f"Parent writable: {{os.access(audit_path.parent, os.W_OK)}}")

Audit enforcement ensures DD-30 (Progressive Audit Trail) compliance.
                    """
                }

            # Check 3: Audit file is readable and contains valid JSON
            try:
                import json
                with open(audit_file, 'r') as f:
                    audit_data = json.load(f)

                # Check 4: Recent entry exists for this step/gate
                steps = audit_data.get("steps", [])
                recent_entry = next(
                    (s for s in reversed(steps)
                     if s.get("step") == step and s.get("gate") == gate_name),
                    None
                )

                if not recent_entry:
                    return {
                        "status": "fail",
                        "error": f"Audit entry not found for Step {step} {gate_name} (DD-30 violation)",
                        "fix_hint": f"""
Audit file exists but entry was not written.

File: {audit_file}
Expected: Step {step}, Gate {gate_name}, Mode {mode or 'POST'}
Found: {len(steps)} total entries

Pattern:
1. Check AuditLogger.log_gate() is called correctly
2. Verify step/gate_name parameters match
3. Ensure JSON write is not failing silently

Debug:
import json
with open("{audit_file}", 'r') as f:
    data = json.load(f)
    print("Steps logged:", [s.get("gate") for s in data.get("steps", [])])

Audit enforcement ensures DD-30 (Progressive Audit Trail) compliance.
                        """
                    }

            except json.JSONDecodeError:
                return {
                    "status": "fail",
                    "error": f"Audit file corrupted: {audit_file.name} (DD-30 violation)",
                    "fix_hint": """
Audit file exists but contains invalid JSON.

Pattern:
1. Check if write operation was interrupted
2. Verify file wasn't manually edited
3. Delete corrupted file and regenerate

Fix:
# Delete corrupted audit file
import os
os.remove("tests/_audit/audit_log_<run_id>.json")
# Restart workflow from Step 1

Audit enforcement ensures DD-30 (Progressive Audit Trail) compliance.
                    """
                }

        except Exception as e:
            # Catch any unexpected errors
            return {
                "status": "fail",
                "error": f"Audit enforcement error: {str(e)}",
                "fix_hint": f"""
Unexpected error during audit trail validation.

Error: {str(e)}

Pattern:
1. Check AuditLogger is initialized correctly
2. Verify tests/_audit/ directory permissions
3. Ensure no file system issues

Debug:
import os
from pathlib import Path
audit_dir = Path("tests/_audit")
print(f"Directory exists: {{audit_dir.exists()}}")
print(f"Directory writable: {{os.access(audit_dir, os.W_OK)}}")
print(f"Run ID: {{cls.get_audit_logger().run_id}}")

Audit enforcement ensures DD-30 (Progressive Audit Trail) compliance.
                """
            }

        # All checks passed
        return None

    @classmethod
    def set_state_manager(cls, manager: Optional["StateManager"]) -> None:
        """
        Set the state manager for attempt tracking.

        Args:
            manager: StateManager instance, or None to disable tracking.
        """
        cls._state_manager = manager

    @classmethod
    def get_state_manager(cls) -> Optional["StateManager"]:
        """Get the current state manager."""
        return cls._state_manager

    @classmethod
    def blocked_response(
        cls,
        step: int,
        attempts: int,
        errors: List[str],
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Return blocked response when max attempts exceeded (DD-22).

        Args:
            step: Step number that is blocked
            attempts: Number of attempts made
            errors: List of errors from previous attempts
            metadata: Validation data from this step (for audit logging)

        Returns:
            {"status": "blocked", "step": int, "attempts": int, "errors": list, "fix_hint": str}
        """
        # DEF-040: Always log to audit trail (lazy init)
        cls.get_audit_logger().log_gate(
            step=step,
            gate_name=f"step_{step}_blocked",
            mode="POST",
            result="blocked",
            error=f"Max attempts ({attempts}) exceeded",
            metadata=metadata
        )

        return {
            "status": "blocked",
            "step": step,
            "attempts": attempts,
            "errors": errors,
            "fix_hint": f"Step {step} blocked after {attempts} attempts. Manual user intervention required (DD-22)."
        }

    @classmethod
    def pass_response(
        cls,
        step: Optional[int] = None,
        gate_name: Optional[str] = None,
        mode: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Return standard pass response and optionally log to audit trail.

        Args:
            step: Step number (for audit logging)
            gate_name: Gate name (for audit logging)
            mode: Gate mode PRE/POST (for audit logging)
            source: Execution source tool/ai/self-heal (for audit logging)
            metadata: Validation data from this step (for audit logging)

        Returns:
            {"status": "pass"}
        """
        # DEF-040: Log to audit trail if context provided (lazy init)
        if step is not None and gate_name is not None:
            cls.get_audit_logger().log_gate(
                step=step,
                gate_name=gate_name,
                mode=mode or "POST",
                result="pass",
                source=source,
                metadata=metadata
            )

            # Smart gate enforcement: Validate audit write succeeded
            audit_error = cls._enforce_audit_write(step, gate_name, mode)
            if audit_error:
                return audit_error

        return {"status": "pass"}

    @classmethod
    def fail_response(
        cls,
        error: str,
        fix_hint: str,
        step: Optional[int] = None,
        gate_name: Optional[str] = None,
        mode: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> dict:
        """
        Return standard fail response and optionally log to audit trail.

        Args:
            error: Error message
            fix_hint: Hint for fixing the issue
            step: Step number (for audit logging)
            gate_name: Gate name (for audit logging)
            mode: Gate mode PRE/POST (for audit logging)
            source: Execution source tool/ai/self-heal (for audit logging)
            metadata: Validation data from this step (for audit logging)

        Returns:
            {"status": "fail", "error": str, "fix_hint": str}
        """
        # DEF-040: Log to audit trail if context provided (lazy init)
        if step is not None and gate_name is not None:
            cls.get_audit_logger().log_gate(
                step=step,
                gate_name=gate_name,
                mode=mode or "POST",
                result="fail",
                error=error,
                source=source,
                metadata=metadata
            )

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
