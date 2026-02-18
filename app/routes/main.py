"""
Main routes for the application
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    """Home page route - redirects based on user role or to login"""
    if current_user.is_authenticated:
        # Redirect based on user role
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'officer':
            return redirect(url_for('officer.dashboard'))
        else:
            return redirect(url_for('citizen.dashboard'))
    return redirect(url_for('auth.login'))

@bp.route('/about')
def about():
    """About page route"""
    return render_template('about.html')
