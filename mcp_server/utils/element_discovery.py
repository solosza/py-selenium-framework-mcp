"""
Element Discovery Utility

Selenium-based page inspection to discover interactive elements.
Used by Tool 5 (discover_page_elements) for just-in-time POM generation.
"""

from typing import Dict, List, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ElementDiscovery:
    """Discover interactive elements on a web page using Selenium."""

    # Interactive element selectors
    INTERACTIVE_SELECTORS = {
        "buttons": "button, input[type='button'], input[type='submit'], input[type='reset']",
        "links": "a[href]",
        "inputs": "input[type='text'], input[type='password'], input[type='email'], input[type='search'], input[type='tel'], input[type='url']",
        "checkboxes": "input[type='checkbox']",
        "radios": "input[type='radio']",
        "selects": "select",
        "textareas": "textarea",
        "images": "img[src]",
    }

    def __init__(self, driver: webdriver.Chrome):
        """
        Initialize ElementDiscovery.

        Args:
            driver: Selenium WebDriver instance
        """
        self.driver = driver

    def discover_elements(self, url: str, wait_seconds: int = 10) -> List[Dict[str, str]]:
        """
        Navigate to URL and discover interactive elements.

        Args:
            url: Page URL to inspect
            wait_seconds: Seconds to wait for page load

        Returns:
            List of discovered element dictionaries
        """
        # Navigate to page
        self.driver.get(url)

        # Wait for page to load
        WebDriverWait(self.driver, wait_seconds).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Discover all interactive elements
        discovered = []

        for element_type, selector in self.INTERACTIVE_SELECTORS.items():
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)

            for index, element in enumerate(elements):
                try:
                    element_data = self._extract_element_data(element, element_type, index)
                    if element_data:
                        discovered.append(element_data)
                except Exception as e:
                    # Skip elements that can't be inspected
                    continue

        return discovered

    def _extract_element_data(self, element: WebElement, element_type: str, index: int) -> Optional[Dict[str, str]]:
        """
        Extract data from a web element.

        Args:
            element: Selenium WebElement
            element_type: Type category (buttons, links, inputs, etc.)
            index: Element index within type

        Returns:
            Dictionary with element data or None if element invalid
        """
        try:
            # Skip hidden elements
            if not element.is_displayed():
                return None

            # Extract attributes
            tag_name = element.tag_name
            element_id = element.get_attribute("id") or ""
            element_class = element.get_attribute("class") or ""
            element_name = element.get_attribute("name") or ""
            element_text = element.text.strip() or element.get_attribute("value") or ""
            element_placeholder = element.get_attribute("placeholder") or ""
            element_type_attr = element.get_attribute("type") or ""
            href = element.get_attribute("href") or ""
            src = element.get_attribute("src") or ""

            # Generate suggested name
            suggested_name = self._generate_element_name(
                element_type,
                element_id,
                element_name,
                element_text,
                element_placeholder,
                index
            )

            # Generate locator strategies
            locators = self._generate_locators(
                tag_name,
                element_id,
                element_class,
                element_name,
                element_text,
                element_type_attr
            )

            return {
                "suggested_name": suggested_name,
                "element_type": element_type,
                "tag_name": tag_name,
                "type_attr": element_type_attr,
                "id": element_id,
                "class": element_class,
                "name": element_name,
                "text": element_text,
                "placeholder": element_placeholder,
                "href": href,
                "src": src,
                "locator_id": locators.get("id", ""),
                "locator_css": locators.get("css", ""),
                "locator_xpath": locators.get("xpath", ""),
                "visible": "Yes"
            }

        except Exception as e:
            return None

    def _generate_element_name(
        self,
        element_type: str,
        element_id: str,
        element_name: str,
        element_text: str,
        placeholder: str,
        index: int
    ) -> str:
        """
        Generate suggested variable name for element.

        Args:
            element_type: Type category
            element_id: Element ID attribute
            element_name: Element name attribute
            element_text: Element text content
            placeholder: Placeholder text
            index: Element index

        Returns:
            Suggested variable name (e.g., LOGIN_BUTTON)
        """
        # Priority order for naming
        name_source = element_id or element_name or element_text or placeholder or f"{element_type}_{index}"

        # Clean and format name
        name = name_source.strip()
        name = name.replace("-", "_").replace(" ", "_").replace(".", "_")
        name = "".join(c for c in name if c.isalnum() or c == "_")
        name = name.upper()

        # Limit length
        if len(name) > 40:
            name = name[:40]

        return name

    def _generate_locators(
        self,
        tag_name: str,
        element_id: str,
        element_class: str,
        element_name: str,
        element_text: str,
        element_type: str
    ) -> Dict[str, str]:
        """
        Generate locator strategies for element.

        Args:
            tag_name: HTML tag name
            element_id: ID attribute
            element_class: Class attribute
            element_name: Name attribute
            element_text: Text content
            element_type: Type attribute

        Returns:
            Dictionary with locator strategies
        """
        locators = {}

        # ID locator (highest priority)
        if element_id:
            locators["id"] = f"#{element_id}"
            locators["xpath"] = f"//{tag_name}[@id='{element_id}']"

        # Name locator
        elif element_name:
            locators["css"] = f"{tag_name}[name='{element_name}']"
            locators["xpath"] = f"//{tag_name}[@name='{element_name}']"

        # Class locator
        elif element_class:
            # Use first class only
            first_class = element_class.split()[0] if element_class else ""
            if first_class:
                locators["css"] = f"{tag_name}.{first_class}"
                locators["xpath"] = f"//{tag_name}[contains(@class, '{first_class}')]"

        # Type locator (for inputs)
        elif element_type:
            locators["css"] = f"{tag_name}[type='{element_type}']"
            locators["xpath"] = f"//{tag_name}[@type='{element_type}']"

        # Text locator (for links/buttons)
        elif element_text:
            locators["xpath"] = f"//{tag_name}[contains(text(), '{element_text[:20]}')]"

        # Fallback to tag name
        else:
            locators["css"] = tag_name
            locators["xpath"] = f"//{tag_name}"

        return locators


def discover_page_elements(url: str, driver: Optional[webdriver.Chrome] = None) -> List[Dict[str, str]]:
    """
    Convenience function to discover elements on a page.

    Args:
        url: Page URL to inspect
        driver: Optional existing WebDriver instance (creates new one if None)

    Returns:
        List of discovered element dictionaries
    """
    # Create driver if not provided
    created_driver = False
    if driver is None:
        from selenium.webdriver.chrome.options import Options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        driver = webdriver.Chrome(options=options)
        created_driver = True

    try:
        discovery = ElementDiscovery(driver)
        elements = discovery.discover_elements(url)
        return elements
    finally:
        # Clean up driver if we created it
        if created_driver:
            driver.quit()
