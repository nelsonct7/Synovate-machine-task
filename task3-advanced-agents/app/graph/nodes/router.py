"""Agent 1 - the Router.

Decides which agent or action should handle the request (requirement 3.7). It writes
`route` into the state; the graph's conditional edge reads that key to pick a branch.
"""

import logging

from app.exceptions import LLMUnavailableError
from app.graph.llm import get_llm
from app.graph.prompts import build_router_prompt
from app.graph.state import AssistantState
from app.memory.store import Finding
from app.schemas.routing import RouteDecision

logger = logging.getLogger(__name__)


def _format_candidates(candidates: list[Finding]) -> str:
    if not candidates:
        return "None. No research has been completed in this session yet."
    return "\n\n".join(
        f"[id={c.id}] topic: {c.topic}\n{c.content[:1200]}" for c in candidates
    )


def _format_conversation(conversation: list[tuple[str, str]]) -> str:
    if not conversation:
        return "None. This is the first message in the session."
    return "\n".join(f"{role}: {content[:300]}" for role, content in conversation)


def router_node(state: AssistantState) -> dict:
    """Decide how this question should be handled."""
    candidates = state.get("candidates", [])

    # Classification is a shallow task - low effort keeps the routing decision fast
    # and cheap, which matters because it runs on every single request.
    chain = build_router_prompt() | get_llm(effort="low").with_structured_output(RouteDecision)

    try:
        decision = chain.invoke(
            {
                "question": state["question"],
                "conversation": _format_conversation(state.get("conversation", [])),
                "candidates": _format_candidates(candidates),
            }
        )
    except Exception as exc:
        logger.exception("[Agent 1: Router] failed")
        raise LLMUnavailableError() from exc

    route = decision.route
    recalled_content = ""

    if route == "answer_from_memory":
        match = next(
            (c for c in candidates if c.id == decision.memory_finding_id), None
        )
        if match is None:
            # The model chose memory but named a finding that isn't in the shortlist.
            # Rather than answering from nothing, fall back to doing the research.
            logger.warning(
                "[Agent 1: Router] chose memory but finding id=%s not found; "
                "falling back to research",
                decision.memory_finding_id,
            )
            route = "research"
        else:
            recalled_content = match.content

    logger.info("[Agent 1: Router] route=%s reason=%s", route, decision.reason)

    return {
        "route": route,
        "route_reason": decision.reason,
        "recalled_content": recalled_content,
        "agents_run": ["router"],
    }

