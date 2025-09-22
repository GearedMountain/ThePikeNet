from flask import render_template, request, redirect, url_for, session, jsonify
from pikenet.utils.decorators import login_required, role_required
from .snackboxAPI import runSnackboxAPI
from . import bp

@bp.route('/snackbox-api')
def index():
    result = runSnackboxAPI()
    print(result)
    return "running"
