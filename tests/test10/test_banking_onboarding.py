"""
Test: Banking Onboarding - Complete New Customer Journey

As a new customer, I want to register for an account, log in, open a new
checking account, and transfer funds to it so I can start banking.

BDD Scenario:
  Given I am on the ParaBank homepage
  When I register as a new user
  And I open a new checking account
  And I transfer $100 to the new account
  Then I should see the transfer complete confirmation
  And the transferred amount should be $100
"""
import uuid
import pytest
from framework.roles.test10.new_customer import NewCustomer
from framework.pages.test10.registration_page import RegistrationPage
from framework.pages.test10.open_account_page import OpenAccountPage
from framework.pages.test10.transfer_funds_page import TransferFundsPage
from framework.resources.utilities import autologger


@pytest.mark.banking
@pytest.mark.onboarding
@autologger.automation_logger("Test")
def test_new_customer_completes_banking_onboarding(web_interface, config):
    """
    Test that a new customer can complete the full banking onboarding workflow.

    Steps:
    1. Register new user account
    2. Open new checking account (auto-logged in after registration)
    3. Transfer $100 to the new account
    4. Verify transfer complete
    """
    # Arrange
    base_url = config["url"]
    customer = NewCustomer(web_interface, base_url)

    # Generate unique test data
    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "first_name": "Test",
        "last_name": "Customer",
        "address": "123 Banking Ave",
        "city": "Springfield",
        "state": "IL",
        "zip_code": "62701",
        "phone": "555-987-6543",
        "ssn": "987-65-4321",
        "username": f"testcust_{unique_id}",
        "password": "SecurePass123!"
    }

    # Create POM instances for assertions
    registration_page = RegistrationPage(web_interface)
    open_account_page = OpenAccountPage(web_interface)
    transfer_funds_page = TransferFundsPage(web_interface)

    # Act - Execute the complete onboarding workflow
    customer.complete_banking_onboarding(user_data, transfer_amount="100")

    # Assert - Verify via POM state-check methods
    assert transfer_funds_page.is_transfer_complete(), \
        "Transfer should be completed successfully"

    transfer_message = transfer_funds_page.get_transfer_message()
    assert "$100.00" in transfer_message, \
        f"Transfer message should contain $100.00. Got: {transfer_message}"


@pytest.mark.banking
@pytest.mark.registration
@autologger.automation_logger("Test")
def test_new_customer_registration_only(web_interface, config):
    """
    Test that a new customer can successfully register.

    Smaller test covering just the registration step.
    """
    # Arrange
    base_url = config["url"]
    customer = NewCustomer(web_interface, base_url)

    unique_id = uuid.uuid4().hex[:8]
    user_data = {
        "first_name": "John",
        "last_name": "Doe",
        "address": "456 Test Lane",
        "city": "Chicago",
        "state": "IL",
        "zip_code": "60601",
        "phone": "312-555-1234",
        "ssn": "111-22-3333",
        "username": f"johndoe_{unique_id}",
        "password": "MyPassword123!"
    }

    registration_page = RegistrationPage(web_interface)

    # Act
    customer.register_and_verify(user_data)

    # Assert
    assert registration_page.is_registration_successful(), \
        "Registration should be successful"

    assert registration_page.is_success_message_displayed(), \
        "Success message should be displayed"
