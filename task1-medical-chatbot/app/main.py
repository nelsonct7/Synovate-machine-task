"""Application entry point."""

import logging

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.router import api_router
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "A domain-specific chatbot for general medical and healthcare information. "
            "It does not diagnose, prescribe, or give personalised medical advice."
        ),
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
