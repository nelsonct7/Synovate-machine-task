"""Turns exceptions into consistent JSON, so clients never receive a stack trace."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.exceptions import MedicalChatbotError
from app.schemas.common import ErrorResponse

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach our handlers to the application."""

    @app.exception_handler(MedicalChatbotError)
    async def handle_app_error(_: Request, exc: MedicalChatbotError) -> JSONResponse:
        """Errors we raise on purpose already know their status code."""
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(error=exc.error_code, detail=exc.detail).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        """Reshape FastAPI's verbose 422 into our simple error format."""
        first = exc.errors()[0]
        field = ".".join(str(part) for part in first["loc"] if part != "body")
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error="validation_error",
                detail=f"{field}: {first['msg']}",
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        """Last line of defence - nothing escapes as an unhandled crash."""
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="internal_error",
                detail="An unexpected error occurred.",
            ).model_dump(),
        )
