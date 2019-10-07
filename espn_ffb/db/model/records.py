from espn_ffb.db.database import db


class Records(db.Model):
    PKEY_NAME = "records_year_team_id_pkey"

    year = db.Column(db.Integer, nullable=False)
    team_id = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.String, nullable=False)
    standing = db.Column(db.Integer, nullable=False)
    wins = db.Column(db.Integer, nullable=False)
    losses = db.Column(db.Integer, nullable=False)
    ties = db.Column(db.Integer, nullable=False)
    points_for = db.Column(db.Numeric, nullable=False)
    points_against = db.Column(db.Numeric, nullable=False)
    streak_length = db.Column(db.Integer, nullable=False)
    streak_type = db.Column(db.String, nullable=False)
    db.PrimaryKeyConstraint(year, team_id, name=PKEY_NAME)

    def __str__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def __repr__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def __key(self):
        return (
            self.year,
            self.team_id,
            self.owner_id,
            self.standing,
            self.wins,
            self.losses,
            self.ties,
            self.points_for,
            self.points_against,
            self.streak_length,
            self.streak_type
        )

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()

    def as_dict(self):
        return {
            'year': self.year,
            'team_id': self.team_id,
            'owner_id': self.owner_id,
            'standing': self.standing,
            'wins': self.wins,
            'losses': self.losses,
            'ties': self.ties,
            'points_for': self.points_for,
            'points_against': self.points_against,
            'streak_length': self.streak_length,
            'streak_type': self.streak_type
        }

    def props_dict(self):
        return self.as_dict()
