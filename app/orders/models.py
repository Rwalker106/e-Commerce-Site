# app/orders/models.py

from datetime import datetime, timezone
from app.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'

    # --- Identity ---
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # --- Status ---
    status     = db.Column(db.String(32), nullable=False, default='pending')
    # pending → paid → shipped → delivered
    # or: pending → failed
    # or: paid → refunded

    # --- Financials (all in cents) ---
    subtotal   = db.Column(db.Integer, nullable=False)  # before tax/shipping
    tax        = db.Column(db.Integer, nullable=False, default=0)
    shipping   = db.Column(db.Integer, nullable=False, default=0)
    total      = db.Column(db.Integer, nullable=False)  # what Stripe charged

    # --- Stripe ---
    stripe_payment_intent_id = db.Column(db.String(255), nullable=True, unique=True)

    # --- Shipping Address ---
    shipping_name    = db.Column(db.String(128), nullable=True)
    shipping_email   = db.Column(db.String(254), nullable=True)
    shipping_address = db.Column(db.String(255), nullable=True)
    shipping_city    = db.Column(db.String(64),  nullable=True)
    shipping_state   = db.Column(db.String(64),  nullable=True)
    shipping_zip     = db.Column(db.String(16),  nullable=True)
    shipping_country = db.Column(db.String(64),  nullable=True)

    # --- Timestamps ---
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    # --- Relationships ---
    user  = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order',
                            cascade='all, delete-orphan')

    # --- Helpers ---
    def display_total(self):
        return f'${self.total / 100:.2f}'

    def display_subtotal(self):
        return f'${self.subtotal / 100:.2f}'

    def __repr__(self):
        return f'<Order {self.id} — {self.status} — {self.display_total()}>'


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id         = db.Column(db.Integer, primary_key=True)
    order_id   = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)

    # --- Snapshot of product at time of purchase ---
    product_name  = db.Column(db.String(128), nullable=False)
    product_sku   = db.Column(db.String(32),  nullable=False)
    unit_price    = db.Column(db.Integer,     nullable=False)  # cents, at time of purchase
    quantity      = db.Column(db.Integer,     nullable=False)
    line_total    = db.Column(db.Integer,     nullable=False)  # unit_price * quantity

    # --- Relationship ---
    product = db.relationship('Product', backref='order_items')

    def display_unit_price(self):
        return f'${self.unit_price / 100:.2f}'

    def display_line_total(self):
        return f'${self.line_total / 100:.2f}'

    def __repr__(self):
        return f'<OrderItem {self.product_sku} x{self.quantity}>'