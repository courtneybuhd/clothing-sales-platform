"""
File: app/controllers/customer_controller.py
Description: Customer management controller for the Multi-Brand Clothing Sales Platform.
             Handles customer profile updates, address management, and data retrieval.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

from app import db
from app.models.user import Customer, Address, User
from app.models.order import Order
from app.models.review import Review


class CustomerController:
    """
    Controller class for customer profile and data management operations.
    All methods are static and can be called without instantiation.
    """
    
    @staticmethod
    def get_customer_by_id(customer_id):
        """
        Retrieve a customer by their ID.
        
        Args:
            customer_id (str): UUID of the customer
            
        Returns:
            Customer: Customer object or None if not found
        """
        return Customer.query.get(customer_id)
    
    @staticmethod
    def update_profile(customer, name=None, email=None):
        """
        Update a customer's profile information.
        
        Args:
            customer (Customer): Customer to update
            name (str, optional): New name
            email (str, optional): New email address
            
        Returns:
            Customer: Updated customer object
        """
        # Update name if provided
        if name is not None:
            customer.name = name
        
        # Update email if provided and ensure uniqueness
        if email is not None:
            # Check if email is already in use by another user
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != customer.id:
                raise ValueError("Email address already in use by another account")
            customer.email = email
        
        try:
            db.session.commit()
            return customer
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update customer profile: {str(e)}")
    
    @staticmethod
    def add_address(customer, name, line1, line2, city, state, zip_code, country):
        """
        Add a new shipping address for a customer.
        
        Args:
            customer (Customer): Customer to add address for
            name (str): Recipient name
            line1 (str): Address line 1
            line2 (str): Address line 2
            city (str): City
            state (str): State/Province
            zip_code (str): ZIP/Postal code
            country (str): Country
            
        Returns:
            Address: The newly created address
        """
        # Use the Customer model's add_address method
        address = customer.add_address(
            name=name,
            line1=line1,
            line2=line2,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country
        )
        
        try:
            db.session.commit()
            return address
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to add address: {str(e)}")
    
    @staticmethod
    def delete_address(address_id):
        """
        Delete a customer's shipping address.
        
        Args:
            address_id (str): UUID of the address to delete
            
        Returns:
            bool: True if deletion succeeded, False if address not found
        """
        address = Address.query.get(address_id)
        
        if not address:
            return False
        
        try:
            db.session.delete(address)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete address: {str(e)}")
    
    @staticmethod
    def get_customer_orders(customer):
        """
        Retrieve all orders for a specific customer.
        
        Args:
            customer (Customer): Customer whose orders to retrieve
            
        Returns:
            list: List of Order objects, ordered by creation date (newest first)
        """
        orders = Order.query.filter_by(customer_id=customer.id)\
                           .order_by(Order.created_at.desc())\
                           .all()
        return orders
    
    @staticmethod
    def get_customer_reviews(customer):
        """
        Retrieve all reviews created by a specific customer.
        
        Args:
            customer (Customer): Customer whose reviews to retrieve
            
        Returns:
            list: List of Review objects, ordered by creation date (newest first)
        """
        reviews = Review.query.filter_by(customer_id=customer.id)\
                             .order_by(Review.created_at.desc())\
                             .all()
        return reviews
