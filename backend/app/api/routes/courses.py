import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.db.session import get_db
from app.models.course import Course, Lesson, Module
from app.schemas.course import CourseDetail, CourseSummary, LessonDetail

router = APIRouter(prefix="/courses", tags=["courses"])
# Lessons get their own top-level URL space (/lessons/{id}, not
# /courses/lessons/{id}) even though the route lives in this same file —
# lessons are addressed independently once a reader is inside one.
lessons_router = APIRouter(prefix="/lessons", tags=["courses"])


@router.get("", response_model=list[CourseSummary])
def list_courses(db: Session = Depends(get_db)) -> list[Course]:
    return list(db.scalars(select(Course).order_by(Course.title)).all())


@router.get("/{course_id}", response_model=CourseDetail)
def get_course(course_id: uuid.UUID, db: Session = Depends(get_db)) -> Course:
    course = db.execute(
        select(Course)
        .where(Course.id == course_id)
        .options(selectinload(Course.modules).selectinload(Module.lessons))
    ).scalar_one_or_none()
    if course is None:
        raise AppError("Course not found", status_code=404, code="course_not_found")
    return course


@lessons_router.get("/{lesson_id}", response_model=LessonDetail)
def get_lesson(lesson_id: uuid.UUID, db: Session = Depends(get_db)) -> LessonDetail:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise AppError("Lesson not found", status_code=404, code="lesson_not_found")

    module = db.get(Module, lesson.module_id)

    # Prev/next must flow across module boundaries — a reader finishing the
    # last lesson of one module should continue into the first lesson of
    # the next module, not hit a dead end just because the module changed.
    # So this orders every lesson in the whole course (not just this
    # module) by (module order, lesson order) and finds this lesson's
    # position in that single flattened sequence.
    course_lessons = list(
        db.scalars(
            select(Lesson)
            .join(Module, Lesson.module_id == Module.id)
            .where(Module.course_id == module.course_id)
            .order_by(Module.order, Lesson.order)
        ).all()
    )
    index = next(i for i, entry in enumerate(course_lessons) if entry.id == lesson.id)
    prev_lesson_id = course_lessons[index - 1].id if index > 0 else None
    next_lesson_id = (
        course_lessons[index + 1].id if index < len(course_lessons) - 1 else None
    )

    return LessonDetail(
        id=lesson.id,
        title=lesson.title,
        body=lesson.body,
        order=lesson.order,
        module_id=lesson.module_id,
        prev_lesson_id=prev_lesson_id,
        next_lesson_id=next_lesson_id,
    )
