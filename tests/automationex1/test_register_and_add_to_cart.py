"""
test_register_and_add_to_cart - Test for new user registration and cart workflow.

Tests the complete workflow: register new account and add product to cart.
Uses AAA pattern: Arrange, Act, Assert.
Dynamic credential strategy: Generate fresh credentials, save to config, Role reads from config.
"""

import pytest
import json
import os
from faker import Faker
from resources.utilities import autologger
from roles.automationex1.new_user import NewUser
from pages.automationex1.registration_page import RegistrationPage
from pages.automationex1.products_page import ProductsPage


@pytest.mark.automationex1
@autologger.automation_logger("Test")
def test_register_and_add_to_cart(web_interface):
    """
    Test: New user can register account and add product to cart.

    Given: I am a new user
    When: I register an account and add a product to cart
    Then: I should see registration success AND product added confirmation

    Dynamic credential strategy (Step 1 config):
    1. Generate fresh user data with Faker
    2. Save to workflow-specific location (tests/automationex1/data/test_users.json)
    3. Role reads from saved config file in __init__
    4. Execute workflow with saved credentials
    """
    # Arrange - Generate fresh credentials (dynamic strategy)
    fake = Faker()
    user_data = {
        "name": fake.name(),
        "email": fake.email(),
        "password": "TestPass123!",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "address": fake.street_address(),
        "state": fake.state(),
        "city": fake.city(),
        "zipcode": fake.zipcode(),
        "mobile": fake.phone_number(),
        "day": "15",
        "month": "May",
        "year": "1990",
        "country": "United States"
    }

    # Save credentials to config file (workflow-specific data location from Step 1)
    data_dir = "tests/automationex1/data"
    os.makedirs(data_dir, exist_ok=True)
    config_file = os.path.join(data_dir, "test_users.json")

    # Write to config file - Role will read from here
    with open(config_file, "w") as f:
        json.dump({"new_user": user_data}, f, indent=2)

    # Create Role - reads credentials from config file in __init__ (dynamic strategy)
    user = NewUser(web_interface)

    # Create Page Objects for assertions
    registration_page = RegistrationPage(web_interface)
    products_page = ProductsPage(web_interface)

    # Act - Call ONE workflow method, NO return value
    user.register_and_add_to_cart()

    # Assert - Via POM state-check methods (NOT return values)
    assert registration_page.is_registration_successful(), "Registration should succeed"
    assert products_page.is_product_in_cart(), "Product should be in cart"
