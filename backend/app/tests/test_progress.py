import uuid

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Course, Lesson, Module, User
from app.models.progress import LessonProgress, QuizAttempt
from app.models.quiz import Quiz


def _course_with_lessons(db: Session, count: int) -> tuple[Course, list[Lesson]]:
    """A committed Course/Module with `count` lessons, order 1..count —
    the `lesson` fixture only ever builds one lesson, and course-progress
    aggregation needs several to be meaningful (some complete, some not)."""
    course = Course(title="Progress Test Course", description="Fixture course.")
    module = Module(title="Test Module", order=1, course=course)
    lessons = [
        Lesson(title=f"Lesson {i}", body="Fixture body.", order=i, module=module)
        for i in range(1, count + 1)
    ]
    db.add(course)
    db.commit()
    return course, lessons


# --- POST /lessons/{lesson_id}/complete ---


def test_complete_lesson_creates_a_progress_row(
    client: TestClient,
    db: Session,
    lesson: Lesson,
    user: User,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(f"/lessons/{lesson.id}/complete", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["lesson_id"] == str(lesson.id)

    row = db.scalars(select(LessonProgress)).one()
    assert (row.user_id, row.lesson_id) == (user.id, lesson.id)


def test_complete_lesson_is_idempotent(
    client: TestClient, db: Session, lesson: Lesson, auth_headers: dict[str, str]
) -> None:
    # Marking the same lesson complete twice must not create a second row
    # or raise on the unique (user_id, lesson_id) constraint.
    client.post(f"/lessons/{lesson.id}/complete", headers=auth_headers)
    response = client.post(f"/lessons/{lesson.id}/complete", headers=auth_headers)
    assert response.status_code == 200

    rows = db.scalars(select(LessonProgress)).all()
    assert len(rows) == 1


def test_complete_lesson_requires_auth(client: TestClient, lesson: Lesson) -> None:
    response = client.post(f"/lessons/{lesson.id}/complete")
    assert response.status_code == 401


def test_complete_lesson_404s_for_unknown_lesson(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.post(f"/lessons/{uuid.uuid4()}/complete", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "lesson_not_found"


# --- GET /courses/{course_id}/progress ---


def test_progress_counts_completed_and_total_lessons(
    client: TestClient, db: Session, user: User, auth_headers: dict[str, str]
) -> None:
    course, lessons = _course_with_lessons(db, count=3)
    db.add(LessonProgress(user_id=user.id, lesson_id=lessons[0].id))
    db.commit()

    response = client.get(f"/courses/{course.id}/progress", headers=auth_headers)
    assert response.status_code == 200

    body = response.json()
    assert (body["completed_lessons"], body["total_lessons"]) == (1, 3)
    assert body["completed_lesson_ids"] == [str(lessons[0].id)]


def test_progress_is_scoped_to_the_current_user(
    client: TestClient, db: Session, user: User, auth_headers: dict[str, str]
) -> None:
    course, lessons = _course_with_lessons(db, count=1)
    # A different user's completion of the same lesson must not count
    # towards this user's progress on the course.
    other = User(
        email="other@example.com", hashed_password="x", full_name="Other Learner"
    )
    db.add(other)
    db.commit()
    db.add(LessonProgress(user_id=other.id, lesson_id=lessons[0].id))
    db.commit()

    response = client.get(f"/courses/{course.id}/progress", headers=auth_headers)
    body = response.json()
    assert (body["completed_lessons"], body["total_lessons"]) == (0, 1)


def test_progress_reports_the_best_ever_quiz_attempt(
    client: TestClient, db: Session, user: User, auth_headers: dict[str, str]
) -> None:
    course, lessons = _course_with_lessons(db, count=1)
    quiz = Quiz(lesson_id=lessons[0].id)
    db.add(quiz)
    db.commit()

    # A worse attempt recorded after a better one must not overwrite the
    # reported score — "best ever", not "most recent", mirrors Exercise's
    # monotonic solved flag (M3.12).
    db.add(
        QuizAttempt(user_id=user.id, quiz_id=quiz.id, correct_count=3, graded_count=3)
    )
    db.add(
        QuizAttempt(user_id=user.id, quiz_id=quiz.id, correct_count=1, graded_count=3)
    )
    db.commit()

    response = client.get(f"/courses/{course.id}/progress", headers=auth_headers)
    body = response.json()
    assert body["quiz_scores"] == [
        {
            "quiz_id": str(quiz.id),
            "lesson_id": str(lessons[0].id),
            "correct_count": 3,
            "graded_count": 3,
        }
    ]


def test_progress_requires_auth(client: TestClient, db: Session) -> None:
    course, _ = _course_with_lessons(db, count=1)
    response = client.get(f"/courses/{course.id}/progress")
    assert response.status_code == 401


def test_progress_404s_for_unknown_course(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    response = client.get(f"/courses/{uuid.uuid4()}/progress", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "course_not_found"
