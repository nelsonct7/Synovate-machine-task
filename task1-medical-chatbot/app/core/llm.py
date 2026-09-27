"""Creates the Claude client used by every chain in this app.

Kept in its own module so that changing the model - or swapping Anthropic for
another provider entirely - is a one-file change that nothing else notices.
"""

from functools import lru_cache

from langchain_anthropic import ChatAnthropic

from app.config import get_settings


@lru_cache
def get_llm() -> ChatAnthropic:
    """Return the shared chat model, building it only once per process."""
    settings = get_settings()

    return ChatAnthropic(
        model=settings.anthropic_model,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.anthropic_api_key,
        timeout=90,       # seconds before we give up on a slow request
        max_retries=2,    # retry twice on network blips / rate limits
        effort=settings.llm_effort
    )
