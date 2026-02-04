#!/usr/bin/env python3
"""
Isagawa QA Public Repo Sync Script
Syncs code from private codebase to public repo.

Usage:
    python setup_public_repo.py --target D:\my_ai_projects\isagawa-qa --dry-run
    python setup_public_repo.py --target D:\my_ai_projects\isagawa-qa
"""

import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# Source directory (current project)
SOURCE_DIR = Path(__file__).parent.parent

# Files/folders to COPY (public-safe)
# IMPORTANT: Use explicit whitelist, NOT broad directories like "framework/"
# Generated workflow artifacts (pages/roles/tasks/tests per workflow) stay private
INCLUDE = [
    # Core framework - production code only
    "framework/interfaces/",       # BrowserInterface
    "framework/resources/",        # Utilities, config, drivers
    "framework/_reference/",       # Canonical 4-layer pattern examples

    # MCP server
    "mcp_server/tools/",
    "mcp_server/utils/",
    "mcp_server/server.py",
    "mcp_server/requirements.txt",
    "mcp_server/__init__.py",

    # Test infrastructure (not generated tests)
    "tests/conftest.py",
    "tests/data/",                 # Shared test data

    # Skills/protocols
    ".claude/skills/qa-management-layer/",
    ".claude/commands/qa-workflow.md",
    ".claude/commands/qa-workflow-dev.md",
    ".claude/commands/run-test.md",
    ".claude/settings.json",

    # Project config
    "requirements.txt",
    "pytest.ini",
    ".gitignore",
    "README.md",
    "FRAMEWORK.md",
]

# Files/folders to EXCLUDE (private - never copy)
EXCLUDE = [
    # Business & internal docs
    ".business/",
    "docs/",
    "SESSION.md",
    "DEFECT_LOG.md",
    "CLAUDE.md",  # Contains internal process

    # Internal skills/config
    ".claude/settings.local.json",
    ".claude/skills/dialogue-engine/",
    ".claude/skills/design-execution-engine/",
    ".claude/skills/fix-workflow/",
    ".claude/commands/intel.md",
    ".claude/commands/cleanup.md",
    ".claude/commands/sync-to-isagawa-qa.md",

    # Dev/internal
    "mcp_server/_dev_tests/",
    "scripts/",
    ".git/",
    "__pycache__/",
    "*.pyc",
    ".env",

    # Generated workflow artifacts (created by QA workflow, stay private)
    # These patterns catch any workflow-specific generated code
    "framework/pages/helios*/",
    "framework/pages/clawdbot/",
    "framework/pages/automationex*/",
    "framework/pages/test*/",
    "framework/pages/workflow*/",
    "framework/pages/parabank*/",
    "framework/roles/helios*/",
    "framework/roles/clawdbot/",
    "framework/roles/automationex*/",
    "framework/roles/test*/",
    "framework/roles/workflow*/",
    "framework/roles/parabank*/",
    "framework/tasks/helios*/",
    "framework/tasks/clawdbot/",
    "framework/tasks/automationex*/",
    "framework/tasks/test*/",
    "framework/tasks/workflow*/",
    "framework/tasks/parabank*/",
    "tests/helios*/",
    "tests/clawdbot/",
    "tests/automationex*/",
    "tests/test*/",
    "tests/workflow*/",
    "tests/parabank*/",
]



def should_exclude(path: Path, source_dir: Path) -> bool:
    """Check if path should be excluded."""
    import fnmatch
    rel_path = str(path.relative_to(source_dir)).replace("\\", "/")

    for pattern in EXCLUDE:
        pattern_clean = pattern.rstrip("/")

        if "*" in pattern:
            # Wildcard pattern - match against full relative path
            if fnmatch.fnmatch(rel_path, pattern_clean):
                return True
            # Also check if path starts with a wildcard directory match
            if "/" in pattern_clean:
                # Pattern like "framework/pages/helios*" should match "framework/pages/helios1/file.py"
                pattern_parts = pattern_clean.split("/")
                path_parts = rel_path.split("/")
                if len(path_parts) >= len(pattern_parts):
                    match = True
                    for i, p_part in enumerate(pattern_parts):
                        if not fnmatch.fnmatch(path_parts[i], p_part):
                            match = False
                            break
                    if match:
                        return True
        elif pattern.endswith("/"):
            # Directory pattern (exact)
            if rel_path.startswith(pattern_clean) or rel_path == pattern_clean:
                return True
        else:
            # Exact match
            if rel_path == pattern_clean or rel_path.startswith(pattern_clean + "/"):
                return True

    return False


def copy_with_filter(src: Path, dst: Path, source_dir: Path, dry_run: bool = False):
    """Copy file/directory, excluding private content."""
    if should_exclude(src, source_dir):
        print(f"  SKIP (excluded): {src.relative_to(source_dir)}")
        return

    if src.is_file():
        if dry_run:
            print(f"  COPY: {src.relative_to(source_dir)} -> {dst}")
        else:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  COPIED: {src.relative_to(source_dir)}")

    elif src.is_dir():
        for item in src.iterdir():
            copy_with_filter(
                item,
                dst / item.name,
                source_dir,
                dry_run
            )


def main():
    parser = argparse.ArgumentParser(description="Sync Isagawa QA to public repo")
    parser.add_argument(
        "--target",
        type=Path,
        required=True,
        help="Target directory (existing public repo)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without doing it"
    )

    args = parser.parse_args()

    target_dir = args.target.resolve()

    print(f"{'DRY RUN - ' if args.dry_run else ''}Isagawa QA Public Repo Sync")
    print(f"=" * 50)
    print(f"Source: {SOURCE_DIR}")
    print(f"Target: {target_dir}")
    print(f"Time: {datetime.now().isoformat()}")
    print()

    # Verify target exists
    if not target_dir.exists():
        print(f"ERROR: Target directory does not exist: {target_dir}")
        print("Clone the public repo first.")
        return 1

    # Copy included files
    print("Syncing files...")
    for pattern in INCLUDE:
        src_path = SOURCE_DIR / pattern.rstrip("/")

        if not src_path.exists():
            print(f"  WARN: Source not found: {pattern}")
            continue

        if pattern.endswith("/"):
            # Directory - remove existing and copy fresh
            dst_path = target_dir / pattern.rstrip("/")
            if dst_path.exists() and not args.dry_run:
                shutil.rmtree(dst_path)
            copy_with_filter(src_path, dst_path, SOURCE_DIR, args.dry_run)
        else:
            # File
            dst_path = target_dir / pattern
            copy_with_filter(src_path, dst_path, SOURCE_DIR, args.dry_run)

    print()
    print("=" * 50)
    print("DONE!" if not args.dry_run else "DRY RUN COMPLETE")
    print()
    print("Next steps:")
    print(f"  1. cd {target_dir}")
    print("  2. git status  # Review changes")
    print("  3. git add -A && git commit -m 'Sync from private repo'")
    print("  4. git push")

    return 0


if __name__ == "__main__":
    exit(main())
