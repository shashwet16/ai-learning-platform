"""Attach a quiz to each of the 6 lessons in "Machine Learning
Foundations" — same 2-MCQ + 1-open-ended shape and per-lesson
idempotence as every other quiz seed script in this platform.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_machine_learning_foundations_quizzes

Depends on seed_machine_learning_foundations.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.quiz import Choice, Question, Quiz


def _supervised_vs_unsupervised() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "Grouping customers by purchase history with no "
                    "predefined segments is an example of:"
                ),
                order=1,
                choices=[
                    Choice(text="Supervised learning", is_correct=False, order=1),
                    Choice(text="Unsupervised learning", is_correct=True, order=2),
                    Choice(text="Reinforcement learning", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "What does supervised learning require that "
                    "unsupervised learning doesn't?"
                ),
                order=2,
                choices=[
                    Choice(text="A large dataset", is_correct=False, order=1),
                    Choice(
                        text="Labeled examples with a known right answer",
                        is_correct=True,
                        order=2,
                    ),
                    Choice(text="A neural network", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson says this course focuses on supervised "
                    "learning because it's most relevant to evaluation. "
                    "Explain that connection in your own words."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _features_and_labels() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="In a house-price dataset, which is the label?",
                order=1,
                choices=[
                    Choice(text="Square footage", is_correct=False, order=1),
                    Choice(text="Number of bedrooms", is_correct=False, order=2),
                    Choice(text="The sale price", is_correct=True, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "What does 'garbage in, garbage out' mean in this "
                    "lesson's context?"
                ),
                order=2,
                choices=[
                    Choice(
                        text=(
                            "Training data quality usually matters "
                            "more than which algorithm you pick"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Models should discard incomplete rows automatically",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Only clean code can produce a working model",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Using the lesson's own house-price example, write one "
                    "more training example as a Python dict with features "
                    "and a label."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _regression_vs_classification() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="Predicting a house's exact sale price is:",
                order=1,
                choices=[
                    Choice(text="Regression", is_correct=True, order=1),
                    Choice(text="Classification", is_correct=False, order=2),
                    Choice(text="Unsupervised learning", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="Classifying a photo as cat, dog, or bird is an example of:",
                order=2,
                choices=[
                    Choice(text="Binary classification", is_correct=False, order=1),
                    Choice(text="Multi-class classification", is_correct=True, order=2),
                    Choice(text="Regression", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain why regression and classification need "
                    "different evaluation metrics, using the lesson's own "
                    "reasoning."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _train_val_test() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="Which split should be touched exactly once, at the very end?",
                order=1,
                choices=[
                    Choice(text="Training set", is_correct=False, order=1),
                    Choice(text="Validation set", is_correct=False, order=2),
                    Choice(text="Test set", is_correct=True, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What is the validation set used for?",
                order=2,
                choices=[
                    Choice(
                        text=(
                            "Comparing choices during development "
                            "without touching test data"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Training the model directly", is_correct=False, order=2
                    ),
                    Choice(
                        text="Nothing — it's only used in unsupervised learning",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain what goes wrong if you tune your model based "
                    "on test-set performance, using the lesson's own "
                    "reasoning."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _overfitting_and_underfitting() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "A model with excellent training performance but "
                    "much worse validation performance is:"
                ),
                order=1,
                choices=[
                    Choice(text="Underfitting", is_correct=False, order=1),
                    Choice(text="Overfitting", is_correct=True, order=2),
                    Choice(text="Perfectly fit", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "A model that performs poorly on both training "
                    "and validation data is:"
                ),
                order=2,
                choices=[
                    Choice(text="Overfitting", is_correct=False, order=1),
                    Choice(text="Underfitting", is_correct=True, order=2),
                    Choice(
                        text="Overfitting on the validation set specifically",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain the lesson's exam-memorization analogy for "
                    "overfitting in your own words."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _accuracy_precision_recall() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="Why can accuracy be misleading on an imbalanced dataset?",
                order=1,
                choices=[
                    Choice(
                        text=(
                            "A model that always predicts the majority "
                            "class can score high accuracy while being useless"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Accuracy can never be computed on imbalanced data",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Accuracy only applies to regression",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="Recall answers which question?",
                order=2,
                choices=[
                    Choice(
                        text="Of everything flagged positive, how much actually was?",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text=(
                            "Of everything that actually was "
                            "positive, how much did the model catch?"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="What fraction of all predictions were correct?",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain the lesson's example of a spam filter with "
                    "perfect recall but terrible precision — what is it "
                    "doing wrong?"
                ),
                order=3,
                choices=[],
            ),
        ],
    )


LESSON_BUILDERS: dict[str, Callable[[], Quiz]] = {
    "Supervised vs. Unsupervised Learning": _supervised_vs_unsupervised,
    "Features, Labels, and Training Data": _features_and_labels,
    "Regression vs. Classification": _regression_vs_classification,
    "Training, Validation, and Test Splits": _train_val_test,
    "Overfitting and Underfitting": _overfitting_and_underfitting,
    "Evaluation Metrics: Accuracy, Precision, Recall": _accuracy_precision_recall,
}


def _seed_one(db, lesson_title: str, build_quiz: Callable[[], Quiz]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_machine_learning_foundations.py first."
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
