import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Exercise(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "exercises"

    # unique=True: a lesson has at most one attached exercise (M3.11 renders
    # "a lesson's attached exercise, if it has one" — singular, not a list).
    # `order` isn't for ordering multiple exercises within this one lesson;
    # it's for M3.12's practice catalog, which lists exercises across every
    # course/lesson and needs a stable display order, the same role `order`
    # plays on Module/Lesson within their own parent.
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), unique=True
    )
    prompt: Mapped[str] = mapped_column(Text)
    starter_code: Mapped[str] = mapped_column(Text)
    # Deliberately never included in ExerciseRead / sent to the client.
    # Grading runs client-side in the learner's own Pyodide sandbox (same
    # execution model as M3.9), but the hidden test itself must stay
    # server-only — otherwise a learner could just read it out of the
    # network tab and hand-satisfy it without solving anything. See the
    # Phase 3B planning note for the full reasoning and its honest
    # tradeoff (a determined user can still fake a `passed: true` result;
    # acceptable for a self-paced tool, not for anything tamper-proof).
    test_code: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column()

    submissions: Mapped[list["ExerciseSubmission"]] = relationship(
        back_populates="exercise",
        cascade="all, delete-orphan",
        order_by="ExerciseSubmission.submitted_at",
    )


class ExerciseSubmission(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "exercise_submissions"

    # No TimestampMixin here, unlike every other model in this project —
    # deliberate, not an oversight. A submission is an immutable log entry
    # (one attempt, recorded once); it's never updated after creation, so
    # an `updated_at` column would be meaningless. `submitted_at` (the
    # field name the roadmap itself specifies) plays the role `created_at`
    # plays elsewhere.
    exercise_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("exercises.id", ondelete="CASCADE")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    code: Mapped[str] = mapped_column(Text)
    passed: Mapped[bool] = mapped_column(Boolean)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    exercise: Mapped["Exercise"] = relationship(back_populates="submissions")
