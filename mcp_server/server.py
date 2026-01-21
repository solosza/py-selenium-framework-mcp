#!/usr/bin/env python3
"""
MCP Server for QA Test Automation Framework

Provides tools following the 4-layer architecture workflow:

IMPLEMENTED (Tools 1-6):
1. generate_tests_from_user_story - User story → test scenarios (Given-When-Then)
2. discover_page_elements - Page URL → discovered elements
3. generate_page_object - Elements → POM code
4. generate_task - POM → Task module
5. generate_role - Task → Role module
6. generate_test_runner - Role → pytest runner code

QUALITY GATES (Steps 1-10):
- qg_preflight (Step 1) - Pre-flight configuration validation
- qg_user_input (Step 2) - User input validation
- qg_ai_processing (Step 3) - AI processing validation
- qg_test_scenarios (Step 4) - Test scenarios validation (PRE+POST)
- qg_discovered_elements (Step 5) - Discovered elements validation (PRE+POST)
- qg_page_object (Step 6) - Page object validation (PRE+POST)
- qg_task (Step 7) - Task validation (PRE+POST)
- qg_role (Step 8) - Role validation (PRE+POST)
- qg_test_runner (Step 9) - Test runner validation (PRE+POST)
- qg_save_run (Step 10) - File validation (PRE-only)

PLANNED (Tools 7-11):
7. list_tests - Catalog all tests
8. get_framework_structure - Map framework architecture
9. run_test - Execute tests
10. analyze_failure - AI-powered debugging
11. get_test_coverage - Coverage tracking
"""

import asyncio
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from mcp.server import Server
from mcp.types import Tool, TextContent

# Import tool implementations (Tools 1-6 implemented)
from tools.tool_01_generate_tests_from_user_story import generate_tests_from_user_story
from tools.tool_02_discover_page_elements import discover_elements as discover_page_elements
from tools.tool_03_generate_page_object import generate_page_object
from tools.tool_04_generate_task import generate_task
from tools.tool_05_generate_role import generate_role
from tools.tool_06_generate_test_runner import generate_test_runner

# Import quality gates (Steps 1-11)
from tools.gates.qg_preflight import QGPreflight
from tools.gates.qg_user_input import QGUserInput
from tools.gates.qg_ai_processing import QGAIProcessing
from tools.gates.qg_test_scenarios import QGTestScenarios
from tools.gates.qg_discovered_elements import QGDiscoveredElements
from tools.gates.qg_page_object import QGPageObject
from tools.gates.qg_task import QGTask
from tools.gates.qg_role import QGRole
from tools.gates.qg_test_runner import QGTestRunner
from tools.gates.qg_save_run import QGSaveRun
from tools.gates.qg_execution import QGExecution
from tools.gates.qg_workflow_complete import QGWorkflowComplete

# Import operations (Tool 9: run_test)
from tools.operations.run_test import run_test_async

# Tools 7-11 not yet implemented - stub functions
async def list_tests(arguments: dict) -> str:
    return '{"status": "not_implemented", "message": "Tool 7 (list_tests) is planned but not yet implemented"}'

async def get_framework_structure(arguments: dict) -> str:
    return '{"status": "not_implemented", "message": "Tool 8 (get_framework_structure) is planned but not yet implemented"}'

async def run_test(arguments: dict) -> str:
    """Tool 9: Execute pytest test with standard flags and capture results."""
    return await run_test_async(arguments)

async def analyze_failure(arguments: dict) -> str:
    return '{"status": "not_implemented", "message": "Tool 10 (analyze_failure) is planned but not yet implemented"}'

async def get_test_coverage(arguments: dict) -> str:
    return '{"status": "not_implemented", "message": "Tool 11 (get_test_coverage) is planned but not yet implemented"}'


# =============================================================================
# Quality Gate Wrapper Functions (Steps 1-10)
# =============================================================================

