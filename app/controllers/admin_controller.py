"""
File: app/controllers/admin_controller.py
Description: Administrator management controller for the Multi-Brand Clothing Sales Platform.
             Provides admin-level operations for user management, vendor approval, and order oversight.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

from app import db
from app.models.user import User, Customer, Vendor, Admin
from app.models.order import Order


class AdminController:
    """
    Controller class for administrator-level operations.
    All methods are static and can be called without instantiation.
    """
    
    @staticmethod
    def list_all_users():
        """
        Retrieve all users in the system (customers, vendors, and admins).
        
        Returns:
            list: List of all User objects
        """
        users = User.query.order_by(User.created_at.desc()).all()
        return users
    
    @staticmethod
    def list_vendors(pending_only=False):
        """
        Retrieve all vendors, optionally filtering for pending approval.
        
        Args:
            pending_only (bool): If True, return only unapproved vendors
            
        Returns:
            list: List of Vendor objects matching criteria
        """
        query = Vendor.query
        
        if pending_only:
            # Filter for vendors awaiting approval
            query = query.filter_by(approved=False)
        
        vendors = query.order_by(Vendor.created_at.desc()).all()
        return vendors
    
    @staticmethod
    def approve_vendor(vendor_id):
        """
        Approve a vendor's application, allowing them to list products.
        Also ensures the vendor is not suspended.
        
        Args:
            vendor_id (str): UUID of the vendor to approve
            
        Returns:
            Vendor: Approved vendor object, or None if not found
        """
        vendor = Vendor.query.get(vendor_id)
        
        if not vendor:
            return None
        
        # Set approved to True and ensure not suspended
        vendor.approved = True
        vendor.suspended = False
        
        try:
            db.session.commit()
            return vendor
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to approve vendor: {str(e)}")
    
    @staticmethod
    def suspend_user(user_id):
        """
        Suspend a user account, preventing login and platform access.
        
        Args:
            user_id (str): UUID of the user to suspend
            
        Returns:
            User: Suspended user object, or None if not found
        """
        user = User.query.get(user_id)
        
        if not user:
            return None
        
        # Set suspended flag to True
        user.suspended = True
        
        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to suspend user: {str(e)}")
    
    @staticmethod
    def unsuspend_user(user_id):
        """
        Remove suspension from a user account, restoring access.
        
        Args:
            user_id (str): UUID of the user to unsuspend
            
        Returns:
            User: Unsuspended user object, or None if not found
        """
        user = User.query.get(user_id)
        
        if not user:
            return None
        
        # Set suspended flag to False
        user.suspended = False
        
        try:
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to unsuspend user: {str(e)}")
    
    @staticmethod
    def list_all_orders():
        """
        Retrieve all orders in the system for admin oversight.
        
        Returns:
            list: List of all Order objects, ordered by creation date
        """
        orders = Order.query.order_by(Order.created_at.desc()).all()
        return orders
    
    @staticmethod
    def get_order_by_id(order_id):
        """
        Retrieve a specific order by its ID.
        
        Args:
            order_id (str): UUID of the order
            
        Returns:
            Order: Order object or None if not found
        """
        return Order.query.get(order_id)
