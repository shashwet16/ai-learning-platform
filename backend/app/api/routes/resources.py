import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.resource import Resource
from app.schemas.resource import ResourceRead

router = APIRouter(tags=["resources"])


@router.get("/lessons/{lesson_id}/resources", response_model=list[ResourceRead])
def get_resources_for_lesson(
    lesson_id: uuid.UUID, db: Session = Depends(get_db)
) -> list[Resource]:
    # Public, no auth — same reasoning as the quiz/lesson GETs: "Further
    # Reading" is the same curated list for every learner, nothing
    # per-user to gate. Unlike quiz/exercise, this is a genuine list
    # endpoint (a lesson can have any number of resources, or none), so a
    # lesson with nothing curated yet returns an empty list rather than
    # 404ing — there's no "the resources" singular to be missing.
    return list(
        db.scalars(
            select(Resource)
            .where(Resource.lesson_id == lesson_id)
            .order_by(Resource.order)
        ).all()
    )
