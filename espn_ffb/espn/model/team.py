from espn_ffb import util
from espn_ffb.espn.model.record import Record
import pprint
from typing import Mapping


class Team:
    def __init__(self, data: Mapping):
        """
        Initialize team for a given dict.

        :param data: dict of team attributes to values
        """
        self._data = data

        self.abbrev = self._data.get("abbrev")
        self.current_projected_rank = self._data.get("currentProjectedRank")
        self.division_id = self._data.get("divisionId")
        self.draft_day_projected_rank = self._data.get("draftDayProjectedRank")
        self.draft_strategy = self._data.get("draftStrategy")
        self.id = self._data.get("id")
        self.is_active = self._data.get("isActive")
        self.location = self._data.get("location")
        self.logo = self._data.get("logo")
        self.logo_type = self._data.get("logoType")
        self.nickname = self._data.get("nickname")
        self.owners = self._data.get("owners")
        self.playoff_seed = self._data.get("playoffSeed")
        self.points = self._data.get("points")
        self.points_adjusted = self._data.get("pointsAdjusted")
        self.points_delta = self._data.get("pointsDelta")
        self.primary_owner = self._data.get("primaryOwner")
        self.standing = self._data.get("rankCalculatedFinal")
        self.rank_final = self._data.get("rankFinal")
        self.record = Record(self._data.get("record").get("overall"))
        self.trade_block = self._data.get("tradeBlock")
        self.transaction_counter = self._data.get("transactionCounter")
        self.values_by_stat = self._data.get("valuesByStat")
        self.waiver_rank = self._data.get("waiverRank")

    def __str__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def print_attributes(self):
        util.print_attributes(self._data)

    @property
    def data(self):
        return pprint.pformat(self._data)
