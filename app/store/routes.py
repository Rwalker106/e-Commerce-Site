# app/store/routes.py
from flask import render_template, request
from . import store_bp
from ..extensions import db
from .models import Product
from ..auth.models import User
from sqlalchemy import distinct

@store_bp.route('/')
def index():
    search_query = request.args.get('q', '').strip()
    selected_category = request.args.get('category', '')

    categories = [
        row[0] for row in
        db.session.query(distinct(Product.category))
        .filter(Product.is_active, Product.category.isnot(None))
        .order_by(Product.category)
        .all()
    ]

    query = Product.query.filter_by(is_active=True)

    if search_query:
        query = query.filter(
            db.or_(
                Product.name.ilike(f'%{search_query}%'),
                Product.description.ilike(f'%{search_query}%'),
                Product.brand.ilike(f'%{search_query}%'),
                Product.category.ilike(f'%{search_query}%'),
            )
        )

    if selected_category:
        query = query.filter(Product.category == selected_category)

    products = query.order_by(Product.name).all()

    return render_template(
        'store/index.html',
        products=products,
        categories=categories,
        search_query=search_query,
        selected_category=selected_category,
    )

@store_bp.route('/product/<int:id>')
def product_detail(id):
    product = Product.query.get_or_404(id)
    if not product.is_active:
        abort(404)
    return render_template('store/product_detail.html', product=product)