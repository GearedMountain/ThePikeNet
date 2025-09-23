from flask import render_template, request, redirect, url_for, session, jsonify
from pikenet.utils.decorators import login_required, role_required
from .models import addNote, getMostRecent, getNoteById
from . import bp

@bp.route('/intelstack')
@role_required(0)
def index():
    return render_template('intelstack-index.html')

@bp.route('/addnote-submit', methods=['POST'])
@role_required(0)
def addNoteSubmit():
    data = request.get_json() 
    title = data.get('title')
    result = addNote(title)
    return str(result)

@bp.route('/get-most-recent')
@role_required(0)
def getMostRecentRequest():
    result = getMostRecent()
    return jsonify(result)

@bp.route('/show-note')
@role_required(0)
def showNote():
    noteId = request.args.get('id')
    if not noteId.isnumeric():
        return "NaN" 
    if not noteId:
        return "No parameter"
    result = getNoteById(noteId)
    return render_template('show-note.html', data=result)