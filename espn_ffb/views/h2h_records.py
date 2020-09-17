from flask import Blueprint, current_app, render_template, request
from espn_ffb import util

h2h_records = Blueprint("h2h_records", __name__, template_folder="templates")
TABLE_HEADERS = ['Opponent', 'Wins', 'Losses']
COLUMN_NAMES = ['opponent_name', 'wins', 'losses']


@h2h_records.route('/h2h-records', methods=['GET'])
def show():
    query = current_app.config.get("QUERY")

    matchup_type = request.args.get('matchup_type', default=util.REGULAR_SEASON)
    owner_id = request.args.get('owner_id', type=str)

    owners = query.get_owners(exclude=True)
    is_playoffs = util.get_is_playoffs(matchup_type)

    if not owner_id:
        owner_id = owners[0].id

    records = query.get_h2h_records(owner_id=owner_id, is_playoffs=is_playoffs)
    return render_template("h2h-records.html", title='H2H Records', table_headers=TABLE_HEADERS,
                           column_names=COLUMN_NAMES, matchup_type=matchup_type, owners=owners, selected_owner=owner_id,
                           records=records)
