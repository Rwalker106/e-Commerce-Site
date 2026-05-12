import json
import os
from datetime import datetime, timezone

from app import create_app
from app.extensions import db
from app.store.models import Product

app = create_app('development')

def cents(value):
    """Helper function to convert dollars to cents. E.g. 19.99 -> 1999"""
    if value is None:
        return None
    return round(value * 100)

def parse_dt(iso_string):
    if iso_string is None:
        return datetime.now(timezone.utc)
    return datetime.fromisoformat(iso_string.replace('Z', '+00:00')) # handle Zulu time (UTC) by replacing 'Z' with '+00:00'

with app.app_context():
    
    
    # Load products from JSON file
    json_path = os.path.join(os.path.dirname(__file__), 'products.json')
    with open(json_path, 'r', encoding='utf-8') as f:
        products_data = json.load(f)
        
    if Product.query.count() > 0:
        print("Products already exist in the database. Skipping seeding.")
    else:
        products = []
        for p in products_data:
            product = Product(
                # Identity
                sku=p['sku'],
                slug=p['slug'],
                name=p['name'],
                brand=p.get('brand'),

                # Description & categorisation
                description=p.get('description'),
                category=p.get('category'),
                subcategory=p.get('subcategory'),
                image_prompt=p.get('image_prompt'),

                # Pricing — convert floats to cents
                price=cents(p['price']),
                discount_price=cents(p.get('discount_price')),
                cost=cents(p.get('cost')),

                # Inventory
                stock=p.get('stock', 0),
                reorder_level=p.get('reorder_level', 0),

                # Variants & media
                variants=p.get('variants'),
                images=p.get('images', []),

                # Merchandising
                is_active=p.get('active', True),
                featured=p.get('featured', False),
                tax_class=p.get('tax_class', 'standard'),

                # Social proof
                rating=p.get('rating'),
                review_count=p.get('review_count', 0),

                # Timestamps — preserve the original dates from the JSON
                created_at=parse_dt(p.get('created_at')),
            )
            products.append(product)
        db.session.add_all(products)
        db.session.commit()
        print(f"Seeded {len(products)} products into the database.")