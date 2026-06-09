from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80))
    profile: Mapped[dict] = mapped_column(JSON)  # full StudentProfileIn payload
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    adventures: Mapped[list["Adventure"]] = relationship(back_populates="student")


class Adventure(Base):
    """A generated playthrough: story arc + missions, stored verbatim so every
    run is reproducible and auditable."""

    __tablename__ = "adventures"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    generator: Mapped[str] = mapped_column(String(16))  # "llm" | "template"
    format: Mapped[str] = mapped_column(String(32), default="mission-map-2d")
    story_arc: Mapped[dict] = mapped_column(JSON)
    missions: Mapped[list] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    student: Mapped[Student] = relationship(back_populates="adventures")
    submissions: Mapped[list["Submission"]] = relationship(back_populates="adventure")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    adventure_id: Mapped[int] = mapped_column(ForeignKey("adventures.id"))
    mission_id: Mapped[str] = mapped_column(String(80))
    code: Mapped[str] = mapped_column(Text)
    passed: Mapped[bool] = mapped_column(Boolean)
    test_results: Mapped[list] = mapped_column(JSON, default=list)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    adventure: Mapped[Adventure] = relationship(back_populates="submissions")


class MissionState(Base):
    __tablename__ = "mission_states"

    id: Mapped[int] = mapped_column(primary_key=True)
    adventure_id: Mapped[int] = mapped_column(ForeignKey("adventures.id"), index=True)
    mission_id: Mapped[str] = mapped_column(String(80))
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
