from espn_ffb.db.database import db


class Matchups(db.Model):
    PKEY_NAME = "matchups_year_matchup_id_team_id_pkey"

    year = db.Column(db.Integer, nullable=False)
    matchup_id = db.Column(db.Integer, nullable=False)
    team_id = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.String, nullable=False)
    opponent_team_id = db.Column(db.Integer)
    opponent_owner_id = db.Column(db.String)
    team_score = db.Column(db.Numeric, nullable=False)
    opponent_team_score = db.Column(db.Numeric)
    is_win = db.Column(db.Boolean, nullable=False)
    is_loss = db.Column(db.Boolean, nullable=False)
    is_pending = db.Column(db.Boolean, nullable=False)
    is_bye = db.Column(db.Boolean, nullable=False)
    is_playoffs = db.Column(db.Boolean, nullable=False)
    is_consolation = db.Column(db.Boolean, nullable=False)
    db.PrimaryKeyConstraint(year, matchup_id, team_id, name=PKEY_NAME)

    def __str__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def __repr__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def __key(self):
        return (
            self.year,
            self.matchup_id,
            self.team_id,
            self.owner_id,
            self.opponent_team_id,
            self.opponent_owner_id,
            self.team_score,
            self.opponent_team_score,
            self.is_win,
            self.is_loss,
            self.is_pending,
            self.is_bye,
            self.is_playoffs,
            self.is_consolation
        )

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()

    def as_dict(self):
        return {
            'year': self.year,
            'matchup_id': self.matchup_id,
            'team_id': self.team_id,
            'owner_id': self.owner_id,
            'opponent_team_id': self.opponent_team_id,
            'opponent_owner_id': self.opponent_owner_id,
            'team_score': self.team_score,
            'opponent_team_score': self.opponent_team_score,
            'is_win': self.is_win,
            'is_loss': self.is_loss,
            'is_pending': self.is_pending,
            'is_bye': self.is_bye,
            'is_playoffs': self.is_playoffs,
            'is_consolation': self.is_consolation
        }

    def props_dict(self):
        return self.as_dict()
