from flask import render_template, request, redirect, url_for, session, jsonify, send_from_directory
from pikenet.utils.decorators import login_required, role_required
from .snackboxAPI import runSnackboxAPI
from . import bp
import os

@bp.route('/snackbox/snackbox-api')
@role_required(0)
def index():
    result = runSnackboxAPI()
    print(result)
    return "running"


@bp.route('/snackbox/image/<countryname>/<filename>')
@role_required(0)
def get_image(countryname, filename):
    basePath = 'pikenet/webapps/snackbox/dynamic'
    currentCountryFolder = os.path.abspath(os.path.join(basePath, countryname))
    return send_from_directory(currentCountryFolder, filename)