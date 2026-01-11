"""initializes admin module"""

from flask import Blueprint

# routes.py import
from . import routes

admin = Blueprint("admin", __name__, template_folder="templates/admin")
