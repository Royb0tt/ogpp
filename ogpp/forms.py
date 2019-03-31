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


class LeaderboardSelectForm(FlaskForm):
    queues = SelectField(
        'Filter By Queue',
        choices=[
            (choice, choice)
            for choice in
            ('RANKED_SOLO_5x5', 'RANKED_FLEX_SR', 'RANKED_FLEX_TT')
        ]
    )

    groups = SelectField(
        'Filter By Group',
        choices=[
            (group, group.title())
            for group in
            ('masters', 'grandmasters', 'challengers')
        ]
    )

    submit = SubmitField('Filter')


SUMMONER_OPTIONS = [(champ, champ.title()) for champ in CHAMPIONS.values()]
SUMMONER_OPTIONS.append(('all', 'All champions'))


# To be used when refactoring the summoner view
class SummonerSelectForm(FlaskForm):
    champions = SelectField(
        'Filter By Champion',
        choices=SUMMONER_OPTIONS,
        default='all'
    )
    queues = ''
    submit = SubmitField('Filter')
