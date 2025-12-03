from flask import Blueprint

auth = Blueprint("auth", __name__)

# routes.py import
from . import routes