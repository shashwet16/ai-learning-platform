"""Curate a "Further Reading" list on each of the 6 lessons in
"Programming Foundations" — same reasoning and idempotence as
seed_resources.py: real, existing pages found via actual web research,
not written from memory, picked for durability (the official language
docs, plus one well-regarded independent tutorial per topic) over
whatever ranks first in a search engine.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_programming_foundations_resources

Safe to run more than once: idempotent per (lesson, url) pair, same as
seed_resources.py.

Depends on seed_programming_foundations.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.resource import Resource

_CONTROL_FLOW_DOCS = "https://docs.python.org/3/tutorial/controlflow.html"
_DATA_STRUCTURES_DOCS = "https://docs.python.org/3/tutorial/datastructures.html"


def _variables_and_values() -> list[Resource]:
    return [
        Resource(
            title="An Informal Introduction to Python",
            url="https://docs.python.org/3/tutorial/introduction.html",
            description=(
                "The official Python tutorial's own first real chapter — "
                "numbers, strings, and the basics of assignment, straight "
                "from the language's own documentation rather than a "
                "third party's summary of it."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Basic Data Types in Python: A Quick Exploration",
            url="https://realpython.com/python-data-types/",
            description=(
                "A friendlier tour of the same ground — every built-in "
                "type this lesson mentions (and a few it doesn't yet), "
                "with more worked examples than the official docs bother "
                "with."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _conditionals() -> list[Resource]:
    return [
        Resource(
            title="More Control Flow Tools",
            url=_CONTROL_FLOW_DOCS,
            description=(
                "The official tutorial's chapter covering `if`/`elif`/"
                "`else` in full, including edge cases this lesson "
                "doesn't get into, like chaining comparisons and the "
                "`pass` statement."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Conditional Statements in Python",
            url="https://realpython.com/python-conditional-statements/",
            description=(
                "A gentler, example-heavy walkthrough of the exact "
                "if/elif/else logic this lesson teaches, including "
                "common mistakes beginners make with it."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _loops() -> list[Resource]:
    return [
        Resource(
            title="More Control Flow Tools",
            url=_CONTROL_FLOW_DOCS,
            description=(
                "Same official chapter as the conditionals lesson — it's "
                "also where Python's own docs cover `for`, `while`, "
                "`break`, and `continue` in full."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title='Python "for" Loops: The Pythonic Way',
            url="https://realpython.com/python-for-loop/",
            description=(
                "Goes past this lesson's own scope into what makes a "
                "`for` loop 'Pythonic' — iterating directly over "
                "collections rather than manually indexing into them."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _functions() -> list[Resource]:
    return [
        Resource(
            title="Defining Your Own Python Function",
            url="https://realpython.com/defining-your-own-python-function/",
            description=(
                "A thorough, beginner-paced walk from this lesson's "
                "basic `def`/`return` shape all the way to default "
                "arguments, `*args`/`**kwargs`, and docstrings."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="More Control Flow Tools (Defining Functions)",
            url=_CONTROL_FLOW_DOCS,
            description=(
                "The official tutorial's own section on defining "
                "functions, further down the same chapter as "
                "conditionals and loops."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


def _lists() -> list[Resource]:
    return [
        Resource(
            title="Data Structures",
            url=_DATA_STRUCTURES_DOCS,
            description=(
                "The official tutorial's full chapter on lists — "
                "everything this lesson covers, plus using a list as a "
                "stack or queue and list comprehensions, a step past "
                "this lesson's own scope."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Lists vs Tuples in Python",
            url="https://realpython.com/python-lists-tuples/",
            description=(
                "Covers the mutable list this lesson teaches, plus its "
                "immutable sibling — a natural next question once you "
                "know lists can be changed in place."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _dictionaries() -> list[Resource]:
    return [
        Resource(
            title="Data Structures (Dictionaries)",
            url=_DATA_STRUCTURES_DOCS,
            description=(
                "Same official chapter as the lists lesson — it's also "
                "where the language's own docs define dictionaries as "
                "key-based, unordered-by-design (ordered by insertion "
                "since 3.7) collections."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Dictionaries in Python",
            url="https://realpython.com/python-dicts/",
            description=(
                "A deep, example-driven guide covering everything from "
                "this lesson's basic key lookups to dict comprehensions "
                "and merging dictionaries together."
            ),
            resource_type="article",
            order=2,
        ),
    ]


LESSON_BUILDERS: dict[str, Callable[[], list[Resource]]] = {
    "Variables and Values": _variables_and_values,
    "Making Decisions: Conditionals": _conditionals,
    "Loops": _loops,
    "Functions": _functions,
    "Lists": _lists,
    "Dictionaries": _dictionaries,
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
            "seed_programming_foundations.py first."
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
