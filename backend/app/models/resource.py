import uuid

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Resource(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "resources"

    # No unique=True, unlike Exercise/Quiz's lesson_id — a lesson's
    # "Further Reading" is deliberately a curated list, not a single
    # attached item, so many resources can point at the same lesson.
    # No ORM relationship back to Lesson either, same as Quiz/Exercise —
    # this codebase queries child-of-lesson tables directly by lesson_id
    # rather than adding a back_populates collection to Lesson itself.
    lesson_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("lessons.id", ondelete="CASCADE")
    )
    title: Mapped[str] = mapped_column()
    url: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column(Text)
    # Native Postgres enum, same pattern as Question.question_type (M5.1)
    # and Message.role (M4.4) — lets the "Further Reading" UI group or
    # icon-differentiate real docs from a blog post or a paper, and lets
    # the DB itself reject anything outside this set at insert time.
    resource_type: Mapped[str] = mapped_column(
        SQLEnum(
            "official_docs",
            "article",
            "video",
            "paper",
            "repo",
            "interactive",
            name="resource_type",
        )
    )
    order: Mapped[int] = mapped_column()
