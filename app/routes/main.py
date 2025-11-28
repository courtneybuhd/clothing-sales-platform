"""
File: app/routes/main.py
Description: Main routes (homepage and simple test page)
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: November 27, 2025
"""

from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # For now, just return plain text or a very simple template
    return "Multi-Brand Clothing Platform is running! ❄️🛒"
