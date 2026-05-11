from flask import Blueprint

bp = Blueprint("pikepay", __name__, template_folder="templates")

from . import routes
