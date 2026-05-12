# app/__init__.py

import os
from flask import Flask
from .config import config, ProductionConfig # Import the config dictionary
from .extensions import db, login_manager, migrate, mail # Import the extension objects


def create_app(config_name=None):
    # If no config_name passed, check the environment variable
    # This is how deployment platforms (Heroku, Railway) control your app
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
                
    app = Flask(__name__)
    
    # Load configuration from our config class
    #    app.config.from_object() reads all UPPERCASE attributes
    #    from the class and loads them into Flask's config dict
    app.config.from_object(config[config_name])
    # Validate required variables if we are in production
    if config_name == 'production':
        ProductionConfig.validate()

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db) # need to pass the db object to Flask-Migrate so it knows what to manage as well as the app
    mail.init_app(app)
    

    # Import models so SQLAlchemy knows about them.
    with app.app_context():
        from app.store import models #noqa: F401
        from app.auth import models #noqa: F401
        from app.orders import models #noqa: F401
 

    # Register blueprints 
    from .store import store_bp
    from .auth import auth_bp
    from .cart import cart_bp
    from .checkout import checkout_bp
    from .orders import orders_bp
    from .admin import admin_bp

    # Register blueprints continued
    app.register_blueprint(store_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(admin_bp)
    
    @app.context_processor
    def inject_cart_count():
        from app.cart.cart import Cart
        try:
            return {'cart_count': Cart().item_count()}
        except Exception:
            return {'cart_count': 0}
    
    return app

