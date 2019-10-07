from espn_ffb import util
import pprint
from typing import Mapping


class Member:
    def __init__(self, data: Mapping):
        """
        Initialize member for a given dict.

        :param data: dict of member attributes to values
        """
        self._data = data

        self.id = self._data.get("id")
        self.username = self._data.get("displayName")
        self.first_name = self._data.get("firstName")
        self.last_name = self._data.get("lastName")

    def __str__(self):
        return ', '.join("%s: %s" % item for item in vars(self).items() if "_json" not in item)

    def print_attributes(self):
        util.print_attributes(self._data)

    @property
    def data(self):
        return pprint.pformat(self._data)
