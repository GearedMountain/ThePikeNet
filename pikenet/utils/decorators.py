from functools import wraps
from flask import session, redirect, url_for, flash

def login_required(view_func):
    """
    Decorator to ensure the user is logged in.
    Redirects to login page if not authenticated.
    """
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if 'username' not in session:
            flash("Please log in to access this page.", "warning")
            return redirect(url_for('main.login'))  # Adjust 'main.login' to your login route
        return view_func(*args, **kwargs)
    return wrapped_view


def role_required(*roles):
    """
    Decorator to restrict access to users with specific auth levels.
    Example usage: @roles_required(0, 1) allows auth_level 0 or 1.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            auth_value = session.get('auth_value')
            if auth_value not in roles:
                return "unauthorized", 500  # Or another 'unauthorized' page
            return view_func(*args, **kwargs)
        return wrapped_view
    return decorator
