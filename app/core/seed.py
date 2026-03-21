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
            else:
                venue.city = city
                venue.country_code = country_code
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

        sports = {
            "football": get_or_create_sport("Football"),
            "basketball": get_or_create_sport("Basketball"),
            "tennis": get_or_create_sport("Tennis"),
            "f1": get_or_create_sport("Formula 1"),
            "mma": get_or_create_sport("MMA"),
        }

        competitions = {
            "ucl": get_or_create_competition("UCL", "UEFA Champions League", "2025/26", sports["football"].id),
            "epl": get_or_create_competition("EPL", "Premier League", "2025/26", sports["football"].id),
            "laliga": get_or_create_competition("LL", "La Liga", "2025/26", sports["football"].id),
            "seriea": get_or_create_competition("SA", "Serie A", "2025/26", sports["football"].id),
            "nba": get_or_create_competition("NBA", "NBA", "2025/26", sports["basketball"].id),
            "euroleague": get_or_create_competition("EL", "EuroLeague", "2025/26", sports["basketball"].id),
            "atp": get_or_create_competition("ATP", "ATP Tour", "2025", sports["tennis"].id),
            "wimbledon": get_or_create_competition("WIM", "Wimbledon", "2025", sports["tennis"].id),
            "rg": get_or_create_competition("RG", "Roland Garros", "2025", sports["tennis"].id),
            "usopen": get_or_create_competition("USO", "US Open", "2025", sports["tennis"].id),
            "f1wc": get_or_create_competition("F1WC", "Formula 1 World Championship", "2025", sports["f1"].id),
            "ufc": get_or_create_competition("UFC", "UFC", "2025", sports["mma"].id),
            "pfl": get_or_create_competition("PFL", "Professional Fighters League", "2025", sports["mma"].id),
        }

        team_specs = [
            ("Real Madrid", "Real Madrid Club de Futbol", "real-madrid", "RMA", "ES", "laliga"),
            ("Barcelona", "Futbol Club Barcelona", "barcelona", "BAR", "ES", "laliga"),
            ("Manchester City", "Manchester City Football Club", "manchester-city", "MCI", "GB", "epl"),
            ("Liverpool", "Liverpool Football Club", "liverpool", "LIV", "GB", "epl"),
            ("Arsenal", "Arsenal Football Club", "arsenal", "ARS", "GB", "epl"),
            ("Bayern Munich", "FC Bayern Munich", "bayern-munich", "BAY", "DE", "ucl"),
            ("Inter Milan", "Football Club Internazionale Milano", "inter-milan", "INT", "IT", "seriea"),
            ("Paris Saint-Germain", "Paris Saint-Germain Football Club", "paris-saint-germain", "PSG", "FR", "ucl"),
            ("Borussia Dortmund", "Ballspielverein Borussia 09 Dortmund", "borussia-dortmund", "BVB", "DE", "ucl"),
            ("Juventus", "Juventus Football Club", "juventus", "JUV", "IT", "seriea"),
            ("Los Angeles Lakers", "Los Angeles Lakers", "los-angeles-lakers", "LAL", "US", "nba"),
            ("Boston Celtics", "Boston Celtics", "boston-celtics", "BOS", "US", "nba"),
            ("Golden State Warriors", "Golden State Warriors", "golden-state-warriors", "GSW", "US", "nba"),
            ("Chicago Bulls", "Chicago Bulls", "chicago-bulls", "CHI", "US", "nba"),
            ("Miami Heat", "Miami Heat", "miami-heat", "MIA", "US", "nba"),
            ("Milwaukee Bucks", "Milwaukee Bucks", "milwaukee-bucks", "MIL", "US", "nba"),
            ("Real Madrid Basketball", "Real Madrid Baloncesto", "real-madrid-basketball", "RMB", "ES", "euroleague"),
            ("Fenerbahce Beko", "Fenerbahce Beko Istanbul", "fenerbahce-beko", "FB", "TR", "euroleague"),
            ("Anadolu Efes", "Anadolu Efes S.K.", "anadolu-efes", "EFS", "TR", "euroleague"),
            ("Olympiacos", "Olympiacos B.C.", "olympiacos", "OLY", "GR", "euroleague"),
            ("Novak Djokovic", "Novak Djokovic", "novak-djokovic", "NJD", "RS", "atp"),
            ("Carlos Alcaraz", "Carlos Alcaraz", "carlos-alcaraz", "CAL", "ES", "atp"),
            ("Daniil Medvedev", "Daniil Medvedev", "daniil-medvedev", "DME", "RU", "atp"),
            ("Jannik Sinner", "Jannik Sinner", "jannik-sinner", "JSI", "IT", "atp"),
            ("Alexander Zverev", "Alexander Zverev", "alexander-zverev", "AZV", "DE", "wimbledon"),
            ("Stefanos Tsitsipas", "Stefanos Tsitsipas", "stefanos-tsitsipas", "STS", "GR", "wimbledon"),
            ("Casper Ruud", "Casper Ruud", "casper-ruud", "CRU", "NO", "rg"),
            ("Holger Rune", "Holger Rune", "holger-rune", "HRU", "DK", "rg"),
            ("Max Verstappen", "Max Verstappen", "max-verstappen", "VER", "NL", "f1wc"),
            ("Lewis Hamilton", "Lewis Hamilton", "lewis-hamilton", "HAM", "GB", "f1wc"),
            ("Charles Leclerc", "Charles Leclerc", "charles-leclerc", "LEC", "MC", "f1wc"),
            ("Lando Norris", "Lando Norris", "lando-norris", "NOR", "GB", "f1wc"),
            ("George Russell", "George Russell", "george-russell", "RUS", "GB", "f1wc"),
            ("Fernando Alonso", "Fernando Alonso", "fernando-alonso", "ALO", "ES", "f1wc"),
            ("Islam Makhachev", "Islam Makhachev", "islam-makhachev", "IMK", "RU", "ufc"),
            ("Leon Edwards", "Leon Edwards", "leon-edwards", "LED", "GB", "pfl"),
            ("Alex Pereira", "Alex Pereira", "alex-pereira", "APE", "BR", "ufc"),
            ("Sean O'Malley", "Sean O'Malley", "sean-omalley", "SOM", "US", "ufc"),
            ("Tom Aspinall", "Tom Aspinall", "tom-aspinall", "TAS", "GB", "pfl"),
            ("Khamzat Chimaev", "Khamzat Chimaev", "khamzat-chimaev", "KHC", "AE", "ufc"),
        ]

        teams: dict[str, Team] = {}
        for name, official_name, slug, abbreviation, country_code, competition_key in team_specs:
            teams[slug] = get_or_create_team(
                name=name,
                official_name=official_name,
                slug=slug,
                abbreviation=abbreviation,
                country_code=country_code,
                competition_id=competitions[competition_key].id,
            )

        venues = {
            "santiago-bernabeu": get_or_create_venue("Santiago Bernabeu", "Madrid", "ES"),
            "camp-nou": get_or_create_venue("Camp Nou", "Barcelona", "ES"),
            "etihad-stadium": get_or_create_venue("Etihad Stadium", "Manchester", "GB"),
            "anfield": get_or_create_venue("Anfield", "Liverpool", "GB"),
            "allianz-arena": get_or_create_venue("Allianz Arena", "Munich", "DE"),
            "san-siro": get_or_create_venue("San Siro", "Milan", "IT"),
            "crypto-arena": get_or_create_venue("Crypto.com Arena", "Los Angeles", "US"),
            "td-garden": get_or_create_venue("TD Garden", "Boston", "US"),
            "chase-center": get_or_create_venue("Chase Center", "San Francisco", "US"),
            "united-center": get_or_create_venue("United Center", "Chicago", "US"),
            "fiserv-forum": get_or_create_venue("Fiserv Forum", "Milwaukee", "US"),
            "centre-court": get_or_create_venue("Centre Court", "London", "GB"),
            "chatrier": get_or_create_venue("Court Philippe-Chatrier", "Paris", "FR"),
            "arthur-ashe": get_or_create_venue("Arthur Ashe Stadium", "New York", "US"),
            "silverstone": get_or_create_venue("Silverstone Circuit", "Silverstone", "GB"),
            "monza": get_or_create_venue("Monza Circuit", "Monza", "IT"),
            "spa": get_or_create_venue("Circuit de Spa-Francorchamps", "Stavelot", "BE"),
            "yas-marina": get_or_create_venue("Yas Marina Circuit", "Abu Dhabi", "AE"),
            "msg": get_or_create_venue("Madison Square Garden", "New York", "US"),
            "t-mobile": get_or_create_venue("T-Mobile Arena", "Las Vegas", "US"),
            "o2-arena": get_or_create_venue("O2 Arena", "London", "GB"),
        }

        db.flush()
        today = date.today()

        event_specs = [
            # Football
            ("manchester-city", "liverpool", "football", "epl", "etihad-stadium", 3, time(19, 30), "Matchday 28", "Premier League top-table clash."),
            ("arsenal", "manchester-city", "football", "epl", "anfield", 7, time(18, 45), "Matchday 29", "Title-race six-pointer."),
            ("liverpool", "arsenal", "football", "epl", "anfield", 10, time(20, 0), "Matchday 30", "High-intensity league fixture."),
            ("barcelona", "real-madrid", "football", "laliga", "camp-nou", -5, time(19, 0), "Matchday 31", "El Clasico weekend clash."),
            ("juventus", "inter-milan", "football", "seriea", "san-siro", -9, time(19, 45), "Matchday 30", "Derby d'Italia battle."),
            ("bayern-munich", "paris-saint-germain", "football", "ucl", "allianz-arena", -2, time(20, 0), "Round of 16", "Champions League knockout tie."),
            ("borussia-dortmund", "bayern-munich", "football", "ucl", "allianz-arena", 14, time(20, 0), "Quarter Final", "All-German European showdown."),
            # Basketball
            ("los-angeles-lakers", "boston-celtics", "basketball", "nba", "crypto-arena", 2, time(2, 30), "Regular Season", "Classic NBA rivalry game."),
            ("golden-state-warriors", "chicago-bulls", "basketball", "nba", "chase-center", 6, time(3, 0), "Regular Season", "Fast-paced cross-conference matchup."),
            ("milwaukee-bucks", "miami-heat", "basketball", "nba", "fiserv-forum", -3, time(1, 0), "Regular Season", "Eastern Conference playoff race game."),
            ("real-madrid-basketball", "fenerbahce-beko", "basketball", "euroleague", "td-garden", 9, time(18, 0), "Regular Season", "Top EuroLeague teams collide."),
            ("olympiacos", "anadolu-efes", "basketball", "euroleague", "united-center", -8, time(19, 0), "Regular Season", "Tight EuroLeague contest."),
            # Tennis
            ("novak-djokovic", "carlos-alcaraz", "tennis", "atp", "centre-court", 1, time(13, 0), "Final", "ATP Tour marquee final."),
            ("jannik-sinner", "daniil-medvedev", "tennis", "atp", "centre-court", 5, time(11, 30), "Semi Final", "Hard-court semi-final showdown."),
            ("alexander-zverev", "stefanos-tsitsipas", "tennis", "wimbledon", "centre-court", -4, time(12, 0), "Quarter Final", "Wimbledon quarter-final match."),
            ("casper-ruud", "holger-rune", "tennis", "rg", "chatrier", -7, time(14, 0), "Round of 16", "Roland Garros clay-court battle."),
            ("novak-djokovic", "jannik-sinner", "tennis", "atp", "arthur-ashe", 12, time(23, 0), "Semi Final", "Late-session hard-court semifinal."),
            # Formula 1
            ("max-verstappen", "lewis-hamilton", "f1", "f1wc", "silverstone", 4, time(13, 0), "Grand Prix", "Wheel-to-wheel title fight at Silverstone."),
            ("charles-leclerc", "lando-norris", "f1", "f1wc", "monza", 15, time(14, 0), "Grand Prix", "Italian Grand Prix headline duel."),
            ("george-russell", "fernando-alonso", "f1", "f1wc", "spa", -6, time(13, 30), "Grand Prix", "Strategic race in changeable conditions."),
            ("max-verstappen", "charles-leclerc", "f1", "f1wc", "yas-marina", -11, time(16, 0), "Grand Prix", "Season finale decider."),
            ("lewis-hamilton", "lando-norris", "f1", "f1wc", "silverstone", 20, time(12, 30), "Sprint", "Short-format sprint showdown."),
            # MMA
            ("alex-pereira", "khamzat-chimaev", "mma", "ufc", "msg", 8, time(22, 0), "Main Event", "Five-round headline bout."),
            ("islam-makhachev", "sean-omalley", "mma", "ufc", "t-mobile", 18, time(23, 30), "Title Fight", "Championship super-fight."),
            ("khamzat-chimaev", "islam-makhachev", "mma", "ufc", "o2-arena", -5, time(21, 0), "Co-Main Event", "Top contenders collide."),
            ("leon-edwards", "tom-aspinall", "mma", "pfl", "msg", -10, time(20, 30), "Playoff", "PFL playoff elimination bout."),
            ("tom-aspinall", "leon-edwards", "mma", "pfl", "t-mobile", 25, time(22, 30), "Final", "PFL season final matchup."),
        ]

        for home_slug, away_slug, sport_key, competition_key, venue_key, day_offset, start_time, stage_name, description in event_specs:
            event_dt = today + timedelta(days=day_offset)
            status = "scheduled" if day_offset >= 0 else "finished"
            home = teams[home_slug]
            away = teams[away_slug]
            title = f"{home.name} vs {away.name}"
            get_or_create_event(
                title=title,
                event_date=event_dt,
                event_time_utc=start_time,
                status=status,
                stage_name=stage_name,
                stage_ordering=1,
                description=description,
                sport_id=sports[sport_key].id,
                competition_id=competitions[competition_key].id,
                home_team_id=home.id,
                away_team_id=away.id,
                venue_id=venues[venue_key].id,
            )

        db.commit()
    finally:
        db.close()

