# Phase 0: Test Design - py_sel_framework_mcp

**Project:** Python Selenium Test Automation Framework with MCP Integration
**Target Application:** http://www.automationpractice.pl/index.php
**Phase:** Phase 0 - Requirements Gathering & Test Design
**Status:** In Progress

---

## Overview

This document captures all design decisions made during Phase 0 for the py_sel_framework_mcp project. Phase 0 for QA differs from software development Phase 0:

**QA Phase 0 Process:**
1. Identify features/workflows to test
2. Write user stories for each workflow
3. Derive test scenarios from user stories
4. Design page objects to support test scenarios
5. Design task methods to support test scenarios

**Output:** This design document feeds into Phase 1 (Test Plan generation)

---

## Phase 0 Task Management Strategy

### The Question: When Does Phase 0 Need Formal Task Lists?

**Context:** Phase 0 is exploratory/design work, not implementation. The 4D Framework generates formal task lists in Phase 2 (for implementation). But what if Phase 0 becomes large and complex?

### Two Approaches

#### Approach 1: Simple Completion Checklist (Default)
Use a lightweight checklist embedded in this document to track sections:

```markdown
## Phase 0 Completion Checklist
- [x] Section 1: Foundation Layer Design
- [ ] Section 2: Authentication Workflows
- [ ] Section 3: Product Catalog Workflows
...
```

**When to use:**
- Phase 0 has 3-8 sections
- Sections are conversational/exploratory
- Each section takes <2 hours
- Design decisions flow naturally

**Pros:**
- Low overhead
- Fast iteration
- Keeps Phase 0 conversational
- No meta-process complexity

**Cons:**
- Less structure for very large Phase 0
- No detailed sub-task tracking

---

#### Approach 2: Formal Task List (Phase 2 Process)
Create a "PRD for Phase 0 Completion" and generate tasks using Phase 2 process:

```markdown
## Phase 0 Implementation Tasks
- [ ] 1.0 Complete Section 1: Foundation Layer Design [CORE]
  - [ ] 1.1 Design web_interface.py enhancements
  - [ ] 1.2 Design config management approach
  - [ ] 1.3 Design data_generator.py
  - [ ] 1.4 Design conftest.py fixtures
...
```

**When to use:**
- Phase 0 has >8 sections
- Each section requires substantial work (>2 hours)
- Multiple people working on Phase 0
- Phase 0 spans multiple sessions and needs precise handoff
- Design work is prescriptive, not exploratory

**Pros:**
- Rigorous tracking
- Clear handoff between sessions
- Supports larger Phase 0 efforts
- Applies proven Phase 2/3 execution discipline

**Cons:**
- Overhead for small Phase 0
- Meta-process complexity (PRD for design work)
- Can feel like over-engineering

---

### Decision Criteria: When is Phase 0 "Too Large"?

Use **Approach 2 (Formal Task List)** if ANY of these are true:

1. **Size:** Phase 0 has >8 major sections
2. **Duration:** Phase 0 will span >4 work sessions (>10 hours total)
3. **Complexity:** Each section requires >2 hours of design work
4. **Team Size:** Multiple people working on Phase 0 simultaneously
5. **Handoff Risk:** High risk of losing context between sessions
6. **Prescriptive Work:** Design decisions are clear and can be broken into discrete tasks

Otherwise, use **Approach 1 (Simple Checklist)**.

---

### This Project's Decision

**MVP Scope:** 4 workflow sections (Auth, Catalog, Cart, Checkout) + MCP design
**Estimated Effort:** ~2.5 hours remaining (Section 3-5 + MCP)
**Sessions:** 2-3 sessions total

**Decision:** Use **Approach 1 (Simple Checklist)**

**Rationale:**
- Only 5 sections remaining
- Each section is <1 hour
- Conversational/exploratory design
- Single person working
- Low handoff risk

If we expand to full scope (7 sections, 55 test scenarios), we would reconsider Approach 2.

---

## Phase 0 Completion Checklist

- [x] Section 1: Foundation Layer Design
- [x] Section 2: Authentication Workflows (user stories, scenarios, page objects, tasks)
- [x] Section 3: Product Catalog Workflows (MVP: 4 scenarios, page objects, tasks)
- [x] Section 4: Shopping Cart Workflows (user stories → scenarios → design)
- [x] Section 5: Checkout Workflows (user stories → scenarios → design)
- [x] Section 8: MCP Server Design
- [x] Review and finalize document

**Deferred to v2.0:**
- Section 6: Account Management Workflows
- Section 7: Additional Workflows (wishlist, compare, contact, reviews)

**Phase 0 Status:** ✅ COMPLETE

---

## Section 1: Foundation Layer Design

### web_interface.py Enhancements

The WebInterface class wraps Selenium WebDriver and provides 7 method categories:

1. **Logging Integration**
   - Log all actions (clicks, inputs, navigations)
   - Configurable log levels

2. **Screenshot Capture**
   - `take_screenshot(filename)` method
   - Auto-screenshot on error

3. **URL Utilities**
   - `get_current_url()` - Return current page URL
   - `get_page_title()` - Return page title
   - `wait_for_url_to_contain(text)` - Wait for URL to match pattern

4. **Element Query Methods**
   - `is_element_visible(locator)` - Check if element is visible
   - `is_element_present(locator)` - Check if element exists in DOM
   - `get_text(locator)` - Get element text content

5. **Alert Handling**
   - `accept_alert()` - Accept alert dialog
   - `dismiss_alert()` - Dismiss alert dialog
   - `get_alert_text()` - Get alert message text

6. **Execute Script**
   - JavaScript execution support
   - Scroll into view, manipulate DOM, etc.

7. **Enhanced Error Handling**
   - Auto-screenshot on exceptions
   - Detailed error messages with context

### No base_page.py

**Decision:** Do NOT create a base_page class

**Rationale:**
- Matches original framework (OGF) pattern
- Pages are simple classes with `__init__(self, web_interface)`
- No inheritance needed
- Navigation helpers live in task classes, not page base class

**Example:**
```python
class AuthenticationPage:
    def __init__(self, web_interface):
        self.web = web_interface
```

### Config Management

**Decision:** Use .env file (NOT JSON configs like OGF)

**Rationale:**
- Simpler for single-site e-commerce testing
- Standard practice for environment variables
- python-dotenv for loading

**Keys:**
- `BASE_URL` - Base URL of application
- `BROWSER` - Browser type (chrome, firefox)
- `HEADLESS` - Run headless (true/false)
- `IMPLICIT_WAIT` - Implicit wait timeout (seconds)
- `EXPLICIT_WAIT` - Explicit wait timeout (seconds)
- `SCREENSHOT_DIR` - Directory for screenshots
- `REPORT_DIR` - Directory for HTML reports

### data_generator.py (Hybrid Approach)

**Decision:** Combine JSON file loading + Faker wrapper methods

**Rationale:**
- OGF TestData class loads/parses JSON files (proven pattern)
- Add Faker wrapper methods for dynamic data generation
- Best of both: static test data (JSON) + dynamic data (Faker)

