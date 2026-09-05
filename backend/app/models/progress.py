import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import UUIDPrimaryKeyMixin


class LessonProgress(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "lesson_progress"
    # One row per (user, lesson): marking a lesson complete is a status,
    # not a log — a learner either has completed a lesson or hasn't, so a
    # second "mark complete" call must not create a second row. Contrast
    # with QuizAttempt below, which is deliberately an unbounded log, the
    # same way ExerciseSubmission (M3.10) is a log while Exercise itself
    # has a unique-per-lesson constraint.
    __table_args__ = (UniqueConstraint("user_id", "lesson_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE")
    )
    # No TimestampMixin — same reasoning as ExerciseSubmission.submitted_at:
    # this row is never updated after creation, so an updated_at column
    # would be meaningless. completed_at plays created_at's role.
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class QuizAttempt(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "quiz_attempts"

    # No unique constraint, unlike LessonProgress above — a learner can
    # retake a quiz, and each attempt is its own immutable log entry (same
    # shape as ExerciseSubmission: one row per attempt, never updated).
    # "Where you stand" on a quiz is computed from this log at read time
    # (see get_course_progress's best-attempt query), not stored as a
    # separate mutable summary row.
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )
    quiz_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE")
    )
    # Counts, not a single score/percentage — same shape as
    # QuizSubmitResponse (M5.4/M5.5), so a course-progress read can report
    # "6/8" rather than a lossy 75%, and graded_count still grows on its
    # own if a quiz gains more gradable question types later.
    correct_count: Mapped[int] = mapped_column()
    graded_count: Mapped[int] = mapped_column()
    attempted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
