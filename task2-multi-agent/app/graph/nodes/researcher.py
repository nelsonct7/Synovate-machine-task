"""Agent 1 - the Research Agent.

Gathers information about the topic. It does not summarise and it does not conclude.
It writes exactly one key into the state: `research_notes`.
"""

import logging

from langchain_core.output_parsers import StrOutputParser

from app.exceptions import LLMUnavailableError
from app.graph.llm import get_llm
from app.graph.prompts import build_researcher_prompt
from app.graph.state import ResearchState

logger = logging.getLogger(__name__)


def research_node(state: ResearchState) -> dict:
    """Gather information about the topic and write it into the state."""
    topic = state["topic"]
    logger.info("[Agent 1: Researcher] starting on topic: %s", topic)

    chain = build_researcher_prompt() | get_llm(effort="low") | StrOutputParser()

    try:
        notes = chain.invoke({"topic": topic})
    except Exception as exc:
        logger.exception("[Agent 1: Researcher] failed")
        raise LLMUnavailableError() from exc

    logger.info("[Agent 1: Researcher] produced %d characters of notes", len(notes))

    # Return ONLY the keys this node updates. LangGraph merges this into the state.
    return {"research_notes": notes}
