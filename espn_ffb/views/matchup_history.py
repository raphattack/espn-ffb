from flask import Blueprint, current_app, render_template, request
from espn_ffb import util

matchup_history = Blueprint("matchup_history", __name__, template_folder="templates")
TABLE_HEADERS = ["Year", "Matchup ID", "Team", "Opponent Score", "Result"]
COLUMN_NAMES = ["year", "matchup_id", "team_score", "opponent_team_score", "is_win"]


@matchup_history.route('/matchup-history', methods=['GET'])
def show():
    query = current_app.config.get("QUERY")

    matchup_type = request.args.get('matchup_type', default=util.REGULAR_SEASON)
    owner_id = request.args.get('owner_id', type=str)
    opponent_owner_id = request.args.get('opponent_owner_id', type=str)

    owners = query.get_owners(exclude=True)
    is_playoffs = util.get_is_playoffs(matchup_type)

    if not owner_id:
        owner_id = owners[0].id
        opponent_owner_id = owners[1].id

    records = query.get_matchup_history(owner_id=owner_id, opponent_owner_id=opponent_owner_id, is_playoffs=is_playoffs)
    return render_template('matchup-history.html', title='Matchup History', table_headers=TABLE_HEADERS,
                           column_names=COLUMN_NAMES, matchup_type=matchup_type, owners=owners, selected_owner=owner_id,
                           selected_opponent=opponent_owner_id, records=records)
