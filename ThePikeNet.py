pikenetVersion = 1.0
from flask import Flask, request, send_from_directory, session, render_template, Response, redirect, url_for, jsonify
from datetime import datetime, timezone
import secrets
import subprocess
import hashlib
from dotenv import load_dotenv
from logic.Routing import basic_routing  # import the Blueprint
from logic.AdminRouting import admin_routing  # import the Blueprint
from logic.Email import sendAuthCheck, configureEmail # import email service
from logic.Authenticator import *
from logic.Database import configureDB
from logic.AuthenticationDB import *
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

# Set flask session key to env var key, this is used to sign cookies
app.secret_key = secret_key

# Helper functions for bcrypt
def sha1Hash(message: str) -> str:
    # Encode the string to bytes, then hash it
    sha1 = hashlib.sha1()
    sha1.update(message.encode('utf-8'))
    return sha1.hexdigest()

# Helper functions for email interaction
currentAuthorizationChecks = {}
def createAuthCheck(username: str, email: str, password: str, hash: str):
    
    epochTime = int(datetime.now(timezone.utc).timestamp())    
    currentAuthorizationChecks[hash] = (username, email, password, epochTime, False)
    
    sendAuthCheck(
        to_address=email,
        code=hash
    )
    print(f"Creating new authorization request: {currentAuthorizationChecks}")

configureDB(app)

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
    userId = checkLoginCredentials(username, password)
    if not userId:
        return "incorrect"
    createSession(userId, username)
    # Process data or return a response
    return redirect('dashboard')

# TEMPORARY TO TEST SUBPROCESS USE
@app.route('/wake-pc')
def wakePC():
    try:
        if isLoggedIn():
            res = subprocess.run(
                "/usr/local/bin/startBrandonsPc.sh",    
                capture_output=True,   
                text=True,            
                timeout=30              
            )
            return "worked"
        else:
            return "no"
    except subprocess.TimeoutExpired:
        print("Script timed out")
    else:
        print("returncode:", res.returncode)
        print("stdout:", res.stdout)
        print("stderr:", res.stderr)

# Registering new user
@app.route('/register-account-submit', methods=['POST'])
def registerAccountSubmit():
    data = request.get_json() 
    username = data.get('username')
    email = data.get('email') 
    password = data.get('password')
    try:
        result = checkAccountUnique(username, email, password)
        
        if result.scalar() > 0:
            return jsonify({"message": "Not unique"}), 400
            
        # If valid and unique, start verification process before officially adding it to the database    
        hashValue = sha1Hash(username + email + password); 

        # Sanitize for illegal characters or spaces before

        # No spaces or special characters in username
        if not username.isalnum():
            return jsonify({"message": "Invalid characters in username"}), 400 
        
        # Password must be 8 characters
        if not len(password) >= 8:
            return jsonify({"message": "Password not long enough"}), 400
        
        # No spaces or illegal characters in email
        email = email.replace(" ", "")

        createAuthCheck(username, email, password, hashValue)
        return jsonify({"message": "WaitToValidate", "hashValue": hashValue}), 200
        
    except Exception as e:
        return jsonify({"message": "Error"}), 400

@app.route('/register-account-verification-check', methods=['POST'])
def checkVerificationStatus():
        data = request.get_json() 
        received_hash = data.get('hash')
        response = currentAuthorizationChecks[received_hash][4]
        if currentAuthorizationChecks[received_hash][4]:
            del currentAuthorizationChecks[received_hash]
        return jsonify({"message": response}), 200

@app.route('/verify-registration')
def verifyRegistration():
    # Get the 'id' parameter from the URL query string
    hashValue = request.args.get('val')

    if hashValue not in currentAuthorizationChecks:
        print("Fake or expired validation link")
        return render_template('login-redirect.html'), 200

    else:
        oldTuple = currentAuthorizationChecks[hashValue]
        newTuple = oldTuple[:4] + (True,) + oldTuple[5:]
        currentAuthorizationChecks[hashValue] = newTuple
        result = registerUserIntoDatabase(currentAuthorizationChecks[hashValue][0],currentAuthorizationChecks[hashValue][1],currentAuthorizationChecks[hashValue][2])
        print(f"new list: {currentAuthorizationChecks}")
        return render_template('login-redirect.html'), 200

# Registering account helper functions
def registerUserIntoDatabase(username, email, password):
    try:
        insert_sql = text("""
            INSERT INTO users (username, email, password)
            VALUES (:username, :email, :password)
        """)
        db.session.execute(insert_sql, {
            "username": username,
            "email": email,
            "password": password
        })
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
    return False

# Authentication management, probably move to another file soon

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

