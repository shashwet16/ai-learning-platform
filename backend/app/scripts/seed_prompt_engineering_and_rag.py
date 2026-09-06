"""Populate the database with "Prompt Engineering & RAG" — course #7 of
the 10-course curriculum plan (see ROADMAP.md's "Curriculum content
expansion plan").

Expands the existing "Prompting Fundamentals" and "Retrieval-Augmented
Generation (RAG)" lessons (from "Intro to AI Engineering") into their
own full course, deliberately going *past* what those two lessons
already cover rather than repeating it — few-shot prompting and
chain-of-thought instead of the basic instructions-vs-data split;
chunking strategy and reranking instead of the basic
chunk-embed-retrieve-insert pipeline. Original writing throughout.

Usage (from backend/, with the venv active):
    python -m app.scripts.seed_prompt_engineering_and_rag

Safe to run more than once — if a course with the same title already
exists, the script skips seeding instead of creating a duplicate tree.
"""

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Course, Lesson, Module

COURSE_TITLE = "Prompt Engineering & RAG"


def build_course() -> Course:
    return Course(
        title=COURSE_TITLE,
        description=(
            "Beyond the basics — few-shot prompting, chain-of-thought, "
            "reliable structured output, and a real RAG pipeline "
            "(chunking strategy, reranking) past the introductory "
            "version in 'Intro to AI Engineering'."
        ),
        modules=[
            Module(
                title="Advanced Prompting Techniques",
                order=1,
                lessons=[
                    Lesson(
                        title="Few-Shot Prompting and Examples",
                        order=1,
                        body=(
                            "# Few-Shot Prompting and Examples\n\n"
                            "A **zero-shot** prompt just describes the "
                            "task in words. A **few-shot** prompt "
                            "shows the model 2-3 worked examples of "
                            "the exact input→output pattern you want, "
                            "before asking it to handle the real "
                            "case:\n\n"
                            "```python\n"
                            "def build_few_shot_prompt(examples, query):\n"
                            "    parts = [\n"
                            '        f"Input: {i}\\nOutput: {o}" for i, o in examples\n'
                            "    ]\n"
                            '    parts.append(f"Input: {query}\\nOutput:")\n'
                            '    return "\\n\\n".join(parts)\n'
                            "```\n\n"
                            "Examples work because some things are "
                            "much easier to *show* than to fully "
                            "*describe* — a desired tone, an output "
                            "format's exact punctuation, or a subtle "
                            "reasoning pattern. Rather than writing "
                            "paragraphs of instructions trying to "
                            "nail down every detail, two or three good "
                            "examples often communicate the pattern "
                            "more reliably than words alone.\n\n"
                            "This isn't free: every example added to "
                            "the prompt is real tokens, counted "
                            "against both the context window and the "
                            "bill, exactly as the 'Tokens, Context "
                            "Windows, and Cost' lesson describes. More "
                            "examples generally help up to a point, "
                            "then hit diminishing returns — the "
                            "engineering judgment is picking the "
                            "*fewest* examples that reliably establish "
                            "the pattern, not the most."
                        ),
                    ),
                    Lesson(
                        title="Chain-of-Thought Reasoning",
                        order=2,
                        body=(
                            "# Chain-of-Thought Reasoning\n\n"
                            "Asking a model to show its reasoning "
                            "before giving a final answer — often "
                            "literally by adding 'think step by step' "
                            "to a prompt — measurably improves "
                            "accuracy on problems that need several "
                            "steps to solve, like arithmetic word "
                            "problems or multi-step logic.\n\n"
                            "The intuition: a model generates its "
                            "answer one token at a time, and each "
                            "token it's already written becomes part "
                            "of the context for the next one. Asked "
                            "to jump straight to a final answer, "
                            "there's no scratch space for intermediate "
                            "work — the model has to get a multi-step "
                            "problem right in one token-by-token pass "
                            "with no chance to reconsider. Asked to "
                            "reason step by step first, each "
                            "intermediate step it writes becomes "
                            "context the model can build on for the "
                            "next step, much the way a person solving "
                            "a hard problem on paper writes down "
                            "intermediate work rather than staring at "
                            "the question until the final answer "
                            "appears.\n\n"
                            "The tradeoff is real, not free: a "
                            "reasoning-first response is a longer "
                            "response, which costs more tokens and "
                            "takes longer to generate — worth it for "
                            "genuinely multi-step problems, wasted "
                            "overhead for a question with a direct "
                            "one-step answer."
                        ),
                    ),
                ],
            ),
            Module(
                title="Structuring Prompts for Reliability",
                order=2,
                lessons=[
                    Lesson(
                        title="Structured Output and Formatting",
                        order=1,
                        body=(
                            "# Structured Output and Formatting\n\n"
                            "A free-form prose reply is fine for a "
                            "human reading it directly, but useless as "
                            "one step in an automated pipeline — the "
                            "next piece of code has nothing reliable "
                            "to parse. Asking the model to reply in a "
                            "structured format, most commonly JSON, "
                            "turns its reply into something a program "
                            "can consume directly, using exactly the "
                            "same `json.loads()` this platform's "
                            "'Working with JSON' lesson covers:\n\n"
                            "```python\n"
                            "import json\n\n"
                            "def extract_json_from_response(response_text):\n"
                            "    text = response_text.strip()\n"
                            '    if text.startswith("```"):\n'
                            '        lines = text.split("\\n")[1:]\n'
                            '        if lines and lines[-1].strip() == "```":\n'
                            "            lines = lines[:-1]\n"
                            '        text = "\\n".join(lines)\n'
                            "    return json.loads(text)\n"
                            "```\n\n"
                            "That fence-stripping step isn't "
                            "paranoia — models frequently wrap JSON "
                            "in a ` ```json ` markdown code fence even "
                            "when explicitly asked for raw JSON, "
                            "since that's the shape JSON most commonly "
                            "appears in in their training data. Code "
                            "calling an LLM and expecting structured "
                            "output back has to handle that "
                            "presentation detail defensively, not "
                            "assume the model will always comply "
                            "exactly."
                        ),
                    ),
                    Lesson(
                        title="System Prompts and Role Instructions",
                        order=2,
                        body=(
                            "# System Prompts and Role Instructions\n\n"
                            "Most chat APIs accept a separate "
                            "**system** message alongside the ongoing "
                            "back-and-forth of user and assistant "
                            "turns. A system message sets standing "
                            "behavior for the *entire* conversation — "
                            "a persona, a set of constraints, an "
                            "output format to always follow — set "
                            "once, rather than repeated inside every "
                            "single user message.\n\n"
                            "This is a different tool from the "
                            "few-shot examples earlier in this course: "
                            "examples shape *what a good answer looks "
                            "like* for a specific kind of question; a "
                            "system prompt shapes *how the model "
                            "behaves* across every question in the "
                            "conversation, including ones no example "
                            "anticipated.\n\n"
                            "One honest caveat worth knowing early: a "
                            "system prompt is an instruction, not a "
                            "security boundary. A sufficiently "
                            "determined user can often get a model to "
                            "ignore, contradict, or reveal its system "
                            "prompt through carefully crafted input — "
                            "known as a **prompt injection**. Anything "
                            "in a system prompt that would be "
                            "genuinely damaging to leak or bypass "
                            "needs enforcement outside the model "
                            "entirely (permissions checks, content "
                            "filtering in real code), not just a "
                            "stern instruction inside the prompt."
                        ),
                    ),
                ],
            ),
            Module(
                title="Building a Real RAG Pipeline",
                order=3,
                lessons=[
                    Lesson(
                        title="Chunking Strategies",
                        order=1,
                        body=(
                            "# Chunking Strategies\n\n"
                            "The existing RAG lesson's pipeline starts "
                            "with 'split source documents into "
                            "chunks' — this lesson is about how to "
                            "actually make that split well, since the "
                            "chunk size genuinely changes retrieval "
                            "quality:\n\n"
                            "- **Too small**, and a chunk loses "
                            "surrounding context needed to make sense "
                            "of it on its own\n"
                            "- **Too large**, and a chunk dilutes the "
                            "one relevant sentence among a lot of "
                            "irrelevant text, hurting how precisely "
                            "embedding similarity can find it — and "
                            "costs more tokens once it's inserted into "
                            "a prompt\n\n"
                            "A common fix for content getting cut off "
                            "awkwardly at a chunk boundary is "
                            "**overlap** — each chunk repeats a bit of "
                            "the end of the previous one:\n\n"
                            "```python\n"
                            "def chunk_text(text, chunk_size, overlap):\n"
                            "    step = chunk_size - overlap\n"
                            "    chunks = []\n"
                            "    start = 0\n"
                            "    while start < len(text):\n"
                            "        chunks.append(text[start:start + chunk_size])\n"
                            "        start += step\n"
                            "    return chunks\n"
                            "```\n\n"
                            "A more sophisticated approach chunks "
                            "along semantic boundaries — paragraphs, "
                            "sections, or headings — rather than a "
                            "fixed character count, so a chunk never "
                            "splits a single idea across two pieces in "
                            "the first place. The right choice depends "
                            "on the source documents: fixed-size "
                            "chunking is simple and works everywhere; "
                            "structure-aware chunking needs documents "
                            "with real structure to key off of, but "
                            "produces cleaner chunks when it's "
                            "available."
                        ),
                    ),
                    Lesson(
                        title="Reranking and Retrieval Quality",
                        order=2,
                        body=(
                            "# Reranking and Retrieval Quality\n\n"
                            "The existing RAG lesson retrieves chunks "
                            "by embedding similarity alone: embed the "
                            "query, find the nearest chunk vectors, "
                            "done. That's fast, but embedding "
                            "similarity is only an approximation of "
                            "true relevance — it can rank a "
                            "superficially similar chunk above a "
                            "genuinely more useful one.\n\n"
                            "**Reranking** adds a second pass: take "
                            "the top handful of candidates the fast "
                            "embedding search already found, then "
                            "score them again with a slower, more "
                            "precise method that looks at the query "
                            "and each candidate *together* rather than "
                            "comparing two vectors computed "
                            "separately. As a simplified stand-in for "
                            "a real reranker (which uses a trained "
                            "model), word overlap already illustrates "
                            "the two-stage shape:\n\n"
                            "```python\n"
                            "def rerank_by_keyword_overlap(query, candidates):\n"
                            "    query_words = set(query.lower().split())\n\n"
                            "    def score(candidate):\n"
                            "        candidate_words = set(candidate.lower().split())\n"
                            "        return len(query_words & candidate_words)\n\n"
                            "    return sorted(candidates, key=score, reverse=True)\n"
                            "```\n\n"
                            "This costs more — a second pass over "
                            "every candidate takes real time — so "
                            "it's only run on the small shortlist the "
                            "first, cheap retrieval step already "
                            "narrowed things down to, not the entire "
                            "document collection. And exactly like the "
                            "existing 'Evaluation and Testing' lesson "
                            "argues, whether reranking actually helped "
                            "is a question for a golden dataset and a "
                            "real metric, not a feeling — measure "
                            "retrieval precision with and without the "
                            "reranking step, on the same queries, "
                            "before trusting that the extra cost paid "
                            "for itself."
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
