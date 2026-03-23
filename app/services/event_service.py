from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import or_, select
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

    def list_events(
        self,
        db: Session,
        sport_id: int | None = None,
        event_date: date | None = None,
        mode: str = "upcoming",
        page: int = 1,
        page_size: int = 5,
    ) -> list[Event]:
        return self.repository.list_events(
            db=db,
            sport_id=sport_id,
            event_date=event_date,
            mode=mode,
            page=page,
            page_size=page_size,
        )

    def get_event(self, db: Session, event_id: int) -> Event | None:
        return self.repository.get_event(db=db, event_id=event_id)

    def create_event(self, db: Session, payload: EventCreate) -> Event:
        self._validate_references(db=db, payload=payload)
        return self.repository.create_event(db=db, event_data=payload)

    def delete_event(self, db: Session, event_id: int) -> bool:
        return self.repository.delete_event(db=db, event_id=event_id)

    def _validate_references(self, db: Session, payload: EventCreate) -> None:
        if payload.sport_id <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sport is required")
        if payload.competition_id <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Competition is required")
        if payload.away_team_id <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Away team is required")
        if payload.event_date < date.today():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Event date cannot be in the past")
        if payload.home_team_id is not None and payload.home_team_id == payload.away_team_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Home team and away team must be different",
            )

        sport = db.get(Sport, payload.sport_id)
        if sport is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Sport not found")

        competition = db.get(Competition, payload.competition_id)
        if competition is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Competition not found")

        if competition._sport_id != sport.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Competition does not belong to selected sport",
            )

        away_team = db.get(Team, payload.away_team_id)
        if away_team is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Away team not found")
        if away_team._competition_id != competition.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Away team does not belong to selected competition",
            )

        home_team = None
        if payload.home_team_id is not None:
            home_team = db.get(Team, payload.home_team_id)
            if home_team is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Home team not found")
            if home_team._competition_id != competition.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Home team does not belong to selected competition",
                )

        self._apply_generated_title(payload=payload, home_team=home_team, away_team=away_team)

        if payload.venue_id is not None and db.get(Venue, payload.venue_id) is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Venue not found")

        duplicate_stmt = select(Event.id).where(
            Event._competition_id == payload.competition_id,
            Event._away_team_id == payload.away_team_id,
            Event.event_date == payload.event_date,
        )
        if payload.home_team_id is None:
            duplicate_stmt = duplicate_stmt.where(Event._home_team_id.is_(None))
        else:
            duplicate_stmt = duplicate_stmt.where(Event._home_team_id == payload.home_team_id)

        is_duplicate = db.scalar(duplicate_stmt.limit(1)) is not None
        if is_duplicate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate event exists for this competition, teams, and date",
            )

        team_ids = [payload.away_team_id]
        if payload.home_team_id is not None:
            team_ids.append(payload.home_team_id)
        for team_id in team_ids:
            conflict_stmt = select(Event.id).where(
                Event.event_date == payload.event_date,
                Event.event_time_utc == payload.event_time_utc,
                or_(Event._home_team_id == team_id, Event._away_team_id == team_id),
            )
            has_conflict = db.scalar(conflict_stmt.limit(1)) is not None
            if has_conflict:
                team = db.get(Team, team_id)
                team_name = team.name if team is not None else f"Team {team_id}"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Scheduling conflict: {team_name} already has an event at this date and time",
                )

    def _apply_generated_title(self, payload: EventCreate, home_team: Team | None, away_team: Team) -> None:
        if payload.title.strip():
            return
        home_name = home_team.name if home_team is not None else "TBD"
        payload.title = f"{home_name} vs {away_team.name}"
