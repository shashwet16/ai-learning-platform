import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Course, Lesson, Module


def _course_with_two_modules(
    db: Session,
) -> tuple[Course, list[Lesson]]:
    """A committed Course with two Modules of two Lessons each, returned as
    a single flattened list in true (module order, lesson order) sequence —
    [m1l1, m1l2, m2l1, m2l2] — so a test can index into it directly to
    assert prev/next. Everything is added out of that order (modules and
    lessons alike) so a passing ordering assertion can only be explained by
    the route's own `order_by`, not by insertion order happening to match.
    """
    course = Course(title="Two-Module Course", description="Fixture course.")
    module2 = Module(title="Second Module", order=2, course=course)
    module1 = Module(title="First Module", order=1, course=course)
    m2l2 = Lesson(title="M2 Lesson 2", body="Body.", order=2, module=module2)
    m2l1 = Lesson(title="M2 Lesson 1", body="Body.", order=1, module=module2)
    m1l2 = Lesson(title="M1 Lesson 2", body="Body.", order=2, module=module1)
    m1l1 = Lesson(title="M1 Lesson 1", body="Body.", order=1, module=module1)
    db.add(course)
    db.commit()
    return course, [m1l1, m1l2, m2l1, m2l2]


# --- GET /courses ---


def test_list_courses_returns_them_ordered_by_title(
    client: TestClient, db: Session
) -> None:
    # Inserted Z-then-A so a passing alphabetical assertion can only be
    # explained by the route's own order_by(Course.title), not by
    # insertion order happening to match.
    db.add(Course(title="Z Course", description="Second alphabetically... last."))
    db.add(Course(title="A Course", description="First alphabetically."))
    db.commit()

    response = client.get("/courses")
    assert response.status_code == 200
    assert [c["title"] for c in response.json()] == ["A Course", "Z Course"]


def test_list_courses_summary_omits_modules(client: TestClient, db: Session) -> None:
    # CourseSummary is deliberately lighter than CourseDetail — a catalog
    # listing shouldn't pull every module/lesson for every course.
    db.add(Course(title="A Course", description="Fixture."))
    db.commit()

    response = client.get("/courses")
    body = response.json()
    assert len(body) == 1
    assert set(body[0]) == {"id", "title", "description", "created_at"}


# --- GET /courses/{course_id} ---


def test_get_course_returns_modules_and_lessons_in_order(
    client: TestClient, db: Session
) -> None:
    course, lessons = _course_with_two_modules(db)

    response = client.get(f"/courses/{course.id}")
    assert response.status_code == 200

    body = response.json()
    assert [m["title"] for m in body["modules"]] == ["First Module", "Second Module"]
    assert [lesson["title"] for lesson in body["modules"][0]["lessons"]] == [
        "M1 Lesson 1",
        "M1 Lesson 2",
    ]
    assert [lesson["title"] for lesson in body["modules"][1]["lessons"]] == [
        "M2 Lesson 1",
        "M2 Lesson 2",
    ]


def test_get_course_404s_for_unknown_course(client: TestClient) -> None:
    response = client.get(f"/courses/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "course_not_found"


# --- GET /lessons/{lesson_id} ---


def test_get_lesson_returns_body_and_own_fields(
    client: TestClient, lesson: Lesson
) -> None:
    response = client.get(f"/lessons/{lesson.id}")
    assert response.status_code == 200

    body = response.json()
    assert body["id"] == str(lesson.id)
    assert body["title"] == lesson.title
    assert body["body"] == lesson.body
    assert body["module_id"] == str(lesson.module_id)


def test_get_lesson_prev_next_are_null_at_the_course_boundaries(
    client: TestClient, db: Session
) -> None:
    course, lessons = _course_with_two_modules(db)

    first = client.get(f"/lessons/{lessons[0].id}").json()
    assert first["prev_lesson_id"] is None
    assert first["next_lesson_id"] == str(lessons[1].id)

    last = client.get(f"/lessons/{lessons[-1].id}").json()
    assert last["next_lesson_id"] is None
    assert last["prev_lesson_id"] == str(lessons[-2].id)


def test_get_lesson_prev_next_flows_across_module_boundaries(
    client: TestClient, db: Session
) -> None:
    # The last lesson of one module must point forward into the first
    # lesson of the next module (and vice versa) rather than treating each
    # module as its own dead-ended sequence.
    course, lessons = _course_with_two_modules(db)
    m1l2, m2l1 = lessons[1], lessons[2]

    end_of_module1 = client.get(f"/lessons/{m1l2.id}").json()
    assert end_of_module1["next_lesson_id"] == str(m2l1.id)

    start_of_module2 = client.get(f"/lessons/{m2l1.id}").json()
    assert start_of_module2["prev_lesson_id"] == str(m1l2.id)


def test_get_lesson_404s_for_unknown_lesson(client: TestClient) -> None:
    response = client.get(f"/lessons/{uuid.uuid4()}")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "lesson_not_found"
