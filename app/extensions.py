"""This is behavioral settings and not app-specific settings. These do not depend on which config is loaded. They are not environment-specific. They are just how we want the extensions to behave in general."""

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail

# Phase 1 - create extension objects without an app

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()

# Configure login_manager behavior
# This is the endpoint Flask-Login redirects to when a user tries to access a @login_required route without being logged in.
login_manager.login_view = 'auth.login' # 'auth.login' is the endpoint for the login route in the auth blueprint. This is where users will be sent to log in if they try to access a protected page.
login_manager.login_message_category = 'info' # This sets the category for the flash message that is shown when a user is redirected to the login page. 'info' will style the message with Bootstrap's info alert class. You can choose other categories like 'warning', 'danger', etc. depending on how you want the message to appear.
@login_manager.user_loader
def load_user(user_id):
    # This import is intentionally inside the function. It avoids any remaining circular import risk at module load time.
    from  app.auth.models import User
    return User.query.get(int(user_id)) # Flask-Login will pass the user_id as a string, so we convert it to an integer before querying the database. This function should return the user object corresponding to the given user_id, or None if no such user exists. Flask-Login uses this function to load the currently logged-in user from the session.