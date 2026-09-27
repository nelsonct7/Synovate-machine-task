"""Creates the Claude client used by the agents.

`get_llm` takes optional overrides so each agent can ask for the settings its own
job needs, rather than every agent sharing one compromise configuration.
"""

from functools import lru_cache

from langchain_anthropic import ChatAnthropic

from app.config import get_settings


@lru_cache
def get_llm(
    effort: str | None = None,
    max_tokens: int | None = None,
) -> ChatAnthropic:
    """Return a chat model, cached per unique combination of settings."""
    settings = get_settings()

    return ChatAnthropic(
        model=settings.anthropic_model,
        max_tokens=max_tokens or settings.llm_max_tokens,
        effort=effort or settings.llm_effort,
        api_key=settings.anthropic_api_key,
        # Reasoning takes real time. A plain request would hit the HTTP timeout
        # before the model finished; streaming keeps the connection alive.
        streaming=True,
        timeout=180,
        max_retries=2,
    )
