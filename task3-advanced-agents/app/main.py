"""Application entry point."""

import logging

from fastapi import FastAPI

from app.api.errors import register_exception_handlers
from app.api.router import api_router
from app.config import get_settings
from app.memory.store import init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()

    # Create the memory tables before the first request arrives.
    init_db()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "An advanced multi-agent research assistant built with LangGraph. A Router "
            "agent decides how each request is handled, a Research agent gathers "
            "information using custom tools of its own choosing, and an Analyst agent "
            "produces the final structured answer. Completed research is remembered, so "
            "repeat questions skip the research workflow entirely."
        ),
    )

    register_exception_handlers(app)
    app.include_router(api_router)
    return app


app = create_app()
