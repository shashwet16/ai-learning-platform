"""Attach a quiz to each of the 6 lessons in "Python for AI Engineers" —
same 2-MCQ + 1-open-ended shape and per-lesson idempotence as every other
quiz seed script in this platform.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_python_for_ai_engineers_quizzes

Depends on seed_python_for_ai_engineers.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.quiz import Choice, Question, Quiz


def _default_args_and_kwargs() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What type does `*args` collect its extra arguments into?",
                order=1,
                choices=[
                    Choice(text="A tuple", is_correct=True, order=1),
                    Choice(text="A dict", is_correct=False, order=2),
                    Choice(text="A list", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What's wrong with `def f(items=[]):` as a function signature?",
                order=2,
                choices=[
                    Choice(text="It's a syntax error", is_correct=False, order=1),
                    Choice(
                        text=(
                            "The default list is created once and shared "
                            "across every call, not recreated fresh each time"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="Lists can't be used as default arguments at all",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson says `**kwargs` shows up constantly in real "
                    "libraries. Explain why a function like "
                    "`requests.get(url, **kwargs)` would want that instead "
                    "of listing every possible option by name."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _comprehensions() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What does `[n * n for n in [1, 2, 3]]` evaluate to?",
                order=1,
                choices=[
                    Choice(text="[1, 2, 3]", is_correct=False, order=1),
                    Choice(text="[1, 4, 9]", is_correct=True, order=2),
                    Choice(text="9", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "When does the lesson say a plain `for` loop is the "
                    "more honest choice over a comprehension?"
                ),
                order=2,
                choices=[
                    Choice(
                        text="Never — comprehensions are always better",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text="Once it needs more than one condition or a nested loop",
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="Whenever the list has more than 10 items",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Write, in words, what `{word: len(word) for word in "
                    '["a", "ab"]}` would produce and why.'
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _classes_and_objects() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What is `self` inside a class's method?",
                order=1,
                choices=[
                    Choice(text="The class itself", is_correct=False, order=1),
                    Choice(text="This particular object", is_correct=True, order=2),
                    Choice(text="The method's return value", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="When is `__init__` called?",
                order=2,
                choices=[
                    Choice(
                        text="Automatically, when a new object is created",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Only if you call it manually", is_correct=False, order=2
                    ),
                    Choice(
                        text="Once per class, shared across all objects",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson argues a class is better than 'a loose dict "
                    "plus a separate function' in some cases. Explain when, "
                    "using the lesson's own reasoning."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _error_handling() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "If a `try` block raises a `ValueError` but the "
                    "`except` only names `ZeroDivisionError`, what "
                    "happens?"
                ),
                order=1,
                choices=[
                    Choice(
                        text="The ValueError is silently ignored",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text="The ValueError still crashes the program",
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="Python converts it to a ZeroDivisionError",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="When does a `finally` block run?",
                order=2,
                choices=[
                    Choice(
                        text="Only if an exception was raised",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text="Only if no exception was raised",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text=(
                            "Always — success, failure, or even a "
                            "return on the way out"
                        ),
                        is_correct=True,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson connects try/except to calling model APIs "
                    "specifically. Explain that connection."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _modules_and_pip() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What's the difference between a module and a package?",
                order=1,
                choices=[
                    Choice(
                        text="A module is one file; a package is a folder of modules",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="They're the same thing, just different names",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="A package can only contain standard-library modules",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What is `pip` for?",
                order=2,
                choices=[
                    Choice(text="Running Python scripts", is_correct=False, order=1),
                    Choice(
                        text="Installing packages not in the standard library",
                        is_correct=True,
                        order=2,
                    ),
                    Choice(text="Formatting Python code", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain why real projects pin exact package versions "
                    "instead of just installing 'whatever pip installs "
                    "today,' using the lesson's own reasoning."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _json() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "What Python type does a JSON object become after "
                    "`json.loads()`?"
                ),
                order=1,
                choices=[
                    Choice(text="A dict", is_correct=True, order=1),
                    Choice(text="A list", is_correct=False, order=2),
                    Choice(text="A string", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="Which function converts a Python dict into a JSON string?",
                order=2,
                choices=[
                    Choice(text="json.loads()", is_correct=False, order=1),
                    Choice(text="json.dumps()", is_correct=True, order=2),
                    Choice(text="json.parse()", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson says this is 'the exact mechanism' behind "
                    "every response this platform's backend has sent your "
                    "browser. Explain what it means by that."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


LESSON_BUILDERS: dict[str, Callable[[], Quiz]] = {
    "Default Arguments and *args/**kwargs": _default_args_and_kwargs,
    "List and Dictionary Comprehensions": _comprehensions,
    "Classes and Objects": _classes_and_objects,
    "Handling Errors: try/except": _error_handling,
    "Modules, Packages, and pip": _modules_and_pip,
    "Working with JSON": _json,
}


def _seed_one(db, lesson_title: str, build_quiz: Callable[[], Quiz]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_python_for_ai_engineers.py first."
        )

    existing = db.execute(
        select(Quiz).where(Quiz.lesson_id == lesson.id)
    ).scalar_one_or_none()
    if existing is not None:
        return f'Lesson "{lesson_title}" already has a quiz — skipping.'

    quiz = build_quiz()
    quiz.lesson_id = lesson.id
    db.add(quiz)
    db.commit()
    return f'Seeded quiz on "{lesson_title}".'


def seed() -> None:
    db = SessionLocal()
    try:
        for lesson_title, build_quiz in LESSON_BUILDERS.items():
            print(_seed_one(db, lesson_title, build_quiz))
    finally:
        db.close()


if __name__ == "__main__":
    seed()
