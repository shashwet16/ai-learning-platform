import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models import Choice, Lesson, Question, Quiz
from app.services.llm.base import ChatMessage, LLMProvider


class StubProvider(LLMProvider):
    """Fixed grader reply, so an open-ended assertion doesn't depend on
    what a real model happens to say. Mirrors test_grading.py's stub.
    """

    def __init__(self, reply: str) -> None:
        self._reply = reply

    def generate(self, messages: list[ChatMessage]) -> str:
        return self._reply


@pytest.fixture
def quiz(db: Session, lesson: Lesson) -> Quiz:
    """One mcq (choices deliberately out of insertion order, to prove the
    relationship's order_by is what sorts them) plus one open_ended.
    """
    quiz = Quiz(
        lesson_id=lesson.id,
        questions=[
            Question(
                question_type="mcq",
                prompt="Which is correct?",
                order=1,
                choices=[
                    Choice(text="Wrong answer", is_correct=False, order=2),
                    Choice(text="Right answer", is_correct=True, order=1),
                ],
            ),
            Question(
                question_type="open_ended",
                prompt="Explain it in your own words.",
                order=2,
                choices=[],
            ),
        ],
    )
    db.add(quiz)
    db.commit()
    return quiz


def _question_by_type(quiz: Quiz, question_type: str) -> Question:
    return next(q for q in quiz.questions if q.question_type == question_type)


# --- GET /lessons/{lesson_id}/quiz ---


def test_get_quiz_returns_questions_and_choices_in_order(
    client: TestClient, lesson: Lesson, quiz: Quiz
) -> None:
    response = client.get(f"/lessons/{lesson.id}/quiz")
    assert response.status_code == 200

    body = response.json()
    assert body["lesson_id"] == str(lesson.id)
    assert [q["order"] for q in body["questions"]] == [1, 2]
    assert [q["question_type"] for q in body["questions"]] == ["mcq", "open_ended"]
    # Seeded 2-then-1; served 1-then-2 via Choice.order.
    assert [c["text"] for c in body["questions"][0]["choices"]] == [
        "Right answer",
        "Wrong answer",
    ]
    assert body["questions"][1]["choices"] == []


def test_get_quiz_never_leaks_the_answer_key(
    client: TestClient, lesson: Lesson, quiz: Quiz
) -> None:
    # The single most important assertion about this endpoint: is_correct
    # is what makes the quiz gradable, and a learner fetching the questions
    # must not receive it. Checked on the raw body, not the parsed schema,
    # so an accidental field on ChoiceRead would still be caught.
    response = client.get(f"/lessons/{lesson.id}/quiz")
    assert "is_correct" not in response.text
    for choice in response.json()["questions"][0]["choices"]:
        assert set(choice) == {"id", "text", "order"}


def test_get_quiz_404s_for_lesson_without_one(
    client: TestClient, lesson: Lesson
) -> None:
    response = client.get(f"/lessons/{lesson.id}/quiz")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "quiz_not_found"


# --- POST /quizzes/{quiz_id}/submit ---


def test_submit_grades_correct_mcq_choice(
    client: TestClient, db: Session, quiz: Quiz
) -> None:
    question = _question_by_type(quiz, "mcq")
    right = next(c for c in question.choices if c.is_correct)

    response = client.post(
        f"/quizzes/{quiz.id}/submit",
        json={
            "answers": [{"question_id": str(question.id), "choice_id": str(right.id)}]
        },
    )
    assert response.status_code == 200

    body = response.json()
    result = next(r for r in body["results"] if r["question_id"] == str(question.id))
    assert result["correct"] is True
    assert result["feedback"] is None
    assert (body["correct_count"], body["graded_count"]) == (1, 1)


def test_submit_grades_incorrect_mcq_choice(
    client: TestClient, db: Session, quiz: Quiz
) -> None:
    question = _question_by_type(quiz, "mcq")
    wrong = next(c for c in question.choices if not c.is_correct)

    response = client.post(
        f"/quizzes/{quiz.id}/submit",
        json={
            "answers": [{"question_id": str(question.id), "choice_id": str(wrong.id)}]
        },
    )
    body = response.json()
    result = next(r for r in body["results"] if r["question_id"] == str(question.id))
    assert result["correct"] is False
    assert (body["correct_count"], body["graded_count"]) == (0, 1)


def test_unanswered_questions_are_ungraded_not_wrong(
    client: TestClient, quiz: Quiz
) -> None:
    # An empty submission still returns a result row per question, but with
    # correct=None — and graded_count stays 0, so the score isn't diluted by
    # questions the learner never attempted.
    response = client.post(f"/quizzes/{quiz.id}/submit", json={"answers": []})
    assert response.status_code == 200

    body = response.json()
    assert len(body["results"]) == 2
    assert all(r["correct"] is None for r in body["results"])
    assert (body["correct_count"], body["graded_count"]) == (0, 0)


def test_open_ended_answer_is_graded_by_the_llm_provider(
    client: TestClient, quiz: Quiz, monkeypatch: pytest.MonkeyPatch
) -> None:
    # get_llm_provider is called directly by the route, not injected via
    # Depends, so it's patched where the route looks it up rather than
    # through app.dependency_overrides.
    monkeypatch.setattr(
        "app.api.routes.quizzes.get_llm_provider",
        lambda: StubProvider("VERDICT: correct\nFEEDBACK: Good explanation."),
    )
    question = _question_by_type(quiz, "open_ended")

    response = client.post(
        f"/quizzes/{quiz.id}/submit",
        json={
            "answers": [
                {"question_id": str(question.id), "answer_text": "Because of X."}
            ]
        },
    )
    body = response.json()
    result = next(r for r in body["results"] if r["question_id"] == str(question.id))
    assert result["correct"] is True
    assert result["feedback"] == "Good explanation."
    assert (body["correct_count"], body["graded_count"]) == (1, 1)


def test_blank_open_ended_answer_is_not_sent_to_the_provider(
    client: TestClient, quiz: Quiz, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Whitespace-free empty text is falsy, so the route must skip grading
    # entirely rather than spend an API call on nothing.
    def fail_if_called() -> LLMProvider:
        raise AssertionError("provider must not be constructed for a blank answer")

    monkeypatch.setattr("app.api.routes.quizzes.get_llm_provider", fail_if_called)
    question = _question_by_type(quiz, "open_ended")

    response = client.post(
        f"/quizzes/{quiz.id}/submit",
        json={"answers": [{"question_id": str(question.id), "answer_text": ""}]},
    )
    assert response.status_code == 200
    result = next(
        r for r in response.json()["results"] if r["question_id"] == str(question.id)
    )
    assert result["correct"] is None


def test_mcq_only_submission_never_constructs_a_provider(
    client: TestClient, quiz: Quiz, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The lazy-construction promise in the route's own comment: a quiz
    # graded entirely from mcq answers must work with no LLM configured.
    def fail_if_called() -> LLMProvider:
        raise AssertionError("provider must not be constructed for mcq-only grading")

    monkeypatch.setattr("app.api.routes.quizzes.get_llm_provider", fail_if_called)
    question = _question_by_type(quiz, "mcq")
    right = next(c for c in question.choices if c.is_correct)

    response = client.post(
        f"/quizzes/{quiz.id}/submit",
        json={
            "answers": [{"question_id": str(question.id), "choice_id": str(right.id)}]
        },
    )
    assert response.status_code == 200
    assert response.json()["correct_count"] == 1


def test_submit_404s_for_unknown_quiz(client: TestClient) -> None:
    response = client.post(f"/quizzes/{uuid.uuid4()}/submit", json={"answers": []})
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "quiz_not_found"
