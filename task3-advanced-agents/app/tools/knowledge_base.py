"""Custom tool 2 - retrieval over Synnovate's internal document library.

Documents live in `data/knowledge_base/` as markdown. They are split into sections by
heading, and a query is matched against those sections by word overlap.

This is deliberately simple rather than a vector database: it has no extra dependency,
no embedding cost, and it is easy to read. Swapping in a real vector store later means
changing `_load_sections` and `_score` only - the tool's interface to the agent is
unchanged.
"""

import logging
import re
from functools import lru_cache
from pathlib import Path

from langchain_core.tools import tool

logger = logging.getLogger(__name__)

KNOWLEDGE_BASE_DIR = Path("data/knowledge_base")
MAX_SECTIONS_RETURNED = 3

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "do", "does", "for", "from",
    "how", "in", "is", "it", "of", "on", "or", "our", "that", "the", "to", "we",
    "what", "when", "which", "who", "why", "with",
}


def _tokenise(text: str) -> set[str]:
    return set(_WORD.findall(text.lower())) - _STOPWORDS


@lru_cache
def _load_sections() -> tuple[tuple[str, str, str], ...]:
    """Load every markdown file and split it into (filename, heading, body) sections.

    Cached, so the files are read from disk once per process.
    """
    if not KNOWLEDGE_BASE_DIR.exists():
        logger.warning("Knowledge base directory %s not found", KNOWLEDGE_BASE_DIR)
        return ()

    sections: list[tuple[str, str, str]] = []
    for path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        for chunk in re.split(r"^##\s+", path.read_text(encoding="utf-8"), flags=re.MULTILINE):
            chunk = chunk.strip()
            if not chunk:
                continue
            heading, _, body = chunk.partition("\n")
            sections.append((path.name, heading.lstrip("# ").strip(), body.strip()))

    logger.info("Loaded %d knowledge base sections", len(sections))
    return tuple(sections)


@tool
def knowledge_base_search(query: str) -> str:
    """Search Synnovate's internal document library.

    Use this for anything about Synnovate's own products, platforms, policies, SLAs,
    rate limits, internal metrics or procedures - for example the Atlas platform, the
    research data handling policy, or quarterly performance figures. This information
    is private and will not be found on the public web, so prefer this tool over web
    search whenever the question is about Synnovate itself.

    Args:
        query: What you are looking for. Include distinctive terms such as a product
            name, a policy area, or a metric.

    Returns:
        The most relevant document sections, each labelled with its source file.
    """
    logger.info("[TOOL: knowledge_base_search] query=%r", query)

    sections = _load_sections()
    if not sections:
        return "The internal knowledge base is empty or unavailable."

    query_terms = _tokenise(query)
    if not query_terms:
        return "Please provide a more specific query."

    scored = []
    for filename, heading, body in sections:
        overlap = query_terms & _tokenise(f"{heading} {body}")
        if not overlap:
            continue
        # A heading match counts twice: a section titled "Service level agreement" is a
        # better hit for "uptime SLA" than one that merely mentions it in passing.
        score = len(overlap) + len(query_terms & _tokenise(heading))
        scored.append((score, filename, heading, body))

    if not scored:
        return f"No internal documents matched {query!r}."

    scored.sort(key=lambda row: row[0], reverse=True)
    top = scored[:MAX_SECTIONS_RETURNED]
    logger.info("[TOOL: knowledge_base_search] matched %d sections", len(top))

    return "\n\n".join(
        f"[{filename} > {heading}]\n{body}" for _, filename, heading, body in top
    )
