'''functions that help store information retrieved
   from the web api to the database.

    TODO: refector get_highest_rank() as it only picks up a single rank now
    TODO: make page that shows win percentage of champion played by all players
'''
from functools import wraps
from types import SimpleNamespace
from sqlalchemy.exc import DBAPIError
from .models import Summoner, MatchByReference, Match, Player
from .game_consts import CHAMPIONS, RANK_DIVISIONS, RANK_TIERS, SUMMONER_SPELLS
# from . import game_api, db
from . import db, game_api


def sanitize_name(name):
    '''make a name indexable for database querying'''
    return name.replace(' ', '').lower()


def wrap_database_action(func):
    '''
    Rollback the database in the event we catch an error
    while performing a database action.
    '''
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            out = func(*args, **kwargs)
        except DBAPIError as e:
            error_fmt = "Database error: {0.__traceback__}"
            print(error_fmt.format(e))
            db.session.rollback()
            return
        return out
    return wrapper


@wrap_database_action
def grab_summoner(name):
    '''
    attempt to pull the summoner from the database, if it exists.
    in the event it does not, do an api call to get the summoner info,
    then store it into the database for later retrieval.
    '''
    indexed_name = sanitize_name(name)
    summoner = Summoner.query.filter_by(indexed_name=indexed_name).first()
    if summoner is None:
        s = game_api.grab_summoner(name)
        summoner = serialize_summoner_to_db(s, indexed_name)
        add_summoner_to_db(summoner)
        populate_match_history(summoner)

    return summoner


def add_summoner_to_db(summoner):
    db.session.add(summoner)
    db.session.commit()


def get_highest_rank(summoner_id):
    '''Note: Riot just permanently retired position rankings.
       Since they have reverted back to single ranks,
       this function will be reworked in the future as well.

       obtain the highest positional rank out of a list of positions from the api call
       Param summoner takes a SimpleNamespace object representing the summoner obtained by the api.
       Returns a SimpleNamespace object representing the highest rank calculated
    '''
    ranks = game_api.get_summoner_ranks(summoner_id)
    if not ranks:
        rank = SimpleNamespace()
        rank.tier = 'unranked'
        rank.rank = ''
        rank.leaguePoints = 0
        rank.wins = 0
        rank.losses = 0
        rank.queueType = 'none'
        rank.position = 'none'
        return rank

    ranks = [SimpleNamespace(**rank) for rank in ranks]
    highest_rank = max(ranks, key=lambda r: RANK_TIERS[r.tier] +
                       RANK_DIVISIONS[r.rank] + r.leaguePoints)
    return highest_rank


def serialize_summoner_to_db(summoner, indexed_name):
    summoner = SimpleNamespace(**summoner)
    rank = get_highest_rank(summoner.id)
    summoner = Summoner(name=summoner.name, indexed_name=indexed_name,
                        level=summoner.summonerLevel,
                        profile_icon=summoner.profileIconId,
                        account_id=summoner.accountId,
                        summoner_id=summoner.id,
                        highest_rank=rank.tier,
                        rank_division=rank.rank,
                        points=rank.leaguePoints,
                        wins=rank.wins, losses=rank.losses,
                        ranked_mode=rank.queueType,
                        position=rank.position
                        )
    return summoner


@wrap_database_action
def populate_match_history(summoner):
    match_history = game_api.get_match_history_list(summoner.account_id)['matches']
    for match in match_history:
        m = serialize_matchref_to_db(match, summoner)
        add_matchref_to_db(m)


def add_matchref_to_db(match_ref):
    db.session.add(match_ref)
    db.session.commit()


@wrap_database_action
def update_match_history(summoner):
    '''
    this will be used when we implement a refresh button on the webpage
    which when clicked will signal the app to call the game api and grab
    the latest games from riots database.
    '''
    match_references = game_api.get_match_history_list(summoner.account_id)['matches']
    for match in match_references:
        # once we come across a match that is already in the database
        # we know we're up to date so break from the iteration
        m = MatchByReference.query.filter_by(summoner_context=summoner,
                                             match_id=match['gameId']).first()
        if m:
            break
        else:
            m = serialize_matchref_to_db(match, summoner)
            db.session.add(m)
    db.session.commit()


