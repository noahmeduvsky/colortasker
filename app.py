from flask import Flask
from extensions import db, login_manager, csrf
from config import Config
from models import user, folder, task
from controllers.auth import auth_bp
from controllers.main import main_bp
from controllers.errors import errors_bp
from logging_config import setup_logging
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
    app.register_blueprint(errors_bp)

    # Setup logging
    if not app.debug and not app.testing:
        setup_logging(app)

    # Set up user loader
    @login_manager.user_loader
    def load_user(user_id):
        return user.User.query.get(int(user_id))

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
