"""Save ParaBank Task and Role from state to disk."""
import sys
import os
sys.path.insert(0, 'D:/my_ai_projects/py_sel_framework_mcp/mcp_server')

from utils.state_manager import StateManager

# Load state
sm = StateManager()
step7 = sm.get_step(7)
step8 = sm.get_step(8)

# Base directories
tasks_dir = "D:/my_ai_projects/py_sel_framework_mcp/framework/tasks/parabank"
roles_dir = "D:/my_ai_projects/py_sel_framework_mcp/framework/roles/parabank"

# Create directories
os.makedirs(tasks_dir, exist_ok=True)
os.makedirs(roles_dir, exist_ok=True)

print("=" * 80)
print("Saving ParaBank Task and Role from state...")
print("=" * 80)

# Save Task
if step7 and 'task_code' in step7:
    task_code = step7['task_code']
    task_file = os.path.join(tasks_dir, "parabank_tasks.py")

    print(f"\nSaving ParabankTasks to {task_file}...")
    with open(task_file, 'w', encoding='utf-8') as f:
        f.write(task_code)
    print(f"  [OK] Saved: {task_file}")

    # Create __init__.py for tasks
    init_file = os.path.join(tasks_dir, "__init__.py")
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write("# ParaBank task workflows\n")
    print(f"  [OK] Created __init__.py")
else:
    print("\nWARNING: Task code not found in state")

# Save Role
if step8 and 'role_code' in step8:
    role_code = step8['role_code']
    role_file = os.path.join(roles_dir, "existing_customer.py")

    print(f"\nSaving ExistingCustomer to {role_file}...")
    with open(role_file, 'w', encoding='utf-8') as f:
        f.write(role_code)
    print(f"  [OK] Saved: {role_file}")

    # Create __init__.py for roles
    init_file = os.path.join(roles_dir, "__init__.py")
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write("# ParaBank role classes\n")
    print(f"  [OK] Created __init__.py")
else:
    print("\nWARNING: Role code not found in state")

print("\n" + "=" * 80)
print("Task and Role saved successfully!")
print("=" * 80)
