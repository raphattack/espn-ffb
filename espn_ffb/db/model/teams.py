from espn_ffb.db.database import db


class Teams(db.Model):
    PKEY_NAME = "teams_year_id_pkey"

    year = db.Column(db.Integer, nullable=False)
    id = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.String, nullable=False)
    abbreviation = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    nickname = db.Column(db.String, nullable=False)
    db.PrimaryKeyConstraint(year, id, name=PKEY_NAME)

    def __str__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def __repr__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def __key(self):
        return (
            self.year,
            self.id,
            self.owner_id,
            self.abbreviation,
            self.location,
            self.nickname
        )

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()

    def as_dict(self):
        return {
            'year': self.year,
            'id': self.id,
            'owner_id': self.owner_id,
            'abbreviation': self.abbreviation,
            'location': self.location,
            'nickname': self.nickname
        }

    def props_dict(self):
        return self.as_dict()