**Features:**
- Load JSON files (e.g., `users.json`, `products.json`)
- Faker wrapper methods:
  - `generate_email()`
  - `generate_name()`
  - `generate_address()`
  - `generate_phone()`
  - `generate_password()`

### conftest.py Fixtures

**Decision:** NO role fixtures (match OGF pattern)

**Fixtures:**
- `driver` (function scope) - WebDriver instance
- `config` (session scope) - Environment configuration
- `web_interface` (function scope) - WebInterface wrapper instance
- `test_users` (session scope) - Pre-created test user accounts

**Rationale:**
- Roles/tasks instantiated manually in tests
- Tests explicitly create roles they need
- More transparent than auto-injected role fixtures

### Test Accounts

**Decision:** Pre-create 3-5 accounts manually on automationpractice.pl

**Storage:** `framework/resources/data/users.json`

**Format:**
```json
{
  "registered_user_1": {
    "email": "user1@example.com",
    "password": "Password123",
    "first_name": "John",
    "last_name": "Doe"
  },
  "registered_user_2": { ... }
}
```

**Test Data Strategy:**
- Pre-created accounts: Use for login tests (stable data)
- Faker-generated data: Use for addresses, payment info (dynamic per test)
- Registration test: Use Faker to generate new user each run (avoid duplicate email errors)

---

## Section 2: Authentication Workflows

### User Stories (6 Total)

#### User Story 1: User Login
**As a** registered customer
**I want to** log in with my email and password
**So that** I can access my account and make purchases

**Acceptance Criteria:**
- User can navigate to login page
- User can enter email and password
- Clicking "Sign in" logs user in
- Successful login redirects to "My Account" page
- User's name appears in header after login
- "Sign out" link is visible after login

---

#### User Story 2: New User Registration
**As a** new customer
**I want to** create an account
**So that** I can save my information and track orders

**Acceptance Criteria:**
- User can navigate to registration page from login page
- User can enter email to start registration
- User can complete registration form (first name, last name, password, address)
- Clicking "Register" creates account
- Successful registration logs user in automatically
- User is redirected to "My Account" page

---

#### User Story 3: User Logout
**As a** logged-in user
**I want to** log out of my account
**So that** I can secure my account when finished shopping

**Acceptance Criteria:**
- "Sign out" link is visible when logged in
- Clicking "Sign out" logs user out
- User is redirected to login/home page
- User's name is no longer visible in header
- "Sign in" link replaces "Sign out" link

---

#### User Story 4: Password Recovery
**As a** registered user who forgot their password
**I want to** reset my password via email
**So that** I can regain access to my account

**Acceptance Criteria:**
- "Forgot your password?" link is visible on login page
- User can enter email address for password reset
- Clicking submit shows confirmation message
- Email is sent with password reset link (cannot verify in tests)

---

#### User Story 5: Login Validation - Invalid Credentials
**As a** user
**I want to** see error messages when login fails
**So that** I understand why I can't log in and can correct my input

**Acceptance Criteria:**
- Invalid email format shows validation error
- Wrong password shows "Authentication failed" error
- Nonexistent email shows "Authentication failed" error
- Empty email/password fields show validation errors
- User remains on login page after error

---

#### User Story 6: Registration Validation
**As a** user
**I want to** see validation errors during registration
**So that** I can correct my input and successfully create an account

**Acceptance Criteria:**
- Duplicate email shows "Email already registered" error
- Missing required fields show validation errors
- Invalid email format shows validation error
- Weak password shows validation error
- User remains on registration page after error

---

### Test Scenarios (14 Total)

#### Login Scenarios (7)
1. **Valid Login** - User logs in with valid email and password, redirected to My Account
2. **Invalid Email Format** - User enters invalid email, sees validation error
3. **Wrong Password** - User enters valid email but wrong password, sees "Authentication failed"
4. **Nonexistent Email** - User enters email not registered, sees "Authentication failed"
5. **Empty Email Field** - User leaves email empty, sees validation error
6. **Empty Password Field** - User leaves password empty, sees validation error
7. **Logout After Login** - User logs in, then logs out successfully

#### Registration Scenarios (5)
1. **Valid Registration** - New user registers with valid data, account created and logged in
2. **Duplicate Email** - User tries to register with existing email, sees error
3. **Missing Required Fields** - User submits form with missing fields, sees validation errors
4. **Invalid Email Format** - User enters invalid email, sees validation error
5. **Weak Password** - User enters weak password, sees validation error

#### Password Recovery Scenarios (2)
1. **Valid Email** - User enters registered email, sees confirmation message
2. **Invalid Email** - User enters invalid/nonregistered email, sees error or no confirmation

---

### Page Objects

#### AuthenticationPage
**Location:** `framework/pages/common/authentication_page.py`

**Purpose:** Handles login, "Create account" initiation, and forgot password

**Locators:**
- Email input field
- Password input field
- Sign in button
- Create account email input
- Create account button
- Forgot password link
- Error message container

**Methods:**
- `enter_login_email(email)`
- `enter_login_password(password)`
- `click_sign_in()`
- `get_login_error_message()`
- `enter_create_account_email(email)`
- `click_create_account()`
- `click_forgot_password()`
- `is_login_form_visible()`

---

#### RegistrationPage
**Location:** `framework/pages/common/registration_page.py`

**Purpose:** Handles registration form completion

**Locators:**
- Gender radio buttons (Mr./Mrs.)
- First name input
- Last name input
- Password input
- Address fields (address, city, state, zip, country)
- Phone input
- Register button
- Error message containers

**Methods:**
- `select_gender(gender)`
- `enter_first_name(name)`
- `enter_last_name(name)`
- `enter_password(password)`
- `enter_address_line1(address)`
- `enter_city(city)`
- `select_state(state)`
- `enter_zip_code(zip)`
- `select_country(country)`
- `enter_phone(phone)`
- `click_register()`
- `get_validation_errors()`
- `is_registration_form_visible()`

---

### Task Methods

**Location:** `framework/tasks/common_tasks.py`

#### CommonTasks.log_in(email, password)
**Purpose:** Complete login workflow

**Steps:**
1. Navigate to login page (if not already there)
2. Enter email
3. Enter password
4. Click sign in button
5. Wait for My Account page to load

---

#### CommonTasks.log_out()
**Purpose:** Log out of account

**Steps:**
1. Click "Sign out" link in header
2. Wait for redirect to home/login page

---

#### CommonTasks.register_new_user(user_data)
**Purpose:** Complete registration workflow

**Parameters:** `user_data` dict with keys: email, password, first_name, last_name, address, city, state, zip, country, phone

**Steps:**
1. Navigate to login page
2. Enter email in "Create account" section
3. Click "Create account" button
4. Wait for registration form to load
5. Fill all required fields
6. Click "Register" button
7. Wait for My Account page to load

---

#### CommonTasks.verify_logged_in()
**Purpose:** Assert user is logged in

**Steps:**
1. Check "Sign out" link is visible in header
2. Check user name is displayed in header

---

#### CommonTasks.verify_logged_out()
**Purpose:** Assert user is logged out

**Steps:**
1. Check "Sign in" link is visible in header
2. Check user name is NOT displayed in header