async def qg_preflight(arguments: dict) -> str:
    """Step 1: Pre-flight configuration validation (POST-only)."""
    result = QGPreflight.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_user_input(arguments: dict) -> str:
    """Step 2: User input validation (POST-only)."""
    result = QGUserInput.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_ai_processing(arguments: dict) -> str:
    """Step 3: AI processing validation (POST-only)."""
    result = QGAIProcessing.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_test_scenarios(arguments: dict) -> str:
    """Step 4: Test scenarios validation (PRE+POST). Requires 'mode' field."""
    result = QGTestScenarios.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_discovered_elements(arguments: dict) -> str:
    """Step 5: Discovered elements validation (PRE+POST). Requires 'mode' field."""
    result = QGDiscoveredElements.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_page_object(arguments: dict) -> str:
    """Step 6: Page object validation (PRE+POST). Requires 'mode' field."""
    result = QGPageObject.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_task(arguments: dict) -> str:
    """Step 7: Task validation (PRE+POST). Requires 'mode' field."""
    result = QGTask.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_role(arguments: dict) -> str:
    """Step 8: Role validation (PRE+POST). Requires 'mode' field."""
    result = QGRole.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_test_runner(arguments: dict) -> str:
    """Step 9: Test runner validation (PRE+POST). Requires 'mode' field."""
    result = QGTestRunner.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_save_run(arguments: dict) -> str:
    """Step 10: Final save/run validation (PRE-only)."""
    result = QGSaveRun.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_execution(arguments: dict) -> str:
    """Step 11: Execution validation with HITL triage (POST-only)."""
    result = QGExecution.validate(arguments)
    return json.dumps(result, indent=2)


async def qg_workflow_complete(arguments: dict) -> str:
    """Step 11: Workflow completion validation - 8 cross-step consistency checks."""
    result = QGWorkflowComplete.validate(arguments)
    return json.dumps(result, indent=2)


# Initialize MCP server
server = Server("qa-automation-framework")


