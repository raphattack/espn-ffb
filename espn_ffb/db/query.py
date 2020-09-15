from collections import namedtuple
from espn_ffb.db.model.champions import Champions
from espn_ffb.db.model.matchups import Matchups
from espn_ffb.db.model.owners import Owners
from espn_ffb.db.model.records import Records
from espn_ffb.db.model.sackos import Sackos
from espn_ffb.db.model.teams import Teams
from sqlalchemy import case, desc, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import Sequence


class Query:
    def __init__(self, db):
        self.db = db

    def get_champions(self):
        """
        Select champions.

        :return: list of champions
        """
        champions = self.db.session.query(Champions, Owners) \
            .join(Owners, Champions.owner_id == Owners.id) \
            .order_by(desc(Champions.year)) \
            .all()

        return champions

    def get_distinct_matchup_team_ids(self, year: int):
        distinct_matchup_team_ids = dict()
        matchups = self.get_matchups(year)
        for matchup in matchups:
            if matchup.matchup_id not in distinct_matchup_team_ids:
                distinct_matchup_team_ids[matchup.matchup_id] = {matchup.team_id}
            else:
                if (matchup.opponent_team_id is None) or (
                        matchup.opponent_team_id not in distinct_matchup_team_ids.get(matchup.matchup_id)):
                    distinct_matchup_team_ids[matchup.matchup_id].add(matchup.team_id)

        return distinct_matchup_team_ids

    def get_h2h_record_current(self, matchups, year, week):
        Record = namedtuple('Record', ['wins', 'losses'])
        h2h_record = list()
        for m in matchups:
            wins, losses = 0, 0
            h2h_history = [h2h for h2h in self.get_matchup_history(m.owner_id, m.opponent_owner_id, False) if
                           not (h2h.year == year and h2h.matchup_id == week)]

            for h2h in h2h_history:
                if h2h.is_win:
                    wins += 1
                else:
                    losses += 1

            h2h_record.append(Record(wins, losses))

        return h2h_record

    def get_h2h_records(self, owner_id, is_playoffs):
        COLUMN_NAMES = ['opponent_name', 'wins', 'losses']
        Record = namedtuple('H2HRecord', COLUMN_NAMES)

        full_name_concat = func.CONCAT(Owners.first_name, ' ', Owners.last_name)

        owner_name = (
          self.db.session.query(full_name_concat)
          .filter(Owners.id == Matchups.owner_id)
          .label("owner_name")
        )

        opponent_name = (
          self.db.session.query(full_name_concat)
          .filter(Owners.id == Matchups.opponent_owner_id)
          .label("opponent_name")
        )

        wins = case([(Matchups.is_win.is_(True), 1)], else_=0).label("wins")

        losses = case(
          [(Matchups.is_loss.is_(True), 1)], else_=0
        ).label("losses")

        columns = [
            Matchups.year,
            Matchups.matchup_id,
            owner_name,
            Matchups.owner_id,
            opponent_name,
            Matchups.opponent_owner_id,
            wins,
            losses,
        ]

        record_subquery = (
          self.db.session.query(*columns).filter_by(
            owner_id=owner_id,
            is_playoffs=is_playoffs,
            is_pending=False,
            is_consolation=False,
          )
          .filter(
            Matchups.opponent_owner_id.isnot(None)
          )
          .group_by(*columns)
          .subquery()
        )

        h2h_records_query = (
          self.db.session.query(
            record_subquery.c.opponent_name,
            func.sum(record_subquery.c.wins).label("wins"),
            func.sum(record_subquery.c.losses).label("losses"),
          )
          .group_by(record_subquery.c.opponent_name)
          .order_by(record_subquery.c.opponent_name)
        )

        return [Record(*r) for r in h2h_records_query]

    def get_matchup_history(self, owner_id, opponent_owner_id, is_playoffs):
        matchups = self.db.session.query(Matchups) \
            .filter_by(owner_id=owner_id,
                       opponent_owner_id=opponent_owner_id,
                       is_playoffs=is_playoffs,
                       is_pending=False,
                       is_consolation=False) \
            .order_by(desc(Matchups.year), Matchups.matchup_id) \
            .all()
        return matchups

    def get_matchups(self, year: int) -> Sequence[Matchups]:
        """
        Select matchups for a given year.

        :param year: the year
        :return: list of matchups
        """
        matchups = self.db.session.query(Matchups) \
            .filter_by(year=year) \
            .order_by(Matchups.matchup_id, Matchups.team_id) \
            .all()
        return matchups

    def get_owners(self):
        return self.db.session.query(Owners).all()

    def get_records(self, year: int) -> Sequence[Records]:
        """
        Select records for a given year.

        :param year: the year
        :return: list of records
        """
        records = self.db.session.query(Records).filter_by(year=year).all()
        return records

    def get_sacko_current(self):
        sacko = self.db.session.query(Sackos) \
            .order_by(desc(Sackos.year)) \
            .first()
        return sacko

    def get_standings(self, year: int):
        COLUMN_NAMES = ["owner_id", "wins", "losses", "win_percentage", "points_for", "points_against", "avg_points_for",
                        "avg_points_against", "championships", "sackos"]
        Record = namedtuple('Standings', COLUMN_NAMES)

        query = f"""
        select 
          r.owner_id as owner_id,
          r.wins as wins,
          r.losses as losses,
          case 
            when (r.wins + r.losses) = 0 
              then 0 
            else 
              round(r.wins::decimal/(r.wins + r.losses) , 4) 
          end as win_percentage,
          r.points_for as points_for,
          r.points_against as points_against,
          case 
            when (r.wins + r.losses) = 0 
              then 0 
            else 
              round(r.points_for/(r.wins + r.losses), 2) 
          end as avg_points_for,
          case 
            when (r.wins + r.losses) = 0 
              then 0 
            else 
              round(r.points_against/(r.wins + r.losses), 2) 
          end as avg_points_against,
          (select count(1) from champions where owner_id = r.owner_id and year = r.year) as championships,
          (select count(1) from sackos where owner_id = r.owner_id and year = r.year) as sackos
        from 
          records r
        where 
          r.year = {year}
        group by
          r.year,
          r.owner_id,
          r.wins,
          r.losses,
          r.points_for,
          r.points_against
        order by
          win_percentage desc,
          points_for desc
        """

        return [Record(**r) for r in self.db.engine.execute(query)]

    def get_standings_overall(self):
        COLUMN_NAMES = ["owner_id", "wins", "losses", "win_percentage", "points_for", "points_against", "avg_points_for",
                        "avg_points_against", "championships", "sackos"]
        Record = namedtuple('Standings', COLUMN_NAMES)

        query = f"""
        select
          r.owner_id as owner_id,
          sum(r.wins) as wins,
          sum(r.losses) as losses,
          case 
            when (sum(r.wins) + sum(r.losses)) = 0 
              then 0 
            else 
              round(sum(r.wins)::decimal/(sum(r.wins) + sum(r.losses)) , 4) 
          end as win_percentage,
          sum(r.points_for) as points_for,
          sum(r.points_against) as points_against,
          case 
            when (sum(r.wins) + sum(r.losses)) = 0 
              then 0 
            else 
              round(sum(r.points_for)/(sum(r.wins) + sum(r.losses)), 2) 
          end as avg_points_for,
          case 
            when (sum(r.wins) + sum(r.losses)) = 0 
              then 0 
            else 
              round(sum(r.points_against)/(sum(r.wins) + sum(r.losses)), 2) 
          end as avg_points_against,
          (select count(1) from champions where owner_id = r.owner_id) as championships,
          (select count(1) from sackos where owner_id = r.owner_id) as sackos
        from
          records r
        group by
          r.owner_id
        order by
          win_percentage desc,
          avg_points_for desc
        """

        return [Record(**r) for r in self.db.engine.execute(query)]

    def get_team_id_to_record(self, year, week):
        team_id_to_record = dict()
        Record = namedtuple('Record', ['wins', 'losses'])
        matchups = self.get_matchups(year)
        for m in matchups:
            if m.team_id in team_id_to_record:
                r = team_id_to_record.get(m.team_id)
            else:
                r = Record(0, 0)
                team_id_to_record[m.team_id] = r

            if m.matchup_id < week:
                if m.team_score > m.opponent_team_score:
                    team_id_to_record[m.team_id] = Record(r.wins + 1, r.losses)
                if m.team_score < m.opponent_team_score:
                    team_id_to_record[m.team_id] = Record(r.wins, r.losses + 1)

        return team_id_to_record

    def get_team_id_to_team_name(self, year):
        records = self.get_teams(year)
        return dict((record.id, record.location + " " + record.nickname) for record in records)

    def get_teams(self, year: int):
        """
        Select teams for a given year.

        :param year: the year
        :return: list of teams
        """
        teams = self.db.session.query(Teams).filter_by(year=year).all()
        return teams

    def get_win_streak_by_year(self, matchups, year, week):
        win_streaks = list()
        WinStreak = namedtuple('WinStreak', ['streak', 'streak_owner'])

        for m in matchups:
            streak, streak_owner, streak_type = 0, None, None
            h2h_history = [h2h for h2h in self.get_matchup_history(m.owner_id, m.opponent_owner_id, False) if
                           not (h2h.year == year and h2h.matchup_id == week)]

            for h2h in h2h_history:
                if streak == 0:
                    streak_type = h2h.is_win
                    streak_owner = m.team_id if streak_type else m.opponent_team_id

                if h2h.is_win != streak_type:
                    streak_owner = m.team_id if streak_type else m.opponent_team_id
                    break

                streak += 1
            win_streaks.append(WinStreak(streak, streak_owner))

        return win_streaks

    def get_distinct_years(self):
      distinct_matchup_years = (
        self.db.session.query(Matchups.year)
        .distinct(Matchups.year)
        .order_by(Matchups.year.desc())
      )

      return [matchup.year for matchup in distinct_matchup_years]

    def upsert_matchups(self, matchups):
        for m in matchups:
            statement = pg_insert(Matchups) \
                .values(**m.as_dict()) \
                .on_conflict_do_update(constraint=Matchups.PKEY_NAME, set_=m.props_dict())
            self.db.session.execute(statement)
        self.db.session.commit()

    def upsert_records(self, records):
        for record in records:
            statement = pg_insert(Records) \
                .values(**record.as_dict()) \
                .on_conflict_do_update(constraint=Records.PKEY_NAME, set_=record.props_dict())
            self.db.session.execute(statement)
        self.db.session.commit()

    def upsert_teams(self, teams):
        for team in teams:
            statement = pg_insert(Teams) \
                .values(**team.as_dict()) \
                .on_conflict_do_update(constraint=Teams.PKEY_NAME, set_=team.props_dict())
            self.db.session.execute(statement)
        self.db.session.commit()
