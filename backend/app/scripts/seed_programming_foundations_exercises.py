"""Attach a graded coding exercise to 5 of the 6 lessons in "Programming
Foundations" — same reasoning and idempotence as seed_exercises.py:
"Variables and Values" is skipped as too small a concept to reduce to a
meaningful testable function (there's no real behavior to check beyond
"did you assign a variable," which the lesson's own playground already
covers), matching that script's precedent of skipping purely conceptual
lessons.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_programming_foundations_exercises

Every test_code here uses bare `assert` statements only, same Pyodide
grading contract as every other exercise in this platform (see
lib/pyodide.ts and seed_exercises.py's own docstring for why).

Depends on seed_programming_foundations.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Exercise, Lesson


def _conditionals() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Making Decisions: Conditionals — using this lesson's own "
            "thresholds (`> 25` is hot, `> 10` is mild, otherwise cold), "
            "write `classify_temperature(temperature)`, returning one of "
            'the strings `"hot"`, `"mild"`, or `"cold"`.'
        ),
        starter_code=(
            "def classify_temperature(temperature: float) -> str:\n"
            '    """Return "hot" if temperature > 25, "mild" if > 10,\n'
            '    otherwise "cold" — matching the lesson\'s own example."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'assert classify_temperature(30) == "hot"\n'
            'assert classify_temperature(15) == "mild"\n'
            'assert classify_temperature(5) == "cold"\n'
            'assert classify_temperature(25) == "mild", (\n'
            '    "25 is not > 25, so it falls through to mild"\n'
            ")\n"
            'assert classify_temperature(10) == "cold", (\n'
            '    "10 is not > 10, so it falls through to cold"\n'
            ")\n"
            'print("All conditional checks passed.")\n'
        ),
    )


def _loops() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Loops — using the same `continue`-to-skip-evens technique "
            "as this lesson's playground, write "
            "`odd_numbers_up_to(n)`, returning a list of every odd "
            "number from 1 to `n` inclusive, in order."
        ),
        starter_code=(
            "def odd_numbers_up_to(n: int) -> list[int]:\n"
            '    """Return a list of every odd number from 1 to n\n'
            '    inclusive, in order."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "assert odd_numbers_up_to(1) == [1]\n"
            "assert odd_numbers_up_to(6) == [1, 3, 5]\n"
            "assert odd_numbers_up_to(7) == [1, 3, 5, 7]\n"
            "assert odd_numbers_up_to(2) == [1]\n"
            'print("All loop checks passed.")\n'
        ),
    )


def _functions() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Functions — write `make_full_name(first_name, last_name)`, "
            'returning `"First Last"`. If `last_name` is an empty '
            "string, return just `first_name` with no trailing space."
        ),
        starter_code=(
            "def make_full_name(first_name: str, last_name: str) -> str:\n"
            '    """Return "first_name last_name", or just first_name\n'
            '    (no trailing space) if last_name is empty."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'assert make_full_name("Ada", "Lovelace") == "Ada Lovelace"\n'
            'assert make_full_name("Madonna", "") == "Madonna", (\n'
            '    "an empty last_name must not leave a trailing space"\n'
            ")\n"
            'print("All function checks passed.")\n'
        ),
    )


def _lists() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Lists — using the same `.append()` pattern as this "
            "lesson's example, write `double_each(numbers)`, returning "
            "a *new* list where every number in `numbers` has been "
            "doubled, in the same order."
        ),
        starter_code=(
            "def double_each(numbers: list[int]) -> list[int]:\n"
            '    """Return a new list with every number in `numbers`\n'
            '    doubled, in the same order."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "assert double_each([1, 2, 3]) == [2, 4, 6]\n"
            "assert double_each([]) == []\n"
            "assert double_each([-1, 0, 5]) == [-2, 0, 10]\n\n"
            "original = [1, 2, 3]\n"
            "double_each(original)\n"
            "assert original == [1, 2, 3], (\n"
            '    "double_each must not mutate the original list"\n'
            ")\n"
            'print("All list checks passed.")\n'
        ),
    )


def _dictionaries() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Dictionaries — write `count_words(text)`, returning a dict "
            "mapping each lowercased word in `text` to how many times "
            "it appears. Split on whitespace; ignore case."
        ),
        starter_code=(
            "def count_words(text: str) -> dict[str, int]:\n"
            '    """Return a dict mapping each lowercased word in text\n'
            '    to how many times it appears, split on whitespace."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'assert count_words("") == {}\n'
            'assert count_words("hello world") == {"hello": 1, "world": 1}\n'
            'assert count_words("the cat and the dog") == {\n'
            '    "the": 2,\n'
            '    "cat": 1,\n'
            '    "and": 1,\n'
            '    "dog": 1,\n'
            "}\n"
            'assert count_words("Hello hello HELLO") == {"hello": 3}, (\n'
            '    "word counting must be case-insensitive"\n'
            ")\n"
            'print("All dictionary checks passed.")\n'
        ),
    )


LESSON_BUILDERS: dict[str, Callable[[], Exercise]] = {
    "Making Decisions: Conditionals": _conditionals,
    "Loops": _loops,
    "Functions": _functions,
    "Lists": _lists,
    "Dictionaries": _dictionaries,
}


def _seed_one(db, lesson_title: str, build_exercise: Callable[[], Exercise]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_programming_foundations.py first."
        )

    existing = db.execute(
        select(Exercise).where(Exercise.lesson_id == lesson.id)
    ).scalar_one_or_none()
    if existing is not None:
        return f'Lesson "{lesson_title}" already has an exercise — skipping.'

    exercise = build_exercise()
    exercise.lesson_id = lesson.id
    db.add(exercise)
    db.commit()
    return f'Seeded exercise on "{lesson_title}".'


def seed() -> None:
    db = SessionLocal()
    try:
        for lesson_title, build_exercise in LESSON_BUILDERS.items():
            print(_seed_one(db, lesson_title, build_exercise))
    finally:
        db.close()


if __name__ == "__main__":
    seed()
