"""
File: app/models/order.py
Description: Order, OrderItem, and PaymentRecord entity models for the Multi-Brand Clothing Sales Platform.
             Implements order management, line items, and payment tracking.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

import uuid
from datetime import datetime
from app import db


class Order(db.Model):
    """
    Order entity representing a customer's purchase.
    Contains order items, payment information, and fulfillment status.
    """
    __tablename__ = 'orders'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to customer (users table)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), 
                           nullable=False, index=True)
    
    # Order status tracking
    status = db.Column(db.String(50), default='pending', nullable=False, index=True)
    
    # Total amount for the order
    total_amount = db.Column(db.Numeric(10, 2), default=0.0, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, 
                          onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to customer
    customer = db.relationship('Customer', back_populates='orders')
    
    # Relationship to order items
    items = db.relationship('OrderItem', back_populates='order', 
                           lazy=True, cascade='all, delete-orphan')
    
    # One-to-one relationship to payment record
    payment_record = db.relationship('PaymentRecord', back_populates='order',
                                    uselist=False, cascade='all, delete-orphan')
    
    def calculate_total(self):
        """
        Calculate the total amount for the order by summing all line items.
        Updates the total_amount field.
        
        Returns:
            Decimal: Total amount for the order
        """
        total = 0
        for item in self.items:
            total += item.line_total
        
        self.total_amount = total
        self.updated_at = datetime.utcnow()
        return total
    
    def add_item(self, sku, quantity):
        """
        Add a product SKU to the order as a line item.
        
        Args:
            sku (SKU): The SKU object to add
            quantity (int): Quantity to order
            
        Returns:
            OrderItem: The created order item
        """
        # Get the current price from the product
        if sku.product:
            unit_price = sku.product.get_final_price(sku)
            line_total = unit_price * quantity
            
            # Create new order item
            order_item = OrderItem(
                order_id=self.id,
                product_id=sku.product_id,
                sku_id=sku.id,
                quantity=quantity,
                unit_price=unit_price,
                line_total=line_total
            )
            
            db.session.add(order_item)
            self.updated_at = datetime.utcnow()
            
            # Recalculate order total
            self.calculate_total()
            
            return order_item
        return None
    
    def __repr__(self):
        return f'<Order {self.id} - Status: {self.status}>'


class OrderItem(db.Model):
    """
    Individual line item within an order.
    Records the product, SKU, quantity, and price at time of purchase.
    """
    __tablename__ = 'order_items'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to order
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), 
                        nullable=False, index=True)
    
    # Foreign key to product (for reference even if SKU is deleted)
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), 
                          nullable=False, index=True)
    
    # Foreign key to specific SKU variant
    sku_id = db.Column(db.String(36), db.ForeignKey('skus.id'), 
                      nullable=False, index=True)
    
    # Order details
    quantity = db.Column(db.Integer, nullable=False)
    
    # Price snapshot at time of order (prevents price changes from affecting past orders)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    line_total = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Relationship to order
    order = db.relationship('Order', back_populates='items')
    
    # Relationship to product
    product = db.relationship('Product', back_populates='order_items')
    
    # Relationship to SKU (no back_populates defined in SKU for order_items)
    sku = db.relationship('SKU')
    
    def __repr__(self):
        return f'<OrderItem {self.id} - Product {self.product_id} × {self.quantity}>'


class PaymentRecord(db.Model):
    """
    Payment record entity tracking payment transaction details for an order.
    Maintains one-to-one relationship with Order.
    """
    __tablename__ = 'payment_records'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to order (unique for one-to-one relationship)
    order_id = db.Column(db.String(36), db.ForeignKey('orders.id'), 
                        unique=True, nullable=False, index=True)
    
    # Payment amount
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Payment method (credit_card, paypal, etc.)
    method = db.Column(db.String(50), nullable=False)
    
    # External transaction ID from payment gateway
    transaction_id = db.Column(db.String(200), index=True)
    
    # Payment timestamp
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to order (one-to-one)
    order = db.relationship('Order', back_populates='payment_record')
    
    def __repr__(self):
        return f'<PaymentRecord {self.id} - Order {self.order_id} - Method: {self.method}>'
