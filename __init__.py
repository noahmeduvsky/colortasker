# colortasker/__init__.py

from flask import Flask
from .config import Config
from .extensions import db, login_manager, csrf
from .controllers import auth_bp, main_bp
from .models import User
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate = Migrate(app, db)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    # User loader callback
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app
