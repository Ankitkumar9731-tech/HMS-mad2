from functools import wraps
from flask import session, flash, redirect, url_for
from models import User, db

# Decorator for role-based access control
def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            user = User.query.get(session['user_id'])
            if not user or user.role not in roles or user.is_blacklisted:
                flash('You do not have permission to access this page.', 'danger')
                return redirect(url_for('auth.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

