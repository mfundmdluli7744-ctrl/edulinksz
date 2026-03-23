from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import User
from extensions import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_based_on_role(current_user.role)
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect_based_on_role(user.role)
        else:
            flash('Invalid username or password. Please try again.', 'danger')
            
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

def redirect_based_on_role(role):
    if role == 'Admin':
        return redirect(url_for('admin.dashboard'))
    elif role == 'Teacher':
        return redirect(url_for('teacher.dashboard'))
    elif role == 'Parent':
        return redirect(url_for('parent.dashboard'))
    elif role == 'Principal':
        return redirect(url_for('principal.dashboard'))
    return redirect(url_for('auth.login'))
