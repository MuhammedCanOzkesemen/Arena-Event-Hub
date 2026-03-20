from datetime import date, time, datetime

from pydantic import BaseModel, ConfigDict


class EventCreate(BaseModel):
    title: str
    event_date: date
    event_time_utc: time
    status: str
    stage_name: str
    stage_ordering: int = 1
    description: str | None = None
    sport_id: int
    competition_id: int
    home_team_id: int | None = None
    away_team_id: int
    venue_id: int | None = None


class EventRead(BaseModel):
    id: int
    title: str
    event_date: date
    event_time_utc: time
    status: str
    stage_name: str
    stage_ordering: int
    description: str | None
    sport_id: int
    competition_id: int
    home_team_id: int | None
    away_team_id: int
    venue_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)