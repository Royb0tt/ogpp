'''helper functions to export data queried from the database
   and prepare them to be rendered onto webpage

   TODO: Finish implementing and test out most_played_champs() function
'''

from types import SimpleNamespace
from flask import url_for
from .db_helpers import grab_summoner, get_match_stats, populate_match_history
from .models import Match, MatchByReference
from .game_consts import QUEUE_TYPE
from . import app


# blacklist certain properties in the object's __dict__
BLACKLIST = ['_sa_instace_state']


def generate_summoner_page_context(summoner_name, page):
    summoner = grab_summoner(summoner_name)
    if summoner.match_history.count() < 1:
        populate_match_history(summoner)

    match_refs = summoner.match_history.order_by(
        MatchByReference.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)

    matches = get_match_stats(match_refs, page)
    matches = make_matches_exportable(matches, summoner.name)

    title = "Profile Page of %s" % summoner.name

    page_items = SimpleNamespace()

    page_items.summoner = summoner
    page_items.matches = matches
    # page_items.next_url = next_url
    # page_items.prev_url = prev_url
    page_items.page_urls = paginate(match_refs, 'summoner', **{'name': summoner_name})
    page_items.title = title

    return page_items


def paginate(paginatable, page_context, **kwargs):
    '''
    generate a pagination sequence to be rendered on webpage contexts
    that require it.

    page_context should be an html file, page is the current page.
    paginatable should be a pagination object generated from sqlalchemy.
    kwargs are extra keywords needed for the page_context.
    '''

    # preserve_kwargs = **kwargs

    paginate_list = []

    k = paginatable.page - 2  # lower limit
    page_upper_limit = paginatable.page + 2
    max_pages = paginatable.pages

    while k <= page_upper_limit:
        if k < 1:  # skip item
            k += 1
            # make sure we get at least 5 pagination items
            page_upper_limit += 1
            continue
        elif k > max_pages:
            break
        elif k == paginatable.page:
            page = (k, 'CURRENT')
            paginate_list.append(page)
            k += 1
            continue

        page = (k, url_for(page_context, page=k, **kwargs))
        paginate_list.append(page)
        k += 1

    pages = SimpleNamespace()
    pages.first = url_for(page_context, page=1, **kwargs)
    pages.last = url_for(page_context, page=max_pages, **kwargs)
    pages.page_list = paginate_list

    return pages


def make_matches_exportable(matches, summoner_name):
    out = []

    for match in matches:
        m = SimpleNamespace(**{k: v for k, v in match.__dict__.items() if k not in BLACKLIST})
        # get properties that __dict__ didn't pick up
        m.players = match.players
        m.date = match.date
        # get team sides
        m.blue_side = get_team(m.players, side_id=100)
        m.red_side = get_team(m.players, side_id=200)
<<<<<<< HEAD
        m.queue_type = QUEUE_TYPE[match.game_mode]
=======

        m.queue_type = match.queue_type
>>>>>>> nav_feature

        m.win = is_win_or_loss(match, summoner_name)

        out.append(m)
    return out


def get_team(players, side_id):
    '''function that sorts which players belonged on what side'''
    return [p for p in players if p.team_id == side_id]


def is_win_or_loss(match, summoner_name):
    player = match.participants.filter_by(name=summoner_name).first()
    if player.win == 0:
        return 'Defeat'
    else:
        return 'Victory'


def most_played_champs(summoner):
    games = summoner.ranked_games
    champions_played = set(match.champion_played for match in games)
    ranked_champions = []

    for champ in champions_played:
        all_played_matches = [match for match in games if match.champion_played == champ]
        total_played = len(all_played_matches)

        total_avg_kdas = 0
        wins = 0

        for match in all_played_matches:
            match = Match.query.filter_by(match_id=match.match_id)
            player_instance = match.participants.filter_by(
                name=summoner.name).first()
            total_avg_kdas += player_instance.avg_kda

            if player_instance.win:
                wins += 1

        effective_kda = total_avg_kdas / total_played
        win_rate = wins / total_played

        exportable_chamion = make_exportable_top_champ(
            champ,
            win_rate,
            effective_kda,
            total_played
        )

        ranked_champions.append(exportable_chamion)

    ranked_champions.sort(key=lambda c: c.total_played)

    # get only the top 5 at most
    return ranked_champions[:5]


def make_exportable_top_champ(name, win_rate, avg_kda, amt_played):
    champ = SimpleNamespace()
    champ.name = name
    champ.win_rate = win_rate
    champ.avg_kda = avg_kda
    champ.total_played = amt_played

    return champ
