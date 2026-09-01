import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ExerciseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    lesson_id: uuid.UUID
    prompt: str
    starter_code: str
    order: int
    # test_code is intentionally absent — see the model's own comment.
    # Never add it here without re-reading why it's excluded. It has its
    # own separate schema/endpoint below (M3.11) for the one place it
    # legitimately needs to reach the client at all: grading time.


class ExerciseTestCode(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Served only by GET /exercises/{id}/test-code (authenticated, called
    # by the frontend only at Submit time — never bundled into ExerciseRead
    # or fetched on page load). This is a soft-hidden test, not a truly
    # secret one: grading runs in the learner's own Pyodide sandbox, which
    # means the browser must receive this to run it, and a technically
    # curious user could read it via devtools. That's an explicit,
    # accepted tradeoff for a self-paced learning tool — see the Phase 3B
    # planning note and M3.11's notes for the full reasoning. A genuinely
    # secret test would require server-side execution in a real sandbox,
    # which is exactly the infrastructure commitment Pyodide was chosen to
    # avoid.
    test_code: str


class ExerciseListItem(BaseModel):
    # Built by hand in the route (M3.12), not from_attributes=True off the
    # ORM object — lesson_title comes from a join, and solved is computed
    # from a separate per-user query, so there's no single object with all
    # five of these as real attributes.
    id: uuid.UUID
    lesson_id: uuid.UUID
    lesson_title: str
    prompt: str
    order: int
    solved: bool


class ExerciseSubmissionCreate(BaseModel):
    code: str
    # Computed and reported by the client (Pyodide ran test_code against
    # `code` in-browser) — the server trusts this value rather than
    # re-deriving it, per M3.10's stated security tradeoff.
    passed: bool


class ExerciseSubmissionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    exercise_id: uuid.UUID
    code: str
    passed: bool
    submitted_at: datetime
