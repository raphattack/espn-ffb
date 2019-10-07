import argparse
from espn_ffb import util
from espn_ffb.db.database import db
from espn_ffb.db.model.matchups import Matchups
from espn_ffb.db.model.records import Records
from espn_ffb.db.model.teams import Teams
from espn_ffb.db.query import Query
from espn_ffb.espn import api
from espn_ffb.espn.model.league_setting import LeagueSetting
from flask import Flask
import logging
from typing import Mapping, Sequence, Set

app = Flask(__name__)


def parse_args() -> Mapping:
    """

    :return: dict of parsed arguments
    """
    parser = argparse.ArgumentParser(description="Update matchups, records, and teams")
    parser.add_argument('-e', '--environment', help="The development environment", type=str, required=True,
                        choices=util.SUPPORTED_ENVIRONMENTS)
    return vars(parser.parse_args())


def update(query: Query, league_settings: Sequence[LeagueSetting], year: int):
    """
    Update matchups, records, and teams for the current year.

    :param query: the query object
    :param league_settings: the league settings for the current year
    :param year: the current year
    :return: None
    """
    update_matchups(query=query, league_settings=league_settings, year=year)
    update_records_and_teams(query=query, league_settings=league_settings, year=year)


def update_matchups(query: Query, league_settings: Sequence[LeagueSetting], year: int):
    """
    Update matchups for the current year.

    :param query: the query object
    :param league_settings: the league settings for the current year
    :param year: the current year
    :return: None
    """
    matchups = set(m for m in query.get_matchups(year=year))
    current_matchups = get_current_matchups(league_settings=league_settings) - matchups

    count = len(current_matchups)
    if count == 0:
        logging.info("No matchups to update")
        return

    logging.info(f"Updating {count} matchup scores")
    query.upsert_matchups(current_matchups)


def get_current_matchups(league_settings: Sequence[LeagueSetting]) -> Set[Matchups]:
    """
    Get the current matchups for the current year from the ESPN API.

    :param league_settings: the league settings for the current year
    :return: set of matchups for the current year
    """
    current_matchups = api.get_matchups(league_settings=league_settings)
    return set(m for m in current_matchups)


def update_records_and_teams(query: Query, league_settings: Sequence[LeagueSetting], year: int):
    """
    Update records and teams for the current year.

    :param query: the query object
    :param league_settings: the league settings for the current year
    :param year: the current year
    :return: None
    """
    records = set(r for r in query.get_records(year=year))
    teams = set(t for t in query.get_teams(year=year))
    current_records, current_teams = get_current_records_and_teams(league_settings=league_settings)

    update_records(query=query, current_records=current_records, records=records)
    update_teams(query=query, current_teams=current_teams, teams=teams)


def get_current_records_and_teams(league_settings: Sequence[LeagueSetting]) -> (Set[Records], Set[Teams]):
    """
    Get the current records and teams for the current year from the ESPN API.

    :param league_settings: the league settings for the current year
    :return: tuple of a set of records and a set of teams
    """
    records, teams = api.get_records_and_teams(league_settings=league_settings)
    return set(r for r in records), set(t for t in teams)


def update_records(query: Query, current_records: Set[Records], records: Set[Records]):
    """
    Update records for the given year.

    :param query: the query object
    :param current_records: the records for the current year from the api
    :param records: the records for the current year from the db
    :return:
    """
    current_records = current_records - records

    count = len(current_records)
    if count == 0:
        logging.info("No records to update")
        return

    logging.info(f"Updating {count} records")
    query.upsert_records(current_records)


def update_teams(query: Query, current_teams: Set[Teams], teams: Set[Teams]):
    """
    Update teams for the current year.

    :param query: the query object
    :param current_teams: the teams for the current year from the api
    :param teams: the teams for the current year from the db
    :return: None
    """
    current_teams = current_teams - teams

    count = len(current_teams)
    if count == 0:
        logging.info("No teams to update")
        return

    logging.info(f"Updating {count} teams")
    query.upsert_teams(current_teams)


def main():
    args = parse_args()
    environment = args.get("environment")
    config = util.get_config(environment)
    app.config.from_object(util.get_config(environment))
    util.set_logger(config=config, filename=__file__)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get("DB_URI")
    db.init_app(app)
    query = Query(db)

    with app.app_context():
        league_settings = api.get_league_settings(config=config, years=[config.CURRENT_YEAR])
        update(query=query, league_settings=league_settings, year=config.CURRENT_YEAR)


if __name__ == "__main__":
    main()
