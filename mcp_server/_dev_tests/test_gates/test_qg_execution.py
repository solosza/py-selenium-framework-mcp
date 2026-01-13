"""
Unit tests for QGExecution gate - Task 60.0

Test suite for Step 11 execution validation gate with HITL triage.

Test Matrix:
- Happy path: 1 test (P0) - test passed validation
- Validation: 3 tests (P0) - test failed, missing result, invalid status
- Diagnostic capture: 1 test (P1) - 7 data types captured
- AI analysis: 3 tests (P1) - assertion, timeout, element not found
- Triage presentation: 1 test (P1) - format validation
- Retry policy: 1 test (P1) - error signature tracking
- Triage decisions: 3 tests (P0) - defect, test issue, investigate

Testing Skill Reference: .claude/skills/testing/
"""

import pytest
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from tools.gates.qg_execution import QGExecution


# ============================================================================
# HAPPY PATH TESTS
# ============================================================================

class TestQGExecutionHappyPath:
    """
    Happy path tests for qg_execution gate.

    Verifies test passed validation returns pass response.
    """

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_passed_test_returns_pass(self):
        """
        P0: Verify passed test returns pass_response.

        AAA Pattern:
        1. Arrange - Create test result with status="passed"
        2. Act - Validate
        3. Assert - Returns pass response with metadata
        """
        # Arrange
        arguments = {
            "test_result": {
                "status": "passed",
                "exit_code": 0,
                "output": "test_example.py::test_success PASSED",
                "duration": 1.23,
                "report_path": "tests/_reports/report.html"
            },
            "test_path": "tests/test_example.py"
        }

        # Act
        result = QGExecution.validate(arguments)

        # Assert
        assert result["status"] == "pass", \
            f"Passed test should return 'pass', got {result['status']}"
        assert "metadata" not in result or result.get("metadata", {}).get("test_status") == "passed", \
            "Metadata should indicate passed test"


# ============================================================================
# VALIDATION TESTS
# ============================================================================

class TestQGExecutionValidation:
    """
    Validation tests for qg_execution gate.

    Verifies parameter validation and error handling.
    """

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_missing_test_result_returns_fail(self):
        """
        P0: Verify missing test_result parameter returns fail response.

        AAA Pattern:
        1. Arrange - Create arguments without test_result
        2. Act - Validate
        3. Assert - Returns fail with error message
        """
        # Arrange
        arguments = {"test_path": "tests/test_example.py"}

        # Act
        result = QGExecution.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Missing test_result should return 'fail'"
        assert "test_result" in result["error"].lower(), \
            f"Error should mention test_result, got: {result['error']}"

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_invalid_status_returns_fail(self):
        """
        P0: Verify invalid test status returns fail response.

        AAA Pattern:
        1. Arrange - Create test result with invalid status
        2. Act - Validate
        3. Assert - Returns fail with error message
        """
        # Arrange
        arguments = {
            "test_result": {
                "status": "unknown",  # Invalid status
                "exit_code": 1
            }
        }

        # Act
        result = QGExecution.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Invalid status should return 'fail'"
        assert "Invalid test status" in result["error"], \
            f"Error should mention invalid status, got: {result['error']}"

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_failed_test_returns_fail_with_diagnostics(self):
        """
        P0: Verify failed test returns fail response with diagnostic data.

        AAA Pattern:
        1. Arrange - Create test result with status="failed"
        2. Act - Validate
        3. Assert - Returns fail with diagnostic data and triage options
        """
        # Arrange
        arguments = {
            "test_result": {
                "status": "failed",
                "exit_code": 1,
                "output": "test_example.py::test_fail FAILED\nE   assert False",
                "duration": 0.5,
                "failure_data": {
                    "failed_assertion": "False",
                    "error_location": "tests/test_example.py:10",
                    "stack_trace": "test_fail\n    assert False"
                }
            },
            "test_path": "tests/test_example.py",
            "workflow": "auth"
        }

        # Act
        result = QGExecution.validate(arguments)

        # Assert
        assert result["status"] == "fail", \
            "Failed test should return 'fail'"
        assert "fix_hint" in result, \
            "Failed test should include fix_hint with triage presentation"
        assert "HOW SHOULD WE PROCEED?" in result["fix_hint"], \
            "Fix hint should include triage options"
        assert "1. Application Defect" in result["fix_hint"], \
            "Fix hint should include option 1"
        assert "2. Test Issue" in result["fix_hint"], \
            "Fix hint should include option 2"
        assert "3. Investigate" in result["fix_hint"], \
            "Fix hint should include option 3"


# ============================================================================
# DIAGNOSTIC CAPTURE TESTS
# ============================================================================

