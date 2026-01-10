"""
Unit tests for semantic validation rules (Task 36.0, FR-14.1-14.4).

Tests the pluggable semantic rules framework and individual rules.
"""

import pytest
from tools.gates.semantic_rules.base import SemanticRule
from tools.gates.semantic_rules.registry import SemanticRuleRegistry, SEMANTIC_RULES
from tools.gates.semantic_rules.contradiction_rule import ParameterContradictionRule
from tools.gates.semantic_rules.credential_strategy_rule import CredentialStrategyRule
from tools.gates.semantic_rules.test_data_location_rule import TestDataLocationRule


class TestSemanticRuleFramework:
    """Test the pluggable framework itself."""

    def test_registry_can_register_rules(self):
        """Test that registry can register and list rules."""
        # Create a test registry
        registry = SemanticRuleRegistry()

        # Register a rule
        rule = ParameterContradictionRule()
        registry.register(rule)

        # Verify rule is registered
        rules = registry.list_rules()
        assert len(rules) == 1
        assert rules[0]["name"] == "parameter_contradiction"

    def test_registry_check_all_runs_rules(self):
        """Test that check_all runs all registered rules."""
        registry = SemanticRuleRegistry()
        rule = ParameterContradictionRule()
        registry.register(rule)

        # Code with contradiction
        code = 'user.transfer_funds(from_account="123", to_account="123")'
        context = {}

        result = registry.check_all(code, context)

        # Should fail
        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "parameter_contradiction" in result.get("failed_rule", "")

    def test_registry_check_all_passes_clean_code(self):
        """Test that check_all passes code without violations."""
        registry = SemanticRuleRegistry()
        rule = ParameterContradictionRule()
        registry.register(rule)

        # Code without contradiction
        code = 'user.transfer_funds(from_account="123", to_account="456")'
        context = {}

        result = registry.check_all(code, context)

        # Should pass
        assert result is None

    def test_global_registry_has_rules(self):
        """Test that global SEMANTIC_RULES registry has rules registered."""
        rules = SEMANTIC_RULES.list_rules()

        # Should have at least the contradiction rule
        assert len(rules) >= 1
        rule_names = [r["name"] for r in rules]
        assert "parameter_contradiction" in rule_names


