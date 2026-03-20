from sqlalchemy import select

from app.core.database import SessionLocal
from app.models.competition import Competition
from app.models.sport import Sport
from app.models.team import Team
from app.models.venue import Venue


def seed_sample_data_if_empty() -> None:
    db = SessionLocal()
    try:
        has_sports = db.scalar(select(Sport.id).limit(1)) is not None
        if has_sports:
            return

        football = Sport(name="Football")
        basketball = Sport(name="Basketball")
        tennis = Sport(name="Tennis")
        db.add_all([football, basketball, tennis])
        db.flush()

        ucl = Competition(
            external_id="UCL",
            name="UEFA Champions League",
            season="2025/26",
            _sport_id=football.id,
        )
        nba = Competition(
            external_id="NBA",
            name="NBA",
            season="2025/26",
            _sport_id=basketball.id,
        )
        atp = Competition(
            external_id="ATP",
            name="ATP Tour",
            season="2025",
            _sport_id=tennis.id,
        )
        db.add_all([ucl, nba, atp])
        db.flush()

        teams = [
            Team(
                name="Real Madrid",
                official_name="Real Madrid Club de Fútbol",
                slug="real-madrid",
                abbreviation="RMA",
                country_code="ES",
                _competition_id=ucl.id,
            ),
            Team(
                name="Manchester City",
                official_name="Manchester City Football Club",
                slug="manchester-city",
                abbreviation="MCI",
                country_code="GB",
                _competition_id=ucl.id,
            ),
            Team(
                name="Los Angeles Lakers",
                official_name="Los Angeles Lakers",
                slug="los-angeles-lakers",
                abbreviation="LAL",
                country_code="US",
                _competition_id=nba.id,
            ),
            Team(
                name="Boston Celtics",
                official_name="Boston Celtics",
                slug="boston-celtics",
                abbreviation="BOS",
                country_code="US",
                _competition_id=nba.id,
            ),
            Team(
                name="Novak Djokovic",
                official_name="Novak Djokovic",
                slug="novak-djokovic",
                abbreviation="NJD",
                country_code="RS",
                _competition_id=atp.id,
            ),
            Team(
                name="Carlos Alcaraz",
                official_name="Carlos Alcaraz",
                slug="carlos-alcaraz",
                abbreviation="CAL",
                country_code="ES",
                _competition_id=atp.id,
            ),
        ]
        db.add_all(teams)

        venues = [
            Venue(name="Santiago Bernabeu", city="Madrid", country_code="ES"),
            Venue(name="TD Garden", city="Boston", country_code="US"),
            Venue(name="Centre Court", city="London", country_code="GB"),
        ]
        db.add_all(venues)

        db.commit()
    finally:
        db.close()

