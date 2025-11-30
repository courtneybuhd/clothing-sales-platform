"""
File: tests/test_auth.py
Description: Basic auth tests for registration.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 30, 2025
"""

def test_register_customer(client):
    """
    Simple test: can we POST to the customer registration endpoint
    without the app crashing?
    """
    response = client.post(
        "/auth/register/customer",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    # 200 means the route exists, form processed, and no exception exploded.
    assert response.status_code == 200
