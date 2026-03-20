from datetime import date, datetime, time

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Event(Base):
    __tablename__ = "events"
    __table_args__ = (
        CheckConstraint("stage_ordering >= 1", name="ck_event_stage_ordering_positive"),
        CheckConstraint("_home_team_id IS NULL OR _home_team_id != _away_team_id", name="ck_event_teams_different"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    event_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    event_time_utc: Mapped[time] = mapped_column(Time, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    stage_name: Mapped[str] = mapped_column(String(100), nullable=False)
    stage_ordering: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    _sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), index=True, nullable=False)
    _competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), index=True, nullable=False)
    _home_team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), index=True, nullable=True)
    _away_team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True, nullable=False)
    _venue_id: Mapped[int | None] = mapped_column(ForeignKey("venues.id"), index=True, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    sport: Mapped["Sport"] = relationship("Sport", back_populates="events")
    competition: Mapped["Competition"] = relationship("Competition", back_populates="events")
    home_team: Mapped["Team | None"] = relationship("Team", back_populates="home_events", foreign_keys=[_home_team_id])
    away_team: Mapped["Team"] = relationship("Team", back_populates="away_events", foreign_keys=[_away_team_id])
    venue: Mapped["Venue | None"] = relationship("Venue", back_populates="events")
