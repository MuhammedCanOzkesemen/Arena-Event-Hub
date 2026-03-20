from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Sport(Base):
    __tablename__ = "sports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)

    competitions: Mapped[list["Competition"]] = relationship(
        "Competition",
        back_populates="sport",
        cascade="all, delete-orphan",
    )
    events: Mapped[list["Event"]] = relationship("Event", back_populates="sport")
