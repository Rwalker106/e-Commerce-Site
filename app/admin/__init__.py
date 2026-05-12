from flask import Blueprint, abort
from flask_login import current_user
from functools import wraps


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)  # Unauthorized
        if not current_user.is_admin:
            abort(403)  # Forbidden
        return f(*args, **kwargs)
    return decorated_function

from . import routes # noqa: F401 - import routes so that the route decorators are executed and the routes are registered with the blueprint. We put this import at the end to avoid circular imports, since routes.py also needs to import the blueprint object from __init__.py.