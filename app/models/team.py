from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Team(Base):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("slug", name="uq_team_slug"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    official_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    slug: Mapped[str] = mapped_column(String(140), index=True, nullable=False)
    abbreviation: Mapped[str | None] = mapped_column(String(10), nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(2), index=True, nullable=True)
    _competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"), index=True, nullable=False)

    competition: Mapped["Competition"] = relationship("Competition", back_populates="teams")
    home_events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="home_team", foreign_keys="Event._home_team_id"
    )
    away_events: Mapped[list["Event"]] = relationship(
        "Event", back_populates="away_team", foreign_keys="Event._away_team_id"
    )
