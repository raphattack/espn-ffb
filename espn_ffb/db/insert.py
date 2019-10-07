import argparse
from espn_ffb import util
from espn_ffb.db.database import db
from espn_ffb.db.model.champions import Champions
from espn_ffb.db.model.matchups import Matchups
from espn_ffb.db.model.owners import Owners
from espn_ffb.db.model.records import Records
from espn_ffb.db.model.sackos import Sackos
from espn_ffb.db.model.teams import Teams
from espn_ffb.espn import api
from espn_ffb.espn.model.league_setting import LeagueSetting
from flask import Flask
import logging
from sqlalchemy import desc, func
from typing import Mapping, Sequence

app = Flask(__name__)


def parse_args() -> Mapping:
    """

    :return: dict of parsed arguments
    """
    parser = argparse.ArgumentParser(description="Create tables and insert into database.")
    parser.add_argument('-e', '--environment', help="The development environment", type=str, required=True,
                        choices=util.SUPPORTED_ENVIRONMENTS)
    return vars(parser.parse_args())


def truncate_tables():
    logging.info("Truncating tables")
    db.session.query(Champions).delete()
    db.session.query(Matchups).delete()
    db.session.query(Owners).delete()
    db.session.query(Records).delete()
    db.session.query(Sackos).delete()
    db.session.query(Teams).delete()
    db.session.commit()


def insert_owners(league_settings: Sequence[LeagueSetting]):
    """
    Insert owners for the given league settings.

    :param league_settings: list of league settings
    :return: None
    """
    logging.info("Inserting owners")
    owners = api.get_owners(league_settings)
    db.session.bulk_save_objects(owners.values())
    db.session.commit()


def insert_records_and_teams(league_settings: Sequence[LeagueSetting]):
    """
    Insert records and teams for the given league settings.

    :param league_settings: list of league settings
    :return: None
    """
    logging.info("Inserting records and teams")
    records, teams = api.get_records_and_teams(league_settings)
    db.session.bulk_save_objects(records)
    db.session.bulk_save_objects(teams)
    db.session.commit()


def insert_matchups(league_settings: Sequence[LeagueSetting]):
    """
    Insert matchups for the given years.

    :param league_settings: list of league settings
    :return: None
    """
    logging.info("Inserting matchups")
    matchups = api.get_matchups(league_settings)
    db.session.bulk_save_objects(matchups)
    db.session.commit()


def insert_champions():
    """
    Insert championships.

    :return: None
    """
    logging.info("Inserting champions")
    champions = get_champions()
    db.session.bulk_save_objects(champions)
    db.session.commit()


def get_champions():
    """
    Select championships.

    :return: list of championships
    """
    subquery = db.session.query(Matchups, func.row_number().over(
        partition_by=Matchups.year,
        order_by=desc(Matchups.matchup_id)
    ).label("row_number"))
    subquery = subquery.filter(Matchups.is_playoffs.is_(True)).subquery()
    matchups = db.session.query(subquery).filter(subquery.c.row_number == 1).all()

    champions = list()
    for m in matchups:
        if m.is_win:
            champions.append(Champions(year=m.year, owner_id=m.owner_id))
        else:
            champions.append(Champions(year=m.year, owner_id=m.opponent_owner_id))
    return champions


def insert_sackos():
    logging.info("Inserting sackos")
    sackos = list()
    # sackos.append(Sackos(year=2018, owner_id="{some_owner_id}"))
    db.session.bulk_save_objects(sackos)
    db.session.commit()


def main():
    args = parse_args()
    environment = args.get("environment")
    config = util.get_config(environment)
    app.config.from_object(util.get_config(environment))

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get("DB_URI")
    db.init_app(app)

    with app.app_context():
        truncate_tables()

        years = api.get_league_years(config)
        league_settings = api.get_league_settings(config, years)
        insert_owners(league_settings)
        insert_records_and_teams(league_settings)
        insert_matchups(league_settings)
        insert_champions()
        insert_sackos()


if __name__ == "__main__":
    main()