class TestDiagnosticCapture:
    """
    Tests for diagnostic data capture.

    Verifies 7 data types captured correctly.
    """

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_captures_7_diagnostic_data_types(self):
        """
        P1: Verify all 7 diagnostic data types are captured.

        AAA Pattern:
        1. Arrange - Create test result with failure data
        2. Act - Capture diagnostic data
        3. Assert - All 7 types present
        """
        # Arrange
        test_result = {
            "status": "failed",
            "exit_code": 1,
            "output": "test failed",
            "duration": 1.0,
            "failure_data": {
                "failed_assertion": "assert False",
                "error_location": "test.py:10"
            }
        }
        arguments = {"test_path": "tests/test.py", "workflow": "auth"}

        # Act
        diagnostic_data = QGExecution._capture_diagnostic_data(test_result, arguments)

        # Assert
        assert diagnostic_data["version"] == "v1", \
            "Diagnostic data should be version v1"
        assert "data_types" in diagnostic_data, \
            "Diagnostic data should include data_types"

        # Verify all 7 types present
        data_types = diagnostic_data["data_types"]
        required_types = [
            "test_execution",
            "page_state",
            "browser_context",
            "expected_vs_actual",
            "test_context",
            "test_data",
            "execution_flow"
        ]
        for data_type in required_types:
            assert data_type in data_types, \
                f"Diagnostic data should include {data_type}"


# ============================================================================
# AI ANALYSIS TESTS
# ============================================================================

class TestAIAnalysis:
    """
    Tests for AI analysis generation.

    Verifies suggestive analysis with confidence levels.
    """

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_ai_analysis_for_assertion_failure(self):
        """
        P1: Verify AI analysis detects assertion failures.

        AAA Pattern:
        1. Arrange - Create diagnostic data with assertion failure
        2. Act - Generate AI analysis
        3. Assert - Likely cause is assertion failure, confidence > 50%
        """
        # Arrange
        diagnostic_data = {
            "version": "v1",
            "data_types": {
                "test_execution": {
                    "pytest_output": "test.py::test_fail FAILED\nE   assert False",
                    "failure_data": {"failed_assertion": "assert False"}
                }
            }
        }

        # Act
        ai_analysis = QGExecution._generate_ai_analysis(diagnostic_data)

        # Assert
        assert ai_analysis["confidence"] >= 50, \
            f"Confidence should be >= 50%, got {ai_analysis['confidence']}%"
        assert "assertion" in ai_analysis["likely_cause"].lower(), \
            f"Likely cause should mention assertion, got: {ai_analysis['likely_cause']}"

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_ai_analysis_for_timeout(self):
        """
        P1: Verify AI analysis detects timeout issues.

        AAA Pattern:
        1. Arrange - Create diagnostic data with timeout error
        2. Act - Generate AI analysis
        3. Assert - Likely cause is timeout, high confidence
        """
        # Arrange
        diagnostic_data = {
            "version": "v1",
            "data_types": {
                "test_execution": {
                    "pytest_output": "FAILED: TimeoutException: Test exceeded 30s timeout",
                    "failure_data": None
                }
            }
        }

        # Act
        ai_analysis = QGExecution._generate_ai_analysis(diagnostic_data)

        # Assert
        assert ai_analysis["confidence"] >= 80, \
            f"Timeout detection should have high confidence, got {ai_analysis['confidence']}%"
        assert "timeout" in ai_analysis["likely_cause"].lower(), \
            f"Likely cause should mention timeout, got: {ai_analysis['likely_cause']}"

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_ai_analysis_for_element_not_found(self):
        """
        P1: Verify AI analysis detects element locator issues.

        AAA Pattern:
        1. Arrange - Create diagnostic data with NoSuchElementException
        2. Act - Generate AI analysis
        3. Assert - Likely cause is locator issue, high confidence
        """
        # Arrange
        diagnostic_data = {
            "version": "v1",
            "data_types": {
                "test_execution": {
                    "pytest_output": "NoSuchElementException: Unable to locate element",
                    "failure_data": None
                }
            }
        }

        # Act
        ai_analysis = QGExecution._generate_ai_analysis(diagnostic_data)

        # Assert
        assert ai_analysis["confidence"] >= 75, \
            f"Element locator detection should have high confidence, got {ai_analysis['confidence']}%"
        assert "element" in ai_analysis["likely_cause"].lower() or "locator" in ai_analysis["likely_cause"].lower(), \
            f"Likely cause should mention element/locator, got: {ai_analysis['likely_cause']}"


# ============================================================================
# TRIAGE PRESENTATION TESTS
# ============================================================================

