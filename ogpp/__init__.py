from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .riot_api import RiotAPI
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

if not app.config['RIOT_API_KEY']:
    print("API key not set. Get a key and set it in the console: $set RIOT_API_KEY=<your-key>")
else:
    print("You API key: %s" % app.config['RIOT_API_KEY'])

game_api = RiotAPI(app.config['RIOT_API_KEY'])

from ogpp import routes, models
