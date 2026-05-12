# app/admin/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from . import admin_bp, admin_required
from app.extensions import db
from app.store.models import Product
from app.orders.models import Order


# ── Dashboard ──────────────────────────────────────────────────────────────

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    product_count = Product.query.count()
    order_count   = Order.query.count()
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    return render_template('admin/dashboard.html',
                           product_count=product_count,
                           order_count=order_count,
                           recent_orders=recent_orders)


# ── Products ───────────────────────────────────────────────────────────────

@admin_bp.route('/products')
@login_required
@admin_required
def products():
    all_products = Product.query.order_by(Product.name).all()
    return render_template('admin/products.html', products=all_products)


@admin_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_product():
    if request.method == 'POST':
        product = Product(
            name        = request.form['name'],
            sku         = request.form['sku'],
            slug        = request.form['slug'],
            brand       = request.form.get('brand'),
            description = request.form.get('description'),
            category    = request.form.get('category'),
            subcategory = request.form.get('subcategory'),
            price       = int(float(request.form['price']) * 100),
            stock       = int(request.form.get('stock', 0)),
            is_active   = 'is_active' in request.form,
        )
        db.session.add(product)
        db.session.commit()
        flash(f'Product "{product.name}" created.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=None)


@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name        = request.form['name']
        product.sku         = request.form['sku']
        product.slug        = request.form['slug']
        product.brand       = request.form.get('brand')
        product.description = request.form.get('description')
        product.category    = request.form.get('category')
        product.subcategory = request.form.get('subcategory')
        product.price       = int(float(request.form['price']) * 100)
        product.stock       = int(request.form.get('stock', 0))
        product.is_active   = 'is_active' in request.form
        db.session.commit()
        flash(f'Product "{product.name}" updated.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=product)


@admin_bp.route('/products/<int:product_id>/deactivate', methods=['POST'])
@login_required
@admin_required
def deactivate_product(product_id):
    product = Product.query.get_or_404(product_id)
    product.is_active = False
    db.session.commit()
    flash(f'"{product.name}" deactivated.', 'info')
    return redirect(url_for('admin.products'))


# ── Orders ─────────────────────────────────────────────────────────────────

@admin_bp.route('/orders')
@login_required
@admin_required
def orders():
    all_orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=all_orders)


@admin_bp.route('/orders/<int:order_id>')
@login_required
@admin_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)


@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
@admin_required
def update_order_status(order_id):
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    valid = ['pending', 'paid', 'shipped', 'delivered', 'refunded', 'failed']
    if new_status in valid:
        order.status = new_status
        db.session.commit()
        flash(f'Order #{order.id} status updated to {new_status}.', 'success')
    return redirect(url_for('admin.order_detail', order_id=order.id))