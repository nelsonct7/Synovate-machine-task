"""Application settings.

Every tunable value lives here and nowhere else.
"""

from functools import lru_cache
from typing import Literal  


from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    anthropic_api_key: str = Field(..., description="Read from ANTHROPIC_API_KEY.")
    # --- LLM settings ---
    anthropic_model: str = Field(default="claude-opus-5")
    llm_max_tokens: int = Field(
        default=4000,
        gt=0,
        description="Cap on output tokens. Reasoning tokens count against this.",
    )
    llm_effort: Literal["low", "medium", "high", "xhigh", "max"] = Field(
        default="medium",
        description="Default reasoning depth. Individual agents may override it.",
    )

    app_name: str = Field(default="AI Research Assistant")
    app_version: str = Field(default="1.0.0")
    # --- Memory ---
    memory_db_path: str = Field(
        default="data/memory.db",
        description="SQLite file holding conversation history and past findings.",
    )

    # --- Tools ---
    max_search_results: int = Field(default=5, gt=0, le=10)


@lru_cache
def get_settings() -> Settings:
    return Settings()
