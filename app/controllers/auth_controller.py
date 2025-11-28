"""
File: app/controllers/auth_controller.py
Description: Authentication controller for the Multi-Brand Clothing Sales Platform.
             Provides user registration, login, logout, and password management functionality.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

from app import db
from app.models.user import User, Customer, Vendor, Admin
from flask_login import login_user, logout_user


class AuthController:
    """
    Controller class for authentication and user management operations.
    All methods are static and can be called without instantiation.
    """
    
    @staticmethod
    def register_customer(name, email, password):
        """
        Register a new customer account.
        
        Args:
            name (str): Customer's full name
            email (str): Customer's email address
            password (str): Plain text password
            
        Returns:
            tuple: (Customer object, None) on success, (None, error_message) on failure
        """
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "Email address already registered"
        
        # Create new customer
        customer = Customer(
            name=name,
            email=email,
            role='customer'
        )
        
        # Hash and set password
        customer.set_password(password)
        
        # Customer accounts are approved by default
        customer.approved = True
        
        try:
            db.session.add(customer)
            db.session.commit()
            return customer, None
        except Exception as e:
            db.session.rollback()
            return None, f"Registration failed: {str(e)}"
    
    @staticmethod
    def register_vendor(name, email, password, business_name, tax_id):
        """
        Register a new vendor account (requires admin approval).
        
        Args:
            name (str): Vendor contact name
            email (str): Vendor email address
            password (str): Plain text password
            business_name (str): Business/brand name
            tax_id (str): Tax identification number
            
        Returns:
            tuple: (Vendor object, None) on success, (None, error_message) on failure
        """
        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return None, "Email address already registered"
        
        # Create new vendor
        vendor = Vendor(
            name=name,
            email=email,
            role='vendor',
            business_name=business_name,
            tax_id=tax_id
        )
        
        # Hash and set password
        vendor.set_password(password)
        
        # Vendors default to approved=False (handled in Vendor.__init__)
        # but we explicitly set it here for clarity
        vendor.approved = False
        
        try:
            db.session.add(vendor)
            db.session.commit()
            return vendor, None
        except Exception as e:
            db.session.rollback()
            return None, f"Vendor registration failed: {str(e)}"
    
    @staticmethod
    def authenticate_user(email, password):
        """
        Authenticate a user by email and password.
        
        Args:
            email (str): User's email address
            password (str): Plain text password to verify
            
        Returns:
            User: User object if authentication succeeds, None otherwise
        """
        # Look up user by email
        user = User.query.filter_by(email=email).first()
        
        # Verify user exists and password matches
        if user and user.check_password(password):
            return user
        
        return None
    
    @staticmethod
    def login_user_account(user, remember=False):
        """
        Log in a user account with Flask-Login.
        Enforces business rules: user must not be suspended,
        and vendors must be approved.
        
        Args:
            user (User): User object to log in
            remember (bool): Whether to remember the user session
            
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
        """
        # Check if user is suspended
        if user.suspended:
            return False, "Account has been suspended. Please contact support."
        
        # Check if vendor is approved
        if user.role == 'vendor' and not user.approved:
            return False, "Vendor account pending approval. Please wait for admin approval."
        
        # Perform Flask-Login login
        login_user(user, remember=remember)
        return True, None
    
    @staticmethod
    def logout_current_user():
        """
        Log out the current user session.
        
        Returns:
            bool: Always returns True
        """
        logout_user()
        return True
    
    @staticmethod
    def change_password(user, old_password, new_password):
        """
        Change a user's password after verifying the old password.
        
        Args:
            user (User): User object whose password to change
            old_password (str): Current password for verification
            new_password (str): New password to set
            
        Returns:
            tuple: (True, None) on success, (False, error_message) on failure
        """
        # Verify old password
        if not user.check_password(old_password):
            return False, "Current password is incorrect"
        
        # Set new password
        user.set_password(new_password)
        
        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Password change failed: {str(e)}"
