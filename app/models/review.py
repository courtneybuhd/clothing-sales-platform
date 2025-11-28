"""
File: app/models/review.py
Description: Review entity model for the Multi-Brand Clothing Sales Platform.
             Allows customers to rate and comment on products they have purchased.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

import uuid
from datetime import datetime
from app import db


class Review(db.Model):
    """
    Review entity for customer product ratings and comments.
    Customers can leave reviews with ratings (1-5) and optional text comments.
    """
    __tablename__ = 'reviews'
    
    # Primary key as UUID string
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to customer (users table)
    customer_id = db.Column(db.String(36), db.ForeignKey('users.id'), 
                           nullable=False, index=True)
    
    # Foreign key to product
    product_id = db.Column(db.String(36), db.ForeignKey('products.id'), 
                          nullable=False, index=True)
    
    # Rating from 1 to 5
    rating = db.Column(db.Integer, nullable=False)
    
    # Optional text comment
    comment = db.Column(db.Text)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to customer
    customer = db.relationship('Customer', back_populates='reviews')
    
    # Relationship to product
    product = db.relationship('Product', back_populates='reviews')
    
    def __repr__(self):
        return f'<Review {self.id} - Product {self.product_id} - Rating: {self.rating}/5>'
