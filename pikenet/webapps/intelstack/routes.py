from flask import render_template, request, redirect, url_for, session, jsonify
from pikenet.utils.decorators import login_required, role_required
from . import bp

@bp.route('/intelstack')
@role_required(0)
def index():
    print(result)
    return render_template('index.html')

