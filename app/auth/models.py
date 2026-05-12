from datetime import datetime, timezone
from flask_login import UserMixin
from app.extensions import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    # --- Identity ---
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # --- Security ---
    password_hash = db.Column(db.String(255), nullable=False) # store hashed password, not plaintext
    
    # --- Profile ---
    first_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    
    # --- Permissions ---
    is_admin = db.Column(db.Boolean, default=False) # whether the user has admin privileges
    is_active = db.Column(db.Boolean, default=True) # whether the user's account is active. This can be used to disable accounts without deleting them.
    
    # --- Timestamps ---    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    
    # --- Helper methods ---
    def set_password(self, password):
        """Hash the password and store the hash."""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Check the password against the stored hash."""
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    
    def __repr__(self):
        return f'<User {self.username}>'