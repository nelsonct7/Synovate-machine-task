"""Memory lookup. Not an agent - there is no LLM call here at all.

Runs before the Router so the Router can see what we already know. Keeping this
step free means the "do we already know this?" check costs nothing.
"""

import logging

from app.graph.state import AssistantState
from app.memory.recall import find_candidates
from app.memory.store import recent_messages

logger = logging.getLogger(__name__)


def recall_node(state: AssistantState) -> dict:
    """Load conversation history and shortlist relevant past findings."""
    session_id = state["session_id"]
    candidates = find_candidates(session_id, state["question"])
    conversation = recent_messages(session_id, limit=6)

    logger.info(
        "[recall] session=%s: %d past message(s), %d candidate finding(s)",
        session_id, len(conversation), len(candidates),
    )
    return {"candidates": candidates, "conversation": conversation}
