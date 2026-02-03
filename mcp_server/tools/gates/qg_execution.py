"""
QGExecution - Step 5 Execution Validation Gate with HITL Triage.

Validates test execution results and enables Human-in-the-Loop (HITL)
triage workflow when tests fail.

Features:
- Test passed/failed validation
- 7 diagnostic data types capture (MVP)
- AI analysis (suggestive with confidence 0-100%)
- HITL triage presentation (3 options)
- Error signature tracking and retry policy

Adapted from archived Step 11 implementation for 5-step workflow.
Part of FR-05: Execution Validation Quality Gate with HITL.
"""

import json
import hashlib
from typing import Dict, Any, Optional, List
from pathlib import Path
from .base_gate import BaseGate


class QGExecution(BaseGate):
    """Step 5: Execution validation gate with HITL triage workflow."""

    # Retry policy constants
    SAME_ERROR_LIMIT = 2  # Same error 2x -> ask human
    TOTAL_ATTEMPT_LIMIT = 5  # 5 attempts total -> confirm with human

    @classmethod
    def validate(cls, arguments: dict) -> dict:
        """
        Validate test execution results and enable HITL triage.

        Args:
            arguments: Dict with:
                - test_result (required): Result dict from run_test operation
                - workflow (optional): Workflow/domain name
                - test_path (optional): Path to test file

        Returns:
            pass_response if test passed
            NEEDS_RETRY with hitl_required if test failed (triggers HITL triage)

        Workflow:
        1. Validate test execution completed
        2. If passed -> return pass_response
        3. If failed -> capture diagnostic data -> return NEEDS_RETRY with hitl_required
        """
        # Validate required fields
        test_result = arguments.get("test_result")
        if not test_result:
            return cls.fail_response(
                error="Missing required parameter: test_result",
                teach="Provide test_result from run_test operation.",
                step=5,
                gate_name="qg_execution",
                mode="POST"
            )

        # Validate test execution completed
        if test_result.get("status") not in ["passed", "failed", "crashed"]:
            return cls.fail_response(
                error=f"Invalid test status: {test_result.get('status')}",
                teach="Test status must be 'passed', 'failed', or 'crashed'.",
                step=5,
                gate_name="qg_execution",
                mode="POST"
            )

        # Test passed -> PASS response
        if test_result.get("status") == "passed":
            return cls.pass_response(
                step=5,
                gate_name="qg_execution",
                mode="POST",
                metadata={
                    "test_status": "passed",
                    "duration": test_result.get("duration"),
                    "report_path": test_result.get("report_path")
                }
            )

        # Test failed or crashed -> Capture diagnostic data + HITL triage
        diagnostic_data = cls._capture_diagnostic_data(test_result, arguments)

        # AI analysis
        ai_analysis = cls._generate_ai_analysis(diagnostic_data)

        # Triage presentation
        triage_message = cls._format_triage_presentation(
            test_result=test_result,
            diagnostic_data=diagnostic_data,
            ai_analysis=ai_analysis,
            test_path=arguments.get("test_path")
        )

        # Check retry policy
        retry_decision = cls._check_retry_policy(
            test_result=test_result,
            workflow=arguments.get("workflow")
        )

        # Log to audit trail
        cls.get_audit_logger().log_gate(
            step=5,
            gate_name="qg_execution",
            mode="POST",
            result="needs_retry",
            error=f"Test failed: {test_result.get('status')}",
            metadata={
                "test_status": test_result.get("status"),
                "ai_analysis": ai_analysis,
                "retry_decision": retry_decision
            }
        )

        # Return NEEDS_RETRY with hitl_required (triggers HITL triage)
        return {
            "status": "NEEDS_RETRY",
            "fix_applied": "hitl_required",
            "fix_data": {
                "diagnostic_data": diagnostic_data,
                "ai_analysis": ai_analysis,
                "triage_options": ["application_defect", "test_issue", "investigate", "other"],
                "presentation": triage_message,
                "retry_decision": retry_decision
            },
            "message": "Test failed. HITL triage required - present options to user and await decision."
        }

    @classmethod
    def _capture_diagnostic_data(cls, test_result: dict, arguments: dict) -> dict:
        """
        Capture 7 diagnostic data types.

        Args:
            test_result: Result from run_test operation
            arguments: Original validation arguments

        Returns:
            Dict with 7 diagnostic data types (MVP v1)
        """
        return {
            "version": "v1",
            "data_types": {
                # 1. Test Execution
                "test_execution": {
                    "pytest_output": test_result.get("output"),
                    "exit_code": test_result.get("exit_code"),
                    "duration": test_result.get("duration"),
                    "report_path": test_result.get("report_path"),
                    "failure_data": test_result.get("failure_data")
                },
                # 2. Page State (Playwright snapshot - to be implemented)
                "page_state": {
                    "snapshot": None,  # TODO: Implement automatic snapshot on failure
                    "url": None,
                    "dom_structure": None
                },
                # 3. Browser Context
                "browser_context": {
                    "url": None,  # TODO: Extract from test execution
                    "cookies": None,
                    "local_storage": None,
                    "session_storage": None
                },
                # 4. Expected vs Actual
                "expected_vs_actual": {
                    "expected": None,  # TODO: Extract from assertion
                    "actual": None,
                    "comparison": test_result.get("failure_data", {}).get("failed_assertion") if test_result.get("failure_data") else None
                },
                # 5. Test Context
                "test_context": {
                    "test_file": arguments.get("test_path"),
                    "test_function": None,  # TODO: Extract from pytest output
                    "line_number": test_result.get("failure_data", {}).get("error_location") if test_result.get("failure_data") else None,
                    "fixtures": None
                },
                # 6. Test Data
                "test_data": {
                    "credentials": "[REDACTED]",  # Credentials redacted for security
                    "workflow_parameters": arguments.get("workflow"),
                    "test_inputs": None
                },
                # 7. Execution Flow
                "execution_flow": {
                    "stack_trace": test_result.get("failure_data", {}).get("stack_trace") if test_result.get("failure_data") else None,
                    "framework_calls": None,  # TODO: Extract from logs
                    "navigation_history": None  # TODO: Read from audit trail
                }
            }
        }

    @classmethod
    def _generate_ai_analysis(cls, diagnostic_data: dict) -> dict:
        """
        Generate AI analysis of failure (suggestive, not definitive).

        AI presents hypothesis with confidence level (0-100%),
        not definitive classification.

        Args:
            diagnostic_data: Captured diagnostic data

        Returns:
            Dict with:
                - likely_cause: Hypothesis about failure cause
                - confidence: 0-100% confidence level
                - evidence: Supporting evidence from diagnostic data
                - suggested_fix: Potential fix approach
        """
        test_exec = diagnostic_data["data_types"]["test_execution"]
        failure_data = test_exec.get("failure_data", {})

        # Simple heuristic analysis (MVP - can be enhanced with LLM later)
        likely_cause = "Unknown failure"
        confidence = 50
        evidence = []
        suggested_fix = "Review test code and application behavior"

        # Heuristic 1: Assertion failure
        if failure_data and failure_data.get("failed_assertion"):
            likely_cause = "Assertion failure - expected value not met"
            confidence = 70
            evidence.append(f"Assertion: {failure_data['failed_assertion']}")
            suggested_fix = "Verify assertion logic and expected values"

        # Heuristic 2: Timeout
        if test_exec.get("pytest_output") and "timeout" in test_exec["pytest_output"].lower():
            likely_cause = "Test timeout - execution exceeded time limit"
            confidence = 85
            evidence.append("Pytest output contains 'timeout'")
            suggested_fix = "Increase timeout or optimize test execution"

        # Heuristic 3: Element not found
        if test_exec.get("pytest_output") and any(
            kw in test_exec["pytest_output"].lower()
            for kw in ["element not found", "nosuchelementexception", "could not find"]
        ):
            likely_cause = "Element locator issue - element not found on page"
            confidence = 80
            evidence.append("Selenium exception: Element not found")
            suggested_fix = "Verify locator strategy and add explicit waits"

        # Heuristic 4: Import error
        if test_exec.get("pytest_output") and "importerror" in test_exec["pytest_output"].lower():
            likely_cause = "Import error - missing module or incorrect path"
            confidence = 90
            evidence.append("ImportError in pytest output")
            suggested_fix = "Check import paths and module availability"

        return {
            "likely_cause": likely_cause,
            "confidence": confidence,
            "evidence": evidence,
            "suggested_fix": suggested_fix
        }

    @classmethod
    def _format_triage_presentation(
        cls,
        test_result: dict,
        diagnostic_data: dict,
        ai_analysis: dict,
        test_path: Optional[str]
    ) -> str:
        """
        Format HITL triage presentation.

        Args:
            test_result: Result from run_test
            diagnostic_data: Captured diagnostic data
            ai_analysis: AI analysis results
            test_path: Path to test file

        Returns:
            Formatted triage message for user
        """
        test_exec = diagnostic_data["data_types"]["test_execution"]
        failure_data = test_exec.get("failure_data", {})

        # Extract test name from path
        test_name = Path(test_path).stem if test_path else "unknown_test"

        # Build triage message
        message = f"""
===== STEP 5: TEST EXECUTION FAILED =====

Test: {test_name}
Status: {test_result.get('status')}
Duration: {test_result.get('duration', 0):.2f}s

Error: {failure_data.get('failed_assertion', 'See output below') if failure_data else 'See output below'}
Location: {failure_data.get('error_location', 'Unknown') if failure_data else 'Unknown'}

AI Analysis (Confidence: {ai_analysis['confidence']}%):
{ai_analysis['likely_cause']}

Evidence:
{chr(10).join('- ' + e for e in ai_analysis['evidence']) if ai_analysis['evidence'] else '- No specific evidence identified'}

Suggested Fix:
{ai_analysis['suggested_fix']}

==========================================

HOW SHOULD WE PROCEED?

1. Application Defect
   -> Test is correct, application behavior is unexpected
   -> Log defect to DEFECT_LOG.md and stop workflow
   -> Manual investigation required

2. Test Issue
   -> Fix test code (locator/timing/logic)
   -> AI generates fix based on triage decision
   -> Re-run validation after fix

3. Investigate Further
   -> Show full diagnostic data (all 7 types)
   -> Review detailed evidence before deciding
   -> Return to these options after investigation

4. Other
   -> Describe what you want to do
   -> AI follows your instructions

Enter choice (1-4):
"""
        return message.strip()

    @classmethod
    def _check_retry_policy(cls, test_result: dict, workflow: Optional[str]) -> dict:
        """
        Check retry policy and error signature tracking.

        Args:
            test_result: Result from run_test
            workflow: Workflow/domain name

        Returns:
            Dict with:
                - should_retry: bool
                - reason: str (why retry is/isn't allowed)
                - attempt_count: int
                - same_error_count: int
                - error_signature: str
        """
        # Generate error signature (hash of error message + location)
        error_output = test_result.get("output", "")
        failure_data = test_result.get("failure_data", {})
        error_location = failure_data.get("error_location", "") if failure_data else ""

        error_signature = hashlib.md5(
            f"{error_output[:500]}{error_location}".encode()
        ).hexdigest()[:16]

        # TODO: Integrate with StateManager to track attempts
        # For now, return basic structure
        return {
            "should_retry": True,  # Default: allow retry
            "reason": "No retry limits reached yet",
            "attempt_count": 0,  # TODO: Read from state
            "same_error_count": 0,  # TODO: Track error signature matches
            "error_signature": error_signature,
            "policy": {
                "same_error_limit": cls.SAME_ERROR_LIMIT,
                "total_attempt_limit": cls.TOTAL_ATTEMPT_LIMIT
            }
        }

    @classmethod
    def handle_triage_decision(cls, decision: str, diagnostic_data: dict) -> dict:
        """
        Handle user's triage decision.

        Args:
            decision: User's choice (1=defect, 2=test_issue, 3=investigate) or custom text
            diagnostic_data: Diagnostic data from validation

        Returns:
            Dict with next action and instructions
        """
        decision_normalized = decision.strip().lower()

        # Option 1: Application Defect
        if decision_normalized in ["1", "application_defect", "defect", "app bug"]:
            return {
                "action": "log_defect",
                "next_step": "Stop workflow and log to DEFECT_LOG.md",
                "blocking": True,
                "instructions": "Create defect entry with diagnostic data, stop workflow."
            }

        # Option 2: Test Issue
        elif decision_normalized in ["2", "test_issue", "fix test", "test bug"]:
            return {
                "action": "fix_test",
                "next_step": "AI generates fix, re-validate through dependency chain",
                "blocking": False,
                "instructions": "Determine which file to fix (POM/Task/Role/Test), apply fix, re-run gates."
            }

        # Option 3: Investigate
        elif decision_normalized in ["3", "investigate", "show data", "more info"]:
            return {
                "action": "investigate",
                "next_step": "Display full diagnostic data, return to triage options",
                "blocking": False,
                "instructions": f"""
Full Diagnostic Data (7 types):

{json.dumps(diagnostic_data, indent=2)}

After reviewing, make triage decision:
1. Application Defect
2. Test Issue
3. Abort workflow
"""
            }

        # Option 4: Other (explicit custom guidance)
        elif decision_normalized in ["4", "other"]:
            return {
                "action": "prompt_for_guidance",
                "next_step": "Ask user to describe what they want to do",
                "blocking": True,
                "instructions": "User selected 'Other'. Ask: What would you like to do?"
            }

        # Custom guidance (user typed instructions directly)
        else:
            return {
                "action": "custom_guidance",
                "next_step": "AI interprets custom instructions and proceeds",
                "blocking": False,
                "user_input": decision,
                "instructions": f"User provided custom guidance: {decision}"
            }
