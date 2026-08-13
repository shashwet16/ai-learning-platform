from datetime import UTC, datetime, timedelta

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.errors import AppError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

JWT_ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    minutes = (
        expires_minutes if expires_minutes is not None else settings.jwt_expire_minutes
    )
    expire_at = datetime.now(UTC) + timedelta(minutes=minutes)
    payload = {"sub": subject, "exp": expire_at}
    return jwt.encode(payload, settings.jwt_secret, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise AppError(
            "Token has expired", status_code=401, code="token_expired"
        ) from exc
    except jwt.PyJWTError as exc:
        raise AppError("Invalid token", status_code=401, code="invalid_token") from exc
    return payload["sub"]
