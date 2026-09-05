"""Attach a sample quiz to each of the six lessons seed_quiz.py doesn't
cover — every lesson in "Intro to AI Engineering" except "Prompting
Fundamentals".

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_more_quizzes

Written in response to real user feedback ("why do I have only one quiz
throughout the lessons?") — seed_quiz.py deliberately seeded just one quiz
as minimal data to build the quiz API against (M5.2); this script closes
that content gap for the rest of the course without touching that one.

Safe to run more than once, same idempotence as seed_quiz.py: iterates
lesson-by-lesson and skips any that already have a quiz (a lesson can
only have one, per Quiz.lesson_id's unique constraint from M5.1), so it
composes cleanly with seed_quiz.py regardless of run order.

Depends on seed_courses.py having already run — looks lessons up by
title rather than creating them.

Each question's answer key is drawn directly from that lesson's own
seeded body text (see seed_courses.py), not invented separately, so the
quiz actually tests what the lesson teaches.
"""

from collections.abc import Callable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models import Choice, Lesson, Question, Quiz


def _what_is_ai_engineering() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What does AI engineering primarily involve?",
                order=1,
                choices=[
                    Choice(
                        text="Building products on top of pretrained models",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Training large language models from scratch",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Designing the GPUs models run on",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "Which of these is listed as a core AI engineering "
                    "concern, beyond traditional software engineering?"
                ),
                order=2,
                choices=[
                    Choice(
                        text="Evaluating non-deterministic outputs",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Writing the model's training loop",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Manually labeling pretraining data",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Name two concerns the lesson says AI engineering adds "
                    "on top of traditional software engineering, and "
                    "briefly explain why each one doesn't really come up "
                    "in software that has no model in it."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _modern_ai_stack() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "Which layer of the stack is responsible for fetching "
                    "relevant context the model doesn't already know?"
                ),
                order=1,
                choices=[
                    Choice(text="Retrieval", is_correct=True, order=1),
                    Choice(text="Model provider", is_correct=False, order=2),
                    Choice(text="Application layer", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="Which of these correctly matches the lesson's request flow?",
                order=2,
                choices=[
                    Choice(
                        text="User -> Application -> Orchestration -> Model",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="User -> Model -> Application -> Orchestration",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Application -> User -> Model -> Orchestration",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Describe what the 'orchestration' layer is responsible "
                    "for, and give an example of something it might do "
                    "beyond simply forwarding text to the model."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _tokens_context_cost() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What does a model actually see text as?",
                order=1,
                choices=[
                    Choice(text="Tokens", is_correct=True, order=1),
                    Choice(text="Individual characters", is_correct=False, order=2),
                    Choice(text="Whole words only", is_correct=False, order=3),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="Why does a long conversation history cost more money?",
                order=2,
                choices=[
                    Choice(
                        text="Providers bill per token, and history adds tokens",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Providers charge a flat fee per conversation",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Longer histories require a larger GPU rental",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson says managing context size is 'a core "
                    "engineering concern, not just a cost optimization.' "
                    "In your own words, explain what it means for context "
                    "size to be an engineering concern, not just a cost one."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _rag() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt="What problem is RAG designed to solve?",
                order=1,
                choices=[
                    Choice(
                        text=(
                            "A model only knows what it was trained on, "
                            "never private or up-to-date data"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Models are too slow to answer in real time",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Models can't format their output as JSON",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt="What is the first step of the typical RAG pipeline?",
                order=2,
                choices=[
                    Choice(
                        text="Split source documents into chunks",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Embed the user's question",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="Insert chunks into the prompt",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Walk through the four steps of a typical RAG pipeline "
                    "in order, and explain what it means to 'embed' a chunk "
                    "or a question."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _agentic_systems() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "What distinguishes an agent from a plain, one-shot " "model call?"
                ),
                order=1,
                choices=[
                    Choice(
                        text=(
                            "It can call tools, observe results, and decide "
                            "what to do next in a loop"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="It always uses a larger, more expensive model",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="It never needs a prompt to get started",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt=(
                    "Which of these is listed as a key design decision when "
                    "building an agent?"
                ),
                order=2,
                choices=[
                    Choice(
                        text="How many loop iterations are allowed before giving up",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Which font the chat UI should use",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="How many GPUs to buy",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "The lesson lists 'what happens when a tool call fails?' "
                    "as a design decision. Why does this need to be decided "
                    "deliberately, rather than left to whatever happens by "
                    "default?"
                ),
                order=3,
                choices=[],
            ),
        ],
    )


def _evaluation_and_testing() -> Quiz:
    return Quiz(
        questions=[
            Question(
                question_type="mcq",
                prompt=(
                    "Why can't AI applications rely on traditional unit " "tests alone?"
                ),
                order=1,
                choices=[
                    Choice(
                        text="LLM output is not deterministic",
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Unit tests can't be written in Python",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="LLM APIs don't return status codes",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="mcq",
                prompt='What is "LLM-as-judge"?',
                order=2,
                choices=[
                    Choice(
                        text=(
                            "Using a second model call to grade the "
                            "first one's output"
                        ),
                        is_correct=True,
                        order=1,
                    ),
                    Choice(
                        text="Letting end users vote on the best response",
                        is_correct=False,
                        order=2,
                    ),
                    Choice(
                        text="A legal review process for AI products",
                        is_correct=False,
                        order=3,
                    ),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt=(
                    "Explain what a 'golden dataset' is, and why regression "
                    "tracking needs to measure a prompt change's effect "
                    "across the whole dataset rather than just one example."
                ),
                order=3,
                choices=[],
            ),
        ],
    )


LESSON_BUILDERS: dict[str, Callable[[], Quiz]] = {
    "What is AI Engineering?": _what_is_ai_engineering,
    "The Modern AI Stack": _modern_ai_stack,
    "Tokens, Context Windows, and Cost": _tokens_context_cost,
    "Retrieval-Augmented Generation (RAG)": _rag,
    "Designing Agentic Systems": _agentic_systems,
    "Evaluation and Testing": _evaluation_and_testing,
}


def _seed_one(db: Session, lesson_title: str, build_quiz: Callable[[], Quiz]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return f'Lesson "{lesson_title}" not found — run seed_courses.py first.'

    existing = db.execute(
        select(Quiz).where(Quiz.lesson_id == lesson.id)
    ).scalar_one_or_none()
    if existing is not None:
        return f'Lesson "{lesson_title}" already has a quiz — skipping.'

    quiz = build_quiz()
    quiz.lesson_id = lesson.id
    db.add(quiz)
    db.commit()

    mcq_count = sum(1 for q in quiz.questions if q.question_type == "mcq")
    open_count = len(quiz.questions) - mcq_count
    return (
        f'Seeded quiz on "{lesson_title}": {mcq_count} MCQ, '
        f"{open_count} open-ended question(s)."
    )


def seed() -> None:
    db = SessionLocal()
    try:
        for lesson_title, build_quiz in LESSON_BUILDERS.items():
            print(_seed_one(db, lesson_title, build_quiz))
    finally:
        db.close()


if __name__ == "__main__":
    seed()
