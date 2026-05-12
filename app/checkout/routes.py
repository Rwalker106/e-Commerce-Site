# app/checkout/routes.py

import stripe
from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user
from . import checkout_bp
from app.cart.cart import Cart
from app.extensions import db
from app.orders.models import Order, OrderItem


@checkout_bp.route('/', methods=['GET', 'POST'])
def checkout():
    cart = Cart()

    if cart.is_empty():
        flash('Your cart is empty.', 'info')
        return redirect(url_for('store.index'))

    if request.method == 'POST':
        # Collect shipping details from the form
        shipping = {
            'name':    request.form.get('name', '').strip(),
            'email':   request.form.get('email', '').strip().lower(),
            'address': request.form.get('address', '').strip(),
            'city':    request.form.get('city', '').strip(),
            'state':   request.form.get('state', '').strip(),
            'zip':     request.form.get('zip', '').strip(),
            'country': request.form.get('country', '').strip(),
        }

        # Calculate totals
        items     = cart.get_items()
        subtotal  = cart.total()  # cents
        tax       = round(subtotal * 0.08)  # 8% flat tax for demo
        shipping_cost = 500  # flat $5 shipping fee for demo
        total     = subtotal + tax + shipping_cost

        # Create Stripe PaymentIntent
        stripe.api_key = current_app.config['STRIPE_SECRET_KEY']


        try:
            intent = stripe.PaymentIntent.create(
                amount=total,
                currency='usd',
                metadata={
                    'user_id': current_user.id if current_user.is_authenticated else 'guest',
                    'email':   shipping['email'],
                }
            )
        except stripe.error.StripeError as e:
            flash(f'Payment error: {str(e)}', 'error')
            return redirect(url_for('checkout.checkout'))

        # Store order details in session for after payment
        from flask import session
        session['pending_order'] = {
            'shipping':       shipping,
            'subtotal':       subtotal,
            'tax':            tax,
            'shipping_cost':  shipping_cost,
            'total':          total,
            'payment_intent': intent.id,
        }

        return render_template('checkout/payment.html',
                               client_secret=intent.client_secret,
                               stripe_public_key=current_app.config['STRIPE_PUBLIC_KEY'],
                               total=total,
                               items=items,
                               subtotal=subtotal,
                               tax=tax)

    # GET — show shipping form
    items = cart.get_items()
    return render_template('checkout/checkout.html',
                           items=items,
                           total=cart.display_total(),
                           subtotal=cart.total())


@checkout_bp.route('/confirm')
def confirm():
    """Called after Stripe redirects back to our site."""
    payment_intent_id = request.args.get('payment_intent')
    redirect_status   = request.args.get('redirect_status')

    if redirect_status != 'succeeded':
        flash('Payment was not successful. Please try again.', 'error')
        return redirect(url_for('checkout.checkout'))

    # Check we haven't already processed this payment
    existing = Order.query.filter_by(
        stripe_payment_intent_id=payment_intent_id
    ).first()

    if existing:
        return redirect(url_for('store.index'))

    # Retrieve pending order from session
    from flask import session
    pending = session.get('pending_order')

    if not pending or pending['payment_intent'] != payment_intent_id:
        flash('Order details not found. Please contact support.', 'error')
        return redirect(url_for('store.index'))

    # Verify payment with Stripe
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    intent = stripe.PaymentIntent.retrieve(payment_intent_id)

    if intent.status != 'succeeded':
        flash('Payment not confirmed. Please contact support.', 'error')
        return redirect(url_for('store.index'))

    # Create the Order
    cart     = Cart()
    items    = cart.get_items()
    shipping = pending['shipping']

    order = Order(
        user_id=current_user.id if current_user.is_authenticated else None,
        status='paid',
        subtotal=pending['subtotal'],
        tax=pending['tax'],
        shipping=pending['shipping_cost'],
        total=pending['total'],
        stripe_payment_intent_id=payment_intent_id,
        shipping_name=shipping['name'],
        shipping_email=shipping['email'],
        shipping_address=shipping['address'],
        shipping_city=shipping['city'],
        shipping_state=shipping['state'],
        shipping_zip=shipping['zip'],
        shipping_country=shipping['country'],
    )
    db.session.add(order)
    db.session.flush()  # get order.id without committing

    # Create OrderItems
    for item in items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item['product'].id,
            product_name=item['product'].name,
            product_sku=item['product'].sku,
            unit_price=item['product'].price,
            quantity=item['quantity'],
            line_total=item['line_total'],
        )
        db.session.add(order_item)

        # Decrement stock
        item['product'].stock -= item['quantity']

    db.session.commit()

    # Clear the cart and session
    cart.clear()
    session.pop('pending_order', None)

    flash('Payment successful! Your order has been placed.', 'success')
    return redirect(url_for('store.index'))

@checkout_bp.route('/webhook', methods=['POST'])
def webhook():
    payload    = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config['STRIPE_WEBHOOK_SECRET']

    # Verify the webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        # Invalid payload
        return '', 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature — not from Stripe
        return '', 400

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        intent = event['data']['object']
        _handle_payment_succeeded(intent)

    elif event['type'] == 'payment_intent.payment_failed':
        intent = event['data']['object']
        _handle_payment_failed(intent)

    # Return 200 to acknowledge receipt
    return '', 200


def _handle_payment_succeeded(intent):
    """
    Called when Stripe confirms payment succeeded.
    Creates the order if it doesn't already exist.
    """
    payment_intent_id = intent['id']

    # Idempotency check — don't create duplicate orders
    existing = Order.query.filter_by(
        stripe_payment_intent_id=payment_intent_id
    ).first()

    if existing:
        # Order already created by the confirm route — just update status
        if existing.status != 'paid':
            existing.status = 'paid'
            db.session.commit()
        return

    # Access metadata safely from StripeObject
    try:
        user_id = intent.metadata['user_id']
    except (KeyError, AttributeError):
        user_id = None

    try:
        email = intent.metadata['email']
    except (KeyError, AttributeError):
        email = None

    # Convert user_id back — 'guest' means no user
    if user_id == 'guest':
        user_id = None
    else:
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            user_id = None

    order = Order(
        user_id=user_id,
        status='paid',
        subtotal=intent['amount'],  # we don't have breakdown here
        tax=0,
        shipping=0,
        total=intent['amount'],
        stripe_payment_intent_id=payment_intent_id,
        shipping_email=email,
    )
    db.session.add(order)
    db.session.commit()


def _handle_payment_failed(intent):
    """
    Called when a payment attempt fails.
    Log it — useful for analytics and support.
    """
    payment_intent_id = intent['id']
    existing = Order.query.filter_by(
        stripe_payment_intent_id=payment_intent_id
    ).first()

    if existing:
        existing.status = 'failed'
        db.session.commit()