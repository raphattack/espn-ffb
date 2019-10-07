import argparse
from espn_ffb import util
from espn_ffb.db import create, insert
from espn_ffb.db.database import db
from flask import Flask
from typing import Mapping

app = Flask(__name__)


def parse_args() -> Mapping:
    """

    :return: dict of parsed arguments
    """
    parser = argparse.ArgumentParser(description="Create tables and insert into database.")
    parser.add_argument('-e', '--environment', help="The development environment", type=str, required=True,
                        choices=util.SUPPORTED_ENVIRONMENTS)
    return vars(parser.parse_args())


def main():
    args = parse_args()
    environment = args.get("environment")
    app.config.from_object(util.get_config(environment))

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = app.config.get("DB_URI")
    db.init_app(app)

    with app.app_context():
        create.main()
        insert.main()


if __name__ == "__main__":
    main()
