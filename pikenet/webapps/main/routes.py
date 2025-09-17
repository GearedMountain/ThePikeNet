from flask import render_template, request, redirect, url_for, session
from pikenet.utils.decorators import login_required, role_required
from .models import checkLoginCredentials
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
            userId, authLevel = response
            session['user_id'] = userId
            session['username'] = username
            session['auth_value'] = authValue
        return redirect(url_for('main.index'))

    return render_template('login.html')
