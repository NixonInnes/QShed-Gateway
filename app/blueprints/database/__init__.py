from flask import Blueprint

data_bp = Blueprint("database", __name__)

from . import routes
