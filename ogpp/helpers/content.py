'''helper functions to export data queried from the database
   and prepare them to be rendered onto webpage
'''

from types import SimpleNamespace

from flask import url_for, current_app

from .storage import grab_summoner, get_match_stats
from ..models import Match, ByReferenceMatch
from ..game import CHAMPIONS, _TEAMS
from ..game import _QUEUE_TYPE as REVERSE_QUEUE_LOOKUP
from .. import game_api

# blacklist certain properties in the model object's __dict__
BLACKLIST = ['_sa_instace_state']


def generate_summoner_page_context(summoner_name, page, champion, queue):
    '''
    page is the current counter in a pagination sequence
    champion & queue are args obtained as url query keywords(default: 'all')
    '''
    view = 'summoner.summoner'
    paginate_kwargs = {'name': summoner_name}

    summoner = grab_summoner(summoner_name)

    match_refs = summoner.match_history
    if queue != 'all':
        match_refs = summoner.match_history.filter_by(game_mode=REVERSE_QUEUE_LOOKUP[queue])
        paginate_kwargs['queue'] = queue
    if champion != 'all':
        match_refs = match_refs.filter_by(champion_played=champion)
        paginate_kwargs['champion'] = champion

    match_refs = match_refs.order_by(
        ByReferenceMatch.timestamp.desc()
    ).paginate(
        page, current_app.config['POSTS_PER_PAGE']
    )

    matches = get_match_stats(match_refs, page)
    matches = make_matches_exportable(matches, summoner.name)

    title = "Profile Page of %s" % summoner.name

    page_items = SimpleNamespace()

    page_items.ranked_stats = get_ranked_stats(summoner)
    page_items.summoner = make_summoner_exportable(summoner)
    page_items.matches = matches
    page_items.page_urls = make_paginate(match_refs, view, **paginate_kwargs)
    page_items.title = title

    return page_items


def make_paginate(paginatable, view, **kwargs):
    '''
    generate a pagination sequence to be rendered on webpage contexts
    that require it.

    args
    view -> str
        : the string representation of the view name used in
        : flask's url_for() function i.e. url_for(<view_name>).
    page -> int
        : the current page of the paginatable's sequence.
    paginatable -> SQLAlchemy pagination object
        : a pagination object generated from sqlalchemy.
    kwargs -> dict
        : extra keywords needed for the page context.
    '''
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

        page = (k, url_for(view, page=k, **kwargs))
        paginate_list.append(page)
        k += 1

    prev = url_for(view, page=paginatable.prev_num, **kwargs) \
        if paginatable.has_prev else None
    nxt = url_for(view, page=paginatable.next_num, **kwargs) \
        if paginatable.has_next else None

    pages = SimpleNamespace()
    pages.first = url_for(view, page=1, **kwargs)
    pages.last = url_for(view, page=max_pages, **kwargs)
    pages.prev = prev
    pages.next = nxt
    pages.page_list = paginate_list

    return pages


def make_summoner_exportable(s):
    summoner = SimpleNamespace()
    summoner.name = s.name
    summoner.profile_icon = 'img/profileicon/{}.png'.format(s.profile_icon)
    summoner.level = s.level
    summoner.rank = s.rank
    if 'unranked' in summoner.rank or summoner.rank is None:
        summoner.points = ''
        summoner.win_loss = ''
        summoner.win_ratio = ''
    else:
        summoner.points = '{}LP'.format(s.points)
        summoner.win_loss = '{}W/{}L'.format(s.wins, s.losses)
        summoner.win_ratio = '{}% Winrate'.format(s.ranked_win_ratio)

    return summoner


def make_matches_exportable(matches, summoner_name):
    out = []

    for match in matches:
        m = SimpleNamespace(**{k: v for k, v in match.__dict__.items() if k not in BLACKLIST})
        # get properties that __dict__ didn't pick up
        m.players = match.players
        m.date = match.date
        # get team sides
        m.blue_side = get_team(m.players, side_id=_TEAMS['blue'])
        m.red_side = get_team(m.players, side_id=_TEAMS['red'])
        m.queue_type = match.queue_type

        m.win = is_win_or_loss(match, summoner_name)

        out.append(m)
    return out