@server.list_tools()
async def list_available_tools() -> list[Tool]:
    """Register all 11 MCP tools."""
    return [
        # Phase 1: Requirements Analysis
        Tool(
            name="generate_tests_from_user_story",
            description="Convert user story into test scenarios (Given-When-Then format)",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_story": {
                        "type": "string",
                        "description": "User story with acceptance criteria"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Target workflow/domain (e.g., auth, catalog, cart, checkout, or any custom domain)"
                    }
                },
                "required": ["user_story", "workflow"]
            }
        ),

        # Tool 6: Generate Test Runner (pytest code)
        Tool(
            name="generate_test_runner",
            description="Generate pytest test runner code from scenario (executes scenarios from Tool 1)",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {
                        "type": "string",
                        "description": "Test function name (e.g., test_add_to_cart)"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Workflow/domain category (e.g., auth, catalog, cart, checkout, or custom)"
                    },
                    "role": {
                        "type": "string",
                        "description": "Role class name (e.g., GuestUser, RegisteredUser)"
                    },
                    "scenario": {
                        "type": "object",
                        "description": "Test scenario with given/when/then (from Tool 1)"
                    },
                    "role_metadata": {
                        "type": "object",
                        "description": "Role metadata from Tool 5 (class_name, import_path, workflow_methods)"
                    },
                    "pom_metadata": {
                        "type": "object",
                        "description": "POM metadata from Tool 3 (for state-check method references)"
                    },
                    "task_metadata": {
                        "type": "object",
                        "description": "Task metadata from Tool 4"
                    }
                },
                "required": ["test_name", "workflow", "role"]
            }
        ),

        # Phase 3: Supporting Framework - Role
        Tool(
            name="generate_role",
            description="Generate role class from test requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "role_name": {
                        "type": "string",
                        "description": "Role name (e.g., RegisteredUser, GuestUser)"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Workflow/domain (e.g., auth, catalog, cart, checkout, or custom)"
                    },
                    "capabilities": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "What this role can do (e.g., can_login, has_cart_items)"
                    },
                    "credentials": {
                        "type": "object",
                        "description": "Optional user credentials"
                    },
                    "task_metadata": {
                        "type": "object",
                        "description": "Task metadata from Tool 4 (class_name, import_path, task_methods)"
                    },
                    "force_generate": {
                        "type": "boolean",
                        "description": "Skip existing role check (default: false)"
                    }
                },
                "required": ["role_name"]
            }
        ),

        # Phase 3: Supporting Framework - Task
        Tool(
            name="generate_task",
            description="Generate task workflow methods from test requirements",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_name": {
                        "type": "string",
                        "description": "Task class name (e.g., CatalogTasks, CartTasks)"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Workflow/domain (e.g., auth, catalog, cart, checkout, or custom)"
                    },
                    "workflow_description": {
                        "type": "string",
                        "description": "Description of workflow steps"
                    },
                    "pom_metadata": {
                        "type": "object",
                        "description": "POM metadata from Tool 3 (class_name, import_path, action_methods, state_methods)"
                    },
                    "page_objects": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Legacy: list of page object dicts (deprecated, use pom_metadata)"
                    },
                    "force_generate": {
                        "type": "boolean",
                        "description": "Skip existing task check (default: false)"
                    },
                    "base_url_path": {
                        "type": "string",
                        "description": "URL path for navigation (optional)"
                    }
                },
                "required": ["task_name"]
            }
        ),

        # Phase 4: Just-in-Time Element Discovery
        Tool(
            name="discover_page_elements",
            description="Discover interactive elements on page (just-in-time, right before POM generation)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "Page URL to analyze"
                    },
                    "page_name": {
                        "type": "string",
                        "description": "Suggested page object name"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Workflow/domain for organizing discovered elements"
                    },
                    "wait_for_state": {
                        "type": "string",
                        "description": "Wait condition before discovery (e.g., 'networkidle', 'domcontentloaded')"
                    }
                },
                "required": ["url"]
            }
        ),

        # Phase 5: POM Generation
        Tool(
            name="generate_page_object",
            description="Generate page object code from discovered elements",
            inputSchema={
                "type": "object",
                "properties": {
                    "page_name": {
                        "type": "string",
                        "description": "Page object class name"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Workflow/domain for file path organization"
                    },
                    "elements": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "Elements from discover_page_elements"
                    },
                    "expected_states": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Expected state names for state-check methods (from AI processing)"
                    },
                    "base_url": {
                        "type": "string",
                        "description": "Base URL for the page"
                    }
                },
                "required": ["page_name", "elements"]
            }
        ),

        # Phase 6: Framework Discovery
        Tool(
            name="list_tests",
            description="Catalog all available tests, organized by workflow",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow": {
                        "type": "string",
                        "description": "Optional filter by workflow"
                    }
                }
            }
        ),

        Tool(
            name="get_framework_structure",
            description="Map framework architecture (layers, components, coverage)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        # Phase 7: Test Execution
        Tool(
            name="run_test",
            description="Execute test(s) and return structured results",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_path": {
                        "type": "string",
                        "description": "Pytest path (e.g., tests/auth/test_login.py::test_valid_login)"
                    },
                    "marker": {
                        "type": "string",
                        "description": "Optional pytest marker filter (e.g., smoke)"
                    }
                },
                "required": ["test_path"]
            }
        ),

        # Phase 8: Failure Analysis
        Tool(
            name="analyze_failure",
            description="AI-powered debugging for failed tests with actionable suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_name": {
                        "type": "string",
                        "description": "Name of failed test"
                    },
                    "run_id": {
                        "type": "string",
                        "description": "Optional specific run timestamp"
                    }
                },
                "required": ["test_name"]
            }
        ),

        # Phase 9: Coverage Tracking
        Tool(
            name="get_test_coverage",
            description="Calculate test coverage by comparing designed scenarios vs implemented tests",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow": {
                        "type": "string",
                        "description": "Optional filter by workflow"
                    }
                }
            }
        ),

        # =================================================================
        # Quality Gates (Steps 1-10)
        # =================================================================

        # Step 1: Pre-flight Configuration (POST-only)
        Tool(
            name="qg_preflight",
            description="Step 1 quality gate: Validate pre-flight configuration (credential_strategy, test_data_location)",
            inputSchema={
                "type": "object",
                "properties": {
                    "credential_strategy": {
                        "type": "string",
                        "description": "Credential approach (e.g., static, dynamic, self-contained, none)"
                    },
                    "test_data_location": {
                        "type": "string",
                        "description": "Test data location (e.g., shared, workflow, both, none)"
                    }
                },
                "required": ["credential_strategy", "test_data_location"]
            }
        ),

        # Step 2: User Input (POST-only)
        Tool(
            name="qg_user_input",
            description="Step 2 quality gate: Validate user input (persona, URL, role_name, workflow)",
            inputSchema={
                "type": "object",
                "properties": {
                    "persona": {
                        "type": "string",
                        "description": "User persona (e.g., 'As a registered user')"
                    },
                    "URL": {
                        "type": "string",
                        "description": "Target page URL"
                    },
                    "role_name": {
                        "type": "string",
                        "description": "Derived role name (e.g., RegisteredUser)"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Workflow/domain (e.g., auth, catalog, cart, checkout, or custom)"
                    },
                    "raw_requirement": {
                        "type": "string",
                        "description": "Original user requirement text"
                    }
                },
                "required": ["persona", "URL", "role_name", "workflow"]
            }
        ),

        # Step 3: AI Processing (POST-only)
        Tool(
            name="qg_ai_processing",
            description="Step 3 quality gate: Validate AI processing output (bdd_scenarios, expected_states, intent)",
            inputSchema={
                "type": "object",
                "properties": {
                    "bdd_scenarios": {
                        "type": "array",
                        "description": "BDD scenarios with given/when/then",
                        "items": {"type": "object"}
                    },
                    "expected_states": {
                        "type": "array",
                        "description": "Expected state names for POM state-check methods",
                        "items": {"type": "string"}
                    },
                    "intent": {
                        "type": "string",
                        "description": "User intent (e.g., login, browse, checkout)"
                    }
                },
                "required": ["bdd_scenarios", "expected_states", "intent"]
            }
        ),

        # Step 4: Test Scenarios (PRE+POST)
        Tool(
            name="qg_test_scenarios",
            description="Step 4 quality gate: Validate test scenarios (PRE+POST mode). PRE checks Step 3 complete, POST validates scenarios.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Validation mode: PRE (before Tool 1) or POST (after Tool 1)",
                        "enum": ["PRE", "POST"]
                    },
                    "metadata_context": {
                        "type": "object",
                        "description": "PRE mode: Context from Step 3 (bdd_scenarios, expected_states, intent)"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "PRE mode: Target workflow/domain"
                    },
                    "test_scenarios": {
                        "type": "array",
                        "description": "POST mode: Generated test scenarios from Tool 1",
                        "items": {"type": "object"}
                    }
                },
                "required": ["mode"]
            }
        ),

        # Step 5: Discovered Elements (PRE+POST)
        Tool(
            name="qg_discovered_elements",
            description="Step 5 quality gate: Validate element discovery (PRE+POST mode). PRE checks Step 4 complete, POST validates elements.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Validation mode: PRE (before Tool 2) or POST (after Tool 2)",
                        "enum": ["PRE", "POST"]
                    },
                    "url": {
                        "type": "string",
                        "description": "PRE mode: Target page URL"
                    },
                    "page_name": {
                        "type": "string",
                        "description": "Page object class name (PascalCase)"
                    },
                    "credential_strategy": {
                        "type": "string",
                        "description": "PRE mode: Credential strategy from Step 1 (e.g., none, static, dynamic, self-contained)"
                    },
                    "discovery_method": {
                        "type": "string",
                        "description": "PRE mode: Discovery method (e.g., tool2, playwright)"
                    },
                    "elements": {
                        "type": "array",
                        "description": "POST mode: Discovered elements from Tool 2 or snapshot extraction",
                        "items": {"type": "object"}
                    }
                },
                "required": ["mode"]
            }
        ),

        # Step 6: Page Object (PRE+POST)
        Tool(
            name="qg_page_object",
            description="Step 6 quality gate: Validate POM generation (PRE+POST mode). PRE checks Step 5 complete, POST validates code quality.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Validation mode: PRE (before Tool 3) or POST (after Tool 3)",
                        "enum": ["PRE", "POST"]
                    },
                    "discovered_elements": {
                        "type": "array",
                        "description": "PRE mode: Elements from Step 5",
                        "items": {"type": "object"}
                    },
                    "page_name": {
                        "type": "string",
                        "description": "Page object class name (PascalCase)"
                    },
                    "expected_states": {
                        "type": "array",
                        "description": "PRE mode: Expected states from Step 3",
                        "items": {"type": "object"}
                    },
                    "code": {
                        "type": "string",
                        "description": "POST mode: Generated POM code"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "POST mode: POM metadata (class_name, import_path, locators, methods)"
                    }
                },
                "required": ["mode"]
            }
        ),

        # Step 7: Task (PRE+POST)
        Tool(
            name="qg_task",
            description="Step 7 quality gate: Validate Task generation (PRE+POST mode). PRE checks Step 6 complete, POST validates no locators/skeleton.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Validation mode: PRE (before Tool 4) or POST (after Tool 4)",
                        "enum": ["PRE", "POST"]
                    },
                    "pom_metadata": {
                        "type": "object",
                        "description": "PRE mode: POM metadata from Step 6"
                    },
                    "code": {
                        "type": "string",
                        "description": "POST mode: Generated Task code"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "POST mode: Task metadata"
                    }
                },
                "required": ["mode"]
            }
        ),

        # Step 8: Role (PRE+POST)
        Tool(
            name="qg_role",
            description="Step 8 quality gate: Validate Role generation (PRE+POST mode). PRE checks Step 7 complete, POST validates no skeleton.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Validation mode: PRE (before Tool 5) or POST (after Tool 5)",
                        "enum": ["PRE", "POST"]
                    },
                    "task_metadata": {
                        "type": "object",
                        "description": "PRE mode: Task metadata from Step 7"
                    },
                    "code": {
                        "type": "string",
                        "description": "POST mode: Generated Role code"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "POST mode: Role metadata"
                    }
                },
                "required": ["mode"]
            }
        ),

        # Step 9: Test Runner (PRE+POST)
        Tool(
            name="qg_test_runner",
            description="Step 9 quality gate: Validate test code (PRE+POST mode). PRE checks Step 8 complete, POST validates assertions use POM.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Validation mode: PRE (before Tool 6) or POST (after Tool 6)",
                        "enum": ["PRE", "POST"]
                    },
                    "role_metadata": {
                        "type": "object",
                        "description": "PRE mode: Role metadata from Step 8"
                    },
                    "pom_metadata": {
                        "type": "object",
                        "description": "PRE mode: POM metadata from Step 6"
                    },
                    "code": {
                        "type": "string",
                        "description": "POST mode: Generated test code"
                    },
                    "metadata": {
                        "type": "object",
                        "description": "POST mode: Test metadata"
                    }
                },
                "required": ["mode"]
            }
        ),

        # Step 10: Save Run (PRE-only)
        Tool(
            name="qg_save_run",
            description="Step 10 quality gate: Final validation before save (PRE-only). Validates all code present and no skeleton.",
            inputSchema={
                "type": "object",
                "properties": {
                    "mode": {
                        "type": "string",
                        "description": "Validation mode: PRE only",
                        "enum": ["PRE"]
                    },
                    "pom_code": {
                        "type": "string",
                        "description": "Generated POM code"
                    },
                    "task_code": {
                        "type": "string",
                        "description": "Generated Task code"
                    },
                    "role_code": {
                        "type": "string",
                        "description": "Generated Role code"
                    },
                    "test_code": {
                        "type": "string",
                        "description": "Generated test code"
                    }
                },
                "required": ["mode"]
            }
        ),

        # Step 11: Execution (POST-only)
        Tool(
            name="qg_execution",
            description="Step 11 quality gate: Execution validation with HITL triage (POST-only). Validates test execution results and provides diagnostic data for failures.",
            inputSchema={
                "type": "object",
                "properties": {
                    "test_result": {
                        "type": "object",
                        "description": "Test result from run_test operation (status, exit_code, output, duration, failure_data)"
                    },
                    "test_path": {
                        "type": "string",
                        "description": "Test path that was executed"
                    },
                    "workflow": {
                        "type": "string",
                        "description": "Optional workflow/domain name"
                    }
                },
                "required": ["test_result", "test_path"]
            }
        ),

        # Step 11: Workflow Complete (Meta-Gate)
        Tool(
            name="qg_workflow_complete",
            description="Step 11 meta-gate: Workflow completion validation with 8 cross-step consistency checks. Validates 11-step workflow integrity.",
            inputSchema={
                "type": "object",
                "properties": {
                    "workflow_id": {
                        "type": "string",
                        "description": "Workflow identifier from workflow state"
                    },
                    "test_path": {
                        "type": "string",
                        "description": "Test path from Step 11 execution"
                    },
                    "test_result": {
                        "type": "object",
                        "description": "Test result from run_test operation"
                    }
                },
                "required": ["workflow_id", "test_path", "test_result"]
            }
        )
    ]