class TestParameterContradictionRule:
    """Test FR-14.1: Parameter contradiction detection."""

    def test_detects_transfer_same_account(self):
        """Test detection of from_account == to_account."""
        rule = ParameterContradictionRule()

        code = '''
def test_transfer_funds(user):
    user.transfer_funds(from_account="123", to_account="123", amount=100)
    assert user.is_transfer_complete()
'''
        context = {}

        result = rule.check(code, context)

        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "from_account" in result["error"]
        assert "to_account" in result["error"]
        assert "meaningless operation" in result["error"]

    def test_detects_database_migration_same_db(self):
        """Test detection of source_db == target_db."""
        rule = ParameterContradictionRule()

        code = '''
def test_migrate_data(admin):
    admin.migrate_data(source_db="prod", target_db="prod")
    assert admin.is_migration_complete()
'''
        context = {}

        result = rule.check(code, context)

        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "source_db" in result["error"]
        assert "target_db" in result["error"]

    def test_detects_password_change_same_password(self):
        """Test detection of old_password == new_password."""
        rule = ParameterContradictionRule()

        code = '''
def test_update_password(user):
    user.update_password(old_password="abc123", new_password="abc123")
    assert user.is_password_updated()
'''
        context = {}

        result = rule.check(code, context)

        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "old_password" in result["error"]
        assert "new_password" in result["error"]

    def test_detects_message_sender_equals_receiver(self):
        """Test detection of sender == receiver."""
        rule = ParameterContradictionRule()

        code = '''
def test_send_message(user):
    user.send_message(sender="alice", receiver="alice", text="Hello")
    assert user.is_message_sent()
'''
        context = {}

        result = rule.check(code, context)

        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "sender" in result["error"]
        assert "receiver" in result["error"]

    def test_detects_file_copy_same_path(self):
        """Test detection of src_path == dst_path."""
        rule = ParameterContradictionRule()

        code = '''
def test_copy_file(user):
    user.copy_file(src_path="/home/file.txt", dst_path="/home/file.txt")
    assert user.is_file_copied()
'''
        context = {}

        result = rule.check(code, context)

        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "src_path" in result["error"]
        assert "dst_path" in result["error"]

    def test_passes_transfer_different_accounts(self):
        """Test that different values pass validation."""
        rule = ParameterContradictionRule()

        code = '''
def test_transfer_funds(user):
    user.transfer_funds(from_account="123", to_account="456", amount=100)
    assert user.is_transfer_complete()
'''
        context = {}

        result = rule.check(code, context)

        assert result is None

    def test_passes_multiple_params_without_opposite_pairs(self):
        """Test that unrelated parameters don't trigger false positives."""
        rule = ParameterContradictionRule()

        code = '''
def test_create_user(admin):
    admin.create_user(username="alice", email="alice@test.com", role="user")
    assert admin.is_user_created()
'''
        context = {}

        result = rule.check(code, context)

        assert result is None

    def test_passes_when_only_one_side_of_pair_present(self):
        """Test that having only from_X or only to_X doesn't trigger."""
        rule = ParameterContradictionRule()

        code = '''
def test_deposit_funds(user):
    user.deposit_funds(to_account="123", amount=100)
    assert user.is_deposit_complete()
'''
        context = {}

        result = rule.check(code, context)

        assert result is None

    def test_detects_multiple_contradictions_returns_first(self):
        """Test that multiple contradictions are detected (returns first)."""
        rule = ParameterContradictionRule()

        code = '''
def test_complex_operation(user):
    user.transfer_funds(from_account="123", to_account="123", amount=100)
    user.update_password(old_password="abc", new_password="abc")
    assert user.is_complete()
'''
        context = {}

        result = rule.check(code, context)

        # Should detect at least one contradiction
        assert result is not None
        assert result["status"] == "NEEDS_RETRY"

    def test_handles_single_quotes(self):
        """Test that single quotes are parsed correctly."""
        rule = ParameterContradictionRule()

        code = """
def test_transfer_funds(user):
    user.transfer_funds(from_account='123', to_account='123', amount=100)
    assert user.is_transfer_complete()
"""
        context = {}

        result = rule.check(code, context)

        assert result is not None
        assert "from_account" in result["error"]


