from flask import Blueprint

auth = Blueprint("auth", __name__, template_folder="templates")

# routes.py import
from . import routes