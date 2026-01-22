# Protocol: Environment Validation (DD-52)

**Version:** 1.0
**Status:** Production
**Owner:** QA Management Layer
**Pattern:** Protocol + Smart Error (Defense-in-Depth Lite)

---

## Overview

Environment validation ensures tests run against the correct target environment using the `--env` flag. This protocol defines validation rules (Layer 1) and smart error handling (Layer 2) without overengineering a full quality gate.

**Why Not Full Gate?**
Environment validation is a pytest-level concern that happens at fixture loading. Smart Error in `conftest.py` catches all errors at the right time. A full quality gate would be overengineering since:
- No tool chain involvement (not part of Steps 1-9)
- Error occurs at pytest startup, not workflow execution
- conftest.py is the natural enforcement point

---

## Architecture: 2 Layers

```
┌──────────────────────────────────────────────────────────────────┐
│ Layer 1: PROTOCOL (Validation Rules)                             │
├──────────────────────────────────────────────────────────────────┤
│ • When to validate                                                │
│ • What to validate                                                │
│ • How to validate                                                 │
└──────────────────────────────────────────────────────────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────────┐
│ Layer 2: SMART ERROR (Teaching Data)                             │
├──────────────────────────────────────────────────────────────────┤
│ • List available environments                                     │
│ • Show --env flag syntax                                          │
│ • Provide example commands                                        │
│ • Point to config location                                        │
└──────────────────────────────────────────────────────────────────┘
```

---

## Layer 1: Protocol (Validation Rules)

### When to Validate

Environment validation occurs at:
1. **Pytest Startup** - conftest.py `config` fixture loads environment
2. **Step 2 (User Input)** - AI detects environment from URL (optional enhancement)

### What to Validate

| Check | Rule | Error If |
|-------|------|----------|
| **env_id exists** | Must be a key in `environment_config.json` | env_id not found |
| **env_id not empty** | Must be non-empty string | Empty or whitespace-only |
| **Config has url** | Environment must have `url` key | Missing url field |

### How to Validate

```python
# conftest.py config fixture (lines 59-79)
def config(request):
    env_id = request.config.getoption("--env")

    # Load environment config
    config_path = Path(...) / "environment_config.json"
    with open(config_path, 'r') as f:
        environments = json.load(f)

    # Validate env_id exists
    if env_id not in environments:
        # Raise Smart Error (Layer 2)
        raise ValueError(error_msg)

    return environments[env_id]
```

---

## Layer 2: Smart Error (Teaching Data)

### Error Message Format

```
╔═══════════════════════════════════════════════════════════════╗
║ Environment Validation Error (DD-52)                          ║
╚═══════════════════════════════════════════════════════════════╝

❌ ERROR: Environment '{env_id}' not found in configuration

📋 AVAILABLE ENVIRONMENTS:
  - parabank11: https://parabank.parasoft.com
  - parabank12: https://parabank.parasoft.com
  - parabank13: https://parabank.parasoft.com
  - automationex1: https://www.automationexercise.com
  - helios1: https://heliosdigital-retail-qa.azurewebsites.net

🔧 HOW TO FIX:
   Use the --env flag to specify a valid environment:

   pytest tests/path/to/test.py --env=<environment_id>

📚 EXAMPLES:
   pytest tests/helios1/test_create_service_inquiry.py --env=helios1
   pytest tests/parabank13/test_open_checking_account.py --env=parabank13
   pytest tests/automationex1/test_registration.py --env=automationex1

📍 CONFIG LOCATION:
   framework/resources/config/environment_config.json

💡 TIP: Add new environments by editing the config file above.
```

### Smart Error Components

| Component | Purpose | Example |
|-----------|---------|---------|
| **❌ ERROR** | What went wrong | "Environment 'DEFAULT' not found" |
| **📋 AVAILABLE** | Show valid options | List all env_ids with URLs |
| **🔧 HOW TO FIX** | Command syntax | `pytest ... --env=<id>` |
| **📚 EXAMPLES** | Concrete examples | Real test paths + env flags |
| **📍 CONFIG** | Where to add more | Path to config file |
| **💡 TIP** | Next action | "Edit config to add environments" |

