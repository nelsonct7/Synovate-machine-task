"""Agent 2 - the Research Agent.

Binds the custom tools to the model and lets Claude decide which, if any, to call.
The API never calls a tool - only this agent does (requirement 3.10).

This node runs MORE THAN ONCE per request: agent -> tools -> agent -> ... until the
model stops asking for tools. The loop itself is wired in `builder.py`.
"""

import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from app.exceptions import LLMUnavailableError
from app.graph.llm import get_llm
from app.graph.prompts import RESEARCHER_SYSTEM
from app.graph.state import AssistantState
from app.tools.registry import ALL_TOOLS

logger = logging.getLogger(__name__)


def research_node(state: AssistantState) -> dict:
    """Research the question, calling tools when the model judges them useful."""
    existing = state.get("messages") or []

    if existing:
        # A later pass through the loop: tool results are already in the state.
        conversation = existing
        new_messages = []
    else:
        # First pass: seed the conversation. These two must also be added to the
        # state, or the next pass would lose the system prompt and the question.
        conversation = [
            SystemMessage(content=RESEARCHER_SYSTEM),
            HumanMessage(content=state["question"]),
        ]
        new_messages = list(conversation)

    # bind_tools is what makes tool calling possible: it sends the tool schemas
    # alongside the prompt so the model can choose to call one.
    llm_with_tools = get_llm(effort="low").bind_tools(ALL_TOOLS)

    try:
        response = llm_with_tools.invoke(conversation)
    except Exception as exc:
        logger.exception("[Agent 2: Researcher] failed")
        raise LLMUnavailableError() from exc

    new_messages.append(response)
    tool_names = [call["name"] for call in (response.tool_calls or [])]

    update: dict = {
        "messages": new_messages,
        "agents_run": ["researcher"],
        "tools_used": tool_names,
    }

    if tool_names:
        logger.info("[Agent 2: Researcher] requesting tools: %s", tool_names)
    else:
        # No tool calls means the model is done gathering - this reply is the notes.
        notes = StrOutputParser().invoke(response)
        update["research_notes"] = notes
        logger.info("[Agent 2: Researcher] finished with %d chars of notes", len(notes))

    return update
