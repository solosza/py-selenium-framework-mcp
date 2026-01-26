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

            # DEF-052 FIX: Reuse run_id from session if active
            # This allows multiple MCP tool calls (separate Python processes)
            # to share the same run_id within a workflow session
            session_run_id = cls._get_session_run_id()
            if session_run_id:
                # Continuing existing workflow session
                cls._audit_logger = AuditLogger(run_id=session_run_id)
            else:
                # Starting new workflow session
                cls._audit_logger = AuditLogger()  # Fresh run_id
                cls._save_session_run_id(cls._audit_logger.run_id)

        return cls._audit_logger

    @classmethod
    def _get_session_run_id(cls) -> Optional[str]:
        """
        Get run_id from session marker if active (per-run isolation).

        Session marker pattern:
        - File: tests/_state/.current_run_id
        - Format: "run_id" (plain text, no timestamp)
        - Cleared by qg_user_input when starting new workflow

        Returns:
            run_id if session marker exists, None otherwise.
        """
        from pathlib import Path

        # Use new per-run isolation marker location
        project_root = Path(__file__).parent.parent.parent.parent
        marker_file = project_root / "tests" / "_state" / ".current_run_id"

        if not marker_file.exists():
            return None

        try:
            run_id = marker_file.read_text().strip()
            return run_id if run_id else None
        except Exception:
            return None

    @classmethod
    def _save_session_run_id(cls, run_id: str) -> None:
        """
        Save run_id to session marker (per-run isolation).

        Creates or updates session marker file with current run_id.
        This allows multiple MCP tool calls (separate Python processes) to share
        the same run_id within a workflow session.

        Args:
            run_id: Run ID to save to session marker.
        """
        from pathlib import Path

        # Save to new per-run isolation marker
        project_root = Path(__file__).parent.parent.parent.parent
        marker_file = project_root / "tests" / "_state" / ".current_run_id"
        marker_file.parent.mkdir(parents=True, exist_ok=True)
        marker_file.write_text(run_id)

    @classmethod
    def _clear_session_marker(cls) -> None:
        """
        Clear session marker (per-run isolation).

        Called when starting a new workflow (Step 1) to ensure fresh run_id.
        """
        from pathlib import Path

        # Clear new per-run isolation marker
        project_root = Path(__file__).parent.parent.parent.parent
        marker_file = project_root / "tests" / "_state" / ".current_run_id"
        if marker_file.exists():
            try:
                marker_file.unlink()
            except Exception:
                pass

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
                    "teach": """
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
                    "teach": f"""
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
                events = audit_data.get("events", [])
                recent_entry = next(
                    (e for e in reversed(events)
                     if e.get("step") == step and e.get("gate") == gate_name),
                    None
                )

                if not recent_entry:
                    return {
                        "status": "fail",
                        "error": f"Audit entry not found for Step {step} {gate_name} (DD-30 violation)",
                        "teach": f"""
Audit file exists but entry was not written.

File: {audit_file}
Expected: Step {step}, Gate {gate_name}, Mode {mode or 'POST'}
Found: {len(events)} total entries

Pattern:
1. Check AuditLogger.log_gate() is called correctly
2. Verify step/gate_name parameters match
3. Ensure JSON write is not failing silently

Debug:
import json
with open("{audit_file}", 'r') as f:
    data = json.load(f)
    print("Events logged:", [e.get("gate") for e in data.get("events", [])])

Audit enforcement ensures DD-30 (Progressive Audit Trail) compliance.
                        """
                    }

            except json.JSONDecodeError:
                return {
                    "status": "fail",
                    "error": f"Audit file corrupted: {audit_file.name} (DD-30 violation)",
                    "teach": """
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
                "teach": f"""
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
            {"status": "blocked", "step": int, "attempts": int, "errors": list, "teach": str}
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
            "teach": f"Step {step} blocked after {attempts} attempts. Manual user intervention required (DD-22)."
        }

    @classmethod
    def validate_and_pass(
        cls,
        step: int,
        step_name: str,
        gate_name: str,
        state_data: dict,
        metadata: Optional[dict] = None,
        mode: str = "POST",
        source: Optional[str] = None
    ) -> dict:
        """
        Universal gate completion pattern: Save state, return pass.

        Defense-in-depth design:
        1. THIS gate: Validates data, saves state, returns PASS
        2. POST-ACTION: Hook writes transcript after gate PASS
        3. NEXT gate PRE-check: Verifies previous step's transcript exists

        Transcript check moved to next step's PRE-check (not this gate's responsibility).

        Args:
            step: Step number (1-5)
            step_name: Human-readable step name (e.g., "User Input", "Pre-flight Configuration")
            gate_name: Gate name (e.g., "qg_user_input", "qg_preflight")
            state_data: Data to save to workflow state
            metadata: Metadata to log to audit trail (defaults to state_data if not provided)
            mode: Gate mode (default: "POST")
            source: Execution source (default: None)

        Returns:
            {"status": "pass"} on success
        """
        # 1. Save state (per-run isolation)
        from utils.state_manager import StateManager
        audit_logger = cls.get_audit_logger()
        state_manager = StateManager(run_id=audit_logger.run_id)
        state_manager.save(step=step, data=state_data)

        # 2. Return pass (logs audit, validates audit write)
        # POST-ACTION: Hook writes transcript after this returns
        return cls.pass_response(
            step=step,
            gate_name=gate_name,
            mode=mode,
            source=source,
            metadata=metadata or state_data
        )

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

        NOTE: For POST-only gates, prefer using validate_and_pass() which enforces
        transcript validation and state saving. This method is for lower-level use.

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
        teach: str,
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
            teach: Teaching guidance for fixing the issue (Smart Gates = Validate + Teach)
            step: Step number (for audit logging)
            gate_name: Gate name (for audit logging)
            mode: Gate mode PRE/POST (for audit logging)
            source: Execution source tool/ai/self-heal (for audit logging)
            metadata: Validation data from this step (for audit logging)

        Returns:
            {"status": "fail", "error": str, "teach": str}
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
            "teach": teach
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

    @classmethod
    def _validate_param_format(cls, params: List, context: str) -> Optional[dict]:
        """
        DEF-057: Validate params are string format 'name: type', not dict format.

        Per DEF-054 standard, params must be string arrays like:
        ["email: str", "password: str"]

        NOT dict arrays like:
        [{"name": "email", "type": "str"}]

        Args:
            params: List of param strings or dicts to validate
            context: Context string for error message (e.g., "action_method 'enter_email'")

        Returns:
            fail_response dict if invalid format detected, None if valid
        """
        if not params:
            return None  # Empty params list is valid

        for param in params:
            # Check for dict format (WRONG)
            if isinstance(param, dict):
                return cls.fail_response(
                    error=f"{context}: Param must be string format, got dict: {param}",
                    teach="""
Params must be string format per DEF-054 standard.

CORRECT: ["email: str", "password: str"]
WRONG:   [{"name": "email", "type": "str"}]

Pattern:
- Each param is a string with format "name: type"
- NOT a dict with "name" and "type" keys

Fix:
Convert dict format to string format:
  {"name": "email", "type": "str"} → "email: str"
                    """
                )

            # Check for invalid string format
            if not isinstance(param, str):
                return cls.fail_response(
                    error=f"{context}: Param must be string, got {type(param).__name__}: {param}",
                    teach="Params must be strings with format 'name: type' like 'email: str'"
                )

            # Check for colon separator (required format: "name: type")
            if ":" not in param:
                return cls.fail_response(
                    error=f"{context}: Param missing colon separator: '{param}'",
                    teach="""
Params must have format 'name: type' with colon separator.

Examples:
- "email: str"
- "password: str"
- "product_name: str"

NOT:
- "email"  ← missing type
- "email str"  ← missing colon
                    """
                )

        return None  # All params valid

    @classmethod
    def _check_transcript_written(
        cls,
        step: int,
        step_name: str,
        input_data: dict
    ) -> Optional[dict]:
        """
        Check/create workflow transcript entry (Protocol POST-ACTION requirement).

        Validates:
        - tests/_reports/{run_id}/workflow_transcript.md exists
        - Contains entry for this step

        Args:
            step: Step number (1-5)
            step_name: Human-readable step name
            input_data: Input data to include in transcript

        Returns:
            None if transcript exists with entry for this step
            NEEDS_RETRY dict with template if missing
        """
        from pathlib import Path
        from datetime import datetime

        # Get run_id from audit logger
        audit_logger = cls.get_audit_logger()
        run_id = audit_logger.run_id

        # Safe run_id for Windows paths
        safe_run_id = run_id.replace(":", "-")

        # Transcript file path
        transcript_file = Path(f"tests/_reports/{safe_run_id}/workflow_transcript.md")

        # Check if transcript directory exists
        if not transcript_file.parent.exists():
            # Create directory template
            return {
                "status": "NEEDS_RETRY",
                "fix_applied": "transcript_infrastructure_created",
                "error": "Transcript directory missing",
                "message": f"Create transcript directory and write Step {step} entry",
                "transcript_scaffolding": {
                    "directory": str(transcript_file.parent),
                    "file": str(transcript_file),
                    "step": step,
                    "step_name": step_name,
                    "template": cls._generate_transcript_template(step, step_name, input_data)
                }
            }

        # Check if transcript file exists
        if not transcript_file.exists():
            # Create transcript with first entry
            return {
                "status": "NEEDS_RETRY",
                "fix_applied": "transcript_file_created",
                "error": "Transcript file missing",
                "message": f"Create transcript file with Step {step} entry",
                "transcript_scaffolding": {
                    "file": str(transcript_file),
                    "step": step,
                    "step_name": step_name,
                    "template": cls._generate_transcript_template(step, step_name, input_data, is_first_entry=True)
                }
            }

        # Transcript exists - check if this step's entry exists
        content = transcript_file.read_text(encoding='utf-8')
        step_marker = f"## Step {step}: {step_name}"

        if step_marker not in content:
            # Append this step's entry
            return {
                "status": "NEEDS_RETRY",
                "fix_applied": "transcript_entry_appended",
                "error": f"Transcript missing Step {step} entry",
                "message": f"Append Step {step} entry to existing transcript",
                "transcript_scaffolding": {
                    "file": str(transcript_file),
                    "step": step,
                    "step_name": step_name,
                    "mode": "append",
                    "template": cls._generate_transcript_template(step, step_name, input_data)
                }
            }

        # Transcript exists with this step's entry
        return None

    @staticmethod
    def _generate_transcript_template(
        step: int,
        step_name: str,
        input_data: dict,
        is_first_entry: bool = False
    ) -> str:
        """
        Generate transcript entry template.

        Args:
            step: Step number
            step_name: Human-readable step name
            input_data: Input data to include
            is_first_entry: If True, include header

        Returns:
            Formatted transcript entry
        """
        from datetime import datetime

        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Header for first entry only
        header = ""
        if is_first_entry:
            header = f"""# Workflow Transcript

**Run ID:** {input_data.get('run_id', 'N/A')}
**Started:** {timestamp}

---

"""

        # Format input data as bullet points
        input_lines = []
        for key, value in input_data.items():
            if key == 'run_id':  # Skip run_id (in header)
                continue
            # Format nested dicts
            if isinstance(value, dict):
                input_lines.append(f"- **{key}:**")
                for k, v in value.items():
                    input_lines.append(f"  - {k}: {v}")
            else:
                input_lines.append(f"- **{key}:** {value}")

        inputs_section = "\n".join(input_lines) if input_lines else "- (No inputs)"

        # Entry template
        entry = f"""{header}## Step {step}: {step_name}
**Timestamp:** {timestamp}
**Status:** PASS

**Inputs:**
{inputs_section}

---

"""

        return entry

    @classmethod
    def pre_check_previous_transcript(
        cls,
        previous_step: int,
        previous_step_name: str
    ) -> Optional[dict]:
        """
        PRE-check: Verify previous step's transcript exists.

        Defense-in-depth: Returns NEEDS_RETRY with instructions for AI to
        regenerate transcript from audit log. AI is responsible for transcript
        generation (not the hook).

        Args:
            previous_step: Previous step number (e.g., 1 for Step 2's PRE-check)
            previous_step_name: Previous step name (e.g., "User Input")

        Returns:
            None if previous transcript exists (PRE-check passes)
            NEEDS_RETRY dict with instructions if missing (AI regenerates)
        """
        from pathlib import Path

        # Get run_id from audit logger
        audit_logger = cls.get_audit_logger()
        run_id = audit_logger.run_id

        # Safe run_id for Windows paths
        safe_run_id = run_id.replace(":", "-")

        # Transcript file path
        transcript_file = Path(f"tests/_reports/{safe_run_id}/workflow_transcript.md")

        # Check if transcript file exists
        if not transcript_file.exists():
            return {
                "status": "NEEDS_RETRY",
                "fix_applied": "transcript_regeneration_needed",
                "error": f"Step {previous_step} transcript missing",
                "message": "Regenerate transcript from audit log using TranscriptWriter",
                "transcript_fix": {
                    "run_id": run_id,
                    "expected_file": str(transcript_file),
                    "command": f'python -c "import sys; sys.path.insert(0, \'mcp_server\'); from utils.transcript_writer import TranscriptWriter; TranscriptWriter(\'{run_id}\').generate()"'
                },
                "teach": f"""
Transcript file missing. AI must regenerate from audit log.

**Action Required:**
Run this command to regenerate transcript:
```
python -c "import sys; sys.path.insert(0, 'mcp_server'); from utils.transcript_writer import TranscriptWriter; TranscriptWriter('{run_id}').generate()"
```

Then retry this gate call.

**Why:** Transcript generation is AI's responsibility (not hook).
The audit log has all the data - TranscriptWriter converts it to markdown.
                """
            }

        # Check if previous step's entry exists
        content = transcript_file.read_text(encoding='utf-8')
        step_marker = f"## Step {previous_step}"

        if step_marker not in content:
            return {
                "status": "NEEDS_RETRY",
                "fix_applied": "transcript_regeneration_needed",
                "error": f"Step {previous_step} ({previous_step_name}) entry missing from transcript",
                "message": "Regenerate transcript from audit log to include all steps",
                "transcript_fix": {
                    "run_id": run_id,
                    "expected_file": str(transcript_file),
                    "missing_step": previous_step,
                    "command": f'python -c "import sys; sys.path.insert(0, \'mcp_server\'); from utils.transcript_writer import TranscriptWriter; TranscriptWriter(\'{run_id}\').generate()"'
                },
                "teach": f"""
Transcript exists but Step {previous_step} entry is missing.

**Action Required:**
Regenerate transcript from audit log:
```
python -c "import sys; sys.path.insert(0, 'mcp_server'); from utils.transcript_writer import TranscriptWriter; TranscriptWriter('{run_id}').generate()"
```

Then retry this gate call.

**Why:** The audit log should have Step {previous_step} data.
TranscriptWriter reads audit log and generates complete transcript.
                """
            }

        # PRE-check passed
        return None
