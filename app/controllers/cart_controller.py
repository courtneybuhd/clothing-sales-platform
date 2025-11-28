"""
File: app/controllers/cart_controller.py
Description: Shopping cart management controller for the Multi-Brand Clothing Sales Platform.
             Provides cart creation, item management, and total calculation functionality.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

from datetime import datetime
from app import db
from app.models.user import Customer
from app.models.cart import Cart, CartItem
from app.models.product import SKU


class CartController:
    """
    Controller class for shopping cart operations.
    All methods are static and can be called without instantiation.
    """
    
    @staticmethod
    def get_or_create_active_cart(customer):
        """
        Get the customer's active cart or create a new one if none exists.
        For simplicity, we return the most recently created cart or create a new one.
        
        Args:
            customer (Customer): Customer whose cart to retrieve/create
            
        Returns:
            Cart: The active cart for the customer
        """
        # Look for the customer's most recent cart
        active_cart = Cart.query.filter_by(customer_id=customer.id)\
                                .order_by(Cart.created_at.desc())\
                                .first()
        
        # If no cart exists, create a new one
        if not active_cart:
            active_cart = Cart(customer_id=customer.id)
            db.session.add(active_cart)
            db.session.commit()
        
        return active_cart
    
    @staticmethod
    def add_item_to_cart(cart, sku_id, quantity):
        """
        Add a SKU to the cart or update quantity if it already exists.
        
        Args:
            cart (Cart): Cart to add item to
            sku_id (str): UUID of the SKU to add
            quantity (int): Quantity to add
            
        Returns:
            CartItem: The created or updated cart item
        """
        # Look up the SKU
        sku = SKU.query.get(sku_id)
        
        if not sku:
            raise ValueError(f"SKU with id {sku_id} not found")
        
        # Check if SKU is available
        if not sku.is_available():
            raise ValueError(f"SKU {sku_id} is not available or out of stock")
        
        # Check if we have enough inventory
        if sku.inventory < quantity:
            raise ValueError(f"Insufficient inventory. Only {sku.inventory} available")
        
        # Use the Cart model's add_item method
        cart_item = cart.add_item(sku, quantity)
        
        try:
            db.session.commit()
            return cart_item
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to add item to cart: {str(e)}")
    
    @staticmethod
    def remove_item_from_cart(cart, sku_id):
        """
        Remove a specific SKU from the cart.
        
        Args:
            cart (Cart): Cart to remove item from
            sku_id (str): UUID of the SKU to remove
            
        Returns:
            bool: True if item was removed, False if not found
        """
        # Use the Cart model's remove_item method
        result = cart.remove_item(sku_id)
        
        try:
            db.session.commit()
            return result
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to remove item from cart: {str(e)}")
    
    @staticmethod
    def update_item_quantity(cart, sku_id, quantity):
        """
        Update the quantity of a cart item. If quantity <= 0, remove the item.
        
        Args:
            cart (Cart): Cart containing the item
            sku_id (str): UUID of the SKU to update
            quantity (int): New quantity (if <= 0, item is removed)
            
        Returns:
            CartItem: Updated cart item, or None if removed/not found
        """
        # If quantity is 0 or negative, remove the item
        if quantity <= 0:
            CartController.remove_item_from_cart(cart, sku_id)
            return None
        
        # Find the cart item
        cart_item = CartItem.query.filter_by(
            cart_id=cart.id,
            sku_id=sku_id
        ).first()
        
        if not cart_item:
            return None
        
        # Check inventory availability
        if cart_item.sku and cart_item.sku.inventory < quantity:
            raise ValueError(f"Insufficient inventory. Only {cart_item.sku.inventory} available")
        
        # Update the quantity
        cart_item.quantity = quantity
        cart.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return cart_item
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update cart item quantity: {str(e)}")
    
    @staticmethod
    def clear_cart(cart):
        """
        Remove all items from the cart.
        
        Args:
            cart (Cart): Cart to clear
        """
        # Use the Cart model's clear method
        cart.clear()
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to clear cart: {str(e)}")
    
    @staticmethod
    def calculate_cart_total(cart):
        """
        Calculate the total price for all items in the cart.
        
        Args:
            cart (Cart): Cart to calculate total for
            
        Returns:
            Decimal: Total price of all items in the cart
        """
        # Use the Cart model's get_total_price method
        return cart.get_total_price()
