pikenetVersion = 1.0
from flask import Flask, request, send_from_directory, render_template, session, Response, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import text
from datetime import datetime, timezone
import secrets
from dotenv import load_dotenv
from logic.Routing import basic_routing  # import the Blueprint
from logic.AdminRouting import admin_routing  # import the Blueprint
from logic.Email import sendAuthCode, configureEmail # import email service
import bcrypt
import os 
import random

load_dotenv()

# Pass the email service the password from environment variables
configureEmail(os.getenv("EMAIL_PASS"))

app = Flask(__name__)
app.register_blueprint(basic_routing, url_prefix='/')
app.register_blueprint(admin_routing, url_prefix='/admin')

# Grab environment variables
secret_key = os.getenv("SECRET_KEY")
database_url = os.getenv("DATABASE_URL")

# Error if there is no databaseurl
if not database_url:
    raise ValueError("DATABASE_URL is not set or is empty")
    
# remove DATABASE_URL= from the variable because sqlalchemy is stupid
if database_url.startswith("DATABASE_URL="):
    database_url = database_url[len("DATABASE_URL="):]
  
app.config['SQLALCHEMY_DATABASE_URI'] = database_url

# Helper functions for bcrypt

# Helper functions for email interaction
currentAuthorizationChecks = {}
def createAuthCode(email: str):
    
    epochTime = int(datetime.now(timezone.utc).timestamp())
    sendCode = f"{secrets.randbelow(10**6):06}"
    
    currentAuthorizationChecks[email] = (sendCode, epochTime)
    
    sendAuthCode(
        to_address="brandon917@icloud.com",
        code=sendCode
    )
    print(f"Creating new authorization request: {currentAuthorizationChecks}")

def validateAuthCode():
    print("check code")


# REMOVE THIS ----------------------------------------------------------------------------
db = SQLAlchemy(app)
@app.route('/test_db')
def test_db_connection():
    try:
        # Try to execute a basic query to test the connection
        result = db.session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';")) 
        rows = result.fetchall()
        rows_dict = [{"table_name": row[0]} for row in rows]
        print(rows[0])
        return jsonify(rows_dict), 200

    except Exception as e:
        return f"Error connecting to the database: {str(e)}", 500
        
@app.route('/see_db')
def see_db_users():
    try:
        # Try to execute a basic query to test the connection
        result = db.session.execute(text("SELECT * FROM users")) 
        user = result.fetchone()
        return f"{user}", 200
    except Exception as e:
        return f"Error connecting to the database: {str(e)}", 500
        
@app.route('/delete_db')
def delete_db_users():
    try:
        # Try to execute a basic query to test the connection
        result = db.session.execute(text("DELETE FROM users")) 
        db.session.commit() # Have to run commit for something like a deletion
        return f"{result.rowcount}", 200
    except Exception as e:
        return f"Error connecting to the database: {str(e)}", 500
# REMOVE THIS ----------------------------------------------------------------------------

# Track current users with a session
SET_ACTIVESESSIONS = set()

# Logging user in 
@app.route('/login-submit', methods=['POST'])
def loginSubmit():
    username = request.form['username']
    password = request.form['password']
    # check if theyre empty, have invalid chars etc
    if not username or not password:
        return "Field is empty or invalid"
        
    # Parameterize the SQL
    sql = text("SELECT * FROM users WHERE username = :username")
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    # Process data or return a response
    return f"Received: {user}"

# Registering new user
@app.route('/register-account-submit', methods=['POST'])
def registerAccountSubmit():
    data = request.get_json() 
    username = data.get('username')
    email = data.get('email') 
    password = data.get('password')
    try:
        sql = text("""
            INSERT INTO users (username, email, password)
            VALUES (:username, :email, :password)
        """)

        db.session.execute(sql, {
            "username": username,
            "email": email,
            "password": password
        })
        result = db.session.commit()
        createAuthCode(email)
        return jsonify({"message": "Success"}), 200
    except Exception as e:
        return jsonify({"message": "Error"}), 403
 # Username or email already taken
    


# @@@@@@@@@@@@@@@@@@@@@@@@ SERVING IMAGES @@@@@@@@@@@@@@@@@@@@@@@@
# Serve images from the 'images/official' folder
@app.route('/images/official/<filename>')
def get_official_image(filename):
    # Define the path to the 'images/official' folder
    image_folder = os.path.join(app.root_path, 'images', 'official')
    return send_from_directory(image_folder, filename)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
    
if __name__ == '__main__':
	app.run(debug=True)

