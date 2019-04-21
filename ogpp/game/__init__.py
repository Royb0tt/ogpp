import os

from .consts import (QUEUE_TYPE, _QUEUE_TYPE, CHAMPIONS,
                     RANK_DIVISIONS, RANK_TIERS, SUMMONER_SPELLS, _TEAMS)
from .api import RiotAPI

api = RiotAPI(os.environ.get('RIOT_API_KEY'))
