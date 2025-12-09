"""
GuestUser - Unauthenticated user role for browsing catalog.

Represents a guest visitor who can browse products without logging in.
"""

from interfaces.web_interface import WebInterface
from tasks.catalog.catalog_tasks import CatalogTasks
from pages.catalog.product_list_page import ProductListPage
from resources.utilities import autologger


class GuestUser:
    """
    GuestUser - orchestrates browsing workflows without authentication.

    Capabilities:
    - Browse product categories
    - View product listings
    """

    @autologger.automation_logger("Role Constructor")
    def __init__(self, web_interface: WebInterface, base_url: str):
        """
        Initialize GuestUser with task modules.

        Args:
            web_interface: WebInterface instance
            base_url: Application base URL
        """
        self.web = web_interface
        self.base_url = base_url

        # Compose task modules
        self.catalog_tasks = CatalogTasks(web_interface, base_url)

        # Page objects for state verification
        self.product_list_page = ProductListPage(web_interface)

    # ==================== WORKFLOW METHODS ====================

    @autologger.automation_logger("Role")
    def browse_tshirts_category(self) -> None:
        """
        Browse the T-shirts category.

        Workflow:
        1. Navigate to T-shirts category

        NO return value - test asserts via product_list_page.has_products()
        """
        self.catalog_tasks.browse_category("T-shirts")
        # NO return - test asserts via POM
