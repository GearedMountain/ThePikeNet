from flask import render_template, request, redirect, url_for, session, jsonify
from pikenet.utils.decorators import login_required, role_required
from .models import checkLoginCredentials, isAccountUnique, registerAccount
import hashlib
from .emailRegistrar import registerValidated, createAuthCheck, verifyRegistrationHash
from . import bp

@bp.route('/')
def index():
    print(session.get('auth_level'))
    return render_template('index.html')


@bp.route('/login', methods=['GET', 'POST'])
#@role_required(0)
def login():
    if request.method == 'POST':
        # fake login example
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        response = checkLoginCredentials(username, password)
        if response == None:
            return render_template('login.html', error="Invalid credentials")
        else:
            userId, authValue = response
            session['user_id'] = userId
            session['username'] = username
            session['auth_value'] = authValue
        return redirect(url_for('main.index'))

    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
#@role_required(0)
def register():
    if request.method == 'POST':
        # fake login example
        data = request.get_json() 
        username = data.get('username')
        email = data.get('email') 
        password = data.get('password')

        result = isAccountUnique(username, password, email)
        
        if not result:
            return jsonify({"message": "Not unique"}), 400
            
        # If valid and unique, start verification process before officially adding it to the database    
        hashValue = sha1Hash(username + email + password); 
        if not username.isalnum():
            return jsonify({"message": "Invalid characters in username"}), 400 
        
        # Password must be 8 characters
        if not len(password) >= 8:
            return jsonify({"message": "Password not long enough"}), 400
        
        # No spaces or illegal characters in email
        email = email.replace(" ", "")

        createAuthCheck(username, password, email, hashValue)
        return jsonify({"message": "WaitToValidate", "hashValue": hashValue}), 200

        registerAccount(username, password, email)    
    return render_template('register.html')
    
@bp.route('/register-check', methods=['POST'])
def registerCheck():
        data = request.get_json() 
        receivedHash = data.get('hash')

        response = registerValidated(receivedHash)
        return jsonify({"message": response}), 200

@bp.route('/verify-registration')
def verifyRegistration():
    # Get the 'id' parameter from the URL query string
    hashValue = request.args.get('val')
    verifyRegistrationHash(hashValue)
    return render_template('login-redirect.html'), 200

def sha1Hash(message: str) -> str:
    # Encode the string to bytes, then hash it
    sha1 = hashlib.sha1()
    sha1.update(message.encode('utf-8'))
    return sha1.hexdigest()