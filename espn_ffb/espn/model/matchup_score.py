from decimal import Decimal
from espn_ffb import util
import pprint
from typing import Mapping


class MatchupScore:
    def __init__(self, data: Mapping):
        """
        Initialize team for a given dict.

        :param data: dict of team attributes to values
        """
        AWAY = "AWAY"
        HOME = "HOME"
        LOSERS_CONSOLATION_LADDER = "LOSERS_CONSOLATION_LADDER"
        UNDECIDED = "UNDECIDED"
        WINNERS_BRACKET = "WINNERS_BRACKET"
        WINNERS_CONSOLATION_LADDER = "WINNERS_CONSOLATION_LADDER"

        CONSOLATION_LADDER = {LOSERS_CONSOLATION_LADDER, WINNERS_CONSOLATION_LADDER}

        self._data = data

        self.team_count = 0
        self.away_adjustment = None
        self.away_team_id = None
        self.away_tie_break = None
        self.away_total_points = None
        self.home_adjustment = None
        self.home_team_id = None
        self.home_tie_break = None
        self.home_total_points = None

        self.away = self._data.get("away")
        if self.away is not None:
            self.team_count += 1
            self.away_adjustment = self.away.get("adjustment")
            self.away_team_id = self.away.get("teamId")
            self.away_tie_break = self.away.get("tiebreak")
            self.away_total_points = round(Decimal(self.away.get("totalPoints")), 2)

        self.home = self._data.get("home")
        if self.home is not None:
            self.team_count += 1
            self.home_adjustment = self.home.get("adjustment")
            self.home_team_id = self.home.get("teamId")
            self.home_tie_break = self.home.get("tiebreak")
            self.home_total_points = round(Decimal(self.home.get("totalPoints")), 2)

        self.id = self._data.get("id")
        self.matchup_period_id = self._data.get("matchupPeriodId")
        self.playoff_tier_type = self._data.get("playoffTierType")
        self.winner = self._data.get("winner")

        self.is_bye = self.winner == UNDECIDED and self.playoff_tier_type == WINNERS_BRACKET
        self.is_consolation = self.playoff_tier_type in CONSOLATION_LADDER
        self.is_loss = self.winner == AWAY
        self.is_pending = self.winner == UNDECIDED and self.team_count == 2
        self.is_playoffs = self.playoff_tier_type == WINNERS_BRACKET
        self.is_win = self.winner == HOME

    def __str__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def print_attributes(self):
        util.print_attributes(self._data)

    @property
    def data(self):
        return pprint.pformat(self._data)
