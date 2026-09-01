import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError
from app.db.session import get_db
from app.models.course import Lesson
from app.models.exercise import Exercise, ExerciseSubmission
from app.models.user import User
from app.schemas.exercise import (
    ExerciseListItem,
    ExerciseRead,
    ExerciseSubmissionCreate,
    ExerciseSubmissionRead,
    ExerciseTestCode,
)

router = APIRouter(prefix="/exercises", tags=["exercises"])


@router.get("", response_model=list[ExerciseListItem])
def list_exercises(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ExerciseListItem]:
    # Authenticated, unlike the single-exercise GET below — the entire
    # point of this endpoint is per-user "solved" status, which has no
    # meaning for an anonymous caller.
    rows = db.execute(
        select(Exercise, Lesson.title)
        .join(Lesson, Exercise.lesson_id == Lesson.id)
        .order_by(Exercise.order)
    ).all()

    # "Solved" means at least one passing submission ever exists, not
    # just that the *latest* one passed — once solved, an exercise stays
    # marked solved even if the learner later re-submits something wrong
    # while experimenting. A single query for every solved id, rather than
    # one query per exercise, avoids an N+1 here the same way M3.3's
    # selectinload avoided one for course/module/lesson.
    solved_ids = set(
        db.scalars(
            select(ExerciseSubmission.exercise_id)
            .where(
                ExerciseSubmission.user_id == current_user.id,
                ExerciseSubmission.passed.is_(True),
            )
            .distinct()
        ).all()
    )

    return [
        ExerciseListItem(
            id=exercise.id,
            lesson_id=exercise.lesson_id,
            lesson_title=lesson_title,
            prompt=exercise.prompt,
            order=exercise.order,
            solved=exercise.id in solved_ids,
        )
        for exercise, lesson_title in rows
    ]


@router.get("/{lesson_id}", response_model=ExerciseRead)
def get_exercise_for_lesson(
    lesson_id: uuid.UUID, db: Session = Depends(get_db)
) -> Exercise:
    # Public, no Depends(get_current_user) — same as course/lesson reads
    # (courses.py has no auth check either). Only the submission endpoints
    # below need to know who's asking, since a submission is tied to one
    # user's own attempt history.
    exercise = db.scalars(
        select(Exercise).where(Exercise.lesson_id == lesson_id)
    ).one_or_none()
    if exercise is None:
        raise AppError("Exercise not found", status_code=404, code="exercise_not_found")
    return exercise


@router.get("/{exercise_id}/test-code", response_model=ExerciseTestCode)
def get_exercise_test_code(
    exercise_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Exercise:
    # Authenticated, and only ever called by the frontend at Submit time
    # (M3.11) — not on page load. See ExerciseTestCode's own docstring for
    # why this is a soft-hidden test, not a truly secret one: client-side
    # Pyodide grading means the browser must receive this to run it at all.
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise AppError("Exercise not found", status_code=404, code="exercise_not_found")
    return exercise


@router.post(
    "/{exercise_id}/submissions",
    response_model=ExerciseSubmissionRead,
    status_code=201,
)
def submit_exercise(
    exercise_id: uuid.UUID,
    body: ExerciseSubmissionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ExerciseSubmission:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise AppError("Exercise not found", status_code=404, code="exercise_not_found")

    submission = ExerciseSubmission(
        exercise_id=exercise_id,
        user_id=current_user.id,
        code=body.code,
        passed=body.passed,
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.get("/{exercise_id}/submissions", response_model=list[ExerciseSubmissionRead])
def list_submissions(
    exercise_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[ExerciseSubmission]:
    exercise = db.get(Exercise, exercise_id)
    if exercise is None:
        raise AppError("Exercise not found", status_code=404, code="exercise_not_found")

    # Scoped to the current user, same as chat's conversation history —
    # one learner's attempts are never visible to another.
    return list(
        db.scalars(
            select(ExerciseSubmission)
            .where(
                ExerciseSubmission.exercise_id == exercise_id,
                ExerciseSubmission.user_id == current_user.id,
            )
            .order_by(ExerciseSubmission.submitted_at)
        ).all()
    )
