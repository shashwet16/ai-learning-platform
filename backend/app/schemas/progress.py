import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LessonProgressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lesson_id: uuid.UUID
    completed_at: datetime


class QuizScore(BaseModel):
    # Built by hand in the route, not from_attributes=True off QuizAttempt
    # directly — lesson_id comes from the attempt's quiz, not the attempt
    # row itself, so there's no single ORM object with both as attributes.
    quiz_id: uuid.UUID
    lesson_id: uuid.UUID
    correct_count: int
    graded_count: int


class CourseProgress(BaseModel):
    completed_lessons: int
    total_lessons: int
    # Beyond the roadmap's literal {completed_lessons, total_lessons,
    # quiz_scores} shape: per-lesson checkmarks on the course detail page
    # (M6.4) need to know *which* lessons are done, not just how many —
    # an aggregate count alone can't render that. Returned here instead of
    # a second per-lesson endpoint so the page stays a single request.
    completed_lesson_ids: list[uuid.UUID]
    quiz_scores: list[QuizScore]
