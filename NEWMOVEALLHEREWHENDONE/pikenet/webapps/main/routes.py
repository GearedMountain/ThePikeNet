from flask import render_template, request, redirect, url_for, session
from pikenet.utils.decorators import login_required, role_required
from . import bp

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/login', methods=['GET', 'POST'])
#@role_required(0)
def login():
    if request.method == 'POST':
        # fake login example
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'admin' and password == 'admin':
            session['user_id'] = 1
            session['auth_level'] = 0
            return redirect(url_for('main.index'))
        return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')
