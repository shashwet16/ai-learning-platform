from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app as fastapi_app

# Imported for the side effect of registering every mapper on Base.metadata
# before create_all runs — importing only the models a given test file uses
# would leave the rest of the schema (and their FK targets) uncreated.
from app.models import Course, Lesson, Module  # noqa: F401


@pytest.fixture
def db() -> Generator[Session, None, None]:
    """A fresh, empty in-memory database per test.

    SQLite rather than Postgres: as of SQLAlchemy 2.0 the dialect-specific
    postgresql.UUID subclasses the backend-agnostic Uuid type and renders as
    CHAR(32) here, and Question.question_type's Enum renders as VARCHAR plus
    a CHECK constraint, so the whole schema builds without a live Postgres.

    Built per test with create_all rather than the docs' "join an external
    transaction" savepoint recipe: that recipe needs working SAVEPOINTs, and
    pysqlite's legacy transaction mode emits SAVEPOINT without an enclosing
    BEGIN, so a nested rollback silently fails to participate in the outer
    transaction. A throwaway engine per test sidesteps that entirely, and
    the suite is small enough that the extra create_all costs nothing.

    StaticPool + check_same_thread=False: an in-memory database lives and
    dies with its connection, so TestClient's request thread has to be
    handed the *same* connection this fixture seeded, not a new one.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, autocommit=False, autoflush=False)()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


@pytest.fixture
def client(db: Session) -> Generator[TestClient, None, None]:
    """TestClient wired to the same session `db` hands out.

    The override is cleared in teardown because `app` is a module-level
    singleton shared by every test — a leftover override would silently
    apply to the rest of the suite.
    """
    fastapi_app.dependency_overrides[get_db] = lambda: db
    try:
        yield TestClient(fastapi_app)
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest.fixture
def lesson(db: Session) -> Lesson:
    """A committed Lesson, with the Course/Module its FK chain requires."""
    course = Course(title="Test Course", description="Fixture course.")
    module = Module(title="Test Module", order=1, course=course)
    lesson = Lesson(title="Test Lesson", body="Fixture body.", order=1, module=module)
    db.add(lesson)
    db.commit()
    return lesson
