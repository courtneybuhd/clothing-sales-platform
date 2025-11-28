"""
File: app/models/cart.py
Description: Cart and CartItem entity models for the Multi-Brand Clothing Sales Platform.
             Implements shopping cart functionality with item management and total calculation.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

import uuid
from datetime import datetime
from app import db


class Cart(db.Model):
    """
    Shopping cart entity for customers to manage items before checkout.
    Each customer can have multiple carts (active and historical).
    """
    __tablename__ = 'carts'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to customer (users table)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), 
                           nullable=False, index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to customer
    customer = db.relationship('Customer', back_populates='carts')
    
    # Relationship to cart items
    items = db.relationship('CartItem', back_populates='cart', 
                           lazy=True, cascade='all, delete-orphan')
    
    def add_item(self, sku, quantity):
        """
        Add a product SKU to the cart or update quantity if already exists.
        
        Args:
            sku (SKU): The SKU object to add
            quantity (int): Quantity to add
            
        Returns:
            CartItem: The created or updated cart item
        """
        # Check if item already exists in cart
        existing_item = CartItem.query.filter_by(
            cart_id=self.id,
            sku_id=sku.id
        ).first()
        
        if existing_item:
            # Update quantity of existing item
            existing_item.quantity += quantity
            self.updated_at = datetime.utcnow()
            return existing_item
        else:
            # Create new cart item
            new_item = CartItem(
                cart_id=self.id,
                sku_id=sku.id,
                quantity=quantity
            )
            db.session.add(new_item)
            self.updated_at = datetime.utcnow()
            return new_item
    
    def remove_item(self, sku_id):
        """
        Remove a specific SKU from the cart.
        
        Args:
            sku_id (str): UUID of the SKU to remove
            
        Returns:
            bool: True if item was removed, False if not found
        """
        item = CartItem.query.filter_by(
            cart_id=self.id,
            sku_id=sku_id
        ).first()
        
        if item:
            db.session.delete(item)
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def get_total_price(self):
        """
        Calculate the total price of all items in the cart.
        
        Returns:
            Decimal: Total price including all items and their quantities
        """
        total = 0
        for item in self.items:
            # Get the final price from the product including SKU adjustments
            if item.sku and item.sku.product:
                item_price = item.sku.product.get_final_price(item.sku)
                total += item_price * item.quantity
        return total
    
    def clear(self):
        """
        Remove all items from the cart.
        """
        # Delete all cart items (cascade will handle this)
        for item in self.items:
            db.session.delete(item)
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f'<Cart {self.id} for customer {self.customer_id}>'


class CartItem(db.Model):
    """
    Individual item within a shopping cart.
    Links a specific SKU variant to a cart with a quantity.
    """
    __tablename__ = 'cart_items'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to cart
    cart_id = db.Column(db.String(36), db.ForeignKey('carts.id'), 
                       nullable=False, index=True)
    
    # Foreign key to SKU
    sku_id = db.Column(db.String(36), db.ForeignKey('skus.id'), 
                      nullable=False, index=True)
    
    # Quantity of this SKU in the cart
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    # Relationship to cart
    cart = db.relationship('Cart', back_populates='items')
    
    # Relationship to SKU
    sku = db.relationship('SKU', back_populates='cart_items')
    
    def get_item_total(self):
        """
        Calculate the total price for this cart item (price × quantity).
        
        Returns:
            Decimal: Total price for this line item
        """
        if self.sku and self.sku.product:
            unit_price = self.sku.product.get_final_price(self.sku)
            return unit_price * self.quantity
        return 0
    
    def __repr__(self):
        return f'<CartItem {self.id} - SKU {self.sku_id} × {self.quantity}>'
