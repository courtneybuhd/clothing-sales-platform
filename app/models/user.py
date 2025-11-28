"""
File: app/models/user.py
Description: User entity models for the Multi-Brand Clothing Sales Platform.
             Implements User base class with Customer, Vendor, and Admin subclasses
             using single-table inheritance. Also includes Address model.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: [Update this date]
"""

import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """
    Base User class for all user types in the platform.
    Uses single-table inheritance with polymorphic discrimination on role.
    """
    __tablename__ = 'users'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Core user attributes
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Role-based discrimination for inheritance
    role = db.Column(db.String(20), nullable=False)
    
    # User status flags
    approved = db.Column(db.Boolean, default=True, nullable=False)
    suspended = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Single-table inheritance configuration
    __mapper_args__ = {
        'polymorphic_on': role,
        'polymorphic_identity': 'user'
    }
    
    def set_password(self, password):
        """
        Hash and store the user's password using werkzeug security.
        
        Args:
            password (str): Plain text password to hash
        """
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password (str): Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """
        Required by Flask-Login to return the user identifier.
        
        Returns:
            str: User's UUID as string
        """
        return str(self.id)
    
    def __repr__(self):
        return f'<User {self.email} (role={self.role})>'


class Customer(User):
    """
    Customer user type with shopping-related relationships.
    Customers can have multiple addresses, carts, orders, and reviews.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'customer'
    }
    
    # Relationships to other entities
    # FIXED: back_populates now points to 'user' not 'customer'
    addresses = db.relationship('Address', back_populates='user',
                               cascade='all, delete-orphan')
    carts = db.relationship('Cart', back_populates='customer')
    orders = db.relationship('Order', back_populates='customer')
    reviews = db.relationship('Review', back_populates='customer')
    
    def add_address(self, name, line1, line2, city, state, zip_code, country):
        """
        Add a new shipping address for this customer.
        
        Args:
            name (str): Recipient name
            line1 (str): Address line 1
            line2 (str): Address line 2
            city (str): City
            state (str): State/Province
            zip_code (str): ZIP/Postal code
            country (str): Country
            
        Returns:
            Address: The newly created address object
        """
        address = Address(
            user_id=self.id,
            name=name,
            line1=line1,
            line2=line2,
            city=city,
            state=state,
            zip=zip_code,
            country=country
        )
        db.session.add(address)
        return address


class Vendor(User):
    """
    Vendor user type representing clothing brand sellers.
    Vendors must be approved by admin before they can list products.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'vendor'
    }
    
    # Vendor-specific attributes
    business_name = db.Column(db.String(200))
    tax_id = db.Column(db.String(50))
    
    # Relationship to products managed by this vendor
    products = db.relationship('Product', back_populates='vendor')
    
    def __init__(self, **kwargs):
        """
        Initialize vendor with approved=False by default.
        """
        super().__init__(**kwargs)
        # New vendors require admin approval
        if 'approved' not in kwargs:
            self.approved = False
    
    def set_approved(self, approved_status):
        """
        Update the vendor's approval status.
        
        Args:
            approved_status (bool): True to approve, False to revoke approval
        """
        self.approved = approved_status


class Admin(User):
    """
    Administrator user type with platform management capabilities.
    Admins can approve vendors, manage users, and oversee the platform.
    """
    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }
    
    def __init__(self, **kwargs):
        """
        Initialize admin user with automatic approval.
        Admins are always approved and never suspended by default.
        """
        super().__init__(**kwargs)
        # Admins are automatically approved
        self.approved = True


class Address(db.Model):
    """
    Shipping address entity linked to Customer users.
    Stores complete address information for order fulfillment.
    """
    __tablename__ = 'addresses'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to users table (not customer-specific)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    # Address fields
    name = db.Column(db.String(100), nullable=False)
    line1 = db.Column(db.String(200), nullable=False)
    line2 = db.Column(db.String(200))
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    
    # FIXED: Relationship back to User (polymorphic), not Customer directly
    user = db.relationship('User', back_populates='addresses')
    
    def __repr__(self):
        return f'<Address {self.line1}, {self.city}, {self.state}>'
    