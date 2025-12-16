from flask import Blueprint

data = Blueprint("data", __name__)

# routes.py import
from . import routes
