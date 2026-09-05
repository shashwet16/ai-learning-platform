"""Attach a quiz to each of the 6 lessons in "Programming Foundations" —
same 2-MCQ + 1-open-ended shape and per-lesson idempotence as
seed_more_quizzes.py, just targeting the new course instead of the
existing one.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_programming_foundations_quizzes

Every question's answer key is drawn from that lesson's own body text in
seed_programming_foundations.py, same "answerable purely from the lesson
it's attached to" principle as every other quiz in this platform.

Depends on seed_programming_foundations.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.quiz import Choice, Question, Quiz


def _variables_and_values() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "What happens if you reassign a variable that "
                    "currently holds an int to a string instead?"
                ),
                order=1,
                choices=[
                    Choice(
                        text="Python raises a type error", is_correct=False, order=1
                    ),
                    Choice(
                        text=(
                            "Python allows it — a name can point to a "
                            "value of a different type later"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="The variable keeps its original int type forever",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="When does a typo in a variable name cause an error?",
                order=2,
                choices=[
                    Choice(
                        text="At runtime, the moment that line actually runs",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Before the program runs at all, like a compiled language",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Never — Python silently ignores it",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Name the four basic types mentioned in this lesson and "
                    "give one example value of each."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _conditionals() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="In an if/elif/else chain, how many branches run?",
                order=1,
                choices=[
                    Choice(
                        text=(
                            "Exactly one — the first condition (top to "
                            "bottom) that's True"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Every branch whose condition is True",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Always the else branch, as a fallback check",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="Which of these is a comparison, not an assignment?",
                order=2,
                choices=[
                    Choice(text="age = 20", is_correct=False, order=1),
                    Choice(text="age == 20", is_correct=True, order=2),
                    Choice(text="age += 20", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain the difference between `=` and `==` in your own "
                    "words, and what happens if you write `if age = 20:`."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _loops() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "Which loop should you reach for when you don't know "
                    "in advance how many iterations you'll need?"
                ),
                order=1,
                choices=[
                    Choice(text="for", is_correct=False, order=1),
                    Choice(text="while", is_correct=True, order=2),
                    Choice(
                        text="Neither — Python has no loops for that case",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What does `continue` do inside a loop?",
                order=2,
                choices=[
                    Choice(
                        text="Exits the loop immediately", is_correct=False, order=1
                    ),
                    Choice(
                        text=(
                            "Skips the rest of the current iteration and "
                            "moves to the next one"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="Restarts the loop from the beginning",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson's playground example uses `continue` to "
                    "print only odd numbers. Explain why it does that."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _functions() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What does a function return if it has no `return` statement?",
                order=1,
                choices=[
                    Choice(text="0", is_correct=False, order=1),
                    Choice(text="An empty string", is_correct=False, order=2),
                    Choice(text="None", is_correct=True, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="In `def greet(name):`, what is `name`?",
                order=2,
                choices=[
                    Choice(text="A parameter", is_correct=True, order=1),
                    Choice(text="An argument", is_correct=False, order=2),
                    Choice(text="A return value", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson connects functions to this platform's own "
                    "graded exercises. Explain that connection."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _lists() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What does `fruits[-1]` return?",
                order=1,
                choices=[
                    Choice(text="The first item", is_correct=False, order=1),
                    Choice(text="The last item", is_correct=True, order=2),
                    Choice(
                        text="An error — negative indices aren't allowed",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="Are Python lists mutable (changeable in place)?",
                order=2,
                choices=[
                    Choice(text="Yes", is_correct=True, order=1),
                    Choice(
                        text="No — a new list is created on every change",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Only if declared with the `mutable` keyword",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson says lists are the right structure when "
                    "'order matters.' Give an example of data where order "
                    "matters, and one where it doesn't."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _dictionaries() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "What does `user.get('email')` return if `'email'` "
                    "isn't a key in `user`?"
                ),
                order=1,
                choices=[
                    Choice(text="It raises a KeyError", is_correct=False, order=1),
                    Choice(text="None", is_correct=True, order=2),
                    Choice(text="An empty string", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    'What does `user["email"]` do if `"email"` isn\'t a '
                    "key in `user`?"
                ),
                order=2,
                choices=[
                    Choice(
                        text="Returns None, same as .get()", is_correct=False, order=1
                    ),
                    Choice(text="Raises a KeyError", is_correct=True, order=2),
                    Choice(
                        text="Creates the key with a value of None",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain when you'd reach for a dict instead of a list, "
                    "using the lesson's own reasoning."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


LESSON_BUILDERS: dict[str, Callable[[], Quiz]] = {
    "Variables and Values": _variables_and_values,
    "Making Decisions: Conditionals": _conditionals,
    "Loops": _loops,
    "Functions": _functions,
    "Lists": _lists,
    "Dictionaries": _dictionaries,
}


def _seed_one(db, lesson_title: str, build_quiz: Callable[[], Quiz]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_programming_foundations.py first."
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
