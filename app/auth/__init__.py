from flask import Blueprint
from app.extensions import login_manager

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@login_manager.user_loader
def load_user(user_id):
    from app.auth.models import User
    return User.query.get(int(user_id))

from . import routes # noqa: F401 - import routes so that the route decorators are executed and the routes are registered with the blueprint. We put this import at the end to avoid circular imports, since routes.py also needs to import the blueprint object from __init__.py.