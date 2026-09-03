import re

from app.services.llm.base import ChatMessage, LLMProvider

# Deliberately asks for a fixed, parseable format rather than free-form
# prose — the response still has to survive being read back by a regex, the
# same reason M5.4's grading is entirely deterministic and this is the one
# spot in quiz grading that isn't.
_RUBRIC_SYSTEM_PROMPT = (
    "You are grading a learner's short free-text answer to a quiz question "
    "from an AI engineering course. Judge only whether the answer "
    "demonstrates correct understanding of the concept being asked about — "
    "don't penalize wording, brevity, or a missing example if the core "
    "idea is right.\n\n"
    "Respond in exactly this format and nothing else:\n"
    "VERDICT: correct\n"
    "FEEDBACK: <one or two sentences of specific feedback>\n"
    "(use VERDICT: incorrect if the answer misses or misunderstands the "
    "concept)"
)


def _build_prompt(question_prompt: str, answer_text: str) -> list[ChatMessage]:
    return [
        {"role": "system", "content": _RUBRIC_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": (
                f"Question: {question_prompt}\n\nLearner's answer: {answer_text}"
            ),
        },
    ]


def grade_open_ended(
    question_prompt: str, answer_text: str, provider: LLMProvider
) -> tuple[bool, str]:
    """Grade one open-ended answer against its question using the given
    LLM provider and a rubric prompt. Returns (correct, feedback).

    Takes an LLMProvider instance rather than calling get_llm_provider()
    itself — the same separation M4.5's chat endpoint keeps between
    "which provider is configured" (the factory's job) and "what to do
    with one" (this function's job), which also makes this trivially
    testable with FakeProvider.
    """
    reply = provider.generate(_build_prompt(question_prompt, answer_text))

    verdict_match = re.search(r"VERDICT:\s*(correct|incorrect)", reply, re.IGNORECASE)
    feedback_match = re.search(r"FEEDBACK:\s*(.+)", reply, re.IGNORECASE | re.DOTALL)

    # A model that ignores the format entirely is treated as incorrect
    # with its raw reply surfaced as feedback, rather than raising — a
    # malformed grading response shouldn't 500 the whole submission.
    correct = verdict_match is not None and verdict_match.group(1).lower() == "correct"
    feedback = feedback_match.group(1).strip() if feedback_match else reply.strip()
    return correct, feedback
