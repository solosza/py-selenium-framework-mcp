"""
Unit tests for gate enforcer step_4 consolidation (Task 1.1.4.3)

Tests verify:
1. Gate enforcer blocks writes without step_4 metadata
2. Gate enforcer allows writes with correct step_4.metadata_key
3. StateManager merges multiple metadata sub-keys into step_4
"""

import json
import pytest
from pathlib import Path
from mcp_server.utils.state_manager import StateManager


class TestGateEnforcerStep4:
    """Test gate enforcer with step_4 consolidation"""

    @pytest.fixture
    def run_id(self):
        """Use a test-specific run_id"""
        return "2026-01-22T09-00-00.000000Z"

    @pytest.fixture
    def state_dir(self, run_id):
        """Create test state directory"""
        base_dir = Path(__file__).parent.parent.parent.parent
        state_dir = base_dir / "tests" / "_state" / run_id
        state_dir.mkdir(parents=True, exist_ok=True)
        return state_dir

    @pytest.fixture(autouse=True)
    def cleanup(self, state_dir):
        """Cleanup test state after each test"""
        yield
        state_file = state_dir / "workflow_state.json"
        if state_file.exists():
            state_file.unlink()

    def test_state_manager_merges_metadata_subkeys(self, run_id, state_dir):
        """
        Test that StateManager merges multiple metadata sub-keys into step_4.

        Simulates construction gates saving sequentially:
        1. qg_page_object saves pom_metadata
        2. qg_task saves task_metadata
        3. qg_role saves role_metadata
        4. qg_test_runner saves test_metadata

        Expected: All 4 metadata keys coexist in step_4
        """
        state_manager = StateManager(run_id=run_id)

        # Simulate qg_page_object saving
        state_manager.save(step=4, data={"pom_metadata": {"class_name": "LoginPage"}})

        # Simulate qg_task saving
        state_manager.save(step=4, data={"task_metadata": {"class_name": "AuthTasks"}})

        # Simulate qg_role saving
        state_manager.save(step=4, data={"role_metadata": {"class_name": "Customer"}})

        # Simulate qg_test_runner saving
        state_manager.save(step=4, data={"test_metadata": {"file_path": "tests/test1.py"}})

        # Verify all metadata sub-keys exist
        state_file = state_dir / "workflow_state.json"
        assert state_file.exists(), "State file should exist"

        with open(state_file, 'r') as f:
            state = json.load(f)

        assert "step_4" in state, "step_4 should exist"
        step_4_data = state["step_4"]

        # All 4 metadata keys should coexist (state accumulation)
        assert "pom_metadata" in step_4_data, "pom_metadata should exist"
        assert "task_metadata" in step_4_data, "task_metadata should exist"
        assert "role_metadata" in step_4_data, "role_metadata should exist"
        assert "test_metadata" in step_4_data, "test_metadata should exist"

        # Verify content
        assert step_4_data["pom_metadata"]["class_name"] == "LoginPage"
        assert step_4_data["task_metadata"]["class_name"] == "AuthTasks"
        assert step_4_data["role_metadata"]["class_name"] == "Customer"
        assert step_4_data["test_metadata"]["file_path"] == "tests/test1.py"

    def test_gate_enforcer_blocks_without_metadata(self, run_id, state_dir):
        """
        Test that gate enforcer blocks writes to tests/ without step_4.test_metadata.

        This simulates the error we encountered in Task 1.1.3.4:
        - Step 1 complete (user input)
        - Try to write to tests/_reports/ (transcript)
        - Should block: step_4.test_metadata doesn't exist yet
        """
        state_manager = StateManager(run_id=run_id)

        # Create state with only step_1 (like our real test)
        state_manager.save(step=1, data={
            "persona": "customer",
            "URL": "https://example.com",
            "role_name": "Customer",
            "workflow": "helios5"
        })

        # Now verify gate enforcer would block
        from mcp_server._dev_tests.test_gates.test_gate_enforcer_step4_helper import check_gate_enforcer

        # Should block: step_4.test_metadata doesn't exist
        result = check_gate_enforcer(
            file_path="tests/_reports/2026-01-22T09-00-00/workflow_transcript.md",
            state_dir=state_dir
        )

        assert result["blocked"] is True, "Gate enforcer should block write"
        assert "step_4" in result["error"], "Error should mention step_4"
        assert "test_metadata" in result["error"], "Error should mention test_metadata"

    def test_gate_enforcer_allows_with_metadata(self, run_id, state_dir):
        """
        Test that gate enforcer allows writes to tests/ WITH step_4.test_metadata.

        This simulates construction complete:
        - Step 4 has test_metadata
        - Write to tests/ should be allowed
        """
        state_manager = StateManager(run_id=run_id)

        # Create state with step_4.test_metadata
        state_manager.save(step=1, data={"persona": "customer", "URL": "https://example.com"})
        state_manager.save(step=4, data={
            "test_metadata": {
                "file_path": "tests/helios5/test_search.py",
                "test_name": "test_search_sales_rep"
            }
        })

        # Now verify gate enforcer would allow
        from mcp_server._dev_tests.test_gates.test_gate_enforcer_step4_helper import check_gate_enforcer

        # Should allow: step_4.test_metadata exists
        result = check_gate_enforcer(
            file_path="tests/helios5/test_search.py",
            state_dir=state_dir
        )

        assert result["blocked"] is False, "Gate enforcer should allow write"
        assert result["error"] is None, "No error should be present"

    def test_gate_enforcer_path_specific_metadata(self, run_id, state_dir):
        """
        Test that gate enforcer checks correct metadata sub-key based on file path.

        - framework/pages/ requires pom_metadata
        - framework/tasks/ requires task_metadata
        - framework/roles/ requires role_metadata
        - tests/ requires test_metadata
        """
        state_manager = StateManager(run_id=run_id)

        # Create state with only pom_metadata
        state_manager.save(step=4, data={
            "pom_metadata": {"class_name": "LoginPage"}
        })

        from mcp_server._dev_tests.test_gates.test_gate_enforcer_step4_helper import check_gate_enforcer

        # Should allow: framework/pages/ with pom_metadata
        result_page = check_gate_enforcer(
            file_path="framework/pages/auth/login_page.py",
            state_dir=state_dir
        )
        assert result_page["blocked"] is False, "Should allow pages/ with pom_metadata"

        # Should block: framework/tasks/ without task_metadata
        result_task = check_gate_enforcer(
            file_path="framework/tasks/auth_tasks.py",
            state_dir=state_dir
        )
        assert result_task["blocked"] is True, "Should block tasks/ without task_metadata"
        assert "task_metadata" in result_task["error"], "Error should mention task_metadata"

        # Should block: tests/ without test_metadata
        result_test = check_gate_enforcer(
            file_path="tests/test_login.py",
            state_dir=state_dir
        )
        assert result_test["blocked"] is True, "Should block tests/ without test_metadata"
        assert "test_metadata" in result_test["error"], "Error should mention test_metadata"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
