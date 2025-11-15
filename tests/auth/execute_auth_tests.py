"""
Authentication Test Suite Executor.

Entry point for running authentication tests (login, logout, registration).
"""

from pathlib import Path
import sys

# Add tests directory to path
sys.path.append(str(Path(__file__).parent.parent))
import main


if __name__ == "__main__":
    main.main(
        test_path=Path(__file__).parent,  # Run all tests in auth/ folder
        base_report_name="auth_tests",
        env="DEFAULT",
        headless=False,
        report_path="./_reports"
    )
