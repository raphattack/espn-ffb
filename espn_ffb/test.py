from espn_ffb import util
from espn_ffb.db.database import db
from espn_ffb.db.query import Query
from flask import Flask
import sys


app = Flask(__name__)
app.config.from_object(util.get_config(sys.argv[2]))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get("DB_URI")
db.init_app(app)
query = Query(db)
app.config['QUERY'] = query


# noinspection DuplicatedCode,PyBroadException
def main():
    with app.app_context():
        q = Query(db)
        playoff_standings = q.get_playoff_standings(year=2014)
        for p in playoff_standings:
            print(p)


if __name__ == "__main__":
    main()
