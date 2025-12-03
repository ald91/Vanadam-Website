from flask import Blueprint

admin = Blueprint("admin", __name__)

# routes.py import
from . import routes