def make_exportable_top_champ(champ_name, win_rate, avg_kda, amt_played):
    num_fmt = '{:.2f}'
    champ = SimpleNamespace()
    champ.name = champ_name
    champ.win_rate = num_fmt.format(win_rate * 100) + '% Winrate'
    champ.avg_kda = num_fmt.format(avg_kda)
    champ.total_played = amt_played
    champ.img = 'img/champion/{}.png'.format(champ_name)

    return champ


def get_team(players, side_id):
    '''function that sorts which players belonged on what side'''
    return [p for p in players if p.team_id == side_id]


def is_win_or_loss(match, summoner_name):
    player = match.participants.filter_by(name=summoner_name).first()
    if not player.win:
        return 'Defeat'
    else:
        return 'Victory'


def get_ranked_stats(summoner):
    '''
    get a summoner's 5 most played ranked champions, if any.
    returns data to be displayed on the summoner page side bar.
    '''
    games = summoner.ranked_games
    champions_played = set(match.champion_played for match in games)
    ranked_champions = []

    def match_query(m):
        return Match.query.filter_by(match_id=m.match_id).first()

    total_wins = 0
    games_total = 0

    for champ in champions_played:
        # match references
        all_played_matches = [
            match
            for match in games
            if match.champion_played == champ
        ]
        # query-able rows from Match table
        queried_matches = [
            match_query(match)
            for match in all_played_matches
            if match_query(match) is not None
        ]

        total_played = len(queried_matches)

        total_avg_kdas = 0
        wins = 0

        for match in queried_matches:
            player_instance = match.participants.filter_by(
                name=summoner.name).first()
            total_avg_kdas += player_instance.avg_kda

            if player_instance.win:
                total_wins += 1
                wins += 1

        try:
            effective_kda = total_avg_kdas / total_played
        except ZeroDivisionError:
            effective_kda = total_avg_kdas
        try:
            win_rate = wins / total_played
        except ZeroDivisionError:
            win_rate = 0

        exportable_champion = make_exportable_top_champ(
            champ,
            win_rate,
            effective_kda,
            total_played
        )

        ranked_champions.append(exportable_champion)

        games_total += total_played

    ranked_champions.sort(key=lambda c: c.total_played)
    ranked_champions.reverse()

    ranked_items = SimpleNamespace()
    # get on only the top 5 at most
    ranked_items.champions = ranked_champions[:5]
    ranked_items.win_loss = '{}W/{}L'.format(total_wins, games_total - total_wins)
    try:
        ranked_items.win_ratio = '{}% Winrate'.format(int((total_wins / games_total) * 100))
    except ZeroDivisionError:
        ranked_items.win_ratio = ''

    return ranked_items


def get_champion_masteries(summoner_name):
    summoner = grab_summoner(summoner_name)
    masteries = game_api.get_summoner_mastery(summoner.summoner_id)

    out = []

    for mastery in masteries:
        m = SimpleNamespace()
        m.champion_level = mastery['championLevel']
        m.champion_name = CHAMPIONS[mastery['championId']]
        m.points = mastery['championPoints']
        m.img = 'img/champion/{}.png'.format(CHAMPIONS[mastery['championId']])
        m.last_played = last_recently_played(summoner, m.champion_name)
        out.append(m)

    return out


def last_recently_played(summoner, champ_name):
    most_recent = ByReferenceMatch.query.filter_by(
        summoner_context=summoner, champion_played=champ_name
    ).order_by(
        ByReferenceMatch.timestamp.desc()
    ).first()

    if most_recent is None:
        last_played = "N/A"
    else:
        last_played = most_recent.date

    return last_played


def get_leaderboard_data(leaderboard_group, queue_type):
    leaderboard = game_api.get_leaderboard(leaderboard_group, queue_type)['entries']

    out = []
    for player in leaderboard:
        data = SimpleNamespace()
        data.name = player['summonerName']
        data.points = player['leaguePoints']
        data.wins = player['wins']
        data.losses = player['losses']

        total_games = data.wins + data.losses
        data.winrate = '{:.2f}%'.format((data.wins / total_games) * 100)

        out.append(data)

    out.sort(key=lambda p: p.points)
    out.reverse()
    return enumerate(out, start=1)
