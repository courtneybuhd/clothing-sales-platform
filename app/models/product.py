"""
File: app/models/product.py
Description: Product and SKU entity models for the Multi-Brand Clothing Sales Platform.
             Implements Product catalog with variant SKUs for size/color combinations.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 29, 2025
"""

import uuid
from datetime import datetime
from app import db


class Product(db.Model):
    """
    Product entity representing a clothing item in the catalog.
    Each product belongs to a vendor and can have multiple SKU variants.
    """
    __tablename__ = 'products'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to vendor (users table)
    vendor_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Product information
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100), nullable=False, index=True)
    base_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Optional product image URL
    image_url = db.Column(db.String(500))
    
    # Availability flag
    available = db.Column(db.Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to vendor (must match backref from User model)
    vendor = db.relationship('Vendor', back_populates='products')
    
    # Relationship to SKU variants
    skus = db.relationship('SKU', back_populates='product', 
                          lazy=True, cascade='all, delete-orphan')
    
    # Relationship to order items
    order_items = db.relationship('OrderItem', back_populates='product',
                                 lazy='dynamic', cascade='all, delete-orphan')
    
    # Relationship to reviews
    reviews = db.relationship('Review', back_populates='product',
                            lazy='dynamic', cascade='all, delete-orphan')
    
    def get_active_variants(self):
        """
        Get all SKU variants that have inventory available.
        
        Returns:
            list: List of SKU objects with inventory > 0
        """
        return [sku for sku in self.skus if sku.inventory > 0]
    
    def get_final_price(self, sku=None):
        """
        Calculate the final price for a product or specific SKU variant.
        
        Args:
            sku (SKU, optional): Specific SKU variant to price
            
        Returns:
            Decimal: Final price including any SKU price adjustment
        """
        if sku and sku.price_adjustment:
            return self.base_price + sku.price_adjustment
        return self.base_price
    
    def __repr__(self):
        return f'<Product {self.name} (category={self.category})>'


class SKU(db.Model):
    """
    SKU (Stock Keeping Unit) entity representing a specific variant of a product.
    Each SKU represents a unique size/color combination with its own inventory.
    """
    __tablename__ = 'skus'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to product
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), 
                          nullable=False, index=True)
    
    # Variant attributes
    size = db.Column(db.String(20), nullable=False)
    color = db.Column(db.String(50), nullable=False)
    
    # Inventory management
    inventory = db.Column(db.Integer, default=0, nullable=False)
    
    # Optional price adjustment for this specific variant
    price_adjustment = db.Column(db.Numeric(10, 2), default=0.0)
    
    # Relationship back to product
    product = db.relationship('Product', back_populates='skus')
    
    # Relationship to cart items
    cart_items = db.relationship('CartItem', back_populates='sku',
                                lazy='dynamic', cascade='all, delete-orphan')
    
    def is_available(self):
        """
        Check if this SKU variant is currently available for purchase.
        
        Returns:
            bool: True if inventory > 0 and parent product is available
        """
        return self.inventory > 0 and self.product.available
    
    def reserve_stock(self, quantity):
        """
        Attempt to reserve inventory for a cart or order.
        Must be called within a database transaction.
        
        Args:
            quantity (int): Number of units to reserve
            
        Returns:
            bool: True if reservation successful, False if insufficient inventory
        """
        if self.inventory >= quantity:
            self.inventory -= quantity
            return True
        return False
    
    def release_stock(self, quantity):
        """
        Return reserved inventory back to available stock.
        Used when items are removed from cart or orders are cancelled.
        
        Args:
            quantity (int): Number of units to return to inventory
        """
        self.inventory += quantity
    
    def __repr__(self):
        return f'<SKU {self.product.name if self.product else "Unknown"} - {self.color}/{self.size}>'
    