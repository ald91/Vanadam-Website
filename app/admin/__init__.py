"""initializes admin module"""

from flask import Blueprint

admin = Blueprint("admin", __name__, template_folder="templates/admin")

# routes.py import
from . import routes
