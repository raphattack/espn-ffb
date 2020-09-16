from flask import Blueprint, current_app, render_template

standings = Blueprint("standings", __name__, template_folder="templates")
TABLE_HEADERS = ["Name", "Wins", "Losses", "Ties", "Win Percentage", "Points For", "Points Against", "Average Points For",
                 "Average Points Against", "Championships", "Sackos"]
COLUMN_NAMES = ["owner_id", "wins", "losses", "ties", "win_percentage", "points_for", "points_against", "avg_points_for",
                "avg_points_against", "championships", "sackos"]


def get_owner_id_to_name(query):
    return {o.id: o.first_name + " " + o.last_name for o in query.get_owners()}


@standings.route('/standings/<string:year>', methods=['GET'])
def show(year: str):
    # return "<h1 style='color:blue'>Hello There!</h1>" + str(sys.argv[1])
    query = current_app.config.get("QUERY")

    owner_id_to_name = get_owner_id_to_name(query)
    sacko = query.get_sacko_current()

    if year == "overall":
        records = query.get_standings()
    else:
        records = query.get_standings(year=int(year))

    return render_template('standings.html', title='Standings', table_headers=TABLE_HEADERS,
                           column_names=COLUMN_NAMES, records=records, sacko=sacko,
                           owner_id_to_name=owner_id_to_name)
