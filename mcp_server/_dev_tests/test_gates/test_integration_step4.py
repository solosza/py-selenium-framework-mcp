"""
Mini integration test for gate enforcer step_4 consolidation (Option 3)

Simulates real workflow:
1. Create state with step_4.test_metadata
2. Try to Write a test file using Claude Code's Write tool
3. Verify gate enforcer allows the write
"""

import json
from pathlib import Path
from mcp_server.utils.state_manager import StateManager


def test_mini_integration_step4():
    """
    Mini integration test: Simulate construction gates, then write files.

    Workflow:
    1. User Input (step_1)
    2. Construction: POM, Task, Role, Test (all save to step_4)
    3. Try to write test file (should be allowed after step_4.test_metadata exists)
    """
    # Setup
    run_id = "2026-01-22T10-00-00.000000Z"
    state_manager = StateManager(run_id=run_id)

    base_dir = Path(__file__).parent.parent.parent.parent
    state_dir = base_dir / "tests" / "_state" / run_id.replace(":", "-")
    state_dir.mkdir(parents=True, exist_ok=True)

    try:
        print("=" * 70)
        print("MINI INTEGRATION TEST: Step 4 Consolidation")
        print("=" * 70)

        # Step 1: User Input
        print("\n[Step 1] User Input")
        state_manager.save(step=1, data={
            "persona": "customer",
            "URL": "https://example.com",
            "role_name": "Customer",
            "workflow": "helios5"
        })
        print("[OK] Step 1 saved")

        # Step 4: Construction gates (simulate sequential saves)
        print("\n[Step 4] Construction Phase")

        print("  [4.1] POM generation (qg_page_object)")
        state_manager.save(step=4, data={
            "pom_metadata": {
                "class_name": "SearchPage",
                "import_path": "framework.pages.helios5.search_page"
            }
        })
        print("  [OK] pom_metadata saved")

        print("  [4.2] Task generation (qg_task)")
        state_manager.save(step=4, data={
            "task_metadata": {
                "class_name": "SearchTasks",
                "import_path": "framework.tasks.helios5.search_tasks"
            }
        })
        print("  [OK] task_metadata saved")

        print("  [4.3] Role generation (qg_role)")
        state_manager.save(step=4, data={
            "role_metadata": {
                "class_name": "Customer",
                "import_path": "framework.roles.helios5.customer"
            }
        })
        print("  [OK] role_metadata saved")

        print("  [4.4] Test generation (qg_test_runner)")
        state_manager.save(step=4, data={
            "test_metadata": {
                "file_path": "tests/helios5/test_search_sales_rep.py",
                "test_name": "test_search_sales_rep"
            }
        })
        print("  [OK] test_metadata saved")

        # Verify state accumulation
        print("\n[Verification] State Accumulation")
        state = state_manager.load()
        step_4_data = state.get("step_4", {})

        required_keys = ["pom_metadata", "task_metadata", "role_metadata", "test_metadata"]
        all_present = all(key in step_4_data for key in required_keys)

        if all_present:
            print("  [OK] All 4 metadata keys present in step_4")
            for key in required_keys:
                print(f"    - {key}: {step_4_data[key].get('class_name') or step_4_data[key].get('file_path')}")
        else:
            missing = [key for key in required_keys if key not in step_4_data]
            print(f"  [FAIL] Missing keys: {missing}")
            return False

        # Test gate enforcer logic
        print("\n[Gate Enforcer] Simulated Write Operations")

        from mcp_server._dev_tests.test_gates.test_gate_enforcer_step4_helper import check_gate_enforcer

        # Test 1: Write to tests/ (should be allowed with test_metadata)
        result_test = check_gate_enforcer(
            file_path="tests/helios5/test_search_sales_rep.py",
            state_dir=state_dir
        )

        if not result_test["blocked"]:
            print("  [OK] tests/ write ALLOWED (test_metadata present)")
        else:
            print(f"  [FAIL] tests/ write BLOCKED: {result_test['error']}")
            return False

        # Test 2: Write to framework/pages/ (should be allowed with pom_metadata)
        result_page = check_gate_enforcer(
            file_path="framework/pages/helios5/search_page.py",
            state_dir=state_dir
        )

        if not result_page["blocked"]:
            print("  [OK] framework/pages/ write ALLOWED (pom_metadata present)")
        else:
            print(f"  [FAIL] framework/pages/ write BLOCKED: {result_page['error']}")
            return False

        # Test 3: Write to framework/tasks/ (should be allowed with task_metadata)
        result_task = check_gate_enforcer(
            file_path="framework/tasks/helios5/search_tasks.py",
            state_dir=state_dir
        )

        if not result_task["blocked"]:
            print("  [OK] framework/tasks/ write ALLOWED (task_metadata present)")
        else:
            print(f"  [FAIL] framework/tasks/ write BLOCKED: {result_task['error']}")
            return False

        # Test 4: Write to framework/roles/ (should be allowed with role_metadata)
        result_role = check_gate_enforcer(
            file_path="framework/roles/helios5/customer.py",
            state_dir=state_dir
        )

        if not result_role["blocked"]:
            print("  [OK] framework/roles/ write ALLOWED (role_metadata present)")
        else:
            print(f"  [FAIL] framework/roles/ write BLOCKED: {result_role['error']}")
            return False

        print("\n" + "=" * 70)
        print("[PASS] MINI INTEGRATION TEST PASSED")
        print("=" * 70)
        print("\nSummary:")
        print("  • StateManager merges metadata into step_4 [OK]")
        print("  • Gate enforcer checks correct metadata sub-keys [OK]")
        print("  • All construction files can be written after step_4 [OK]")

        return True

    finally:
        # Cleanup
        state_file = state_dir / "workflow_state.json"
        if state_file.exists():
            state_file.unlink()


if __name__ == "__main__":
    success = test_mini_integration_step4()
    exit(0 if success else 1)
