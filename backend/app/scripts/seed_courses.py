"""Populate the database with a sample "Intro to AI Engineering" course.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_courses

Safe to run more than once — if a course with the same title already
exists, the script skips seeding instead of creating a duplicate tree.
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Course, Lesson, Module

COURSE_TITLE = "Intro to AI Engineering"


def build_course() -> Course:
    return Course(
        title=COURSE_TITLE,
        description=(
            "A practical introduction to building software on top of large "
            "language models — from core concepts through to shipping a "
            "real application."
        ),
        modules=[
            Module(
                title="Foundations",
                order=1,
                lessons=[
                    Lesson(
                        title="What is AI Engineering?",
                        order=1,
                        body=(
                            "# What is AI Engineering?\n\n"
                            "AI engineering is the practice of building "
                            "products *on top of* pretrained models, rather "
                            "than training models from scratch. It borrows "
                            "from traditional software engineering but adds "
                            "a new set of concerns:\n\n"
                            "- Prompting and context management\n"
                            "- Evaluating non-deterministic outputs\n"
                            "- Cost and latency tradeoffs per request\n"
                            "- Safety and reliability when the model can "
                            "say almost anything\n\n"
                            "This course covers each of these in turn."
                        ),
                    ),
                    Lesson(
                        title="The Modern AI Stack",
                        order=2,
                        body=(
                            "# The Modern AI Stack\n\n"
                            "A typical AI application is composed of a few "
                            "layers:\n\n"
                            "1. **Model provider** — the LLM API itself "
                            "(Anthropic, OpenAI, or a self-hosted model)\n"
                            "2. **Orchestration** — code that constructs "
                            "prompts, calls tools, and manages state\n"
                            "3. **Retrieval** — fetching relevant context "
                            "the model doesn't already know\n"
                            "4. **Application layer** — the actual product "
                            "surface a user interacts with\n\n"
                            "```text\n"
                            "User -> Application -> Orchestration -> Model\n"
                            "                           |\n"
                            "                       Retrieval\n"
                            "```"
                        ),
                    ),
                ],
            ),
            Module(
                title="Working with LLMs",
                order=2,
                lessons=[
                    Lesson(
                        title="Prompting Fundamentals",
                        order=1,
                        body=(
                            "# Prompting Fundamentals\n\n"
                            "A prompt is the only interface you have to "
                            "steer a model's behavior. Effective prompts "
                            "tend to share a few traits:\n\n"
                            "- They state the task explicitly, not "
                            "implicitly\n"
                            "- They show the model the output format they "
                            "expect\n"
                            "- They separate instructions from the data "
                            "being acted on\n\n"
                            "> A model can only respond to what's actually "
                            "in the prompt — it has no access to your "
                            "intentions beyond what you wrote down."
                        ),
                    ),
                    Lesson(
                        title="Tokens, Context Windows, and Cost",
                        order=2,
                        body=(
                            "# Tokens, Context Windows, and Cost\n\n"
                            "Models don't see text as characters — they see "
                            "**tokens**, roughly a few characters each. "
                            "Two practical consequences:\n\n"
                            "- Every model has a maximum **context "
                            "window** — the total tokens (input + output) "
                            "it can handle in one request\n"
                            "- Providers bill per token, so verbose prompts "
                            "and long conversation histories directly cost "
                            "more money\n\n"
                            "Managing context size is a core engineering "
                            "concern, not just a cost optimization."
                        ),
                    ),
                    Lesson(
                        title="Retrieval-Augmented Generation (RAG)",
                        order=3,
                        body=(
                            "# Retrieval-Augmented Generation (RAG)\n\n"
                            "A model only knows what it was trained on, "
                            "which is never your private or up-to-date "
                            "data. RAG fixes this by retrieving relevant "
                            "documents at request time and inserting them "
                            "into the prompt before the model generates a "
                            "response.\n\n"
                            "The typical pipeline:\n\n"
                            "1. Split source documents into chunks\n"
                            "2. Embed each chunk into a vector\n"
                            "3. At query time, embed the question and find "
                            "the nearest chunks\n"
                            "4. Insert those chunks into the prompt as "
                            "context"
                        ),
                    ),
                ],
            ),
            Module(
                title="Building AI Applications",
                order=3,
                lessons=[
                    Lesson(
                        title="Designing Agentic Systems",
                        order=1,
                        body=(
                            "# Designing Agentic Systems\n\n"
                            'An "agent" is a model given the ability to '
                            "call tools and observe their results, then "
                            "decide what to do next — looping until the "
                            "task is done rather than answering in one "
                            "shot.\n\n"
                            "Key design decisions:\n\n"
                            "- Which tools does the model actually need?\n"
                            "- How many loop iterations are allowed before "
                            "giving up?\n"
                            "- What happens when a tool call fails?"
                        ),
                    ),
                    Lesson(
                        title="Evaluation and Testing",
                        order=2,
                        body=(
                            "# Evaluation and Testing\n\n"
                            "Traditional unit tests assume deterministic "
                            "output. LLM output is not deterministic, so "
                            "AI applications need a different testing "
                            "approach:\n\n"
                            "- **Golden datasets** — a fixed set of inputs "
                            "with known-good expected properties\n"
                            "- **LLM-as-judge** — using a second model call "
                            "to grade the first one's output\n"
                            "- **Regression tracking** — measuring whether "
                            "a prompt change made things better or worse "
                            "across the whole dataset, not just one example"
                        ),
                    ),
                ],
            ),
        ],
    )


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.execute(
            select(Course).where(Course.title == COURSE_TITLE)
        ).scalar_one_or_none()
        if existing is not None:
            print(f'Course "{COURSE_TITLE}" already exists — skipping seed.')
            return

        course = build_course()
        db.add(course)
        db.commit()

        lesson_count = sum(len(m.lessons) for m in course.modules)
        print(
            f'Seeded "{COURSE_TITLE}": {len(course.modules)} modules, '
            f"{lesson_count} lessons."
        )
    finally:
        db.close()


if __name__ == "__main__":
    seed()
