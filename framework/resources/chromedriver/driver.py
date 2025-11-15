"""
WebDriver Factory - Creates and configures ChromeDriver instances.

Handles driver initialization with appropriate options (headless, window size, etc.).
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


def create_driver(headless=False, window_size="1920x1080"):
    """
    Create and configure a ChromeDriver instance.

    Args:
        headless: Run browser in headless mode (default: False)
        window_size: Browser window size as "WIDTHxHEIGHT" (default: "1920x1080")

    Returns:
        WebDriver: Configured ChromeDriver instance
    """
    # Configure Chrome options
    chrome_options = Options()

    # Headless mode
    if headless:
        chrome_options.add_argument("--headless=new")  # Use new headless mode
        chrome_options.add_argument("--disable-gpu")

    # Window size
    chrome_options.add_argument(f"--window-size={window_size}")

    # Performance and stability options
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Suppress logging
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

    # Create driver using WebDriver Manager (auto-downloads correct chromedriver)
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Set implicit wait
    driver.implicitly_wait(10)

    # Maximize window if not headless
    if not headless:
        driver.maximize_window()

    return driver
