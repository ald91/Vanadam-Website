from flask import Blueprint

content = Blueprint("content", __name__, template_folder="../templates")

# routes.py import
from . import routes, routes_article, routes_video
