from datetime import date

from sqlalchemy.orm import Session

from app.models.competition import Competition
from app.models.event import Event
from app.models.sport import Sport
from app.models.team import Team
from app.models.venue import Venue
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate


class EventService:
    def __init__(self, repository: EventRepository | None = None) -> None:
        self.repository = repository or EventRepository()

    def list_events(self, db: Session, sport_id: int | None = None, event_date: date | None = None) -> list[Event]:
        return self.repository.list_events(db=db, sport_id=sport_id, event_date=event_date)

    def get_event(self, db: Session, event_id: int) -> Event | None:
        return self.repository.get_event(db=db, event_id=event_id)

    def create_event(self, db: Session, payload: EventCreate) -> Event:
        self._validate_references(db=db, payload=payload)
        return self.repository.create_event(db=db, event_data=payload)

    def _validate_references(self, db: Session, payload: EventCreate) -> None:
        if db.get(Sport, payload.sport_id) is None:
            raise ValueError("Sport not found")
        if db.get(Competition, payload.competition_id) is None:
            raise ValueError("Competition not found")
        if db.get(Team, payload.away_team_id) is None:
            raise ValueError("Away team not found")
        if payload.home_team_id is not None and db.get(Team, payload.home_team_id) is None:
            raise ValueError("Home team not found")
        if payload.venue_id is not None and db.get(Venue, payload.venue_id) is None:
            raise ValueError("Venue not found")
        if payload.home_team_id is not None and payload.home_team_id == payload.away_team_id:
            raise ValueError("Home team and away team must be different")
