from flask import Flask, session


def createSession(userId):
    session['user_id'] = userId[0]

def isLoggedIn():
    userId = session.get('user_id')
    if userId == None:
        return False
    else:
        return True