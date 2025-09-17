from flask import Flask
from Config import Config
from .utils.database import db 

def create_app():
    app = Flask(__name__)

    # Load configs and 
    app.config.from_object(Config)
    db.init_app(app)

    # Register blueprints
    from pikenet.webapps.main import bp as main_bp
    app.register_blueprint(main_bp)

    # If you have more addons, register them here
    # from app.addons.blog import bp as blog_bp
    # app.register_blueprint(blog_bp)

    return app
