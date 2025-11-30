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
from resources.utilities import autologger


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

    @autologger.automation_logger("Task")
    def navigate_to_category(self, category_name: str) -> None:
        """
        Navigate to a product category.

        Args:
            category_name: Category to navigate to ("Women", "Dresses", "T-shirts")
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
            return

        # Click category
        category_map[category_key]()

        # Verify page loaded
        if not self.product_list_page.is_page_loaded():
            self.web.logger.error(f"Failed to load category: {category_name}")
            return

        self.web.logger.info(f"Navigated to category: {category_name}")

    @autologger.automation_logger("Task")
    def browse_category(self, category_name: str) -> None:
        """
        Browse a category. Tests should verify via product_list_page.has_products().

        Args:
            category_name: Category to browse
        """
        # Navigate to category
        self.navigate_to_category(category_name)

        # Log product count if products are displayed
        if self.product_list_page.has_products():
            product_count = self.product_list_page.get_product_count()
            self.web.logger.info(f"Browsing {category_name}: {product_count} products found")
        else:
            self.web.logger.error(f"No products found in category: {category_name}")

    @autologger.automation_logger("Task")
    def browse_subcategory(self, category_name: str, subcategory_name: str) -> None:
        """
        Browse a subcategory within a main category.

        Args:
            category_name: Main category
            subcategory_name: Subcategory to browse
        """
        # Navigate to main category first
        self.navigate_to_category(category_name)

        # Click subcategory
        self.product_list_page.click_subcategory(subcategory_name)

        # Verify page loaded
        if not self.product_list_page.is_page_loaded():
            self.web.logger.error(f"Failed to load subcategory: {subcategory_name}")
            return

        # Log results
        if self.product_list_page.has_products():
            self.web.logger.info(f"Browsing subcategory: {subcategory_name}")
        else:
            self.web.logger.error(f"No products in subcategory: {subcategory_name}")

    # ==================== FILTERING METHODS ====================

    @autologger.automation_logger("Task")
    def filter_products(self, category_name: str, size: Optional[str] = None, color: Optional[str] = None) -> None:
        """
        Filter products by size and/or color.

        Args:
            category_name: Category to browse
            size: Optional size filter ("S", "M", "L")
            color: Optional color filter (e.g., "White", "Black")
        """
        # Navigate to category
        self.navigate_to_category(category_name)

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
                return

        # Apply color filter if specified
        if color:
            try:
                self.product_list_page.filter_by_color(color)
                self.web.logger.info(f"Applied color filter: {color}")
            except ValueError as e:
                self.web.logger.error(f"Color filter error: {e}")
                return

        # Log filtering results
        filtered_count = self.product_list_page.get_product_count()
        self.web.logger.info(f"Filtered product count: {filtered_count}")

        if not self.product_list_page.has_products():
            self.web.logger.warning("No products match the filter criteria")

    # ==================== SORTING METHODS ====================

    @autologger.automation_logger("Task")
    def sort_products(self, category_name: str, sort_by: str) -> None:
        """
        Sort products in a category.

        Args:
            category_name: Category to browse
            sort_by: Sort option ("price_asc", "price_desc", "name_asc", "name_desc")
        """
        # Navigate to category
        self.navigate_to_category(category_name)

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
            return

        # Apply sort
        sort_map[sort_key]()
        self.web.logger.info(f"Applied sort: {sort_by}")

    # ==================== QUICK VIEW METHODS ====================

    @autologger.automation_logger("Task")
    def open_quick_view(self, category_name: str, product_index: int = 0) -> None:
        """
        Open quick view modal for a product.

        Args:
            category_name: Category to browse
            product_index: Index of product to quick view (0-based)
        """
        # Navigate to category
        self.navigate_to_category(category_name)

        # Verify product exists
        product_count = self.product_list_page.get_product_count()
        if product_index >= product_count:
            self.web.logger.error(f"Product index {product_index} out of range (total: {product_count})")
            return

        # Click quick view
        try:
            self.product_list_page.click_quick_view_by_index(product_index)
            self.web.logger.info(f"Clicked quick view for product at index {product_index}")
        except Exception as e:
            self.web.logger.error(f"Failed to click quick view: {e}")
            return

        # Wait for modal to open
        time.sleep(2)

        # Verify modal opened
        if not self.quick_view_modal.is_modal_open():
            self.web.logger.error("Quick view modal did not open")
            return

        # Switch to iframe
        self.quick_view_modal.switch_to_modal_iframe()
        self.web.logger.info("Quick view modal opened successfully")

    @autologger.automation_logger("Task")
    def close_quick_view(self) -> None:
        """Close quick view modal."""
        try:
            self.quick_view_modal.close_modal()
            time.sleep(1)
            self.web.logger.info("Quick view modal closed")
        except Exception as e:
            self.web.logger.error(f"Failed to close quick view: {e}")

    # ==================== DATA RETRIEVAL METHODS ====================

    @autologger.automation_logger("Task")
    def get_product_count(self) -> int:
        """
        Get number of products currently displayed.

        Returns:
            Product count
        """
        return self.product_list_page.get_product_count()

    @autologger.automation_logger("Task")
    def get_product_names(self) -> list:
        """
        Get list of product names currently displayed.

        Returns:
            List of product names
        """
        return self.product_list_page.get_product_names()

    @autologger.automation_logger("Task")
    def get_product_prices(self) -> list:
        """
        Get list of product prices currently displayed.

        Returns:
            List of product prices
        """
        return self.product_list_page.get_product_prices()
