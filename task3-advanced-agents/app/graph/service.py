"""Runs the assistant workflow for one request, and updates memory afterwards."""

import logging

from app.exceptions import GraphExecutionError
from app.graph.builder import get_assistant_graph
from app.memory.store import add_message, save_finding
from app.schemas.assistant import AssistantResponse, ExecutionTrace

logger = logging.getLogger(__name__)


def _dedupe(names: list[str]) -> list[str]:
    """Preserve order, drop repeats - the researcher appears once per loop pass."""
    seen: set[str] = set()
    return [n for n in names if not (n in seen or seen.add(n))]


def ask(session_id: str, question: str) -> AssistantResponse:
    """Answer one question, routing through whichever agents are actually needed."""
    initial_state = {
        "session_id": session_id,
        "question": question,
        "candidates": [],
        "conversation": [],
        "route": None,
        "route_reason": "",
        "recalled_content": "",
        "messages": [],
        "research_notes": "",
        "answer": None,
        "agents_run": [],
        "tools_used": [],
    }

    final_state = get_assistant_graph().invoke(initial_state)

    answer = final_state.get("answer")
    if answer is None:
        raise GraphExecutionError("The workflow finished without producing an answer.")

    route = final_state.get("route") or "unknown"
    tools_used = _dedupe(final_state.get("tools_used", []))

    # Remember the exchange. And when we did fresh research, remember the findings
    # so the same question next time can take the memory shortcut.
    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer.summary)
    if route == "research" and final_state.get("research_notes"):
        save_finding(session_id, question, final_state["research_notes"], tools_used)

    return AssistantResponse(
        session_id=session_id,
        question=question,
        answer=answer,
        execution=ExecutionTrace(
            route=route,
            route_reason=final_state.get("route_reason", ""),
            agents_run=_dedupe(final_state.get("agents_run", [])),
            tools_used=tools_used,
            from_memory=route == "answer_from_memory",
        ),
    )
