from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.competition import Competition
from app.models.sport import Sport
from app.models.team import Team
from app.models.venue import Venue


def seed_sample_data_if_empty() -> None:
    db = SessionLocal()
    try:
        def get_or_create_sport(name: str) -> Sport:
            sport = db.scalar(select(Sport).where(Sport.name == name))
            if sport is None:
                sport = Sport(name=name)
                db.add(sport)
                db.flush()
            return sport

        def get_or_create_competition(external_id: str, name: str, season: str, sport_id: int) -> Competition:
            competition = db.scalar(
                select(Competition).where(
                    Competition.external_id == external_id,
                    Competition.season == season,
                )
            )
            if competition is None:
                competition = Competition(
                    external_id=external_id,
                    name=name,
                    season=season,
                    _sport_id=sport_id,
                )
                db.add(competition)
                db.flush()
            else:
                competition.name = name
                competition._sport_id = sport_id
            return competition

        def get_or_create_team(
            name: str,
            official_name: str,
            slug: str,
            abbreviation: str,
            country_code: str,
            competition_id: int,
        ) -> Team:
            team = db.scalar(select(Team).where(Team.slug == slug))
            if team is None:
                team = Team(
                    name=name,
                    official_name=official_name,
                    slug=slug,
                    abbreviation=abbreviation,
                    country_code=country_code,
                    _competition_id=competition_id,
                )
                db.add(team)
            else:
                team.name = name
                team.official_name = official_name
                team.abbreviation = abbreviation
                team.country_code = country_code
                team._competition_id = competition_id
            return team

        def get_or_create_venue(name: str, city: str, country_code: str) -> Venue:
            venue = db.scalar(select(Venue).where(Venue.name == name))
            if venue is None:
                venue = Venue(name=name, city=city, country_code=country_code)
                db.add(venue)
            return venue

        football = get_or_create_sport("Football")
        basketball = get_or_create_sport("Basketball")
        tennis = get_or_create_sport("Tennis")

        ucl = get_or_create_competition("UCL", "UEFA Champions League", "2025/26", football.id)
        premier_league = get_or_create_competition("EPL", "Premier League", "2025/26", football.id)
        la_liga = get_or_create_competition("LL", "La Liga", "2025/26", football.id)

        nba = get_or_create_competition("NBA", "NBA", "2025/26", basketball.id)
        euroleague = get_or_create_competition("EL", "EuroLeague", "2025/26", basketball.id)

        atp_tour = get_or_create_competition("ATP", "ATP Tour", "2025", tennis.id)
        wimbledon = get_or_create_competition("WIM", "Wimbledon", "2025", tennis.id)
        roland_garros = get_or_create_competition("RG", "Roland Garros", "2025", tennis.id)

        get_or_create_team(
            "Real Madrid",
            "Real Madrid Club de Futbol",
            "real-madrid",
            "RMA",
            "ES",
            la_liga.id,
        )
        get_or_create_team(
            "Manchester City",
            "Manchester City Football Club",
            "manchester-city",
            "MCI",
            "GB",
            premier_league.id,
        )
        get_or_create_team(
            "Barcelona",
            "Futbol Club Barcelona",
            "barcelona",
            "FCB",
            "ES",
            la_liga.id,
        )
        get_or_create_team(
            "Liverpool",
            "Liverpool Football Club",
            "liverpool",
            "LIV",
            "GB",
            premier_league.id,
        )
        get_or_create_team(
            "Arsenal",
            "Arsenal Football Club",
            "arsenal",
            "ARS",
            "GB",
            premier_league.id,
        )
        get_or_create_team(
            "Bayern Munich",
            "FC Bayern Munich",
            "bayern-munich",
            "BAY",
            "DE",
            ucl.id,
        )
        get_or_create_team(
            "Inter Milan",
            "Football Club Internazionale Milano",
            "inter-milan",
            "INT",
            "IT",
            ucl.id,
        )
        get_or_create_team(
            "Paris Saint-Germain",
            "Paris Saint-Germain Football Club",
            "paris-saint-germain",
            "PSG",
            "FR",
            ucl.id,
        )
        get_or_create_team(
            "Borussia Dortmund",
            "Ballspielverein Borussia 09 e.V. Dortmund",
            "borussia-dortmund",
            "BVB",
            "DE",
            ucl.id,
        )

        get_or_create_team(
            "Los Angeles Lakers",
            "Los Angeles Lakers",
            "los-angeles-lakers",
            "LAL",
            "US",
            nba.id,
        )
        get_or_create_team(
            "Boston Celtics",
            "Boston Celtics",
            "boston-celtics",
            "BOS",
            "US",
            nba.id,
        )
        get_or_create_team(
            "Golden State Warriors",
            "Golden State Warriors",
            "golden-state-warriors",
            "GSW",
            "US",
            nba.id,
        )
        get_or_create_team(
            "Chicago Bulls",
            "Chicago Bulls",
            "chicago-bulls",
            "CHI",
            "US",
            nba.id,
        )
        get_or_create_team(
            "Real Madrid Basketball",
            "Real Madrid Baloncesto",
            "real-madrid-basketball",
            "RMB",
            "ES",
            euroleague.id,
        )
        get_or_create_team(
            "Fenerbahce Beko",
            "Fenerbahce Beko Istanbul",
            "fenerbahce-beko",
            "FB",
            "TR",
            euroleague.id,
        )
        get_or_create_team(
            "Olympiacos",
            "Olympiacos B.C.",
            "olympiacos",
            "OLY",
            "GR",
            euroleague.id,
        )
        get_or_create_team(
            "Anadolu Efes",
            "Anadolu Efes S.K.",
            "anadolu-efes",
            "EFS",
            "TR",
            euroleague.id,
        )

        get_or_create_team(
            "Novak Djokovic",
            "Novak Djokovic",
            "novak-djokovic",
            "NJD",
            "RS",
            atp_tour.id,
        )
        get_or_create_team(
            "Carlos Alcaraz",
            "Carlos Alcaraz",
            "carlos-alcaraz",
            "CAL",
            "ES",
            atp_tour.id,
        )
        get_or_create_team(
            "Daniil Medvedev",
            "Daniil Medvedev",
            "daniil-medvedev",
            "DME",
            "RU",
            atp_tour.id,
        )
        get_or_create_team(
            "Jannik Sinner",
            "Jannik Sinner",
            "jannik-sinner",
            "JSI",
            "IT",
            atp_tour.id,
        )
        get_or_create_team(
            "Alexander Zverev",
            "Alexander Zverev",
            "alexander-zverev",
            "AZV",
            "DE",
            wimbledon.id,
        )
        get_or_create_team(
            "Stefanos Tsitsipas",
            "Stefanos Tsitsipas",
            "stefanos-tsitsipas",
            "STS",
            "GR",
            wimbledon.id,
        )
        get_or_create_team(
            "Casper Ruud",
            "Casper Ruud",
            "casper-ruud",
            "CRU",
            "NO",
            roland_garros.id,
        )
        get_or_create_team(
            "Holger Rune",
            "Holger Rune",
            "holger-rune",
            "HRU",
            "DK",
            roland_garros.id,
        )

        get_or_create_venue("Santiago Bernabeu", "Madrid", "ES")
        get_or_create_venue("Etihad Stadium", "Manchester", "GB")
        get_or_create_venue("Camp Nou", "Barcelona", "ES")
        get_or_create_venue("Anfield", "Liverpool", "GB")
        get_or_create_venue("TD Garden", "Boston", "US")
        get_or_create_venue("Crypto.com Arena", "Los Angeles", "US")
        get_or_create_venue("United Center", "Chicago", "US")
        get_or_create_venue("Centre Court", "London", "GB")
        get_or_create_venue("Court Philippe-Chatrier", "Paris", "FR")

        db.commit()
    finally:
        db.close()

