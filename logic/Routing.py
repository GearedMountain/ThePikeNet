from flask import Blueprint, render_template, request, jsonify, redirect
from logic.Authenticator import *
from .IntelStackDB import *

basic_routing = Blueprint('basic_routing', __name__)

# Login Page
@basic_routing.route('/')
def index():
    if isLoggedIn():
        return redirect("dashboard")
    return redirect("login")

##################### Routing for Intel Stack ###########################

# Login page for intel stack
@basic_routing.route('/intelstack')
def intelIndex():
    if isLoggedIn():
        return render_template('IntelStack/index.html', username=getUsername())
    return render_template('index.html', pikenetVersion=1.0)

@basic_routing.route('/addnote-submit', methods=['POST'])
def addnoteSubmit():
    data = request.get_json() 
    title = data.get('title')
    result = addNote(title)
    return str(result)

@basic_routing.route('/get-most-recent')
def getMostRecentRequest():
    result = getMostRecent()
    return jsonify(result)

@basic_routing.route('/show-note')
def showNote():
    noteId = request.args.get('id')
    if not noteId.isnumeric():
        return "NaN" 
    if not noteId:
        return "No parameter"
    result = getNoteById(noteId)
    return render_template('IntelStack/showNote.html', data=result)

@basic_routing.route('/add-tag-submit', methods=['POST'])
def addTagSubmit():
    data = request.get_json() 
    tagName = data.get('tagName')
    noteId = data.get('id')
    result = addTag(tagName, noteId)
    return str(result)

@basic_routing.route('/get-all-tags')
def getAllTagsRequest():
    result = getAllTags()
    return jsonify(result)

##################### Routing for Register Page ###########################

# Register Page
@basic_routing.route('/register-account')
def registerAccount():
    return render_template('register-account.html')

# Register Page
@basic_routing.route('/login-redirect')
def loginRedirect():
    return render_template('login-redirect.html')

# Authenticated Routing
@basic_routing.route('/dashboard')
def dashboardIndex():
    if isLoggedIn():
        return render_template('Dashboard/index.html', auth_value=getAuthValue())
    else:
        return render_template('Dashboard/index.html',auth_value=getAuthValue())
    
