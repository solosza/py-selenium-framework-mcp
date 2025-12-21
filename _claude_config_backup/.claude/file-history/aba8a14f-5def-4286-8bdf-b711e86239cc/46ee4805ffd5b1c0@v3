"""
Guest User Role - Unauthenticated user with browse-only capabilities.

This role represents a guest/anonymous user who can:
- Browse product catalog
- View product details via quick view
- Filter and sort products
- View cart (but not checkout)
"""

from typing import Optional
from interfaces.web_interface import WebInterface
from tasks.catalog.catalog_tasks import CatalogTasks
from resources.utilities import autologger


class GuestUser:
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
        self.web = web_interface
        self.base_url = base_url

        # Compose task modules
        self.catalog_tasks = CatalogTasks(web_interface, base_url)

    # ==================== CATALOG BROWSING WORKFLOWS ====================

    @autologger.automation_logger("Role")
    def browse_category(self, category_name: str) -> None:
        """
        Browse a product category.

        Tests should verify via product_list_page.has_products().

        Args:
            category_name: Name of category to browse ("Women", "Dresses", "T-shirts")
        """
        self.catalog_tasks.browse_category(category_name)

    @autologger.automation_logger("Role")
    def browse_and_count_products(self, category_name: str) -> int:
        """
        Browse category and return product count.

        Args:
            category_name: Name of category to browse

        Returns:
            Number of products in category
        """
        self.catalog_tasks.browse_category(category_name)
        return self.catalog_tasks.get_product_count()

    @autologger.automation_logger("Role")
    def filter_products_in_category(
        self,
        category_name: str,
        size: Optional[str] = None,
        color: Optional[str] = None
    ) -> None:
        """
        Browse category and apply filters.

        Tests should verify filtered results via product_list_page.

        Args:
            category_name: Name of category to browse
            size: Optional size filter ("S", "M", "L")
            color: Optional color filter ("White", "Black", etc.)
        """
        self.catalog_tasks.filter_products(category_name, size=size, color=color)

    @autologger.automation_logger("Role")
    def sort_products_in_category(self, category_name: str, sort_by: str) -> None:
        """
        Browse category and sort products.

        Tests should verify sort order via product_list_page.

        Args:
            category_name: Name of category to browse
            sort_by: Sort option ("price_asc", "price_desc", "name_asc", "name_desc")
        """
        self.catalog_tasks.sort_products(category_name, sort_by)

    @autologger.automation_logger("Role")
    def view_product_quick_view(self, category_name: str, product_index: int = 0) -> None:
        """
        Browse category and open quick view for a product.

        Tests should verify via quick_view_modal.is_modal_open().

        Args:
            category_name: Name of category to browse
            product_index: Index of product to view (0-based)
        """
        self.catalog_tasks.open_quick_view(category_name, product_index)

    @autologger.automation_logger("Role")
    def close_quick_view(self) -> None:
        """Close the quick view modal."""
        self.catalog_tasks.close_quick_view()

    # ==================== DATA RETRIEVAL METHODS ====================

    @autologger.automation_logger("Role")
    def get_product_count(self) -> int:
        """
        Get number of products on current page.

        Returns:
            Count of products displayed
        """
        return self.catalog_tasks.get_product_count()
