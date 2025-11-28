"""
File: app/controllers/order_controller.py
Description: Order management controller for the Multi-Brand Clothing Sales Platform.
             Handles order creation from cart, payment recording, and order status management.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

from datetime import datetime
from app import db
from app.models.user import Customer
from app.models.cart import Cart, CartItem
from app.models.product import Product, SKU
from app.models.order import Order, OrderItem, PaymentRecord


class OrderController:
    """
    Controller class for order processing and management operations.
    All methods are static and can be called without instantiation.
    """
    
    @staticmethod
    def create_order_from_cart(customer, cart):
        """
        Create a new order from a customer's shopping cart.
        Converts all cart items into order items and calculates totals.
        
        Args:
            customer (Customer): Customer placing the order
            cart (Cart): Cart to convert into an order
            
        Returns:
            Order: The newly created order
        """
        # Validate cart has items
        if not cart.items or len(cart.items) == 0:
            raise ValueError("Cannot create order from empty cart")
        
        # Create new order with pending status
        order = Order(
            customer_id=customer.id,
            status='pending',
            total_amount=0  # Will be calculated after adding items
        )
        
        db.session.add(order)
        # Flush to get the order.id for creating order items
        db.session.flush()
        
        # Convert each cart item to an order item
        for cart_item in cart.items:
            # Get the SKU and its parent product
            sku = cart_item.sku
            product = sku.product
            
            if not sku or not product:
                raise ValueError(f"Invalid cart item: missing SKU or Product")
            
            # Check if product is still available
            if not product.available:
                raise ValueError(f"Product {product.name} is no longer available")
            
            # Check if SKU has sufficient inventory
            if sku.inventory < cart_item.quantity:
                raise ValueError(
                    f"Insufficient inventory for {product.name} "
                    f"({sku.color}/{sku.size}). Only {sku.inventory} available."
                )
            
            # Calculate pricing at time of order (snapshot pricing)
            unit_price = product.get_final_price(sku)
            line_total = unit_price * cart_item.quantity
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                sku_id=sku.id,
                quantity=cart_item.quantity,
                unit_price=unit_price,
                line_total=line_total
            )
            
            db.session.add(order_item)
            
            # Decrement SKU inventory (reserve stock)
            sku.inventory -= cart_item.quantity
        
        # Calculate total for the order
        order.calculate_total()
        
        try:
            # Commit the order and all order items
            db.session.commit()
            
            # Clear the cart after successful order creation
            cart.clear()
            db.session.commit()
            
            return order
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to create order: {str(e)}")
    
    @staticmethod
    def attach_payment_record(order, amount, method, transaction_id=None):
        """
        Attach a payment record to an order after payment processing.
        
        Args:
            order (Order): Order to attach payment to
            amount (Decimal): Payment amount
            method (str): Payment method (e.g., "credit_card", "paypal")
            transaction_id (str, optional): External transaction ID from payment gateway
            
        Returns:
            PaymentRecord: The created payment record
        """
        # Validate that amount matches order total
        if amount != order.total_amount:
            raise ValueError(
                f"Payment amount {amount} does not match order total {order.total_amount}"
            )
        
        # Create payment record
        payment_record = PaymentRecord(
            order_id=order.id,
            amount=amount,
            method=method,
            transaction_id=transaction_id,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(payment_record)
        
        # Update order status to paid
        order.status = 'paid'
        order.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return payment_record
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to attach payment record: {str(e)}")
    
    @staticmethod
    def get_orders_for_customer(customer):
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
    def update_order_status(order_id, new_status):
        """
        Update the status of an order.
        
        Args:
            order_id (str): UUID of the order to update
            new_status (str): New status value (e.g., "pending", "paid", "shipped", "cancelled")
            
        Returns:
            Order: Updated order object, or None if not found
        """
        # Valid order statuses
        valid_statuses = ['pending', 'paid', 'processing', 'shipped', 'delivered', 'cancelled']
        
        if new_status not in valid_statuses:
            raise ValueError(
                f"Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}"
            )
        
        order = Order.query.get(order_id)
        
        if not order:
            return None
        
        # Update status and timestamp
        order.status = new_status
        order.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            return order
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update order status: {str(e)}")
