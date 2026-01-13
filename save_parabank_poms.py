"""Save fixed ParaBank POMs from state to disk."""
import sys
import os
sys.path.insert(0, 'D:/my_ai_projects/py_sel_framework_mcp/mcp_server')

from utils.state_manager import StateManager

# File name mapping
POM_FILES = {
    "LoginPage": "login_page.py",
    "OpenAccountPage": "open_account_page.py",
    "TransferFundsPage": "transfer_funds_page.py",
    "AccountActivityPage": "account_activity_page.py"
}

# Load state
sm = StateManager()
step6 = sm.get_step(6)
poms = step6['generated_poms']

# Base directory
base_dir = "D:/my_ai_projects/py_sel_framework_mcp/framework/pages/parabank"

# Save each POM
for pom_name, file_name in POM_FILES.items():
    pom_data = poms.get(pom_name)
    if not pom_data:
        print(f"WARNING: {pom_name} not found in state")
        continue

    code = pom_data['code']
    file_path = os.path.join(base_dir, file_name)

    print(f"Saving {pom_name} to {file_name}...")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(code)

    print(f"  [OK] Saved: {file_path}")

# Create __init__.py
init_file = os.path.join(base_dir, "__init__.py")
with open(init_file, 'w', encoding='utf-8') as f:
    f.write("# ParaBank page objects\n")

print(f"\n[OK] Created __init__.py")

print("\n" + "=" * 80)
print("All POMs saved successfully!")
print("=" * 80)
print(f"Saved {len(POM_FILES)} POMs to {base_dir}")
