from espn_ffb.db.model.champions import Champions
from espn_ffb.db.model.matchups import Matchups
from espn_ffb.db.model.owners import Owners
from espn_ffb.db.model.records import Records
from espn_ffb.db.model.sackos import Sackos
from espn_ffb.db.model.teams import Teams
from sqlalchemy import case, desc, func
from sqlalchemy.dialects.postgresql import insert as pg_insert
from typing import Dict, List, NamedTuple, Optional, Set, Sequence


# exclude specific owners
exclude_owners = {
    "{some_owner_id}"
}


class H2HRecord(NamedTuple):
    opponent_name: str
    wins: int
    losses: int


class StandingsRecord(NamedTuple):
    owner_id: int
    wins: int
    losses: int
    ties: int
    win_percentage: float
    points_for: float
    points_against: float
    avg_points_for: float
    avg_points_against: float
    championships: float
    sackos: float


class WinLossRecord(NamedTuple):
    wins: int
    losses: int


class WinStreakRecord(NamedTuple):
    streak: int
    streak_owner: Optional[int]


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

    def get_distinct_matchup_team_ids(self, year: int) -> Dict[str, Set[int]]:
        distinct_matchup_team_ids = dict()
        matchups = self.get_matchups(year)
        for matchup in matchups:
            if matchup.matchup_id not in distinct_matchup_team_ids:
                distinct_matchup_team_ids[matchup.matchup_id] = {matchup.team_id}
            else:
                if (matchup.opponent_team_id is None) or (
                        matchup.opponent_team_id not in distinct_matchup_team_ids[matchup.matchup_id]):
                    distinct_matchup_team_ids[matchup.matchup_id].add(matchup.team_id)

        return distinct_matchup_team_ids

    def get_h2h_record_current(self, matchups: Sequence[Matchups], year: int, week: int) -> List[WinLossRecord]:
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

            h2h_record.append(WinLossRecord(wins, losses))

        return h2h_record

    def get_h2h_records(self, owner_id: int, is_playoffs: bool) -> List[H2HRecord]:
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
        losses = case([(Matchups.is_loss.is_(True), 1)], else_=0).label("losses")

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
                Matchups.opponent_owner_id.isnot(None),
                Matchups.opponent_owner_id.notin_(exclude_owners)
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

        return [H2HRecord(*r) for r in h2h_records_query]

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

    def get_owners(self, exclude: bool = False):
        if exclude:
            return self.db.session.query(Owners).filter(Owners.id.notin_(exclude_owners))
        return self.db.session.query(Owners).all()

    def get_records(self, year: Optional[int]) -> Sequence[Records]:
        """
        Select records for a given year or all years if year is None.

        :param year: the year
        :return: list of records
        """
        records_query = self.db.session.query(Records)
        if year:
            records_query = records_query.filter_by(year=year)
        return records_query.all()

    def get_playoff_matchups(self, year: Optional[int]) -> Sequence[Matchups]:
        playoff_matchups = self.db.session.query(Matchups)
        if year:
            playoff_matchups = playoff_matchups.filter_by(year=year)
        return playoff_matchups.filter(
            Matchups.opponent_owner_id.isnot(None),
            Matchups.is_playoffs.is_(True)).all()
    
    def get_sacko_current(self):
        sacko = self.db.session.query(Sackos) \
            .order_by(desc(Sackos.year)) \
            .first()
        return sacko

    def get_standings(self, year: Optional[int] = None, is_playoffs: bool = False) -> List[StandingsRecord]:
        if is_playoffs:
            return self.get_playoff_standings(year=year)
        return self.get_regular_standings(year=year)

    def get_regular_standings(self, year: Optional[int]) -> List[StandingsRecord]:
        owners = self.get_owners()
        records = self.get_records(year=year)

        standings = []
        for owner in owners:
            if not year:
                if owner.id in exclude_owners:
                    continue

            owners_records = [r for r in records if r.owner_id == owner.id]
            # Skip owner without records. Common when viewing standings for a
            # year where an owner did not participate.
            if not owners_records:
                continue

            wins = sum(r.wins for r in owners_records)
            losses = sum(r.losses for r in owners_records)
            ties = sum(r.ties for r in owners_records)
            total_games = wins + losses + ties

            points_for = sum(r.points_for for r in owners_records)
            points_against = sum(r.points_against for r in owners_records)

            avg_points_for = float(0)
            avg_points_against = float(0)
            win_percentage = float(0)
            if total_games > 0:
                win_percentage = float(f"{wins / total_games:.4f}")
                avg_points_for = float(f"{points_for / total_games:.2f}")
                avg_points_against = float(f"{points_against / total_games:.2f}")

            sackos_query = self.db.session.query(Sackos).filter_by(owner_id=owner.id)
            champions_query = self.db.session.query(Champions).filter_by(owner_id=owner.id)
            if year:
                sackos_query = sackos_query.filter_by(year=year)
                champions_query = champions_query.filter_by(year=year)

            standings.append(
                StandingsRecord(
                    owner.id,
                    wins,
                    losses,
                    ties,
                    win_percentage,
                    points_for,
                    points_against,
                    avg_points_for,
                    avg_points_against,
                    champions_query.count(),
                    sackos_query.count(),
                )
            )

        standings.sort(key=lambda x: (x.win_percentage, x.avg_points_for), reverse=True)

        return standings

    def get_playoff_standings(self, year: Optional[int]) -> List[StandingsRecord]:
        owners = self.get_owners()
        matchups = self.get_playoff_matchups(year=year)

        standings = list()
        for owner in owners:
            if not year:
                if owner.id in exclude_owners:
                    continue

            owner_matchups = [m for m in matchups if m.owner_id == owner.id]
            # Skip owner without records. Common when viewing standings for a
            # year where an owner did not participate.
            if not owner_matchups:
                continue

            wins = sum(m.is_win for m in owner_matchups)
            losses = sum(m.is_loss for m in owner_matchups)
            ties = sum(1 if m.team_score == m.opponent_team_score else 0 for m in owner_matchups)
            total_games = wins + losses + ties

            points_for = sum(m.team_score for m in owner_matchups)
            points_against = sum(m.opponent_team_score for m in owner_matchups)

            avg_points_for = float(0)
            avg_points_against = float(0)
            win_percentage = float(0)
            if total_games > 0:
                win_percentage = float(f"{wins / total_games:.4f}")
                avg_points_for = float(f"{points_for / total_games:.2f}")
                avg_points_against = float(f"{points_against / total_games:.2f}")

            sackos_query = self.db.session.query(Sackos).filter_by(owner_id=owner.id)
            champions_query = self.db.session.query(Champions).filter_by(owner_id=owner.id)
            if year:
                sackos_query = sackos_query.filter_by(year=year)
                champions_query = champions_query.filter_by(year=year)

            standings.append(
                StandingsRecord(
                    owner.id,
                    wins,
                    losses,
                    ties,
                    win_percentage,
                    points_for,
                    points_against,
                    avg_points_for,
                    avg_points_against,
                    champions_query.count(),
                    sackos_query.count(),
                )
            )

        standings.sort(key=lambda x: (x.win_percentage, x.avg_points_for), reverse=True)

        return standings

    def get_team_id_to_record(self, year: int, week: int) -> Dict[str, WinLossRecord]:
        team_id_to_record: Dict[str, WinLossRecord] = dict()
        matchups = self.get_matchups(year)
        for m in matchups:
            if m.team_id in team_id_to_record:
                r = team_id_to_record[m.team_id]
            else:
                r = WinLossRecord(0, 0)
                team_id_to_record[m.team_id] = r

            if m.matchup_id < week:
                if m.team_score > m.opponent_team_score:
                    team_id_to_record[m.team_id] = WinLossRecord(r.wins + 1, r.losses)
                if m.team_score < m.opponent_team_score:
                    team_id_to_record[m.team_id] = WinLossRecord(r.wins, r.losses + 1)

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

    def get_win_streak_by_year(self, matchups: Sequence[Matchups], year: int, week: int) -> List[WinStreakRecord]:
        win_streaks = list()
        for m in matchups:
            # noinspection DuplicatedCode
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
            win_streaks.append(WinStreakRecord(streak, streak_owner))

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
