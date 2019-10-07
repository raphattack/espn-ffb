from decimal import Decimal
from espn_ffb import util
import pprint
from typing import Mapping


class Record:
    def __init__(self, data: Mapping):
        """
        Initialize record for a given dict.

        :param data: dict of record attributes to values
        """
        self._data = data

        self.losses = self._data.get("losses")
        self.points_against = round(Decimal(self._data.get("pointsAgainst")), 2)
        self.points_for = round(Decimal(self._data.get("pointsFor")), 2)
        self.streak_length = self._data.get("streakLength")
        self.streak_type = self._data.get("streakType")
        self.ties = self._data.get("ties")
        self.wins = self._data.get("wins")

    def __str__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def print_attributes(self):
        util.print_attributes(self._data)

    @property
    def data(self):
        return pprint.pformat(self._data)
