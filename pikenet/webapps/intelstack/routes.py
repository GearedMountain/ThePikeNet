from flask import render_template, request, redirect, url_for, session, jsonify
from pikenet.utils.decorators import login_required, role_required
from .models import addnote
from . import bp

@bp.route('/intelstack')
@role_required(0)
def index():
    return render_template('intelstack-index.html')

@bp.route('/addnote-submit', methods=['POST'])
@role_required(0)
def addnoteSubmit():
    data = request.get_json() 
    title = data.get('title')
    result = addNote(title)
    return str(result)