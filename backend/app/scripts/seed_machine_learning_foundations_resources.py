"""Curate a "Further Reading" list on each of the 6 lessons in "Machine
Learning Foundations" — same reasoning and idempotence as every other
resources seed script: real, existing pages found via actual web
research, not written from memory. Leans heavily on Google's own
Machine Learning Crash Course, since it's a free, well-maintained,
authoritative source that happens to cover this course's exact scope
almost lesson-for-lesson.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_machine_learning_foundations_resources

Depends on seed_machine_learning_foundations.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.resource import Resource


def _supervised_vs_unsupervised() -> list[Resource]:
    return [
        Resource(
            title="What is Machine Learning?",
            url="https://developers.google.com/machine-learning/intro-to-ml/what-is-ml",
            description=(
                "Google's own framing of the field this lesson "
                "introduces, including where supervised and "
                "unsupervised learning each fit."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Supervised Learning",
            url="https://developers.google.com/machine-learning/intro-to-ml/supervised",
            description=(
                "A deeper look at supervised learning specifically — "
                "the category this course spends the rest of its time "
                "in, per this lesson's own stated reasoning."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


def _features_and_labels() -> list[Resource]:
    return [
        Resource(
            title="Framing: Key ML Terminology",
            url="https://developers.google.com/machine-learning/crash-course/framing/ml-terminology",
            description=(
                "The official source of the exact features/label/"
                "example vocabulary this lesson teaches, with more "
                "terminology (labeled vs. unlabeled examples, "
                "inference) than this lesson covers."
            ),
            resource_type="official_docs",
            order=1,
        ),
    ]


def _regression_vs_classification() -> list[Resource]:
    return [
        Resource(
            title="Linear Regression",
            url="https://developers.google.com/machine-learning/crash-course/linear-regression",
            description=(
                "Goes past this lesson's illustrative example into "
                "how a real regression model's coefficients are "
                "actually learned from data, via loss and gradient "
                "descent."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Classification",
            url="https://developers.google.com/machine-learning/crash-course/classification",
            description=(
                "The classification half of the same course — "
                "thresholding, the confusion matrix, and the metrics "
                "the last lesson in this course covers in more depth."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


def _train_val_test() -> list[Resource]:
    return [
        Resource(
            title="Datasets: Dividing the original dataset",
            url="https://developers.google.com/machine-learning/crash-course/overfitting/dividing-datasets",
            description=(
                "The official source for the exact three-way split "
                "this lesson teaches, with more discussion of *why* "
                "a validation set specifically prevents overfitting to "
                "your own decisions during development."
            ),
            resource_type="official_docs",
            order=1,
        ),
    ]


def _overfitting_and_underfitting() -> list[Resource]:
    return [
        Resource(
            title="Overfitting",
            url="https://developers.google.com/machine-learning/crash-course/overfitting/overfitting",
            description=(
                "The official explanation this lesson's own "
                "exam-memorization analogy is a simplified version of, "
                "including common causes: unrepresentative training "
                "data and overly complex models."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Generalization",
            url="https://developers.google.com/machine-learning/crash-course/overfitting/generalization",
            description=(
                "Covers how to actually *detect* overfitting in "
                "practice — diverging training/validation loss curves "
                "— a step past this lesson's conceptual explanation."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


def _accuracy_precision_recall() -> list[Resource]:
    return [
        Resource(
            title="Classification: Accuracy, recall, precision, and related metrics",
            url="https://developers.google.com/machine-learning/crash-course/classification/accuracy-precision-recall",
            description=(
                "The official source for this lesson's own formulas, "
                "with an interactive confusion-matrix exercise and "
                "coverage of the accuracy/precision/recall tradeoff in "
                "more depth."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Precision-Recall",
            url="https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html",
            description=(
                "A real, runnable code example (not just a formula) "
                "computing and plotting precision and recall from an "
                "actual scikit-learn classifier's predictions."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


LESSON_BUILDERS: dict[str, Callable[[], list[Resource]]] = {
    "Supervised vs. Unsupervised Learning": _supervised_vs_unsupervised,
    "Features, Labels, and Training Data": _features_and_labels,
    "Regression vs. Classification": _regression_vs_classification,
    "Training, Validation, and Test Splits": _train_val_test,
    "Overfitting and Underfitting": _overfitting_and_underfitting,
    "Evaluation Metrics: Accuracy, Precision, Recall": _accuracy_precision_recall,
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
            "seed_machine_learning_foundations.py first."
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
