"""
Product List Page - Product catalog/listing page object.

This page represents product category pages and search results.
Handles browsing, filtering, sorting, and quick view interactions.
"""

import time
from selenium.webdriver.common.by import By
from pages.base_page import BasePage
from interfaces.web_interface import WebInterface


class ProductListPage(BasePage):
    """
    Page Object for Product List/Catalog pages.

    Provides methods for browsing categories, filtering products,
    sorting results, and triggering quick view modals.
    """

    def __init__(self, web: WebInterface):
        """
        Initialize ProductListPage.

        Args:
            web: WebInterface instance
        """
        super().__init__(web)

    # ==================== LOCATORS ====================

    # Category navigation
    WOMEN_CATEGORY = (By.LINK_TEXT, "WOMEN")
    DRESSES_CATEGORY = (By.LINK_TEXT, "DRESSES")
    TSHIRTS_CATEGORY = (By.LINK_TEXT, "T-SHIRTS")

    # Product grid
    PRODUCT_CONTAINER = (By.CSS_SELECTOR, "ul.product_list")
    PRODUCT_ITEMS = (By.CSS_SELECTOR, "ul.product_list li.ajax_block_product")
    PRODUCT_NAME = (By.CSS_SELECTOR, ".product-name")
    PRODUCT_PRICE = (By.CSS_SELECTOR, ".price.product-price")

    # Quick view
    QUICK_VIEW_BUTTON = (By.CSS_SELECTOR, ".quick-view")

    # Sorting
    SORT_DROPDOWN = (By.ID, "selectProductSort")

    # Filtering - Size
    SIZE_HEADING = (By.XPATH, "//div[@class='layered_subtitle_heading' and normalize-space()='Size']")
    SIZE_S_CHECKBOX = (By.ID, "layered_id_attribute_group_1")
    SIZE_M_CHECKBOX = (By.ID, "layered_id_attribute_group_2")
    SIZE_L_CHECKBOX = (By.ID, "layered_id_attribute_group_3")

    # Filtering - Color
    COLOR_BEIGE = (By.CSS_SELECTOR, "input[name='layered_id_attribute_group_7']")
    COLOR_WHITE = (By.CSS_SELECTOR, "input[name='layered_id_attribute_group_8']")
    COLOR_BLACK = (By.CSS_SELECTOR, "input[name='layered_id_attribute_group_11']")
    COLOR_ORANGE = (By.CSS_SELECTOR, "input[name='layered_id_attribute_group_13']")
    COLOR_BLUE = (By.CSS_SELECTOR, "input[name='layered_id_attribute_group_14']")
    COLOR_YELLOW = (By.CSS_SELECTOR, "input[name='layered_id_attribute_group_16']")

    # Results
    RESULTS_COUNT = (By.CSS_SELECTOR, ".product-count")
    BREADCRUMB = (By.CSS_SELECTOR, ".breadcrumb")

    # ==================== PAGE METHODS ====================

    def is_page_loaded(self) -> bool:
        """
        Verify product list page is loaded.

        Returns:
            True if product container is visible
        """
        return self.web.is_element_displayed(*self.PRODUCT_CONTAINER, timeout=10)

    # ==================== NAVIGATION METHODS ====================

    def click_women_category(self):
        """
        Navigate to Women category.

        Returns:
            self for method chaining
        """
        self.web.click(*self.WOMEN_CATEGORY)
        return self

    def click_dresses_category(self):
        """
        Navigate to Dresses category.

        Returns:
            self for method chaining
        """
        self.web.click(*self.DRESSES_CATEGORY)
        return self

    def click_tshirts_category(self):
        """
        Navigate to T-shirts category.

        Returns:
            self for method chaining
        """
        self.web.click(*self.TSHIRTS_CATEGORY)
        return self

    def click_subcategory(self, subcategory_name: str):
        """
        Click a subcategory by name.

        Args:
            subcategory_name: Name of the subcategory link

        Returns:
            self for method chaining
        """
        locator = (By.LINK_TEXT, subcategory_name)
        self.web.click(*locator)
        return self

    # ==================== SORTING METHODS ====================

    def sort_by_price_low_to_high(self):
        """
        Sort products by price: lowest first.

        Returns:
            self for method chaining
        """
        self.web.select_dropdown_by_value(*self.SORT_DROPDOWN, option_value="price:asc")
        time.sleep(2)  # Wait for page to reload with sorted results
        return self

    def sort_by_price_high_to_low(self):
        """
        Sort products by price: highest first.

        Returns:
            self for method chaining
        """
        self.web.select_dropdown_by_value(*self.SORT_DROPDOWN, option_value="price:desc")
        time.sleep(2)  # Wait for page to reload with sorted results
        return self

    def sort_by_name_a_to_z(self):
        """
        Sort products by name: A to Z.

        Returns:
            self for method chaining
        """
        self.web.select_dropdown_by_value(*self.SORT_DROPDOWN, option_value="name:asc")
        time.sleep(2)  # Wait for page to reload with sorted results
        return self

    def sort_by_name_z_to_a(self):
        """
        Sort products by name: Z to A.

        Returns:
            self for method chaining
        """
        self.web.select_dropdown_by_value(*self.SORT_DROPDOWN, option_value="name:desc")
        time.sleep(2)  # Wait for page to reload with sorted results
        return self

    # ==================== FILTERING METHODS ====================

    def filter_by_size(self, size: str):
        """
        Filter products by size.

        Args:
            size: Size to filter ("S", "M", or "L")

        Returns:
            self for method chaining
        """
        size_map = {
            "S": self.SIZE_S_CHECKBOX,
            "M": self.SIZE_M_CHECKBOX,
            "L": self.SIZE_L_CHECKBOX
        }

        if size.upper() not in size_map:
            raise ValueError(f"Invalid size: {size}. Must be S, M, or L")

        # Check if size checkbox is visible, if not expand the Size section
        checkbox_locator = size_map[size.upper()]
        if not self.web.is_element_displayed(*checkbox_locator, timeout=2):
            # Click Size heading to expand the section
            self.web.click(*self.SIZE_HEADING)
            time.sleep(2)  # Wait for section to expand

            # Wait for checkbox to become visible after expansion
            for _ in range(5):  # Try for 5 seconds
                if self.web.is_element_displayed(*checkbox_locator, timeout=1):
                    break
                time.sleep(1)

        # Click the size checkbox using JavaScript (checkbox might be hidden by CSS)
        checkbox_element = self.web.find_element(*checkbox_locator)
        self.web.driver.execute_script("arguments[0].scrollIntoView(true);", checkbox_element)
        time.sleep(0.5)
        self.web.driver.execute_script("arguments[0].click();", checkbox_element)
        time.sleep(2)  # Wait for filtered results (AJAX reload)
        return self

    def filter_by_color(self, color: str):
        """
        Filter products by color.

        Args:
            color: Color to filter (e.g., "White", "Black", "Blue")

        Returns:
            self for method chaining
        """
        color_map = {
            "BEIGE": self.COLOR_BEIGE,
            "WHITE": self.COLOR_WHITE,
            "BLACK": self.COLOR_BLACK,
            "ORANGE": self.COLOR_ORANGE,
            "BLUE": self.COLOR_BLUE,
            "YELLOW": self.COLOR_YELLOW
        }

        color_key = color.upper()
        if color_key not in color_map:
            raise ValueError(f"Invalid color: {color}")

        self.web.click(*color_map[color_key])
        time.sleep(2)  # Wait for filtered results
        return self

    # ==================== PRODUCT GRID METHODS ====================

    def get_product_count(self) -> int:
        """
        Get number of products displayed.

        Returns:
            Count of products in the grid
        """
        products = self.web.find_elements(*self.PRODUCT_ITEMS)
        return len(products)

    def get_product_names(self) -> list:
        """
        Get all product names on the page.

        Returns:
            List of product names
        """
        products = self.web.find_elements(*self.PRODUCT_ITEMS)
        names = []

        for product in products:
            name_element = product.find_element(*self.PRODUCT_NAME)
            names.append(name_element.text.strip())

        return names

    def get_product_prices(self) -> list:
        """
        Get all product prices on the page.

        Returns:
            List of product prices as floats
        """
        products = self.web.find_elements(*self.PRODUCT_ITEMS)
        prices = []

        for product in products:
            price_element = product.find_element(*self.PRODUCT_PRICE)
            price_text = price_element.text.strip().replace("$", "").replace(",", "")
            try:
                prices.append(float(price_text))
            except ValueError:
                self.web.logger.warning(f"Could not parse price: {price_text}")

        return prices

    def click_product_by_index(self, index: int):
        """
        Click a product by index.

        Args:
            index: Product index (0-based)

        Returns:
            self for method chaining
        """
        products = self.web.find_elements(*self.PRODUCT_ITEMS)
        if index >= len(products):
            raise IndexError(f"Product index {index} out of range")

        product = products[index]
        name_element = product.find_element(*self.PRODUCT_NAME)
        name_element.click()
        return self

    # ==================== QUICK VIEW METHODS ====================

    def hover_product_by_index(self, index: int):
        """
        Hover over a product to reveal Quick View button.

        Args:
            index: Product index (0-based)

        Returns:
            self for method chaining
        """
        products = self.web.find_elements(*self.PRODUCT_ITEMS)
        if index >= len(products):
            raise IndexError(f"Product index {index} out of range")

        product = products[index]
        self.web.hover_over_element(product)
        return self

    def click_quick_view_by_index(self, index: int):
        """
        Click Quick View button for a product.

        Args:
            index: Product index (0-based)

        Returns:
            self for method chaining
        """
        products = self.web.find_elements(*self.PRODUCT_ITEMS)
        if index >= len(products):
            raise IndexError(f"Product index {index} out of range")

        # Hover to reveal Quick View button
        product = products[index]
        self.web.hover_over_element(product)
        time.sleep(1)  # Brief wait for button to appear

        # Click Quick View within this product
        quick_view_btn = product.find_element(*self.QUICK_VIEW_BUTTON)
        quick_view_btn.click()
        return self

    # ==================== VALIDATION METHODS ====================

    def has_products(self) -> bool:
        """
        Check if any products are displayed.

        Returns:
            True if products present
        """
        return self.get_product_count() > 0

    def is_sorted_by_price_ascending(self) -> bool:
        """
        Verify products sorted by price (low to high).

        Returns:
            True if sorted correctly
        """
        prices = self.get_product_prices()
        return prices == sorted(prices)

    def is_sorted_by_price_descending(self) -> bool:
        """
        Verify products sorted by price (high to low).

        Returns:
            True if sorted correctly
        """
        prices = self.get_product_prices()
        return prices == sorted(prices, reverse=True)
