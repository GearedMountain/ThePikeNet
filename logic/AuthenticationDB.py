from .Database import db, text

def checkLoginCredentials(username, password):
    sql = text("SELECT id, auth_value FROM users WHERE username = :username AND password = :password")
    result = db.session.execute(sql, {"username": username, "password": password})
    
    row = result.fetchone()

    if row:
        userId, auth_value = row
        return userId, auth_value
    else:
        return None
    
def checkAccountUnique(username, email, password):
    sql = text("""
            SELECT COUNT(*) as count FROM users
            WHERE username = :username OR email = :email
        """)

    result = db.session.execute(sql, {
            "username": username,
            "email": email,
            "password": password
    })
    return result
    