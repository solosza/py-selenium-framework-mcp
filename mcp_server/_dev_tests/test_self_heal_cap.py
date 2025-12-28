"""
Tests for Self-Heal Cap Enforcement (Task 2.0)

Test Pyramid:
1. ATTEMPT TRACKING    - StateManager increment/get/reset
2. MAX ATTEMPTS        - BaseGate constant and blocked response
3. GATE INTEGRATION    - POST gates check attempts before validation
4. AUDIT INTEGRATION   - Attempts logged to audit trail
5. RESET ON SUCCESS    - Attempts reset when gate passes
6. EDGE CASES          - Boundary conditions, concurrent steps
"""

import tempfile
import os
from pathlib import Path

import pytest

from utils.state_manager import StateManager
from tools.gates.base_gate import BaseGate
from utils.audit_logger import AuditLogger


class TestAttemptTracking:
    """1. ATTEMPT TRACKING - StateManager increment/get/reset."""

    def test_get_attempt_count_returns_zero_for_new_step(self):
        """New steps should have zero attempts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            count = manager.get_attempt_count(6)

            assert count == 0

    def test_increment_attempt_returns_new_count(self):
        """increment_attempt() should return the new count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            count = manager.increment_attempt(6)

            assert count == 1

    def test_increment_attempt_accumulates(self):
        """Multiple increments should accumulate."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            manager.increment_attempt(6)
            manager.increment_attempt(6)
            count = manager.increment_attempt(6)

            assert count == 3

    def test_get_attempt_count_after_increment(self):
        """get_attempt_count() should return current count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            manager.increment_attempt(6)
            manager.increment_attempt(6)

            assert manager.get_attempt_count(6) == 2

    def test_reset_attempts_clears_count(self):
        """reset_attempts() should set count to zero."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            manager.increment_attempt(6)
            manager.increment_attempt(6)
            manager.reset_attempts(6)

            assert manager.get_attempt_count(6) == 0

    def test_attempts_are_per_step(self):
        """Attempts should be tracked per-step independently."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            manager.increment_attempt(6)
            manager.increment_attempt(6)
            manager.increment_attempt(7)

            assert manager.get_attempt_count(6) == 2
            assert manager.get_attempt_count(7) == 1
            assert manager.get_attempt_count(8) == 0

    def test_attempts_persist_across_manager_instances(self):
        """Attempts should persist to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")

            # First instance: increment
            manager1 = StateManager(state_file)
            manager1.increment_attempt(6)
            manager1.increment_attempt(6)

            # Second instance: should see same count
            manager2 = StateManager(state_file)
            assert manager2.get_attempt_count(6) == 2


class TestMaxAttempts:
    """2. MAX ATTEMPTS - BaseGate constant and blocked response."""

    def test_max_attempts_is_three(self):
        """MAX_ATTEMPTS should be 3."""
        assert BaseGate.MAX_ATTEMPTS == 3

    def test_blocked_response_returns_blocked_status(self):
        """blocked_response() should return status=blocked."""
        response = BaseGate.blocked_response(
            step=6,
            attempts=3,
            errors=["skeleton detected", "missing method", "invalid import"]
        )

        assert response["status"] == "blocked"

    def test_blocked_response_includes_step(self):
        """blocked_response() should include step number."""
        response = BaseGate.blocked_response(
            step=6,
            attempts=3,
            errors=["error1"]
        )

        assert response["step"] == 6

    def test_blocked_response_includes_attempt_count(self):
        """blocked_response() should include attempt count."""
        response = BaseGate.blocked_response(
            step=6,
            attempts=3,
            errors=["error1"]
        )

        assert response["attempts"] == 3

    def test_blocked_response_includes_error_history(self):
        """blocked_response() should include all previous errors."""
        errors = ["skeleton detected", "missing method", "invalid import"]
        response = BaseGate.blocked_response(
            step=6,
            attempts=3,
            errors=errors
        )

        assert response["errors"] == errors

    def test_blocked_response_includes_fix_hint(self):
        """blocked_response() should include user action hint."""
        response = BaseGate.blocked_response(
            step=6,
            attempts=3,
            errors=["error1"]
        )

        assert "fix_hint" in response
        assert "manual" in response["fix_hint"].lower() or "user" in response["fix_hint"].lower()


class TestGateIntegration:
    """3. GATE INTEGRATION - POST gates check attempts before validation."""

    def test_qg_page_object_blocks_after_max_attempts(self):
        """qg_page_object POST should return blocked after 3 failures."""
        from tools.gates.qg_page_object import QGPageObject

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            # Simulate 3 previous failures
            manager.increment_attempt(6)
            manager.increment_attempt(6)
            manager.increment_attempt(6)

            # Set manager for gate
            QGPageObject.set_state_manager(manager)

            try:
                # Any validation should return blocked
                result = QGPageObject.validate_post({
                    "code": "class LoginPage: pass",
                    "metadata": {"class_name": "LoginPage"}
                })

                assert result["status"] == "blocked"
            finally:
                QGPageObject.set_state_manager(None)

    def test_qg_task_blocks_after_max_attempts(self):
        """qg_task POST should return blocked after 3 failures."""
        from tools.gates.qg_task import QGTask

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            # Simulate 3 previous failures
            manager.increment_attempt(7)
            manager.increment_attempt(7)
            manager.increment_attempt(7)

            QGTask.set_state_manager(manager)

            try:
                result = QGTask.validate_post({
                    "code": "class AuthTasks: pass",
                    "metadata": {"class_name": "AuthTasks"}
                })

                assert result["status"] == "blocked"
            finally:
                QGTask.set_state_manager(None)

    def test_qg_role_blocks_after_max_attempts(self):
        """qg_role POST should return blocked after 3 failures."""
        from tools.gates.qg_role import QGRole

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            # Simulate 3 previous failures
            manager.increment_attempt(8)
            manager.increment_attempt(8)
            manager.increment_attempt(8)

            QGRole.set_state_manager(manager)

            try:
                result = QGRole.validate_post({
                    "code": "class GuestUser: pass",
                    "metadata": {"class_name": "GuestUser"}
                })

                assert result["status"] == "blocked"
            finally:
                QGRole.set_state_manager(None)

    def test_qg_test_runner_blocks_after_max_attempts(self):
        """qg_test_runner POST should return blocked after 3 failures."""
        from tools.gates.qg_test_runner import QGTestRunner

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            # Simulate 3 previous failures
            manager.increment_attempt(9)
            manager.increment_attempt(9)
            manager.increment_attempt(9)

            QGTestRunner.set_state_manager(manager)

            try:
                result = QGTestRunner.validate_post({
                    "code": "def test_login(): pass",
                    "metadata": {"test_name": "test_login"}
                })

                assert result["status"] == "blocked"
            finally:
                QGTestRunner.set_state_manager(None)


class TestAuditIntegration:
    """4. AUDIT INTEGRATION - Attempts logged to audit trail."""

    def test_blocked_response_logs_to_audit(self):
        """blocked_response() should log to audit if logger set."""
        logger = AuditLogger(run_id="test-run")
        BaseGate.set_audit_logger(logger)

        try:
            BaseGate.blocked_response(
                step=6,
                attempts=3,
                errors=["error1", "error2", "error3"]
            )

            # Check audit log contains blocked entry
            assert len(logger.steps) == 1
            entry = logger.steps[0]
            assert entry["step"] == 6
            assert entry["result"] == "blocked"
        finally:
            BaseGate.set_audit_logger(None)

    def test_gate_failure_increments_and_logs_attempt(self):
        """Gate failure should increment attempt and log to audit."""
        from tools.gates.qg_page_object import QGPageObject

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)
            logger = AuditLogger(run_id="test-run")

            QGPageObject.set_state_manager(manager)
            BaseGate.set_audit_logger(logger)

            try:
                # Submit code that will fail (skeleton with pass)
                QGPageObject.validate_post({
                    "code": "class LoginPage:\n    pass",
                    "metadata": {"class_name": "LoginPage"}
                })

                # Attempt should be incremented
                assert manager.get_attempt_count(6) == 1

                # Audit should contain failure
                assert any(e["result"] == "fail" for e in logger.steps)
            finally:
                QGPageObject.set_state_manager(None)
                BaseGate.set_audit_logger(None)


class TestResetOnSuccess:
    """5. RESET ON SUCCESS - Attempts reset when gate passes."""

    def test_gate_pass_resets_attempts(self):
        """Successful gate pass should reset attempt count."""
        from tools.gates.qg_page_object import QGPageObject

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            # Simulate previous failures
            manager.increment_attempt(6)
            manager.increment_attempt(6)

            QGPageObject.set_state_manager(manager)

            try:
                # Submit valid code that passes all validations
                valid_code = '''
class LoginPage:
    EMAIL = ("css", "#email")

    def __init__(self, web):
        self.web = web

    def enter_email(self, text):
        self.web.type_text(*self.EMAIL, text)
        return self

    def is_logged_in(self):
        return self.web.is_element_displayed(*self.EMAIL)
'''
                QGPageObject.validate_post({
                    "code": valid_code,
                    "metadata": {
                        "class_name": "LoginPage",
                        "import_path": "framework.pages.auth.login_page",
                        "locators": ["EMAIL"],
                        "action_methods": [{"name": "enter_email"}],
                        "state_methods": [{"name": "is_logged_in"}]
                    }
                })

                # Attempts should be reset
                assert manager.get_attempt_count(6) == 0
            finally:
                QGPageObject.set_state_manager(None)


class TestEdgeCases:
    """6. EDGE CASES - Boundary conditions, concurrent steps."""

    def test_attempt_at_boundary_two(self):
        """At 2 attempts, should still allow validation."""
        from tools.gates.qg_page_object import QGPageObject

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            manager.increment_attempt(6)
            manager.increment_attempt(6)

            QGPageObject.set_state_manager(manager)

            try:
                # Should NOT be blocked (at 2, not 3)
                result = QGPageObject.validate_post({
                    "code": "class LoginPage:\n    pass",
                    "metadata": {"class_name": "LoginPage"}
                })

                # Should fail validation, not be blocked
                assert result["status"] == "fail"
            finally:
                QGPageObject.set_state_manager(None)

    def test_different_steps_tracked_independently(self):
        """Attempts for different steps should not interfere."""
        from tools.gates.qg_page_object import QGPageObject
        from tools.gates.qg_task import QGTask

        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            # Max out step 6
            manager.increment_attempt(6)
            manager.increment_attempt(6)
            manager.increment_attempt(6)

            # Step 7 should be unaffected
            QGPageObject.set_state_manager(manager)
            QGTask.set_state_manager(manager)

            try:
                # Step 6 blocked
                result6 = QGPageObject.validate_post({
                    "code": "class LoginPage: pass",
                    "metadata": {"class_name": "LoginPage"}
                })
                assert result6["status"] == "blocked"

                # Step 7 should still validate (and fail, but not blocked)
                result7 = QGTask.validate_post({
                    "code": "class AuthTasks:\n    pass",
                    "metadata": {"class_name": "AuthTasks"}
                })
                assert result7["status"] == "fail"  # Not blocked
            finally:
                QGPageObject.set_state_manager(None)
                QGTask.set_state_manager(None)

    def test_reset_nonexistent_step_is_safe(self):
        """reset_attempts() on step with no attempts should not error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            state_file = os.path.join(tmpdir, "state.json")
            manager = StateManager(state_file)

            # Should not raise
            manager.reset_attempts(6)

            assert manager.get_attempt_count(6) == 0

    def test_blocked_with_no_errors_list(self):
        """blocked_response() should handle empty errors list."""
        response = BaseGate.blocked_response(
            step=6,
            attempts=3,
            errors=[]
        )

        assert response["status"] == "blocked"
        assert response["errors"] == []
