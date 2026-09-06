"""Curate a "Further Reading" list on each of the 6 lessons in "Deep
Learning & Transformers" — same reasoning and idempotence as every
other resources seed script: real, existing pages found via actual web
research, not written from memory. Leans on 3Blue1Brown's deep learning
video series and Jay Alammar's "Illustrated" blog posts, both widely
regarded as the clearest visual explanations of this exact material
anywhere, rather than generic SEO content.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_deep_learning_and_transformers_resources

Depends on seed_deep_learning_and_transformers.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.resource import Resource


def _neurons_and_activations() -> list[Resource]:
    return [
        Resource(
            title="But what is a Neural Network?",
            url="https://www.3blue1brown.com/lessons/neural-networks/",
            description=(
                "3Blue1Brown's animated introduction to exactly what "
                "this lesson describes in words — neurons, weights, "
                "and activations — made visible."
            ),
            resource_type="video",
            order=1,
        ),
    ]


def _forward_and_backprop() -> list[Resource]:
    return [
        Resource(
            title="Gradient descent, how neural networks learn",
            url="https://www.3blue1brown.com/lessons/gradient-descent/",
            description=(
                "A visual walkthrough of gradient descent at the "
                "scale of a real network — thousands of weights, not "
                "this lesson's single toy variable."
            ),
            resource_type="video",
            order=1,
        ),
        Resource(
            title="What is backpropagation really doing?",
            url="https://www.3blue1brown.com/lessons/backpropagation/",
            description=(
                "The direct follow-up, explaining how the gradient "
                "for every individual weight actually gets computed — "
                "the mechanism this lesson names but doesn't derive."
            ),
            resource_type="video",
            order=2,
        ),
    ]


def _embeddings() -> list[Resource]:
    return [
        Resource(
            title="The Illustrated Word2vec",
            url="https://jalammar.github.io/illustrated-word2vec/",
            description=(
                "A gentle, heavily visual introduction to how "
                "embeddings are actually learned from text, going "
                "well past this lesson's hand-written toy example."
            ),
            resource_type="article",
            order=1,
        ),
    ]


def _attention() -> list[Resource]:
    return [
        Resource(
            title="Attention in transformers, visually explained",
            url="https://www.3blue1brown.com/lessons/attention/",
            description=(
                "A full visual walkthrough of query/key/value "
                "attention on a real sentence — the exact mechanism "
                "this lesson describes with a toy example and a "
                "single softmax function."
            ),
            resource_type="video",
            order=1,
        ),
    ]


def _transformer_architecture() -> list[Resource]:
    return [
        Resource(
            title="The Illustrated Transformer",
            url="https://jalammar.github.io/illustrated-transformer/",
            description=(
                "Widely regarded as the clearest walkthrough of the "
                "full transformer architecture anywhere — diagrams "
                "every piece this lesson names (residual connections, "
                "normalization, stacked blocks) working together."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="Attention Is All You Need",
            url="https://arxiv.org/abs/1706.03762",
            description=(
                "The actual 2017 paper that introduced the "
                "transformer this lesson describes — dense and "
                "technical, but the real source everything else "
                "written about transformers since is downstream of."
            ),
            resource_type="paper",
            order=2,
        ),
    ]


def _pretraining_and_finetuning() -> list[Resource]:
    return [
        Resource(
            title="The Illustrated GPT-2",
            url="https://jalammar.github.io/illustrated-gpt2/",
            description=(
                "A visual deep dive into a real pretrained "
                "next-token-prediction model — the base-model half of "
                "this lesson's pretraining/fine-tuning split, made "
                "concrete."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="Illustrating Reinforcement Learning from Human Feedback (RLHF)",
            url="https://huggingface.co/blog/rlhf",
            description=(
                "Covers the fine-tuning half this lesson only "
                "gestures at — how human feedback on which responses "
                "are better actually gets turned into a training "
                "signal for the model."
            ),
            resource_type="article",
            order=2,
        ),
    ]


LESSON_BUILDERS: dict[str, Callable[[], list[Resource]]] = {
    "Neurons, Weights, and Activation Functions": _neurons_and_activations,
    "Forward Pass and Backpropagation": _forward_and_backprop,
    "Embeddings: Turning Tokens into Vectors": _embeddings,
    "The Attention Mechanism": _attention,
    "The Transformer Architecture": _transformer_architecture,
    (
        "From Next-Token Prediction to Chat: Pretraining and Fine-Tuning"
    ): _pretraining_and_finetuning,
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
            "seed_deep_learning_and_transformers.py first."
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
