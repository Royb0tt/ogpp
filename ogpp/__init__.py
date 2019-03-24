from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .riot_api import RiotAPI
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

game_api = RiotAPI(app.config['RIOT_API_KEY'])

from ogpp import routes, models
