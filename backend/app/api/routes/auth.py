from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.errors import AppError
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import Token, UserCreate, UserLogin, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

# A precomputed hash with no matching real user, used so login always runs
# a bcrypt verify of the same cost regardless of whether the email exists —
# see login() below for why.
_DUMMY_HASH = hash_password("dummy-password-for-constant-time-login")


@router.post("/register", response_model=UserRead, status_code=201)
def register(body: UserCreate, db: Session = Depends(get_db)) -> User:
    user = User(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise AppError(
            "Email already registered", status_code=409, code="email_taken"
        ) from exc
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(body: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = db.execute(select(User).where(User.email == body.email)).scalar_one_or_none()

    # Always run verify_password, even when no user was found, comparing
    # against a dummy hash in that case. bcrypt verification is slow on
    # purpose (see M2.2 notes); if it only ran for existing emails, an
    # attacker could tell "no such account" (fast) apart from "wrong
    # password" (slow) purely from response time, and use that to
    # enumerate which emails are registered without ever seeing an error
    # message that says so.
    hashed_password = user.hashed_password if user is not None else _DUMMY_HASH
    password_is_valid = verify_password(body.password, hashed_password)

    if user is None or not password_is_valid:
        raise AppError(
            "Incorrect email or password", status_code=401, code="invalid_credentials"
        )

    access_token = create_access_token(str(user.id))
    return Token(access_token=access_token)


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> User:
    return current_user
