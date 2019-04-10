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
    'league': {
        'summoner_rank': 'league/v{version}/positions/by-summoner/{encrypted_summoner_id}',
        'masters': 'league/v{version}/masterleagues/by-queue/{queue}',
        'grandmasters': 'league/v{version}/grandmasterleagues/by-queue/{queue}',
        'challengers': 'league/v{version}/challengerleagues/by-queue/{queue}'
    },
    'champion_mastery': 'champion-mastery/v{version}/champion-masteries/by-summoner/{encrypted_summoner_id}',

}

API_VERSION = {
    'summoner': '4',
    'champion_mastery': '4',
    'match_history': '4',
    'match_by_id': '4',
    'summoner_rank': '4',
    'masters': '4',
    'grandmasters': '4',
    'challengers': '4'
}

REGIONS = {
    'north_america': 'na1'
}


class BadResponse(BaseException):
    '''Raised exception when we get a bad response code from the server'''
    pass


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
        '''
        Get the match history of the current summoner.

        args
        account_id -> str
            : summoner account id that is a valid encrypted hash string.
        champion -> str
            : name of the champion.
        queue_type -> int
            : the queue type's id representation.
        end_index -> int
            : the upper limit of requested matches.
        season -> int
            : filter matches by season number.
            : the current season(2019) is season 2013.
            : google riot's game constants for more info on exactly how
            : game seasons are annotated.
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
        api_url = URL['match']['by_id'].format(
            version=API_VERSION['match_by_id'],
            match_id=match_id
        )

        match_data = self.get(api_url)
        return match_data

    def get_summoner_ranks(self, summoner_id):
        '''api call which gets a list of all ranked positions for solo/duo.'''
        api_url = URL['league']['summoner_rank'].format(
            version=API_VERSION['summoner_rank'],
            encrypted_summoner_id=summoner_id
        )

        summoner_rank_data = self.get(api_url)
        return summoner_rank_data

    def get_summoner_mastery(self, summoner_id):
        api_url = URL['champion_mastery'].format(
            version=API_VERSION['champion_mastery'],
            encrypted_summoner_id=summoner_id
        )

        mastery_list = self.get(api_url)
        return mastery_list

    def get_leaderboard(self, leaderboard_type='masters', queue='RANKED_SOLO_5x5'):
        '''
        Get leaderboard data from a type of either: masters, grandmasters, or challegers
        from a choice queue of: RANKED_SOLO_5x5, RANKED_FLEX_SR, or RANKED_FLEX_TT
        default choices provided are from masters and ranked solor
        '''
        api_url = URL['league'][leaderboard_type].format(
            version=API_VERSION['masters'],
            queue=queue
        )

        leaderboard = self.get(api_url)
        return leaderboard
