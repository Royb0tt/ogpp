'''TODO: Handle adding summoner form to views better'''

from functools import wraps

from flask import Blueprint, redirect, url_for, request, render_template

from ..forms import SummonerSearchForm, SummonerSelectForm
from ..helpers import generate_summoner_page_context, get_champion_masteries
from ..helpers import update_summoner_page
from ..helpers import slug

summoner_bp = Blueprint('summoner', __name__, url_prefix='/summoner')


def make_bp_endpoint(bp, view):
    '''
    give the canon name of the view with the related blueprint

    bp     -> flask blueprint object
    view   -> view function
    return -> str
    '''
    return '.'.join((bp.name, view.__name__))


def slug_summoner_url(view):
    '''slug user names so they look nice on summoner view pages'''
    @wraps(view)
    def slugger(name, **kwargs):
        view_name = make_bp_endpoint(summoner_bp, view)
        if ' ' in name:
            slugged = slug(name)
            return redirect(url_for(view_name, name=slugged, **kwargs))
        page = view(name, **kwargs)
        return page

    return slugger


def view_with_search_bar(view):
    @wraps(view)
    def form_provider(*pargs, **kwargs):
        summoner_form = SummonerSearchForm()
        if summoner_form.validate_on_submit():
            summoner_view = make_bp_endpoint(summoner_bp, summoner)
            return redirect(url_for(summoner_view, name=summoner_form.summoner.data))
        page = view(*pargs, **kwargs, summoner_form=summoner_form)
        return page
    return form_provider


@summoner_bp.route('/<name>', methods=['GET', 'POST'])
@slug_summoner_url
@view_with_search_bar
def summoner(name, summoner_form):
    page = request.args.get('page', 1, type=int)
    queue_type = request.args.get('queue', 'all', type=str)
    champion = request.args.get('champion', 'all', type=str)
    select_form = SummonerSelectForm(queues=queue_type, champions=champion)
    if select_form.validate_on_submit():
        queue_type = select_form.queues.data
        champion = select_form.champions.data
        return redirect(url_for('summoner.summoner',
                                name=name, queue=queue_type,
                                champion=champion))

    page_items = generate_summoner_page_context(name, page, champion, queue_type)

    return render_template('summoner.html',
                           summoner_form=summoner_form,
                           select_form=select_form,
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

    return render_template('masteries.html', masteries=masteries, summoner_form=summoner_form)


@summoner_bp.route('/<name>/refresh')
@slug_summoner_url
def refresh(name):
    update_summoner_page(name)
    return redirect(url_for('summoner.summoner', name=name))
