"""Application settings.

Every tunable value in the app is defined here and nowhere else. If you want to
change the model, the token limit, or how much history is remembered, this is the
only file you touch.
"""

from functools import lru_cache
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings read from environment variables, falling back to `.env`."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Required: the app refuses to start without this ---
    anthropic_api_key: str = Field(
        ...,
        description="Anthropic API key. Read from ANTHROPIC_API_KEY.",
    )

    # --- LLM settings ---
    anthropic_model: str = Field(default="claude-opus-5")
    llm_max_tokens: int = Field(
        default=8000,
        gt=0,
        description="Cap on output tokens. Reasoning tokens count against this.",
    )
    llm_effort: Literal["low", "medium", "high", "xhigh", "max"] = Field(
        default="medium",
        description="How hard the model reasons before answering. Higher = better, slower, dearer.",
    )

    # --- Conversation settings ---
    max_history_messages: int = Field(
        default=10,
        gt=0,
        description="How many past messages to send back to the model as context.",
    )

    # --- App metadata, shown in the API docs ---
    app_name: str = Field(default="Medical Information Chatbot")
    app_version: str = Field(default="1.0.0")


@lru_cache
def get_settings() -> Settings:
    """Return the settings, building them only once per process."""
    return Settings()
