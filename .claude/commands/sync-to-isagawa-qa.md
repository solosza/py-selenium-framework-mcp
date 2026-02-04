# Sync to Isagawa QA Public Repository (HITL)

Sync code from private codebase to public isagawa-qa repo with human approval.

## Instructions

**Step 1: Dry Run**
Run the sync script in dry-run mode:
```bash
python scripts/setup_public_repo.py --target D:\isagawa_co\isagawa-qa --dry-run
```

**Step 2: Present Results and Ask User**

Show the dry run output, then present options:

```
SYNC PREVIEW COMPLETE

Files to copy: [count]
Files excluded: [count]

HOW SHOULD WE PROCEED?

1. Proceed
   -> Run sync, review changes, commit and push

2. Abort
   -> Cancel sync, no changes made

3. Review excludes
   -> Show excluded files/folders and why

4. Other
   -> Describe what you want to do

Select option (1-4):
```

**Step 3: Handle User Decision**

| Option | Action |
|--------|--------|
| 1. Proceed | Run actual sync, then go to Step 4 |
| 2. Abort | Stop immediately, no changes |
| 3. Review excludes | Show EXCLUDE list from script, return to options |
| 4. Other | Wait for user input, follow their instructions |

**Step 4: Execute Sync (if Proceed)**
```bash
python scripts/setup_public_repo.py --target D:\isagawa_co\isagawa-qa
```

**Step 5: Review and Commit**
```bash
cd D:\isagawa_co\isagawa-qa && git status
```

Show git status, then ask:
```
Changes ready to commit. Provide commit message:
```

**Step 6: Commit and Push**
```bash
git add -A && git commit -m "<user message>" && git push origin main
```

## HITL Checkpoints

- After dry run → User approves file list
- After sync → User reviews git status
- Before commit → User provides commit message
- Before push → User confirms

**Never auto-push without explicit user approval.**
