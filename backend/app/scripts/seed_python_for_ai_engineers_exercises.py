"""Attach a graded coding exercise to 5 of the 6 lessons in "Python for
AI Engineers" — same reasoning and idempotence as every other exercise
seed script: "Modules, Packages, and pip" is skipped, since installing a
package is an environment action, not something a hidden test can check
by calling a function.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_python_for_ai_engineers_exercises

Every test_code here uses bare `assert` statements only, same Pyodide
grading contract as every other exercise in this platform.

Depends on seed_python_for_ai_engineers.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Exercise, Lesson


def _default_args_and_kwargs() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Default Arguments and *args/**kwargs — write "
            "`make_profile(name, **kwargs)`, returning a dict with "
            '`"name"` set to `name` plus every keyword argument merged '
            "in."
        ),
        starter_code=(
            "def make_profile(name, **kwargs):\n"
            '    """Return a dict with "name": name, plus every\n'
            '    keyword argument merged in."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'profile = make_profile("Ada", age=27, role="engineer")\n'
            'assert profile == {"name": "Ada", "age": 27, "role": "engineer"}\n\n'
            'solo = make_profile("Grace")\n'
            'assert solo == {"name": "Grace"}\n'
            'print("All kwargs checks passed.")\n'
        ),
    )


def _comprehensions() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "List and Dictionary Comprehensions — write "
            "`evens_squared(numbers)`, returning a list of the square "
            "of every even number in `numbers`, preserving order."
        ),
        starter_code=(
            "def evens_squared(numbers: list[int]) -> list[int]:\n"
            '    """Return the square of every even number in numbers,\n'
            '    preserving order."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "assert evens_squared([1, 2, 3, 4, 5, 6]) == [4, 16, 36]\n"
            "assert evens_squared([1, 3, 5]) == []\n"
            "assert evens_squared([]) == []\n"
            "assert evens_squared([-2, -1, 0]) == [4, 0]\n"
            'print("All comprehension checks passed.")\n'
        ),
    )


def _classes_and_objects() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Classes and Objects — complete the `Rectangle` class: "
            "`__init__` should store `width` and `height`; `area` "
            "should return their product; `perimeter` should return "
            "`2 * (width + height)`."
        ),
        starter_code=(
            "class Rectangle:\n"
            "    def __init__(self, width, height):\n"
            "        # TODO: store width and height on self\n"
            "        pass\n\n"
            "    def area(self):\n"
            "        # TODO: return width * height\n"
            "        pass\n\n"
            "    def perimeter(self):\n"
            "        # TODO: return 2 * (width + height)\n"
            "        pass\n"
        ),
        test_code=(
            "rect = Rectangle(3, 4)\n"
            "assert rect.area() == 12\n"
            "assert rect.perimeter() == 14\n\n"
            "square = Rectangle(5, 5)\n"
            "assert square.area() == 25\n"
            "assert square.perimeter() == 20\n"
            'print("All Rectangle checks passed.")\n'
        ),
    )


def _error_handling() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Handling Errors: try/except — write `safe_divide(a, b)`, "
            "returning `a / b`, or `None` if `b` is `0` — never let it "
            "raise `ZeroDivisionError`."
        ),
        starter_code=(
            "def safe_divide(a: float, b: float) -> float | None:\n"
            '    """Return a / b, or None if b is 0 (never raise\n'
            '    ZeroDivisionError)."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "assert safe_divide(10, 2) == 5.0\n"
            "assert safe_divide(7, 0) is None, (\n"
            '    "dividing by zero must return None, not raise"\n'
            ")\n"
            "assert safe_divide(-9, 3) == -3.0\n"
            'print("All error-handling checks passed.")\n'
        ),
    )


def _json() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Working with JSON — write `get_value_or_none(json_text, "
            "key)`, parsing `json_text` (a JSON object string) and "
            "returning the value at the top-level `key`, or `None` if "
            "the key isn't present."
        ),
        starter_code=(
            "import json\n\n\n"
            "def get_value_or_none(json_text: str, key: str):\n"
            '    """Parse json_text (a JSON object string) and return\n'
            "    the value at the top-level key, or None if the key\n"
            '    isn\'t present."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'assert get_value_or_none(\'{"name": "Ada", "age": 27}\', "name") == (\n'
            '    "Ada"\n'
            ")\n"
            'assert get_value_or_none(\'{"name": "Ada", "age": 27}\', "age") == 27\n'
            'assert get_value_or_none(\'{"name": "Ada"}\', "missing") is None\n'
            'print("All JSON checks passed.")\n'
        ),
    )


LESSON_BUILDERS: dict[str, Callable[[], Exercise]] = {
    "Default Arguments and *args/**kwargs": _default_args_and_kwargs,
    "List and Dictionary Comprehensions": _comprehensions,
    "Classes and Objects": _classes_and_objects,
    "Handling Errors: try/except": _error_handling,
    "Working with JSON": _json,
}


def _seed_one(db, lesson_title: str, build_exercise: Callable[[], Exercise]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_python_for_ai_engineers.py first."
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
