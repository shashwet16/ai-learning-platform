import logging
import time

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.routes.auth import router as auth_router
from app.api.routes.chat import router as chat_router
from app.api.routes.courses import lessons_router
from app.api.routes.courses import router as courses_router
from app.api.routes.exercises import router as exercises_router
from app.api.routes.quizzes import router as quizzes_router
from app.api.routes.resources import router as resources_router
from app.core.config import settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.db.session import get_db

configure_logging()
logger = logging.getLogger("app.request")

# The frontend Vite dev server. No other origins are allowed yet — this
# will need to grow once a real deployed frontend origin exists.
ALLOWED_ORIGINS = ["http://localhost:5173"]

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(courses_router)
app.include_router(lessons_router)
app.include_router(exercises_router)
app.include_router(quizzes_router)
app.include_router(resources_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        # Truly unhandled exceptions are converted to a 500 JSON response by
        # register_exception_handlers, but that conversion happens in
        # Starlette's outermost ServerErrorMiddleware — *above* this
        # middleware in the stack. That means the exception propagates
        # past the logging call below before this middleware ever sees a
        # response, so without this except clause the single most
        # important case (a real server error) would go completely
        # unlogged. Log it here, then re-raise so the exception handler
        # still runs and the client still gets the proper JSON response.
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "%s %s %s %.2fms", request.method, request.url.path, 500, duration_ms
        )
        raise
    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "%s %s %s %.2fms",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)) -> dict[str, str]:
    db.execute(text("SELECT 1"))
    return {"status": "ok"}
