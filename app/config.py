import os
from re import M
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Mail configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.example.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    
    #SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False # suppresses a deprecation warning.
    
    # Stripe - both keys come from the .env file
    STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.getenv('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET= os.getenv('STRIPE_WEBHOOK_SECRET')
    
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///store_dev.db')
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI ='sqlite:///:memory:'
    WTF_CSRF_ENABLED = False # Disable CSRF for testing purposes
    # Use fake Stripe test keys - never his real Stripe keys in tests!
    STRIPE_SECRET_KEY = 'sk_test_fake_key_for_testing'
    
class ProductionConfig(Config):
    DEBUG = False
    # In production, DATABASE_URL MUST exist — no fallback
    # If it's not set, this will be None and SQLAlchemy will throw immediately
    # That's intentional — loud failure beats silent misconfiguration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') # no fallback, must be set in environment.
    
    @classmethod
    def validate(cls):
        """Call this on startup to catch missing production config early"""
        required = [
            'SECRET_KEY', 
            'DATABASE_URL',  
            'STRIPE_PUBLIC_KEY',
             'STRIPE_SECRET_KEY',
             'MAIL_PASSWORD']
        missing = [ key for key in required if not os.environ.get(key)]
        if missing:
            raise EnvironmentError(f'Missing required environment variables: {missing}')
    
# This dictionary is the key - it's how the factory looks up configs by name
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}