@server.call_tool()
async def call_tool_handler(name: str, arguments: dict) -> list[TextContent]:
    """Route tool calls to appropriate handler."""

    # Tool routing (matches tool file numbers)
    handlers = {
        # Tools 1-6: Implemented
        "generate_tests_from_user_story": generate_tests_from_user_story,  # Tool 1
        "discover_page_elements": discover_page_elements,                   # Tool 2
        "generate_page_object": generate_page_object,                       # Tool 3
        "generate_task": generate_task,                                     # Tool 4
        "generate_role": generate_role,                                     # Tool 5
        "generate_test_runner": generate_test_runner,                       # Tool 6
        # Tools 7-11: Planned (stubs)
        "list_tests": list_tests,
        "get_framework_structure": get_framework_structure,
        "run_test": run_test,
        "analyze_failure": analyze_failure,
        "get_test_coverage": get_test_coverage,
        # Quality Gates (Steps 1-11)
        "qg_preflight": qg_preflight,                     # Step 1
        "qg_user_input": qg_user_input,                   # Step 2
        "qg_ai_processing": qg_ai_processing,             # Step 3
        "qg_test_scenarios": qg_test_scenarios,           # Step 4
        "qg_discovered_elements": qg_discovered_elements, # Step 5
        "qg_page_object": qg_page_object,                 # Step 6
        "qg_task": qg_task,                               # Step 7
        "qg_role": qg_role,                               # Step 8
        "qg_test_runner": qg_test_runner,                 # Step 9
        "qg_save_run": qg_save_run,                       # Step 10
        "qg_execution": qg_execution,                     # Step 11
        "qg_workflow_complete": qg_workflow_complete,     # Step 11 (meta-gate)
    }

    if name not in handlers:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool '{name}'"
        )]

    try:
        result = await handlers[name](arguments)
        return [TextContent(
            type="text",
            text=result
        )]
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """Start MCP server."""
    from mcp.server.stdio import stdio_server

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
