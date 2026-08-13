import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app.errors")


class AppError(Exception):
    """Base class for application-raised errors with a stable error code.

    Route/service code should raise this (or a subclass) instead of a bare
    HTTPException when it wants control over the machine-readable `code`,
    e.g. `raise AppError("Email taken", status_code=409, code="email_taken")`.
    """

    def __init__(
        self, message: str, *, status_code: int = 400, code: str = "bad_request"
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.code = code


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(exc.status_code, exc.code, exc.message)

    # Registered against Starlette's base HTTPException, not fastapi's
    # subclass: Starlette's own router raises the *base* class directly for
    # an unmatched route (no handler found), and a handler registered only
    # for fastapi.HTTPException would never catch that — exception-handler
    # lookup walks the raised instance's own MRO upward, and a subclass is
    # not an ancestor of its base class. Registering against the base
    # class here still catches fastapi.HTTPException too, since that's a
    # subclass and therefore has the base class in its MRO.
    @app.exception_handler(StarletteHTTPException)
    async def handle_http_exception(
        request: Request, exc: StarletteHTTPException
    ) -> JSONResponse:
        return _error_response(exc.status_code, "http_error", str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return _error_response(422, "validation_error", "Request validation failed")

    @app.exception_handler(Exception)
    async def handle_unhandled_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.exception("Unhandled exception while processing request")
        return _error_response(500, "internal_error", "Internal server error")
