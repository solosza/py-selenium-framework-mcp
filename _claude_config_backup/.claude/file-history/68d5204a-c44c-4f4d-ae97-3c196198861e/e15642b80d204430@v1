"""
Registered User Role - Authenticated user with full e-commerce capabilities.

This role represents a logged-in customer who can:
- Browse product catalog
- Add products to cart
- Complete checkout process
- View order history
- Manage account settings
"""

from typing import Dict, Any, Optional
from roles.role import Role
from interfaces.web_interface import WebInterface
from tasks.common_tasks import CommonTasks


class RegisteredUser(Role):
    """
    Registered User role with full e-commerce workflow capabilities.

    This role orchestrates high-level business workflows for authenticated users
    by composing task modules (authentication, catalog, cart, checkout).
    """

    def __init__(self, web_interface: WebInterface, user_data: Dict[str, Any], base_url: str):
        """
        Initialize RegisteredUser with credentials and task orchestrators.

        Args:
            web_interface: WebInterface instance for browser interactions
            user_data: Dictionary containing user credentials and profile data
                Required keys: email, password
                Optional keys: first_name, last_name, address, phone, etc.
            base_url: Application base URL for navigation
        """
        super().__init__(web_interface, user_data)

        # Validate required credentials
        if not self.has_credentials():
            raise ValueError("RegisteredUser requires email and password in user_data")

        # Compose task modules
        self.common_tasks = CommonTasks(web_interface, base_url)

        # TODO: Add these task modules as they are implemented
        # self.catalog_tasks = CatalogTasks(web_interface)
        # self.cart_tasks = CartTasks(web_interface)
        # self.checkout_tasks = CheckoutTasks(web_interface)

    # ==================== AUTHENTICATION WORKFLOWS ====================

    def login(self) -> bool:
        """
        Log in to the application.

        High-level business workflow that orchestrates authentication.

        Returns:
            True if login successful, False otherwise
        """
        return self.common_tasks.log_in(self.email, self.password)

    def logout(self) -> bool:
        """
        Log out from the application.

        High-level business workflow that completes logout process.

        Returns:
            True if logout successful, False otherwise
        """
        return self.common_tasks.log_out()

    def is_logged_in(self) -> bool:
        """
        Check if user is currently logged in.

        Returns:
            True if logged in, False otherwise
        """
        return self.common_tasks.verify_logged_in()

    # ==================== E-COMMERCE WORKFLOWS (TO BE IMPLEMENTED) ====================

    def browse_product_catalog(self, search_term: Optional[str] = None) -> bool:
        """
        Browse product catalog with optional search.

        TODO: Implement after catalog_tasks module is created.

        Args:
            search_term: Optional product search term

        Returns:
            True if catalog browsing successful
        """
        raise NotImplementedError("Catalog browsing workflow not yet implemented")

    def add_product_to_cart(self, product_data: Dict[str, Any]) -> bool:
        """
        Add a product to shopping cart.

        TODO: Implement after catalog_tasks and cart_tasks modules are created.

        Args:
            product_data: Product information (name, quantity, size, color, etc.)

        Returns:
            True if product added successfully
        """
        raise NotImplementedError("Add to cart workflow not yet implemented")

    def view_shopping_cart(self) -> bool:
        """
        Navigate to and view shopping cart.

        TODO: Implement after cart_tasks module is created.

        Returns:
            True if cart viewed successfully
        """
        raise NotImplementedError("View cart workflow not yet implemented")

    def complete_purchase(self, payment_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Complete end-to-end purchase flow.

        TODO: Implement after checkout_tasks module is created.

        High-level workflow that orchestrates:
        1. Review cart
        2. Confirm addresses
        3. Select shipping method
        4. Select payment method
        5. Confirm order

        Args:
            payment_data: Payment information (if different from saved)

        Returns:
            True if purchase completed successfully
        """
        raise NotImplementedError("Purchase workflow not yet implemented")

    def purchase_product_end_to_end(self, product_data: Dict[str, Any],
                                    payment_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Complete end-to-end workflow: search → add to cart → purchase.

        TODO: Implement after all task modules are created.

        This is the ultimate business workflow that demonstrates full
        e-commerce journey from product discovery to order confirmation.

        Args:
            product_data: Product information (name, quantity, etc.)
            payment_data: Payment information (optional)

        Returns:
            True if entire workflow completed successfully
        """
        raise NotImplementedError("End-to-end purchase workflow not yet implemented")

    # ==================== ACCOUNT MANAGEMENT (TO BE IMPLEMENTED) ====================

    def view_order_history(self) -> bool:
        """
        View past orders.

        TODO: Implement after account_tasks module is created.

        Returns:
            True if order history viewed successfully
        """
        raise NotImplementedError("Order history workflow not yet implemented")

    def update_account_info(self, updated_data: Dict[str, Any]) -> bool:
        """
        Update account information (address, password, etc.).

        TODO: Implement after account_tasks module is created.

        Args:
            updated_data: Dictionary with updated account fields

        Returns:
            True if account updated successfully
        """
        raise NotImplementedError("Account update workflow not yet implemented")
