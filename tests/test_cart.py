"""
File: tests/test_cart.py
Description: Simple test to ensure Cart model and table exist.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 30, 2025
"""

def test_cart_creation(app):
    """
    This just checks:
    - Cart model can be imported
    - Cart table can be queried without error
    """
    from app.models.cart import Cart

    with app.app_context():
        carts = Cart.query.all()
        # We only care that this doesn't blow up and returns a list
        assert carts is not None
