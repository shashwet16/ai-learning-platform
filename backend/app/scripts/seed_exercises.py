"""Attach a graded coding exercise to five lessons in "Intro to AI
Engineering" — the ones where writing actual Python is a natural way to
practice the lesson's own concept, rather than every lesson mechanically.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_exercises

Written after discovering, while seeding more quizzes, that the whole
graded-exercise feature (M3.10-M3.12) had been built, tested, and
verified but never actually seeded with any real content — the
`exercises` table had zero rows. Same underlying gap as M5.2's
single-quiz seed, just never separately noticed or reported until now.

Deliberately skips the two purely conceptual "Foundations" lessons
("What is AI Engineering?", "The Modern AI Stack") — a coding exercise
bolted onto a lesson with no code-shaped concept in it would be filler,
not practice. Real courses skip exercises on intro/theory lessons for
the same reason; this isn't a shortcut, it's the honest call.

Safe to run more than once, same idempotence as seed_quiz.py /
seed_more_quizzes.py: iterates lesson-by-lesson and skips any that
already have an exercise (a lesson can have at most one, per
Exercise.lesson_id's unique constraint from M3.10).

Depends on seed_courses.py having already run — looks lessons up by
title rather than creating them.

Every exercise's test_code uses plain `assert` statements only. That's
not a style choice — it's what `runCode()` in the frontend actually
depends on: an unhandled AssertionError is what makes Pyodide's
execution surface as an error (see lib/pyodide.ts), which is what
ExercisePlayground.tsx reads as "failed." A test written as, say, a
silently-swallowed comparison would always report success regardless of
the learner's code.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Exercise, Lesson


def _prompting_fundamentals() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Prompting Fundamentals: the lesson's own rule is 'separate "
            "instructions from the data being acted on.' Write "
            "`format_prompt(instruction, data)`, returning one string "
            "where the instruction appears first, the data appears "
            "second, and the data is clearly delimited (e.g. wrapped in "
            "`---` lines) so a model can tell where the data starts and "
            "ends."
        ),
        starter_code=(
            "def format_prompt(instruction: str, data: str) -> str:\n"
            '    """Return a single prompt string with the instruction\n'
            "    first, then the data, clearly delimited (e.g. with\n"
            "    '---' lines) so a model can tell where it starts and\n"
            "    ends.\n"
            '    """\n'
            "    # TODO: build and return the prompt\n"
            "    pass\n"
        ),
        test_code=(
            "result = format_prompt(\n"
            '    "Summarize the following text.", "Cats are mammals."\n'
            ")\n"
            'assert isinstance(result, str), "must return a string"\n'
            'assert "Summarize the following text." in result, (\n'
            '    "instruction missing from the prompt"\n'
            ")\n"
            'assert "Cats are mammals." in result, "data missing from the prompt"\n'
            'assert result.index("Summarize the following text.") < result.index(\n'
            '    "Cats are mammals."\n'
            '), "instruction must come before the data"\n'
            'assert result.count("---") >= 2, (\n'
            "    \"data should be wrapped in a delimiter, e.g. '---'\"\n"
            ")\n"
            'print("All prompt-formatting checks passed.")\n'
        ),
    )


def _tokens_context_cost() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Tokens, Context Windows, and Cost: using the common "
            "rule-of-thumb that one token is roughly 4 characters of "
            "English text, write `estimate_tokens(text)` (round up — a "
            "partial token still costs a full one) and "
            "`fits_in_context(text, context_window)`, returning whether "
            "`text`'s estimated token count fits within `context_window`."
        ),
        starter_code=(
            "import math\n\n\n"
            "def estimate_tokens(text: str) -> int:\n"
            '    """Estimate the token count of `text` at ~4 characters\n'
            '    per token, rounded up."""\n'
            "    # TODO: implement\n"
            "    pass\n\n\n"
            "def fits_in_context(text: str, context_window: int) -> bool:\n"
            '    """Return True if `text`\'s estimated token count fits\n'
            '    within `context_window` tokens."""\n'
            "    # TODO: implement, reusing estimate_tokens\n"
            "    pass\n"
        ),
        test_code=(
            'assert estimate_tokens("") == 0\n'
            'assert estimate_tokens("abcd") == 1\n'
            'assert estimate_tokens("abcde") == 2, "a partial token still counts"\n'
            'assert estimate_tokens("a" * 100) == 25\n'
            'assert fits_in_context("short text", 1000) is True\n'
            'assert fits_in_context("a" * 40000, 1000) is False\n'
            'print("All token-estimation checks passed.")\n'
        ),
    )


