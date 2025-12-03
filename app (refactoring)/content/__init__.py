from flask import Blueprint

content = Blueprint("site", __name__)

# routes.py import
from . import routes, routes_article, routes_video
