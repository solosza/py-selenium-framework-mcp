# Development Test Scripts

This folder contains helper scripts used during MCP tool development and testing.

## Test Scripts

### Comprehensive Tests
- **test_complete_generation.py** - Tests the full workflow chain (Tool 1 → 5 → 6 → 4 → 3 → 2)
  - Verifies each tool generates complete code vs scaffolding
  - Creates output files for visual inspection
  - Used during refactoring to verify Tools 4, 5, 6 generate complete implementations

### Individual Tool Chain Tests
- **test_tools_5_6_chain.py** - Tests Tool 5 (discover) → Tool 6 (generate POM)
- **test_complete_workflow.py** - End-to-end workflow validation
- **test_workflow_detailed_output.py** - Detailed output analysis

## Output Files (Archive)
- **_output_tool4_task.py** - Sample Task output (before fix)
- **_correct_tool4_output.py** - Sample Task output (after fix)

## Usage

These scripts are for development only. They are NOT part of the MCP server runtime.

To run a test:
```bash
cd mcp_server/_dev_tests
python -u test_complete_generation.py
```

## Notes
- Output files are generated in `examples/generated_demo/` for proper organization
- These tests helped verify the refactoring from scaffolding → complete code generation
