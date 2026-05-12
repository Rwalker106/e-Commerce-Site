from flask import Blueprint

# Three arguments:
# 1 Bludeprint's name - used internally and in url_for()
# 2 __name__  - helps Flask find templates and static files relative to this blueprint
# 3 url_prefix - all routes in this blueprint will be prefixed with /store
store_bp = Blueprint('store', __name__, url_prefix='/')

from . import routes #noqa: F401