import uuid

from sqlalchemy import Boolean, ForeignKey, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Quiz(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "quizzes"

    # unique=True: same one-per-lesson design as Exercise (M3.10) — a
    # lesson has at most one attached quiz, not a list of quizzes to choose
    # from. M5.6 links "the quiz" for a lesson, singular.
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE"), unique=True
    )

    questions: Mapped[list["Question"]] = relationship(
        back_populates="quiz",
        cascade="all, delete-orphan",
        order_by="Question.order",
    )


class Question(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "questions"

    quiz_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("quizzes.id", ondelete="CASCADE")
    )
    # Native Postgres enum, same pattern as Message.role (M4.4) — a plain
    # string column constrained to a fixed value set, not a Python Enum
    # class, so the DB itself rejects anything else at insert time.
    question_type: Mapped[str] = mapped_column(
        SQLEnum("mcq", "open_ended", name="question_type")
    )
    prompt: Mapped[str] = mapped_column(Text)
    order: Mapped[int] = mapped_column()

    quiz: Mapped["Quiz"] = relationship(back_populates="questions")
    # Only populated for question_type == "mcq"; an open-ended question has
    # zero choices and is graded by M5.5's LLM rubric instead.
    choices: Mapped[list["Choice"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Choice.order",
    )


class Choice(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "choices"

    # No TimestampMixin — same reasoning as ExerciseSubmission (M3.10): a
    # choice is a fixed piece of quiz content defined once alongside its
    # question, never independently updated after creation.
    question_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="CASCADE")
    )
    text: Mapped[str] = mapped_column(Text)
    # Deliberately never included in any client-facing schema (M5.3) — the
    # whole point of the fetch endpoint is serving questions without
    # leaking the answer key. Only touched server-side, at grading time
    # (M5.4).
    is_correct: Mapped[bool] = mapped_column(Boolean)
    order: Mapped[int] = mapped_column()

    question: Mapped["Question"] = relationship(back_populates="choices")
