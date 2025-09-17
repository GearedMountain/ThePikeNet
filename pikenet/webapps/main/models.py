from pikenet.utils.database import db
from sqlalchemy import text

# See if the username and password provided are valid
def checkLoginCredentials(username, password):
    sql = text("SELECT id, auth_value FROM users WHERE username = :username AND password = :password")
    result = db.session.execute(sql, {"username": username, "password": password})
    row = result.fetchone()
    if row:
        userId, authValue = row
        return userId, authValue
    else:
        return None