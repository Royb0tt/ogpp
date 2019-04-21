'''
background work to help with how player ranked stats are displayed
'''
import time

from ..helpers import add_match_to_db
from ..models import ByReferenceMatch, Match
from ..game import api

RATE_LIMIT = 7


class Interrupt(BaseException):
    pass


def populate_match_table():
    '''
    populate match table with ranked games to stabilize player ranked stats
    '''
    all_references = ByReferenceMatch.query.filter(
        ByReferenceMatch.game_mode.in_([440, 420])
    ).order_by(
        ByReferenceMatch.timestamp.desc()
    ).all()

    total = 0
    count = 0

    start = time.time()
    try:
        for match in all_references:
            existing_entry = Match.query.filter_by(match_id=match.match_id).first()
            if existing_entry is not None:
                print("Skipping %r" % existing_entry)
                continue
            else:
                match_from_api = api.get_match_stats(match.match_id)
                m = add_match_to_db(match_from_api, match.timestamp)
                print("Added %r..." % m)
                total = total + 1
                count += 1
                if count == RATE_LIMIT:
                    print("Rate limit reached, sleeping...")
                    time.sleep(5)
                    count = 0
    except Exception as e:
        raise Interrupt(str(e))
    finally:
        elapsed_time = time.time() - start
        time_format = time.strftime("%H hours %M minutes %S seconds", time.gmtime(elapsed_time))
        print("Elapsed time: {}, stored {} new ranked games".format(time_format, total))
