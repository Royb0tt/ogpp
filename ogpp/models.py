from .game_consts import _QUEUE_TYPE as Q_TYPE
from .game_consts import QUEUE_TYPE
from datetime import datetime
from ogpp import db
'''
Database entities
'''


class Summoner(db.Model):
    '''Account level information as well as match history'''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True, unique=True)
    # a database sane version of the true name of the summoner
    indexed_name = db.Column(db.String(32), unique=True)

    level = db.Column(db.String(50))
    profile_icon = db.Column(db.String(50))
    account_id = db.Column(db.String(128), unique=True)
    summoner_id = db.Column(db.String(128), unique=True)
    # rank info
    highest_rank = db.Column(db.String(10))
    rank_division = db.Column(db.String(3))
    position = db.Column(db.String(20))
    points = db.Column(db.Integer)
    wins = db.Column(db.Integer)
    losses = db.Column(db.Integer)
    ranked_mode = db.Column(db.String(20))

    match_history = db.relationship('ByReferenceMatch',
                                    backref="summoner_context", lazy='dynamic')

    def __repr__(self):
        return "Summoner<{0.name}, Level:{0.level}>".format(self)

    @property
    def rank(self):
        fmt = '{0.highest_rank} {0.rank_division}'
        return fmt.format(self)

    @property
    def ranked_games_total(self):
        return self.wins + self.losses

    @property
    def ranked_win_ratio(self):
        try:
            return int((self.wins / self.ranked_games_total) * 100)
        except ZeroDivisionError:
            return 100

    @property
    def ranked_games(self):
        valid_queue_types = [Q_TYPE['RANKED_SOLO'], Q_TYPE['RANKED_FLEX']]
        ranked = self.match_history.filter(
            ByReferenceMatch.game_mode.in_(valid_queue_types)
        ).order_by(
            ByReferenceMatch.timestamp.desc()
        )

        return ranked

    @property
    def all_games(self):
        '''give matches in order of most recent'''
        mh = self.match_history.all()
        mh.sort(key=lambda m: m.timestamp)
        mh.reverse()
        return mh


class ByReferenceMatch(db.Model):
    '''
    Database model that holds light references to
    access matches in more detail using the api.
    It will be used to either query
    or, populate through the game api, the Match table.
    '''
    id = db.Column(db.Integer, primary_key=True)
    summoner_id = db.Column(db.Integer, db.ForeignKey('summoner.id'))
    lane_played = db.Column(db.String(20))
    # consider storing the champion played as the name instead of the id
    champion_played = db.Column(db.String(20))

    match_id = db.Column(db.BigInteger)
    # consider storing the game mode as the string representation instead
    game_mode = db.Column(db.Integer)
    timestamp = db.Column(db.Float)

    def __repr__(self):
        return "ByReferenceMatch<ID: {0.match_id} Type:{0.queue_type}, of {0.summoner_context} playing: {0.champion_played}>".format(self)

    @property
    def date(self):
        dt = datetime.utcfromtimestamp(self.timestamp)
        return dt.strftime('%a %m/%d/%Y %I:%M%p')

    @property
    def queue_type(self):
        return QUEUE_TYPE[self.game_mode]


