from flask import Blueprint

# Create blueprint with standard name
auth_bp = Blueprint('auth', __name__, template_folder='templates')

from . import routes # Import routes after creating blueprint
