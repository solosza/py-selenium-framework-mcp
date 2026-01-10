"""
Test FR-14.2 Option 2: Credential Strategy Validation in qg_role POST gate.

Test Plan:
1. Set Step 1 config: credential_strategy="static"
2. Generate Role code with WRONG pattern (self-contained with hardcoded credentials)
3. Call qg_role POST validation
4. Verify gate catches violation
5. Verify NEEDS_RETRY response includes pattern_template for static strategy

Success Criteria:
- Gate returns status="NEEDS_RETRY"
- Error mentions "credential" or "strategy"
- Response includes "pattern_template" with user_data example
"""

import pytest
import os
import sys

# Add mcp_server to path
mcp_server_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, mcp_server_path)

from tools.gates.qg_role import QGRole
from utils.state_manager import StateManager
from utils.audit_logger import AuditLogger


class TestFR14_2_Option2_CredentialValidation:
    """Test FR-14.2: Credential strategy enforcement in qg_role POST validation."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup test environment with isolated state."""
        # Create unique run_id for this test
        self.run_id = "test_fr14_2_option2"

        # Initialize state manager and audit logger
        self.state_manager = StateManager(run_id=self.run_id)
        self.audit_logger = AuditLogger(run_id=self.run_id)

        # Inject into gate (Task 17.0 pattern)
        QGRole._state_manager = self.state_manager
        QGRole._audit_logger = self.audit_logger

        yield

        # Cleanup
        QGRole._state_manager = None
        QGRole._audit_logger = None

        # Clean up state files
        try:
            state_file = self.state_manager._get_state_file_path()
            if os.path.exists(state_file):
                os.remove(state_file)
        except Exception:
            pass

    def test_static_strategy_catches_self_contained_pattern(self):
        """
        Test that qg_role POST catches violation when:
        - Step 1 specifies credential_strategy="static"
        - Role code uses self-contained pattern (uuid generation)

        Expected: NEEDS_RETRY with pattern_template
        """
        # ARRANGE: Set Step 1 config with static strategy
        self.state_manager.save(step=1, data={
            "credential_strategy": "static",
            "test_data_location": "shared"
        })

        # Mark Step 7 complete (prerequisite for Step 8)
        self.state_manager.save(step=7, data={
            "task_code": "dummy_task_code",
            "task_metadata": {
                "class_name": "AuthTasks",
                "import_path": "tasks.auth_tasks",
                "task_methods": ["log_in"]
            }
        })

        # Create WRONG Role code (self-contained pattern when static expected)
        wrong_role_code = '''
import uuid
from interfaces.web_interface import WebInterface
from tasks.auth_tasks import AuthTasks
from resources.utilities import autologger

class RegisteredUser:
    """RegisteredUser role with WRONG credential pattern."""

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, base_url: str):
        self.web = web_interface
        # WRONG: Generates credentials (self-contained) but Step 1 said static
        self.email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "TestPass123!"
        self.auth_tasks = AuthTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login_workflow(self):
        """Complete login workflow."""
        self.auth_tasks.log_in(self.email, self.password)
'''

        # Create metadata for Role
        role_metadata = {
            "class_name": "RegisteredUser",
            "import_path": "roles.registered_user",
            "workflow_methods": ["login_workflow"]
        }

        # Create task_metadata (required by qg_role POST)
        task_metadata = {
            "class_name": "AuthTasks",
            "import_path": "tasks.auth_tasks",
            "task_methods": ["log_in"]
        }

        # ACT: Call qg_role POST validation
        result = QGRole.validate_post({
            "code": wrong_role_code,
            "metadata": role_metadata,
            "task_metadata": task_metadata,
            "source": "test_fr14_2_option2"
        })

        # ASSERT: Validation should catch credential strategy mismatch
        print("\n" + "="*80)
        print("TEST: FR-14.2 Option 2 - Credential Strategy Validation")
        print("="*80)
        print(f"\nGate Response Status: {result.get('status')}")
        print(f"Gate Response Error: {result.get('error', 'N/A')}")
        print(f"Gate Response Message: {result.get('message', 'N/A')}")
        print(f"Has Pattern Template: {'pattern_template' in result}")

        if 'pattern_template' in result:
            print(f"\nPattern Template Preview (first 200 chars):")
            print(result['pattern_template'][:200] + "...")

        print("\n" + "="*80)

        # Validate response structure
        assert result is not None, "Gate should return a response"
        assert result.get("status") == "NEEDS_RETRY", \
            f"Expected NEEDS_RETRY, got {result.get('status')}"

        # Validate error message mentions credential/strategy
        error_msg = result.get("error", "").lower()
        assert "credential" in error_msg or "strategy" in error_msg, \
            f"Error should mention 'credential' or 'strategy': {result.get('error')}"

        # Validate pattern_template is present
        assert "pattern_template" in result, \
            "Response should include 'pattern_template' for AI to fix code"

        # Validate pattern_template contains static strategy example
        pattern_template = result.get("pattern_template", "")
        assert "user_data" in pattern_template, \
            "Pattern template should show user_data parameter (static strategy)"
        assert "user_data.get" in pattern_template, \
            "Pattern template should show user_data.get() usage"

        # Validate failed_rule is present
        assert result.get("failed_rule") == "credential_strategy", \
            "Response should identify which rule failed"

        print("\nVALIDATION SUMMARY:")
        print(f"  Status: NEEDS_RETRY [PASS]")
        print(f"  Error mentions credential/strategy: [PASS]")
        print(f"  Pattern template present: [PASS]")
        print(f"  Pattern shows user_data example: [PASS]")
        print(f"  Failed rule identified: [PASS]")
        print("="*80)

    def test_static_strategy_passes_correct_pattern(self):
        """
        Test that qg_role POST passes when:
        - Step 1 specifies credential_strategy="static"
        - Role code uses correct static pattern (user_data parameter)

        Expected: Pass validation
        """
        # ARRANGE: Set Step 1 config with static strategy
        self.state_manager.save(step=1, data={
            "credential_strategy": "static",
            "test_data_location": "shared"
        })

        # Mark Step 7 complete
        self.state_manager.save(step=7, data={
            "task_code": "dummy_task_code",
            "task_metadata": {
                "class_name": "AuthTasks",
                "import_path": "tasks.auth_tasks",
                "task_methods": ["log_in"]
            }
        })

        # Create CORRECT Role code (static pattern)
        correct_role_code = '''
from typing import Dict, Any
from interfaces.web_interface import WebInterface
from tasks.auth_tasks import AuthTasks
from resources.utilities import autologger

class RegisteredUser:
    """RegisteredUser role with CORRECT static credential pattern."""

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        self.web = web_interface
        # CORRECT: Reads from user_data (static strategy)
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.auth_tasks = AuthTasks(web_interface, base_url)

    @autologger.automation_logger("Role")
    def login_workflow(self):
        """Complete login workflow."""
        self.auth_tasks.log_in(self.email, self.password)
'''

        # Create metadata
        role_metadata = {
            "class_name": "RegisteredUser",
            "import_path": "roles.registered_user",
            "workflow_methods": ["login_workflow"]
        }

        task_metadata = {
            "class_name": "AuthTasks",
            "import_path": "tasks.auth_tasks",
            "task_methods": ["log_in"]
        }

        # ACT: Call qg_role POST validation
        result = QGRole.validate_post({
            "code": correct_role_code,
            "metadata": role_metadata,
            "task_metadata": task_metadata,
            "source": "test_fr14_2_option2_positive"
        })

        # ASSERT: Should pass validation
        print("\n" + "="*80)
        print("POSITIVE TEST: Correct static pattern should pass")
        print("="*80)
        print(f"Gate Response Status: {result.get('status')}")
        print("="*80)

        assert result.get("status") == "pass", \
            f"Expected pass, got {result.get('status')}: {result.get('error')}"

        # Verify Step 8 state saved
        step_8_data = self.state_manager.get_step(8)
        assert step_8_data is not None, "Step 8 state should be saved on pass"
        assert "role_code" in step_8_data, "Step 8 should save role_code"
        assert "role_metadata" in step_8_data, "Step 8 should save role_metadata"


def print_test_report():
    """Print test execution report."""
    print("\n" + "="*80)
    print("FR-14.2 OPTION 2 TEST REPORT")
    print("="*80)
    print("\nTest: Credential Strategy Validation in qg_role POST gate")
    print("\nValidation Rules Tested:")
    print("  1. Gate catches credential_strategy mismatch (static vs self-contained)")
    print("  2. Gate returns NEEDS_RETRY status")
    print("  3. Gate provides pattern_template with correct example")
    print("  4. Gate identifies failed_rule as 'credential_strategy'")
    print("  5. Gate passes correct static pattern")
    print("\nExpected Behavior:")
    print("  - When Step 1 says 'static' but Role uses 'self-contained':")
    print("    -> Gate should block with NEEDS_RETRY")
    print("    -> Error should mention credential/strategy mismatch")
    print("    -> Response should include pattern_template with user_data example")
    print("  - When Step 1 says 'static' and Role uses 'static':")
    print("    -> Gate should pass")
    print("="*80 + "\n")


if __name__ == "__main__":
    print_test_report()
    pytest.main([__file__, "-v", "-s"])
