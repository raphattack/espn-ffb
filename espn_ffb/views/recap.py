from flask import Blueprint, current_app, render_template
from espn_ffb import util

recap = Blueprint("recap", __name__, template_folder="templates")


@recap.route('/recap/<int:year>/<int(fixed_digits=2):week>', methods=['GET'])
def show(year, week):
    query = current_app.config.get("QUERY")

    team_ids = set(query.get_distinct_matchup_team_ids(year)[week])
    matchups = [m for m in query.get_matchups(year) if m.matchup_id == week and m.team_id in team_ids]
    matchups = sorted(matchups, key=lambda m: m.team_id)
    win_streaks = query.get_win_streak_by_year(matchups, year, week)
    team_id_to_record = query.get_team_id_to_record(year, week)
    team_id_to_team_name = query.get_team_id_to_team_name(year)
    h2h_records = query.get_h2h_record_current(matchups, year, week)

    recaps = list()
    for m, ws, h2h_record in zip(matchups, win_streaks, h2h_records):
        streak_owner = team_id_to_team_name.get(ws.streak_owner)

        recaps.append(
            util.Recap(
                team=team_id_to_team_name[m.team_id],
                team_record=team_id_to_record[m.team_id],
                opponent=team_id_to_team_name[m.opponent_team_id],
                opponent_record=team_id_to_record[m.opponent_team_id],
                streak=ws.streak,
                streak_owner=streak_owner,
                h2h_record=h2h_record,
                body=f"recap/{year}/{week:02d}/{m.team_id}.html"
            )
        )
    return render_template("recap.html", title='Weekly Recap', recaps=recaps)
