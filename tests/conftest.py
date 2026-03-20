import os
from datetime import date, time, timedelta
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

test_db_path = Path("test_arena_event_hub.db").resolve()
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path.as_posix()}"

from app.core.database import Base, SessionLocal, engine  # noqa: E402
from app.main import app  # noqa: E402
from app.models.competition import Competition  # noqa: E402
from app.models.event import Event  # noqa: E402
from app.models.sport import Sport  # noqa: E402
from app.models.team import Team  # noqa: E402
from app.models.venue import Venue  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if test_db_path.exists():
        try:
            test_db_path.unlink()
        except PermissionError:
            # Windows may keep the SQLite file locked briefly.
            pass


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def db_session() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def seeded_calendar_data(db_session: Session):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    sport_football = Sport(name="Football")
    sport_basketball = Sport(name="Basketball")
    db_session.add_all([sport_football, sport_basketball])
    db_session.flush()

    comp_ucl = Competition(external_id="UCL-T", name="UEFA Champions League", season="2025/26", _sport_id=sport_football.id)
    comp_nba = Competition(external_id="NBA-T", name="NBA", season="2025/26", _sport_id=sport_basketball.id)
    db_session.add_all([comp_ucl, comp_nba])
    db_session.flush()

    team_real = Team(
        name="Real Madrid",
        official_name="Real Madrid Club de Futbol",
        slug="real-madrid-test",
        abbreviation="RMA",
        country_code="ES",
        _competition_id=comp_ucl.id,
    )
    team_city = Team(
        name="Manchester City",
        official_name="Manchester City Football Club",
        slug="manchester-city-test",
        abbreviation="MCI",
        country_code="GB",
        _competition_id=comp_ucl.id,
    )
    team_lakers = Team(
        name="Los Angeles Lakers",
        official_name="Los Angeles Lakers",
        slug="los-angeles-lakers-test",
        abbreviation="LAL",
        country_code="US",
        _competition_id=comp_nba.id,
    )
    team_celtics = Team(
        name="Boston Celtics",
        official_name="Boston Celtics",
        slug="boston-celtics-test",
        abbreviation="BOS",
        country_code="US",
        _competition_id=comp_nba.id,
    )
    db_session.add_all([team_real, team_city, team_lakers, team_celtics])
    db_session.flush()

    venue = Venue(name="Santiago Bernabeu Test", city="Madrid", country_code="ES")
    db_session.add(venue)
    db_session.flush()

    today = date.today()
    upcoming_event = Event(
        title="Upcoming Match",
        event_date=today + timedelta(days=2),
        event_time_utc=time(18, 0),
        status="scheduled",
        stage_name="Group Stage",
        stage_ordering=1,
        description="Upcoming football event",
        _sport_id=sport_football.id,
        _competition_id=comp_ucl.id,
        _home_team_id=team_real.id,
        _away_team_id=team_city.id,
        _venue_id=venue.id,
    )
    past_event = Event(
        title="Past Match",
        event_date=today - timedelta(days=2),
        event_time_utc=time(15, 0),
        status="finished",
        stage_name="League",
        stage_ordering=1,
        description="Past basketball event",
        _sport_id=sport_basketball.id,
        _competition_id=comp_nba.id,
        _home_team_id=team_lakers.id,
        _away_team_id=team_celtics.id,
        _venue_id=venue.id,
    )
    db_session.add_all([upcoming_event, past_event])
    db_session.commit()
    db_session.refresh(upcoming_event)
    db_session.refresh(past_event)

    return {
        "sports": {"football": sport_football, "basketball": sport_basketball},
        "competitions": {"ucl": comp_ucl, "nba": comp_nba},
        "teams": {"real": team_real, "city": team_city, "lakers": team_lakers, "celtics": team_celtics},
        "venue": venue,
        "events": {"upcoming": upcoming_event, "past": past_event},
    }