class TestCredentialStrategyRule:
    """Test FR-14.2: Credential strategy enforcement."""

    def test_self_contained_passes_with_uuid(self):
        """Test self-contained strategy passes with uuid generation."""
        rule = CredentialStrategyRule()

        code = '''
import uuid
class RegisteredUser:
    def __init__(self, web_interface, base_url):
        self.email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.password = "TestPass123!"
        self.auth_tasks = AuthTasks(web_interface, base_url)
'''
        context = {"step_1_config": {"credential_strategy": "self-contained"}}

        result = rule.check(code, context)
        assert result is None

    def test_self_contained_fails_with_test_users(self):
        """Test self-contained strategy fails when using test_users fixture."""
        rule = CredentialStrategyRule()

        code = '''
class RegisteredUser:
    def __init__(self, web_interface, user_data, base_url):
        self.user_data = user_data
        self.email = user_data.get('email')
        self.auth_tasks = AuthTasks(web_interface, base_url)
'''
        context = {"step_1_config": {"credential_strategy": "self-contained"}}

        result = rule.check(code, context)
        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "static" in result["error"].lower()
        assert "test_users" in result["message"]

    def test_static_passes_with_test_users(self):
        """Test static strategy passes with test_users fixture."""
        rule = CredentialStrategyRule()

        code = '''
class RegisteredUser:
    def __init__(self, web_interface, user_data, base_url):
        self.user_data = user_data
        self.email = user_data.get('email')
        self.password = user_data.get('password')
        self.auth_tasks = AuthTasks(web_interface, base_url)
'''
        context = {"step_1_config": {"credential_strategy": "static"}}

        result = rule.check(code, context)
        assert result is None

    def test_static_fails_with_uuid(self):
        """Test static strategy fails when generating credentials."""
        rule = CredentialStrategyRule()

        code = '''
import uuid
class RegisteredUser:
    def __init__(self, web_interface, base_url):
        self.email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.auth_tasks = AuthTasks(web_interface, base_url)
'''
        context = {"step_1_config": {"credential_strategy": "static"}}

        result = rule.check(code, context)
        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "generates credentials" in result["error"]
        assert "test_users" in result["message"]

    def test_dynamic_passes_with_config_read(self):
        """Test dynamic strategy passes with config file read."""
        rule = CredentialStrategyRule()

        code = '''
import json
class RegisteredUser:
    def __init__(self, web_interface, base_url):
        with open('tests/data/test_users.json') as f:
            users = json.load(f)
            self.user_data = users.get('registered_user')
        self.auth_tasks = AuthTasks(web_interface, base_url)
'''
        context = {"step_1_config": {"credential_strategy": "dynamic"}}

        result = rule.check(code, context)
        assert result is None

    def test_dynamic_fails_with_test_users_fixture(self):
        """Test dynamic strategy fails with test_users fixture."""
        rule = CredentialStrategyRule()

        code = '''
class RegisteredUser:
    def __init__(self, web_interface, user_data, base_url):
        self.user_data = user_data
        self.auth_tasks = AuthTasks(web_interface, base_url)
'''
        context = {"step_1_config": {"credential_strategy": "dynamic"}}

        result = rule.check(code, context)
        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "static" in result["error"].lower()

    def test_none_passes_without_credentials(self):
        """Test none strategy passes when no credentials present."""
        rule = CredentialStrategyRule()

        code = '''
class GuestUser:
    def __init__(self, web_interface, base_url):
        self.web = web_interface
        self.catalog_tasks = CatalogTasks(web_interface, base_url)
'''
        context = {"step_1_config": {"credential_strategy": "none"}}

        result = rule.check(code, context)
        assert result is None

    def test_none_fails_with_credentials(self):
        """Test none strategy fails when credentials present."""
        rule = CredentialStrategyRule()

        code = '''
import uuid
class GuestUser:
    def __init__(self, web_interface, base_url):
        self.email = f"test_{uuid.uuid4().hex[:8]}@example.com"
        self.catalog_tasks = CatalogTasks(web_interface, base_url)
'''
        context = {"step_1_config": {"credential_strategy": "none"}}

        result = rule.check(code, context)
        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "none" in result["error"].lower()

    def test_skips_validation_when_no_strategy(self):
        """Test rule skips validation when no strategy specified."""
        rule = CredentialStrategyRule()

        code = '''
class RegisteredUser:
    def __init__(self, web_interface, user_data, base_url):
        self.user_data = user_data
'''
        context = {"step_1_config": {}}  # No credential_strategy

        result = rule.check(code, context)
        assert result is None

    def test_global_registry_has_credential_strategy_rule(self):
        """Test that global registry includes credential strategy rule."""
        rules = SEMANTIC_RULES.list_rules()
        rule_names = [r["name"] for r in rules]
        assert "credential_strategy" in rule_names


