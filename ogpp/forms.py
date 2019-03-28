from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired

from .game_consts import CHAMPIONS


class SummonerSearchForm(FlaskForm):
    summoner = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')


class ChampionSelectForm(FlaskForm):
    champions = SelectField('Filter By Champion',
                            choices=[(champ, champ.title()) for champ in CHAMPIONS.values()])
    submit = SubmitField('Filter')
