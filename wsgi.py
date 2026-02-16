"""
WSGI entry point for production deployment
This file is used by gunicorn and other WSGI servers
"""
from app import create_app
import os

# Create the Flask application instance
# Use production config in production environment
config_name = os.environ.get('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    # This allows running the app directly for testing
    # In production, gunicorn will use the 'app' object above
    app.run()
