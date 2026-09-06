"""Curate a "Further Reading" list on each of the 6 lessons in "Prompt
Engineering & RAG" — same reasoning and idempotence as every other
resources seed script: real, existing pages found via actual web
research, not written from memory.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_prompt_engineering_and_rag_resources

Depends on seed_prompt_engineering_and_rag.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.resource import Resource


def _few_shot() -> list[Resource]:
    return [
        Resource(
            title="Prompt engineering",
            url="https://developers.openai.com/api/docs/guides/prompt-engineering",
            description=(
                "OpenAI's own guidance on few-shot prompting, "
                "including its own recommendation to try zero-shot "
                "first and add examples only when needed."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Include few-shot examples",
            url="https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompts/few-shot-examples",
            description=(
                "Google Cloud's own take on the same technique, with "
                "guidance on how many examples to include and how to "
                "pick a diverse set."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


def _chain_of_thought() -> list[Resource]:
    return [
        Resource(
            title=(
                "Chain-of-Thought Prompting Elicits Reasoning in "
                "Large Language Models"
            ),
            url="https://arxiv.org/abs/2201.11903",
            description=(
                "The original 2022 Wei et al. paper that introduced "
                "and named chain-of-thought prompting — the actual "
                "source behind this lesson's own explanation."
            ),
            resource_type="paper",
            order=1,
        ),
    ]


def _structured_output() -> list[Resource]:
    return [
        Resource(
            title="Increase output consistency (JSON mode)",
            url="https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/increase-consistency",
            description=(
                "Anthropic's own guidance on getting reliable "
                "structured output from Claude, including format "
                "specification and — for guaranteed schema "
                "compliance — real Structured Outputs support."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Get structured output from agents",
            url="https://platform.claude.com/docs/en/agent-sdk/structured-outputs",
            description=(
                "The API-level mechanism behind guaranteed schema "
                "compliance — a step past this lesson's own "
                "fence-stripping fallback for when a provider doesn't "
                "guarantee valid JSON."
            ),
            resource_type="official_docs",
            order=2,
        ),
    ]


def _system_prompts() -> list[Resource]:
    return [
        Resource(
            title="LLM01: Prompt Injection",
            url="https://genai.owasp.org/llmrisk2023-24/llm01-24-prompt-injection/",
            description=(
                "OWASP's own top-ranked LLM security risk — the real, "
                "documented attack class behind this lesson's own "
                "caveat that a system prompt is an instruction, not a "
                "security boundary."
            ),
            resource_type="official_docs",
            order=1,
        ),
    ]


def _chunking() -> list[Resource]:
    return [
        Resource(
            title="Chunking Strategies for LLM Applications",
            url="https://www.pinecone.io/learn/chunking-strategies/",
            description=(
                "Goes past this lesson's fixed-size example into "
                "several real chunking strategies, including semantic "
                "chunking by topic shift."
            ),
            resource_type="article",
            order=1,
        ),
    ]


def _reranking() -> list[Resource]:
    return [
        Resource(
            title="Rerankers and Two-Stage Retrieval",
            url="https://www.pinecone.io/learn/series/rag/rerankers/",
            description=(
                "Covers a real reranking model (a cross-encoder) in "
                "place of this lesson's simplified word-overlap "
                "stand-in, and explains why the two-stage "
                "retrieve-then-rerank shape exists at all."
            ),
            resource_type="article",
            order=1,
        ),
    ]


LESSON_BUILDERS: dict[str, Callable[[], list[Resource]]] = {
    "Few-Shot Prompting and Examples": _few_shot,
    "Chain-of-Thought Reasoning": _chain_of_thought,
    "Structured Output and Formatting": _structured_output,
    "System Prompts and Role Instructions": _system_prompts,
    "Chunking Strategies": _chunking,
    "Reranking and Retrieval Quality": _reranking,
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
            "seed_prompt_engineering_and_rag.py first."
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
