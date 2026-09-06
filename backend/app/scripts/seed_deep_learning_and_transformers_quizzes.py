"""Attach a quiz to each of the 6 lessons in "Deep Learning &
Transformers" — same 2-MCQ + 1-open-ended shape and per-lesson
idempotence as every other quiz seed script in this platform.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_deep_learning_and_transformers_quizzes

Depends on seed_deep_learning_and_transformers.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.quiz import Choice, Question, Quiz


def _neurons_and_activations() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What does training actually adjust in a neuron?",
                order=1,
                choices=[
                    Choice(
                        text="The activation function's formula",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(text="The weights and bias", is_correct=True, order=2),
                    Choice(text="The number of inputs", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "Why does the lesson say a non-linear activation "
                    "function matters?"
                ),
                order=2,
                choices=[
                    Choice(
                        text=(
                            "Without one, stacking layers still only "
                            "computes one big linear function"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="It makes the network train faster",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="It reduces the number of weights needed",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain, in your own words, what a single neuron "
                    "computes, using the lesson's own weighted-sum-plus-"
                    "bias description."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _forward_and_backprop() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What does a loss function measure?",
                order=1,
                choices=[
                    Choice(
                        text="How many weights the network has",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text=(
                            "How wrong a prediction was compared to "
                            "the correct answer"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="How fast the forward pass ran", is_correct=False, order=3
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What does backpropagation compute for each weight?",
                order=2,
                choices=[
                    Choice(
                        text=(
                            "A gradient — how much that weight "
                            "contributed to the error"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(text="A random new value", is_correct=False, order=2),
                    Choice(
                        text="The weight's original initialization value",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson's gradient_descent_step example minimizes "
                    "(x - 3)². Explain what happens if you call it "
                    "repeatedly, feeding each result back in as the new x."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _embeddings() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What is an embedding?",
                order=1,
                choices=[
                    Choice(
                        text="A learned mapping from a token to a vector of numbers",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="A rule-based dictionary of synonyms",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="The activation function used in a neuron",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What does cosine similarity measure?",
                order=2,
                choices=[
                    Choice(
                        text="How many dimensions two vectors have",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text="How closely two vectors point in the same direction",
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="The exact distance between two tokens in a sentence",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson says cosine similarity between 'cat' and "
                    "'kitten' should be much higher than between 'cat' and "
                    "'car'. Explain why, using the lesson's own reasoning."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _attention() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What are the three vectors each token produces for attention?",
                order=1,
                choices=[
                    Choice(text="Query, key, and value", is_correct=True, order=1),
                    Choice(
                        text="Weight, bias, and gradient", is_correct=False, order=2
                    ),
                    Choice(text="Input, output, and loss", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "Why does the lesson's softmax subtract the max "
                    "score before exponentiating?"
                ),
                order=2,
                choices=[
                    Choice(
                        text="It changes the final result to be more accurate",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text=(
                            "It prevents floating-point overflow "
                            "without changing the result"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="It's required for the weights to sum to 1",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Using the lesson's own 'trophy'/'suitcase' example, "
                    "explain what attention lets the model do that looking "
                    "only at neighboring words couldn't."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _transformer_architecture() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What does a residual (skip) connection do?",
                order=1,
                choices=[
                    Choice(
                        text="Deletes unnecessary weights after training",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text=(
                            "Adds a block's output back to its own "
                            "input, instead of replacing it"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="Skips attention entirely for short sequences",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "What made the transformer's parallel processing "
                    "a big practical deal?"
                ),
                order=2,
                choices=[
                    Choice(
                        text=(
                            "It made training on internet-scale "
                            "datasets practical on real hardware"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="It removed the need for any activation functions",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="It made models require zero training data",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain how a transformer block combines ideas from "
                    "earlier lessons in this course (neurons, attention)."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _pretraining_and_finetuning() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What is the pretraining objective for a base LLM?",
                order=1,
                choices=[
                    Choice(
                        text="Predict the single next token, given all text so far",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Classify text as helpful or unhelpful",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Translate between languages", is_correct=False, order=3
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="Why isn't a base model automatically a good chat assistant?",
                order=2,
                choices=[
                    Choice(
                        text="Base models can't process attention",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text=(
                            "It has no particular reason to behave "
                            "helpfully, only to continue text plausibly"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="Base models are too small to hold a conversation",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson connects this back to 'What is AI "
                    "Engineering?'s claim that AI engineers build on "
                    "pretrained models. Explain that connection."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


LESSON_BUILDERS: dict[str, Callable[[], Quiz]] = {
    "Neurons, Weights, and Activation Functions": _neurons_and_activations,
    "Forward Pass and Backpropagation": _forward_and_backprop,
    "Embeddings: Turning Tokens into Vectors": _embeddings,
    "The Attention Mechanism": _attention,
    "The Transformer Architecture": _transformer_architecture,
    (
        "From Next-Token Prediction to Chat: Pretraining and Fine-Tuning"
    ): _pretraining_and_finetuning,
}


def _seed_one(db, lesson_title: str, build_quiz: Callable[[], Quiz]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_deep_learning_and_transformers.py first."
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