class Match(db.Model):
    '''
    This table is intended to be standalone and not linked
    to any player in particular via a n-to-many relationship.
    The intended use of this table is to be accessed
    using the match ids from a summoner's match history
    which IS actually linked to a specific player.

    The benefit of not having this table solidly linked
    to another table is that:
        -It's a general information table. It's purpose is clear
        and it shouldn't be biased towards a single player
        I can query just using a match's id as it is after all
        lone table with loose reference(same match id in ByReferenceMatch)

            for match in summoner.match_history.all():
                Match.query.filter_by(match.match_id)

        -Implicit reduction of data redundancy. As this table and
        it's player-relationship by far holds the most amount of information
        compared to the other tables, we would be repeating entries
        to the table based on different summoners.
        This can prove to be disadvantageous, the only difference between the
        redundant entries of the same match would be summoner contextual data(summoner id & champ id)

        So it would be fine if ByReferenceMatch had multiple redundant entries
        as the information they carry is relatively light
        in comparison to the information being stored here.
        Furthermore they are a perfectly intuitive intermediary step for
        grabbing larger amounts of data that would be found here because
        they're tied to the summoner table as match history.
    '''
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.BigInteger)
    # consider storing the game_mode as a string representation
    game_mode = db.Column(db.Integer)
    timestamp = db.Column(db.Float)
    # this column should return a list of players from a game instance
    # i.e.
    #       match = Match.query.filter_by(match_id)
    #       print(match.participants) -> [<Player 1>, <Player 2>, ..., etc.]
    participants = db.relationship('Player', backref='game_context', lazy='dynamic')

    def __repr__(self):
        return "Match<ID: {0.match_id}, Mode: {0.queue_type}>".format(self)

    @property
    def players(self):
        return self.participants.all()

    @property
    def date(self):
        dt = datetime.utcfromtimestamp(self.timestamp)
        return dt.strftime('%a %m/%d/%Y %I:%M%p')

    @property
    def queue_type(self):
        return QUEUE_TYPE[self.game_mode]

    @property
    def contains_player(self, player_name):
        return any(p.name == player_name for p in self.players)

    def get_player(self, player_name):
        if self.contains_player:
            self.participants.filter_by(name=player_name).first()


class Player(db.Model):
    '''
    Database model that is distinct from a summoner in the sense
    that a summoner refers to general account information.
    The context of a player here describes an in-game entity
    that is tied to a specific game instance, this is distinct
    from a summoner, as the context of a summoner is the account level information.
    This table will contain in-game related columns
    such as items as well as other in-game related stats.
    '''
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('match.id'))

    # summoner info
    name = db.Column(db.String(32))
    indexed_name = db.Column(db.String(32))  # this is the name that should be used to look up queries related to a player
    current_rank = db.Column(db.String(20))
    # consider storing the champion as a string instead of it's id.
    champion_played = db.Column(db.String(20))
    champion_level = db.Column(db.Integer)
    win = db.Column(db.Boolean)
    team_id = db.Column(db.Integer)         # 100 - blue, 200 - red
    participant_id = db.Column(db.Integer)

    # summoner spells
    spell1 = db.Column(db.String(10))
    spell2 = db.Column(db.String(10))

    # items
    item1 = db.Column(db.String(5))
    item2 = db.Column(db.String(5))
    item3 = db.Column(db.String(5))
    item4 = db.Column(db.String(5))
    item5 = db.Column(db.String(5))
    item6 = db.Column(db.String(5))
    # ward slot
    item7 = db.Column(db.String(5))

    # kda
    kills = db.Column(db.Integer)
    deaths = db.Column(db.Integer)
    assists = db.Column(db.Integer)

    damage_dealt = db.Column(db.Integer)
    damage_healed = db.Column(db.Integer)
    gold_earned = db.Column(db.Integer)
    gold_spent = db.Column(db.Integer)
    # etc...

    def __repr__(self):
        return "Player<{0.name}, playing {0.champion_played} level {0.champion_level} on team {0.team_id} of {0.game_context}>".format(self)

    @property
    def items(self):
        return [self.item1, self.item2, self.item3, self.item4, self.item5, self.item6, self.item7]

    @property
    def avg_kda(self):
        try:
            out = (self.kills + self.assists) / self.deaths
        except ZeroDivisionError:
            out = self.kills + self.assists

        out = float('{:.2f}'.format(out))
        return out

    @property
    def kda(self):
        fmt = "{0}/{1}/{2}"
        return fmt.format(self.kills, self.deaths, self.assists)

    @property
    def game_mode(self):
        return QUEUE_TYPE[self.game_context.game_mode]