---

### Assumptions (To Validate During Implementation)

1. Successful login redirects to "My Account" page
2. Registration auto-logs user in (no separate login step)
3. "Sign out" link appears in header when logged in
4. Forgot password sends email (cannot verify in automated tests)
5. Duplicate email shows specific error message during registration
6. Validation errors are displayed inline near fields (or in error container)

---

## Section 3: Product Catalog Workflows

### User Stories (9 Total)

#### User Story 1: Browse Products by Category
**As a** shopper
**I want to** browse products by category (Women, Dresses, T-Shirts)
**So that** I can see all items available in that category and discover products

**Acceptance Criteria:**
- Category menu is visible in header navigation
- Clicking a category loads the corresponding product listing page
- Breadcrumbs show current category path
- Product count is displayed (e.g., "Showing 1-7 of 7 items")

---

#### User Story 2: Filter Products
**As a** shopper
**I want to** filter products by size, color, price, composition, style, manufacturer, and condition
**So that** I can narrow down results to find products that meet my specific needs

**Acceptance Criteria:**
- Filter sidebar displays all available filter categories:
  - Categories (subcategories: Tops, Dresses)
  - Size (S, M, L)
  - Color (Beige, White, Black, Orange, Blue, Green, Yellow)
  - Properties (Colorful Dress, Maxi Dress, Midi Dress, Short Dress, Short Sleeve)
  - Compositions (Cotton, Polyester, Viscose)
  - Styles (Casual, Dressy, Girly)
  - Availability (Not available, In stock)
  - Condition (New)
  - Price (slider range)
- Multiple filters can be applied simultaneously
- Product list updates dynamically when filters are applied
- Applied filters are visually indicated (checked boxes, selected colors)
- Product count updates to reflect filtered results

---

#### User Story 3: Sort Products
**As a** shopper
**I want to** sort products by price, name, or relevance
**So that** I can organize results in a way that helps me make decisions

**Acceptance Criteria:**
- Sorting dropdown is visible on product listing page
- Options include: Price (Low to High), Price (High to Low), Product Name (A-Z), Product Name (Z-A)
- Product list reorders immediately when sort option is selected
- Current sort option is displayed in dropdown

---

#### User Story 4: Change View Mode
**As a** shopper
**I want to** toggle between grid and list view modes
**So that** I can view products in my preferred layout

**Acceptance Criteria:**
- Grid/List toggle buttons are visible
- Grid view shows multiple products per row with images
- List view shows products in single column with more details
- View preference persists during browsing session

---

#### User Story 5: Quick View Product
**As a** shopper
**I want to** view product details in a Quick View modal
**So that** I can see key information without navigating away from the listing page

**Acceptance Criteria:**
- Hovering over product card reveals "Quick view" button overlaid on image
- Clicking "Quick view" opens modal with product details
- Modal displays: product name, price, reference, condition, description, size dropdown, color swatches, stock status, image gallery (thumbnails), social sharing buttons (Tweet, Facebook, Google+, Pinterest)
- Size and color can be selected in modal
- Modal can be closed with X button
- Background listing page is dimmed but still visible

---

#### User Story 6: View Full Product Details
**As a** shopper
**I want to** view complete product details on a dedicated page
**So that** I can see all information, reviews, and related products before purchasing

**Acceptance Criteria:**
- Clicking "More" button (visible on hover) navigates to full product detail page
- Detail page shows: large product images, price, description, size/color options, quantity selector, Add to Cart button, Add to Wishlist button, product specifications, reviews (if available)
- Breadcrumbs allow navigation back to category
- "Back to results" link available (if applicable)

---

#### User Story 7: Search Products
**As a** shopper
**I want to** search for products using keywords
**So that** I can quickly find specific items I'm looking for

**Acceptance Criteria:**
- Search bar is visible in header
- Entering keyword and clicking search icon/pressing Enter loads search results page
- Search results page displays products matching keyword
- Search results can be filtered and sorted like category pages
- "No results" message displays if no products match
- Search term is displayed on results page

---

#### User Story 8: Compare Products
**As a** shopper
**I want to** add products to a comparison list
**So that** I can evaluate multiple products side-by-side

**Acceptance Criteria:**
- "Compare" counter is visible in header (e.g., "Compare (0)")
- Hovering over product card reveals "Add to Compare" link
- Clicking "Add to Compare" adds product to comparison list
- Compare counter increments when products are added
- Clicking "Compare (X)" button/link shows comparison view with selected products
- Products can be removed from comparison
- Comparison view shows products side-by-side with key attributes

---

#### User Story 9: Add to Cart from Listing
**As a** shopper
**I want to** add a product to my cart directly from the listing page
**So that** I can quickly add items without viewing full details

**Acceptance Criteria:**
- Hovering over product card reveals "Add to cart" button
- Clicking "Add to cart" adds product to cart (default size/color if applicable)
- Cart counter in header increments
- Success confirmation is displayed (visual feedback - likely a modal or toast)
- If product is out of stock, "Add to cart" is disabled or shows "Out of stock" badge
- Color swatches visible on hover allow selecting color before adding

---

### Test Scenarios (MVP: 4 of 41)

**MVP Scope:** Testing 4 critical catalog scenarios (full 41 scenarios deferred to v2.0)

#### 1. Browse Category
**Scenario:** Navigate to Women category, verify products load, breadcrumbs display, product count shows

**Steps:**
1. Click "WOMEN" in navigation menu
2. Wait for product listing page to load
3. Verify breadcrumbs show "Home > Women"
4. Verify product count displays (e.g., "Showing 1-7 of 7 items")
5. Verify at least 1 product is displayed

---

#### 2. Filter by Multiple Criteria (Size + Color)
**Scenario:** Apply size "M" and color "Blue" filters, verify only matching products shown

**Steps:**
1. Navigate to Women category
2. Check "M" size filter
3. Wait for product list to update
4. Check "Blue" color filter
5. Wait for product list to update
6. Verify product count updates
7. Verify all visible products have size M and color Blue available

---

#### 3. Sort by Price
**Scenario:** Sort products by "Price: Low to High", verify products are ordered correctly

**Steps:**
1. Navigate to Women category
2. Click sort dropdown
3. Select "Price: Low to High"
4. Wait for products to reorder
5. Get all product prices
6. Verify prices are in ascending order

---

#### 4. Quick View Product
**Scenario:** Open Quick View modal for a product, verify details displayed

**Steps:**
1. Navigate to Women category
2. Hover over first product card
3. Wait for "Quick view" button to appear
4. Click "Quick view"
5. Wait for modal to open
6. Verify modal displays: product name, price, description, size dropdown, color swatches
7. Close modal
8. Verify modal is closed and listing page visible

---

**Deferred Scenarios (37 total):** Search, compare products, add to cart from listing, additional filter combinations, list/grid view toggle, full product detail page, etc.

---

### Page Objects (MVP)

#### ProductListPage
**Location:** `framework/pages/catalog/product_list_page.py`

**Purpose:** Handles product listing page interactions (category pages, search results)

