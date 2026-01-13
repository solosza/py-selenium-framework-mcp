"""Fix ParaBank POMs by adding navigate() methods and correcting import paths."""
import sys
import os
import json
sys.path.insert(0, 'D:/my_ai_projects/py_sel_framework_mcp/mcp_server')

from utils.state_manager import StateManager

# POM-specific navigate configurations
POM_NAV_CONFIG = {
    "LoginPage": {
        "url_path": "/parabank/index.htm",
        "import_path": "pages.parabank.login_page"
    },
    "OpenAccountPage": {
        "url_path": "/parabank/openaccount.htm",
        "import_path": "pages.parabank.open_account_page"
    },
    "TransferFundsPage": {
        "url_path": "/parabank/transfer.htm",
        "import_path": "pages.parabank.transfer_funds_page"
    },
    "AccountActivityPage": {
        "url_path": "/parabank/activity.htm",
        "import_path": "pages.parabank.account_activity_page"
    }
}

def add_navigate_method(code: str, class_name: str, url_path: str) -> str:
    """Add navigate() method to POM code."""
    navigate_method = f'''
    def navigate(self) -> "{class_name}":
        """Navigate to {class_name.replace('Page', ' page')}."""
        self.web.navigate_to(self.web.config['url'] + '{url_path}')
        return self
'''

    # Find insertion point (after __init__ method, before LOCATORS section)
    # Try both marker formats
    insert_marker_long = "# ==================== LOCATORS (Class Constants) ===================="
    insert_marker_short = "    # Locators"

    if insert_marker_long in code:
        code = code.replace(
            insert_marker_long,
            f"{navigate_method}\n    {insert_marker_long}"
        )
    elif insert_marker_short in code:
        code = code.replace(
            insert_marker_short,
            f"{navigate_method}\n{insert_marker_short}"
        )
    else:
        print(f"WARNING: Could not find insertion point for {class_name}")

    return code

def update_metadata(metadata: dict, import_path: str) -> dict:
    """Update metadata with navigate() method and correct import_path."""
    # Fix import_path
    metadata['import_path'] = import_path

    # Add navigate to action_methods if not present
    action_methods = metadata.get('action_methods', [])
    action_method_names = [m.get('name') for m in action_methods]

    if 'navigate' not in action_method_names:
        action_methods.insert(0, {
            'name': 'navigate',
            'params': [],
            'returns': metadata['class_name']
        })
        metadata['action_methods'] = action_methods

    return metadata

# Load state
sm = StateManager()
step6 = sm.get_step(6)
poms = step6['generated_poms']

# Fix each POM
fixed_poms = {}
for pom_name, pom_data in poms.items():
    print(f"\nFixing {pom_name}...")

    config = POM_NAV_CONFIG.get(pom_name)
    if not config:
        print(f"  WARNING: No config for {pom_name}, skipping")
        continue

    # Get original data
    code = pom_data['code']
    metadata = pom_data['metadata']

    # Add navigate() method
    fixed_code = add_navigate_method(code, pom_name, config['url_path'])

    # Update metadata
    fixed_metadata = update_metadata(metadata, config['import_path'])

    fixed_poms[pom_name] = {
        'code': fixed_code,
        'metadata': fixed_metadata
    }

    print(f"  [OK] Added navigate() method")
    print(f"  [OK] Fixed import_path: {fixed_metadata['import_path']}")

# Update state with fixed POMs
step6['generated_poms'] = fixed_poms
sm.save(6, step6)

print("\n" + "=" * 80)
print("State updated successfully!")
print("=" * 80)
print(f"Fixed {len(fixed_poms)} POMs")
for pom_name in fixed_poms.keys():
    print(f"  - {pom_name}")
