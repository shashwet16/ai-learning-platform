import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Course, Lesson, Module
from app.models.resource import Resource


def test_get_resources_returns_them_ordered(
    client: TestClient, db: Session, lesson: Lesson
) -> None:
    # Inserted out of order so a passing ordering assertion can only be
    # explained by the route's own order_by(Resource.order).
    db.add(
        Resource(
            lesson_id=lesson.id,
            title="Second Resource",
            url="https://example.com/second",
            description="Comes second.",
            resource_type="article",
            order=2,
        )
    )
    db.add(
        Resource(
            lesson_id=lesson.id,
            title="First Resource",
            url="https://example.com/first",
            description="Comes first.",
            resource_type="official_docs",
            order=1,
        )
    )
    db.commit()

    response = client.get(f"/lessons/{lesson.id}/resources")
    assert response.status_code == 200
    body = response.json()
    assert [r["title"] for r in body] == ["First Resource", "Second Resource"]
    assert body[0]["resource_type"] == "official_docs"


def test_get_resources_is_a_no_auth_public_endpoint(
    client: TestClient, lesson: Lesson
) -> None:
    # No Authorization header at all — same public-fetch posture as the
    # quiz and lesson-detail GETs.
    response = client.get(f"/lessons/{lesson.id}/resources")
    assert response.status_code == 200


def test_get_resources_returns_empty_list_for_a_lesson_with_none(
    client: TestClient, lesson: Lesson
) -> None:
    # Unlike quiz/exercise (one-or-404), resources are a genuine list —
    # nothing curated yet is a valid, unremarkable state, not a 404.
    response = client.get(f"/lessons/{lesson.id}/resources")
    assert response.status_code == 200
    assert response.json() == []


def test_get_resources_404s_are_not_used_for_unknown_lesson(
    client: TestClient,
) -> None:
    # A nonexistent lesson also just returns an empty list — this route
    # never inspects the Lesson table at all, only filters Resource by
    # lesson_id, so there's no lesson-existence check to 404 on.
    response = client.get(f"/lessons/{uuid.uuid4()}/resources")
    assert response.status_code == 200
    assert response.json() == []


def test_get_resources_is_scoped_to_the_requested_lesson(
    client: TestClient, db: Session, lesson: Lesson
) -> None:
    other_course = Course(title="Other Course", description="Fixture.")
    other_module = Module(title="Other Module", order=1, course=other_course)
    other_lesson = Lesson(
        title="Other Lesson", body="Body.", order=1, module=other_module
    )
    db.add(other_lesson)
    db.commit()
    db.add(
        Resource(
            lesson_id=other_lesson.id,
            title="Belongs To Other Lesson",
            url="https://example.com/other",
            description="Should never show up for `lesson`.",
            resource_type="video",
            order=1,
        )
    )
    db.commit()

    response = client.get(f"/lessons/{lesson.id}/resources")
    assert response.json() == []
