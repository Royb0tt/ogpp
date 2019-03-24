'''
TODO: make a summoner champion mastery page
'''

from flask import render_template, request, url_for, redirect
from .db_helpers import update_summoner_page
from .export_helpers import generate_summoner_page_context
from .forms import SummonerSearchForm
from . import app


LANDING_TITLE = 'ogpp: The Old Games & Player Profiles League Database'


@app.route('/summoner/<name>', methods=['GET', 'POST'])
def summoner(name):
    form = SummonerSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('summoner', name=form.summoner.data))

    page = request.args.get('page', 1, type=int)

    page_items = generate_summoner_page_context(name, page)

    return render_template('summoner.html',
                           form=form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title)


@app.route('/summoner/<summoner_name>/refresh')
def refresh(summoner_name):
    update_summoner_page(summoner_name)
    return redirect(url_for('summoner', name=summoner_name))


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def index():
    form = SummonerSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('summoner', name=form.summoner.data))

    return render_template('index.html', title=LANDING_TITLE, form=form, index=True)
