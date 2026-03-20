from datetime import date

from sqlalchemy import Select, select
from sqlalchemy.orm import Session, joinedload

from app.models.event import Event
from app.schemas.event import EventCreate


class EventRepository:
    def list_events(
        self,
        db: Session,
        sport_id: int | None = None,
        event_date: date | None = None,
        mode: str = "upcoming",
    ) -> list[Event]:
        statement: Select[tuple[Event]] = (
            select(Event)
            .options(
                joinedload(Event.sport),
                joinedload(Event.competition),
                joinedload(Event.home_team),
                joinedload(Event.away_team),
                joinedload(Event.venue),
            )
        )

        if sport_id is not None:
            statement = statement.where(Event._sport_id == sport_id)
        if event_date is not None:
            statement = statement.where(Event.event_date == event_date)
        else:
            today = date.today()
            if mode == "upcoming":
                statement = statement.where(Event.event_date >= today)
            elif mode == "past":
                statement = statement.where(Event.event_date < today)

        if mode == "past":
            statement = statement.order_by(Event.event_date.desc(), Event.event_time_utc.desc(), Event.id.desc())
        else:
            statement = statement.order_by(Event.event_date.asc(), Event.event_time_utc.asc(), Event.id.asc())

        return list(db.scalars(statement).all())

    def get_event(self, db: Session, event_id: int) -> Event | None:
        statement: Select[tuple[Event]] = (
            select(Event)
            .where(Event.id == event_id)
            .options(
                joinedload(Event.sport),
                joinedload(Event.competition),
                joinedload(Event.home_team),
                joinedload(Event.away_team),
                joinedload(Event.venue),
            )
        )
        return db.scalar(statement)

    def create_event(self, db: Session, event_data: EventCreate) -> Event:
        event = Event(
            title=event_data.title,
            event_date=event_data.event_date,
            event_time_utc=event_data.event_time_utc,
            status=event_data.status,
            stage_name=event_data.stage_name,
            stage_ordering=event_data.stage_ordering,
            description=event_data.description,
            _sport_id=event_data.sport_id,
            _competition_id=event_data.competition_id,
            _home_team_id=event_data.home_team_id,
            _away_team_id=event_data.away_team_id,
            _venue_id=event_data.venue_id,
        )
        db.add(event)
        db.commit()
        db.refresh(event)
        return event

    def delete_event(self, db: Session, event_id: int) -> bool:
        event = db.get(Event, event_id)
        if event is None:
            return False
        db.delete(event)
        db.commit()
        return True