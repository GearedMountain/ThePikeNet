from flask import Flask, session


def createSession(userId, username, auth_level):
    session['user_id'] = userId[0]
    session['username'] = username
    session['auth_level'] = auth_level
    
def isLoggedIn():
    userId = session.get('user_id')
    if userId == None:
        return False
    else:
        return True
    
def getUsername():
    return session.get('username')