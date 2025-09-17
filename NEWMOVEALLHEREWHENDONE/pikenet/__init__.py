from flask import Flask
from Config import Config
from .utils.database import db  # Add other extensions like login_manager here if needed

def create_app():
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    # login_manager.init_app(app)  # If you're using it

    # Register blueprints
    from pikenet.webapps.main import bp as main_bp
    app.register_blueprint(main_bp)

    # If you have more addons, register them here
    # from app.addons.blog import bp as blog_bp
    # app.register_blueprint(blog_bp)

    return app
