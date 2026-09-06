"""Attach a graded coding exercise to 4 of the 6 lessons in "Prompt
Engineering & RAG" — "Chain-of-Thought Reasoning" and "System Prompts
and Role Instructions" are skipped, same reasoning as every other
course's most conceptual lessons: both describe a prompting technique
or API concept, not a function whose correctness a hidden test can
check.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_prompt_engineering_and_rag_exercises

Every test_code here uses bare `assert` statements only, same Pyodide
grading contract as every other exercise in this platform.

Depends on seed_prompt_engineering_and_rag.py having already run.
"""

from collections.abc import Callable

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Exercise, Lesson


def _few_shot() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Few-Shot Prompting and Examples — write the lesson's own "
            "`build_few_shot_prompt(examples, query)`, where "
            "`examples` is a list of `(input, output)` tuples. Return "
            'one string: each example formatted as `"Input: '
            '...\\nOutput: ..."`, separated by a blank line, followed '
            'by `"Input: {query}\\nOutput:"` — ready for the model '
            "to complete."
        ),
        starter_code=(
            "def build_few_shot_prompt(examples, query):\n"
            '    """Return one prompt string: each (input, output) in\n'
            '    examples formatted as "Input: ...\\nOutput: ...",\n'
            "    separated by a blank line, followed by\n"
            '    "Input: {query}\\nOutput:"."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'examples = [("2+2", "4"), ("3+3", "6")]\n'
            'prompt = build_few_shot_prompt(examples, "5+5")\n'
            'assert "Input: 2+2" in prompt\n'
            'assert "Output: 4" in prompt\n'
            'assert "Input: 3+3" in prompt\n'
            'assert "Output: 6" in prompt\n'
            'assert prompt.endswith("Input: 5+5\\nOutput:"), (\n'
            '    "the final, unanswered query must come last"\n'
            ")\n"
            "assert (\n"
            '    prompt.index("2+2") < prompt.index("3+3") < prompt.index("5+5")\n'
            '), "examples must stay in their original order"\n'
            'print("All few-shot prompt checks passed.")\n'
        ),
    )


def _structured_output() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Structured Output and Formatting — write the lesson's "
            "own `extract_json_from_response(response_text)`: strip a "
            "leading ` ```json ` or ` ``` ` fence and trailing ` ``` ` "
            "if present, then parse the remaining text as JSON."
        ),
        starter_code=(
            "import json\n\n\n"
            "def extract_json_from_response(response_text):\n"
            '    """Strip a leading/trailing markdown code fence, if\n'
            '    present, then parse response_text as JSON."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'assert extract_json_from_response(\'{"a": 1}\') == {"a": 1}\n'
            "assert extract_json_from_response(\n"
            "    '```json\\n{\"a\": 1}\\n```'\n"
            ') == {"a": 1}\n'
            "assert extract_json_from_response(\n"
            "    '```\\n{\"a\": 1}\\n```'\n"
            ') == {"a": 1}, (\n'
            '    "a plain fence with no language tag must also work"\n'
            ")\n"
            'assert extract_json_from_response(\'  {"a": 1}  \') == {"a": 1}\n'
            'print("All structured-output checks passed.")\n'
        ),
    )


def _chunking() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Chunking Strategies — write the lesson's own "
            "`chunk_text(text, chunk_size, overlap)`, splitting "
            "`text` into chunks of at most `chunk_size` characters, "
            "stepping forward by `chunk_size - overlap` characters "
            "each time, until the whole text is covered."
        ),
        starter_code=(
            "def chunk_text(text, chunk_size, overlap):\n"
            '    """Split text into overlapping chunks of at most\n'
            "    chunk_size characters, stepping forward by\n"
            '    (chunk_size - overlap) characters each time."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'text = "ABCDEFGHIJ"\n'
            "chunks = chunk_text(text, chunk_size=4, overlap=1)\n"
            'assert chunks == ["ABCD", "DEFG", "GHIJ", "J"]\n\n'
            "no_overlap = chunk_text(text, chunk_size=5, overlap=0)\n"
            'assert no_overlap == ["ABCDE", "FGHIJ"]\n'
            'print("All chunking checks passed.")\n'
        ),
    )


def _reranking() -> Exercise:
    return Exercise(
        order=1,
        prompt=(
            "Reranking and Retrieval Quality — write the lesson's own "
            "`rerank_by_keyword_overlap(query, candidates)`, "
            "returning `candidates` sorted by word-overlap count with "
            "`query` (case-insensitive), most overlapping first. Ties "
            "keep their original relative order."
        ),
        starter_code=(
            "def rerank_by_keyword_overlap(query, candidates):\n"
            '    """Return candidates sorted by word-overlap count\n'
            "    with query (case-insensitive), most overlapping\n"
            '    first. Ties keep their original relative order."""\n'
            "    # TODO: implement\n"
            "    pass\n"
        ),
        test_code=(
            'query = "python data structures"\n'
            "candidates = [\n"
            '    "python tutorial",\n'
            '    "data structures guide",\n'
            '    "cooking recipes",\n'
            '    "python data science",\n'
            "]\n"
            "result = rerank_by_keyword_overlap(query, candidates)\n"
            "assert result == [\n"
            '    "data structures guide",\n'
            '    "python data science",\n'
            '    "python tutorial",\n'
            '    "cooking recipes",\n'
            "], (\n"
            '    "the two 2-word-overlap candidates must come first, in "\n'
            '    "their original relative order, ahead of the 1-overlap and "\n'
            '    "0-overlap candidates"\n'
            ")\n"
            'print("All reranking checks passed.")\n'
        ),
    )


LESSON_BUILDERS: dict[str, Callable[[], Exercise]] = {
    "Few-Shot Prompting and Examples": _few_shot,
    "Structured Output and Formatting": _structured_output,
    "Chunking Strategies": _chunking,
    "Reranking and Retrieval Quality": _reranking,
}


def _seed_one(db, lesson_title: str, build_exercise: Callable[[], Exercise]) -> str:
    lesson = db.execute(
        select(Lesson).where(Lesson.title == lesson_title)
    ).scalar_one_or_none()
    if lesson is None:
        return (
            f'Lesson "{lesson_title}" not found — run '
            "seed_prompt_engineering_and_rag.py first."
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