**Locators:**
- Product cards container
- Product card elements (individual products)
- Filter checkboxes (size, color, etc.)
- Sort dropdown
- Product count text (e.g., "Showing 1-7 of 7 items")
- Breadcrumb navigation
- Product name links
- Product price elements
- "Quick view" button (appears on hover)

**Methods:**
- `get_product_count()` - Return number from "Showing X-Y of Z items"
- `get_product_names()` - Return list of all visible product names
- `get_product_prices()` - Return list of all visible product prices (as floats)
- `click_size_filter(size)` - Check size filter checkbox (e.g., "M")
- `click_color_filter(color)` - Check color filter checkbox (e.g., "Blue")
- `is_filter_selected(filter_name)` - Check if filter checkbox is checked
- `select_sort_option(option)` - Select sort option from dropdown
- `hover_over_product(product_index)` - Hover over product card by index
- `click_quick_view(product_index)` - Click "Quick view" button on product
- `is_quick_view_modal_visible()` - Check if Quick View modal is displayed
- `get_breadcrumbs()` - Return breadcrumb text

---

#### QuickViewModal
**Location:** `framework/pages/catalog/quick_view_modal.py`

**Purpose:** Handles Quick View modal interactions

**Locators:**
- Modal container
- Product name
- Product price
- Product description
- Size dropdown
- Color swatches
- Close button (X)

**Methods:**
- `get_product_name()` - Return product name from modal
- `get_product_price()` - Return product price from modal
- `get_product_description()` - Return product description text
- `select_size(size)` - Select size from dropdown
- `select_color(color)` - Click color swatch
- `close_modal()` - Click X button to close
- `is_modal_visible()` - Check if modal is displayed

---

### Task Methods (MVP)

**Location:** `framework/tasks/catalog_tasks.py`

#### CatalogTasks.browse_category(category_name)
**Purpose:** Navigate to a product category

**Parameters:** `category_name` - "Women", "Dresses", or "T-Shirts"

**Steps:**
1. Click category link in header navigation
2. Wait for product listing page to load
3. Verify breadcrumb shows correct category

**Returns:** ProductListPage instance

---

#### CatalogTasks.filter_products(filters)
**Purpose:** Apply multiple filters to product listing

**Parameters:** `filters` - dict with keys: "size", "color", "price_min", "price_max", etc.

**Steps:**
1. For each filter in dict:
   - If size: click size filter checkbox
   - If color: click color filter checkbox
2. Wait for product list to update after each filter
3. Verify product count updates

**Returns:** Updated product count

---

#### CatalogTasks.sort_products(sort_option)
**Purpose:** Sort products by specified option

**Parameters:** `sort_option` - "Price: Low to High", "Price: High to Low", "Name: A-Z", "Name: Z-A"

**Steps:**
1. Click sort dropdown
2. Select sort option
3. Wait for product list to reorder

**Returns:** List of product prices in new order

---

#### CatalogTasks.open_quick_view(product_index)
**Purpose:** Open Quick View modal for a product

**Parameters:** `product_index` - index of product in listing (0-based)

**Steps:**
1. Hover over product card
2. Wait for "Quick view" button to appear
3. Click "Quick view" button
4. Wait for modal to open

**Returns:** QuickViewModal instance

---

#### CatalogTasks.verify_sort_order(prices, order)
**Purpose:** Verify products are sorted correctly

**Parameters:**
- `prices` - list of product prices
- `order` - "ascending" or "descending"

**Steps:**
1. Convert prices to floats
2. Compare with sorted list
3. Assert order matches expected

**Returns:** True if verification passes

---

## Section 4: Shopping Cart Workflows

### User Stories (4 Total - MVP)

#### User Story 1: Add Product to Cart
**As a** shopper
**I want to** add a product to my shopping cart
**So that** I can save items for purchase

**Acceptance Criteria:**
- User can add product from product detail page
- User can select size and color before adding
- User can set quantity before adding
- Clicking "Add to Cart" adds product to cart
- Cart counter in header increments
- Success message/modal confirms product was added
- User can continue shopping or proceed to cart

---

#### User Story 2: View Shopping Cart
**As a** shopper
**I want to** view all items in my shopping cart
**So that** I can review my selections before checkout

**Acceptance Criteria:**
- Cart page displays all added products
- Each product shows: image, name, attributes (size/color), unit price, quantity, subtotal
- Cart summary shows: subtotal, shipping cost, tax, total
- Empty cart shows "Your cart is empty" message
- Cart counter in header matches number of items

---

#### User Story 3: Update Product Quantity
**As a** shopper
**I want to** change the quantity of items in my cart
**So that** I can adjust my order before purchasing

**Acceptance Criteria:**
- Quantity input/selector is available for each cart item
- User can increase or decrease quantity
- Quantity changes update subtotal immediately
- Quantity changes update cart total
- Cart counter in header updates to reflect new quantity

---

#### User Story 4: Remove Product from Cart
**As a** shopper
**I want to** remove items from my cart
**So that** I can manage my selections and only purchase what I want

**Acceptance Criteria:**
- "Remove" or "Delete" icon/link is visible for each cart item
- Clicking remove deletes item from cart
- Cart summary updates to reflect removal
- Cart counter in header decrements
- If last item removed, empty cart message displays

---

### Test Scenarios (MVP: 4 Total)

#### 1. Add Product to Cart
**Scenario:** Add a product to cart from product detail page, verify cart counter increments

**Steps:**
1. Navigate to Women category
2. Click on first product (or "More" button to go to detail page)
3. Select size "M"
4. Select color "Blue"
5. Set quantity to 1
6. Click "Add to Cart"
7. Wait for success confirmation (modal or message)
8. Verify cart counter in header shows "1"
9. Close confirmation modal (if present)

---

#### 2. Update Quantity
**Scenario:** Change product quantity in cart, verify totals update

**Steps:**
1. Add product to cart (quantity 1)
2. Navigate to cart page (click cart icon/link)
3. Locate quantity input for product
4. Change quantity from 1 to 2
5. Wait for cart to update
6. Verify product subtotal doubles
7. Verify cart total updates correctly
8. Verify cart counter shows "2"

---

#### 3. Remove Product from Cart
**Scenario:** Delete product from cart, verify it's removed

**Steps:**
1. Add product to cart
2. Navigate to cart page
3. Click "Remove" icon/link for product
4. Wait for cart to update
5. Verify product is no longer in cart
6. Verify cart counter shows "0"
7. Verify "Your cart is empty" message displays (or cart page shows empty state)

---

#### 4. View Cart Summary
**Scenario:** View cart with multiple items, verify totals calculate correctly

**Steps:**
1. Add 2 different products to cart
2. Navigate to cart page
3. Verify both products are listed with correct details (name, size, color, price, quantity)
4. Verify subtotal = sum of all product subtotals
5. Verify total includes subtotal + shipping (+ tax if applicable)
6. Verify cart counter shows total quantity of items

---

### Page Objects (MVP)

#### CartPage
**Location:** `framework/pages/cart/cart_page.py`

**Purpose:** Handles shopping cart page interactions

