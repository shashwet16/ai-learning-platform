import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import AppError
from app.db.session import get_db
from app.models.quiz import Question, Quiz
from app.schemas.quiz import (
    QuestionResult,
    QuizRead,
    QuizSubmitRequest,
    QuizSubmitResponse,
)
from app.services.grading import grade_open_ended
from app.services.llm.base import LLMProvider
from app.services.llm.factory import get_llm_provider

router = APIRouter(tags=["quizzes"])

# Eager-load questions and their choices in one extra query each, rather
# than two, rather than triggering lazy-loads per question — the same
# N+1-avoidance instinct as M3.3's selectinload. Shared by both routes
# below since both need a quiz's full question/choice tree.
_WITH_QUESTIONS = selectinload(Quiz.questions).selectinload(Question.choices)


@router.get("/lessons/{lesson_id}/quiz", response_model=QuizRead)
def get_quiz_for_lesson(lesson_id: uuid.UUID, db: Session = Depends(get_db)) -> Quiz:
    # Public, no auth — same as the single-exercise GET (M3.10) and
    # course/lesson reads. Nothing here is per-user; a quiz's questions
    # (minus the answer key, handled by QuizRead/ChoiceRead) are the same
    # for every learner.
    quiz = db.scalars(
        select(Quiz).where(Quiz.lesson_id == lesson_id).options(_WITH_QUESTIONS)
    ).one_or_none()
    if quiz is None:
        raise AppError("Quiz not found", status_code=404, code="quiz_not_found")
    return quiz


@router.post("/quizzes/{quiz_id}/submit", response_model=QuizSubmitResponse)
def submit_quiz(
    quiz_id: uuid.UUID, body: QuizSubmitRequest, db: Session = Depends(get_db)
) -> QuizSubmitResponse:
    # Public and stateless, same as the fetch endpoint above — unlike
    # exercise submissions (M3.10), nothing here is persisted or scoped to
    # a user; the roadmap's M5.1 models don't include a QuizSubmission
    # table, so grading is pure computation over what the client just sent.
    quiz = db.scalars(
        select(Quiz).where(Quiz.id == quiz_id).options(_WITH_QUESTIONS)
    ).one_or_none()
    if quiz is None:
        raise AppError("Quiz not found", status_code=404, code="quiz_not_found")

    answers_by_question = {a.question_id: a for a in body.answers}
    # Constructed at most once, lazily — only if an open_ended question
    # with an actual answer is present — rather than once per such
    # question, and never at all for a quiz with none (so a missing
    # MISTRAL_API_KEY only breaks grading that's actually needed).
    provider: LLMProvider | None = None

    results: list[QuestionResult] = []
    for question in quiz.questions:
        answer = answers_by_question.get(question.id)

        if question.question_type == "mcq":
            correct: bool | None = None
            if answer is not None and answer.choice_id is not None:
                correct_choice = next(
                    (c for c in question.choices if c.is_correct), None
                )
                correct = (
                    correct_choice is not None and answer.choice_id == correct_choice.id
                )
            results.append(
                QuestionResult(
                    question_id=question.id,
                    question_type=question.question_type,
                    correct=correct,
                )
            )
        else:
            # open_ended: graded via the LLM provider abstraction from
            # Phase 4, with a rubric prompt (M5.5). Left ungraded
            # (correct=None, feedback=None) if the learner didn't submit
            # any text for it at all, same as an unanswered mcq above.
            correct = None
            feedback = None
            if answer is not None and answer.answer_text:
                if provider is None:
                    provider = get_llm_provider()
                correct, feedback = grade_open_ended(
                    question.prompt, answer.answer_text, provider
                )
            results.append(
                QuestionResult(
                    question_id=question.id,
                    question_type=question.question_type,
                    correct=correct,
                    feedback=feedback,
                )
            )

    graded = [r for r in results if r.correct is not None]
    correct_count = sum(1 for r in graded if r.correct)

    return QuizSubmitResponse(
        results=results,
        correct_count=correct_count,
        graded_count=len(graded),
    )
