from flask import Blueprint

bp = Blueprint('snackbox', __name__, template_folder='templates')

from . import routes