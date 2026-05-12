from flask import Blueprint


checkout_bp = Blueprint('checkout', __name__, url_prefix='/checkout')

from . import routes # noqa: F401 - import routes so that the route decorators are executed and the routes are registered with the blueprint. We put this import at the end to avoid circular imports, since routes.py also needs to import the blueprint object from __init__.py.