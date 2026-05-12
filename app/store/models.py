from app.extensions import db
from datetime import datetime, timezone

class Product(db.Model):
    __tablename__ = 'products'
    
    # ---  Identity  ---
    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(120), unique=True, nullable=False) # Stock Keeping Unit - a unique identifier for each product
    slug = db.Column(db.String(120), unique=True, nullable=False) # URL-friendly version of the product name, e.g. "red-t-shirt"
    name = db.Column(db.String(120), nullable=False)
    brand = db.Column(db.String(120), nullable=True)
    
    # ---  Description and categorization  ---
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(120), nullable=True)
    subcategory = db.Column(db.String(120), nullable=True)
    # --- Weight, dimensions, and other physical attributes could be added here in the future if needed ---
    weight = db.Column(db.Float, nullable=True) # in kilograms
    
    # ---  Pricing and cost  ---
    price = db.Column(db.Integer, nullable=False) # cents - NOT a float
    discount_price = db.Column(db.Integer, nullable=True) # cents - NOT a float
    cost = db.Column(db.Integer, nullable=True) # cents - NOT a float. This is the cost to the store, not the price to the customer. It's used for calculating profit margins and other analytics, but it's not shown to customers. 
    
    # ---  Inventory ---
    stock = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=0) # when stock falls to this level, we should reorder more
    
    # --- Variants & Media ---
    variants = db.Column(db.JSON, nullable=True) # e.g. "color: red, size: M; color: red, size: L; color: blue, size: M; color: blue, size: L"
    images = db.Column(db.JSON, nullable=True) # list of image URLs, stored as JSON array. We can use db.JSON type to store a list of strings (image URLs) in a single column. This is more flexible than having a fixed number of image_url columns (e.g. image_url_1, image_url_2, etc.) because we can have any number of images for each product without changing the database schema.
    image_prompt = db.Column(db.Text, nullable=True) # the prompt used to generate the product image with AI. This is stored for reference and potential future use (e.g. to regenerate the image if needed), but it's not shown to customers.
    
    # --- Merchandising ---
    is_active = db.Column(db.Boolean, default=True) 
    featured = db.Column(db.Boolean, default=False) # whether this product should be featured on the homepage or in special promotions
    tax_class = db.Column(db.String(120), nullable=True) # e.g. "standard", "reduced", "zero". This can be used to calculate tax for the product based on the customer's location and the applicable tax rates.
    
    # --- Social Proof
    rating = db.Column(db.Float, nullable=True) # average customer rating from 1.0 to 5.0
    review_count = db.Column(db.Integer, default=0) # number of customer reviews, used to calculate average rating and show review count on product detail page
    
    # ---  Timestamps  ---
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    
    # ---  Helper methods  ---
    @property
    def display_price(self):
        """Convert integer cents to display string: 1999 -> $19.99"""
        p = self.discount_price if self.discount_price is not None else self.price
        return f'${p / 100:.2f}'
    
    def is_on_sale(self):
        return self.discount_price is not None 
    
    def in_stock(self):
        return self.stock > 0
    
    def __repr__(self):
        return f'<Product {self.id}: {self.name}>'
