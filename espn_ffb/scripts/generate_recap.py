import argparse
from espn_ffb import util
from espn_ffb.db.database import db
from flask import Flask
import os
from espn_ffb.db.query import Query

app = Flask(__name__)

HTML_EXTENSION = ".html"
RECAP_TEMPLATE_DIR = "espn_ffb/templates/recap/{year}/{week}"

RECAP_TEMPLATE = """        {{#- {{{{ r.team }}}} = "{team_name}" -#}}
        {{#- {{{{ r.opponent }}}} = "{opponent_name}" #}}
        <img class="img" src="{{{{ url_for('static', filename='images/recap/placeholder.jpg') }}}}">
        <video class="img" playsinline autoplay muted loop>
          <source src="{{{{ url_for('static', filename='images/recap/placeholder.mp4') }}}}" type="video/mp4">
        </video>
        <p>
          body_text
        </p>
"""


def parse_args():
    parser = argparse.ArgumentParser(description="Generates weekly recap templates.")
    parser.add_argument('-e', '--environment', help="The development environment", type=str, required=True,
                        choices={"dev", "prod"})
    parser.add_argument('-w', '--week', help="The season week", type=int, required=True)
    parser.add_argument('-y', '--year', help="The season year", type=int, required=True)
    return vars(parser.parse_args())


def get_filename(year, week, team_id):
    template_dir = RECAP_TEMPLATE_DIR.format(year=year, week=week)
    os.makedirs(template_dir, exist_ok=True)
    return os.path.join(template_dir, str(team_id) + HTML_EXTENSION)


def generate_recap_template(filename, team_name, opponent_name):
    if os.path.isfile(filename):
        print("File alredy exists!")
        return

    with open(filename, 'w') as w:
        w.write(RECAP_TEMPLATE.format(team_name=team_name, opponent_name=opponent_name))


def main():
    args = parse_args()
    environment = args.get("environment")
    year = args.get("year")
    week = args.get("week")

    app.config.from_object(util.get_config(environment))
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get("DB_URI")
    db.init_app(app)
    query = Query(db)

    with app.app_context():
        team_ids = set(query.get_distinct_matchup_team_ids(year)[week])
        team_id_to_team_name = query.get_team_id_to_team_name(year)
        matchups = [m for m in query.get_matchups(year) if m.matchup_id == week and m.team_id in team_ids]
        for m in matchups:
            team_name = team_id_to_team_name.get(m.team_id)
            opponent_name = team_id_to_team_name.get(m.opponent_team_id)
            team_filename = get_filename(year, week, m.team_id)
            generate_recap_template(team_filename, team_name, opponent_name)


if __name__ == "__main__":
    main()
