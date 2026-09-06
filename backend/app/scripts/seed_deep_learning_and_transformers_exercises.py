"""Attach a graded coding exercise to 4 of the 6 lessons in "Deep
Learning & Transformers" — "The Transformer Architecture" and "From
Next-Token Prediction to Chat" are skipped, same reasoning as every
other course's most conceptual lessons: both describe how pieces already
covered elsewhere fit together at a system level, not a new function
whose correctness a hidden test can check.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_deep_learning_and_transformers_exercises

Every test_code here uses bare `assert` statements only, same Pyodide
grading contract as every other exercise in this platform. No deep
learning libraries used — every exercise is plain Python (math module
only) illustrating the underlying arithmetic, consistent with the
course's own no-library constraint.

Depends on seed_deep_learning_and_transformers.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Exercise, Lesson


def _neurons_and_activations() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Neurons, Weights, and Activation Functions — using the "
            "lesson's own `sigmoid`, write `neuron_output(inputs, "
            "weights, bias)`, returning the sigmoid-activated weighted "
            "sum of `inputs` and `weights`, plus `bias`."
        ),
        starter_code=(
            "import math\n\n\n"
            "def sigmoid(x):\n"
            "    return 1 / (1 + math.exp(-x))\n\n\n"
            "def neuron_output(inputs, weights, bias):\n"
            '    """Return sigmoid(weighted sum of inputs and weights,\n'
            '    plus bias)."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "result = neuron_output([1, 0], [2, -1], 0.5)\n"
            "expected = 1 / (1 + math.exp(-2.5))\n"
            "assert abs(result - expected) < 1e-9\n\n"
            "assert abs(neuron_output([0, 0], [2, -1], 0) - 0.5) < 1e-9, (\n"
            '    "sigmoid(0) is exactly 0.5"\n'
            ")\n"
            'print("All neuron checks passed.")\n'
        ),
    )


def _forward_and_backprop() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Forward Pass and Backpropagation — write the lesson's own "
            "`gradient_descent_step(x, learning_rate)`, taking one "
            "gradient-descent step toward the minimum of `(x - 3)²`, "
            "whose slope at any `x` is `2 * (x - 3)`."
        ),
        starter_code=(
            "def gradient_descent_step(x, learning_rate):\n"
            '    """Take one gradient-descent step toward the minimum\n'
            '    of (x - 3)squared, whose slope at x is 2 * (x - 3)."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "assert abs(gradient_descent_step(0, 0.1) - 0.6) < 1e-9\n"
            "assert abs(gradient_descent_step(3, 0.1) - 3.0) < 1e-9, (\n"
            '    "already at the minimum - the gradient is 0, no movement"\n'
            ")\n"
            "assert abs(gradient_descent_step(5, 0.5) - 3.0) < 1e-9\n"
            'print("All gradient-descent checks passed.")\n'
        ),
    )


def _embeddings() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Embeddings — write the lesson's own `cosine_similarity"
            "(vec_a, vec_b)`, returning how closely two vectors point "
            "in the same direction, from -1 (opposite) to 1 "
            "(identical direction)."
        ),
        starter_code=(
            "import math\n\n\n"
            "def cosine_similarity(vec_a, vec_b):\n"
            '    """Return the cosine similarity of vec_a and vec_b,\n'
            '    from -1 (opposite) to 1 (identical direction)."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "assert abs(cosine_similarity([1, 0], [1, 0]) - 1.0) < 1e-9\n"
            "assert abs(cosine_similarity([1, 0], [0, 1]) - 0.0) < 1e-9\n"
            "assert abs(cosine_similarity([1, 0], [-1, 0]) - (-1.0)) < 1e-9\n"
            'print("All embedding checks passed.")\n'
        ),
    )


def _attention() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "The Attention Mechanism — write the lesson's own "
            "`softmax(scores)`, converting raw scores into weights "
            "that sum to 1, subtracting the max score first for "
            "numerical stability."
        ),
        starter_code=(
            "import math\n\n\n"
            "def softmax(scores):\n"
            '    """Return the softmax of scores: exponentiate each\n'
            "    (after subtracting the max score, for numerical\n"
            '    stability), then normalize so they sum to 1."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "equal = softmax([1.0, 1.0, 1.0])\n"
            "assert all(abs(w - 1 / 3) < 1e-9 for w in equal)\n\n"
            "weighted = softmax([1.0, 2.0, 3.0])\n"
            "assert abs(sum(weighted) - 1.0) < 1e-9\n"
            "assert weighted[2] > weighted[1] > weighted[0], (\n"
            '    "a higher score must produce a higher weight"\n'
            ")\n\n"
            "large = softmax([1000.0, 1000.0])\n"
            "assert abs(large[0] - 0.5) < 1e-9, (\n"
            '    "must stay numerically stable for large scores"\n'
            ")\n"
            'print("All attention checks passed.")\n'
        ),
    )


LESSON_BUILDERS: dict[str, Callable[[], Exercise]] = {
    "Neurons, Weights, and Activation Functions": _neurons_and_activations,
    "Forward Pass and Backpropagation": _forward_and_backprop,
    "Embeddings: Turning Tokens into Vectors": _embeddings,
    "The Attention Mechanism": _attention,
}


def _seed_one(db, lesson_title: str, build_exercise: Callable[[], Exercise]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_deep_learning_and_transformers.py first."
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
