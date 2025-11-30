"""
File: app/utils/decorators.py
Description: Custom decorators for the Multi-Brand Clothing Sales Platform.
             Provides role-based access control for routes.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 29, 2025
"""

from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user


def role_required(required_role):
    """
    Decorator to restrict access to routes based on user role.
    
    Args:
        required_role (str): The role required to access the route
                            ('customer', 'vendor', or 'admin')
    
    Returns:
        function: Decorated function that enforces role-based access
    
    Usage:
        @app.route('/customer/dashboard')
        @login_required
        @role_required('customer')
        def customer_dashboard():
            return render_template('customer/dashboard.html')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            # Check if user has the required role
            if current_user.role != required_role:
                flash(f'Access denied. This page is only accessible to {required_role}s.', 'danger')
                return redirect(url_for('main.index'))
            
            # User is authenticated and has the correct role
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
