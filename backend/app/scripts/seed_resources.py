"""Curate a "Further Reading" list on each of the 7 lessons in "Intro to
AI Engineering" — real, existing pages from across the web, not
invented ones, picked so that working through a lesson's own body text
plus its resources takes a learner from "just read the lesson" to
"knows where the production-grade version of this topic lives."

Every URL below was looked up and (for the ones with any doubt about
whether the exact address had moved) fetched and confirmed live during
authoring — none are guessed from memory. Picked for durability
(official docs, foundational papers, and posts from the org that
actually built the thing) over whatever currently ranks first in a
search engine, since a "Further Reading" list that rots in six months
isn't much of one.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_resources

Safe to run more than once: idempotent per (lesson, url) pair, not just
per lesson — Resource has no unique constraint on lesson_id the way
Exercise/Quiz do (a lesson can have any number of resources), so the
guard checks each resource's url individually rather than "does this
lesson have anything yet."

Depends on seed_courses.py having already run — looks lessons up by
title rather than creating them.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.resource import Resource


def _what_is_ai_engineering() -> list[Resource]:
    return [
        Resource(
            title="The Rise of the AI Engineer",
            url="https://www.latent.space/p/ai-engineer",
            description=(
                "The essay that named this job. swyx's 2023 piece argues "
                "that a wide range of AI capability that used to take a "
                "research team years is now reachable with API docs and "
                "an afternoon — and traces what discipline grows up "
                "around that shift. Read this to see the 'why' behind "
                "the lesson's own framing of AI engineering as distinct "
                "from ML research."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="What Is an AI Engineer? (And How to Become One)",
            url="https://www.coursera.org/articles/ai-engineer",
            description=(
                "A plainer, more practical companion to the essay above: "
                "what the job actually looks like day to day, what "
                "skills it expects, and how it differs from a data "
                "scientist or ML researcher role in industry hiring "
                "right now."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _modern_ai_stack() -> list[Resource]:
    return [
        Resource(
            title="Emerging Architectures for LLM Applications",
            url="https://a16z.com/2023/06/20/emerging-architectures-for-llm-applications/",
            description=(
                "The reference diagram this lesson's own "
                "User → Application → Orchestration → Model flow is a "
                "simplified version of. Andreessen Horowitz's widely "
                "cited breakdown of the layers real LLM products are "
                "built from — data pipelines, embeddings, vector "
                "stores, orchestration frameworks, and the model layer "
                "itself."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="LLM App Stack (a16z-infra)",
            url="https://github.com/a16z-infra/llm-app-stack",
            description=(
                "A living, continuously updated catalog of real tools "
                "and vendors at every layer of the stack the article "
                "above describes — useful once you're past 'what are "
                "the layers' and into 'which actual product do I reach "
                "for at each one.'"
            ),
            resource_type="repo",
            order=2,
        ),
    ]


def _prompting_fundamentals() -> list[Resource]:
    return [
        Resource(
            title="Prompt Engineering Overview (Anthropic)",
            url="https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview",
            description=(
                "Anthropic's own living reference on prompting Claude — "
                "clarity, examples, XML structuring, role prompting, and "
                "chaining. The production-grade version of the "
                "'separate instructions from data' rule this lesson "
                "teaches, straight from the model vendor's own docs."
            ),
            resource_type="official_docs",
            order=1,
        ),
        Resource(
            title="Anthropic's Interactive Prompt Engineering Tutorial",
            url="https://github.com/anthropics/prompt-eng-interactive-tutorial",
            description=(
                "A free, hands-on notebook course (9 chapters plus an "
                "advanced appendix) that lets you actually run prompts "
                "against a real model and see the difference each "
                "technique makes, rather than just reading about it."
            ),
            resource_type="interactive",
            order=2,
        ),
    ]


def _tokens_context_cost() -> list[Resource]:
    return [
        Resource(
            title="Tiktokenizer",
            url="https://tiktokenizer.vercel.app/",
            description=(
                "Paste text and watch it split into real tokens, "
                "color-coded, across several real model encodings — the "
                "fastest way to build the intuition this lesson's "
                "~4-characters-per-token rule of thumb is only ever an "
                "approximation of."
            ),
            resource_type="interactive",
            order=1,
        ),
        Resource(
            title="OpenAI Tokenizer",
            url="https://platform.openai.com/tokenizer",
            description=(
                "OpenAI's own official tokenizer tool, for the same "
                "kind of hands-on check against the models most "
                "production API traffic actually runs against."
            ),
            resource_type="interactive",
            order=2,
        ),
        Resource(
            title="tiktoken (OpenAI's tokenizer library)",
            url="https://github.com/openai/tiktoken",
            description=(
                "The real, fast BPE tokenizer library production code "
                "actually calls to count tokens before sending a "
                "request — worth a look once you want exact counts "
                "instead of the lesson's rule-of-thumb estimate."
            ),
            resource_type="repo",
            order=3,
        ),
    ]


def _rag() -> list[Resource]:
    return [
        Resource(
            title="Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
            url="https://arxiv.org/abs/2005.11401",
            description=(
                "The original 2020 Lewis et al. paper that named and "
                "introduced RAG. Denser and more technical than the "
                "lesson, but this is the actual source everything else "
                "written about RAG since then is downstream of."
            ),
            resource_type="paper",
            order=1,
        ),
        Resource(
            title="Retrieval-Augmented Generation (RAG)",
            url="https://www.pinecone.io/learn/retrieval-augmented-generation/",
            description=(
                "A far more approachable walk-through of the same idea, "
                "from a vector database vendor whose entire business is "
                "the retrieval half of a RAG pipeline — good next step "
                "before the original paper above, not instead of it."
            ),
            resource_type="article",
            order=2,
        ),
    ]


def _agentic_systems() -> list[Resource]:
    return [
        Resource(
            title="Building Effective AI Agents",
            url="https://www.anthropic.com/engineering/building-effective-agents",
            description=(
                "Anthropic's own field-tested guidance, distinguishing "
                "fixed-path 'workflows' from genuinely autonomous "
                "'agents' and arguing — counterintuitively — that the "
                "most successful production systems use simple, "
                "composable patterns rather than heavyweight frameworks."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="ReAct: Synergizing Reasoning and Acting in Language Models",
            url="https://arxiv.org/abs/2210.03629",
            description=(
                "The paper behind the 'reason, then act, then observe, "
                "then reason again' loop most agent frameworks still "
                "implement under the hood — the theoretical foundation "
                "for this lesson's retry-loop exercise."
            ),
            resource_type="paper",
            order=2,
        ),
        Resource(
            title="Effective Context Engineering for AI Agents",
            url="https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents",
            description=(
                "A newer, more advanced companion piece: once an agent "
                "runs for many steps, what actually goes into its "
                "context window becomes the main lever for reliability — "
                "the production concern that sits just past this "
                "lesson's own scope."
            ),
            resource_type="article",
            order=3,
        ),
    ]


def _evaluation_and_testing() -> list[Resource]:
    return [
        Resource(
            title="Your AI Product Needs Evals",
            url="https://hamel.dev/blog/posts/evals/",
            description=(
                "Widely regarded as the essay that made 'evals' a "
                "mainstream term outside research labs. Hamel Husain's "
                "case for why teams that skip building real evaluation "
                "infrastructure end up unable to tell if a change to "
                "their AI product helped or hurt."
            ),
            resource_type="article",
            order=1,
        ),
        Resource(
            title="OpenAI Evals",
            url="https://github.com/openai/evals",
            description=(
                "A real, open-source framework for writing and running "
                "evaluations against an LLM or an LLM-powered system — "
                "the production-grade version of this lesson's own "
                "golden-dataset scoring exercise."
            ),
            resource_type="repo",
            order=2,
        ),
    ]


LESSON_BUILDERS: dict[str, Callable[[], list[Resource]]] = {
    "What is AI Engineering?": _what_is_ai_engineering,
    "The Modern AI Stack": _modern_ai_stack,
    "Prompting Fundamentals": _prompting_fundamentals,
    "Tokens, Context Windows, and Cost": _tokens_context_cost,
    "Retrieval-Augmented Generation (RAG)": _rag,
    "Designing Agentic Systems": _agentic_systems,
    "Evaluation and Testing": _evaluation_and_testing,
}


def _seed_one(
    db, lesson_title: str, build_resources: Callable[[], list[Resource]]
) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return f'Lesson "{lesson_title}" not found — run seed_courses.py first.'

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
