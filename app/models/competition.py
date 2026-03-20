from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Competition(Base):
    __tablename__ = "competitions"
    __table_args__ = (
        UniqueConstraint("external_id", "season", name="uq_competition_external_season"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), index=True, nullable=False)
    season: Mapped[str] = mapped_column(String(30), index=True, nullable=False)
    _sport_id: Mapped[int] = mapped_column(ForeignKey("sports.id"), index=True, nullable=False)

    sport: Mapped["Sport"] = relationship("Sport", back_populates="competitions")
    teams: Mapped[list["Team"]] = relationship(
        "Team",
        back_populates="competition",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["Event"]] = relationship("Event", back_populates="competition")
