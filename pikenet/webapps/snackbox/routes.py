from flask import render_template, request, redirect, url_for, session, jsonify, send_from_directory
from pikenet.utils.decorators import login_required, role_required
from werkzeug.utils import secure_filename
from .snackboxAPI import runSnackboxAPI
from . import bp
import os

@bp.route('/snackbox/snackbox-api')
@role_required(0)
def index():
    result = runSnackboxAPI()
    print(result)
    return "running"


@bp.route('/snackbox/image/<countryname>/', defaults={'filename': None})
@bp.route('/snackbox/image/<countryname>/<filename>')
@role_required(2)
def get_image_or_list(countryname, filename):
    # Secure the country name to avoid path traversal
    safe_countryname = secure_filename(countryname)
    base_path = 'pikenet/webapps/snackbox/dynamic'
    country_folder = os.path.abspath(os.path.join(base_path, safe_countryname))

    if not os.path.exists(country_folder):
        print("country not found")

    if filename is None:
        # Return a list of files in the folder
        try:
            files = os.listdir(country_folder)
            # Filter out hidden files or directories
            visible_files = [f for f in files if not f.startswith('.') and os.path.isfile(os.path.join(country_folder, f))]
            return jsonify(visible_files)
        except Exception as e:
            print(f"error returning files: {e}")
    else:
        # Secure the filename too
        safe_filename = secure_filename(filename)
        file_path = os.path.join(country_folder, safe_filename)

        if not os.path.isfile(file_path):
           print("file not found")
        return send_from_directory(country_folder, safe_filename)