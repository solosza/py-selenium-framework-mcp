# Cleanup Test Workflows

Delete all generated test workflows and their associated framework modules.

## Instructions

1. **Scan directories to identify generated content:**
   - `tests/` - Find all workflow directories (exclude: conftest.py, __pycache__, _audit, _reports, _state, data)
   - `framework/pages/` - Find all page object directories (exclude: _reference, __pycache__)
   - `framework/tasks/` - Find all task directories (exclude: _reference, __pycache__)
   - `framework/roles/` - Find all role directories (exclude: _reference, __pycache__)

2. **DO NOT DELETE (infrastructure):**
   - `tests/conftest.py`
   - `tests/_audit/`
   - `tests/_reports/`
   - `tests/_state/`
   - `tests/data/`
   - `framework/_reference/`
   - Any `__pycache__/` directories
   - Any `__init__.py` files in root framework directories

3. **Execution steps:**
   a. List all directories that will be deleted
   b. Show the user what will be removed
   c. Delete the identified directories
   d. Verify deletion was successful

4. **Report format:**
   ```
   CLEANUP COMPLETE
   ================
   Deleted:
   - tests: [list of deleted workflow directories]
   - pages: [list of deleted page modules]
   - tasks: [list of deleted task modules]
   - roles: [list of deleted role modules]

   Preserved:
   - Infrastructure files intact
   ```

ARGUMENTS: $ARGUMENTS
