'''
TODO: make a summoner champion mastery page
TODO: create a stats page displaying w/l for ranked & normal
TODO: create a leaderboards page
TODO: create a page to pick a random summoner from the database
TODO: create filtered tabs on summoner page to distinguish different queue modes
      ensure to use the api's queue_type param in order to create the full list
'''

from flask import render_template, request, url_for, redirect
from .db_helpers import update_summoner_page
from .export_helpers import generate_summoner_page_context, get_champion_masteries
from .forms import SummonerSearchForm, ChampionSelectForm
from . import app


LANDING_TITLE = 'ogpp: The Old Games & Player Profiles League Database'


@app.route('/test/<name>', methods=['GET', 'POST'])
def test(name):
    page = request.args.get('page', 1, type=int)

    if ' ' in name:
        name = name.replace(' ', '')
        return redirect(url_for('summoner', name=name))

    summoner_form = SummonerSearchForm()
    champ_form = ChampionSelectForm()
    if summoner_form.validate_on_submit():
        return redirect(url_for('summoner', name=summoner_form.summoner.data))
    elif champ_form.validate_on_submit():
        pass

    page_items = generate_summoner_page_context(name, page, 'test')

    return render_template('test.html',
                           form=summoner_form,
                           champ_form=champ_form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title,
                           ranked_champs=page_items.ranked_champs)


@app.route('/summoner/<name>', methods=['GET', 'POST'])
def summoner(name):
    page = request.args.get('page', 1, type=int)

    if ' ' in name:
        name = name.replace(' ', '')
        return redirect(url_for('summoner', name=name))

    form = SummonerSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('summoner', name=form.summoner.data))

    page_items = generate_summoner_page_context(name, page, 'summoner')

    return render_template('summoner.html',
                           form=form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title,
                           ranked_champs=page_items.ranked_champs)


@app.route('/summoner/<name>/ranked_games', methods=['GET', 'POST'])
def ranked_games(name):
    page = request.args.get('page', 1, type=int)

    if ' ' in name:
        name = name.replace(' ', '')
        return redirect(url_for('ranked_games', name=name))

    form = SummonerSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('summoner', name=form.summoner.data))

    page_items = generate_summoner_page_context(name, page, 'ranked_games')

    return render_template('summoner.html',
                           form=form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title,
                           ranked_champs=page_items.ranked_champs)


@app.route('/summoner/<name>/masteries', methods=['GET', 'POST'])
def masteries(name):
    if ' ' in name:
        name = name.replace(' ', '')
        return redirect(url_for('masteries', name=name))

    form = SummonerSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('summoner', name=form.summoner.data))

    masteries = get_champion_masteries(name)

    return render_template('masteries.html', masteries=masteries, form=form)


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
