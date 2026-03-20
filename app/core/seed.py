from datetime import date, time, timedelta

from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.competition import Competition
from app.models.event import Event
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

        def get_or_create_event(
            title: str,
            event_date: date,
            event_time_utc: time,
            status: str,
            stage_name: str,
            stage_ordering: int,
            description: str,
            sport_id: int,
            competition_id: int,
            home_team_id: int | None,
            away_team_id: int,
            venue_id: int | None,
        ) -> Event:
            event = db.scalar(
                select(Event).where(
                    Event._competition_id == competition_id,
                    Event._away_team_id == away_team_id,
                    Event.event_date == event_date,
                    Event._home_team_id.is_(None) if home_team_id is None else Event._home_team_id == home_team_id,
                )
            )
            if event is None:
                event = Event(
                    title=title,
                    event_date=event_date,
                    event_time_utc=event_time_utc,
                    status=status,
                    stage_name=stage_name,
                    stage_ordering=stage_ordering,
                    description=description,
                    _sport_id=sport_id,
                    _competition_id=competition_id,
                    _home_team_id=home_team_id,
                    _away_team_id=away_team_id,
                    _venue_id=venue_id,
                )
                db.add(event)
            else:
                event.title = title
                event.event_time_utc = event_time_utc
                event.status = status
                event.stage_name = stage_name
                event.stage_ordering = stage_ordering
                event.description = description
                event._sport_id = sport_id
                event._competition_id = competition_id
                event._home_team_id = home_team_id
                event._away_team_id = away_team_id
                event._venue_id = venue_id
            return event

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

        real_madrid = get_or_create_team(
            "Real Madrid",
            "Real Madrid Club de Futbol",
            "real-madrid",
            "RMA",
            "ES",
            la_liga.id,
        )
        manchester_city = get_or_create_team(
            "Manchester City",
            "Manchester City Football Club",
            "manchester-city",
            "MCI",
            "GB",
            premier_league.id,
        )
        barcelona = get_or_create_team(
            "Barcelona",
            "Futbol Club Barcelona",
            "barcelona",
            "FCB",
            "ES",
            la_liga.id,
        )
        liverpool = get_or_create_team(
            "Liverpool",
            "Liverpool Football Club",
            "liverpool",
            "LIV",
            "GB",
            premier_league.id,
        )
        arsenal = get_or_create_team(
            "Arsenal",
            "Arsenal Football Club",
            "arsenal",
            "ARS",
            "GB",
            premier_league.id,
        )
        bayern_munich = get_or_create_team(
            "Bayern Munich",
            "FC Bayern Munich",
            "bayern-munich",
            "BAY",
            "DE",
            ucl.id,
        )
        inter_milan = get_or_create_team(
            "Inter Milan",
            "Football Club Internazionale Milano",
            "inter-milan",
            "INT",
            "IT",
            ucl.id,
        )
        psg = get_or_create_team(
            "Paris Saint-Germain",
            "Paris Saint-Germain Football Club",
            "paris-saint-germain",
            "PSG",
            "FR",
            ucl.id,
        )
        borussia_dortmund = get_or_create_team(
            "Borussia Dortmund",
            "Ballspielverein Borussia 09 e.V. Dortmund",
            "borussia-dortmund",
            "BVB",
            "DE",
            ucl.id,
        )

        lakers = get_or_create_team(
            "Los Angeles Lakers",
            "Los Angeles Lakers",
            "los-angeles-lakers",
            "LAL",
            "US",
            nba.id,
        )
        celtics = get_or_create_team(
            "Boston Celtics",
            "Boston Celtics",
            "boston-celtics",
            "BOS",
            "US",
            nba.id,
        )
        warriors = get_or_create_team(
            "Golden State Warriors",
            "Golden State Warriors",
            "golden-state-warriors",
            "GSW",
            "US",
            nba.id,
        )
        bulls = get_or_create_team(
            "Chicago Bulls",
            "Chicago Bulls",
            "chicago-bulls",
            "CHI",
            "US",
            nba.id,
        )
        real_madrid_basketball = get_or_create_team(
            "Real Madrid Basketball",
            "Real Madrid Baloncesto",
            "real-madrid-basketball",
            "RMB",
            "ES",
            euroleague.id,
        )
        fenerbahce = get_or_create_team(
            "Fenerbahce Beko",
            "Fenerbahce Beko Istanbul",
            "fenerbahce-beko",
            "FB",
            "TR",
            euroleague.id,
        )
        olympiacos = get_or_create_team(
            "Olympiacos",
            "Olympiacos B.C.",
            "olympiacos",
            "OLY",
            "GR",
            euroleague.id,
        )
        anadolu_efes = get_or_create_team(
            "Anadolu Efes",
            "Anadolu Efes S.K.",
            "anadolu-efes",
            "EFS",
            "TR",
            euroleague.id,
        )

        djokovic = get_or_create_team(
            "Novak Djokovic",
            "Novak Djokovic",
            "novak-djokovic",
            "NJD",
            "RS",
            atp_tour.id,
        )
        alcaraz = get_or_create_team(
            "Carlos Alcaraz",
            "Carlos Alcaraz",
            "carlos-alcaraz",
            "CAL",
            "ES",
            atp_tour.id,
        )
        medvedev = get_or_create_team(
            "Daniil Medvedev",
            "Daniil Medvedev",
            "daniil-medvedev",
            "DME",
            "RU",
            atp_tour.id,
        )
        sinner = get_or_create_team(
            "Jannik Sinner",
            "Jannik Sinner",
            "jannik-sinner",
            "JSI",
            "IT",
            atp_tour.id,
        )
        zverev = get_or_create_team(
            "Alexander Zverev",
            "Alexander Zverev",
            "alexander-zverev",
            "AZV",
            "DE",
            wimbledon.id,
        )
        tsitsipas = get_or_create_team(
            "Stefanos Tsitsipas",
            "Stefanos Tsitsipas",
            "stefanos-tsitsipas",
            "STS",
            "GR",
            wimbledon.id,
        )
        ruud = get_or_create_team(
            "Casper Ruud",
            "Casper Ruud",
            "casper-ruud",
            "CRU",
            "NO",
            roland_garros.id,
        )
        rune = get_or_create_team(
            "Holger Rune",
            "Holger Rune",
            "holger-rune",
            "HRU",
            "DK",
            roland_garros.id,
        )

        santiago_bernabeu = get_or_create_venue("Santiago Bernabeu", "Madrid", "ES")
        etihad = get_or_create_venue("Etihad Stadium", "Manchester", "GB")
        camp_nou = get_or_create_venue("Camp Nou", "Barcelona", "ES")
        anfield = get_or_create_venue("Anfield", "Liverpool", "GB")
        td_garden = get_or_create_venue("TD Garden", "Boston", "US")
        crypto = get_or_create_venue("Crypto.com Arena", "Los Angeles", "US")
        united_center = get_or_create_venue("United Center", "Chicago", "US")
        centre_court = get_or_create_venue("Centre Court", "London", "GB")
        chatrier = get_or_create_venue("Court Philippe-Chatrier", "Paris", "FR")

        db.flush()

        today = date.today()
        get_or_create_event(
            title="Manchester City vs Liverpool",
            event_date=today + timedelta(days=3),
            event_time_utc=time(19, 30),
            status="scheduled",
            stage_name="Matchday 28",
            stage_ordering=1,
            description="Premier League top-table clash at Etihad Stadium.",
            sport_id=football.id,
            competition_id=premier_league.id,
            home_team_id=manchester_city.id,
            away_team_id=liverpool.id,
            venue_id=etihad.id,
        )
        get_or_create_event(
            title="Barcelona vs Real Madrid",
            event_date=today + timedelta(days=6),
            event_time_utc=time(18, 0),
            status="scheduled",
            stage_name="Matchday 30",
            stage_ordering=1,
            description="El Clasico in a key La Liga title-race week.",
            sport_id=football.id,
            competition_id=la_liga.id,
            home_team_id=barcelona.id,
            away_team_id=real_madrid.id,
            venue_id=camp_nou.id,
        )
        get_or_create_event(
            title="Paris Saint-Germain vs Bayern Munich",
            event_date=today - timedelta(days=4),
            event_time_utc=time(20, 0),
            status="finished",
            stage_name="Round of 16",
            stage_ordering=1,
            description="UEFA Champions League round of 16 second leg.",
            sport_id=football.id,
            competition_id=ucl.id,
            home_team_id=psg.id,
            away_team_id=bayern_munich.id,
            venue_id=santiago_bernabeu.id,
        )
        get_or_create_event(
            title="Inter Milan vs Paris Saint-Germain",
            event_date=today - timedelta(days=8),
            event_time_utc=time(19, 0),
            status="finished",
            stage_name="Group Stage",
            stage_ordering=1,
            description="UEFA Champions League group-stage meeting.",
            sport_id=football.id,
            competition_id=ucl.id,
            home_team_id=inter_milan.id,
            away_team_id=psg.id,
            venue_id=anfield.id,
        )
        get_or_create_event(
            title="Los Angeles Lakers vs Boston Celtics",
            event_date=today + timedelta(days=2),
            event_time_utc=time(2, 30),
            status="scheduled",
            stage_name="Regular Season",
            stage_ordering=1,
            description="Classic NBA rivalry game.",
            sport_id=basketball.id,
            competition_id=nba.id,
            home_team_id=lakers.id,
            away_team_id=celtics.id,
            venue_id=crypto.id,
        )
        get_or_create_event(
            title="Golden State Warriors vs Chicago Bulls",
            event_date=today + timedelta(days=9),
            event_time_utc=time(3, 0),
            status="scheduled",
            stage_name="Regular Season",
            stage_ordering=1,
            description="Cross-conference NBA matchup in Chicago.",
            sport_id=basketball.id,
            competition_id=nba.id,
            home_team_id=warriors.id,
            away_team_id=bulls.id,
            venue_id=united_center.id,
        )
        get_or_create_event(
            title="Real Madrid Basketball vs Fenerbahce Beko",
            event_date=today - timedelta(days=3),
            event_time_utc=time(17, 0),
            status="finished",
            stage_name="Regular Season",
            stage_ordering=1,
            description="EuroLeague regular season fixture.",
            sport_id=basketball.id,
            competition_id=euroleague.id,
            home_team_id=real_madrid_basketball.id,
            away_team_id=fenerbahce.id,
            venue_id=crypto.id,
        )
        get_or_create_event(
            title="Olympiacos vs Anadolu Efes",
            event_date=today - timedelta(days=10),
            event_time_utc=time(18, 30),
            status="finished",
            stage_name="Regular Season",
            stage_ordering=1,
            description="EuroLeague defensive battle.",
            sport_id=basketball.id,
            competition_id=euroleague.id,
            home_team_id=olympiacos.id,
            away_team_id=anadolu_efes.id,
            venue_id=united_center.id,
        )
        get_or_create_event(
            title="Djokovic vs Alcaraz",
            event_date=today + timedelta(days=1),
            event_time_utc=time(13, 0),
            status="scheduled",
            stage_name="Final",
            stage_ordering=1,
            description="ATP Tour marquee final.",
            sport_id=tennis.id,
            competition_id=atp_tour.id,
            home_team_id=djokovic.id,
            away_team_id=alcaraz.id,
            venue_id=centre_court.id,
        )
        get_or_create_event(
            title="Sinner vs Medvedev",
            event_date=today + timedelta(days=5),
            event_time_utc=time(11, 30),
            status="scheduled",
            stage_name="Semi Final",
            stage_ordering=1,
            description="ATP Tour semi-final.",
            sport_id=tennis.id,
            competition_id=atp_tour.id,
            home_team_id=sinner.id,
            away_team_id=medvedev.id,
            venue_id=centre_court.id,
        )
        get_or_create_event(
            title="Zverev vs Tsitsipas",
            event_date=today - timedelta(days=2),
            event_time_utc=time(12, 0),
            status="finished",
            stage_name="Quarter Final",
            stage_ordering=1,
            description="Wimbledon quarter-final.",
            sport_id=tennis.id,
            competition_id=wimbledon.id,
            home_team_id=zverev.id,
            away_team_id=tsitsipas.id,
            venue_id=centre_court.id,
        )
        get_or_create_event(
            title="Ruud vs Rune",
            event_date=today - timedelta(days=6),
            event_time_utc=time(14, 0),
            status="finished",
            stage_name="Round of 16",
            stage_ordering=1,
            description="Roland Garros round of 16 clash.",
            sport_id=tennis.id,
            competition_id=roland_garros.id,
            home_team_id=ruud.id,
            away_team_id=rune.id,
            venue_id=chatrier.id,
        )
        get_or_create_event(
            title="Borussia Dortmund vs Arsenal",
            event_date=today + timedelta(days=12),
            event_time_utc=time(19, 45),
            status="scheduled",
            stage_name="Quarter Final",
            stage_ordering=1,
            description="UEFA Champions League knockout tie.",
            sport_id=football.id,
            competition_id=ucl.id,
            home_team_id=borussia_dortmund.id,
            away_team_id=bayern_munich.id,
            venue_id=santiago_bernabeu.id,
        )

        db.commit()
    finally:
        db.close()

