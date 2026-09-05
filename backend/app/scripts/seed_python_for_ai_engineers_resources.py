"""Curate a "Further Reading" list on each of the 6 lessons in "Python
for AI Engineers" — same reasoning and idempotence as every other
resources seed script: real, existing pages found via actual web
research, not written from memory.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_python_for_ai_engineers_resources

Depends on seed_python_for_ai_engineers.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.resource import Resource


def _default_args_and_kwargs() -> list[Resource]:
    return [
        Resource(
            title="Python args and kwargs: Demystified",
            url="https://realpython.com/python-kwargs-and-args/",
            description=(
                "A full walkthrough of `*args`/`**kwargs`, including "
                "the unpacking operators used on the *calling* side, "
                "not just the receiving side this lesson covers."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="More Control Flow Tools (Defining Functions)",
            url="https://docs.python.org/3/tutorial/controlflow.html",
            description=(
                "The official tutorial's own section on default "
                "argument values and arbitrary argument lists."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


def _comprehensions() -> list[Resource]:
    return [
        Resource(
            title="Python List Comprehension: Tutorial With Examples",
            url="https://realpython.com/list-comprehension-python/",
            description=(
                "Goes further than this lesson into performance "
                "characteristics and when a comprehension is (and "
                "isn't) actually the more readable choice."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="Data Structures (List Comprehensions)",
            url="https://docs.python.org/3/tutorial/datastructures.html",
            description=(
                "The official tutorial's own section on list "
                "comprehensions, including nested comprehensions this "
                "lesson doesn't cover."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


def _classes_and_objects() -> list[Resource]:
    return [
        Resource(
            title="Classes",
            url="https://docs.python.org/3/tutorial/classes.html",
            description=(
                "The official tutorial's full chapter on classes — "
                "everything this lesson covers, plus inheritance and "
                "private variables, both a step past this lesson's "
                "own scope."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Object-Oriented Programming (OOP) in Python",
            url="https://realpython.com/python3-object-oriented-programming/",
            description=(
                "A much longer, example-driven guide covering the "
                "same `__init__`/`self` basics this lesson teaches, "
                "then continuing into inheritance and the broader OOP "
                "vocabulary (encapsulation, polymorphism)."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _error_handling() -> list[Resource]:
    return [
        Resource(
            title="Errors and Exceptions",
            url="https://docs.python.org/3/tutorial/errors.html",
            description=(
                "The official tutorial's full chapter on try/except/"
                "finally, including raising your own exceptions — a "
                "step past what this lesson covers."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Python Exceptions: An Introduction",
            url="https://realpython.com/python-exceptions/",
            description=(
                "A gentler walkthrough of the same try/except "
                "mechanics this lesson teaches, plus a worked example "
                "of writing a custom exception class."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _modules_and_pip() -> list[Resource]:
    return [
        Resource(
            title="Installing Packages",
            url="https://packaging.python.org/tutorials/installing-packages/",
            description=(
                "The official Python Packaging User Guide's own "
                "tutorial — covers `pip install` plus virtual "
                "environments, the next concept this lesson doesn't "
                "get into but every real project needs."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="pip documentation",
            url="https://pip.pypa.io/",
            description=(
                "pip's own official reference — every command and "
                "flag beyond the single `pip install` this lesson "
                "shows."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


def _json() -> list[Resource]:
    return [
        Resource(
            title="JSON encoder and decoder",
            url="https://docs.python.org/3/library/json.html",
            description=(
                "The official `json` module reference — every "
                "argument `loads()`/`dumps()` accept beyond this "
                "lesson's basic usage."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Working With JSON Data in Python",
            url="https://realpython.com/python-json/",
            description=(
                "Extends this lesson's basic parsing into reading and "
                "writing whole JSON files and validating JSON "
                "structure — the shape most real API integrations "
                "actually need."
            ),
            resource_type="article",
            order=2,
        ),
    ]


LESSON_BUILDERS: dict[str, Callable[[], list[Resource]]] = {
    "Default Arguments and *args/**kwargs": _default_args_and_kwargs,
    "List and Dictionary Comprehensions": _comprehensions,
    "Classes and Objects": _classes_and_objects,
    "Handling Errors: try/except": _error_handling,
    "Modules, Packages, and pip": _modules_and_pip,
    "Working with JSON": _json,
}


def _seed_one(
    db, lesson_title: str, build_resources: Callable[[], list[Resource]]
) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_python_for_ai_engineers.py first."
        )

    existing_urls = set(
        db.execute(
            select(Resource.url).where(Resource.lesson_id == lesson.id)
        ).scalars()
    )

    seeded = 0
    skipped = 0
    for resource in build_resources():
        if resource.url in existing_urls:
            skipped += 1
            continue
        resource.lesson_id = lesson.id
        db.add(resource)
        seeded += 1
    db.commit()
    return f'"{lesson_title}": seeded {seeded}, skipped {skipped} already-present.'


def seed() -> None:
    db = SessionLocal()
    try:
        for lesson_title, build_resources in LESSON_BUILDERS.items():
            print(_seed_one(db, lesson_title, build_resources))
    finally:
        db.close()


if __name__ == "__main__":
    seed()
