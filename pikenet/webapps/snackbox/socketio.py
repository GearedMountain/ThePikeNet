from flask import request, session
from flask_socketio import emit, join_room
from pikenet import socketio

@socketio.on('connect')
def handle_connect():
    print("Client connected:", request.sid)

@socketio.on('join')
def handle_join(data):
    print("somebody joined")

@socketio.on('disconnect')
def handle_disconnect():
    print('A user disconnected!', request.sid)