"""
Test fixtures for Step 1 (User Input) gate testing.

Provides reusable test data loaders and helper functions for:
- Valid/invalid input data
- Mock environment configuration
- Common test scenarios
"""

import json
from pathlib import Path
from typing import Dict, List, Any


# Path to test data directory
TEST_DATA_DIR = Path(__file__).parent.parent / "test_data"


def load_valid_inputs() -> List[Dict[str, Any]]:
    """
    Load valid Step 1 input test cases.

    Returns:
        List of valid test case dictionaries with persona, URL, role_name, workflow, raw_requirement
    """
    with open(TEST_DATA_DIR / "step1_valid_inputs.json", "r") as f:
        data = json.load(f)
    return data["test_cases"]


def load_invalid_inputs() -> List[Dict[str, Any]]:
    """
    Load invalid Step 1 input test cases (edge cases and errors).

    Returns:
        List of invalid test case dictionaries with expected_error or expected_behavior
    """
    with open(TEST_DATA_DIR / "step1_invalid_inputs.json", "r") as f:
        data = json.load(f)
    return data["test_cases"]


def load_mock_environment_config() -> Dict[str, Dict[str, str]]:
    """
    Load mock environment configuration for testing.

    Returns:
        Dictionary mapping environment names to their config (url, etc.)
    """
    with open(TEST_DATA_DIR / "mock_environment_config.json", "r") as f:
        config = json.load(f)
    # Remove description key if present
    config.pop("description", None)
    return config


def get_valid_input_by_id(test_id: str) -> Dict[str, Any]:
    """
    Get a specific valid test case by ID.

    Args:
        test_id: The test case ID (e.g., "valid_auth_login")

    Returns:
        Test case dictionary

    Raises:
        ValueError: If test_id not found
    """
    test_cases = load_valid_inputs()
    for case in test_cases:
        if case["id"] == test_id:
            return case
    raise ValueError(f"Valid test case '{test_id}' not found")


def get_invalid_input_by_id(test_id: str) -> Dict[str, Any]:
    """
    Get a specific invalid test case by ID.

    Args:
        test_id: The test case ID (e.g., "invalid_missing_persona")

    Returns:
        Test case dictionary

    Raises:
        ValueError: If test_id not found
    """
    test_cases = load_invalid_inputs()
    for case in test_cases:
        if case["id"] == test_id:
            return case
    raise ValueError(f"Invalid test case '{test_id}' not found")


def get_known_environment_url(env_name: str) -> str:
    """
    Get URL for a known test environment.

    Args:
        env_name: Environment name from mock config

    Returns:
        Environment URL

    Raises:
        KeyError: If environment not in mock config
    """
    config = load_mock_environment_config()
    return config[env_name]["url"]


def is_known_environment(url: str) -> bool:
    """
    Check if URL matches a known environment in mock config.

    Args:
        url: URL to check

    Returns:
        True if URL matches any known environment, False otherwise
    """
    config = load_mock_environment_config()
    known_urls = [env_data["url"] for env_data in config.values()]
    return url in known_urls


# Common test data builders

def build_valid_input(
    persona: str = "As a registered user",
    url: str = "http://www.automationpractice.pl/index.php",
    role_name: str = "RegisteredUser",
    workflow: str = "auth",
    raw_requirement: str = "As a registered user, I want to log in"
) -> Dict[str, Any]:
    """
    Build a valid Step 1 input dictionary with custom values.

    Args:
        persona: User persona (defaults to registered user)
        url: Target URL (defaults to automationpractice)
        role_name: Role class name (defaults to RegisteredUser)
        workflow: Workflow/domain name (defaults to auth)
        raw_requirement: Full user story (defaults to login scenario)

    Returns:
        Valid input dictionary for qg_user_input gate
    """
    return {
        "persona": persona,
        "url": url,
        "role_name": role_name,
        "workflow": workflow,
        "raw_requirement": raw_requirement
    }


def build_invalid_input(
    persona: str = "",
    url: str = "http://www.example.com",
    role_name: str = "SomeRole",
    workflow: str = "auth",
    raw_requirement: str = "I want to do something"
) -> Dict[str, Any]:
    """
    Build an invalid Step 1 input dictionary with custom values.

    Defaults create a missing persona error case. Override parameters to test other error conditions.

    Args:
        persona: User persona (defaults to empty for error)
        url: Target URL (defaults to valid URL)
        role_name: Role class name (defaults to valid PascalCase)
        workflow: Workflow/domain name (defaults to valid lowercase)
        raw_requirement: Full user story (defaults to invalid format)

    Returns:
        Invalid input dictionary for qg_user_input gate testing
    """
    return {
        "persona": persona,
        "url": url,
        "role_name": role_name,
        "workflow": workflow,
        "raw_requirement": raw_requirement
    }
