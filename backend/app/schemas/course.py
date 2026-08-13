import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LessonSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    order: int


class ModuleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    order: int
    lessons: list[LessonSummary]


class CourseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    description: str
    created_at: datetime


class CourseDetail(CourseSummary):
    modules: list[ModuleSummary]


class LessonDetail(BaseModel):
    id: uuid.UUID
    title: str
    body: str
    order: int
    module_id: uuid.UUID
    prev_lesson_id: uuid.UUID | None
    next_lesson_id: uuid.UUID | None
