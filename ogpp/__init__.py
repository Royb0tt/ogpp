import logging
import string
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from slugify import Slugify, slugify_unicode

from .riot_api import RiotAPI
from config import Config

VALID_ASCII = string.printable[62:]


class SlugAdapter:
    def __init__(self):
        self.slug = Slugify(to_lower=True)
        self.slug.separator = ''

    def __call__(self, string):
        if any(character not in VALID_ASCII for character in string):
            return slugify_unicode(string).replace('-', '').lower()
        else:
            return self.slug(string)

    def __repr__(self):
        return "SlugAdapter of %r" % self.slug


slug = SlugAdapter()


if os.environ.get('FLASK_ENV') == 'development':
    if not Config.RIOT_API_KEY:
        print("API key not set. Get a key and set it in the console: $set RIOT_API_KEY=<your-key>")
    else:
        print("You API key: %s" % Config.RIOT_API_KEY)

    print('Your secret key: %r' % Config.SECRET_KEY)

game_api = RiotAPI(Config.RIOT_API_KEY)

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

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