class TestTestDataLocationRule:
    """Test FR-14.3: Test data location enforcement."""

    def test_shared_passes_with_shared_import(self):
        """Test shared strategy passes with tests.data imports."""
        rule = TestDataLocationRule()

        code = '''
import pytest
from tests.data import test_users
from roles.registered_user import RegisteredUser

def test_login():
    user_data = test_users.get("registered_user")
    user = RegisteredUser(web, user_data, base_url)
'''
        context = {"step_1_config": {"test_data_location": "shared"}}

        result = rule.check(code, context)
        assert result is None

    def test_shared_fails_with_workflow_import(self):
        """Test shared strategy fails with workflow-specific imports."""
        rule = TestDataLocationRule()

        code = '''
import pytest
from tests.parabank.data import transfer_data
from roles.registered_user import RegisteredUser

def test_transfer():
    data = transfer_data.get("amounts")
'''
        context = {"step_1_config": {"test_data_location": "shared"}}

        result = rule.check(code, context)
        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "tests.parabank.data" in result["error"]
        assert "shared" in result["error"]

    def test_workflow_passes_with_workflow_import(self):
        """Test workflow strategy passes with workflow-specific imports."""
        rule = TestDataLocationRule()

        code = '''
import pytest
from tests.parabank.data import transfer_data
from roles.registered_user import RegisteredUser

def test_transfer():
    data = transfer_data.get("amounts")
'''
        context = {
            "step_1_config": {"test_data_location": "workflow"},
            "test_scenarios": [{"workflow": "parabank"}]
        }

        result = rule.check(code, context)
        assert result is None

    def test_workflow_fails_with_shared_import(self):
        """Test workflow strategy fails with shared imports."""
        rule = TestDataLocationRule()

        code = '''
import pytest
from tests.data import test_users
from roles.registered_user import RegisteredUser

def test_login():
    user_data = test_users.get("registered_user")
'''
        context = {
            "step_1_config": {"test_data_location": "workflow"},
            "test_scenarios": [{"workflow": "auth"}]
        }

        result = rule.check(code, context)
        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "tests.data" in result["error"]
        assert "workflow-specific" in result["error"]

    def test_both_passes_with_shared_import(self):
        """Test both strategy passes with shared imports."""
        rule = TestDataLocationRule()

        code = '''
from tests.data import test_users
'''
        context = {"step_1_config": {"test_data_location": "both"}}

        result = rule.check(code, context)
        assert result is None

    def test_both_passes_with_workflow_import(self):
        """Test both strategy passes with workflow imports."""
        rule = TestDataLocationRule()

        code = '''
from tests.parabank.data import transfer_data
'''
        context = {"step_1_config": {"test_data_location": "both"}}

        result = rule.check(code, context)
        assert result is None

    def test_both_passes_with_mixed_imports(self):
        """Test both strategy passes with mixed imports."""
        rule = TestDataLocationRule()

        code = '''
from tests.data import test_users
from tests.parabank.data import transfer_data
'''
        context = {"step_1_config": {"test_data_location": "both"}}

        result = rule.check(code, context)
        assert result is None

    def test_none_passes_without_data_imports(self):
        """Test none strategy passes when no data imports present."""
        rule = TestDataLocationRule()

        code = '''
import pytest
from roles.registered_user import RegisteredUser
from pages.login_page import LoginPage

def test_login():
    user = RegisteredUser(web, base_url)
    user.login()
'''
        context = {"step_1_config": {"test_data_location": "none"}}

        result = rule.check(code, context)
        assert result is None

    def test_none_fails_with_data_imports(self):
        """Test none strategy fails when data imports present."""
        rule = TestDataLocationRule()

        code = '''
from tests.data import test_users

def test_login():
    user_data = test_users.get("registered_user")
'''
        context = {"step_1_config": {"test_data_location": "none"}}

        result = rule.check(code, context)
        assert result is not None
        assert result["status"] == "NEEDS_RETRY"
        assert "none" in result["error"]

    def test_skips_validation_when_no_strategy(self):
        """Test rule skips validation when no strategy specified."""
        rule = TestDataLocationRule()

        code = '''
from tests.data import test_users
'''
        context = {"step_1_config": {}}

        result = rule.check(code, context)
        assert result is None

    def test_skips_validation_when_no_data_imports(self):
        """Test rule skips when no data imports (regardless of strategy)."""
        rule = TestDataLocationRule()

        code = '''
import pytest
from roles.registered_user import RegisteredUser

def test_something():
    pass
'''
        context = {"step_1_config": {"test_data_location": "shared"}}

        result = rule.check(code, context)
        assert result is None

    def test_global_registry_has_test_data_location_rule(self):
        """Test that global registry includes test data location rule."""
        rules = SEMANTIC_RULES.list_rules()
        rule_names = [r["name"] for r in rules]
        assert "test_data_location" in rule_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
