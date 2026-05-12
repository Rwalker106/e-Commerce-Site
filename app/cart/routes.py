# app/cart/routes.py

from flask import redirect, url_for, flash, request, render_template
from . import cart_bp
from .cart import Cart


@cart_bp.route('/')
def view_cart():
    cart = Cart()
    return render_template('cart/cart.html',
                           items=cart.get_items(),
                           total=cart.display_total(),
                           is_empty=cart.is_empty())


@cart_bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    cart = Cart()
    quantity = int(request.form.get('quantity', 1))
    cart.add(product_id, quantity)
    flash('Item added to cart.', 'success')
    return redirect(request.referrer or url_for('store.index'))


@cart_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = Cart()
    cart.remove(product_id)
    flash('Item removed from cart.', 'info')
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    cart = Cart()
    quantity = int(request.form.get('quantity', 1))
    cart.update(product_id, quantity)
    return redirect(url_for('cart.view_cart'))


@cart_bp.route('/clear', methods=['POST'])
def clear_cart():
    cart = Cart()
    cart.clear()
    flash('Cart cleared.', 'info')
    return redirect(url_for('cart.view_cart'))