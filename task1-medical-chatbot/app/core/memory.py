"""Per-session conversation memory.

One list of messages per session_id, so two users never see each other's context.

We store `BaseMessage` objects in a plain dictionary rather than using LangChain's
chat-history classes: those are deprecated for removal in LangChain 2.0, and the
recommended replacement (LangGraph persistence) belongs in Tasks 2 and 3, not here.

Storage is in-process, so restarting the server forgets every conversation. Because
nothing outside this module knows *how* messages are stored, swapping in Redis or a
database later means changing only this file.
"""

from threading import Lock

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.config import get_settings

# session_id -> that conversation's messages, oldest first
_store: dict[str, list[BaseMessage]] = {}

# A web server handles several requests at once; this stops two of them
# corrupting the dictionary by writing to it at the same moment.
_lock = Lock()


def _history_limit() -> int:
    """The message cap, forced to an even number.

    Messages are always stored as Human/AI pairs. Trimming to an even count keeps
    the oldest surviving message a *human* one - Anthropic rejects a conversation
    that begins with an assistant message.
    """
    configured = get_settings().max_history_messages
    return max(2, (configured // 2) * 2)


def get_history(session_id: str) -> list[BaseMessage]:
    """Return a copy of this session's messages, oldest first."""
    with _lock:
        return list(_store.get(session_id, []))


def record_turn(session_id: str, question: str, answer: str) -> int:
    """Append one question/answer exchange, trim, return the new message count."""
    limit = _history_limit()
    with _lock:
        messages = _store.setdefault(session_id, [])
        messages.append(HumanMessage(content=question))
        messages.append(AIMessage(content=answer))
        if len(messages) > limit:
            del messages[:-limit]   # keep only the most recent `limit` messages
        return len(messages)


def turn_count(session_id: str) -> int:
    """How many messages are currently stored for this session."""
    with _lock:
        return len(_store.get(session_id, []))


def clear_session(session_id: str) -> bool:
    """Forget a conversation. True if there was something to forget."""
    with _lock:
        return _store.pop(session_id, None) is not None
