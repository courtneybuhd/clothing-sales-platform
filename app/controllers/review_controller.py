"""
File: app/controllers/review_controller.py
Description: Review management controller for the Multi-Brand Clothing Sales Platform.
             Handles creation, updating, deletion, and retrieval of product reviews.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

from app import db
from app.models.user import Customer
from app.models.product import Product
from app.models.review import Review


class ReviewController:
    """
    Controller class for product review operations.
    All methods are static and can be called without instantiation.
    """
    
    @staticmethod
    def add_review(customer, product, rating, comment=None):
        """
        Add a new review for a product.
        
        Args:
            customer (Customer): Customer writing the review
            product (Product): Product being reviewed
            rating (int): Rating from 1 to 5
            comment (str, optional): Text comment for the review
            
        Returns:
            Review: The newly created review
        """
        # Validate rating is between 1 and 5
        if rating < 1 or rating > 5:
            raise ValueError("Rating must be between 1 and 5")
        
        # Check if customer has already reviewed this product
        existing_review = Review.query.filter_by(
            customer_id=customer.id,
            product_id=product.id
        ).first()
        
        if existing_review:
            raise ValueError("Customer has already reviewed this product")
        
        # Create new review
        review = Review(
            customer_id=customer.id,
            product_id=product.id,
            rating=rating,
            comment=comment
        )
        
        try:
            db.session.add(review)
            db.session.commit()
            return review
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to add review: {str(e)}")
    
    @staticmethod
    def update_review(review_id, rating=None, comment=None):
        """
        Update an existing review's rating and/or comment.
        
        Args:
            review_id (str): UUID of the review to update
            rating (int, optional): New rating (1-5)
            comment (str, optional): New comment text
            
        Returns:
            Review: Updated review object, or None if not found
        """
        review = Review.query.get(review_id)
        
        if not review:
            return None
        
        # Update rating if provided
        if rating is not None:
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
            review.rating = rating
        
        # Update comment if provided (even if empty string to clear it)
        if comment is not None:
            review.comment = comment
        
        try:
            db.session.commit()
            return review
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to update review: {str(e)}")
    
    @staticmethod
    def delete_review(review_id):
        """
        Delete a review.
        
        Args:
            review_id (str): UUID of the review to delete
            
        Returns:
            bool: True if deletion succeeded, False if review not found
        """
        review = Review.query.get(review_id)
        
        if not review:
            return False
        
        try:
            db.session.delete(review)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise Exception(f"Failed to delete review: {str(e)}")
    
    @staticmethod
    def get_reviews_for_product(product):
        """
        Retrieve all reviews for a specific product.
        
        Args:
            product (Product): Product whose reviews to retrieve
            
        Returns:
            list: List of Review objects, ordered by creation date (newest first)
        """
        reviews = Review.query.filter_by(product_id=product.id)\
                             .order_by(Review.created_at.desc())\
                             .all()
        return reviews
    
    @staticmethod
    def get_average_rating_for_product(product):
        """
        Calculate the average rating for a product.
        
        Args:
            product (Product): Product to calculate average rating for
            
        Returns:
            float: Average rating (0.0 to 5.0), or 0.0 if no reviews exist
        """
        reviews = Review.query.filter_by(product_id=product.id).all()
        
        # Return 0.0 if no reviews
        if not reviews or len(reviews) == 0:
            return 0.0
        
        # Calculate average rating
        total_rating = sum(review.rating for review in reviews)
        average = total_rating / len(reviews)
        
        # Round to 2 decimal places
        return round(average, 2)
