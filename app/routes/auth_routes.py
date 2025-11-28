"""
File: app/routes/auth_routes.py
Description: Authentication routes for the Multi-Brand Clothing Sales Platform.
             Handles login, logout, and registration for customers and vendors.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import current_user, login_required
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from app.controllers.auth_controller import AuthController


# Define authentication blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# Form classes
class LoginForm(FlaskForm):
    """Form for user login."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class CustomerRegisterForm(FlaskForm):
    """Form for customer registration."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')


class VendorRegisterForm(FlaskForm):
    """Form for vendor registration."""
    name = StringField('Contact Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    business_name = StringField('Business Name', validators=[DataRequired(), Length(min=2, max=200)])
    tax_id = StringField('Tax ID', validators=[DataRequired(), Length(min=5, max=50)])
    submit = SubmitField('Register as Vendor')


# Routes
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """
    Handle user login for all user types (customer, vendor, admin).
    """
    # Redirect if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        # Authenticate user
        user = AuthController.authenticate_user(form.email.data, form.password.data)
        
        if user is None:
            flash("Invalid email or password. Please try again.", "danger")
            return render_template("auth/login.html", form=form)
        
        # Attempt to log in the user
        success, error_message = AuthController.login_user_account(user, remember=False)
        
        if not success:
            flash(error_message, "danger")
            return render_template("auth/login.html", form=form)
        
        # Successful login
        flash(f"Welcome back, {user.name}!", "success")
        
        # Redirect to next page if specified, otherwise to index
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for("main.index"))
    
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    """
    Log out the current user.
    """
    AuthController.logout_current_user()
    flash("You have been logged out successfully.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/register/customer", methods=["GET", "POST"])
def register_customer():
    """
    Handle customer registration.
    """
    # Redirect if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = CustomerRegisterForm()
    
    if form.validate_on_submit():
        # Attempt to register the customer
        customer, error_message = AuthController.register_customer(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data
        )
        
        if customer is None:
            flash(error_message, "danger")
            return render_template("auth/register_customer.html", form=form)
        
        # Registration successful
        flash("Account created successfully! Please log in.", "success")
        
        # Optionally auto-login the user
        AuthController.login_user_account(customer, remember=False)
        
        return redirect(url_for("main.index"))
    
    return render_template("auth/register_customer.html", form=form)


@auth_bp.route("/register/vendor", methods=["GET", "POST"])
def register_vendor():
    """
    Handle vendor registration. Vendor accounts require admin approval.
    """
    # Redirect if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    
    form = VendorRegisterForm()
    
    if form.validate_on_submit():
        # Attempt to register the vendor
        vendor, error_message = AuthController.register_vendor(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            business_name=form.business_name.data,
            tax_id=form.tax_id.data
        )
        
        if vendor is None:
            flash(error_message, "danger")
            return render_template("auth/register_vendor.html", form=form)
        
        # Vendor registration successful but pending approval
        flash(
            "Vendor account created successfully! Your account is pending admin approval. "
            "You will be notified once approved.",
            "info"
        )
        
        return redirect(url_for("auth.login"))
    
    return render_template("auth/register_vendor.html", form=form)
