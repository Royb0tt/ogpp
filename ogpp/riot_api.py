from .game_consts import CHAMPION_BY_ID

import requests

'''
riot api module
'''

URL = {
    # base url #
    'base_url': 'https://{region}.api.riotgames.com/lol/{api_url}',
    # api urls #
    'summoner': {
        'by_name': 'summoner/v{version}/summoners/by-name/{arg}',
        'by_account': 'summoner/v{version}/summoners/by-account/{arg}',
        'by_puuid': 'summoner/v{version}/summoners/by-puuid/{arg}',
        'by_id': 'summoner/v{version}/summoners/{arg}'
    },
    'match': {
        'history': 'match/v{version}/matchlists/by-account/{encrypted_account_id}',
        'by_id': 'match/v{version}/matches/{match_id}'
    },
    'summoner_rank': 'league/v{version}/positions/by-summoner/{encrypted_summoner_id}',
    'champion_mastery': 'champion-mastery/v{version}/champion-masteries/by-summoner/{encrypted_summoner_id}',
}

API_VERSION = {
    'summoner': '4',
    'champion_mastery': '4',
    'match_history': '4',
    'match_by_id': '4',
    'summoner_rank': '4'
}

REGIONS = {
    'north_america': 'na1'
}


class BadResponse(BaseException):
    '''Raised exception when we get a bad response code from the server'''
    pass


# this is useless for the time being in the context of a web application
# unless I refactor it into something that is more suited to the app.
def check_response(f):
    '''decorator function for checking api request calls for bad response codes.
    for now, anything that doesn't respond with 200 will be interpreted as a bad code
    and will raise BadResponse.
    '''
    def wrapper(*args, **kwargs):
        try:
            response = f(*args, **kwargs)
        except BadResponse as e:
            return "Response was not okay: {0}".format(str(e))
        return response
    return wrapper


# The main api.
class RiotAPI:
    def __init__(self, api_key, region=REGIONS['north_america']):
        # api key expires daily. need to generate one from developers.riotgames.com
        self.api_key = api_key
        self.region = region

    def __repr__(self):
        return "RiotAPI<key: {0.api_key}>".format(self)

    def get(self, api_url, params=None):
        '''
        send out a prepared api request.
        params should be a dictionary.
        returns a response object.
        '''
        args = {
            'api_key': self.api_key
        }
        if params:
            for key, value in params.items():
                if key not in args:
                    args[key] = value

        full_url = URL['base_url'].format(region=self.region, api_url=api_url)
        response = requests.get(full_url, params=args)
        if response.status_code != 200:
            raise BadResponse(response.status_code)
        return response.json()

    # api calls
    def grab_summoner(self, arg, method='by_name'):
        '''
        api call that gets summoner account info(name, puuid, account_id).
        information grabbed by this api call is the jumping off point for
        other api calls as they use the info obtained from here.

        arg can be a string representing name(by default), puuid, account, or summoner id
        just be sure to change the method when using something that isn't a name
        '''
        api_url = URL['summoner'][method].format(version=API_VERSION['summoner'],
                                                 arg=arg)
        summoner_data = self.get(api_url)

        return summoner_data

    def get_match_history_list(self, account_id, end_index=None,
                               queue_type=None, champion=None,
                               season=13):
        '''Get the match history of the current summoner.
        by default, get matches from last 20(end_index param).
        will add more optional parameters in the future maybe.
        Other params:
            -champion: STR, filter by the champion name which
             we will convert to its in-game id.
            -queue_type: INT, filter by game mode.
            For info on queue type, refer to game_consts.py
        '''
        params = {}
        if end_index:
            params['endIndex'] = end_index
        if champion:
            params['champion'] = CHAMPION_BY_ID[champion]
        if queue_type:
            params['queue'] = queue_type
        if season:
            params['season'] = season

        api_url = URL['match']['history'].format(version=API_VERSION['match_history'],
                                                 encrypted_account_id=account_id)

        match_history = self.get(api_url, params)
        return match_history

    def get_match_stats(self, match_id):
        '''api call that returns data of a match in detail'''
        api_url = URL['match']['by_id'].format(version=API_VERSION['match_by_id'],
                                               match_id=match_id)
        match_data = self.get(api_url)

        return match_data

    def get_summoner_ranks(self, summoner_id):
        '''api call which gets a list of all ranked positions for solo/duo.'''
        api_url = URL['summoner_rank'].format(version=API_VERSION['summoner_rank'],
                                              encrypted_summoner_id=summoner_id)
        summoner_rank_data = self.get(api_url)
        return summoner_rank_data

    def get_summoner_mastery(self, summoner_id):
        api_url = URL['champion_mastery'].format(version=API_VERSION['champion_mastery'],
                                                 encrypted_summoner_id=summoner_id)

        mastery_list = self.get(api_url)
        return mastery_list
