"""
File: app/controllers/vendor_controller.py
Description: Vendor management controller for the Multi-Brand Clothing Sales Platform.
             Handles vendor-specific data including products and orders containing vendor items.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

from app import db
from app.models.user import Vendor
from app.models.product import Product, SKU
from app.models.order import OrderItem, Order


class VendorController:
    """
    Controller class for vendor-specific operations and data retrieval.
    All methods are static and can be called without instantiation.
    """
    
    @staticmethod
    def get_vendor_by_id(vendor_id):
        """
        Retrieve a vendor by their ID.
        
        Args:
            vendor_id (str): UUID of the vendor
            
        Returns:
            Vendor: Vendor object or None if not found
        """
        return Vendor.query.get(vendor_id)
    
    @staticmethod
    def get_vendor_products(vendor):
        """
        Retrieve all products owned by a specific vendor.
        
        Args:
            vendor (Vendor): Vendor whose products to retrieve
            
        Returns:
            list: List of Product objects owned by the vendor
        """
        products = Product.query.filter_by(vendor_id=vendor.id)\
                               .order_by(Product.created_at.desc())\
                               .all()
        return products
    
    @staticmethod
    def get_vendor_orders(vendor):
        """
        Retrieve all orders that contain products from this vendor.
        Uses OrderItem -> Product relationship to find relevant orders.
        
        Args:
            vendor (Vendor): Vendor whose orders to retrieve
            
        Returns:
            list: List of unique Order objects containing vendor's products
        """
        # Get all products owned by this vendor
        vendor_product_ids = [p.id for p in vendor.products]
        
        if not vendor_product_ids:
            return []
        
        # Find all order items that reference this vendor's products
        order_items = OrderItem.query.filter(
            OrderItem.product_id.in_(vendor_product_ids)
        ).all()
        
        # Extract unique order IDs
        order_ids = list(set([item.order_id for item in order_items]))
        
        if not order_ids:
            return []
        
        # Retrieve the actual Order objects
        orders = Order.query.filter(Order.id.in_(order_ids))\
                           .order_by(Order.created_at.desc())\
                           .all()
        
        return orders
    
    @staticmethod
    def set_vendor_approval(vendor, approved):
        """
        Update a vendor's approval status.
        Approved vendors can list products; unapproved vendors cannot.
        
        Args:
            vendor (Vendor): Vendor whose approval status to update
            approved (bool): True to approve, False to revoke approval
            
        Returns:
            Vendor: Updated vendor object
        """
        # Use the Vendor model's set_approved method
        vendor.set_approved(approved)
        
        try:
            db.session.commit()
            return vendor
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update vendor approval status: {str(e)}")
