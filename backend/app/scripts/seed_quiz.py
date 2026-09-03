"""Attach a sample quiz to the "Prompting Fundamentals" lesson.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_quiz

Safe to run more than once — if that lesson already has a quiz, the
script skips seeding instead of creating a duplicate (a lesson can only
have one, per Quiz.lesson_id's unique constraint from M5.1).

Depends on seed_courses.py having already run — it looks up the lesson
by title rather than creating one, the same way M3.10's exercise seeding
attached to an existing seeded lesson instead of inventing its own.
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Choice, Lesson, Question, Quiz

LESSON_TITLE = "Prompting Fundamentals"


def build_quiz() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "Which of these is a trait of an effective prompt, as "
                    'covered in "Prompting Fundamentals"?'
                ),
                order=1,
                choices=[
                    Choice(
                        text="It states the task explicitly, not implicitly",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="It leaves the output format for the model to guess",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="It mixes instructions and data together freely",
                        is_correct=False,
                        order=3,
                    ),
                    Choice(
                        text="It relies on the model inferring unstated intent",
                        is_correct=False,
                        order=4,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=("According to the lesson, what can a model respond to?"),
                order=2,
                choices=[
                    Choice(
                        text="Only what's actually written in the prompt",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Whatever the user privately intended to ask",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Any context from a previous, unrelated session",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "In your own words, explain why separating instructions "
                    "from the data being acted on makes a prompt more "
                    "reliable. Give a short example."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def seed() -> None:
    db = SessionLocal()
    try:
        lesson = db.execute(
            select(Lesson).where(Lesson.title == LESSON_TITLE)
        ).scalar_one_or_none()
        if lesson is None:
            print(f'Lesson "{LESSON_TITLE}" not found — run seed_courses.py first.')
            return

        existing = db.execute(
            select(Quiz).where(Quiz.lesson_id == lesson.id)
        ).scalar_one_or_none()
        if existing is not None:
            print(f'Lesson "{LESSON_TITLE}" already has a quiz — skipping seed.')
            return

        quiz = build_quiz()
        quiz.lesson_id = lesson.id
        db.add(quiz)
        db.commit()

        mcq_count = sum(1 for q in quiz.questions if q.question_type == "mcq")
        open_count = len(quiz.questions) - mcq_count
        print(
            f'Seeded quiz on "{LESSON_TITLE}": {mcq_count} MCQ, '
            f"{open_count} open-ended question(s)."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