**Locators:**
- Cart items container
- Product rows (each cart item)
- Product name
- Product attributes (size, color)
- Product unit price
- Quantity input/selector
- Product subtotal
- Remove button/icon
- Cart summary section
- Subtotal amount
- Shipping amount
- Tax amount (if applicable)
- Total amount
- "Proceed to Checkout" button
- "Continue Shopping" link
- Empty cart message

**Methods:**
- `get_cart_items()` - Return list of all cart items (as dict objects)
- `get_product_name(item_index)` - Return product name for cart item
- `get_product_price(item_index)` - Return unit price for cart item
- `get_product_quantity(item_index)` - Return quantity for cart item
- `get_product_subtotal(item_index)` - Return subtotal for cart item
- `set_quantity(item_index, quantity)` - Update quantity for cart item
- `click_remove(item_index)` - Click remove button for cart item
- `get_cart_subtotal()` - Return subtotal from cart summary
- `get_shipping_cost()` - Return shipping cost from cart summary
- `get_cart_total()` - Return total from cart summary
- `is_cart_empty()` - Check if empty cart message is displayed
- `click_proceed_to_checkout()` - Click checkout button
- `click_continue_shopping()` - Click continue shopping link

---

#### AddToCartModal (or SuccessModal)
**Location:** `framework/pages/cart/add_to_cart_modal.py`

**Purpose:** Handles success confirmation modal after adding to cart

**Locators:**
- Modal container
- Success message/checkmark
- Product name
- Product attributes (size, color)
- Product quantity
- Product price
- "Continue Shopping" button
- "Proceed to Checkout" button
- Close button (X)

**Methods:**
- `is_modal_visible()` - Check if modal is displayed
- `get_success_message()` - Return success message text
- `get_product_name()` - Return added product name
- `click_continue_shopping()` - Click continue shopping button
- `click_proceed_to_checkout()` - Click proceed to checkout button
- `close_modal()` - Click X to close modal

---

### Task Methods (MVP)

**Location:** `framework/tasks/cart_tasks.py`

#### CartTasks.add_product_to_cart(product_index, size, color, quantity)
**Purpose:** Add a product to cart from listing/detail page

**Parameters:**
- `product_index` - index of product in listing
- `size` - size to select (e.g., "M")
- `color` - color to select (e.g., "Blue")
- `quantity` - quantity to add (default 1)

**Steps:**
1. Navigate to product detail page (if not already there)
2. Select size
3. Select color
4. Set quantity
5. Click "Add to Cart"
6. Wait for success modal/message
7. Verify success confirmation

**Returns:** AddToCartModal instance (or confirmation message)

---

#### CartTasks.view_cart()
**Purpose:** Navigate to shopping cart page

**Steps:**
1. Click cart icon/link in header
2. Wait for cart page to load

**Returns:** CartPage instance

---

#### CartTasks.update_cart_quantity(item_index, new_quantity)
**Purpose:** Update quantity for a cart item

**Parameters:**
- `item_index` - index of item in cart (0-based)
- `new_quantity` - new quantity value

**Steps:**
1. Navigate to cart page (if not already there)
2. Locate quantity input for item
3. Clear existing value
4. Enter new quantity
5. Trigger update (blur, press Enter, or click update button)
6. Wait for cart to recalculate

**Returns:** Updated cart total

---

#### CartTasks.remove_from_cart(item_index)
**Purpose:** Remove a product from cart

**Parameters:** `item_index` - index of item to remove (0-based)

**Steps:**
1. Navigate to cart page (if not already there)
2. Click remove button for item
3. Wait for cart to update
4. Verify item is no longer present

**Returns:** True if removal successful

---

#### CartTasks.verify_cart_total(expected_subtotal, expected_shipping, expected_total)
**Purpose:** Verify cart totals calculate correctly

**Parameters:**
- `expected_subtotal` - expected subtotal amount
- `expected_shipping` - expected shipping amount
- `expected_total` - expected total amount

**Steps:**
1. Get subtotal from cart summary
2. Get shipping from cart summary
3. Get total from cart summary
4. Assert all values match expected

**Returns:** True if verification passes

---

#### CartTasks.get_cart_item_count()
**Purpose:** Get number of items in cart from header counter

**Steps:**
1. Locate cart counter element in header
2. Extract number from text (e.g., "Cart (2)" → 2)

**Returns:** Integer count of cart items

---

## Section 5: Checkout Workflows

### User Stories (3 Total - MVP)

#### User Story 1: Complete Checkout as Registered User
**As a** registered customer
**I want to** complete the checkout process
**So that** I can purchase the items in my cart

**Acceptance Criteria:**
- User can click "Proceed to Checkout" from cart page
- Checkout flow includes: address selection/entry, shipping method, payment method, order review
- User can select from saved addresses (if registered)
- User can choose shipping method
- User can select payment method (bank wire, check)
- Order summary displays: items, quantities, prices, total
- Clicking "Confirm Order" completes purchase
- Order confirmation page displays with order number
- User receives confirmation message

---

#### User Story 2: Address Validation During Checkout
**As a** customer
**I want to** see validation errors if my address is incomplete
**So that** I can correct information and complete my order

**Acceptance Criteria:**
- Required address fields are marked
- Submitting incomplete address shows validation errors
- Error messages indicate which fields are missing/invalid
- User must correct errors before proceeding
- Valid address allows progression to next checkout step

---

#### User Story 3: Payment Method Selection
**As a** customer
**I want to** choose my payment method during checkout
**So that** I can pay using my preferred option

**Acceptance Criteria:**
- Payment method options are displayed (Bank wire, Check)
- User can select a payment method via radio button or click
- Selected payment method is visually indicated
- Payment method details/instructions are displayed when selected
- User can proceed to order confirmation with selected payment method

---

### Test Scenarios (MVP: 3 Total)

#### 1. Successful Checkout - Registered User (End-to-End Happy Path)
**Scenario:** Complete full checkout flow from cart to order confirmation

**Steps:**
1. Prerequisites: User is logged in, cart has 1+ products
2. Navigate to cart page
3. Click "Proceed to Checkout"
4. **Address Step:**
   - Verify address form/selection is displayed
   - Select existing address or enter new address
   - Click "Continue" or "Next"
5. **Shipping Step (if separate):**
   - Verify shipping options are displayed
   - Select a shipping method
   - Click "Continue"
6. **Payment Step:**
   - Verify payment method options displayed
   - Select "Bank wire transfer" or "Pay by check"
   - Click "Continue"
7. **Order Review:**
   - Verify order summary shows: products, quantities, prices, subtotal, shipping, total
   - Verify selected address is displayed
   - Verify selected payment method is displayed
8. Click "Confirm Order" or "Place Order"
9. Wait for order confirmation page
10. Verify success message displayed
11. Verify order number is displayed

---

#### 2. Address Validation Error
**Scenario:** Attempt checkout with incomplete address, verify validation errors

**Steps:**
1. Prerequisites: User is logged in, cart has 1+ products
2. Navigate to cart page
3. Click "Proceed to Checkout"
4. **Address Step:**
   - Leave required field empty (e.g., "City" or "Zip Code")
   - Click "Continue" or "Save Address"
