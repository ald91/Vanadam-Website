from flask import Blueprint

forum = Blueprint("forum", __name__, template_folder="templates/forum")

from . import routes