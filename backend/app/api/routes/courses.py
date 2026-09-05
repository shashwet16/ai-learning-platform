import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.models.course import Course, Lesson, Module
from app.models.progress import LessonProgress, QuizAttempt
from app.models.quiz import Quiz
from app.models.user import User
from app.schemas.course import CourseDetail, CourseSummary, LessonDetail
from app.schemas.progress import CourseProgress, LessonProgressRead, QuizScore

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


@lessons_router.post("/{lesson_id}/complete", response_model=LessonProgressRead)
def complete_lesson(
    lesson_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> LessonProgress:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise AppError("Lesson not found", status_code=404, code="lesson_not_found")

    # Idempotent: calling this on an already-completed lesson returns the
    # existing row rather than inserting a duplicate or raising on the
    # unique (user_id, lesson_id) constraint. Same idempotency instinct as
    # M5.2's seed script — it lets the frontend call this unconditionally
    # (e.g. on every "Mark complete" click) without tracking prior state.
    existing = db.scalars(
        select(LessonProgress).where(
            LessonProgress.user_id == current_user.id,
            LessonProgress.lesson_id == lesson_id,
        )
    ).one_or_none()
    if existing is not None:
        return existing

    progress = LessonProgress(user_id=current_user.id, lesson_id=lesson_id)
    db.add(progress)
    db.commit()
    db.refresh(progress)
    return progress


@router.get("/{course_id}/progress", response_model=CourseProgress)
def get_course_progress(
    course_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CourseProgress:
    course = db.get(Course, course_id)
    if course is None:
        raise AppError("Course not found", status_code=404, code="course_not_found")

    lesson_ids = list(
        db.scalars(
            select(Lesson.id)
            .join(Module, Lesson.module_id == Module.id)
            .where(Module.course_id == course_id)
        ).all()
    )

    completed_lesson_ids: list[uuid.UUID] = []
    quiz_scores: list[QuizScore] = []

    if lesson_ids:
        completed_lesson_ids = list(
            db.scalars(
                select(LessonProgress.lesson_id).where(
                    LessonProgress.user_id == current_user.id,
                    LessonProgress.lesson_id.in_(lesson_ids),
                )
            ).all()
        )

        quizzes = list(
            db.scalars(select(Quiz).where(Quiz.lesson_id.in_(lesson_ids))).all()
        )
        quiz_ids = [quiz.id for quiz in quizzes]
        lesson_id_by_quiz = {quiz.id: quiz.lesson_id for quiz in quizzes}

        if quiz_ids:
            # Best attempt ever, not the most recent one — same "stays
            # marked once achieved" reasoning as Exercise's solved flag
            # (M3.12), so retrying a quiz out of curiosity can't make the
            # dashboard look like it regressed. Ordered by correct_count
            # descending and keeping the first row seen per quiz, which is
            # one query rather than one query per quiz — the same
            # N+1-avoidance instinct as M3.12's batched solved-ids query.
            attempts = db.scalars(
                select(QuizAttempt)
                .where(
                    QuizAttempt.user_id == current_user.id,
                    QuizAttempt.quiz_id.in_(quiz_ids),
                )
                .order_by(QuizAttempt.correct_count.desc())
            ).all()
            best_by_quiz: dict[uuid.UUID, QuizAttempt] = {}
            for attempt in attempts:
                best_by_quiz.setdefault(attempt.quiz_id, attempt)

            quiz_scores = [
                QuizScore(
                    quiz_id=quiz_id,
                    lesson_id=lesson_id_by_quiz[quiz_id],
                    correct_count=attempt.correct_count,
                    graded_count=attempt.graded_count,
                )
                for quiz_id, attempt in best_by_quiz.items()
            ]

    return CourseProgress(
        completed_lessons=len(completed_lesson_ids),
        total_lessons=len(lesson_ids),
        completed_lesson_ids=completed_lesson_ids,
        quiz_scores=quiz_scores,
    )