class TestTriagePresentation:
    """
    Tests for triage presentation formatting.

    Verifies correct format and required sections.
    """

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_triage_presentation_format(self):
        """
        P1: Verify triage presentation includes required sections.

        AAA Pattern:
        1. Arrange - Create test result, diagnostic data, AI analysis
        2. Act - Format triage presentation
        3. Assert - Contains test name, error, AI analysis, 3 options
        """
        # Arrange
        test_result = {"status": "failed", "output": "test failed", "duration": 1.0}
        diagnostic_data = {
            "version": "v1",
            "data_types": {
                "test_execution": {
                    "failure_data": {
                        "failed_assertion": "assert False",
                        "error_location": "test.py:10"
                    }
                }
            }
        }
        ai_analysis = {
            "likely_cause": "Assertion failure",
            "confidence": 70,
            "evidence": ["Assertion: assert False"],
            "suggested_fix": "Review logic"
        }

        # Act
        triage_message = QGExecution._format_triage_presentation(
            test_result=test_result,
            diagnostic_data=diagnostic_data,
            ai_analysis=ai_analysis,
            test_path="tests/test_example.py"
        )

        # Assert
        assert "TEST EXECUTION FAILED" in triage_message, \
            "Message should include failure header"
        assert "AI Analysis" in triage_message, \
            "Message should include AI analysis section"
        assert "Confidence: 70%" in triage_message, \
            "Message should include confidence level"
        assert "1. Application Defect" in triage_message, \
            "Message should include option 1"
        assert "2. Test Issue" in triage_message, \
            "Message should include option 2"
        assert "3. Investigate" in triage_message, \
            "Message should include option 3"


# ============================================================================
# RETRY POLICY TESTS
# ============================================================================

class TestRetryPolicy:
    """
    Tests for retry policy and error signature tracking.

    Verifies error signature generation and retry limits.
    """

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_retry_policy_generates_error_signature(self):
        """
        P1: Verify error signature is generated for tracking.

        AAA Pattern:
        1. Arrange - Create test result with error
        2. Act - Check retry policy
        3. Assert - Error signature generated, retry decision provided
        """
        # Arrange
        test_result = {
            "status": "failed",
            "output": "test failed with specific error",
            "failure_data": {"error_location": "test.py:10"}
        }

        # Act
        retry_decision = QGExecution._check_retry_policy(test_result, "auth")

        # Assert
        assert "error_signature" in retry_decision, \
            "Retry decision should include error signature"
        assert retry_decision["error_signature"] is not None, \
            "Error signature should not be None"
        assert len(retry_decision["error_signature"]) == 16, \
            f"Error signature should be 16 chars (MD5 truncated), got {len(retry_decision['error_signature'])}"
        assert "policy" in retry_decision, \
            "Retry decision should include policy limits"


# ============================================================================
# TRIAGE DECISION TESTS
# ============================================================================

class TestTriageDecisions:
    """
    Tests for handling triage decisions.

    Verifies correct action for each decision type.
    """

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_application_defect_decision(self):
        """
        P0: Verify application defect decision triggers defect logging.

        AAA Pattern:
        1. Arrange - User selects option 1 (defect)
        2. Act - Handle decision
        3. Assert - Returns log_defect action, blocking=True
        """
        # Arrange
        diagnostic_data = {"version": "v1", "data_types": {}}

        # Act
        result = QGExecution.handle_triage_decision("1", diagnostic_data)

        # Assert
        assert result["action"] == "log_defect", \
            f"Option 1 should trigger log_defect, got {result['action']}"
        assert result["blocking"] is True, \
            "Defect logging should be blocking"

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_test_issue_decision(self):
        """
        P0: Verify test issue decision triggers fix workflow.

        AAA Pattern:
        1. Arrange - User selects option 2 (test issue)
        2. Act - Handle decision
        3. Assert - Returns fix_test action, blocking=False
        """
        # Arrange
        diagnostic_data = {"version": "v1", "data_types": {}}

        # Act
        result = QGExecution.handle_triage_decision("2", diagnostic_data)

        # Assert
        assert result["action"] == "fix_test", \
            f"Option 2 should trigger fix_test, got {result['action']}"
        assert result["blocking"] is False, \
            "Test fix should not be blocking"

    @pytest.mark.unit
    @pytest.mark.qg_execution
    def test_investigate_decision(self):
        """
        P0: Verify investigate decision shows full diagnostic data.

        AAA Pattern:
        1. Arrange - User selects option 3 (investigate)
        2. Act - Handle decision
        3. Assert - Returns investigate action with full data
        """
        # Arrange
        diagnostic_data = {"version": "v1", "data_types": {"test_execution": {}}}

        # Act
        result = QGExecution.handle_triage_decision("3", diagnostic_data)

        # Assert
        assert result["action"] == "investigate", \
            f"Option 3 should trigger investigate, got {result['action']}"
        assert "Full Diagnostic Data" in result["instructions"], \
            "Instructions should mention full diagnostic data"
