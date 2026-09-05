import uuid

from pydantic import BaseModel, ConfigDict


class ChoiceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    text: str
    order: int
    # is_correct is intentionally absent — M5.3's whole point is serving
    # questions without leaking the answer key. Only touched server-side,
    # at grading time (M5.4).


class QuestionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    question_type: str
    prompt: str
    order: int
    # Empty for an open_ended question — Choice rows only exist for mcq
    # questions in the first place (see Question.choices' own comment).
    choices: list[ChoiceRead]


class QuizRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lesson_id: uuid.UUID
    questions: list[QuestionRead]


class AnswerIn(BaseModel):
    question_id: uuid.UUID
    # Exactly one of these is expected per question, matching its
    # question_type — choice_id for mcq, answer_text for open_ended. Both
    # optional rather than a tagged union: the client sends whichever one
    # applies and the route reads the one it needs for that question's type,
    # ignoring the other if present.
    choice_id: uuid.UUID | None = None
    answer_text: str | None = None


class QuizSubmitRequest(BaseModel):
    answers: list[AnswerIn]


class QuestionResult(BaseModel):
    question_id: uuid.UUID
    question_type: str
    # None means "not graded yet" — true for every open_ended question
    # until M5.5 wires up LLM grading; from M5.5 onward it's only None if
    # the client didn't submit an answer for that question at all.
    correct: bool | None
    # LLM-written feedback, open_ended only (M5.5). Always None for mcq.
    feedback: str | None = None
    # mcq only, always None for open_ended (no single "correct choice"
    # concept there). Revealed here deliberately, unlike ChoiceRead/
    # QuizRead above: this is the *result* of an attempt the learner has
    # already submitted, not the question itself pre-attempt — the
    # answer-key boundary QuizRead enforces is about not leaking it before
    # a learner has committed an answer, not about never showing it at
    # all. Populated for every mcq question in the response, including
    # ones the learner left unanswered, since results are a final review
    # view once submitted, not something to keep guessing at.
    correct_choice_id: uuid.UUID | None = None


class QuizSubmitResponse(BaseModel):
    results: list[QuestionResult]
    # Fraction correct among graded questions only (correct is not None) —
    # so the denominator naturally grows to include open_ended questions
    # once M5.5 makes them gradable, with no change needed here.
    correct_count: int
    graded_count: int
