# MCP Tool Order - Bottom-Up Workflow

## Correct Sequential Order (1→6)

**Tool 1: generate_tests_from_user_story**
- Input: User story (plain text)
- Output: Test scenarios (Given-When-Then)
- Next: Tool 2

**Tool 2: discover_page_elements** (was Tool 5)
- Input: Page URL
- Output: Discovered elements (locators, types)
- Next: Tool 3

**Tool 3: generate_page_object** (was Tool 6)
- Input: Discovered elements from Tool 2
- Output: Complete POM with methods
- Next: Tool 4

**Tool 4: generate_task** (unchanged)
- Input: POM code from Tool 3
- Output: Complete Task workflows
- Next: Tool 5

**Tool 5: generate_role** (was Tool 3)
- Input: Task methods from Tool 4
- Output: Complete Role class
- Next: Tool 6

**Tool 6: generate_test_template** (was Tool 2)
- Input: All components (Tool 1-5) + scenario
- Output: Complete test with real logic
- Next: Run the test!

## Workflow Philosophy: BOTTOM-UP

Build infrastructure FIRST, then write tests:
1. Parse requirements
2. Discover what exists on the page
3. Build Page Objects
4. Build Task workflows
5. Build Role classes
6. Generate complete, executable test

This is the OPPOSITE of TDD (test-first), but produces the SAME result: complete, working code.

## Changes Made

| Old Number | Old Name | New Number | New Name |
|------------|----------|------------|----------|
| Tool 2 | generate_test_template | Tool 6 | generate_test_template |
| Tool 3 | generate_role | Tool 5 | generate_role |
| Tool 5 | discover_page_elements | Tool 2 | discover_page_elements |
| Tool 6 | generate_page_object | Tool 3 | generate_page_object |

Tools 1, 4, 7-11 remained unchanged.
