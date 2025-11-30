"""
File: app/routes/main.py
Description: Main routes for the Multi-Brand Clothing Sales Platform.
             Handles the landing page and root URL redirects.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 29, 2025
"""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import current_user


main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """
    Landing page route.
    Redirects authenticated users to their role-specific dashboard.
    Shows public landing page for unauthenticated visitors.
    """
    if current_user.is_authenticated:
        if current_user.role == 'customer':
            return redirect(url_for('customer.catalog'))
        elif current_user.role == 'vendor':
            return redirect(url_for('vendor.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('auth.login'))
    
    return render_template('home.html')
