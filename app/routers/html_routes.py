from datetime import date, time

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.competition import Competition
from app.models.sport import Sport
from app.models.team import Team
from app.models.venue import Venue
from app.schemas.event import EventCreate
from app.services.event_service import EventService

router = APIRouter(tags=["html"])
templates = Jinja2Templates(directory="app/templates")
service = EventService()


@router.get("/", include_in_schema=False)
def root_redirect() -> RedirectResponse:
    return RedirectResponse(url="/events", status_code=status.HTTP_302_FOUND)


@router.get("/events")
def events_page(
    request: Request,
    sport_id: str | None = Query(default=None),
    event_date: str | None = Query(default=None),
    mode: str = Query(default="upcoming"),
    db: Session = Depends(get_db),
):
    selected_mode = mode if mode in {"upcoming", "all", "past"} else "upcoming"

    parsed_sport_id = None
    if sport_id:
        try:
            parsed_sport_id = int(sport_id)
        except ValueError:
            parsed_sport_id = None

    parsed_event_date = None
    if event_date:
        parsed_event_date = date.fromisoformat(event_date)

    events = service.list_events(
        db=db,
        sport_id=parsed_sport_id,
        event_date=parsed_event_date,
        mode=selected_mode,
    )
    sports = list(db.scalars(select(Sport).order_by(Sport.name.asc())).all())
    return templates.TemplateResponse(
        request=request,
        name="events/index.html",
        context={
            "events": events,
            "sports": sports,
            "selected_sport_id": parsed_sport_id,
            "selected_event_date": parsed_event_date.isoformat() if parsed_event_date else "",
            "selected_mode": selected_mode,
        },
    )


@router.get("/events/new")
def new_event_page(request: Request, db: Session = Depends(get_db)):
    sports = list(db.scalars(select(Sport).order_by(Sport.name.asc())).all())
    competitions = list(db.scalars(select(Competition).order_by(Competition.name.asc())).all())
    teams = list(db.scalars(select(Team).order_by(Team.name.asc())).all())
    venues = list(db.scalars(select(Venue).order_by(Venue.name.asc())).all())
    return templates.TemplateResponse(
        request=request,
        name="events/create.html",
        context={"sports": sports, "competitions": competitions, "teams": teams, "venues": venues, "error": None},
    )


@router.post("/events/new")
def create_event_page(
    request: Request,
    title: str = Form(...),
    event_date: date = Form(...),
    event_time_utc: str = Form(...),
    status_value: str = Form(..., alias="status"),
    stage_name: str = Form(...),
    stage_ordering: int = Form(1),
    description: str = Form(""),
    sport_id: int = Form(..., alias="_sport_id"),
    competition_id: int = Form(..., alias="_competition_id"),
    home_team_id: str = Form("", alias="_home_team_id"),
    away_team_id: int = Form(..., alias="_away_team_id"),
    venue_id: str = Form("", alias="_venue_id"),
    db: Session = Depends(get_db),
):
    payload = EventCreate(
        title=title,
        event_date=event_date,
        event_time_utc=time.fromisoformat(event_time_utc),
        status=status_value,
        stage_name=stage_name,
        stage_ordering=stage_ordering,
        description=description or None,
        sport_id=sport_id,
        competition_id=competition_id,
        home_team_id=int(home_team_id) if home_team_id.strip() else None,
        away_team_id=away_team_id,
        venue_id=int(venue_id) if venue_id.strip() else None,
    )

    try:
        event = service.create_event(db=db, payload=payload)
    except ValueError as exc:
        sports = list(db.scalars(select(Sport).order_by(Sport.name.asc())).all())
        competitions = list(db.scalars(select(Competition).order_by(Competition.name.asc())).all())
        teams = list(db.scalars(select(Team).order_by(Team.name.asc())).all())
        venues = list(db.scalars(select(Venue).order_by(Venue.name.asc())).all())
        return templates.TemplateResponse(
            request=request,
            name="events/create.html",
            context={"sports": sports, "competitions": competitions, "teams": teams, "venues": venues, "error": str(exc)},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return RedirectResponse(url=f"/events/{event.id}?created=1", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/events/{event_id}")
def event_detail_page(
    event_id: int,
    request: Request,
    created: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    event = service.get_event(db=db, event_id=event_id)
    if event is None:
        return templates.TemplateResponse(
            request=request, name="events/detail.html", context={"event": None}, status_code=status.HTTP_404_NOT_FOUND
        )
    return templates.TemplateResponse(
        request=request,
        name="events/detail.html",
        context={"event": event, "created_success": created == "1"},
    )
