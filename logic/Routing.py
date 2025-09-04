from flask import Blueprint, render_template

basic_routing = Blueprint('basic_routing', __name__)

# Login Page
@basic_routing.route('/')
def index():
    return render_template('index.html', pikenetVersion=1.0)
    
# Register Page
@basic_routing.route('/register-account')
def registerAccount():
    return render_template('register-account.html')
