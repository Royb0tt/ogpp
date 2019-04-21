import logging

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

from config import Config


db = SQLAlchemy()
migrate = Migrate()
mail = Mail()
login_manager = LoginManager
login_manager.login_view = 'auth.login'


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    # error: missing one positional arguemnt(app)
    # login_manager.init_app(app)

    if app.config['LOG_TO_STDOUT']:
        # hosting via heroku requires this config to be toggled
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(stream_handler)

    from . import routes
    app.register_blueprint(routes.error_bp)
    app.register_blueprint(routes.index_bp)
    app.register_blueprint(routes.summoner_bp)
    app.register_blueprint(routes.leaderboard_bp)

    return app
