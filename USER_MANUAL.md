# MyStore — User Manual

This manual covers everything a shopper or store administrator needs to use MyStore.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Browsing Products](#2-browsing-products)
3. [Shopping Cart](#3-shopping-cart)
4. [Checkout](#4-checkout)
5. [Payment](#5-payment)
6. [Your Orders](#6-your-orders)
7. [Admin Guide](#7-admin-guide)

---

## 1. Getting Started

### Creating an account

1. Click **Register** in the top-right navigation bar.
2. Enter your email address, choose a username, and set a password.
3. Click **Create Account**.

You will be logged in automatically after registering.

### Logging in

1. Click **Login** in the top-right navigation bar.
2. Enter your email address and password.
3. Click **Log In**.

### Logging out

Click **Logout** in the navigation bar. Your cart is tied to your browser session and will be cleared when you log out.

---

## 2. Browsing Products

The home page (`/`) is the main product listing. It shows all active products as cards.

### Searching

Type a word or phrase into the search bar at the top of the page and press **Search** (or hit Enter). The search looks across product names, descriptions, brands, and categories. The results update immediately and show the number of matches found.

To clear a search, click **Clear filters** next to the results count, or delete your query and search again.

### Filtering by category

Below the search bar is a row of category pills (e.g. Clothing, Electronics). Click any pill to show only products in that category. The active category is highlighted in blue.

You can combine search and category: searching "blue" while the "Clothing" category is selected shows only clothing items matching "blue".

Click **All** to return to the full listing.

### Product cards

Each card shows:

- Product image (or a placeholder icon if no image is set)
- Category / subcategory
- Product name and brand
- A short description
- Price — with the original price struck through and a red **Sale** badge if the item is discounted
- Star rating and review count
- An **Out of stock** badge if the item has no remaining stock

Click **View Product** on any card to open the full product detail page.

### Product detail page

The detail page shows the full description, all available variants (e.g. sizes, colours), and the add-to-cart form. Use the breadcrumb at the top to navigate back to the category listing.

---

## 3. Shopping Cart

### Adding an item

On the product detail page, enter the quantity you want (the maximum is limited to the available stock) and click **Add to Cart**. A confirmation message will appear and the cart count in the navbar will update.

### Viewing the cart

Click **Cart (n)** in the navigation bar at any time, where *n* is the number of items currently in your cart.

The cart page shows each item with its unit price, a quantity field, and the line total.

### Updating quantities

Change the number in the quantity field next to any item and click **Update**. Setting the quantity to **0** removes the item.

### Removing an item

Click **Remove** next to the item you want to delete.

### Clearing the cart

Click **Clear Cart** at the bottom of the summary panel to remove all items at once.

### Continuing to checkout

When you are ready, click **Proceed to Checkout** in the order summary panel on the right.

---

## 4. Checkout

### Shipping details

Fill in the shipping form:

| Field | Notes |
|---|---|
| Full Name | The recipient's full name |
| Email | Confirmation email will be sent here |
| Street Address | House number and street |
| City | |
| State | Two-letter state code (e.g. CA) |
| ZIP Code | Five-digit ZIP |
| Country | Defaults to US |

All fields are required. If you are logged in your email address is pre-filled.

Click **Continue to Payment** when done.

---

## 5. Payment

The payment page shows a final order breakdown (subtotal, tax, and total) above the card entry form, which is powered by Stripe.

### Entering card details

Type your card number, expiry date, and CVC into the secure card fields provided by Stripe. Your card details are transmitted directly to Stripe and never stored on this site.

Click **Pay $XX.XX** to submit the payment.

### After payment

If the payment succeeds you will be redirected to an order confirmation page showing your order number and total charged. From there you can view the full order details or continue shopping.

If there is a payment error (e.g. insufficient funds, incorrect CVC) an error message will appear below the card form. Correct the details and try again — no charge will have been made.

### Test cards (development / staging only)

| Card number | Result |
|---|---|
| 4242 4242 4242 4242 | Approved |
| 4000 0000 0000 9995 | Declined |

Use any future expiry date and any 3-digit CVC when testing.

---

## 6. Your Orders

### Viewing order history

Click **My Orders** in the navigation bar (only visible when logged in). Your orders are listed in reverse chronological order, each showing:

- Order number
- Date placed
- Status badge (see below)
- Number of items
- Total amount

### Order statuses

| Status | Meaning |
|---|---|
| Pending | Payment not yet confirmed |
| Paid | Payment received, order being processed |
| Shipped | Order has been dispatched |
| Delivered | Order has been delivered |
| Refunded | A refund has been issued |
| Failed | Payment failed |

### Viewing an order

Click **View Details** on any order card to see the full breakdown: itemised table, shipping address, and payment reference.

You can only view your own orders. Attempting to access another user's order will return a 403 error.

---

## 7. Admin Guide

The admin panel is available at `/admin/` and is restricted to users with admin privileges. An **Admin** link appears in the navigation bar for admin accounts.

### Dashboard

The dashboard shows two headline stats (total products and total orders) and a table of the five most recent orders. Use the **Manage Products** and **All Orders** buttons to navigate to the full management views.

### Managing products

Navigate to **Admin > Manage Products** (`/admin/products`).

The products table lists every product with its SKU, price, stock level, and active status. From here you can:

- **Edit** — opens the product form pre-filled with the current values.
- **Deactivate** — hides the product from the storefront immediately (the product record is kept in the database). A deactivated product does not appear in search results or category listings.

#### Adding a new product

Click **+ Add Product** at the top of the products page. Fill in the form:

| Field | Notes |
|---|---|
| Name | Display name shown to customers |
| Brand | Brand or manufacturer name |
| SKU | Unique stock-keeping unit code |
| Slug | URL-friendly identifier (e.g. `blue-t-shirt-lg`) — must be unique |
| Category | Top-level category (e.g. Clothing) |
| Subcategory | Sub-level category (e.g. T-Shirts) |
| Price ($) | Enter in dollars (e.g. `19.99`) — stored internally in cents |
| Stock | Available quantity |
| Description | Full product description shown on the detail page |
| Active | Checked = visible on storefront, unchecked = hidden |

Click **Create Product** to save.

#### Editing a product

Click **Edit** next to any product. All fields are pre-filled. Make your changes and click **Save Changes**. To cancel without saving, click **Cancel**.

### Managing orders

Navigate to **Admin > All Orders** (`/admin/orders`).

The orders table shows every order across all customers, sorted newest first. Click **View** to open the order detail page.

#### Updating an order status

On the order detail page, use the **Update Status** dropdown to select a new status and click **Update Status**. Valid transitions are:

```
pending -> paid -> shipped -> delivered
                           -> refunded
       -> failed
```

The change takes effect immediately and is reflected in the customer's order history.
