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
            "A two-agent research system built with LangGraph. A Research Agent gathers "
            "information on a topic and writes it into shared state; an Analyst Agent reads "
            "that state and produces the structured summary returned by the API."
        ),
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
