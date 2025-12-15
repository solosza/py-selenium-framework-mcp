"""
Test runner with organized reports.

Generates reports in timestamped subfolders:
  YYYY-MM-DD_HHMMSS/
    ├── report.html          (pytest results)
    ├── coverage/            (detailed coverage HTML)
    └── coverage_summary.txt (terminal output backup)

Usage:
    python run_tests.py                              # Run all tests
    python run_tests.py test_loader.py               # Run specific test file
    python run_tests.py test_chunker.py::TestChunk   # Run specific test class
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_tests(test_target: str = ""):
    """Run tests with coverage and generate organized reports."""

    # Paths relative to this script's location (tests/_reports folder)
    script_dir = Path(__file__).parent.resolve()
    tests_dir = script_dir.parent  # tests/
    training_assistant_dir = tests_dir.parent  # training-assistant/

    # Test path
    if test_target:
        # Check if it's a path or just a filename
        if "/" in test_target or "\\" in test_target:
            test_path = tests_dir / test_target
        else:
            # Assume it's in ingestion/ subfolder for now
            test_path = tests_dir / "ingestion" / test_target
    else:
        test_path = tests_dir

    # Create timestamped subfolder for this run
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    report_dir = script_dir / timestamp
    report_dir.mkdir(parents=True, exist_ok=True)

    print(f"Report directory: {report_dir}")
    print("=" * 60)

    # Build command
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_path),
        "-v",
        "--cov=rag",
        "--cov-report=term-missing",
        f"--cov-report=html:{report_dir}/coverage",
        f"--html={report_dir}/report.html",
        "--self-contained-html",
    ]

    # Run from training-assistant directory so imports work
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=training_assistant_dir
    )

    # Print to console
    print(result.stdout)
    if result.stderr:
        print(result.stderr)

    # Save terminal output (includes coverage)
    with open(report_dir / "coverage_summary.txt", "w") as f:
        f.write(result.stdout)
        if result.stderr:
            f.write("\n--- STDERR ---\n")
            f.write(result.stderr)

    # Extract coverage percentage
    coverage_line = ""
    for line in result.stdout.split("\n"):
        if "TOTAL" in line and "%" in line:
            coverage_line = line.strip()
            break

    print("=" * 60)
    print(f"Reports saved to: {report_dir}")
    print(f"  - Test results: report.html")
    print(f"  - Coverage HTML: coverage/index.html")
    print(f"  - Coverage text: coverage_summary.txt")
    if coverage_line:
        print(f"\nCoverage: {coverage_line}")

    return result.returncode


if __name__ == "__main__":
    # Allow custom test target from command line
    test_target = sys.argv[1] if len(sys.argv) > 1 else ""
    exit_code = run_tests(test_target)
    sys.exit(exit_code)
