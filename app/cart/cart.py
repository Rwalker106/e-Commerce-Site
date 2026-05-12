# app/cart/cart.py

from flask import session
from app.store.models import Product


class Cart:
    """
    Wraps Flask's session to provide a clean cart interface.
    The session stores: {'cart': {'product_id': {'quantity': n}}}
    """

    CART_KEY = 'cart'

    def __init__(self):
        if self.CART_KEY not in session:
            session[self.CART_KEY] = {}

    # --- Internal ---

    def _get_cart(self):
        return session[self.CART_KEY]

    def _save(self):
        """Tell Flask the session has been modified."""
        session.modified = True

    # --- Public Interface ---

    def add(self, product_id, quantity=1):
        cart = self._get_cart()
        key = str(product_id)

        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            cart[key] = {'quantity': quantity}

        self._save()

    def remove(self, product_id):
        cart = self._get_cart()
        key = str(product_id)

        if key in cart:
            del cart[key]
            self._save()

    def update(self, product_id, quantity):
        cart = self._get_cart()
        key = str(product_id)

        if quantity <= 0:
            self.remove(product_id)
        elif key in cart:
            cart[key]['quantity'] = quantity
            self._save()

    def clear(self):
        session[self.CART_KEY] = {}
        self._save()

    def get_items(self):
        """
        Return a list of dicts with product + quantity.
        Fetches live product data from the DB.
        Silently removes any product IDs that no longer exist.
        """
        cart = self._get_cart()
        if not cart:
            return []

        product_ids = [int(k) for k in cart.keys()]
        products = Product.query.filter(
            Product.id.in_(product_ids),
            Product.is_active == True
        ).all()

        # Build a lookup dict for O(1) access
        product_map = {str(p.id): p for p in products}

        items = []
        stale_keys = []

        for key, data in cart.items():
            product = product_map.get(key)
            if product is None:
                stale_keys.append(key)
                continue

            quantity = data['quantity']
            items.append({
                'product': product,
                'quantity': quantity,
                'line_total': product.price * quantity,  # cents
            })

        # Clean up any product IDs that no longer exist
        for key in stale_keys:
            del cart[key]
        if stale_keys:
            self._save()

        return items

    def total(self):
        """Return cart total in cents."""
        return sum(item['line_total'] for item in self.get_items())

    def display_total(self):
        """Return cart total as a formatted string."""
        return f'${self.total() / 100:.2f}'

    def item_count(self):
        """Return total number of individual items."""
        cart = self._get_cart()
        return sum(data['quantity'] for data in cart.values())

    def is_empty(self):
        return self.item_count() == 0