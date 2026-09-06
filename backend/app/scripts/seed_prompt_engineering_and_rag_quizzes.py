"""Attach a quiz to each of the 6 lessons in "Prompt Engineering & RAG"
— same 2-MCQ + 1-open-ended shape and per-lesson idempotence as every
other quiz seed script in this platform.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_prompt_engineering_and_rag_quizzes

Depends on seed_prompt_engineering_and_rag.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Lesson
from app.models.quiz import Choice, Question, Quiz


def _few_shot() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What is a few-shot prompt?",
                order=1,
                choices=[
                    Choice(
                        text="A prompt with no examples, just instructions",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text=(
                            "A prompt that shows 2-3 worked examples "
                            "before the real task"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="A prompt sent to several models at once",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What's the real cost of adding more examples to a prompt?",
                order=2,
                choices=[
                    Choice(
                        text="There is no cost — more examples are always free",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text=(
                            "Every example is real tokens, counted "
                            "against context and cost"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="Extra examples make the model refuse to answer",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain why examples can communicate a pattern more "
                    "reliably than written instructions, using the "
                    "lesson's own reasoning."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _chain_of_thought() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="Chain-of-thought prompting most helps with:",
                order=1,
                choices=[
                    Choice(
                        text="Single-step, direct factual questions",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text="Multi-step problems like arithmetic word problems",
                        is_correct=True,
                        order=2,
                    ),
                    Choice(text="Making responses shorter", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What's the tradeoff the lesson names for chain-of-thought?",
                order=2,
                choices=[
                    Choice(text="It has no downside at all", is_correct=False, order=1),
                    Choice(
                        text=(
                            "Longer responses cost more tokens and "
                            "take longer to generate"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="It only works with few-shot examples present",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain the lesson's analogy between chain-of-thought "
                    "and a person solving a hard problem on paper."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _structured_output() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "Why does the lesson's extract_json_from_response "
                    "strip markdown fences?"
                ),
                order=1,
                choices=[
                    Choice(
                        text=(
                            "Models often wrap JSON in a fence even "
                            "when asked for raw JSON"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="JSON is never valid without a fence",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Fences make json.loads() run faster",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "Why does structured output matter for automated "
                    "pipelines specifically?"
                ),
                order=2,
                choices=[
                    Choice(
                        text="Free-form prose is nothing a program can reliably parse",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="It makes the model respond faster",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="It's required by every LLM provider's API",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain how this lesson connects to 'Working with "
                    "JSON' from Python for AI Engineers."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _system_prompts() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What does a system prompt set, compared to a user message?",
                order=1,
                choices=[
                    Choice(
                        text="Standing behavior for the entire conversation",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="The answer to one specific question only",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(text="The model's training data", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="Is a system prompt a real security boundary?",
                order=2,
                choices=[
                    Choice(
                        text="Yes — a model can never be made to ignore it",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text=(
                            "No — it's an instruction, and can "
                            "potentially be bypassed via prompt injection"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="Only for open-source models", is_correct=False, order=3
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain the lesson's distinction between what "
                    "few-shot examples shape versus what a system prompt "
                    "shapes."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _chunking() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What goes wrong with chunks that are too large?",
                order=1,
                choices=[
                    Choice(
                        text="They lose surrounding context", is_correct=False, order=1
                    ),
                    Choice(
                        text=(
                            "They dilute the relevant text and cost "
                            "more tokens once inserted"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="They can't be embedded at all", is_correct=False, order=3
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What problem does overlap between chunks solve?",
                order=2,
                choices=[
                    Choice(
                        text="It reduces the total number of chunks needed",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text=(
                            "It stops content from being awkwardly "
                            "cut off at a chunk boundary"
                        ),
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="It makes embeddings compute faster",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain when the lesson says structure-aware chunking "
                    "(by paragraph/section) is worth it over fixed-size "
                    "chunking."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _reranking() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "Why isn't embedding similarity alone always "
                    "enough for good retrieval?"
                ),
                order=1,
                choices=[
                    Choice(
                        text=(
                            "It's only an approximation and can rank "
                            "a superficially similar chunk too high"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Embedding similarity is always 100% accurate",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Embeddings can't be compared to each other",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "Why is reranking only run on a small shortlist, "
                    "not every document?"
                ),
                order=2,
                choices=[
                    Choice(
                        text="Reranking can only handle a handful of items ever",
                        is_correct=False,
                        order=1,
                    ),
                    Choice(
                        text="It's a slower, more expensive second pass",
                        is_correct=True,
                        order=2,
                    ),
                    Choice(
                        text="It's illegal to rerank more than 10 items",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain how the lesson says you should actually check "
                    "whether reranking helped, connecting it to "
                    "'Evaluation and Testing.'"
                ),
                order=3,
                choices=[],
            ),
        ],
    )


LESSON_BUILDERS: dict[str, Callable[[], Quiz]] = {
    "Few-Shot Prompting and Examples": _few_shot,
    "Chain-of-Thought Reasoning": _chain_of_thought,
    "Structured Output and Formatting": _structured_output,
    "System Prompts and Role Instructions": _system_prompts,
    "Chunking Strategies": _chunking,
    "Reranking and Retrieval Quality": _reranking,
}


def _seed_one(db, lesson_title: str, build_quiz: Callable[[], Quiz]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_prompt_engineering_and_rag.py first."
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
