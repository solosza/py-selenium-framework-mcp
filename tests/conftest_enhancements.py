"""
HTML Report Enhancement Options for conftest.py

Add these hooks to conftest.py to enhance pytest-html reports.
Pick and choose which enhancements you want.
"""

import pytest
from datetime import datetime
from py.xml import html


# ==============================================================================
# ENHANCEMENT 1: Screenshots on Failure
# ==============================================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """
    Capture screenshot on test failure and attach to HTML report.

    Benefits:
    - Visual debugging of failure state
    - See exactly what was on screen when test failed
    - Embedded in HTML report (no external files)

    Cost: Increases report file size
    """
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extras', [])

    # Only capture screenshot on test failure
    if report.when == 'call' and report.failed:
        # Get WebInterface fixture from test
        if 'web_interface' in item.funcargs:
            web = item.funcargs['web_interface']

            # Take screenshot
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            screenshot_name = f"{item.name}_{timestamp}"
            screenshot_path = web.take_screenshot(screenshot_name)

            # Attach to report as base64 embedded image
            if screenshot_path:
                with open(screenshot_path, 'rb') as f:
                    screenshot_bytes = f.read()
                    # Embed screenshot in HTML
                    extra.append(pytest_html.extras.image(screenshot_bytes))
                    # Also add as collapsible HTML
                    extra.append(pytest_html.extras.html(
                        f'<div><strong>Screenshot:</strong> {screenshot_name}.png</div>'
                    ))

    report.extras = extra


# ==============================================================================
# ENHANCEMENT 2: Custom Test Metadata
# ==============================================================================

def pytest_html_results_table_header(cells):
    """
    Add custom columns to HTML report table.

    Options shown:
    - Test Duration (already included by default)
    - Browser Used
    - Test Data Used
    """
    cells.insert(2, html.th('Duration', class_='sortable time', col='time'))
    cells.insert(3, html.th('Browser'))
    cells.insert(4, html.th('Test Data'))


def pytest_html_results_table_row(report, cells):
    """
    Populate custom columns with data.
    """
    # Duration (pytest already provides this, but we can format it)
    cells.insert(2, html.td(f"{report.duration:.2f}s", class_='col-time'))

    # Browser info (from config)
    browser = getattr(report, 'browser', 'Chrome')
    cells.insert(3, html.td(browser))

    # Test data used (from test)
    test_data = getattr(report, 'test_data', 'N/A')
    cells.insert(4, html.td(test_data))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport_with_metadata(item, call):
    """
    Attach custom metadata to test report.
    """
    outcome = yield
    report = outcome.get_result()

    # Add browser info
    report.browser = "Chrome (headless)" if item.config.getoption('--headless') == 'true' else "Chrome"

    # Add test data info (if test uses test_users fixture)
    if 'test_users' in item.funcargs:
        test_users = item.funcargs['test_users']
        # Extract which user was used (hacky but works)
        report.test_data = "Registered User 1"


# ==============================================================================
# ENHANCEMENT 3: Test Environment Summary
# ==============================================================================

def pytest_html_report_title(report):
    """
    Customize HTML report title.
    """
    report.title = "Automation Practice - Authentication Test Report"


def pytest_configure(config):
    """
    Add custom metadata to report header.

    Shows:
    - Test environment
    - Execution time
    - Test executor
    - Python/Pytest versions
    """
    config._metadata['Project'] = 'Automation Practice Test Framework'
    config._metadata['Test Suite'] = 'Authentication Tests'
    config._metadata['Environment'] = config.getoption('--env')
    config._metadata['Headless'] = config.getoption('--headless')
    config._metadata['Base URL'] = 'http://www.automationpractice.pl'
    config._metadata['Test Executor'] = 'Selenium WebDriver'
    config._metadata['Report Generated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# ==============================================================================
# ENHANCEMENT 4: Custom CSS Styling
# ==============================================================================

def pytest_html_results_summary(prefix, summary, postfix):
    """
    Add custom summary content after test results.

    Can add:
    - Pass/fail breakdown
    - Links to documentation
    - Known issues
    """
    prefix.extend([
        html.h2("Test Summary"),
        html.p("Authentication test suite for e-commerce application.")
    ])


@pytest.hookimpl(optionalhook=True)
def pytest_html_results_table_html(report, data):
    """
    Add extra HTML content to each test result row (collapsible).

    Can show:
    - Captured logs
    - Request/response data
    - Execution timeline
    """
    if report.passed:
        del data[:]  # Clear default data
        data.append(html.div('Test passed successfully', class_='empty log'))


# ==============================================================================
# ENHANCEMENT 5: Execution Timeline/Performance
# ==============================================================================

# Store test start times
test_start_times = {}

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Record test start time."""
    test_start_times[item.nodeid] = datetime.now()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport_with_timeline(item, call):
    """Add execution timeline info."""
    outcome = yield
    report = outcome.get_result()

    if item.nodeid in test_start_times:
        start_time = test_start_times[item.nodeid]
        end_time = datetime.now()
        report.start_time = start_time.strftime('%H:%M:%S')
        report.end_time = end_time.strftime('%H:%M:%S')
        report.duration_readable = f"{(end_time - start_time).total_seconds():.2f}s"


# ==============================================================================
# ENHANCEMENT 6: Rerun Failed Tests Link
# ==============================================================================

def pytest_sessionfinish(session, exitstatus):
    """
    Generate command to rerun failed tests.
    """
    if exitstatus != 0:
        failed_tests = []
        for item in session.items:
            if hasattr(item, 'result') and item.result.failed:
                failed_tests.append(item.nodeid)

        if failed_tests:
            rerun_cmd = f"pytest {' '.join(failed_tests)}"
            print(f"\n\n{'='*70}")
            print("TO RERUN FAILED TESTS:")
            print(rerun_cmd)
            print(f"{'='*70}\n")


# ==============================================================================
# ENHANCEMENT 7: Custom Markers Summary
# ==============================================================================

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """
    Add custom summary section at end of test run.

    Shows:
    - Tests by marker (@smoke, @regression)
    - Slowest tests
    - Custom statistics
    """
    smoke_tests = []
    regression_tests = []

    for report in terminalreporter.stats.get('passed', []) + terminalreporter.stats.get('failed', []):
        if hasattr(report, 'keywords'):
            if 'smoke' in report.keywords:
                smoke_tests.append(report.nodeid)
            if 'regression' in report.keywords:
                regression_tests.append(report.nodeid)

    terminalreporter.write_sep("=", "Test Breakdown by Marker")
    terminalreporter.write_line(f"@smoke tests: {len(smoke_tests)}")
    terminalreporter.write_line(f"@regression tests: {len(regression_tests)}")
