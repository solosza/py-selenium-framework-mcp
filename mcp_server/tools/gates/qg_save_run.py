"""
Quality Gate: Save Run (Step 10).

PRE-only validation gate for file save and test execution.

PRE Validation:
- Step 9 complete
- All 4 code blocks present (pom_code, task_code, role_code, test_code)
- No skeleton code in any layer (DD-25 final sweep)
- Primary: code from input_data; Fallback: code from state (IC-10-01)

No POST Validation (PRE-only gate per IC-10-02).

Enforces: DD-22, DD-25, IC-10-01 through IC-10-05
"""

import re
from typing import Any, Dict, Optional, Tuple

from .base_gate import BaseGate
from utils.state_manager import StateManager


class QGSaveRun(BaseGate):
    """Quality gate for Step 10: Save & Run."""

    # Skeleton code patterns (DD-25) - same as other gates
    SKELETON_PATTERNS = [
        (r'^\s*pass\s*$', 'pass statement'),
        (r'#\s*TODO:', 'TODO comment'),
        (r'#\s*[Aa]dd\s+.*\s+as\s+needed', 'placeholder comment'),
        (r'raise\s+NotImplementedError', 'NotImplementedError'),
    ]

    # Code field to step mapping (IC-10-05)
    CODE_FIELDS = {
        "pom_code": {"step": 6, "layer": "POM"},
        "task_code": {"step": 7, "layer": "Task"},
        "role_code": {"step": 8, "layer": "Role"},
        "test_code": {"step": 9, "layer": "Test"},
    }

    @classmethod
    def _get_state_manager(cls) -> StateManager:
        """Get StateManager instance. Extracted for testing."""
        # Task 19.0: Use per-run state isolation
        try:
            audit_logger = cls.get_audit_logger()
            if audit_logger and hasattr(audit_logger, 'run_id'):
                return StateManager(run_id=audit_logger.run_id)
        except (AttributeError, TypeError):
            # Fall back to default if audit logger not available (e.g., tests)
            pass
        return StateManager()

    @classmethod
    def _get_code(cls, input_data: Dict[str, Any], field: str, step: int) -> Optional[str]:
        """
        Get code from input_data or fallback to state (IC-10-01).

        Args:
            input_data: Input data dict
            field: Code field name (e.g., 'pom_code')
            step: Step number to read from state if not in input

        Returns:
            Code string or None if not found in either source
        """
        # Primary: check input_data
        code = input_data.get(field)
        if code is not None:
            return code

        # Fallback: check state (use same field name as input)
        state_manager = cls._get_state_manager()
        step_data = state_manager.get_step(step)
        if step_data and isinstance(step_data, dict):
            return step_data.get(field)

        return None

    @classmethod
    def _validate_code_field(
        cls,
        input_data: Dict[str, Any],
        field: str,
        step: int,
        layer: str
    ) -> Optional[Dict[str, Any]]:
        """
        Validate a single code field for presence and skeleton.

        Args:
            input_data: Input data dict
            field: Code field name
            step: Step number for this code
            layer: Human-readable layer name (POM, Task, Role, Test)

        Returns:
            fail_response if validation fails, None if passes
        """
        code = cls._get_code(input_data, field, step)

        # Check presence
        if code is None:
            return cls.fail_response(
                error=f"Missing {field}: {layer} code not found",
                fix_hint=f"Go back to Step {step} to generate {layer} code."
            )

        # Check not empty
        if not isinstance(code, str) or not code.strip():
            return cls.fail_response(
                error=f"Empty {field}: {layer} code is empty",
                fix_hint=f"Go back to Step {step} to generate {layer} code."
            )

        # DEF-048: Check if code was reconstructed and needs POST validation
        reconstruction_error = cls._check_code_reconstruction(input_data, code, field, step, layer)
        if reconstruction_error:
            return reconstruction_error

        # Check for skeleton code (DD-25, IC-10-03)
        skeleton_error = cls._detect_skeleton_code(code, layer)
        if skeleton_error:
            return skeleton_error

        return None

    @classmethod
    def _check_code_reconstruction(
        cls,
        input_data: Dict[str, Any],
        code: str,
        field: str,
        step: int,
        layer: str
    ) -> Optional[Dict[str, Any]]:
        """
        DEF-048: Check if code was reconstructed and enforce POST validation.

        When code is reconstructed (modified after generation), it must pass
        POST gate validation before saving to disk.

        Args:
            input_data: Input data dict
            code: Code string being validated
            field: Code field name
            step: Step number
            layer: Layer name (POM, Task, Role, Test)

        Returns:
            fail_response if reconstructed code not validated, None otherwise
        """
        # Get original code from state
        state_manager = cls._get_state_manager()
        step_data = state_manager.get_step(step)

        if not step_data:
            # No state exists - this is original generation, not reconstruction
            return None

        # Get state code based on layer
        state_code = None
        if layer == "POM":
            # POMs stored in generated_poms structure
            generated_poms = step_data.get("generated_poms", {})
            # Check if ANY POM code differs (simplified check for MVP)
            # In practice, we'd need page_name to check specific POM
            for pom_name, pom_data in generated_poms.items():
                if isinstance(pom_data, dict) and pom_data.get("code") == code:
                    # Found matching code in state - not reconstructed
                    return None
            # If we get here, code doesn't match any POM in state
            state_code = "DIFFERS"  # Marker that code was modified
        else:
            # Task/Role/Test stored directly in step data
            state_code = step_data.get(field)

        # If code differs from state, require POST validation proof
        if state_code and state_code != code:
            # Check if metadata is present (proof of POST validation)
            metadata_field = field.replace("_code", "_metadata")
            metadata = input_data.get(metadata_field)

            if not metadata:
                gate_name = {
                    "POM": "qg_page_object",
                    "Task": "qg_task",
                    "Role": "qg_role",
                    "Test": "qg_test_runner"
                }.get(layer, "appropriate quality gate")

                return cls.fail_response(
                    error=f"Code reconstruction detected for {layer} without POST validation (DEF-048)",
                    fix_hint=f"""
Reconstructed/modified code must pass POST gate before saving.

Pattern:
1. Call {gate_name} POST validation with modified code
2. If validation passes, provide metadata proof
3. Then proceed to Step 10 save

Example:
# Validate modified {layer} code
result = {gate_name}.validate({{
    "mode": "POST",
    "code": modified_code,
    "metadata": {{...}}
}})

if result["status"] == "pass":
    # Now safe to save
    qg_save_run.validate({{
        "mode": "PRE",
        "{field}": modified_code,
        "{metadata_field}": result["metadata"]  # Proof of validation
    }})

Fix: Validate reconstructed {layer} code through POST gate first.
                    """
                )

        return None

    @classmethod
    def _detect_skeleton_code(cls, code: str, layer: str) -> Optional[Dict[str, Any]]:
        """
        Detect skeleton code patterns in generated code (DD-25, IC-10-03).

        Returns fail_response if skeleton detected, None otherwise.
        """
        for pattern, description in cls.SKELETON_PATTERNS:
            if re.search(pattern, code, re.MULTILINE):
                return cls.fail_response(
                    error=f"Skeleton code detected in {layer}: {description}",
                    fix_hint=f"Complete the {layer} code. Remove placeholders and implement all methods."
                )
        return None

    @classmethod
    def _validate_files_exist(cls, state_manager: StateManager) -> Optional[Dict[str, Any]]:
        """
        Task 19.0: Validate that all generated files exist on disk.

        Checks files from Steps 6-9:
        - Step 6 (POMs): May have multiple POM files
        - Step 7 (Task): Single task file
        - Step 8 (Role): Single role file
        - Step 9 (Test): Single test file

        Note: Only validates if metadata with file paths exists.
        If no metadata, validation is skipped (e.g., during testing with mocks).

        Args:
            state_manager: StateManager instance to use for reading state

        Returns:
            fail_response if any files missing, None if all exist or no metadata
        """
        import os
        from pathlib import Path

        missing_files = []
        has_any_metadata = False  # Track if any metadata exists

        # Get project root (3 levels up from mcp_server/tools/gates/)
        project_root = Path(__file__).parent.parent.parent.parent

        # Step 6: Check POM files (may be multiple)
        step6_data = state_manager.get_step(6)
        if step6_data and isinstance(step6_data, dict):
            generated_poms = step6_data.get("generated_poms")
            if generated_poms and isinstance(generated_poms, dict) and len(generated_poms) > 0:
                has_any_metadata = True
                for pom_name, pom_data in generated_poms.items():
                    if isinstance(pom_data, dict):
                        import_path = pom_data.get("import_path")
                        if import_path:
                            # Convert import path to file path
                            relative_path = import_path.replace(".", os.sep) + ".py"
                            file_path = project_root / relative_path
                            if not file_path.exists():
                                missing_files.append({
                                    "step": 6,
                                    "layer": "POM",
                                    "name": pom_name,
                                    "path": str(file_path)
                                })

        # Step 7: Check Task file
        step7_data = state_manager.get_step(7)
        if step7_data and isinstance(step7_data, dict):
            task_metadata = step7_data.get("task_metadata")
            if task_metadata and isinstance(task_metadata, dict) and len(task_metadata) > 0:
                has_any_metadata = True
                import_path = task_metadata.get("import_path")
                if import_path:
                    relative_path = import_path.replace(".", os.sep) + ".py"
                    file_path = project_root / relative_path
                    if not file_path.exists():
                        missing_files.append({
                            "step": 7,
                            "layer": "Task",
                            "name": task_metadata.get("class_name", "Unknown"),
                            "path": str(file_path)
                        })

        # Step 8: Check Role file
        step8_data = state_manager.get_step(8)
        if step8_data and isinstance(step8_data, dict):
            role_metadata = step8_data.get("role_metadata")
            if role_metadata and isinstance(role_metadata, dict) and len(role_metadata) > 0:
                has_any_metadata = True
                import_path = role_metadata.get("import_path")
                if import_path:
                    relative_path = import_path.replace(".", os.sep) + ".py"
                    file_path = project_root / relative_path
                    if not file_path.exists():
                        missing_files.append({
                            "step": 8,
                            "layer": "Role",
                            "name": role_metadata.get("class_name", "Unknown"),
                            "path": str(file_path)
                        })

        # Step 9: Check Test file
        step9_data = state_manager.get_step(9)
        if step9_data and isinstance(step9_data, dict):
            test_metadata = step9_data.get("test_metadata")
            if test_metadata and isinstance(test_metadata, dict) and len(test_metadata) > 0:
                has_any_metadata = True
                file_path_str = test_metadata.get("file_path")
                if file_path_str:
                    # Test file_path may be relative or absolute
                    file_path = Path(file_path_str)
                    if not file_path.is_absolute():
                        file_path = project_root / file_path_str
                    if not file_path.exists():
                        missing_files.append({
                            "step": 9,
                            "layer": "Test",
                            "name": test_metadata.get("test_name", "Unknown"),
                            "path": str(file_path)
                        })

        # Only fail if metadata exists but files are missing
        # If no metadata, skip validation (e.g., test mocks)
        if has_any_metadata and missing_files:
            error_lines = ["Missing generated files on disk:"]
            for missing in missing_files:
                error_lines.append(f"  - Step {missing['step']} ({missing['layer']}): {missing['name']}")
                error_lines.append(f"    Expected: {missing['path']}")

            return cls.fail_response(
                error="\n".join(error_lines),
                fix_hint="""Files were not written to disk. This indicates DEF-051 fix not working.

Possible causes:
1. Quality gates (Steps 6-9) not writing files after POST validation
2. File write permission issues
3. Invalid file paths in metadata

Fix: Check that Steps 6-9 gates write files immediately after POST validation passes.
"""
            )

        return None

    @classmethod
    def validate_pre(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        PRE validation before file save.

        Validates:
        - Step 9 is complete
        - All 4 code blocks present (input_data or state)
        - No skeleton code in any layer (DD-25 final sweep)

        Args:
            input_data: Dict with pom_code, task_code, role_code, test_code

        Returns:
            {"status": "pass"} or {"status": "fail", "error": str, "fix_hint": str}
        """
        # Check Step 9 completion
        state_manager = cls._get_state_manager()
        if not state_manager.is_step_complete(9):
            return cls.fail_response(
                error="Step 9 is not complete. Cannot proceed to Step 10.",
                fix_hint="Complete Step 9 (Generate Test Runner) first."
            )

        # Validate all 4 code blocks (IC-10-04: fail-fast)
        validated_layers = []
        for field, info in cls.CODE_FIELDS.items():
            error = cls._validate_code_field(
                input_data,
                field,
                info["step"],
                info["layer"]
            )
            if error:
                return error
            validated_layers.append(info["layer"])

        # Task 19.0: Validate that all generated files exist on disk
        file_validation_error = cls._validate_files_exist(state_manager)
        if file_validation_error:
            return file_validation_error

        return cls.pass_response(
            step=10,
            gate_name="qg_save_run",
            mode="PRE",
            metadata={
                "validated_layers": validated_layers,
                "ready_for_save": True,
                "files_validated": True  # Task 19.0: Indicate files checked
            }
        )

    @classmethod
    def validate(cls, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main validation entry point.

        Routes to PRE validation only (PRE-only gate per IC-10-02).

        Args:
            input_data: Dict with "mode" field and code fields

        Returns:
            Validation result
        """
        mode = input_data.get("mode", "")

        if not mode:
            return cls.fail_response(
                error="Missing required field: mode",
                fix_hint="Specify mode='PRE' for validation."
            )

        mode_upper = mode.upper() if isinstance(mode, str) else ""

        if mode_upper == "PRE":
            return cls.validate_pre(input_data)
        elif mode_upper == "POST":
            return cls.fail_response(
                error="POST mode not supported. This is a PRE-only gate.",
                fix_hint="Use mode='PRE'. Step 10 validates before save, not after."
            )
        else:
            return cls.fail_response(
                error=f"Invalid mode: '{mode}'. Must be 'PRE'.",
                fix_hint="Specify mode='PRE' for validation."
            )
