from flask import render_template, request, redirect, url_for, session, jsonify, send_from_directory, request, session
from flask_socketio import emit, join_room
from pikenet import socketio

from pikenet.utils.decorators import login_required, role_required
from werkzeug.utils import secure_filename
from .snackboxAPI import runSnackboxAPI, getCurrentCountry
from . import bp
import os

# Class to store all game information
class SnackBoxGame:
    def __init__(self, snackCount=0, playerCount=0, phase="started"):
        print(f"Initialized game with snack count: {snackCount}")
        self.snackCount = snackCount
        self.completedSnacks = [0] * snackCount
        self.playerCount = playerCount
        self.phase = phase
        self.availableRatings = {}

gameState = None
@bp.route('/snackbox/snackbox-api')
@role_required(0)
def index():
    result = runSnackboxAPI()
    print(result)
    return "running"

@bp.route('/snackbox/')
@role_required(2, 1, 0)
def snackbox_index():
    global gameState
    gameState.playerCount += 1
    isAdmin = session.get('auth_value') == 0
    return render_template('snackbox-index.html', username=session['user_id'], isAdmin=isAdmin)

#@bp.route('/snackbox/image/<countryname>/', defaults={'filename': None})
@bp.route('/snackbox/image/<filename>')
@role_required(2, 1, 0)
def getSnackboxImage(filename):
    # Secure the country name to avoid path traversal
    safeFilename = secure_filename(filename)
    basePath = 'pikenet/webapps/snackbox/dynamic'
    countryFolder = os.path.abspath(os.path.join(basePath, getCurrentCountry().lower()))

    if not os.path.exists(countryFolder):
        print("country not found")
    else:
        file_path = os.path.join(countryFolder, safeFilename)
        if not os.path.isfile(file_path):
           print("file not found")
        return send_from_directory(countryFolder, safeFilename)
    
@bp.route('/snackbox/image-list')
def getCurrentCountryName():
    global gameState
    currentCountry = getCurrentCountry()
    basePath = 'pikenet/webapps/snackbox/dynamic'
    countryFolder = os.path.abspath(os.path.join(basePath, currentCountry.lower()))
    try:
            files = os.listdir(countryFolder)
            # Filter out hidden files or directories
            visibleFiles = [f for f in files if not f.startswith('.') and os.path.isfile(os.path.join(countryFolder, f))]
            if gameState is None:
                gameState = SnackBoxGame(len(visibleFiles))
            return jsonify(visibleFiles)
    except Exception as e:
            print(f"error returning files: {e}")
    return  "Error"

@bp.route('/snackbox/start-game')
def startSnackboxGame():
    if session.get('auth_value') < 1:
        print("sending game start emi")
        socketio.emit('game-started', namespace='/snackbox')
    return "Success" 


# Socketio section
playersInGame = {}
@socketio.on('connect', namespace='/snackbox')
def handleConnect():
    sid = request.sid
    if sid not in playersInGame:
        playersInGame[sid] = session["username"]
        players = list(playersInGame.values())
        emit('playerlist_update', {'players': players}, broadcast=True)
        #Emit a socket for everybody to update current playercount

@socketio.on('join', namespace='/snackbox')
def handle_join(data):
    print("somebody joined")

@socketio.on('disconnect', namespace='/snackbox')
def handleDisconnect():
    sid = request.sid
    if sid in playersInGame:
        playersInGame.pop(sid, None)
        players = list(playersInGame.values())
        emit('playerlist_update', {'players': players}, broadcast=True)
