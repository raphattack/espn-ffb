from espn_ffb.config import Config
from espn_ffb.db.model.matchups import Matchups
from espn_ffb.db.model.owners import Owners
from espn_ffb.db.model.records import Records
from espn_ffb.db.model.teams import Teams
from espn_ffb.espn.model.league_setting import LeagueSetting
from espn_ffb.espn.model.matchup_score import MatchupScore
import logging
import requests
from typing import List, Mapping, Sequence, Type


def get_league_years(config: Type[Config]) -> Sequence[int]:
    """
    Get previous league years.

    :param config: the config object
    :return: list of previous league years
    """
    league_office_url = f"https://fantasy.espn.com/apis/v3/games/FFL/seasons/{config.CURRENT_YEAR}/segments/0/leagues" \
                        f"/{config.LEAGUE_ID}?view=mSettings"
    data = requests.get(league_office_url, cookies=config.COOKIES).json()
    years = data.get("status").get("previousSeasons")
    years.append(config.CURRENT_YEAR)
    return years


def get_league_settings(config: Type[Config], years: Sequence[int]) -> Sequence[LeagueSetting]:
    """
    Get league settings for the given years.

    :param config: the config object
    :param years: list of previous league years
    :return: list of league settings
    """
    return [LeagueSetting(config=config, year=year) for year in years]


def get_matchups(league_settings: Sequence[LeagueSetting]) -> Sequence[Matchups]:
    """
    Get matchups for the given years.

    :param league_settings: list of league settings
    :return: list of matchups
    """
    matchups = list()
    for league_setting in league_settings:
        team_id_to_owner_ids = get_team_id_to_owner_id(league_setting.season_id)
        for matchup_score in league_setting.matchup_scores:
            add_matchups(league_setting=league_setting, matchups=matchups, matchup_score=matchup_score,
                         team_id_to_owner_ids=team_id_to_owner_ids)

    return matchups


def add_matchups(league_setting: LeagueSetting, matchups: List[Matchups], matchup_score: MatchupScore,
                 team_id_to_owner_ids: Mapping[int, List[str]]):
    """
    Add two matchups for each matchup score, switching the home and away team attributes.

    :param league_setting: the league setting
    :param matchups: list of matchups
    :param matchup_score: the matchup score
    :param team_id_to_owner_ids: dict of team ID to owner IDs
    :return: None
    """
    owner_id = team_id_to_owner_ids.get(matchup_score.home_team_id)
    opponent_owner_id = team_id_to_owner_ids.get(matchup_score.away_team_id)

    matchups.append(Matchups(year=league_setting.season_id,
                             matchup_id=matchup_score.matchup_period_id,
                             team_id=matchup_score.home_team_id,
                             owner_id=owner_id,
                             opponent_team_id=matchup_score.away_team_id,
                             opponent_owner_id=opponent_owner_id,
                             team_score=matchup_score.home_total_points,
                             opponent_team_score=matchup_score.away_total_points,
                             is_win=matchup_score.is_win,
                             is_loss=matchup_score.is_loss,
                             is_pending=matchup_score.is_pending,
                             is_bye=matchup_score.is_bye,
                             is_playoffs=matchup_score.is_playoffs,
                             is_consolation=matchup_score.is_consolation))

    if matchup_score.team_count > 1:
        matchups.append(Matchups(year=league_setting.season_id,
                                 matchup_id=matchup_score.matchup_period_id,
                                 team_id=matchup_score.away_team_id,
                                 owner_id=opponent_owner_id,
                                 opponent_team_id=matchup_score.home_team_id,
                                 opponent_owner_id=owner_id,
                                 team_score=matchup_score.away_total_points,
                                 opponent_team_score=matchup_score.home_total_points,
                                 is_win=matchup_score.is_loss,
                                 is_loss=matchup_score.is_win,
                                 is_pending=matchup_score.is_pending,
                                 is_bye=matchup_score.is_bye,
                                 is_playoffs=matchup_score.is_playoffs,
                                 is_consolation=matchup_score.is_consolation))


def get_owners(league_settings: Sequence[LeagueSetting]) -> Mapping[str, Owners]:
    """
    Get owners for the given league settings.

    :param league_settings: list of league settings
    :return: list of owners
    """
    owners = dict()
    for l in league_settings:
        for member in l.members:
            if member.username not in owners:
                owners[member.username] = Owners(id=member.id,
                                                 username=member.username,
                                                 first_name=member.first_name,
                                                 last_name=member.last_name)
    return owners


def get_team_id_to_owner_id(year: int):
    """
    Get a dict of team ID to owner IDs.

    :param year: the year
    :return: dict of team ID to owner IDs
    """
    teams = Teams.query.filter_by(year=year).all()
    return dict((team.id, team.owner_id) for team in teams)


def get_records_and_teams(league_settings: Sequence[LeagueSetting]) -> (Sequence[Records], Sequence[Teams]):
    """
    Get records and teams for the given league settings.

    :param league_settings: list of league settings
    :return: tuple of records and teams
    """
    teams = list()
    records = list()

    for l in league_settings:
        for team in l.teams:
            record = team.record
            records.append(Records(year=l.season_id,
                                   team_id=team.id,
                                   owner_id=team.primary_owner,
                                   standing=team.standing,
                                   wins=record.wins,
                                   losses=record.losses,
                                   ties=record.ties,
                                   points_for=round(record.points_for, 2),
                                   points_against=round(record.points_against, 2),
                                   streak_length=record.streak_length,
                                   streak_type=record.streak_type))
            teams.append(Teams(year=l.season_id,
                               id=team.id,
                               owner_id=team.primary_owner,
                               abbreviation=team.abbrev,
                               location=team.location,
                               nickname=team.nickname))

    return records, teams
