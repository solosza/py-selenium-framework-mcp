"""
Requirements Parser Utility

Parses user stories and extracts Given-When-Then scenarios.
Used by Tool 1 (generate_tests_from_user_story).
"""

import re
from typing import Dict, List, Optional


def parse_user_story(user_story: str) -> Dict[str, any]:
    """
    Parse user story and extract structured information.

    Args:
        user_story: User story text with acceptance criteria

    Returns:
        Dict with parsed story components
    """
    result = {
        "title": extract_title(user_story),
        "description": extract_description(user_story),
        "acceptance_criteria": extract_acceptance_criteria(user_story),
        "scenarios": extract_scenarios(user_story)
    }

    return result


def extract_title(user_story: str) -> str:
    """Extract user story title (first line or As a... statement)."""
    lines = user_story.strip().split('\n')

    if not lines:
        return "Untitled User Story"

    # Find first non-empty line
    for line in lines:
        stripped = line.strip()
        if stripped:
            # Check if it's an "As a..." user story format
            if stripped.lower().startswith('as a'):
                return stripped
            return stripped

    return "Untitled User Story"


def extract_description(user_story: str) -> str:
    """Extract user story description."""
    # Simple extraction: everything before "Acceptance Criteria" or "Given"
    lines = user_story.strip().split('\n')
    description_lines = []

    for line in lines:
        lower_line = line.lower().strip()
        if any(keyword in lower_line for keyword in ['acceptance criteria', 'given', 'when', 'then']):
            break
        description_lines.append(line.strip())

    return '\n'.join(description_lines).strip()


def extract_acceptance_criteria(user_story: str) -> List[str]:
    """Extract bullet points from acceptance criteria section."""
    criteria = []
    in_criteria_section = False

    for line in user_story.split('\n'):
        lower_line = line.lower().strip()

        # Start of acceptance criteria section
        if 'acceptance criteria' in lower_line:
            in_criteria_section = True
            continue

        # End of acceptance criteria (scenario starts)
        if in_criteria_section and any(keyword in lower_line for keyword in ['given', 'scenario']):
            break

        # Collect bullet points
        if in_criteria_section:
            stripped = line.strip()
            if stripped.startswith(('-', '*', '•')):
                criteria.append(stripped.lstrip('-*•').strip())

    return criteria


def extract_scenarios(user_story: str) -> List[Dict[str, str]]:
    """
    Extract Given-When-Then scenarios from user story.

    Returns:
        List of scenarios with given/when/then/name
    """
    scenarios = []
    current_scenario = None

    lines = user_story.split('\n')

    for i, line in enumerate(lines):
        line = line.strip()
        lower_line = line.lower()

        # Detect scenario start
        if lower_line.startswith('scenario:') or lower_line.startswith('## scenario'):
            if current_scenario:
                scenarios.append(current_scenario)

            scenario_name = line.split(':', 1)[1].strip() if ':' in line else f"Scenario {len(scenarios) + 1}"
            current_scenario = {
                "name": scenario_name,
                "given": "",
                "when": "",
                "then": ""
            }
            continue

        if not current_scenario:
            # Auto-create scenario if we find Given without explicit Scenario: marker
            if lower_line.startswith('given'):
                current_scenario = {
                    "name": f"Scenario {len(scenarios) + 1}",
                    "given": "",
                    "when": "",
                    "then": ""
                }

        # Extract Given/When/Then (case-insensitive split)
        if current_scenario:
            if lower_line.startswith('given'):
                # Use regex for case-insensitive split
                import re
                parts = re.split(r'given\s*:?\s*', line, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) > 1:
                    current_scenario["given"] = parts[1].strip()
            elif lower_line.startswith('when'):
                import re
                parts = re.split(r'when\s*:?\s*', line, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) > 1:
                    current_scenario["when"] = parts[1].strip()
            elif lower_line.startswith('then'):
                import re
                parts = re.split(r'then\s*:?\s*', line, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) > 1:
                    current_scenario["then"] = parts[1].strip()
            elif lower_line.startswith('and'):
                import re
                parts = re.split(r'and\s*:?\s*', line, maxsplit=1, flags=re.IGNORECASE)
                if len(parts) > 1:
                    and_text = parts[1].strip()
                    if current_scenario["then"]:
                        current_scenario["then"] += f" AND {and_text}"
                    elif current_scenario["when"]:
                        current_scenario["when"] += f" AND {and_text}"
                    elif current_scenario["given"]:
                        current_scenario["given"] += f" AND {and_text}"

    # Add final scenario
    if current_scenario and (current_scenario["given"] or current_scenario["when"] or current_scenario["then"]):
        scenarios.append(current_scenario)

    return scenarios


def generate_test_name(scenario: Dict[str, str], workflow: str) -> str:
    """
    Generate test function name from scenario.

    Args:
        scenario: Scenario dict with given/when/then
        workflow: Workflow name (auth, catalog, cart, checkout)

    Returns:
        Test function name (e.g., test_add_product_to_cart)
    """
    # Use scenario name if available
    if scenario.get("name") and scenario["name"] != "Scenario 1":
        name = scenario["name"]
    elif scenario.get("when"):
        name = scenario["when"]
    else:
        name = scenario.get("then", "test")

    # Convert to snake_case
    name = name.lower()
    name = re.sub(r'[^\w\s]', '', name)  # Remove punctuation
    name = re.sub(r'\s+', '_', name)  # Replace spaces with underscores

    # Ensure it starts with 'test_'
    if not name.startswith('test_'):
        name = f"test_{name}"

    return name


def validate_scenario(scenario: Dict[str, str]) -> bool:
    """
    Validate that scenario has required fields.

    Args:
        scenario: Scenario dict

    Returns:
        True if valid (has at least when/then)
    """
    return bool(scenario.get("when") and scenario.get("then"))
