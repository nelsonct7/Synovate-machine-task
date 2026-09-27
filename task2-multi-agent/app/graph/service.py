"""Runs the agent workflow for one request.

Sits between the HTTP layer and the graph, exactly as `core/service.py` did in Task 1.
The route knows nothing about LangGraph; the graph knows nothing about HTTP.
"""

import logging

from app.exceptions import GraphExecutionError
from app.graph.builder import get_research_graph
from app.schemas.research import ResearchResponse

logger = logging.getLogger(__name__)


def run_research(topic: str) -> ResearchResponse:
    """Execute the two-agent workflow and return the Analyst's summary."""
    initial_state = {"topic": topic, "research_notes": "", "summary": None}

    logger.info("Starting research workflow for topic: %s", topic)
    final_state = get_research_graph().invoke(initial_state)

    # The Analyst writes `summary`. If it is missing, the workflow did not complete
    # and we must not return a half-finished result as if it were an answer.
    summary = final_state.get("summary")
    if summary is None:
        raise GraphExecutionError("The workflow finished without producing a summary.")

    return ResearchResponse(
        topic=topic,
        summary=summary,
        research_notes=final_state.get("research_notes", ""),
    )
