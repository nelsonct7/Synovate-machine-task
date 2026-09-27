"""Agent 2 - the Analyst Agent.

Reads the Research Agent's notes out of the state and produces the structured summary
that the API returns. This is the agent that generates the final response
(requirement 2.5) - the Researcher's output never reaches the caller as the answer.
"""

import logging

from app.exceptions import GraphExecutionError, LLMUnavailableError
from app.graph.llm import get_llm
from app.graph.prompts import build_analyst_prompt
from app.graph.state import ResearchState
from app.schemas.research import ResearchSummary

logger = logging.getLogger(__name__)


def analyst_node(state: ResearchState) -> dict:
    """Turn the research notes into a structured summary."""
    notes = state.get("research_notes", "")

    # The Analyst depends entirely on Agent 1's output. If that key is missing or
    # empty, fail here with a clear message rather than asking the model to
    # summarise nothing.
    if not notes.strip():
        raise GraphExecutionError("The Research Agent produced no notes to analyse.")

    logger.info("[Agent 2: Analyst] summarising %d characters of notes", len(notes))

    # `with_structured_output` hands Claude the ResearchSummary schema and requires
    # the reply to fit it. What comes back is a validated Python object, not prose.
    structured_llm = get_llm(effort="medium").with_structured_output(ResearchSummary)
    chain = build_analyst_prompt() | structured_llm

    try:
        summary = chain.invoke({"topic": state["topic"], "research_notes": notes})
    except Exception as exc:
        logger.exception("[Agent 2: Analyst] failed")
        raise LLMUnavailableError() from exc

    logger.info(
        "[Agent 2: Analyst] produced summary with confidence=%s, %d key findings",
        summary.confidence,
        len(summary.key_findings),
    )
    return {"summary": summary}