5. Verify validation error message displays
6. Verify specific field is highlighted as invalid
7. Verify user cannot proceed to next step
8. Fill in missing field
9. Click "Continue"
10. Verify user proceeds to next checkout step

---

#### 3. Payment Method Selection
**Scenario:** Select different payment methods, verify selection persists

**Steps:**
1. Prerequisites: User is logged in, cart has 1+ products
2. Complete checkout through address and shipping steps
3. Arrive at payment step
4. Verify payment options are displayed (Bank wire, Check)
5. Select "Pay by bank wire"
6. Verify "Bank wire" is visually selected (radio checked or highlighted)
7. Verify bank wire instructions/details are displayed
8. Change selection to "Pay by check"
9. Verify "Check" is now selected
10. Verify check instructions/details are displayed
11. Proceed to order review
12. Verify selected payment method ("Check") is displayed in summary

---

### Page Objects (MVP)

#### CheckoutAddressPage
**Location:** `framework/pages/checkout/checkout_address_page.py`

**Purpose:** Handles address selection/entry during checkout

**Locators:**
- Delivery address section
- Billing address section
- Address selection dropdown (if saved addresses)
- "Use delivery address as billing" checkbox
- Address form fields:
  - Address line 1
  - Address line 2
  - City
  - State/Province
  - Zip code
  - Country dropdown
  - Phone
- Validation error messages
- "Continue" or "Proceed" button

**Methods:**
- `select_saved_address(address_name)` - Select from dropdown
- `enter_address_line1(address)` - Enter address
- `enter_city(city)` - Enter city
- `enter_zip(zip_code)` - Enter zip
- `select_country(country)` - Select country
- `select_state(state)` - Select state
- `enter_phone(phone)` - Enter phone
- `check_use_delivery_for_billing()` - Check checkbox
- `get_validation_errors()` - Return error messages
- `is_field_invalid(field_name)` - Check if field has error
- `click_continue()` - Click continue button

---

#### CheckoutShippingPage
**Location:** `framework/pages/checkout/checkout_shipping_page.py`

**Purpose:** Handles shipping method selection

**Locators:**
- Shipping method options (radio buttons)
- Shipping method names
- Shipping costs
- Delivery time estimates
- Terms of service checkbox
- "Continue" button

**Methods:**
- `select_shipping_method(method_name)` - Select shipping
- `is_shipping_method_selected(method_name)` - Check selection
- `get_shipping_cost(method_name)` - Get cost
- `check_terms_of_service()` - Check TOS checkbox
- `click_continue()` - Click continue

---

#### CheckoutPaymentPage
**Location:** `framework/pages/checkout/checkout_payment_page.py`

**Purpose:** Handles payment method selection

**Locators:**
- Payment method options (Bank wire, Check)
- Payment method radio buttons
- Payment instructions/details
- "Continue" button

**Methods:**
- `select_payment_method(method_name)` - Select payment
- `is_payment_method_selected(method_name)` - Check selection
- `get_payment_instructions()` - Get instructions text
- `click_continue()` - Click continue

---

#### OrderReviewPage
**Location:** `framework/pages/checkout/order_review_page.py`

**Purpose:** Handles final order review and confirmation

**Locators:**
- Order items summary
- Delivery address display
- Billing address display
- Shipping method display
- Payment method display
- Order totals (subtotal, shipping, tax, total)
- "Confirm Order" button

**Methods:**
- `get_order_items()` - Return list of products
- `get_delivery_address()` - Return delivery address text
- `get_payment_method()` - Return payment method
- `get_shipping_method()` - Return shipping method
- `get_order_subtotal()` - Return subtotal
- `get_order_total()` - Return total
- `click_confirm_order()` - Click confirm button

---

#### OrderConfirmationPage
**Location:** `framework/pages/checkout/order_confirmation_page.py`

**Purpose:** Handles order confirmation display

**Locators:**
- Success message/banner
- Order number
- Order summary
- Payment instructions

**Methods:**
- `get_success_message()` - Return confirmation message
- `get_order_number()` - Return order number
- `is_order_confirmed()` - Check if success displayed
- `get_order_total()` - Return total from confirmation

---

### Task Methods (MVP)

**Location:** `framework/tasks/checkout_tasks.py`

#### CheckoutTasks.complete_checkout_registered_user(user_data, payment_method)
**Purpose:** Complete full checkout flow (end-to-end)

**Parameters:**
- `user_data` - dict with address fields (optional if using saved)
- `payment_method` - "Bank wire transfer" or "Pay by check"

**Steps:**
1. Start from cart page
2. Click "Proceed to Checkout"
3. **Address step:** Select/enter address, click continue
4. **Shipping step:** Select shipping, click continue
5. **Payment step:** Select payment method, click continue
6. **Order review:** Verify details, click confirm
7. Capture order number

**Returns:** Order number (string)

---

#### CheckoutTasks.proceed_to_checkout()
**Purpose:** Navigate from cart to checkout

**Steps:**
1. Verify on cart page
2. Click "Proceed to Checkout"
3. Wait for checkout page to load

**Returns:** CheckoutAddressPage instance

---

#### CheckoutTasks.enter_address(address_data)
**Purpose:** Fill in address form

**Parameters:** `address_data` - dict with address fields

**Steps:**
1. Enter address fields
2. Click continue

**Returns:** Next checkout page

---

#### CheckoutTasks.select_payment_method(method_name)
**Purpose:** Select payment method

**Parameters:** `method_name` - "Bank wire transfer" or "Pay by check"

**Steps:**
1. Click payment option
2. Verify selected
3. Click continue

**Returns:** OrderReviewPage instance

---

#### CheckoutTasks.confirm_order()
**Purpose:** Complete order from review page

**Steps:**
1. Click "Confirm Order"
2. Wait for confirmation page

**Returns:** OrderConfirmationPage instance

---

#### CheckoutTasks.verify_order_confirmation(expected_total)
**Purpose:** Verify order was successfully placed

**Parameters:** `expected_total` - expected order total

**Steps:**
1. Verify success message displayed
2. Verify order number present
3. Verify total matches expected

**Returns:** Order number (string)

---

## Section 6: Account Management Workflows
**Deferred to v2.0**

---

## Section 7: Additional Workflows
**Deferred to v2.0** (wishlist, compare, contact form, reviews, etc.)

---

## Section 8: MCP Server Design

### Overview

The MCP (Model Context Protocol) server provides Claude Code with structured access to the test framework for execution, analysis, and reporting.

**Purpose:** Enable AI-assisted test execution and debugging workflows

**Architecture:**
```
Claude Code ←→ MCP Server ←→ Test Framework
               (Python)      (Pytest + Selenium)
```

**Reference:** See `docs/mcp-learning-notes.md` for detailed MCP concepts and rationale.

---

### MCP Server Components

#### 1. Server Implementation
**Location:** `mcp_server/server.py`

**Responsibilities:**
- Define MCP tools (5 core tools)
- Listen for tool calls from Claude Code
- Execute operations against test framework
- Return structured JSON responses

---

#### 2. Tool Executor
**Location:** `mcp_server/tool_executor.py`

