import uuid
from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    attempts: Mapped[list["Attempt"]] = relationship(back_populates="user")


class Level(Base):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(10), index=True)  # A1..C1
    title: Mapped[str] = mapped_column(String(255))

    tasks: Mapped[list["Task"]] = relationship(back_populates="level")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_type: Mapped[str] = mapped_column(String(50))  # quick_fix, translate_duel, etc.
    level_code: Mapped[str] = mapped_column(String(10), index=True)
    prompt: Mapped[str] = mapped_column(Text)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    answer_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    level_id: Mapped[int | None] = mapped_column(ForeignKey("levels.id"), nullable=True)
    level: Mapped["Level"] = relationship(back_populates="tasks")
    attempts: Mapped[list["Attempt"]] = relationship(back_populates="task")


class Attempt(Base):
    __tablename__ = "attempts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), index=True)
    answer_text: Mapped[str] = mapped_column(Text)
    feedback_json: Mapped[dict] = mapped_column(JSON)
    overall_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    time_spent_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="attempts")
    task: Mapped["Task"] = relationship(back_populates="attempts")
    mistakes: Mapped[list["Mistake"]] = relationship(back_populates="source_attempt")


class Mistake(Base):
    __tablename__ = "mistakes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )
    issue_type: Mapped[str] = mapped_column(String(50))
    excerpt: Mapped[str] = mapped_column(Text)
    suggestion: Mapped[str] = mapped_column(Text)
    source_attempt_id: Mapped[int] = mapped_column(
        ForeignKey("attempts.id"), index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    source_attempt: Mapped["Attempt"] = relationship(back_populates="mistakes")



