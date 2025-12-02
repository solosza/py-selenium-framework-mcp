# Test Validation Utilities

Automated validation tools that check if Python code follows the FRAMEWORK.md 4-layer architecture patterns.

## Description

The pattern validator uses Python's AST (Abstract Syntax Tree) to parse source files and verify they conform to the framework's architectural rules. This catches violations early - before code review or runtime.

## Validation Rules

Each layer has specific patterns that are enforced:

### Page Objects (`/pages/`)
| Rule | Check |
|------|-------|
| No decorators | Methods must NOT have `@autologger` or other decorators |
| Returns self | Action methods must return `self` for fluent chaining |
| Locator constants | Locators defined as UPPER_SNAKE class constants |
| State-check methods | Must have `is_*`, `has_*`, or `get_*` methods for assertions |

### Tasks (`/tasks/`)
| Rule | Check |
|------|-------|
| Has decorator | Workflow methods must have `@autologger.automation_logger("Task")` |
| Constructor clean | `__init__` must NOT have decorator |
| Returns None | Methods must not return values (tests assert via POM) |
| No locators | No `By.*` locators (delegate to Page Objects) |

### Roles (`/roles/`)
| Rule | Check |
|------|-------|
| Constructor decorator | `__init__` should have `@autologger("Role Constructor")` |
| Workflow decorator | Methods must have `@autologger.automation_logger("Role")` |
| Returns None | Methods must not return values |
| Composition | Should compose Tasks, not inherit from base classes |

### Tests (`/tests/`)
| Rule | Check |
|------|-------|
| Has decorator | Test methods must have `@autologger.automation_logger("Test")` |
| Pytest marker | Must have `@pytest.mark.<category>` |
| POM assertions | Should assert via POM state-check methods, not return values |

## Usage

### CLI - Validate Existing Code

```bash
# Validate a single file
python pattern_validator.py ../framework/pages/auth/login_page.py

# Validate entire directory
python pattern_validator.py ../framework/pages/

# Validate with verbose warnings
python pattern_validator.py ../framework/tasks/ -v

# Force layer type detection
python pattern_validator.py some_file.py --layer task
```

### Pytest - Validate Generator Output

```bash
# Run all validation tests
cd mcp_server
python -m pytest utils/test_validation/pattern_validator.py -v

# Run specific layer tests
python -m pytest utils/test_validation/pattern_validator.py -v -k "page"
python -m pytest utils/test_validation/pattern_validator.py -v -k "task"
python -m pytest utils/test_validation/pattern_validator.py -v -k "role"
python -m pytest utils/test_validation/pattern_validator.py -v -k "test"
```

### Python API

```python
from utils.test_validation import validate_file, validate_directory

# Validate single file
result = validate_file("framework/pages/auth/login_page.py")
print(f"Valid: {result['valid']}")
print(f"Errors: {result['errors']}")
print(f"Warnings: {result['warnings']}")

# Validate directory
results = validate_directory("framework/tasks/")
for r in results:
    if r['errors']:
        print(f"{r['file']}: {r['errors']}")
```

## Use Cases

### 1. Pre-Commit Validation
Run before committing to catch violations early:
```bash
python mcp_server/utils/test_validation/pattern_validator.py framework/ -v
```

### 2. CI/CD Pipeline
Add to GitHub Actions or similar:
```yaml
- name: Validate Framework Patterns
  run: python mcp_server/utils/test_validation/pattern_validator.py framework/
```

### 3. Code Review Automation
Validate changed files in a PR:
```bash
git diff --name-only HEAD~1 | grep "\.py$" | xargs python pattern_validator.py
```

### 4. Generator Testing
Verify code generators produce compliant output:
```bash
python -m pytest utils/test_validation/pattern_validator.py -v
```

### 5. Architecture Audit
Find all violations in the codebase:
```bash
python pattern_validator.py framework/ -v 2>&1 | grep "ERROR"
```

## Output Format

### Success
```
============================================================
SUMMARY: 6 files checked
  Errors: 0
  Warnings: 2

All validations PASSED!
```

### Failure
```
============================================================
File: ../framework/tasks/catalog/catalog_tasks.py
Layer: task
Valid: NO

ERRORS:
  - Task method 'get_product_count' should return None
  - Task method 'get_product_names' should return None

============================================================
SUMMARY: 2 files checked
  Errors: 2
  Warnings: 0

Validation FAILED with 2 errors
```

## Extending

To add new validation rules, edit `pattern_validator.py`:

1. Add helper function for the check (e.g., `has_type_hints()`)
2. Add the check to the appropriate `validate_*` function
3. Add a test case in the `Test*Validation` class

## Related Files

- `FRAMEWORK.md` - Authoritative architecture documentation
- `mcp_server/utils/generators/` - Code generators that produce compliant code
- `mcp_server/_dev_tests/test_generators.py` - Generator unit tests
