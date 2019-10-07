from espn_ffb import util
from espn_ffb.config import Config
from espn_ffb.espn.model.matchup_score import MatchupScore
from espn_ffb.espn.model.member import Member
from espn_ffb.espn.model.team import Team
import requests
from typing import Type


def get_base_url(league_id: int, season_id: int, is_current_year: bool):
    if is_current_year:
        return f"https://fantasy.espn.com/apis/v3/games/FFL/seasons/{season_id}/segments/0/leagues/{league_id}"
    else:
        return f"https://fantasy.espn.com/apis/v3/games/ffl/leagueHistory/{league_id}?seasonId={season_id}"


class LeagueSetting:
    def __init__(self, config: Type[Config], year: int):
        """
        Initialize league settings for a given year.

        :param config: the config object
        :param year: the year
        """

        _is_current_year = util.get_is_current_year(current_year=config.CURRENT_YEAR, season_id=year)
        _base_url = get_base_url(league_id=config.LEAGUE_ID, season_id=year, is_current_year=_is_current_year)

        # fetch matchup scores data
        _matchup_scores_data = requests.get(_base_url,
                                            params="view=mMatchupScore",
                                            cookies=config.COOKIES).json()

        # fetch settings data
        _settings_data = requests.get(_base_url,
                                      params="view=mSettings",
                                      cookies=config.COOKIES).json()

        # fetch team data
        _team_data = requests.get(_base_url,
                                  params="view=mTeam",
                                  cookies=config.COOKIES).json()

        if not _is_current_year:
            _matchup_scores_data = _matchup_scores_data[0]
            _settings_data = _settings_data[0]
            _team_data = _team_data[0]

        self.matchup_scores = [MatchupScore(matchup_score) for matchup_score in _matchup_scores_data.get("schedule")]
        self.members = [Member(member) for member in _team_data.get("members")]
        self.owner_ids = {member.id for member in self.members}
        self.playoff_matchup_length = _settings_data['settings']['scheduleSettings']['playoffMatchupPeriodLength']
        self.playoff_team_count = _settings_data['settings']['scheduleSettings']['playoffTeamCount']
        self.regular_season_matchup_count = _settings_data['settings']['scheduleSettings']['matchupPeriodCount']
        self.regular_season_matchup_length = _settings_data['settings']['scheduleSettings']['matchupPeriodLength']
        self.season_id = _settings_data.get("seasonId")
        self.teams = [Team(team) for team in _team_data.get("teams")]

    def __str__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)