**Responsibilities:**
- Execute pytest commands
- Parse pytest output
- Locate test artifacts (screenshots, logs, reports)
- Return structured results

---

#### 3. Test Discovery
**Location:** `mcp_server/test_discovery.py`

**Responsibilities:**
- Scan tests/ directory
- Parse test files for test functions
- Organize tests by workflow
- Return test metadata

---

#### 4. Failure Analyzer
**Location:** `mcp_server/failure_analyzer.py`

**Responsibilities:**
- Parse pytest failure output
- Extract error messages, tracebacks
- Locate related artifacts
- Generate failure analysis structure

---

#### 5. Coverage Calculator
**Location:** `mcp_server/coverage_calculator.py`

**Responsibilities:**
- Read Phase 0 design doc for scenario counts
- Scan tests/ for implemented tests
- Match tests to scenarios
- Calculate coverage percentages

---

### MCP Tools (5 Core Tools)

#### Tool 1: `run_test`

**Purpose:** Execute a specific test and return structured results

**Parameters:**
```python
{
  "test_name": str,          # Test function name (e.g., "test_valid_login")
  "environment": str,        # "local", "staging", "prod" (default: "local")
  "browser": str,            # "chrome", "firefox" (optional override)
  "headless": bool           # true/false (optional override)
}
```

**Returns:**
```python
{
  "status": "passed" | "failed" | "error",
  "duration": float,         # seconds
  "output": str,             # pytest terminal output
  "failures": [
    {
      "test": str,          # Test name
      "error": str,         # Error message
      "traceback": str      # Full traceback
    }
  ],
  "screenshots": [str],      # Paths to screenshots (if failure)
  "logs": str,               # Path to log file
  "html_report": str         # Path to HTML report
}
```

**Implementation Approach:**
1. Construct pytest command:
   ```bash
   pytest tests/{workflow}/test_{test_name}.py
   --html=_reports/report_{timestamp}.html
   --browser={browser}
   --headless={headless}
   ```
2. Execute subprocess, capture stdout/stderr
3. Parse pytest exit code (0=pass, 1=fail, other=error)
4. If failure: locate screenshots in `screenshots/` directory
5. Locate log file in `logs/` directory
6. Return structured JSON

**Value:** Structured test execution instead of raw Bash output

---

#### Tool 2: `list_tests`

**Purpose:** Discover all available tests organized by workflow

**Parameters:**
```python
{
  "workflow": str | None     # Filter by "auth", "catalog", "cart", "checkout" (optional)
}
```

**Returns:**
```python
{
  "workflows": {
    "authentication": [
      "test_valid_login",
      "test_invalid_credentials",
      "test_registration",
      "test_logout"
    ],
    "catalog": [
      "test_browse_category",
      "test_filter_products",
      "test_sort_by_price",
      "test_quick_view"
    ],
    "cart": [
      "test_add_to_cart",
      "test_update_quantity",
      "test_remove_from_cart",
      "test_view_cart_summary"
    ],
    "checkout": [
      "test_complete_checkout",
      "test_address_validation",
      "test_payment_selection"
    ]
  },
  "total_tests": 15
}
```

**Implementation Approach:**
1. Scan `tests/` directory structure:
   ```
   tests/
     auth/
       test_valid_login.py
       test_registration.py
     catalog/
       test_browse_category.py
     ...
   ```
2. For each test file:
   - Read file contents
   - Parse functions starting with `test_`
   - Extract test names
3. Group by workflow folder name
4. Return organized structure

**Value:** Test discovery - Claude knows what tests exist

---

#### Tool 3: `get_test_report`

**Purpose:** Retrieve HTML test report with parsed summary

**Parameters:**
```python
{
  "test_name": str | None,   # Specific test (optional)
  "run_id": str | None,      # Specific run timestamp (optional)
  "latest": bool             # Get most recent report (default: true)
}
```

**Returns:**
```python
{
  "report_path": str,        # Absolute path to HTML report
  "url": str,                # file:// URL to open in browser
  "summary": {
    "total": int,
    "passed": int,
    "failed": int,
    "skipped": int,
    "duration": float        # seconds
  },
  "failures": [
    {
      "test": str,
      "reason": str
    }
  ],
  "timestamp": str           # Report generation time
}
```

**Implementation Approach:**
1. Scan `_reports/` directory for HTML reports
2. If `latest=true`: Get most recent by timestamp
3. If `test_name` provided: Filter reports containing test name
4. Parse HTML report using BeautifulSoup or regex:
   - Extract summary stats from report header
   - Extract failure details from results table
5. Construct file:// URL for browser access
6. Return structured data

**Value:** Access test reports with parsed summary stats

---

#### Tool 4: `analyze_failure`

**Purpose:** Deep analysis of test failure with AI-powered debugging insights

**This is the "killer feature" of the MCP server**

**Parameters:**
```python
{
  "test_name": str,          # Test to analyze
  "run_id": str | None       # Specific run (optional, defaults to latest)
}
```

**Returns:**
```python
{
  "test": str,
  "status": "failed",
  "error_type": str,         # "ElementNotFound", "Timeout", "AssertionError", etc.
  "error_message": str,      # Short error message
  "screenshot": str | None,  # Path to failure screenshot
  "log_excerpt": str,        # Relevant log lines (last 50 lines)
  "traceback": str,          # Full Python traceback
  "duration": float,
  "timestamp": str,
  "analysis": {
    "likely_cause": str,     # Human-readable explanation
    "evidence": [str],       # List of evidence points
    "suggestions": [str]     # List of suggested fixes
  },
  "related_failures": [str]  # Other tests that failed similarly
}
```

**Implementation Approach:**
1. **Locate Failure Artifacts:**
   - Find latest test run for `test_name`
   - Read pytest output file or HTML report
   - Locate screenshot: `screenshots/test_{test_name}_failure_{timestamp}.png`
   - Read log file: `logs/test_{timestamp}.log`

2. **Parse Error Information:**
   - Extract error type from traceback
   - Extract error message
   - Get last 50 lines of log (most relevant)
   - Get full traceback

3. **Pattern Recognition (Pre-Analysis):**
   - **ElementNotFound** → "Locator issue or page didn't load"
   - **Timeout** → "Wait/performance issue or slow network"
   - **AssertionError** → "Business logic issue or expected behavior changed"
   - **StaleElementReference** → "DOM changed during test execution"
   - **NoSuchWindow** → "Popup/window handling issue"

4. **Generate Analysis Structure:**
   ```python
   analysis = {
     "likely_cause": "...",
     "evidence": [
       "Screenshot shows 404 page instead of expected page",
       "Log shows 'Connection timeout after 30s'",
       "Previous test run was successful (regression)"
     ],
     "suggestions": [
       "Check if automationpractice.pl is accessible",
       "Verify BASE_URL in .env",
       "Increase EXPLICIT_WAIT timeout",
       "Update locator if site structure changed"
     ]
   }
   ```

5. **Find Related Failures:**
   - Scan recent test runs
   - Identify tests with same error type
   - Return list of related test names

