"""The shared state for the advanced workflow.

Some keys are written by one node and simply overwritten. Others are *accumulated*
across several nodes - those are marked with a reducer via `Annotated`.
"""

from operator import add
from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from app.memory.store import Finding
from app.schemas.assistant import AssistantAnswer
from app.schemas.routing import Route


class AssistantState(TypedDict):
    # --- supplied by the caller ---
    session_id: str
    question: str

    # --- written by the recall node (no LLM involved) ---
    candidates: list[Finding]
    conversation: list[tuple[str, str]]

    # --- written by the Router agent ---
    route: Route | None
    route_reason: str
    recalled_content: str

    # --- written by the Research agent and the tool node ---
    # `add_messages` appends rather than replaces, which is what makes the
    # agent -> tool -> agent loop possible.
    messages: Annotated[list[BaseMessage], add_messages]
    research_notes: str

    # --- written by the Analyst agent ---
    answer: AssistantAnswer | None

    # --- bookkeeping for the execution trace. `add` concatenates the lists,
    # so each node can append its own name without clobbering the others. ---
    agents_run: Annotated[list[str], add]
    tools_used: Annotated[list[str], add]
