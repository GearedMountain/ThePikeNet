from flask import render_template, request, redirect, url_for, session, jsonify, send_from_directory
from pikenet.utils.decorators import login_required, role_required
from .snackboxAPI import runSnackboxAPI
from . import bp
import os

@bp.route('/snackbox-api')
@role_required(0)
def index():
    result = runSnackboxAPI()
    print(result)
    return "running"


@bp.route('/image/<filename>')
@role_required(0)
def get_image(filename):
    currentCountryFoler = os.path.abspath('pikenet/webapps/snackbox/dynamic/mexico')
    return send_from_directory(currentCountryFoler, filename)