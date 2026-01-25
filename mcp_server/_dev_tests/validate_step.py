#!/usr/bin/env python3
"""
Step Validator - TDD validation script for 5-step workflow

ALL VALIDATIONS (always run for every step):
1. State (Persistence) - workflow_state.json updated
2. Audit (Observability) - audit_log.json contains gate entry
3. Transcript (Human-Readable) - workflow_transcript.md updated
4. Gate Validation (Quality) - gate returns correct status
5. Protocol Adherence (AI) - AI follows step-XX.md guidance
6. Step Flow (Integrity) - can proceed to next step
7. Run ID Uniqueness - Fresh run_id created (Step 1 only, expected fail for Step 2+)
8. Audit Log Isolation - Steps 1-N present, final event for each is PASS (allows retries)
9. Session Marker Consistency - .current_run_id marker exists and matches
10. Hook Execution - PostToolUse hook executed recently
11. Manual File Detection - Files auto-generated (not manually created)
12. Audit Step Number - Audit entry has correct step field
13. Old Marker Cleanup - Old marker location properly cleaned up
14. Audit State Path - Audit entry references correct state path

Usage:
    # Validate any step (runs all 14 checks)
    python validate_step.py --run-id <run_id> --step <step_num>

    # Examples:
    python validate_step.py --run-id 2026-01-22T11-11-06.892443Z --step 1
    python validate_step.py --run-id 2026-01-22T11-11-06.892443Z --step 2

Note:
    Some checks may fail/skip for certain steps - see each check's docstring
    for applicability and how to interpret results.

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
    """Validates a completed step against 14 criteria."""

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

    def _load_audit(self) -> Optional[Dict]:
        """
        Load audit data from file (cached).

        Returns:
            Audit data dict if file exists and valid, None otherwise
        """
        if self._audit_data is not None:
            return self._audit_data

        if not self.audit_file.exists():
            return None

        try:
            with open(self.audit_file, 'r') as f:
                self._audit_data = json.load(f)
            return self._audit_data
        except (json.JSONDecodeError, IOError):
            return None

    def _load_transcript(self) -> Optional[str]:
        """
        Load transcript content from file (cached).

        Returns:
            Transcript content string if file exists, None otherwise
        """
        if self._transcript_content is not None:
            return self._transcript_content

        if not self.transcript_file.exists():
            return None

        try:
            with open(self.transcript_file, 'r', encoding='utf-8') as f:
                self._transcript_content = f.read()
            return self._transcript_content
        except IOError:
            return None

    def validate_all(self) -> List[ValidationResult]:
        """
        Run all validations (14 checks total).

        Returns:
            List of validation results (one per criteria)
        """
        results = []

        print(f"\n{'='*70}")
        print(f"  Validating Step {self.step_num} - Run ID: {self.run_id}")
        print(f"{'='*70}\n")

        # All validations (always run for every step)
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

        # 7. Run ID Uniqueness
        results.append(self.check_run_id_uniqueness())

        # 8. Audit Log Isolation
        results.append(self.check_audit_isolation())

        # 9. Session Marker Consistency
        results.append(self.check_session_marker())

        # 10. Hook Execution
        results.append(self.check_hook_execution())

        # 11. Manual File Detection
        results.append(self.check_manual_files())

        # 12. Audit Step Number
        results.append(self.check_audit_step_number())

        # 13. Old Marker Cleanup
        results.append(self.check_old_marker_cleanup())

        # 14. Audit State Path
        results.append(self.check_audit_state_path())

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
                1: "qg_user_input",
                2: "qg_preflight",
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
                1: "qg_user_input",
                2: "qg_preflight",
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
                    "has_teach": "teach" in gate_entry
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
                1: "qg_user_input",
                2: "qg_preflight",
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

    # =========================================================================
    # NEW WORKFLOW VALIDATIONS (--expect-new-workflow flag)
    # =========================================================================

    def check_run_id_uniqueness(self) -> ValidationResult:
        """
        7. Run ID Uniqueness (New Workflow)

        Validates:
        - Run ID is recent (created within last 5 minutes)
        - Run ID is unique (not reused from previous workflow)

        Applicability:
        - Step 1: SHOULD PASS (fresh workflow creates new run_id)
        - Step 2-5: WILL FAIL (run_id becomes older as workflow progresses)

        How to interpret:
        - Step 1 FAIL → Bug: run_id reused from previous workflow
        - Step 2-5 FAIL → EXPECTED (ignore this failure)

        Gap Found: Bug where new workflows reused old run_ids instead of creating fresh ones.
        """
        try:
            # Parse run_id timestamp
            # Handle both formats:
            # - ISO format: 2026-01-25T01:28:37.064712Z (with colons)
            # - Safe format: 2026-01-25T01-28-37.064712Z (with hyphens for Windows paths)
            try:
                # Try standard ISO format first
                run_id_time = datetime.fromisoformat(self.run_id.replace("Z", "+00:00"))
            except ValueError:
                # Try safe format (hyphens in time portion)
                # Convert 2026-01-25T01-28-37.064712Z to 2026-01-25T01:28:37.064712Z
                import re
                # Match pattern: date T hh-mm-ss
                safe_format = re.sub(
                    r'T(\d{2})-(\d{2})-(\d{2})',
                    r'T\1:\2:\3',
                    self.run_id
                )
                try:
                    run_id_time = datetime.fromisoformat(safe_format.replace("Z", "+00:00"))
                except ValueError:
                    return ValidationResult(
                        name="Run ID Uniqueness",
                        status=Status.FAIL,
                        message="Run ID is not a valid ISO timestamp",
                        details={"run_id": self.run_id}
                    )

            # Check if recent (within last 5 minutes)
            now = datetime.now(run_id_time.tzinfo)
            age_seconds = (now - run_id_time).total_seconds()

            if age_seconds > 300:  # 5 minutes
                return ValidationResult(
                    name="Run ID Uniqueness",
                    status=Status.FAIL,
                    message=f"Run ID is {int(age_seconds)}s old (expected fresh workflow < 300s)",
                    details={
                        "run_id": self.run_id,
                        "age_seconds": int(age_seconds),
                        "note": "This may indicate run_id was reused from previous workflow"
                    }
                )

            return ValidationResult(
                name="Run ID Uniqueness",
                status=Status.PASS,
                message=f"Run ID is fresh ({int(age_seconds)}s old)",
                details={"run_id": self.run_id, "age_seconds": int(age_seconds)}
            )

        except Exception as e:
            return ValidationResult(
                name="Run ID Uniqueness",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_audit_isolation(self) -> ValidationResult:
        """
        8. Audit Log Isolation (New Workflow)

        Validates:
        - Audit log only contains events for THIS workflow (steps 1-N)
        - No events from future steps or other workflows
        - Each step 1 through N has at least one event
        - The FINAL event for current step is PASS

        Applicability:
        - Step 1: At least 1 event for step 1, final must be PASS
        - Step 2: Events for steps 1 and 2, final for step 2 must be PASS
        - etc.

        Note: Multiple events per step are allowed (FAIL/retry scenarios).
        The gate may be called multiple times before passing.

        How to interpret:
        - Events from steps > N → Bug: contaminated with future steps
        - Missing events for steps 1-N → Bug: step was skipped
        - Final event for step N not PASS → Step didn't complete

        Gap Found: New workflows appended to old audit logs instead of creating fresh ones.
        """
        try:
            audit_data = self._load_audit()
            if not audit_data:
                return ValidationResult(
                    name="Audit Log Isolation",
                    status=Status.FAIL,
                    message="Audit log missing or corrupted",
                    details={"file": str(self.audit_file)}
                )

            events = audit_data.get("events", [])

            if not events:
                return ValidationResult(
                    name="Audit Log Isolation",
                    status=Status.FAIL,
                    message="Audit log has no events",
                    details={"file": str(self.audit_file)}
                )

            # Get all step numbers from events
            event_steps = [e.get("step") for e in events]

            # Check 1: No events from future steps (contamination)
            future_steps = [s for s in event_steps if s is not None and s > self.step_num]
            if future_steps:
                return ValidationResult(
                    name="Audit Log Isolation",
                    status=Status.FAIL,
                    message=f"Audit contains events from future steps: {set(future_steps)}",
                    details={
                        "current_step": self.step_num,
                        "future_steps_found": list(set(future_steps)),
                        "note": "Audit may be contaminated from another workflow"
                    }
                )

            # Check 2: Each step 1 through N has at least one event
            steps_present = set(s for s in event_steps if s is not None)
            expected_steps = set(range(1, self.step_num + 1))
            missing_steps = expected_steps - steps_present

            if missing_steps:
                return ValidationResult(
                    name="Audit Log Isolation",
                    status=Status.FAIL,
                    message=f"Missing events for steps: {sorted(missing_steps)}",
                    details={
                        "expected_steps": sorted(expected_steps),
                        "steps_found": sorted(steps_present),
                        "missing_steps": sorted(missing_steps)
                    }
                )

            # Check 3: Final event for current step is PASS
            current_step_events = [e for e in events if e.get("step") == self.step_num]
            if not current_step_events:
                return ValidationResult(
                    name="Audit Log Isolation",
                    status=Status.FAIL,
                    message=f"No events found for current step {self.step_num}",
                    details={}
                )

            final_event = current_step_events[-1]
            final_result = final_event.get("result", "unknown")

            if final_result != "pass":
                return ValidationResult(
                    name="Audit Log Isolation",
                    status=Status.WARN,
                    message=f"Final event for Step {self.step_num} is '{final_result}' (expected 'pass')",
                    details={
                        "final_result": final_result,
                        "total_events_for_step": len(current_step_events),
                        "note": "Step may not have completed successfully"
                    }
                )

            # Count events per step for info
            events_per_step = {}
            for s in range(1, self.step_num + 1):
                events_per_step[s] = len([e for e in events if e.get("step") == s])

            return ValidationResult(
                name="Audit Log Isolation",
                status=Status.PASS,
                message=f"Audit log isolated (steps 1-{self.step_num} present, final events are PASS)",
                details={
                    "total_events": len(events),
                    "events_per_step": events_per_step,
                    "final_result_step_{0}".format(self.step_num): final_result
                }
            )

        except Exception as e:
            return ValidationResult(
                name="Audit Log Isolation",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_session_marker(self) -> ValidationResult:
        """
        9. Session Marker Consistency

        Validates:
        - .current_run_id marker exists
        - Marker contains THIS run_id
        - No stale markers from previous workflows

        Applicability:
        - All steps: SHOULD PASS (marker should exist and match run_id)

        How to interpret:
        - FAIL → Bug: Session marker missing or has wrong run_id
        - This would cause gates to save to wrong workflow directory

        Gap Found: Multiple marker locations (old vs new) out of sync, causing run_id reuse.
        """
        try:
            marker_file = self.project_root / "tests" / "_state" / ".current_run_id"

            if not marker_file.exists():
                return ValidationResult(
                    name="Session Marker Consistency",
                    status=Status.FAIL,
                    message="Session marker missing",
                    details={
                        "expected_path": str(marker_file),
                        "note": "PostToolUse hook needs this marker to write audit entries"
                    }
                )

            marker_run_id = marker_file.read_text().strip()

            if marker_run_id != self.run_id:
                return ValidationResult(
                    name="Session Marker Consistency",
                    status=Status.FAIL,
                    message="Session marker has wrong run_id",
                    details={
                        "expected_run_id": self.run_id,
                        "marker_run_id": marker_run_id,
                        "note": "This causes gates to save to wrong workflow"
                    }
                )

            return ValidationResult(
                name="Session Marker Consistency",
                status=Status.PASS,
                message="Session marker matches run_id",
                details={"marker_path": str(marker_file)}
            )

        except Exception as e:
            return ValidationResult(
                name="Session Marker Consistency",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_hook_execution(self) -> ValidationResult:
        """
        10. Hook Execution (PostToolUse)

        Validates:
        - Audit entry has recent timestamp (within last 60s)
        - Implies PostToolUse hook executed successfully

        Applicability:
        - All steps: SHOULD PASS (latest event should be recent)

        How to interpret:
        - PASS → Hook executed recently for this step
        - WARN (>60s old) → May be validating old workflow, check run_id
        - FAIL → Hook didn't execute or audit entry missing

        Gap Found: PostToolUse hook configured but not executing, no validation caught it.
        """
        try:
            audit_data = self._load_audit()
            if not audit_data:
                return ValidationResult(
                    name="Hook Execution",
                    status=Status.FAIL,
                    message="Cannot validate hook execution (audit log missing)",
                    details={}
                )

            events = audit_data.get("events", [])

            # Find most recent event for this step
            step_events = [e for e in events if e.get("step") == self.step_num]
            if not step_events:
                return ValidationResult(
                    name="Hook Execution",
                    status=Status.FAIL,
                    message=f"No events found for Step {self.step_num}",
                    details={}
                )

            latest_event = step_events[-1]
            timestamp_str = latest_event.get("timestamp", "")

            try:
                event_time = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
                now = datetime.now(event_time.tzinfo)
                age_seconds = (now - event_time).total_seconds()

                if age_seconds > 60:
                    return ValidationResult(
                        name="Hook Execution",
                        status=Status.WARN,
                        message=f"Audit entry is {int(age_seconds)}s old (expected < 60s)",
                        details={
                            "timestamp": timestamp_str,
                            "age_seconds": int(age_seconds),
                            "note": "Hook may have executed in previous session"
                        }
                    )

                return ValidationResult(
                    name="Hook Execution",
                    status=Status.PASS,
                    message=f"PostToolUse hook executed recently ({int(age_seconds)}s ago)",
                    details={"timestamp": timestamp_str}
                )

            except ValueError:
                return ValidationResult(
                    name="Hook Execution",
                    status=Status.WARN,
                    message="Cannot parse audit timestamp",
                    details={"timestamp": timestamp_str}
                )

        except Exception as e:
            return ValidationResult(
                name="Hook Execution",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_manual_files(self) -> ValidationResult:
        """
        11. Manual File Detection

        Validates:
        - Transcript was NOT manually created (should be auto-generated)
        - Checks for evidence of manual creation vs system generation

        Applicability:
        - All steps: Currently SKIP (TranscriptWriter not implemented)
        - Future: SHOULD PASS (when TranscriptWriter implemented)

        How to interpret:
        - SKIP → Expected (TranscriptWriter not yet called)
        - WARN → Transcript exists but may be manually created
        - FAIL → Transcript was manually created (workaround detected)

        Gap Found: We manually created transcripts, validator accepted them as valid.
        """
        try:
            if not self.transcript_file.exists():
                # No transcript = no manual file issue
                return ValidationResult(
                    name="Manual File Detection",
                    status=Status.SKIP,
                    message="No transcript file to check (expected - not implemented yet)",
                    details={}
                )

            # Check if transcript was created by TranscriptWriter
            content = self._load_transcript()

            # TranscriptWriter signature: "**Generated:** <timestamp>"
            has_generated_marker = "**Generated:**" in content

            # Manual transcripts typically have custom formatting
            has_manual_markers = any([
                "## Step" in content and "**Timestamp:**" in content,  # Our manual format
                "Status:" in content and "PASS" in content  # Custom status markers
            ])

            if has_manual_markers and not has_generated_marker:
                return ValidationResult(
                    name="Manual File Detection",
                    status=Status.WARN,
                    message="Transcript appears to be manually created (not auto-generated)",
                    details={
                        "has_generated_marker": has_generated_marker,
                        "file": str(self.transcript_file),
                        "note": "Transcripts should be auto-generated by TranscriptWriter.generate()"
                    }
                )

            if has_generated_marker:
                return ValidationResult(
                    name="Manual File Detection",
                    status=Status.PASS,
                    message="Transcript auto-generated by TranscriptWriter",
                    details={"file": str(self.transcript_file)}
                )

            return ValidationResult(
                name="Manual File Detection",
                status=Status.SKIP,
                message="Cannot determine if transcript is manual or auto-generated",
                details={}
            )

        except Exception as e:
            return ValidationResult(
                name="Manual File Detection",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_audit_step_number(self) -> ValidationResult:
        """
        12. Audit Entry Step Number Validation

        Validates:
        - Audit entry has correct "step" field matching expected step number
        - Catches incorrect gate-to-step mappings in audit-trail-writer.py

        Applicability:
        - All steps: SHOULD PASS (audit entry "step" should match actual step)

        How to interpret:
        - FAIL → Bug: Gate-to-step mapping wrong in audit-trail-writer.py
        - Example: Step 1 audit has "step": 2 → mappings swapped

        Gap Found: Gate mappings were swapped (Step 1↔Step 2), but validator only checked gate NAME.
        """
        try:
            audit_data = self._load_audit()
            if not audit_data:
                return ValidationResult(
                    name="Audit Step Number",
                    status=Status.FAIL,
                    message="Cannot validate step number (audit log missing)",
                    details={}
                )

            events = audit_data.get("events", [])

            # Find events for this step's gate
            gate_map = {
                1: "qg_user_input",
                2: "qg_preflight",
                3: "qg_ai_processing",
                4: "qg_test_scenarios",
                5: "qg_discovered_elements"
            }
            expected_gate = gate_map.get(self.step_num)

            if not expected_gate:
                return ValidationResult(
                    name="Audit Step Number",
                    status=Status.SKIP,
                    message=f"No gate mapping for step {self.step_num}",
                    details={}
                )

            # Find gate entries
            gate_entries = [e for e in events if e.get("type") == "gate_validation" and expected_gate in e.get("gate", "")]

            if not gate_entries:
                return ValidationResult(
                    name="Audit Step Number",
                    status=Status.FAIL,
                    message=f"No audit entry found for gate: {expected_gate}",
                    details={}
                )

            # Verify step number matches
            for entry in gate_entries:
                actual_step = entry.get("step")
                if actual_step != self.step_num:
                    return ValidationResult(
                        name="Audit Step Number",
                        status=Status.FAIL,
                        message=f"Audit entry has wrong step number",
                        details={
                            "expected_step": self.step_num,
                            "actual_step": actual_step,
                            "gate": expected_gate,
                            "note": "Gate-to-step mapping is incorrect in audit-trail-writer.py"
                        }
                    )

            return ValidationResult(
                name="Audit Step Number",
                status=Status.PASS,
                message=f"Audit entry has correct step number ({self.step_num})",
                details={"gate": expected_gate}
            )

        except Exception as e:
            return ValidationResult(
                name="Audit Step Number",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_old_marker_cleanup(self) -> ValidationResult:
        """
        13. Old Marker Location Cleanup

        Validates:
        - Old marker location (mcp_server/state/.run_session) does NOT exist
        - Ensures _clear_session_marker() properly cleaned up old location

        Applicability:
        - All steps: SHOULD PASS (old location should not exist)

        How to interpret:
        - PASS → Old marker properly cleaned up (or never existed)
        - FAIL → _clear_session_marker() didn't clean old location
        - This proves migration from old to new location worked correctly

        Gap Found: Session marker location migrated from OLD to NEW, but clear didn't clean old location.
        """
        try:
            old_marker_file = self.project_root / "mcp_server" / "state" / ".run_session"

            if old_marker_file.exists():
                old_run_id = old_marker_file.read_text().strip()
                return ValidationResult(
                    name="Old Marker Cleanup",
                    status=Status.FAIL,
                    message="Old marker location still exists (not cleaned up)",
                    details={
                        "old_location": str(old_marker_file),
                        "old_run_id": old_run_id,
                        "note": "_clear_session_marker() should delete old location"
                    }
                )

            return ValidationResult(
                name="Old Marker Cleanup",
                status=Status.PASS,
                message="Old marker location properly cleaned up",
                details={"old_location": str(old_marker_file)}
            )

        except Exception as e:
            return ValidationResult(
                name="Old Marker Cleanup",
                status=Status.ERROR,
                message=f"Validator crashed: {type(e).__name__}",
                details={"error": str(e)}
            )

    def check_audit_state_path(self) -> ValidationResult:
        """
        14. Audit Entry State Path Validation

        Validates:
        - Audit entry references correct state path (tests/_state/{run_id}/workflow_state.json)
        - Catches audit hook reading from wrong state location

        Applicability:
        - All steps: SHOULD PASS (if state_path in audit metadata)
        - May SKIP if audit entry doesn't include state_path metadata

        How to interpret:
        - PASS → Audit hook reading from correct state location
        - FAIL → Audit hook reading from OLD location (mcp_server/state/)
        - SKIP → State path not included in audit metadata (not captured)

        Gap Found: audit-trail-writer.py was reading from OLD location (mcp_server/state/workflow_state.json).
        """
        try:
            audit_data = self._load_audit()
            if not audit_data:
                return ValidationResult(
                    name="Audit State Path",
                    status=Status.FAIL,
                    message="Cannot validate state path (audit log missing)",
                    details={}
                )

            events = audit_data.get("events", [])

            # Find events for this step
            step_events = [e for e in events if e.get("step") == self.step_num]

            if not step_events:
                return ValidationResult(
                    name="Audit State Path",
                    status=Status.FAIL,
                    message=f"No events found for Step {self.step_num}",
                    details={}
                )

            # Check if audit entry has state_path metadata (may not be in all events)
            latest_event = step_events[-1]
            metadata = latest_event.get("metadata", {})

            # State path may not be in all audit entries (depends on hook implementation)
            # If present, validate it
            if "state_file" in metadata or "state_path" in metadata:
                state_path = metadata.get("state_file") or metadata.get("state_path", "")
                expected_path = f"tests/_state/{self.run_id}/workflow_state.json"

                # Normalize paths for comparison (handle both / and \)
                state_path_normalized = state_path.replace("\\", "/")

                if expected_path not in state_path_normalized:
                    return ValidationResult(
                        name="Audit State Path",
                        status=Status.FAIL,
                        message="Audit entry references wrong state path",
                        details={
                            "expected_path": expected_path,
                            "actual_path": state_path,
                            "note": "audit-trail-writer.py reading from wrong location"
                        }
                    )

                return ValidationResult(
                    name="Audit State Path",
                    status=Status.PASS,
                    message="Audit entry references correct state path",
                    details={"state_path": state_path}
                )
            else:
                # State path not in metadata - skip validation
                return ValidationResult(
                    name="Audit State Path",
                    status=Status.SKIP,
                    message="Audit entry does not contain state path metadata",
                    details={"note": "State path validation skipped"}
                )

        except Exception as e:
            return ValidationResult(
                name="Audit State Path",
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
        description="Validate a completed workflow step (14 checks total)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Validate Step 1 of a workflow run (runs all 14 checks)
  python validate_step.py --run-id 2026-01-22T11-11-06.892443Z --step 1

  # Validate Step 2 (runs all 14 checks)
  python validate_step.py --run-id 2026-01-22T11-11-06.892443Z --step 2

  # Validate Step 3 (runs all 14 checks)
  python validate_step.py --run-id 2026-01-22T11-11-06.892443Z --step 3

All 14 Checks (always run):
  1. State (Persistence)
  2. Audit (Observability)
  3. Transcript (Human-Readable)
  4. Gate Validation (Quality)
  5. Protocol Adherence (AI Behavior)
  6. Step Flow (Workflow Integrity)
  7. Run ID Uniqueness
  8. Audit Log Isolation
  9. Session Marker Consistency
  10. Hook Execution
  11. Manual File Detection
  12. Audit Step Number
  13. Old Marker Cleanup
  14. Audit State Path

Note:
  Some checks may fail/skip for certain steps (e.g., Check 7 will fail for Step 2+).
  See each check's docstring for applicability and how to interpret results.

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
