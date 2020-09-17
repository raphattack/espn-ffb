from espn_ffb import util
from espn_ffb.db.database import db
from espn_ffb.db.model.champions import Champions
from espn_ffb.db.model.matchups import Matchups
from espn_ffb.db.model.owners import Owners
from espn_ffb.db.model.records import Records
from espn_ffb.db.model.sackos import Sackos
from espn_ffb.db.model.teams import Teams
from espn_ffb.db.query import Query
from espn_ffb.views.awards import awards
from espn_ffb.views.champions import champions
from espn_ffb.views.h2h_records import h2h_records
from espn_ffb.views.matchup_history import matchup_history
from espn_ffb.views.playoffs import playoffs
from espn_ffb.views.recap import recap
from espn_ffb.views.standings import standings
from flask import Flask, redirect
import logging
import sys

LOG_FORMAT = "%(asctime)s %(levelname)s %(pathname)s %(lineno)d: %(message)s"

app = Flask(__name__)
app.config.from_object(util.get_config(sys.argv[2]))
app.register_blueprint(awards)
app.register_blueprint(champions)
app.register_blueprint(h2h_records)
app.register_blueprint(matchup_history)
app.register_blueprint(playoffs)
app.register_blueprint(recap)
app.register_blueprint(standings)
app.static_folder = "web/static"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get("DB_URI")
db.init_app(app)
query = Query(db)
app.config['QUERY'] = query


@app.template_filter()
def points_format(value):
    return "{:,}".format(value)


@app.template_filter()
def percentage_format(value):
    return "{:.4f}".format(value)


@app.context_processor
def get_years():
    return dict(years=query.get_distinct_years())


@app.before_first_request
def setup_logging():
    if not app.debug:
        formatter = logging.Formatter(LOG_FORMAT)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)


@app.route('/', methods=['GET'])
def show_index():
    return redirect("/awards", code=302)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