**Value:** Pre-processed failure data enables Claude's LLM to provide better debugging suggestions

---

#### Tool 5: `get_coverage`

**Purpose:** Show test coverage by workflow with gap analysis

**Parameters:**
```python
{
  "workflow": str | None     # Filter by workflow (optional)
}
```

**Returns:**
```python
{
  "workflows": {
    "authentication": {
      "scenarios_designed": 14,
      "tests_implemented": 4,
      "coverage_percent": 28.6,
      "tested_scenarios": [
        "Valid login",
        "Invalid credentials",
        "Registration",
        "Logout"
      ],
      "untested_scenarios": [
        "Password recovery",
        "Empty fields validation",
        "Duplicate email registration",
        "..."
      ]
    },
    "catalog": {
      "scenarios_designed": 41,
      "tests_implemented": 4,
      "coverage_percent": 9.8,
      "tested_scenarios": [
        "Browse category",
        "Filter by multiple criteria",
        "Sort by price",
        "Quick view product"
      ],
      "untested_scenarios": [
        "Search products",
        "Compare products",
        "Add to cart from listing",
        "..."
      ]
    },
    "cart": {
      "scenarios_designed": 4,
      "tests_implemented": 4,
      "coverage_percent": 100.0,
      "tested_scenarios": [
        "Add to cart",
        "Update quantity",
        "Remove from cart",
        "View cart summary"
      ],
      "untested_scenarios": []
    },
    "checkout": {
      "scenarios_designed": 3,
      "tests_implemented": 3,
      "coverage_percent": 100.0,
      "tested_scenarios": [
        "Complete checkout",
        "Address validation",
        "Payment selection"
      ],
      "untested_scenarios": []
    }
  },
  "overall_coverage": {
    "total_scenarios_designed": 62,
    "total_tests_implemented": 15,
    "coverage_percent": 24.2
  }
}
```

**Implementation Approach:**
1. **Read Phase 0 Design Doc:**
   - Parse `docs/0-phase0-test-design.md`
   - Count scenarios in each section:
     - Section 2 (Auth): 14 scenarios
     - Section 3 (Catalog): 41 scenarios (4 MVP, 37 deferred)
     - Section 4 (Cart): 4 scenarios
     - Section 5 (Checkout): 3 scenarios

2. **Scan Implemented Tests:**
   - Use `list_tests()` logic to discover implemented tests
   - Count tests per workflow

3. **Calculate Coverage:**
   - `coverage_percent = (tests_implemented / scenarios_designed) * 100`

4. **Match Tests to Scenarios:**
   - By naming convention: `test_valid_login` → "Valid login" scenario
   - Extract scenario names from test docstrings (if present)

5. **Identify Gaps:**
   - List scenarios from Phase 0 doc
   - Mark which ones have corresponding tests
   - Return untested scenarios

**Value:** Gap analysis shows what's tested vs what's planned

---

### Configuration

#### MCP Server Configuration
**Location:** `.claude/settings.json` (local, not committed to repo)

```json
{
  "mcpServers": {
    "py-selenium-framework": {
      "command": "python",
      "args": ["mcp_server/server.py"],
      "cwd": "D:/my_ai_projects/py_sel_framework_mcp"
    }
  }
}
```

---

### Implementation Notes

**Dependencies:**
```python
# mcp_server/requirements.txt
mcp>=0.1.0              # MCP SDK
pytest>=7.4.0           # Pytest for parsing
beautifulsoup4>=4.12.0  # HTML report parsing
```

**Error Handling:**
- All tools return structured errors:
  ```python
  {
    "error": true,
    "error_type": "TestNotFound" | "ExecutionError" | "ParseError",
    "message": "Detailed error message"
  }
  ```

**Logging:**
- MCP server logs to `mcp_server/logs/mcp_server.log`
- Log all tool calls (params + results)
- Log errors for debugging

**Testing MCP Tools:**
- Create `mcp_server/tests/test_mcp_tools.py`
- Unit tests for each tool
- Mock pytest execution for predictable testing

---

### Usage Examples (Claude Workflows)

#### Workflow 1: Run Test and Analyze Failure
```
You: "Run my login test and tell me why it failed"

Claude:
1. Calls: run_test("test_valid_login")
   → Returns: status="failed"
2. Calls: analyze_failure("test_valid_login")
   → Returns: Error details, screenshot, suggestions
3. Reads screenshot (via built-in Read tool)
4. Responds: "Your login test failed because element '#login-button'
              wasn't found. The screenshot shows a 404 page. The site
              may be down or the URL is incorrect."
```

---

#### Workflow 2: Check Test Coverage
```
You: "What's my test coverage?"

Claude:
1. Calls: get_coverage()
   → Returns: Coverage by workflow
2. Responds: "You have 15 tests covering 24% of designed scenarios.
              - Auth: 28% (4/14)
              - Catalog: 10% (4/41)
              - Cart: 100% (4/4)
              - Checkout: 100% (3/3)

              Want me to prioritize which gaps to fill?"
```

---

#### Workflow 3: Run All Tests and Report
```
You: "Run all my tests and summarize the results"

Claude (using Agent):
1. Calls: list_tests() → Gets all 15 test names
2. For each test:
   - Calls: run_test(test_name)
3. Compiles results
4. For failures:
   - Calls: analyze_failure(test_name)
5. Responds: "Ran 15 tests in 3 minutes:
              - 13 passed
              - 2 failed: test_checkout (timeout), test_cart (assertion)

              Here's the failure analysis for each..."
```

---

### Deferred to v2.0

**Additional Tools (Nice to Have):**
- `run_workflow_tests(workflow)` - Run all tests in a workflow
- `get_test_data(data_type)` - Show available test data
- `scaffold_test_from_scenario(scenario_id)` - Generate test boilerplate
- `validate_page_object_locators(page_object_name)` - Check locator health

---

**Last Updated:** 2025-01-11
**Status:** MCP server design complete, ready for Phase 1 (Test Plan)

---

## Appendix: QA 4D Framework Adaptations

**Discovery:** The 4D Framework (software development) doesn't map cleanly to QA process.

### Software Dev vs QA Phase 0

**Software Dev Phase 0 (Design Discussion):**
- Design the feature (UX/UI, architecture)
- Make technical decisions
- Output: Design decisions → feed into PRD

**QA Phase 0 (Requirements Gathering & Test Design):**
- Gather requirements → Write user stories
- Derive test scenarios from user stories
- Design framework to support tests (page objects, tasks)
- Output: Test design document → feed into Test Plan

### Key Difference

**Software:** Start with architecture, design how to build it
**QA:** Start with requirements/user stories, design what to test and how to test it

**QA Process Flow:**
1. Identify features/workflows (from business requirements)
2. Write user stories (what users need to do)
3. Derive test scenarios (how to verify each user story)
4. Design page objects/tasks (framework architecture to support tests)

**Note:** Normal QA workflow assumes user stories come from Business/PM. For this project, we're acting as BA/PM + QA (no business stakeholder). This is documented for future QA 4D Framework docs.

---

**Last Updated:** 2025-01-11
**Status:** Section 3 user stories complete, test scenarios pending
