from pikenet.utils.database import db
from sqlalchemy import text

# See if the username and password provided are valid
def checkLoginCredentials(username, password):
    sql = text("SELECT id, auth_value FROM users WHERE username = :username AND password = :password")
    result = db.session.execute(sql, {"username": username, "password": password})
    row = result.fetchone()
    if row:
        userId, auth_value = row
        session['user_id'] = userId
        session['username'] = username
        session['auth_value'] = auth_value
        return "Success"
    else:
        return None