'''To run the website: $set FLASK_APP=main.py'''
from ogpp import app, db, game_api
from ogpp.models import Summoner, MatchByReference, Match, Player
from ogpp.game_consts import CHAMPIONS
from ogpp.db_helpers import (grab_summoner, get_match_history, get_match_stats,
                             populate_match_history, update_match_history,
                             update_summoner_info)
from ogpp.export_helpers import make_matches_exportable, most_played_champs, paginate
from ogpp.infod import update_info

import shelve
import pprint

all_tables = [Summoner, MatchByReference, Match, Player]


# development helpers
def nuke_db():
    '''drop all tables from the database.
       useful in development for when flask migrate/alembic
       doesn't pick up smaller changes on existing tables such
       as added/removed columns.

       This will however require making calls to flask db migrate & db upgrade.
    '''
    confirm = input('Really drop all tables? Type "YES" or quit.')
    if confirm == "YES":
        db.session.remove()
        db.drop_all()
        return "Done."

    return "Canceled"


def tear_down_db():
    for table in all_tables:
        table.query.delete()
    db.session.commit()


def is_populated(table):
    return table.query.count() > 0


def check_populated_tables():
    count = 0
    fmt = '{0.__name__} has {1} entries.'
    for table in all_tables:
        if is_populated(table):
            count += 1
            print(fmt.format(table, table.query.count()))
    print("%d tables contain entries." % count)


def unique_player_count():
    return len(set(player.name for player in Player.query.all()))


def remove_duplicate_matchref_entries(summoner):
    '''
    remove any duplicated entries that might have accidentally made its way
    into the database. Keep the originals.
    '''
    for match_ref in summoner.match_history.all():
        query = MatchByReference.query.filter_by(match_id=match_ref.match_id,
                                                 summoner_context=summoner)
        if query.count() > 1:
            match = query.first()
            # keep a copy of the original match
            original = MatchByReference(summoner_context=summoner,
                                        match_id=match.match_id,
                                        lane_played=match.lane_played,
                                        champion_played=match.champion_played,
                                        game_mode=match.game_mode,
                                        timestamp=match.timestamp)
            # remove the duplicate entries
            for duplicate in query.all():
                db.session.delete(duplicate)

            # restore the original copy
            db.session.add(original)
            db.session.commit()


def check_player_cache(player_name):
    with shelve.open('dcache') as d:
        return player_name in d


def dump_cache_contents():
    with shelve.open('dcache') as d:
        pprint.pprint(d['cache'])


@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Summoner': Summoner,
        'MatchByReference': MatchByReference,
        'Match': Match,
        'Player': Player,
        'api': game_api,
        'champs': CHAMPIONS,
        'grab_summoner': grab_summoner,
        'get_match_history': get_match_history,
        'get_match_stats': get_match_stats,
        'tear_down_db': tear_down_db,
        'is_populated': is_populated,
        'check_populated_tables': check_populated_tables,
        'all_tables': all_tables,
        'populate_match_history': populate_match_history,
        'nuke_db': nuke_db,
        'make_matches_exportable': make_matches_exportable,
        'unique_player_count': unique_player_count,
        'update_match_history': update_match_history,
        'update_summoner_info': update_summoner_info,
        'most_played_champs': most_played_champs,
        'update_info': update_info,
        'check_player_cache': check_player_cache,
        'dump_cache_contents': dump_cache_contents,
        'paginate': paginate
    }
