'''
TODO: create a stats page displaying w/l for ranked & normal
TODO: create a leaderboards page
TODO: create a page to pick a random summoner from the database
TODO: create filtered tabs on summoner page to distinguish different queue modes
      ensure to use the api's queue_type param in order to create the full list
TODO: finish restructuring app
'''
from functools import wraps
import string

from flask import render_template, request, url_for, redirect, Blueprint
from .db_helpers import update_summoner_page
from .export_helpers import generate_summoner_page_context, get_champion_masteries, get_leaderboard_data
from .forms import SummonerSearchForm, ChampionSelectForm, LeaderboardSelectForm
from . import slug


LANDING_TITLE = 'ogpp: The Old Games & Player Profiles League Database'
VALID_ASCII = string.printable[:62]

summoner_bp = Blueprint('summoner', __name__, url_prefix='/summoner')
index_bp = Blueprint('home', __name__)
leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/leaderboard')


def make_bp_endpoint(view):
    '''
    give the canon name of the view with the related blueprint

    view -> view function
    return -> str
    '''
    return '.'.join((summoner_bp.name, view.__name__))


def slug_summoner_url(summoner_view):
    '''slug user input to remove whitespace and only valid chararcters'''
    @wraps(summoner_view)
    def slugger(name, **kwargs):
        full_view_name = make_bp_endpoint(summoner_view)
        if ' ' in name or any(c not in VALID_ASCII for c in name):
            slugged = slug(name)
            return redirect(url_for(full_view_name, name=slugged, **kwargs))
        page = summoner_view(name, **kwargs)
        return page

    return slugger


def view_with_search_bar(view):
    @wraps(view)
    def form_provider(*pargs, **kwargs):
        summoner_form = SummonerSearchForm()
        summoner_view = make_bp_endpoint(summoner)
        if summoner_form.validate_on_submit():
            return redirect(url_for(summoner_view, name=summoner_form.summoner.data))
        page = view(*pargs, **kwargs, summoner_form=summoner_form)
        return page
    return form_provider


@summoner_bp.route('/test/<name>', methods=['GET', 'POST'])
@slug_summoner_url
@view_with_search_bar
def test(name, summoner_form):
    page = request.args.get('page', 1, type=int)
    # instead of using multiple similar functioning views I can probably just generate
    # all the specific data I need grabbing optional args from the url
    #
    # select_form = SummonerSelectForm()
    # queue_type = request.args.get('queue', 'all', type=str)
    # champion = request.args.get('champion', 'all', type=str)
    # if select_form.validate_on_submit():
    #       queue_type = select_form.queues.data
    #       champion = select_form.champion.data
    #       return redirect(url_for('summoner.summoner', ...))

    # summoner_form = SummonerSearchForm()
    champ_form = ChampionSelectForm()
    # if summoner_form.validate_on_submit():
    #    return redirect(url_for('summoner', name=summoner_form.summoner.data))
    # elif champ_form.validate_on_submit():
    #    pass

    page_items = generate_summoner_page_context(name, page, 'summoner.test')

    return render_template('test.html',
                           form=summoner_form,
                           champ_form=champ_form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title,
                           ranked_stats=page_items.ranked_stats)


@summoner_bp.route('/<name>', methods=['GET', 'POST'])
@slug_summoner_url
@view_with_search_bar
def summoner(name, summoner_form):
    page = request.args.get('page', 1, type=int)

    page_items = generate_summoner_page_context(name, page, 'summoner.summoner')

    return render_template('summoner.html',
                           form=summoner_form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title,
                           ranked_stats=page_items.ranked_stats)


@summoner_bp.route('/<name>/ranked_games', methods=['GET', 'POST'])
@slug_summoner_url
@view_with_search_bar
def ranked_games(name, summoner_form):
    page = request.args.get('page', 1, type=int)

    page_items = generate_summoner_page_context(name, page, 'summoner.ranked_games')

    return render_template('summoner.html',
                           form=summoner_form,
                           summoner=page_items.summoner,
                           matches=page_items.matches,
                           page_urls=page_items.page_urls,
                           title=page_items.title,
                           ranked_stats=page_items.ranked_stats)


@summoner_bp.route('/<name>/masteries', methods=['GET', 'POST'])
@slug_summoner_url
@view_with_search_bar
def masteries(name, summoner_form):

    masteries = get_champion_masteries(name)

    return render_template('masteries.html', masteries=masteries, form=summoner_form)


@summoner_bp.route('/<name>/refresh')
@slug_summoner_url
def refresh(name):
    update_summoner_page(name)
    return redirect(url_for('summoner.summoner', name=name))


@leaderboard_bp.route('/', methods=['GET', 'POST'])
@view_with_search_bar
def leaderboard(summoner_form):
    queue_type = request.args.get('queue', 'RANKED_SOLO_5x5', type=str)
    group_type = request.args.get('group', 'masters', type=str)
    select_form = LeaderboardSelectForm()
    if select_form.validate_on_submit():
        return redirect(url_for('leaderboard.leaderboard',
                                group=select_form.groups.data,
                                queue=select_form.queues.data))

    leaderboard_data = get_leaderboard_data(group_type, queue_type)

    return render_template('leaderboard.html', data=leaderboard_data,
                           form=summoner_form, select_form=select_form)


@index_bp.route('/', methods=['GET', 'POST'])
@index_bp.route('/home', methods=['GET', 'POST'])
def index():
    form = SummonerSearchForm()
    if form.validate_on_submit():
        return redirect(url_for('summoner.summoner', name=form.summoner.data))

    return render_template('index.html', title=LANDING_TITLE, form=form, index=True)
