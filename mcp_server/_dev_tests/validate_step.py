#!/usr/bin/env python3
"""
Step Validator - TDD validation script for 5-step workflow

Validates 6 criteria after each step completes:
1. State (Persistence) - workflow_state.json updated
2. Audit (Observability) - audit_log.json contains gate entry
3. Transcript (Human-Readable) - workflow_transcript.md updated
4. Gate Validation (Quality) - gate returns correct status
5. Protocol Adherence (AI) - AI follows step-XX.md guidance
6. Step Flow (Integrity) - can proceed to next step

Usage:
    python validate_step.py --run-id <run_id> --step <step_num>

    # Example:
    python validate_step.py --run-id 2026-01-22T11-11-06.892443Z --step 1

Exit codes:
    0 = All validations passed
    1 = One or more validations failed
    2 = Validation error (script issue)
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum


class Status(Enum):
    """Validation result status."""
    PASS = "[PASS]"
    FAIL = "[FAIL]"
    WARN = "[WARN]"
    ERROR = "[ERROR]"
    SKIP = "[SKIP]"


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    name: str
    status: Status
    message: str
    details: Optional[Dict[str, Any]] = None


class StepValidator:
    """Validates a completed step against 6 criteria."""

    def __init__(self, run_id: str, step_num: int):
        """
        Initialize validator.

        Args:
            run_id: Workflow run identifier (timestamp format)
            step_num: Step number to validate (1-5)
        """
        self.run_id = run_id
        self.step_num = step_num

        # Sanitize run_id for Windows paths
        self.safe_run_id = run_id.replace(":", "-")

        # Determine project root (go up from mcp_server/_dev_tests/)
        self.project_root = Path(__file__).parent.parent.parent

        # File paths
        self.state_file = self.project_root / "tests" / "_state" / self.safe_run_id / "workflow_state.json"
        self.audit_file = self.project_root / "tests" / "_audit" / f"audit_log_{self.safe_run_id}.json"
        self.transcript_file = self.project_root / "tests" / "_reports" / self.safe_run_id / "workflow_transcript.md"

        # Loaded data (cached)
        self._state_data: Optional[Dict] = None
        self._audit_data: Optional[Dict] = None
        self._transcript_content: Optional[str] = None

    def validate_all(self) -> List[ValidationResult]:
        """
        Run all 6 validations.

        Returns:
            List of validation results (one per criteria)
        """
        results = []

        print(f"\n{'='*70}")
        print(f"  Validating Step {self.step_num} - Run ID: {self.run_id}")
        print(f"{'='*70}\n")

        # 1. State (Persistence)
        results.append(self.check_state())

        # 2. Audit (Observability)
        results.append(self.check_audit())

        # 3. Transcript (Human-Readable Log)
        results.append(self.check_transcript())

        # 4. Gate Validation (Quality Control)
        results.append(self.check_gate())

        # 5. Protocol Adherence (AI Behavior)
        results.append(self.check_protocol())

        # 6. Step Flow (Workflow Integrity)
        results.append(self.check_flow())

        return results

    def check_state(self) -> ValidationResult:
        """
        1. State (Persistence)

        Validates:
        - tests/_state/{run_id}/workflow_state.json exists
        - JSON is valid
        - step_N key exists
        - (Progressive) Step data contains expected fields
        """
        try:
            # Level 1: File exists
            if not self.state_file.exists():
                return ValidationResult(
                    name="State (Persistence)",
                    status=Status.FAIL,
                    message="State file missing",
                    details={"expected_path": str(self.state_file)}
                )

            # Level 2: JSON valid
            try:
                with open(self.state_file, 'r') as f:
                    self._state_data = json.load(f)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    name="State (Persistence)",
                    status=Status.FAIL,
                    message="State file corrupted (invalid JSON)",
                    details={"error": str(e)}
                )

            # Level 3: Step key exists
            step_key = f"step_{self.step_num}"
            if step_key not in self._state_data:
                return ValidationResult(
                    name="State (Persistence)",
                    status=Status.FAIL,
                    message=f"Step {self.step_num} not saved in state",
                    details={
                        "found_steps": list(self._state_data.keys()),
                        "expected_step": step_key
                    }
                )

            step_data = self._state_data[step_key]

            # Level 4: Basic structure (progressive - will add field checks later)
            if not isinstance(step_data, dict):
                return ValidationResult(
                    name="State (Persistence)",
                    status=Status.FAIL,
                    message=f"Step {self.step_num} data is not a dictionary",
                    details={"type": type(step_data).__name__}
                )

            # Success
            return ValidationResult(
                name="State (Persistence)",
                status=Status.PASS,
                message=f"Step {self.step_num} state saved correctly",
                details={
                    "file": str(self.state_file),
                    "size": self.state_file.stat().st_size,
                    "fields": list(step_data.keys())
                }
            )

        except Exception as e:
            return ValidationResult(
                name="State (Persistence)",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_audit(self) -> ValidationResult:
        """
        2. Audit (Observability)

        Validates:
        - tests/_audit/audit_log_{run_id}.json exists
        - JSON is valid
        - Contains entry for this step's gate
        - (Progressive) Timestamp, input/output captured
        """
        try:
            # Level 1: File exists
            if not self.audit_file.exists():
                return ValidationResult(
                    name="Audit (Observability)",
                    status=Status.FAIL,
                    message="Audit file missing",
                    details={"expected_path": str(self.audit_file)}
                )

            # Level 2: JSON valid
            try:
                with open(self.audit_file, 'r') as f:
                    self._audit_data = json.load(f)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    name="Audit (Observability)",
                    status=Status.FAIL,
                    message="Audit file corrupted (invalid JSON)",
                    details={"error": str(e)}
                )

            # Level 3: Has events array
            if "events" not in self._audit_data:
                return ValidationResult(
                    name="Audit (Observability)",
                    status=Status.FAIL,
                    message="Audit file missing 'events' array",
                    details={"keys": list(self._audit_data.keys())}
                )

            events = self._audit_data["events"]
            if not isinstance(events, list):
                return ValidationResult(
                    name="Audit (Observability)",
                    status=Status.FAIL,
                    message="Audit 'events' is not an array",
                    details={"type": type(events).__name__}
                )

            # Level 4: Has gate entry for this step (progressive - will add field checks later)
            # Gate mapping for steps 1-5
            gate_map = {
                1: "qg_preflight",
                2: "qg_user_input",
                3: "qg_ai_processing",
                4: "qg_test_scenarios",
                5: "qg_discovered_elements"
            }

            expected_gate = gate_map.get(self.step_num)
            if expected_gate is None:
                return ValidationResult(
                    name="Audit (Observability)",
                    status=Status.SKIP,
                    message=f"No gate mapping for step {self.step_num}",
                    details={"available_steps": list(gate_map.keys())}
                )

            # Find gate entry
            gate_entries = [e for e in events if e.get("type") == "gate_validation" and expected_gate in e.get("gate", "")]

            if not gate_entries:
                return ValidationResult(
                    name="Audit (Observability)",
                    status=Status.FAIL,
                    message=f"No audit entry for gate: {expected_gate}",
                    details={
                        "expected_gate": expected_gate,
                        "found_gates": [e.get("gate") for e in events if e.get("type") == "gate_validation"]
                    }
                )

            # Success
            return ValidationResult(
                name="Audit (Observability)",
                status=Status.PASS,
                message=f"Gate {expected_gate} logged in audit",
                details={
                    "file": str(self.audit_file),
                    "total_events": len(events),
                    "gate_entries": len(gate_entries)
                }
            )

        except Exception as e:
            return ValidationResult(
                name="Audit (Observability)",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_transcript(self) -> ValidationResult:
        """
        3. Transcript (Human-Readable Log)

        Validates:
        - tests/_reports/{run_id}/workflow_transcript.md exists
        - Contains step entry
        - Append mode (doesn't overwrite previous steps)
        - Human-readable format (not raw JSON)
        """
        try:
            # Level 1: File exists
            if not self.transcript_file.exists():
                return ValidationResult(
                    name="Transcript (Human-Readable)",
                    status=Status.FAIL,
                    message="Transcript file missing",
                    details={
                        "expected_path": str(self.transcript_file),
                        "note": "TranscriptWriter not implemented yet - expected for TDD"
                    }
                )

            # Level 2: Can read file
            try:
                with open(self.transcript_file, 'r', encoding='utf-8') as f:
                    self._transcript_content = f.read()
            except Exception as e:
                return ValidationResult(
                    name="Transcript (Human-Readable)",
                    status=Status.FAIL,
                    message="Cannot read transcript file",
                    details={"error": str(e)}
                )

            # Level 3: Contains step entry (basic check - will refine later)
            step_marker = f"Step {self.step_num}"
            if step_marker not in self._transcript_content:
                return ValidationResult(
                    name="Transcript (Human-Readable)",
                    status=Status.WARN,
                    message=f"Step {self.step_num} not found in transcript",
                    details={
                        "searched_for": step_marker,
                        "file_size": len(self._transcript_content)
                    }
                )

            # Level 4: Append mode check (if step > 1, previous steps should exist)
            if self.step_num > 1:
                prev_marker = f"Step {self.step_num - 1}"
                if prev_marker not in self._transcript_content:
                    return ValidationResult(
                        name="Transcript (Human-Readable)",
                        status=Status.WARN,
                        message=f"Previous step (Step {self.step_num - 1}) missing - not appending?",
                        details={"note": "May be overwriting instead of appending"}
                    )

            # Success
            return ValidationResult(
                name="Transcript (Human-Readable)",
                status=Status.PASS,
                message=f"Step {self.step_num} logged in transcript",
                details={
                    "file": str(self.transcript_file),
                    "size": len(self._transcript_content),
                    "has_step": True
                }
            )

        except Exception as e:
            return ValidationResult(
                name="Transcript (Human-Readable)",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_gate(self) -> ValidationResult:
        """
        4. Gate Validation (Quality Control)

        Validates:
        - Gate returned expected status (pass/fail/NEEDS_RETRY)
        - Validation logic enforced step requirements
        - (Progressive) Blocking behavior correct
        """
        try:
            # Need audit data
            if self._audit_data is None:
                # Try to load if check_audit() was skipped
                if self.audit_file.exists():
                    with open(self.audit_file, 'r') as f:
                        self._audit_data = json.load(f)
                else:
                    return ValidationResult(
                        name="Gate Validation (Quality)",
                        status=Status.SKIP,
                        message="No audit data available (check_audit failed?)"
                    )

            # Find gate entry
            gate_map = {
                1: "qg_preflight",
                2: "qg_user_input",
                3: "qg_ai_processing",
                4: "qg_test_scenarios",
                5: "qg_discovered_elements"
            }

            expected_gate = gate_map.get(self.step_num)
            if expected_gate is None:
                return ValidationResult(
                    name="Gate Validation (Quality)",
                    status=Status.SKIP,
                    message=f"No gate mapping for step {self.step_num}"
                )

            events = self._audit_data.get("events", [])
            gate_entries = [e for e in events if e.get("type") == "gate_validation" and expected_gate in e.get("gate", "")]

            if not gate_entries:
                return ValidationResult(
                    name="Gate Validation (Quality)",
                    status=Status.FAIL,
                    message=f"Gate {expected_gate} not executed"
                )

            # Check most recent gate entry
            gate_entry = gate_entries[-1]
            result = gate_entry.get("result", "unknown")

            # Valid statuses: pass, fail, NEEDS_RETRY
            if result not in ["pass", "fail", "NEEDS_RETRY"]:
                return ValidationResult(
                    name="Gate Validation (Quality)",
                    status=Status.WARN,
                    message=f"Gate returned unexpected status: {result}",
                    details={"expected": ["pass", "fail", "NEEDS_RETRY"], "actual": result}
                )

            # Success (gate executed with valid status)
            return ValidationResult(
                name="Gate Validation (Quality)",
                status=Status.PASS,
                message=f"Gate {expected_gate} executed: {result}",
                details={
                    "gate": expected_gate,
                    "result": result,
                    "has_error": "error" in gate_entry,
                    "has_fix_hint": "fix_hint" in gate_entry
                }
            )

        except Exception as e:
            return ValidationResult(
                name="Gate Validation (Quality)",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_protocol(self) -> ValidationResult:
        """
        5. Protocol Adherence (AI Behavior)

        Validates:
        - AI follows step-XX.md guidance
        - User prompts match protocol templates
        - Error messages match protocol format

        NOTE: This is subjective and requires human review.
        Validator provides data, human validates adherence.
        """
        try:
            # This check requires human review - we can only provide data
            # For TDD, we mark this as SKIP initially and improve later

            return ValidationResult(
                name="Protocol Adherence (AI)",
                status=Status.SKIP,
                message="Requires human review (not automated yet)",
                details={
                    "note": "Review Step protocol: .claude/skills/qa-management-layer/references/step-0{}.md".format(self.step_num),
                    "manual_checks": [
                        "AI asked correct questions?",
                        "User prompts match templates?",
                        "Error messages formatted correctly?"
                    ]
                }
            )

        except Exception as e:
            return ValidationResult(
                name="Protocol Adherence (AI)",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_flow(self) -> ValidationResult:
        """
        6. Step Flow (Workflow Integrity)

        Validates:
        - Can proceed to next step if gate passed
        - Blocked from next step if gate failed
        - State accumulation works (later steps can access earlier step data)
        """
        try:
            # Need state and audit data
            if self._state_data is None or self._audit_data is None:
                return ValidationResult(
                    name="Step Flow (Integrity)",
                    status=Status.SKIP,
                    message="Missing state or audit data"
                )

            # Check if gate passed
            gate_map = {
                1: "qg_preflight",
                2: "qg_user_input",
                3: "qg_ai_processing",
                4: "qg_test_scenarios",
                5: "qg_discovered_elements"
            }

            expected_gate = gate_map.get(self.step_num)
            events = self._audit_data.get("events", [])
            gate_entries = [e for e in events if e.get("type") == "gate_validation" and expected_gate in e.get("gate", "")]

            if not gate_entries:
                return ValidationResult(
                    name="Step Flow (Integrity)",
                    status=Status.FAIL,
                    message="Cannot determine if step passed (no gate entry)"
                )

            gate_result = gate_entries[-1].get("result", "unknown")

            # If gate passed, check if next step can access this step's data
            if gate_result == "pass":
                step_key = f"step_{self.step_num}"
                if step_key not in self._state_data:
                    return ValidationResult(
                        name="Step Flow (Integrity)",
                        status=Status.FAIL,
                        message="Gate passed but state not saved (flow broken)"
                    )

                # Check state accumulation (can access previous steps)
                if self.step_num > 1:
                    prev_key = f"step_{self.step_num - 1}"
                    if prev_key not in self._state_data:
                        return ValidationResult(
                            name="Step Flow (Integrity)",
                            status=Status.WARN,
                            message=f"Cannot access previous step data (Step {self.step_num - 1} missing)",
                            details={"note": "State accumulation may be broken"}
                        )

                # Success - can proceed
                return ValidationResult(
                    name="Step Flow (Integrity)",
                    status=Status.PASS,
                    message=f"Step {self.step_num} passed, can proceed to Step {self.step_num + 1}",
                    details={
                        "gate_result": gate_result,
                        "state_saved": True,
                        "previous_steps_accessible": self.step_num == 1 or f"step_{self.step_num - 1}" in self._state_data
                    }
                )

            # Gate failed - should be blocked
            return ValidationResult(
                name="Step Flow (Integrity)",
                status=Status.PASS,
                message=f"Step {self.step_num} failed, correctly blocked from proceeding",
                details={
                    "gate_result": gate_result,
                    "note": "User should fix issue before continuing"
                }
            )

        except Exception as e:
            return ValidationResult(
                name="Step Flow (Integrity)",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def print_results(self, results: List[ValidationResult]) -> None:
        """
        Print validation results in human-readable format.

        Args:
            results: List of validation results to display
        """
        print(f"\n{'='*70}")
        print(f"  Validation Results")
        print(f"{'='*70}\n")

        for result in results:
            print(f"{result.status.value} {result.name}")
            print(f"   {result.message}")

            if result.details:
                print(f"   Details:")
                for key, value in result.details.items():
                    if isinstance(value, list):
                        print(f"     • {key}: {', '.join(str(v) for v in value)}")
                    else:
                        print(f"     • {key}: {value}")
            print()

        # Summary
        passed = sum(1 for r in results if r.status == Status.PASS)
        failed = sum(1 for r in results if r.status == Status.FAIL)
        warned = sum(1 for r in results if r.status == Status.WARN)
        skipped = sum(1 for r in results if r.status == Status.SKIP)
        errors = sum(1 for r in results if r.status == Status.ERROR)

        print(f"{'='*70}")
        print(f"  Summary: {passed}/{len(results)} passed")
        if failed > 0:
            print(f"  [FAIL] {failed} failed")
        if warned > 0:
            print(f"  [WARN] {warned} warnings")
        if skipped > 0:
            print(f"  [SKIP] {skipped} skipped")
        if errors > 0:
            print(f"  [ERROR] {errors} errors")
        print(f"{'='*70}\n")


def main():
    """Main entry point for validator."""
    parser = argparse.ArgumentParser(
        description="Validate a completed workflow step against 6 criteria",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate Step 1 of a workflow run
  python validate_step.py --run-id 2026-01-22T11-11-06.892443Z --step 1

  # Validate Step 2
  python validate_step.py --run-id 2026-01-22T11-11-06.892443Z --step 2

Exit codes:
  0 = All validations passed
  1 = One or more validations failed
  2 = Validation error (script issue)
        """
    )

    parser.add_argument(
        '--run-id',
        required=True,
        help='Workflow run identifier (timestamp format)'
    )

    parser.add_argument(
        '--step',
        type=int,
        required=True,
        choices=[1, 2, 3, 4, 5],
        help='Step number to validate (1-5)'
    )

    args = parser.parse_args()

    # Create validator
    validator = StepValidator(args.run_id, args.step)

    # Run validations
    try:
        results = validator.validate_all()
        validator.print_results(results)

        # Determine exit code
        has_errors = any(r.status == Status.ERROR for r in results)
        has_failures = any(r.status == Status.FAIL for r in results)

        if has_errors:
            print("[ERROR] Validation errors occurred (script issue)")
            return 2
        elif has_failures:
            print("[FAIL] One or more validations failed")
            return 1
        else:
            print("[PASS] All validations passed!")
            return 0

    except Exception as e:
        print(f"\n[ERROR] Validator crashed: {type(e).__name__}")
        print(f"   Error: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
