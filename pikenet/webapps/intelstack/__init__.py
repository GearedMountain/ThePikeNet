from flask import Blueprint

bp = Blueprint("intelstack", __name__, template_folder="templates")

from . import routes