def _rag() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Retrieval-Augmented Generation (RAG): as a simplified stand-in "
            "for real embedding similarity search, write "
            "`find_most_relevant_chunk(query, chunks)`, returning whichever "
            "chunk in `chunks` shares the most words with `query`. Ignore "
            "case and punctuation when comparing words (e.g. 'generation?' "
            "should match 'generation'). Ties go to the earliest chunk."
        ),
        starter_code=(
            "def find_most_relevant_chunk(query: str, chunks: list[str]) -> str:\n"
            '    """Return whichever chunk shares the most words with\n'
            "    `query` (case-insensitive, punctuation ignored). Ties go\n"
            '    to the earliest chunk in the list."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "chunks = [\n"
            '    "Cats are small domesticated mammals that sleep a lot",\n'
            '    "Retrieval augmented generation fetches relevant documents '
            'at query time",\n'
            '    "The stock market closed higher today after a strong '
            'earnings report",\n'
            "]\n"
            "result = find_most_relevant_chunk(\n"
            '    "What is retrieval augmented generation?", chunks\n'
            ")\n"
            "assert result == chunks[1], (\n"
            '    f"expected the RAG chunk, got: {result!r}"\n'
            ")\n\n"
            "result2 = find_most_relevant_chunk(\n"
            '    "Tell me about cats and mammals", chunks\n'
            ")\n"
            "assert result2 == chunks[0], (\n"
            '    f"expected the cats chunk, got: {result2!r}"\n'
            ")\n"
            'print("All retrieval checks passed.")\n'
        ),
    )


def _agentic_systems() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Designing Agentic Systems: the lesson lists 'how many loop "
            "iterations before giving up?' and 'what happens when a tool "
            "call fails?' as key design decisions. Write "
            "`run_with_retries(action, max_attempts)`: call `action()`, "
            "and if it raises, retry until it succeeds or `max_attempts` "
            "total calls have been made, re-raising the last exception if "
            "every attempt failed."
        ),
        starter_code=(
            "from typing import Callable\n\n\n"
            "def run_with_retries(\n"
            "    action: Callable[[], str], max_attempts: int\n"
            ") -> str:\n"
            '    """Call `action()`, retrying on exception up to\n'
            "    `max_attempts` total calls. Return the first successful\n"
            "    result, or re-raise the last exception if every attempt\n"
            '    failed."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'calls = {"count": 0}\n\n\n'
            "def flaky_tool():\n"
            '    calls["count"] += 1\n'
            '    if calls["count"] < 3:\n'
            '        raise RuntimeError("tool call failed")\n'
            '    return "tool succeeded"\n\n\n'
            "result = run_with_retries(flaky_tool, max_attempts=5)\n"
            'assert result == "tool succeeded"\n'
            'assert calls["count"] == 3, "should stop retrying once it succeeds"\n\n'
            'calls["count"] = 0\n\n\n'
            "def always_fails():\n"
            '    calls["count"] += 1\n'
            '    raise RuntimeError("always fails")\n\n\n'
            "try:\n"
            "    run_with_retries(always_fails, max_attempts=3)\n"
            "    raise AssertionError(\n"
            '        "expected it to raise after exhausting attempts"\n'
            "    )\n"
            "except RuntimeError:\n"
            "    pass\n"
            'assert calls["count"] == 3, (\n'
            '    "should give up after exactly max_attempts calls"\n'
            ")\n"
            'print("All agent-loop checks passed.")\n'
        ),
    )


def _evaluation_and_testing() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Evaluation and Testing: the lesson says regression tracking "
            "needs to measure across the whole dataset, not just one "
            "example. Write `score_against_golden_dataset(golden, "
            "predictions)`, where `golden` is a list of "
            '`{"input": ..., "expected": ...}` dicts and `predictions` '
            "is a same-order list of answers. Return the fraction that "
            "match their golden `expected` value, case-insensitively, as "
            "a float between 0.0 and 1.0."
        ),
        starter_code=(
            "def score_against_golden_dataset(\n"
            "    golden: list[dict], predictions: list[str]\n"
            ") -> float:\n"
            '    """Return the fraction of `predictions` that match their\n'
            "    golden `expected` value, case-insensitively (0.0 to\n"
            '    1.0)."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            "golden = [\n"
            '    {"input": "2+2", "expected": "4"},\n'
            '    {"input": "capital of France", "expected": "Paris"},\n'
            '    {"input": "capital of Japan", "expected": "Tokyo"},\n'
            "]\n\n"
            "score = score_against_golden_dataset(\n"
            '    golden, ["4", "paris", "Berlin"]\n'
            ")\n"
            "assert abs(score - (2 / 3)) < 1e-9, (\n"
            '    f"expected 2/3, got {score}"\n'
            ")\n\n"
            "assert (\n"
            '    score_against_golden_dataset(golden, ["4", "Paris", "Tokyo"]) == 1.0\n'
            ")\n"
            "assert (\n"
            '    score_against_golden_dataset(golden, ["x", "y", "z"]) == 0.0\n'
            ")\n"
            'print("All evaluation checks passed.")\n'
        ),
    )


LESSON_BUILDERS: dict[str, Callable[[], Exercise]] = {
    "Prompting Fundamentals": _prompting_fundamentals,
    "Tokens, Context Windows, and Cost": _tokens_context_cost,
    "Retrieval-Augmented Generation (RAG)": _rag,
    "Designing Agentic Systems": _agentic_systems,
    "Evaluation and Testing": _evaluation_and_testing,
}


def _seed_one(db, lesson_title: str, build_exercise: Callable[[], Exercise]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return f'Lesson "{lesson_title}" not found — run seed_courses.py first.'

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
