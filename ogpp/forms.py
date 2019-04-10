from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email

from .game_consts import CHAMPIONS, QUEUE_TYPE


SUMMONER_OPTIONS = [(champ, champ.title()) for champ in CHAMPIONS.values()]
SUMMONER_OPTIONS.insert(0, (('all', 'All Champions')))

QUEUE_OPTIONS = [(choice, choice.title().replace('_', ' ')) for choice in QUEUE_TYPE.values()]
QUEUE_OPTIONS.insert(0, (('all', 'All Game Modes')))


class SummonerSearchForm(FlaskForm):
    summoner = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')


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


class SummonerSelectForm(FlaskForm):
    champions = SelectField(
        'Filter By Champion',
        choices=SUMMONER_OPTIONS,
        default='all'
    )

    queues = SelectField(
        'Filter By Queue',
        choices=QUEUE_OPTIONS,
        default='all'
    )
    submit = SubmitField('Filter')


class ContactForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired("Enter a name.")])
    email = StringField('Email', validators=[DataRequired("Email cannot be empty."), Email()])
    subject = StringField('Subject', validators=[DataRequired("Subject Cannot be empty.")])
    message = TextAreaField('Message', validators=[DataRequired("Message cannot be empty.")])
    submit = SubmitField('Send', validators=[DataRequired()])
