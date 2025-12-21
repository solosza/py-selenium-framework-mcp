"""
Guest User Role - Unauthenticated user with browse-only capabilities.

This role represents a guest/anonymous user who can:
- Browse product catalog
- View product details via quick view
- Filter and sort products
- View cart (but not checkout)
"""

from typing import Dict, Any, Optional
from roles.base.role import Role
from interfaces.web_interface import WebInterface
from tasks.catalog.catalog_tasks import CatalogTasks
from resources.utilities import autologger


class GuestUser(Role):
    """
    Guest User role with catalog browsing workflow capabilities.

    This role orchestrates high-level catalog workflows for anonymous users
    by composing the CatalogTasks module.
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, base_url: str):
        """
        Initialize GuestUser.

        Args:
            web_interface: WebInterface instance for browser interactions
            base_url: Application base URL for navigation
        """
        super().__init__(web_interface, user_data=None)
        self.base_url = base_url

        # Compose task modules
        self.catalog_tasks = CatalogTasks(web_interface, base_url)

    # ==================== CATALOG BROWSING WORKFLOWS ====================

    @autologger.automation_logger("Role")
    def browse_category(self, category_name: str) -> bool:
        """
        Browse a product category.

        Complete workflow: navigate to category and verify products displayed.

        Args:
            category_name: Name of category to browse ("Women", "Dresses", "T-shirts")

        Returns:
            True if category loaded with products
        """
        return self.catalog_tasks.browse_category(category_name)

    @autologger.automation_logger("Role")
    def browse_and_count_products(self, category_name: str) -> int:
        """
        Browse category and return product count.

        Workflow:
        1. Navigate to category
        2. Verify products displayed
        3. Return count of products

        Args:
            category_name: Name of category to browse

        Returns:
            Number of products in category, or 0 if browse failed
        """
        if not self.catalog_tasks.browse_category(category_name):
            return 0
        return self.catalog_tasks.get_product_count()

    @autologger.automation_logger("Role")
    def filter_products_in_category(
        self,
        category_name: str,
        size: Optional[str] = None,
        color: Optional[str] = None
    ) -> bool:
        """
        Browse category and apply filters.

        Complete workflow:
        1. Navigate to category
        2. Apply size filter (if specified)
        3. Apply color filter (if specified)
        4. Verify filtered results

        Args:
            category_name: Name of category to browse
            size: Optional size filter ("S", "M", "L")
            color: Optional color filter ("White", "Black", etc.)

        Returns:
            True if filtering workflow completed successfully
        """
        return self.catalog_tasks.filter_products(category_name, size=size, color=color)

    @autologger.automation_logger("Role")
    def sort_products_in_category(self, category_name: str, sort_by: str) -> bool:
        """
        Browse category and sort products.

        Complete workflow:
        1. Navigate to category
        2. Apply sort option
        3. Verify sort order

        Args:
            category_name: Name of category to browse
            sort_by: Sort option ("price_asc", "price_desc", "name_asc", "name_desc")

        Returns:
            True if sorting workflow completed successfully
        """
        return self.catalog_tasks.sort_products(category_name, sort_by)

    @autologger.automation_logger("Role")
    def view_product_quick_view(self, category_name: str, product_index: int = 0) -> bool:
        """
        Browse category and open quick view for a product.

        Complete workflow:
        1. Navigate to category
        2. Hover over product at index
        3. Click quick view button
        4. Verify modal opened

        Args:
            category_name: Name of category to browse
            product_index: Index of product to view (0-based)

        Returns:
            True if quick view opened successfully
        """
        return self.catalog_tasks.open_quick_view(category_name, product_index)

    @autologger.automation_logger("Role")
    def close_quick_view(self) -> bool:
        """
        Close the quick view modal.

        Returns:
            True if modal closed successfully
        """
        return self.catalog_tasks.close_quick_view()

    # ==================== VERIFICATION METHODS ====================

    @autologger.automation_logger("Role")
    def get_product_count(self) -> int:
        """
        Get number of products on current page.

        Returns:
            Count of products displayed
        """
        return self.catalog_tasks.get_product_count()

    @autologger.automation_logger("Role")
    def verify_products_displayed(self) -> bool:
        """
        Verify products are displayed on current page.

        Returns:
            True if products are visible
        """
        return self.catalog_tasks.verify_products_displayed()