def update_summoner_info(summoner):
    '''
    this will be called when we implement a refresh button on the webpage
    which will update the summoner's general info such as current profile icon,
    rank, level, etc.
    '''
    updated_info = game_api.grab_summoner(summoner.name)
    # if summoner.account_id != updated_info:
    # name change
    # get summoner by encrypted id
    # game_api.grab_summoner(summoner.account_id)
    # update the database entry's old name to the new name
    s = SimpleNamespace(**updated_info)
    # update their level and displayed icon
    summoner.level = s.summonerLevel
    summoner.profile_icon = s.profileIconId

    # update their rank progress
    updated_rank = get_highest_rank(s.id)
    summoner.highest_rank = updated_rank.tier
    summoner.rank_division = updated_rank.rank
    summoner.points = updated_rank.leaguePoints
    summoner.wins = updated_rank.wins
    summoner.losses = updated_rank.losses

    db.session.commit()


def update_summoner_page(summoner_name):
    summoner = Summoner.query.filter_by(indexed_name=summoner_name).first()
    update_match_history(summoner)
    update_summoner_info(summoner)


def serialize_matchref_to_db(match, summoner):
    match = SimpleNamespace(**match)
    time_converted_from_milliseconds = match.timestamp / 1000
    m = MatchByReference(summoner_context=summoner, match_id=match.gameId,
                         lane_played=match.lane, game_mode=match.queue,
                         timestamp=time_converted_from_milliseconds,
                         champion_played=CHAMPIONS[match.champion])
    return m


@wrap_database_action
def get_match_stats(matches, page_num=1):
    '''
    attempt to get a match and it's participants in detail from the database.
    if it doesn't exist we call the game's api and then store it in the databse.

    args:
    summoner: Summoner database object which has a match_history attribute.
    page_num: int, used for pagination of query results
    '''
    match_with_stats = []

    for match_ref in matches.items:
        match = Match.query.filter_by(match_id=match_ref.match_id).first()
        if not match:
            match_from_api = game_api.get_match_stats(match_ref.match_id)
            match = add_match_to_db(match_from_api, match_ref.timestamp)
        else:
            for player in match.players:
                rank = get_rank(player)
                player.current_rank = rank
                db.session.commit()

        match_with_stats.append(match)

    return match_with_stats


@wrap_database_action
def add_match_to_db(match, match_timestamp):
    match = SimpleNamespace(**match)
    m = Match(match_id=match.gameId, game_mode=match.queueId,
              timestamp=match_timestamp)

    db.session.add(m)

    for player, player_id in zip(match.participants, match.participantIdentities):
        player.update(player_id['player'])
        player = serialize_player_to_db(player, m)
        db.session.add(player)

    db.session.commit()

    return m


def serialize_player_to_db(player, match):
    player = SimpleNamespace(**player)
    stats = SimpleNamespace(**player.stats)
    indexed_name = sanitize_name(player.summonerName)

    rank = get_rank(player)

    player = Player(game_context=match, name=player.summonerName,
                    indexed_name=indexed_name,
                    current_rank=rank,
                    champion_played=CHAMPIONS[player.championId],
                    champion_level=stats.champLevel,
                    win=stats.win, team_id=player.teamId,
                    item1=stats.item0, item2=stats.item1, item3=stats.item2,
                    item4=stats.item3, item5=stats.item4, item6=stats.item5,
                    item7=stats.item6,
                    kills=stats.kills, deaths=stats.deaths, assists=stats.assists,
                    gold_earned=stats.goldEarned, gold_spent=stats.goldSpent,
                    spell1=SUMMONER_SPELLS[player.spell1Id], spell2=SUMMONER_SPELLS[player.spell2Id])
    return player


def get_rank(player):
    '''
    delayed lookup for player rank that works without making
    an intermediate api call but only fetches something if the player's
    page has been landed on previously.
    '''
    # fresh from json data
    if hasattr(player, 'summonerName'):
        name = player.summonerName
    # already serialized object
    else:
        name = player.name

    summoner = Summoner.query.filter_by(name=name).first()
    if summoner is not None:
        rank = summoner.highest_rank + ' ' + summoner.rank_division
    else:
        rank = 'unranked'

    return rank
