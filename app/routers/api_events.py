from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.event import EventCreate, EventRead
from app.services.event_service import EventService

router = APIRouter(prefix="/api/events", tags=["events"])
service = EventService()

def _to_event_read(event) -> EventRead:
    return EventRead(
        id=event.id,
        title=event.title,
        event_date=event.event_date,
        event_time_utc=event.event_time_utc,
        status=event.status,
        stage_name=event.stage_name,
        stage_ordering=event.stage_ordering,
        description=event.description,
        sport_id=event._sport_id,
        competition_id=event._competition_id,
        home_team_id=event._home_team_id,
        away_team_id=event._away_team_id,
        venue_id=event._venue_id,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


@router.get("", response_model=list[EventRead])
def list_events(
    sport_id: str | None = Query(default=None),
    event_date: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[EventRead]:
    parsed_sport_id = None
    if sport_id:
        try:
            parsed_sport_id = int(sport_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid sport_id") from exc

    parsed_event_date = None
    if event_date:
        parsed_event_date = date.fromisoformat(event_date)

    events = service.list_events(db=db, sport_id=parsed_sport_id, event_date=parsed_event_date)
    return [_to_event_read(item) for item in events]


@router.get("/{event_id}", response_model=EventRead)
def get_event(event_id: int, db: Session = Depends(get_db)) -> EventRead:
    event = service.get_event(db=db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    return _to_event_read(event)


@router.post("", response_model=EventRead, status_code=status.HTTP_201_CREATED)
def create_event(payload: EventCreate, db: Session = Depends(get_db)) -> EventRead:
    try:
        event = service.create_event(db=db, payload=payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return _to_event_read(event)
