"""Attach a graded coding exercise to 4 of the 6 lessons in "Machine
Learning Foundations" — "Supervised vs. Unsupervised Learning" and
"Overfitting and Underfitting" are skipped, same reasoning as every
other course's most conceptual lessons: both teach a way of categorizing
or reasoning about a model, not a function whose correctness a hidden
test can check.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_machine_learning_foundations_exercises

Every test_code here uses bare `assert` statements only, same Pyodide
grading contract as every other exercise in this platform. No ML
libraries used — every exercise is plain Python illustrating the
underlying arithmetic or data-shuffling, consistent with the course's
own no-library constraint.

Depends on seed_machine_learning_foundations.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Exercise, Lesson


def _features_and_labels() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Features, Labels, and Training Data — write "
            "`split_features_and_labels(dataset, label_key)`, "
            "splitting a list of example dicts into a list of feature "
            "dicts (every key except `label_key`) and a list of "
            "labels (the value at `label_key`), in the same order."
        ),
        starter_code=(
            "def split_features_and_labels(dataset, label_key):\n"
            '    """Return (features, labels): features is a list of\n'
            "    dicts with every key except label_key, labels is a\n"
            '    list of the values at label_key, in order."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "dataset = [\n"
            '    {"sqft": 1200, "bedrooms": 2, "price": 250_000},\n'
            '    {"sqft": 1800, "bedrooms": 3, "price": 340_000},\n'
            "]\n"
            'features, labels = split_features_and_labels(dataset, "price")\n'
            "assert labels == [250_000, 340_000]\n"
            "assert features == [\n"
            '    {"sqft": 1200, "bedrooms": 2},\n'
            '    {"sqft": 1800, "bedrooms": 3},\n'
            "]\n"
            'print("All feature/label split checks passed.")\n'
        ),
    )


def _regression_vs_classification() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Regression vs. Classification — write `classify_email"
            '(spam_score, threshold=0.5)`, returning `"spam"` if '
            "`spam_score` is *strictly greater than* `threshold`, "
            'otherwise `"not spam"`.'
        ),
        starter_code=(
            "def classify_email(spam_score, threshold=0.5):\n"
            '    """Return "spam" if spam_score > threshold,\n'
            '    otherwise "not spam"."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'assert classify_email(0.8) == "spam"\n'
            'assert classify_email(0.3) == "not spam"\n'
            'assert classify_email(0.5) == "not spam", (\n'
            '    "exactly at the threshold is not spam - strictly greater "\n'
            '    "than, not greater-or-equal"\n'
            ")\n"
            'assert classify_email(0.9, threshold=0.95) == "not spam"\n'
            'print("All classification checks passed.")\n'
        ),
    )


def _train_val_test() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Training, Validation, and Test Splits — write the "
            "lesson's own `split_dataset(data, train_frac=0.7, "
            "val_frac=0.15)`, returning `(train, val, test)`: the "
            "first `train_frac` of `data` as `train`, the next "
            "`val_frac` as `val`, and everything remaining as `test`."
        ),
        starter_code=(
            "def split_dataset(data, train_frac=0.7, val_frac=0.15):\n"
            '    """Return (train, val, test): the first train_frac of\n'
            '    data, the next val_frac, and the remainder."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "data = list(range(10))\n"
            "train, val, test = split_dataset(data)\n"
            "assert train == [0, 1, 2, 3, 4, 5, 6]\n"
            "assert val == [7]\n"
            "assert test == [8, 9]\n"
            "assert train + val + test == data, (\n"
            '    "every item must end up in exactly one split"\n'
            ")\n"
            'print("All train/val/test split checks passed.")\n'
        ),
    )


def _accuracy_precision_recall() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Evaluation Metrics — write `evaluate_predictions"
            "(predictions, actuals)`, where both are same-length "
            "lists of booleans (`True` = positive). Compare them to "
            "derive true positives, false positives, and false "
            "negatives, then return `(precision, recall)` using the "
            "lesson's own formulas."
        ),
        starter_code=(
            "def evaluate_predictions(predictions, actuals):\n"
            '    """Return (precision, recall), computed by comparing\n'
            "    predictions to actuals (both lists of booleans) to\n"
            '    derive true/false positives/negatives."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "predictions = [True, True, False, True, False]\n"
            "actuals = [True, False, False, True, True]\n"
            "# true positives: 0, 3 | false positive: 1 | false negative: 4\n"
            "precision, recall = evaluate_predictions(predictions, actuals)\n"
            "assert abs(precision - (2 / 3)) < 1e-9\n"
            "assert abs(recall - (2 / 3)) < 1e-9\n\n"
            "assert evaluate_predictions([True, False], [True, False]) == (\n"
            "    1.0,\n"
            "    1.0,\n"
            ")\n"
            'print("All evaluation-metric checks passed.")\n'
        ),
    )


LESSON_BUILDERS: dict[str, Callable[[], Exercise]] = {
    "Features, Labels, and Training Data": _features_and_labels,
    "Regression vs. Classification": _regression_vs_classification,
    "Training, Validation, and Test Splits": _train_val_test,
    "Evaluation Metrics: Accuracy, Precision, Recall": _accuracy_precision_recall,
}


def _seed_one(db, lesson_title: str, build_exercise: Callable[[], Exercise]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_machine_learning_foundations.py first."
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
