"""Custom tool 1 - web search via DuckDuckGo.

No API key is required, so a reviewer can clone this repo and run it immediately.
"""

import logging

from ddgs import DDGS
from langchain_core.tools import tool

from app.config import get_settings

logger = logging.getLogger(__name__)


@tool
def web_search(query: str) -> str:
    """Search the public web for current, external information about a topic.

    Use this when the question involves recent events, current prices or statistics,
    company or product news, or anything that may have changed recently. Do not use it
    for arithmetic, and do not use it for questions about Synnovate's own internal
    documents - the knowledge base tool covers those.

    Args:
        query: A focused search query. Short and specific beats a full sentence.

    Returns:
        Numbered search results, each with a title, URL and snippet.
    """
    settings = get_settings()
    logger.info("[TOOL: web_search] query=%r", query)

    try:
        results = list(DDGS().text(query, max_results=settings.max_search_results))
    except Exception as exc:
        # Return the failure as text rather than raising. The agent can read this,
        # decide the tool is unavailable, and carry on with what it has. Raising
        # would abort the whole workflow over one flaky search.
        logger.warning("[TOOL: web_search] failed: %s", exc)
        return f"Web search failed: {exc}. Continue without these results."

    if not results:
        return f"No web results found for {query!r}."

    blocks = []
    for index, result in enumerate(results, start=1):
        blocks.append(
            f"{index}. {result.get('title', 'Untitled')}\n"
            f"   URL: {result.get('href', '')}\n"
            f"   {result.get('body', '').strip()}"
        )

    logger.info("[TOOL: web_search] returned %d results", len(results))
    return "\n\n".join(blocks)
