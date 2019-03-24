from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SummonerSearchForm(FlaskForm):
    summoner = StringField('', validators=[DataRequired()])
    submit = SubmitField('Search')
