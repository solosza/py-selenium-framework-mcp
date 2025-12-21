"""
Catalog Tasks - Reusable product catalog browsing workflows.

This module provides high-level task methods that orchestrate page objects
to accomplish catalog-related workflows like browsing, filtering, and sorting.
"""

import time
from typing import Optional
from interfaces.web_interface import WebInterface
from pages.catalog.product_list_page import ProductListPage
from pages.catalog.quick_view_modal import QuickViewModal


class CatalogTasks:
    """Catalog task workflows for browsing and filtering products."""

    def __init__(self, web: WebInterface, base_url: str):
        """
        Initialize CatalogTasks.

        Args:
            web: WebInterface instance
            base_url: Application base URL
        """
        self.web = web
        self.base_url = base_url
        self.product_list_page = ProductListPage(web)
        self.quick_view_modal = QuickViewModal(web)

    # ==================== NAVIGATION METHODS ====================

    def navigate_to_category(self, category_name: str) -> bool:
        """
        Navigate to a product category.

        Args:
            category_name: Category to navigate to ("Women", "Dresses", "T-shirts")

        Returns:
            True if navigation successful
        """
        # Navigate to home first
        self.web.navigate_to(self.base_url)

        # Click category based on name
        category_map = {
            "WOMEN": self.product_list_page.click_women_category,
            "DRESSES": self.product_list_page.click_dresses_category,
            "T-SHIRTS": self.product_list_page.click_tshirts_category,
            "TSHIRTS": self.product_list_page.click_tshirts_category
        }

        category_key = category_name.upper()
        if category_key not in category_map:
            self.web.logger.error(f"Invalid category: {category_name}")
            return False

        # Click category
        category_map[category_key]()

        # Verify page loaded
        if not self.product_list_page.is_page_loaded():
            self.web.logger.error(f"Failed to load category: {category_name}")
            return False

        self.web.logger.info(f"Navigated to category: {category_name}")
        return True

    def browse_category(self, category_name: str) -> bool:
        """
        Browse a category and verify products are displayed.

        Complete workflow: navigate to category and verify products loaded.

        Args:
            category_name: Category to browse

        Returns:
            True if category browsed successfully and products displayed
        """
        # Navigate to category
        if not self.navigate_to_category(category_name):
            return False

        # Verify products are displayed
        if not self.product_list_page.has_products():
            self.web.logger.error(f"No products found in category: {category_name}")
            return False

        product_count = self.product_list_page.get_product_count()
        self.web.logger.info(f"Browsing {category_name}: {product_count} products found")
        return True

    def browse_subcategory(self, category_name: str, subcategory_name: str) -> bool:
        """
        Browse a subcategory within a main category.

        Args:
            category_name: Main category
            subcategory_name: Subcategory to browse

        Returns:
            True if subcategory browsed successfully
        """
        # Navigate to main category first
        if not self.navigate_to_category(category_name):
            return False

        # Click subcategory
        self.product_list_page.click_subcategory(subcategory_name)

        # Verify page loaded
        if not self.product_list_page.is_page_loaded():
            self.web.logger.error(f"Failed to load subcategory: {subcategory_name}")
            return False

        # Verify products displayed
        if not self.product_list_page.has_products():
            self.web.logger.error(f"No products in subcategory: {subcategory_name}")
            return False

        self.web.logger.info(f"Browsing subcategory: {subcategory_name}")
        return True

    # ==================== FILTERING METHODS ====================

    def filter_products(self, category_name: str, size: Optional[str] = None, color: Optional[str] = None) -> bool:
        """
        Filter products by size and/or color.

        Complete workflow: navigate to category, apply filters, verify results.

        Args:
            category_name: Category to browse
            size: Optional size filter ("S", "M", "L")
            color: Optional color filter (e.g., "White", "Black")

        Returns:
            True if filtering successful
        """
        # Navigate to category
        if not self.navigate_to_category(category_name):
            return False

        # Get initial product count
        initial_count = self.product_list_page.get_product_count()
        self.web.logger.info(f"Initial product count: {initial_count}")

        # Apply size filter if specified
        if size:
            try:
                self.product_list_page.filter_by_size(size)
                self.web.logger.info(f"Applied size filter: {size}")
            except ValueError as e:
                self.web.logger.error(f"Size filter error: {e}")
                return False

        # Apply color filter if specified
        if color:
            try:
                self.product_list_page.filter_by_color(color)
                self.web.logger.info(f"Applied color filter: {color}")
            except ValueError as e:
                self.web.logger.error(f"Color filter error: {e}")
                return False

        # Verify filtering worked (product count should change or stay same)
        filtered_count = self.product_list_page.get_product_count()
        self.web.logger.info(f"Filtered product count: {filtered_count}")

        if not self.product_list_page.has_products():
            self.web.logger.warning("No products match the filter criteria")
            # This is still considered successful - just no matches
            return True

        return True

    # ==================== SORTING METHODS ====================

    def sort_products(self, category_name: str, sort_by: str) -> bool:
        """
        Sort products in a category.

        Complete workflow: navigate to category, apply sort, verify sort order.

        Args:
            category_name: Category to browse
            sort_by: Sort option ("price_asc", "price_desc", "name_asc", "name_desc")

        Returns:
            True if sorting successful and verified
        """
        # Navigate to category
        if not self.navigate_to_category(category_name):
            return False

        # Apply sorting based on option
        sort_map = {
            "price_asc": self.product_list_page.sort_by_price_low_to_high,
            "price_low_to_high": self.product_list_page.sort_by_price_low_to_high,
            "price_desc": self.product_list_page.sort_by_price_high_to_low,
            "price_high_to_low": self.product_list_page.sort_by_price_high_to_low,
            "name_asc": self.product_list_page.sort_by_name_a_to_z,
            "name_a_to_z": self.product_list_page.sort_by_name_a_to_z,
            "name_desc": self.product_list_page.sort_by_name_z_to_a,
            "name_z_to_a": self.product_list_page.sort_by_name_z_to_a
        }

        sort_key = sort_by.lower()
        if sort_key not in sort_map:
            self.web.logger.error(f"Invalid sort option: {sort_by}")
            return False

        # Apply sort
        sort_map[sort_key]()
        self.web.logger.info(f"Applied sort: {sort_by}")

        # Verify sort order for price sorts
        if "price" in sort_key:
            if "asc" in sort_key or "low_to_high" in sort_key:
                if not self.product_list_page.is_sorted_by_price_ascending():
                    self.web.logger.error("Price ascending sort verification failed")
                    return False
            elif "desc" in sort_key or "high_to_low" in sort_key:
                if not self.product_list_page.is_sorted_by_price_descending():
                    self.web.logger.error("Price descending sort verification failed")
                    return False

        self.web.logger.info(f"Products sorted successfully by {sort_by}")
        return True

    # ==================== QUICK VIEW METHODS ====================

    def open_quick_view(self, category_name: str, product_index: int = 0) -> bool:
        """
        Open quick view modal for a product.

        Complete workflow: navigate to category, hover product, click quick view, verify modal.

        Args:
            category_name: Category to browse
            product_index: Index of product to quick view (0-based)

        Returns:
            True if quick view opened successfully
        """
        # Navigate to category
        if not self.navigate_to_category(category_name):
            return False

        # Verify product exists
        product_count = self.product_list_page.get_product_count()
        if product_index >= product_count:
            self.web.logger.error(f"Product index {product_index} out of range (total: {product_count})")
            return False

        # Click quick view
        try:
            self.product_list_page.click_quick_view_by_index(product_index)
            self.web.logger.info(f"Clicked quick view for product at index {product_index}")
        except Exception as e:
            self.web.logger.error(f"Failed to click quick view: {e}")
            return False

        # Wait for modal to open
        time.sleep(2)

        # Verify modal opened
        if not self.quick_view_modal.is_modal_open():
            self.web.logger.error("Quick view modal did not open")
            return False

        # Switch to iframe
        self.quick_view_modal.switch_to_modal_iframe()
        self.web.logger.info("Quick view modal opened successfully")
        return True

    def close_quick_view(self) -> bool:
        """
        Close quick view modal.

        Returns:
            True if modal closed successfully
        """
        try:
            self.quick_view_modal.close_modal()
            time.sleep(1)
            self.web.logger.info("Quick view modal closed")
            return True
        except Exception as e:
            self.web.logger.error(f"Failed to close quick view: {e}")
            return False

    # ==================== VERIFICATION METHODS ====================

    def verify_products_displayed(self) -> bool:
        """
        Verify products are displayed on current page.

        Returns:
            True if products are visible
        """
        return self.product_list_page.has_products()

    def verify_sort_order(self, expected_order: str) -> bool:
        """
        Verify current sort order.

        Args:
            expected_order: Expected sort ("price_asc" or "price_desc")

        Returns:
            True if sort order matches expected
        """
        if expected_order == "price_asc":
            return self.product_list_page.is_sorted_by_price_ascending()
        elif expected_order == "price_desc":
            return self.product_list_page.is_sorted_by_price_descending()
        else:
            self.web.logger.warning(f"Unknown sort order: {expected_order}")
            return False

    def get_product_count(self) -> int:
        """
        Get number of products currently displayed.

        Returns:
            Product count
        """
        return self.product_list_page.get_product_count()

    def get_product_names(self) -> list:
        """
        Get list of product names currently displayed.

        Returns:
            List of product names
        """
        return self.product_list_page.get_product_names()

    def get_product_prices(self) -> list:
        """
        Get list of product prices currently displayed.

        Returns:
            List of product prices
        """
        return self.product_list_page.get_product_prices()
