"""
File: run.py
Description: Application entry point
Team: Xavier Buentello, Parmida Keymanesh, Courtney Buttler, David Rosas
Date: [Update this date]
"""

from app import create_app, db

app = create_app()

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
        print("Database initialized!")

    # Run the Flask development server
    app.run(debug=True, host='0.0.0.0', port=5000)
