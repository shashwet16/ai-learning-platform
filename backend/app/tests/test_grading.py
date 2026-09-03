from app.services.grading import grade_open_ended
from app.services.llm.base import ChatMessage, LLMProvider


class StubProvider(LLMProvider):
    """Returns a fixed reply regardless of input — lets each test pin the
    exact grader output it wants to parse, the same testing-without-a-
    network idea as FakeProvider but with the reply chosen per test.
    """

    def __init__(self, reply: str) -> None:
        self._reply = reply
        self.calls: list[list[ChatMessage]] = []

    def generate(self, messages: list[ChatMessage]) -> str:
        self.calls.append(messages)
        return self._reply


def test_parses_correct_verdict_and_feedback() -> None:
    provider = StubProvider(
        "VERDICT: correct\nFEEDBACK: Nicely explained with a clear example."
    )
    correct, feedback = grade_open_ended("Why separate instructions?", "...", provider)
    assert correct is True
    assert feedback == "Nicely explained with a clear example."


def test_parses_incorrect_verdict() -> None:
    provider = StubProvider("VERDICT: incorrect\nFEEDBACK: Misses the core idea.")
    correct, feedback = grade_open_ended("Q", "wrong answer", provider)
    assert correct is False
    assert feedback == "Misses the core idea."


def test_verdict_parsing_is_case_insensitive() -> None:
    provider = StubProvider("verdict: Correct\nfeedback: fine")
    correct, _ = grade_open_ended("Q", "a", provider)
    assert correct is True


def test_malformed_reply_is_treated_as_incorrect_with_raw_feedback() -> None:
    # A model that ignores the format shouldn't 500 the submission — it's
    # graded incorrect and its raw reply is surfaced as feedback.
    provider = StubProvider("I think this answer is pretty good actually")
    correct, feedback = grade_open_ended("Q", "a", provider)
    assert correct is False
    assert feedback == "I think this answer is pretty good actually"


def test_feedback_spanning_multiple_lines_is_captured() -> None:
    provider = StubProvider(
        "VERDICT: correct\nFEEDBACK: First sentence.\nSecond sentence."
    )
    _, feedback = grade_open_ended("Q", "a", provider)
    assert feedback == "First sentence.\nSecond sentence."


def test_prompt_includes_question_and_answer() -> None:
    provider = StubProvider("VERDICT: correct\nFEEDBACK: ok")
    grade_open_ended("Explain X", "Because Y", provider)
    user_turn = provider.calls[0][-1]["content"]
    assert "Explain X" in user_turn
    assert "Because Y" in user_turn
