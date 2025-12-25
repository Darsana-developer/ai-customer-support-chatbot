from flask import Flask
from config import Config
import os

def create_app():
    """Create and configure Flask application"""
    # Set static folder path relative to project root
    static_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(Config)
    
    # Register blueprints
    from app.routes import bp
    app.register_blueprint(bp)
    
    return app
