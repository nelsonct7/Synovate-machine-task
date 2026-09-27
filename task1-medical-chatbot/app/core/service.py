"""Orchestrates one chat turn.

This is the only module where sessions, guardrails and the LangChain chain meet.
The route layer above it knows nothing about LangChain; the chain below it knows
nothing about sessions or HTTP.
"""

import logging
from dataclasses import dataclass

from app.core import guardrails, memory
from app.core.chain import get_chain
from app.exceptions import LLMUnavailableError

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ChatResult:
    """What one completed turn produced."""

    reply: str
    in_domain: bool
    turn_count: int


def answer_question(session_id: str, question: str) -> ChatResult:
    """Answer one question in the context of its conversation."""
    history = memory.get_history(session_id)

    try:
        raw = get_chain().invoke({"history": history, "question": question})
    except Exception as exc:
        # Full detail goes to the server log; the caller gets a safe, generic message.
        logger.exception("LLM call failed for session %s", session_id)
        raise LLMUnavailableError() from exc

    text, in_domain = guardrails.interpret_answer(raw)
    reply = guardrails.append_disclaimer(text) if in_domain else text

    # Store the clean text, not the disclaimer - no point paying to resend
    # the same boilerplate to the model on every future turn.
    count = memory.record_turn(session_id, question, text)

    return ChatResult(reply=reply, in_domain=in_domain, turn_count=count)
