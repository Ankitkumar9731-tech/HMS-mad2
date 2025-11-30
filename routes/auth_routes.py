from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Patient
from utils import role_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            if user.is_blacklisted:
                flash('Your account has been blacklisted. Please contact administrator.', 'danger')
                return render_template('login.html')
            
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('Login successful!', 'success')
            return redirect(url_for('auth.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose another.', 'danger')
            return render_template('register.html')
        
        # Create user
        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            role='patient'
        )
        db.session.add(user)
        db.session.flush()
        
        # Create patient profile
        patient = Patient(
            user_id=user.id,
            fullname=username  # Default, can be updated later
        )
        db.session.add(patient)
        db.session.commit()
        
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/dashboard')
@role_required(['admin', 'doctor', 'patient'])
def dashboard():
    role = session.get('role')
    
    if role == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif role == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    else:
        return redirect(url_for('patient.dashboard'))

