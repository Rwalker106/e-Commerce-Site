from flask import render_template, redirect, url_for, flash, request
from flask.cli import F
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from . import auth_bp
from .models import User
from app import auth


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('store.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Basic validation
        if User.query.filter_by(email=email).first():
            flash('An account with that email is already registered.', 'error')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(username=username).first():
            flash('An account with that username is already taken.', 'error')
            return redirect(url_for('auth.register'))
        
        # Create the user
        user = User(email=email, username=username)
        user.set_password(password) # hash the password before storing it.
        db.session.add(user)
        db.session.commit() 
        
        login_user(user) # log the user in immediately after registration
        flash('Account creation successful. Welcome!', 'success')
        return redirect(url_for('store.index'))
    
    return render_template('auth/register.html')    

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('store.index'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        if user is None or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))
    
        login_user(user)
        flash('Login successful. Welcome back!', 'success')
        next_page = request.args.get('next')
        return redirect(next_page or url_for('store.index'))
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required # only logged in users can log out
def logout():
    from app.cart.cart import Cart
    Cart().clear() # Clear the cart on logout to prevent issues with session data
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('store.index'))