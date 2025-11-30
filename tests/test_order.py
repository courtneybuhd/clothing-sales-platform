"""
File: tests/test_order.py
Description: Simple test to ensure Order model and table exist.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 30, 2025
"""

def test_order_model_exists(app):
    """
    Checks that:
    - Order model can be imported
    - Orders table can be queried
    """
    from app.models.order import Order

    with app.app_context():
        orders = Order.query.all()
        assert orders is not None
