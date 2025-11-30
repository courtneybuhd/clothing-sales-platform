"""
File: tests/conftest.py
Description: pytest configuration and fixtures for the clothing platform.
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 30, 2025
"""

import pytest
from app import create_app


@pytest.fixture
def app():
    """
    Create a Flask app instance for tests.
    """
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Flask test client for making HTTP requests in tests."""
    return app.test_client()