---

## Step 2 Integration (Optional Enhancement)

AI can auto-detect environment from URL during Step 2 (User Input).

### Detection Logic

```python
# qg_user_input.py - _detect_environment() helper
def _detect_environment(url: str, config_path: Path) -> str:
    """
    Match URL against environment_config.json.

    Args:
        url: Target page URL from user
        config_path: Path to environment_config.json

    Returns:
        env_id if match found, "DEFAULT" otherwise
    """
    with open(config_path) as f:
        environments = json.load(f)

    # Match URL host against environment URLs
    from urllib.parse import urlparse
    target_host = urlparse(url).netloc

    for env_id, config in environments.items():
        env_host = urlparse(config['url']).netloc
        if target_host == env_host:
            return env_id

    return "DEFAULT"  # No match
```

### Integration Points

1. **Step 2 PRE Validation** - AI detects environment from URL
2. **Save to State** - `step_2.env_id = detected_env_id`
3. **Step 11 Execution** - Pass env_id to `run_test` tool: `pytest ... --env={env_id}`

---

## Usage Examples

### Example 1: Invalid Environment (User Error)

```bash
$ pytest tests/helios1/test_create_service_inquiry.py --env=invalid

╔═══════════════════════════════════════════════════════════════╗
║ Environment Validation Error (DD-52)                          ║
╚═══════════════════════════════════════════════════════════════╝

❌ ERROR: Environment 'invalid' not found in configuration
...
```

**User Action:** Copy example command with correct env_id

### Example 2: Missing --env Flag (Defaults to "DEFAULT")

```bash
$ pytest tests/helios1/test_create_service_inquiry.py

╔═══════════════════════════════════════════════════════════════╗
║ Environment Validation Error (DD-52)                          ║
╚═══════════════════════════════════════════════════════════════╝

❌ ERROR: Environment 'DEFAULT' not found in configuration
...
```

**User Action:** Add `--env=helios1` flag

### Example 3: Valid Environment (Success)

```bash
$ pytest tests/helios1/test_create_service_inquiry.py --env=helios1
============================= 1 passed in 21.43s ==============================
```

---

## Benefits

| Benefit | Description |
|---------|-------------|
| **Self-Teaching** | Error message teaches user how to fix |
| **Context-Aware** | Shows available environments dynamically |
| **Example-Driven** | Provides copy-paste ready commands |
| **Proportional** | Right amount of engineering (no overengineering) |
| **Defense-in-Depth** | Validates at pytest level (natural boundary) |

---

## Comparison: Full Gate vs Smart Error

| Aspect | Full Gate | Smart Error (This Protocol) |
|--------|-----------|----------------------------|
| **Complexity** | High (new gate, tool chain integration) | Low (conftest.py enhancement) |
| **When Validates** | During workflow (Step 2) | At pytest startup (fixture load) |
| **Error Location** | Quality gate failure | Pytest fixture error |
| **Overhead** | Tool chain state tracking | None (pytest native) |
| **Maintenance** | Gate + tests + state management | Single conftest.py block |
| **User Experience** | Same (helpful error message) | Same (helpful error message) |

**Conclusion:** Smart Error provides 90% of the value with 10% of the complexity.

---

## Related Design Decisions

- **DD-50:** Smart Gate Pattern (validate AND teach)
- **DD-52:** Environment Validation (this protocol)
- **Step 2:** User Input validation and metadata extraction

---

## Maintenance

**To Add New Environment:**

1. Edit `framework/resources/config/environment_config.json`
2. Add entry: `"new_env": {"url": "https://example.com"}`
3. Error message automatically includes new environment

**To Update Error Message:**

1. Edit `tests/conftest.py` lines 76-104
2. Modify error_msg string
3. No code changes needed elsewhere

---

**End of Protocol**
