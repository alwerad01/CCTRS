"""
Flask application factory for Civic Complaint Tracking System
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app(config_name='default'):
    """
    Application factory pattern
    Creates and configures the Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Register blueprints
    from app.routes import auth, citizen, officer, admin, supervisor, moderator, auditor
    app.register_blueprint(auth.bp)
    app.register_blueprint(citizen.bp)
    app.register_blueprint(officer.bp)
    app.register_blueprint(admin.bp)
    app.register_blueprint(supervisor.bp)
    app.register_blueprint(moderator.bp)
    app.register_blueprint(auditor.bp)
    
    # Register main blueprint
    from app.routes import main
    app.register_blueprint(main.bp)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Home route

    
    return app

def register_error_handlers(app):
    """Register custom error handlers"""
    
    @app.errorhandler(403)
    def forbidden(e):
        from flask import render_template
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(404)
    def page_not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500
