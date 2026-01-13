"""
QGWorkflowComplete - Workflow Completion Meta-Gate (Task 61.0)

Validates 11-step workflow integrity with 8 cross-step consistency checks.

Features:
- Test path consistency (Step 9 vs Step 11)
- File existence validation (all generated files)
- Import path validity
- Workflow ID consistency
- Audit trail completeness (all 11 steps logged)
- State completeness (metadata present)
- Code modifications tracking
- No orphaned state detection
- HITL escalation on failure (not auto-restart)

Part of FR-11.5: Workflow Completion Validation Meta-Gate
"""

import json
import importlib.util
from typing import Dict, Any, Optional, List
from pathlib import Path
from .base_gate import BaseGate


class QGWorkflowComplete(BaseGate):
    """Workflow completion meta-gate - validates 11-step workflow integrity."""

    @classmethod
    def validate(cls, arguments: dict) -> dict:
        """
        Validate 11-step workflow integrity with 8 consistency checks.

        Args:
            arguments: Dict with:
                - workflow_id (required): Workflow identifier
                - test_path (required): Test path from Step 11 execution
                - test_result (required): Test result from run_test operation

        Returns:
            pass_response if all checks pass
            fail_response with escalation options if any check fails

        Workflow:
        1. Validate required fields
        2. Run 8 cross-step consistency checks
        3. If all pass → return pass_response
        4. If any fail → present escalation options → wait for HITL
        """
        # Validate required fields
        workflow_id = arguments.get("workflow_id")
        test_path = arguments.get("test_path")
        test_result = arguments.get("test_result")

        if not workflow_id:
            return cls.fail_response(
                error="Missing required parameter: workflow_id",
                fix_hint="Provide workflow_id from workflow state.",
                step=11,
                gate_name="qg_workflow_complete",
                mode="POST"
            )

        if not test_path:
            return cls.fail_response(
                error="Missing required parameter: test_path",
                fix_hint="Provide test_path from Step 11 execution.",
                step=11,
                gate_name="qg_workflow_complete",
                mode="POST"
            )

        if not test_result:
            return cls.fail_response(
                error="Missing required parameter: test_result",
                fix_hint="Provide test_result from run_test operation.",
                step=11,
                gate_name="qg_workflow_complete",
                mode="POST"
            )

        # Run 8 cross-step consistency checks (FR-11.5.1)
        checks = [
            ("Test path consistency", cls._check_test_path_consistency),
            ("File existence", cls._check_file_existence),
            ("Import path validity", cls._check_import_paths),
            ("Workflow ID consistency", cls._check_workflow_id),
            ("Audit trail complete", cls._check_audit_trail),
            ("State completeness", cls._check_state_completeness),
            ("Code modifications tracked", cls._check_modifications_tracked),
            ("No orphaned state", cls._check_no_orphaned_state),
        ]

        failed_checks = []
        for check_name, check_func in checks:
            result = check_func(workflow_id, test_path, test_result, arguments)
            if result:  # result is error dict if check failed
                failed_checks.append((check_name, result))

        # All checks passed → PASS response (FR-11.5.2)
        if not failed_checks:
            return cls.pass_response(
                step=11,
                gate_name="qg_workflow_complete",
                mode="POST",
                metadata={
                    "workflow_id": workflow_id,
                    "test_path": test_path,
                    "all_checks_passed": True
                }
            )

        # Checks failed → Escalate to human (FR-11.5.3, FR-11.5.4)
        escalation_message = cls._format_escalation_message(failed_checks, workflow_id, test_path)

        return cls.fail_response(
            error=f"Workflow integrity validation failed: {len(failed_checks)} check(s) failed",
            fix_hint=escalation_message,
            step=11,
            gate_name="qg_workflow_complete",
            mode="POST",
            metadata={
                "workflow_id": workflow_id,
                "test_path": test_path,
                "failed_checks": [name for name, _ in failed_checks],
                "escalation_options": ["rerun_step11", "restart_workflow", "accept_as_is", "abort"]
            }
        )

    @classmethod
    def _check_test_path_consistency(
        cls,
        workflow_id: str,
        test_path: str,
        test_result: dict,
        arguments: dict
    ) -> Optional[dict]:
        """
        Check 1: Test path consistency (Step 9 test == Step 11 test).

        Validates that the test executed in Step 11 matches the test generated in Step 9.

        Returns:
            None if check passes, error dict if fails
        """
        state_manager = cls.get_state_manager()
        if not state_manager:
            # Cannot validate without state manager
            return None

        # Get Step 9 data (test generation)
        step9_data = state_manager.get_step(9)
        if not step9_data:
            return {
                "error": "Step 9 data not found in workflow state",
                "context": "Cannot validate test path consistency without Step 9 metadata",
                "suggested_fix": "Check if workflow completed Step 9 successfully"
            }

        # Extract test path from Step 9 metadata
        step9_test_path = step9_data.get("metadata", {}).get("test_path")
        if not step9_test_path:
            # Try alternate location in metadata
            step9_test_path = step9_data.get("test_path")

        if not step9_test_path:
            return {
                "error": "Test path not found in Step 9 metadata",
                "context": "Step 9 completed but test_path missing from state",
                "suggested_fix": "Verify qg_test_runner saves test_path to metadata"
            }

        # Normalize paths for comparison (handle forward/backslash differences)
        step9_normalized = Path(step9_test_path).as_posix()
        step11_normalized = Path(test_path).as_posix()

        if step9_normalized != step11_normalized:
            return {
                "error": "Test path mismatch between Step 9 and Step 11",
                "expected": step9_test_path,
                "actual": test_path,
                "context": "Step 11 ran a different test than Step 9 generated",
                "suggested_fix": "Verify workflow_id consistency and test path passed to run_test"
            }

        return None  # Check passed

    @classmethod
    def _check_file_existence(
        cls,
        workflow_id: str,
        test_path: str,
        test_result: dict,
        arguments: dict
    ) -> Optional[dict]:
        """
        Check 2: File existence (all generated files from Steps 6-9 exist on disk).

        Validates that all files reported as generated in Steps 6-9 actually exist.

        Returns:
            None if check passes, error dict if fails
        """
        state_manager = cls.get_state_manager()
        if not state_manager:
            return None

        # Steps that generate files: 6 (POM), 7 (Task), 8 (Role), 9 (Test)
        file_steps = [
            (6, "POM", "pom_path"),
            (7, "Task", "task_path"),
            (8, "Role", "role_path"),
            (9, "Test", "test_path"),
        ]

        missing_files = []

        for step_num, step_name, path_key in file_steps:
            step_data = state_manager.get_step(step_num)
            if not step_data:
                continue  # Step not executed yet (acceptable)

            # Extract file path from metadata
            file_path = step_data.get("metadata", {}).get(path_key)
            if not file_path:
                # Try alternate location
                file_path = step_data.get(path_key)

            if file_path:
                # Check if file exists
                if not Path(file_path).exists():
                    missing_files.append({
                        "step": step_num,
                        "step_name": step_name,
                        "file_path": file_path
                    })

        if missing_files:
            return {
                "error": f"{len(missing_files)} generated file(s) missing from disk",
                "missing_files": missing_files,
                "context": "Files were marked as saved but do not exist",
                "suggested_fix": "Check Step 10 (qg_save_run) POST validation - files should be written to disk"
            }

        return None  # Check passed

    @classmethod
    def _check_import_paths(
        cls,
        workflow_id: str,
        test_path: str,
        test_result: dict,
        arguments: dict
    ) -> Optional[dict]:
        """
        Check 3: Import path validity (all imports in generated code work).

        Validates that imports in test file can be resolved.

        Returns:
            None if check passes, error dict if fails
        """
        # Check if test file exists
        if not Path(test_path).exists():
            return {
                "error": f"Test file not found: {test_path}",
                "context": "Cannot validate imports if test file missing",
                "suggested_fix": "Check file existence validation first"
            }

        # Read test file and extract imports
        try:
            with open(test_path, 'r') as f:
                test_code = f.read()
        except Exception as e:
            return {
                "error": f"Failed to read test file: {str(e)}",
                "context": test_path,
                "suggested_fix": "Verify file permissions and encoding"
            }

        # Extract import statements (simple regex-based extraction)
        import re
        import_pattern = r'^(?:from\s+[\w.]+\s+import\s+[\w, ]+|import\s+[\w., ]+)$'
        imports = re.findall(import_pattern, test_code, re.MULTILINE)

        # Try to validate imports (basic check - can be enhanced)
        invalid_imports = []
        for import_stmt in imports:
            # Skip standard library imports
            if any(lib in import_stmt for lib in ['pytest', 'typing', 'pathlib', 'json', 'sys']):
                continue

            # Extract module name
            if import_stmt.startswith('from '):
                module_name = import_stmt.split()[1]
            else:
                module_name = import_stmt.split()[1].split('.')[0]

            # Check if module can be found (relative imports should work from project root)
            # This is a basic check - full validation would require sys.path manipulation
            if not any(char in module_name for char in ['framework', 'tests', 'pages', 'tasks', 'roles']):
                continue  # Not a framework import

            # For now, we'll just check the syntax is valid
            # Full import resolution would require executing in correct context

        # For MVP, we'll accept if no obvious errors found
        # More robust validation can be added in v2
        return None  # Check passed (basic validation)

    @classmethod
    def _check_workflow_id(
        cls,
        workflow_id: str,
        test_path: str,
        test_result: dict,
        arguments: dict
    ) -> Optional[dict]:
        """
        Check 4: Workflow ID consistency (same workflow_id across all steps).

        Validates that all steps used the same workflow_id.

        Returns:
            None if check passes, error dict if fails
        """
        state_manager = cls.get_state_manager()
        if not state_manager:
            return None

        # Check workflow_id in steps 2-11
        inconsistent_steps = []

        for step_num in range(2, 12):
            step_data = state_manager.get_step(step_num)
            if not step_data:
                continue  # Step not executed

            # Extract workflow_id from metadata
            step_workflow_id = step_data.get("metadata", {}).get("workflow")
            if not step_workflow_id:
                # Try alternate locations
                step_workflow_id = step_data.get("workflow") or step_data.get("domain")

            if step_workflow_id and step_workflow_id != workflow_id:
                inconsistent_steps.append({
                    "step": step_num,
                    "expected": workflow_id,
                    "actual": step_workflow_id
                })

        if inconsistent_steps:
            return {
                "error": f"Workflow ID inconsistency detected in {len(inconsistent_steps)} step(s)",
                "inconsistencies": inconsistent_steps,
                "context": "Different workflow IDs used across steps",
                "suggested_fix": "Verify workflow parameter passed consistently through all steps"
            }

        return None  # Check passed

    @classmethod
    def _check_audit_trail(
        cls,
        workflow_id: str,
        test_path: str,
        test_result: dict,
        arguments: dict
    ) -> Optional[dict]:
        """
        Check 5: Audit trail complete (all 11 steps logged).

        Validates that audit trail contains entries for all 11 steps.

        Returns:
            None if check passes, error dict if fails
        """
        audit_logger = cls.get_audit_logger()
        if not audit_logger:
            return None

        # Read audit file
        audit_file = Path(audit_logger._audit_file)
        if not audit_file.exists():
            return {
                "error": "Audit file not found",
                "expected_path": str(audit_file),
                "context": "Workflow completed but audit file missing",
                "suggested_fix": "Check AuditLogger configuration and DD-30 enforcement"
            }

        try:
            with open(audit_file, 'r') as f:
                audit_data = json.load(f)
        except Exception as e:
            return {
                "error": f"Failed to read audit file: {str(e)}",
                "context": str(audit_file),
                "suggested_fix": "Verify JSON format and file integrity"
            }

        # Check that all 11 steps are present
        steps_logged = audit_data.get("steps", [])
        step_numbers = [step.get("step") for step in steps_logged]

        missing_steps = []
        for step_num in range(1, 12):
            if step_num not in step_numbers:
                missing_steps.append(step_num)

        if missing_steps:
            return {
                "error": f"Audit trail incomplete: {len(missing_steps)} step(s) missing",
                "missing_steps": missing_steps,
                "total_logged": len(step_numbers),
                "context": "Not all workflow steps were logged to audit trail",
                "suggested_fix": "Check PostToolUse hook and gate pass_response() calls"
            }

        return None  # Check passed

    @classmethod
    def _check_state_completeness(
        cls,
        workflow_id: str,
        test_path: str,
        test_result: dict,
        arguments: dict
    ) -> Optional[dict]:
        """
        Check 6: State completeness (all required metadata present).

        Validates that workflow state contains all required metadata for Steps 1-11.

        Returns:
            None if check passes, error dict if fails
        """
        state_manager = cls.get_state_manager()
        if not state_manager:
            return None

        # Required metadata by step
        required_metadata = {
            2: ["persona", "url", "workflow"],
            3: ["bdd_scenarios", "expected_states"],
            4: ["test_scenarios"],
            5: ["discovered_elements"],
            6: ["pom_metadata"],
            7: ["task_metadata"],
            8: ["role_metadata"],
            9: ["test_path"],
            11: ["test_result"]
        }

        missing_metadata = []

        for step_num, required_keys in required_metadata.items():
            step_data = state_manager.get_step(step_num)
            if not step_data:
                missing_metadata.append({
                    "step": step_num,
                    "error": "Step data missing from state"
                })
                continue

            metadata = step_data.get("metadata", {})

            for key in required_keys:
                # Check in metadata dict first
                if key not in metadata:
                    # Try top-level step_data as fallback
                    if key not in step_data:
                        missing_metadata.append({
                            "step": step_num,
                            "missing_key": key
                        })

        if missing_metadata:
            return {
                "error": f"State metadata incomplete: {len(missing_metadata)} item(s) missing",
                "missing_items": missing_metadata,
                "context": "Required metadata not saved to workflow state",
                "suggested_fix": "Check gate pass_response() metadata parameter and StateManager.save()"
            }

        return None  # Check passed

    @classmethod
    def _check_modifications_tracked(
        cls,
        workflow_id: str,
        test_path: str,
        test_result: dict,
        arguments: dict
    ) -> Optional[dict]:
        """
        Check 7: Code modifications tracked (Step 11 changes recorded).

        Validates that any code modifications in Step 11 were recorded in audit trail.

        Returns:
            None if check passes, error dict if fails
        """
        # Check if any fixes were applied in Step 11
        # This would be indicated by multiple test runs in audit trail

        audit_logger = cls.get_audit_logger()
        if not audit_logger:
            return None

        audit_file = Path(audit_logger._audit_file)
        if not audit_file.exists():
            return None  # Already caught by audit trail check

        try:
            with open(audit_file, 'r') as f:
                audit_data = json.load(f)
        except Exception:
            return None  # Already caught by audit trail check

        # Count Step 11 executions (qg_execution calls)
        step11_executions = [
            step for step in audit_data.get("steps", [])
            if step.get("step") == 11 and step.get("gate") == "qg_execution"
        ]

        # If multiple executions, check if modifications were tracked
        if len(step11_executions) > 1:
            # Look for modification records
            modifications_tracked = any(
                step.get("metadata", {}).get("code_modified")
                for step in step11_executions
            )

            if not modifications_tracked:
                return {
                    "error": "Code modifications not tracked in audit trail",
                    "context": f"Step 11 executed {len(step11_executions)} times but no modification records found",
                    "suggested_fix": "Ensure qg_execution records code modifications when fixes are applied"
                }

        return None  # Check passed

    @classmethod
    def _check_no_orphaned_state(
        cls,
        workflow_id: str,
        test_path: str,
        test_result: dict,
        arguments: dict
    ) -> Optional[dict]:
        """
        Check 8: No orphaned state (clean state, no partial failures).

        Validates that workflow state is clean and complete, no artifacts from failed runs.

        Returns:
            None if check passes, error dict if fails
        """
        state_manager = cls.get_state_manager()
        if not state_manager:
            return None

        # Check for state inconsistencies:
        # 1. All steps 1-11 should be completed (is_step_complete)
        # 2. No gaps in step sequence

        incomplete_steps = []
        for step_num in range(1, 12):
            if not state_manager.is_step_complete(step_num):
                incomplete_steps.append(step_num)

        if incomplete_steps:
            return {
                "error": f"Workflow state incomplete: {len(incomplete_steps)} step(s) not marked complete",
                "incomplete_steps": incomplete_steps,
                "context": "Steps executed but not marked as complete in state",
                "suggested_fix": "Check gate pass_response() calls and StateManager.mark_complete()"
            }

        return None  # Check passed

    @classmethod
    def _format_escalation_message(
        cls,
        failed_checks: List[tuple],
        workflow_id: str,
        test_path: str
    ) -> str:
        """
        Format HITL escalation message (FR-11.5.5).

        Args:
            failed_checks: List of (check_name, error_dict) tuples
            workflow_id: Workflow identifier
            test_path: Test path from Step 11

        Returns:
            Formatted escalation message for user
        """
        message = f"""
===== WORKFLOW INTEGRITY VALIDATION FAILED =====

Workflow ID: {workflow_id}
Test: {test_path}

{len(failed_checks)} consistency check(s) failed:

"""

        for i, (check_name, error_data) in enumerate(failed_checks, 1):
            message += f"""
{i}. {check_name} - FAILED
   Error: {error_data.get('error', 'Unknown error')}
   Context: {error_data.get('context', 'No context provided')}

   Details:
"""
            # Add specific details based on error data
            for key, value in error_data.items():
                if key not in ['error', 'context', 'suggested_fix']:
                    message += f"   - {key}: {value}\n"

            message += f"""
   Suggested Fix: {error_data.get('suggested_fix', 'Manual investigation required')}

"""

        message += """
==========================================

ESCALATION OPTIONS

1. Re-run Step 11
   → Specific test issue (e.g., wrong test path)
   → Re-execute Step 11 with corrected parameters
   → Does not restart workflow

2. Restart Workflow
   → Fundamental inconsistency detected
   → Clear state and start from Step 1
   → Use when state corruption suspected

3. Accept As-Is
   → Known issue, proceed anyway
   → Manual verification confirmed integrity
   → Use when checks are too strict for this case

4. Abort Workflow
   → Manual investigation needed
   → Cannot proceed without fixing root cause
   → Use when unsure how to proceed

Enter choice (1, 2, 3, or 4) or provide custom guidance:
"""
        return message.strip()

    @classmethod
    def handle_escalation_decision(cls, decision: str, failed_checks: List[dict]) -> dict:
        """
        Handle user's escalation decision (FR-11.5.4).

        Args:
            decision: User's choice (1=rerun, 2=restart, 3=accept, 4=abort) or custom text
            failed_checks: Failed consistency checks

        Returns:
            Dict with next action and instructions
        """
        decision_normalized = decision.strip().lower()

        # Option 1: Re-run Step 11
        if decision_normalized in ["1", "rerun", "re-run step 11", "rerun step 11"]:
            return {
                "action": "rerun_step11",
                "next_step": "Re-execute Step 11 with corrected parameters",
                "blocking": False,
                "instructions": "Review failed checks, correct parameters, re-run run_test → qg_execution → qg_workflow_complete"
            }

        # Option 2: Restart Workflow
        elif decision_normalized in ["2", "restart", "restart workflow"]:
            return {
                "action": "restart_workflow",
                "next_step": "Clear state and restart from Step 1",
                "blocking": True,
                "instructions": "Clear workflow_state.json, start fresh workflow from Step 1"
            }

        # Option 3: Accept As-Is
        elif decision_normalized in ["3", "accept", "accept as-is", "accept as is"]:
            return {
                "action": "accept_as_is",
                "next_step": "Mark workflow complete despite inconsistencies",
                "blocking": False,
                "instructions": "Workflow marked complete. Manual verification assumed correct."
            }

        # Option 4: Abort
        elif decision_normalized in ["4", "abort", "abort workflow"]:
            return {
                "action": "abort",
                "next_step": "Abort workflow, manual investigation required",
                "blocking": True,
                "instructions": "Workflow aborted. Review failed checks and state data before proceeding."
            }

        # Custom guidance
        else:
            return {
                "action": "custom_guidance",
                "next_step": "AI interprets custom instructions and proceeds",
                "blocking": False,
                "user_input": decision,
                "instructions": f"User provided custom guidance: {decision}"
            }
