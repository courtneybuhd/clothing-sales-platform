"""
File: app/routes/auth_routes.py
Description: Authentication routes for the Multi-Brand Clothing Sales Platform.
             Handles user login, logout, and registration for customers and vendors.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 29, 2025
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user
from app.controllers.auth_controller import AuthController
from app.forms.auth_forms import LoginForm, CustomerRegistrationForm, VendorRegistrationForm


auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route.
    Authenticates users and redirects based on role.
    """
    form = LoginForm()
    
    if current_user.is_authenticated:
        if current_user.role == 'customer':
            return redirect(url_for('customer.catalog'))
        elif current_user.role == 'vendor':
            return redirect(url_for('vendor.dashboard'))
        elif current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    if form.validate_on_submit():
        user = AuthController.authenticate_user(form.email.data, form.password.data)
        
        if not user:
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html', form=form)
        
        remember = form.remember_me.data if hasattr(form, 'remember_me') else False
        success, error_message = AuthController.login_user_account(user, remember=remember)
        
        if not success:
            flash(error_message, 'danger')
            return render_template('auth/login.html', form=form)
        
        next_page = request.args.get('next')
        if next_page:
            return redirect(next_page)
        
        if user.role == 'customer':
            return redirect(url_for('customer.catalog'))
        elif user.role == 'vendor':
            return redirect(url_for('vendor.dashboard'))
        elif user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        else:
            return redirect(url_for('main.index'))
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/register/customer', methods=['GET', 'POST'])
def register_customer():
    """
    Customer registration route.
    Creates a new customer account.
    """
    form = CustomerRegistrationForm()
    
    if form.validate_on_submit():
        customer, error_message = AuthController.register_customer(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data
        )
        
        if error_message is not None:
            flash(error_message, 'danger')
            return render_template('auth/register_customer.html', form=form)
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_customer.html', form=form)


@auth_bp.route('/register/vendor', methods=['GET', 'POST'])
def register_vendor():
    """
    Vendor registration route.
    Creates a new vendor account pending admin approval.
    """
    form = VendorRegistrationForm()
    
    if form.validate_on_submit():
        vendor, error_message = AuthController.register_vendor(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            business_name=form.business_name.data,
            tax_id=form.tax_id.data
        )
        
        if error_message is not None:
            flash(error_message, 'danger')
            return render_template('auth/register_vendor.html', form=form)
        
        flash('Vendor account created successfully! Your account is pending admin approval.', 'info')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register_vendor.html', form=form)


@auth_bp.route('/logout')
def logout():
    """
    User logout route.
    Logs out the current user and redirects to login page.
    """
    AuthController.logout_current_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
