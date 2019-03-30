import logging
from flask import Flask
from slugify import Slugify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .riot_api import RiotAPI
from config import Config


slug = Slugify(to_lower=True)
slug.separator = ''

if not Config.RIOT_API_KEY:
    print("API key not set. Get a key and set it in the console: $set RIOT_API_KEY=<your-key>")
else:
    print("You API key: %s" % Config.RIOT_API_KEY)

game_api = RiotAPI(Config.RIOT_API_KEY)

db = SQLAlchemy()
migrate = Migrate()


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    db.init_app(app)
    migrate.init_app(app)
    if app.config['LOG_TO_STDOUT']:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)

    from ogpp import routes
    app.register_blueprint(routes.bp)
    app.add_url_rule('/', endpoint='summoner.index')

    return app


# from ogpp import routes, models
