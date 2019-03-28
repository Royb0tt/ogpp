'''
TODO: make a summoner champion mastery page
TODO: create a stats page displaying w/l for ranked & normal
TODO: create a leaderboards page
TODO: create a page to pick a random summoner from the database
TODO: create filtered tabs on summoner page to distinguish different queue modes
      ensure to use the api's queue_type param in order to create the full list
'''
from functools import wraps
import string

from flask import render_template, request, url_for, redirect
from .db_helpers import update_summoner_page
from .export_helpers import generate_summoner_page_context, get_champion_masteries
from .forms import SummonerSearchForm, ChampionSelectForm
from . import app, slug


LANDING_TITLE = 'ogpp: The Old Games & Player Profiles League Database'
VALID_ASCII = string.printable[:62]


def slug_summoner_url(summoner_view):
    @wraps(summoner_view)
    def slugger(name, **kwargs):
        if ' ' in name or any(c not in VALID_ASCII for c in name):
            slugged = slug(name)
            return redirect(url_for(summoner_view.__name__, name=slugged, **kwargs))
        page = summoner_view(name)
        return page

    return slugger


def view_with_search_bar(view):
    @wraps(view)
    def form_provider(*pargs, **kwargs):
        summoner_form = SummonerSearchForm()
        if summoner_form.validate_on_submit():
            return redirect(url_for(view.__name__, name=summoner_form.summoner.data))
        page = view(*pargs, **kwargs, summoner_form=summoner_form)
        return page
    return form_provider


@app.route('/test/<name>', methods=['GET', 'POST'])
@slug_summoner_url
@view_with_search_bar
def test(name, summoner_form):
    page = request.args.get('page', 1, type=int)

    # summoner_form = SummonerSearchForm()
    champ_form = ChampionSelectForm()
    # if summoner_form.validate_on_submit():
    #    return redirect(url_for('summoner', name=summoner_form.summoner.data))
    # elif champ_form.validate_on_submit():
    #    pass

    page_items = generate_summoner_page_context(name, page, 'test')

    return render_template('test.html',
                           form=summoner_form,
                           champ_form=champ_form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title,
                           ranked_stats=page_items.ranked_stats)


@app.route('/summoner/<name>', methods=['GET', 'POST'])
@slug_summoner_url
@view_with_search_bar
def summoner(name, summoner_form):
    page = request.args.get('page', 1, type=int)

    page_items = generate_summoner_page_context(name, page, 'summoner')

    return render_template('summoner.html',
                           form=summoner_form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title,
                           ranked_stats=page_items.ranked_stats)


@app.route('/summoner/<name>/ranked_games', methods=['GET', 'POST'])
@slug_summoner_url
@view_with_search_bar
def ranked_games(name, summoner_form):
    page = request.args.get('page', 1, type=int)

    page_items = generate_summoner_page_context(name, page, 'ranked_games')

    return render_template('summoner.html',
                           form=summoner_form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title,
                           ranked_stats=page_items.ranked_stats)


@app.route('/summoner/<name>/masteries', methods=['GET', 'POST'])
@slug_summoner_url
@view_with_search_bar
def masteries(name, summoner_form):

    masteries = get_champion_masteries(name)

    return render_template('masteries.html', masteries=masteries, form=summoner_form)


@app.route('/summoner/<summoner_name>/refresh')
@slug_summoner_url
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
