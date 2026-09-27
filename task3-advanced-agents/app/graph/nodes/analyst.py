"""Agent 3 - the Analyst.

Produces the final structured answer. Every route ends here, so this agent has to
cope with three different kinds of input: fresh research, recalled memory, or nothing.
"""

import logging

from app.exceptions import LLMUnavailableError
from app.graph.llm import get_llm
from app.graph.prompts import build_analyst_prompt
from app.graph.state import AssistantState
from app.schemas.assistant import AssistantAnswer

logger = logging.getLogger(__name__)


def _material_for(state: AssistantState) -> tuple[str, str]:
    """Pick the input material based on which route the Router chose."""
    route = state.get("route")
    if route == "answer_from_memory":
        return state.get("recalled_content", ""), "recalled from earlier research in this session"
    if route == "research":
        return state.get("research_notes", ""), "freshly gathered by the Research Agent"
    return "", "none - this question needs no external information"


def _format_conversation(conversation: list[tuple[str, str]]) -> str:
    if not conversation:
        return "None. This is the first message in the session."
    return "\n".join(f"{role}: {content[:300]}" for role, content in conversation)


def analyst_node(state: AssistantState) -> dict:
    """Turn whatever was gathered into the final structured answer."""
    material, source = _material_for(state)
    logger.info(
        "[Agent 3: Analyst] route=%s, %d chars of material (%s)",
        state.get("route"), len(material), source,
    )

    chain = build_analyst_prompt() | get_llm(effort="medium").with_structured_output(AssistantAnswer)

    try:
        answer = chain.invoke(
            {
                "question": state["question"],
                "conversation": _format_conversation(state.get("conversation", [])),
                "material": material or "(none)",
                "source": source,
            }
        )
    except Exception as exc:
        logger.exception("[Agent 3: Analyst] failed")
        raise LLMUnavailableError() from exc

    logger.info("[Agent 3: Analyst] answer confidence=%s", answer.confidence)
    return {"answer": answer, "agents_run": ["analyst"]}
