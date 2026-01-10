"""
Test FR-14.1: Parameter Contradiction Detection (Semantic Validation)

Tests qg_test_runner's ability to detect parameter contradictions in test code.
Example: from_account="12345", to_account="12345" (same account transfer)

Agent: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)
Date: 2026-01-10
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add mcp_server to path for relative imports
mcp_server_path = Path(__file__).parent.parent
sys.path.insert(0, str(mcp_server_path))

from tools.gates.qg_test_runner import QGTestRunner
from utils.state_manager import StateManager


def test_parameter_contradiction_detection():
    """
    Test that qg_test_runner detects parameter contradictions.

    Scenario: Test code transfers money from account "12345" to account "12345"
    Expected: Gate catches this semantic error and provides fix guidance
    """

    print("\n" + "="*80)
    print("TEST: FR-14.1 Parameter Contradiction Detection")
    print("="*80)

    # Step 1: Generate test code with parameter contradiction
    test_code_with_contradiction = '''
import pytest
from framework.roles.parabank.registered_user import RegisteredUser
from framework.pages.parabank.account_overview_page import AccountOverviewPage
from framework.resources.utilities import autologger

@pytest.mark.parabank
@autologger.automation_logger("Test")
def test_transfer_between_accounts(web_interface, config, test_users):
    """
    Test that a registered user can transfer money between accounts.

    SEMANTIC ERROR: from_account and to_account are the same!
    """
    # Arrange
    user = RegisteredUser(web_interface, test_users["registered_user"], config["url"])
    overview_page = AccountOverviewPage(web_interface)

    # Act - Transfer from account 12345 to account 12345 (CONTRADICTION!)
    user.transfer_funds(
        from_account="12345",
        to_account="12345",  # Same as from_account - semantic error!
        amount="100.00"
    )

    # Assert
    assert overview_page.is_transfer_complete(), "Transfer should complete"
'''

    # Step 2: Create input data for gate (matches parabank5 pattern)
    input_data = {
        "mode": "POST",
        "test_name": "test_transfer_between_accounts",
        "workflow": "parabank",
        "role": "RegisteredUser",
        "code": test_code_with_contradiction,
        "pom_metadata": {
            "class_name": "AccountOverviewPage",
            "import_path": "framework.pages.parabank.account_overview_page",
            "state_methods": ["is_transfer_complete"]
        },
        "role_metadata": {
            "class_name": "RegisteredUser",
            "import_path": "framework.roles.parabank.registered_user",
            "workflow_methods": ["transfer_funds"]
        },
        "metadata": {
            "class_name": "test_transfer_between_accounts",
            "file_path": "tests/parabank/test_transfer.py"
        }
    }

    print("\n1. Test Code Generated (with parameter contradiction)")
    print("-" * 80)
    print(test_code_with_contradiction)

    # Step 3: Call qg_test_runner POST validation with mocked state
    print("\n2. Calling QGTestRunner.validate_post()...")
    print("-" * 80)

    # Mock state manager (no Step 1 config needed for FR-14.1)
    state_manager = MagicMock(spec=StateManager)
    state_manager.get_step.return_value = None

    with patch.object(QGTestRunner, '_get_state_manager', return_value=state_manager):
        result = QGTestRunner.validate_post(input_data)

    # Step 4: Verify gate response
    print("\n3. Gate Response:")
    print("-" * 80)
    print(f"Status: {result.get('status')}")
    print(f"\nError: {result.get('error', 'N/A')}")
    print(f"\nMessage: {result.get('message', 'N/A')}")
    if 'fix_applied' in result:
        print(f"\nFix Applied: {result.get('fix_applied')}")

    # Step 5: Validate results
    print("\n4. Validation:")
    print("-" * 80)

    validation_results = {
        "status_is_needs_retry": result.get('status') == 'NEEDS_RETRY',
        "error_mentions_from_account": 'from_account' in str(result.get('error', '')).lower(),
        "error_mentions_to_account": 'to_account' in str(result.get('error', '')).lower(),
        "error_mentions_value": '12345' in str(result.get('error', '')),
        "has_guidance": bool(result.get('message') or result.get('fix_applied'))
    }

    print(f"[OK] Status is NEEDS_RETRY: {validation_results['status_is_needs_retry']}")
    print(f"[OK] Error mentions 'from_account': {validation_results['error_mentions_from_account']}")
    print(f"[OK] Error mentions 'to_account': {validation_results['error_mentions_to_account']}")
    print(f"[OK] Error mentions value '12345': {validation_results['error_mentions_value']}")
    print(f"[OK] Has fix guidance: {validation_results['has_guidance']}")

    # Step 6: Determine test result
    all_validations_pass = all(validation_results.values())

    print("\n5. Test Result:")
    print("-" * 80)
    if all_validations_pass:
        print("[PASS] TEST PASSED")
        print("\nThe gate successfully detected the parameter contradiction!")
        print("- Caught same account transfer (from_account == to_account)")
        print("- Returned NEEDS_RETRY status")
        print("- Provided clear error message with parameter names and values")
        print("- Included fix guidance")
    else:
        print("[FAIL] TEST FAILED")
        print("\nValidation failures:")
        for check, passed in validation_results.items():
            if not passed:
                print(f"  - {check}: FAILED")

    print("\n" + "="*80)

    return {
        "test_name": "FR-14.1 Parameter Contradiction Detection",
        "status": "PASS" if all_validations_pass else "FAIL",
        "gate_response": result,
        "validation_results": validation_results,
        "all_validations_pass": all_validations_pass
    }


def test_valid_code_passes():
    """
    Negative test: Valid test code should pass validation.
    """

    print("\n" + "="*80)
    print("NEGATIVE TEST: Valid Code Should Pass")
    print("="*80)

    valid_test_code = '''
import pytest
from framework.roles.parabank.registered_user import RegisteredUser
from framework.pages.parabank.account_overview_page import AccountOverviewPage
from framework.resources.utilities import autologger

@pytest.mark.parabank
@autologger.automation_logger("Test")
def test_transfer_between_accounts(web_interface, config, test_users):
    """Test that a registered user can transfer money between accounts."""
    # Arrange
    user = RegisteredUser(web_interface, test_users["registered_user"], config["url"])
    overview_page = AccountOverviewPage(web_interface)

    # Act - Transfer from account 12345 to account 67890 (DIFFERENT accounts - valid!)
    user.transfer_funds(
        from_account="12345",
        to_account="67890",  # Different account - no contradiction
        amount="100.00"
    )

    # Assert
    assert overview_page.is_transfer_complete(), "Transfer should complete"
'''

    input_data = {
        "mode": "POST",
        "test_name": "test_transfer_between_accounts",
        "workflow": "parabank",
        "role": "RegisteredUser",
        "code": valid_test_code,
        "pom_metadata": {
            "class_name": "AccountOverviewPage",
            "import_path": "framework.pages.parabank.account_overview_page",
            "state_methods": ["is_transfer_complete"]
        },
        "role_metadata": {
            "class_name": "RegisteredUser",
            "import_path": "framework.roles.parabank.registered_user",
            "workflow_methods": ["transfer_funds"]
        },
        "metadata": {
            "class_name": "test_transfer_between_accounts",
            "file_path": "tests/parabank/test_transfer.py"
        }
    }

    print("\n1. Valid Test Code (no contradiction)")
    print("-" * 80)
    print(valid_test_code)

    print("\n2. Calling QGTestRunner.validate_post()...")
    print("-" * 80)

    # Mock state manager
    state_manager = MagicMock(spec=StateManager)
    state_manager.get_step.return_value = None

    with patch.object(QGTestRunner, '_get_state_manager', return_value=state_manager):
        result = QGTestRunner.validate_post(input_data)

    print("\n3. Gate Response:")
    print("-" * 80)
    print(f"Status: {result.get('status')}")
    if result.get('status') != 'PASS':
        print(f"Error: {result.get('error', 'N/A')}")

    print("\n4. Validation:")
    print("-" * 80)
    is_pass = result.get('status') in ['PASS', 'pass']  # Handle both cases
    print(f"[OK] Status is PASS: {is_pass}")

    if is_pass:
        print("\n[PASS] NEGATIVE TEST PASSED")
        print("Valid code correctly passed validation (no false positives)")
    else:
        print("\n[FAIL] NEGATIVE TEST FAILED")
        print("Valid code was incorrectly flagged as invalid (false positive)")

    print("\n" + "="*80)

    return {
        "test_name": "Valid Code Should Pass",
        "status": "PASS" if is_pass else "FAIL",
        "gate_response": result
    }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("FR-14.1 SEMANTIC VALIDATION TEST SUITE")
    print("Testing: Parameter Contradiction Detection")
    print("Agent: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)")
    print("="*80)

    # Run main test
    main_result = test_parameter_contradiction_detection()

    # Run negative test
    negative_result = test_valid_code_passes()

    # Summary
    print("\n" + "="*80)
    print("TEST SUITE SUMMARY")
    print("="*80)
    print(f"Main Test (Contradiction Detection): {main_result['status']}")
    print(f"Negative Test (Valid Code): {negative_result['status']}")

    overall_pass = (main_result['status'] == 'PASS' and negative_result['status'] == 'PASS')
    print(f"\nOverall Result: {'[PASS] ALL TESTS PASSED' if overall_pass else '[FAIL] SOME TESTS FAILED'}")
    print("="*80)
