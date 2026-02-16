"""
Main entry point for the Civic Complaint Tracking System
Run this file to start the Flask development server
"""
from app import create_app
import os

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5000))
    
    # Run the application
    print("=" * 50)
    print("Civic Complaint Tracking System")
    print("=" * 50)
    print(f"Server starting on http://localhost:{port}")
    print("\nDefault Login Credentials:")
    print("  Admin:   admin1 / password123")
    print("  Officer: officer1 / password123")
    print("  Citizen: citizen1 / password123")
    print("=" * 50)
    print("\nPress CTRL+C to quit")
    print()
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
