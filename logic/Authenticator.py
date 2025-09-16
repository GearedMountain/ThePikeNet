from flask import Flask, session


def createSession(userId, username, auth_value):
    print(f"creating session for {userId}: {username} AUTH {auth_value}")
    session['user_id'] = userId
    session['username'] = username
    session['auth_value'] = auth_value
    
def isLoggedIn():
    userId = session.get('user_id')
    if userId == None:
        return False
    else:
        return True
    
def getUsername():
    return session.get('username')

def getAuthValue():
    return session.get('auth_value')