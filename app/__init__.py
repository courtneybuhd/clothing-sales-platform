"""
File: app/__init__.py
Description: Flask application factory and configuration
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: [Update this date]
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """
    Flask application factory function.
    Creates and configures the Flask app instance.
    """
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///clothing_platform.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # Redirect to login if not authenticated

    # ---- TEMPORARY: we'll register real blueprints later ----
    # For now, we will only register a simple 'main' blueprint so something works.
    from app.routes.main import main_bp
    app.register_blueprint(main_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    """Required by Flask-Login to reload user from session"""
    from app.models.user import User
    # For now, we'll stub this until we create the User model
    # Return None so login-dependent stuff is disabled
    return None
