# Sample User Story: Add Product to Cart

**As a** online shopper
**I want to** add products to my shopping cart
**So that** I can purchase multiple items in one transaction

## Acceptance Criteria
- User can add product from product detail page
- Cart counter updates immediately when product is added
- Success confirmation modal is displayed
- User can specify product quantity before adding

## Test Scenarios

### Scenario: Add single product to cart
Given user is on product detail page for "Faded Short Sleeve T-shirts"
When user clicks "Add to Cart" button
Then product is added to cart
And cart counter increments by 1
And success modal displays "Product successfully added to your shopping cart"

### Scenario: Add multiple quantities
Given user is on product detail page
When user sets quantity to 3
And user clicks "Add to Cart" button
Then cart contains 3 units of the product
And cart counter shows "+3"

### Scenario: Continue shopping after adding
Given user has added product to cart
And success modal is displayed
When user clicks "Continue Shopping" button
Then modal closes
And user remains on product detail page
