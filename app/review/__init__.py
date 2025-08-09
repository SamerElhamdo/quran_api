from flask import Blueprint

review_bp = Blueprint("review", __name__)

# Import routes after blueprint creation
from . import routes 