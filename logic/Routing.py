from flask import Blueprint, render_template
from logic.Authenticator import isLoggedIn

basic_routing = Blueprint('basic_routing', __name__)

# Login Page
@basic_routing.route('/')
def index():
    if isLoggedIn():
        return render_template('Dashboard/index.html')
    return render_template('index.html', pikenetVersion=1.0)
    
# Register Page
@basic_routing.route('/register-account')
def registerAccount():
    return render_template('register-account.html')

# Register Page
@basic_routing.route('/login-redirect')
def loginRedirect():
    return render_template('login-redirect.html')

# Authenticated Routing
@basic_routing.route('/dashboard')
def dashboardIndex():
    if isLoggedIn():
        return render_template('Dashboard/index.html')
    else:
        return "unauthenticated"