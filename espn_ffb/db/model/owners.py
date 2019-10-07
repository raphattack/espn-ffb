from espn_ffb.db.database import db


class Owners(db.Model):
    PKEY_NAME = "owners_username_pkey"

    id = db.Column(db.String, nullable=False)
    username = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    db.PrimaryKeyConstraint(username, name=PKEY_NAME)

    def __key(self):
        return (
            self.id,
            self.username,
            self.first_name,
            self.last_name
        )

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        return isinstance(self, type(other)) and self.__key() == other.__key()

    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name
        }

    def props_dict(self):
        return self.as_dict()
