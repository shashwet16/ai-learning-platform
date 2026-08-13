import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import AppError
from app.core.security import decode_access_token
from app.db.session import get_db
from app.models.user import User

# auto_error=False: FastAPI's HTTPBearer otherwise raises a 403 (not 401)
# when the Authorization header is missing entirely, which doesn't match
# this project's convention of 401 for "not authenticated" — handling the
# missing-header case ourselves below keeps that consistent.
bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None:
        raise AppError("Not authenticated", status_code=401, code="not_authenticated")

    user_id = decode_access_token(credentials.credentials)

    user = db.execute(
        select(User).where(User.id == uuid.UUID(user_id))
    ).scalar_one_or_none()
    if user is None:
        raise AppError("Not authenticated", status_code=401, code="not_authenticated")

    return user
