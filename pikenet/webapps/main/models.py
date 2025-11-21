from pikenet.utils.database import db
from sqlalchemy import text
from .emailRegistrar import createAuthCheck


# See if the username and password provided are valid
def checkLoginCredentials(username, password):
    sql = text(
        "SELECT id, auth_value FROM users WHERE username = :username AND password = :password"
    )
    result = db.session.execute(sql, {"username": username, "password": password})
    row = result.fetchone()
    if row:
        userId, authValue = row
        return userId, authValue
    else:
        return None


def registerAccount(username, password, email):
    try:
        sql = text(
            """
            INSERT INTO users (username, email, password)
            VALUES (:username, :email, :password)
        """
        )

        db.session.execute(
            sql, {"username": username, "email": email, "password": password}
        )
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
    return False


# Helper function for checking username is unique
def isAccountUnique(username, password, email):
    sql = text(
        """
            SELECT COUNT(*) as count FROM users
            WHERE username = :username OR email = :email
    """
    )
    result = db.session.execute(
        sql, {"username": username, "email": email, "password": password}
    )

    if result.scalar() > 0:
        return False
    return True
