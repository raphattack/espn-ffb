from espn_ffb import util


class LeagueMember:
    def __init__(self, json):
        self.json = json

        self.first_name = self.json.get("firstName")
        self.last_name = self.json.get("lastName")
        self.is_league_creator = self.json.get("isLeagueCreator")
        self.invite_id = self.json.get("inviteId")
        self.user_profile_id = self.json.get("userProfileId")
        self.is_league_manager = self.json.get("isLeagueManager")
        self.username = self.json.get("userName")

    def print_attributes(self):
        util.print_attributes(self.json)
