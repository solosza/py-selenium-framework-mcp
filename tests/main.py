"""
Pytest launcher for test execution.

This module provides the main entry point for running tests via pytest.
It configures logging, HTML reporting, and passes custom arguments.
"""

import pytest
import sys
from datetime import datetime as dt
from pathlib import Path

# Add framework to Python path
FRAMEWORK_PATH = str(Path(__file__).parent.parent / "framework")
sys.path.insert(0, FRAMEWORK_PATH)

from resources.utilities.autologger import logger_init


def main(test_path, base_report_name="report", env="DEFAULT", headless=False, report_path="_reports"):
    """
    Launch pytest with configured arguments.

    This function is designed to be called from test executor scripts.

    Args:
        test_path: Path to test file or directory to run
        base_report_name: Base name for HTML report (timestamp will be appended)
        env: Environment ID (default: "DEFAULT")
        headless: Run browser in headless mode (default: False)
        report_path: Directory for reports and logs (default: "_reports")
    """
    # Generate timestamped report name
    report_name = f"{base_report_name}_{dt.now().strftime('%Y%m%d_%H%M%S')}"

    # Create reports directory if it doesn't exist
    reports_dir = Path(test_path).parent / report_path
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Initialize logger with error log file
    logger_init(error_log=str(reports_dir / f"ERROR_LOG_{report_name}.txt"))

    # Launch pytest
    pytest.main(
        args=[
            # Ignore deprecation warnings
            "-W", "ignore::DeprecationWarning",

            # Show output and write to HTML (capture both prints and logging)
            "--capture=tee-sys",

            # Determine pytest rootdir
            f"-c={str(Path(__file__).parent)}",

            # Test path (file or directory)
            str(test_path),

            # Environment
            f"--env={env}",

            # Headless mode
            f"--headless={headless}",

            # HTML report output
            f"--html={reports_dir / report_name}.html",
            "--self-contained-html"
        ]
    )


if __name__ == "__main__":
    # Support direct execution from command line
    import argparse

    parser = argparse.ArgumentParser(description="Run pytest tests")
    parser.add_argument("test_path", help="Path to test file or directory")
    parser.add_argument("--name", default="report", help="Base report name")
    parser.add_argument("--env", default="DEFAULT", help="Environment ID")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--report-path", default="_reports", help="Report directory")

    args = parser.parse_args()

    main(
        test_path=args.test_path,
        base_report_name=args.name,
        env=args.env,
        headless=args.headless,
        report_path=args.report_path
    )
