from espn_ffb.config import Config, DevConfig, DockerConfig, ProdConfig
from collections import namedtuple
import logging.handlers
import os
import re
from typing import Type

REGULAR_SEASON = "regular"
SUPPORTED_ENVIRONMENTS = {"dev", "docker", "prod"}
Recap = namedtuple('Recap', ['team', 'team_record', 'opponent', 'opponent_record', 'streak', 'streak_owner',
                             'h2h_record', 'body'])


def get_is_playoffs(matchup_type):
    if matchup_type == REGULAR_SEASON:
        return False

    return True


def get_is_current_year(current_year: int, season_id: int):
    return season_id == current_year


def get_config(environment) -> Type[Config]:
    """
    Get a config object for a given environment.

    :param environment: the development environment
    :return: the config object
    """
    if environment == "dev":
        return DevConfig
    elif environment == "docker":
        return DockerConfig
    elif environment == "prod":
        return ProdConfig


def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def set_logger(config: Type[Config], filename: str) -> None:
    script_name = os.path.basename(filename).replace(".py", "")

    rootlogger = logging.getLogger()
    rootlogger.setLevel(config.rootlogger_level)
    formatter = logging.Formatter(config.log_format)

    filelog = logging.handlers.TimedRotatingFileHandler(
        os.path.join(config.log_base_dir, f"{script_name}.log"),
        when=config.log_when,
        interval=config.log_interval,
        backupCount=config.log_backup_count
    )
    filelog.setLevel(config.filelog_level)
    filelog.setFormatter(formatter)
    rootlogger.addHandler(filelog)

    console = logging.StreamHandler()
    console.setLevel(config.console_level)
    console.setFormatter(formatter)
    rootlogger.addHandler(console)


def print_attributes(json):
    for k, v in json.items():
        print("self." + convert(k) + " = self._json.get(\"" + k + "\")")
