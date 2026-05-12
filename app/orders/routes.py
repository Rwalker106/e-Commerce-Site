# app/orders/routes.py

from flask import render_template, abort
from flask_login import login_required, current_user
from . import orders_bp
from .models import Order


@orders_bp.route('/')
@login_required
def order_history():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('orders/order_history.html', orders=orders)  

@orders_bp.route('/<int:order_id>')
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    
    # Security check - users can only view their own orders
    if order.user_id != current_user.id:
        abort(403)
        
    return render_template('orders/order_detail.html', order=order)
