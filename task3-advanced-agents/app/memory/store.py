"""Persistent memory, stored in SQLite.

Two tables:

    messages   every question and answer, per session  -> conversation context  [3.6]
    findings   completed research results, per topic   -> the "already known"
               shortcut that lets the system skip the research workflow         [3.8]

SQLite rather than a dictionary (as in Task 1) because this has to survive a restart,
and because the findings table needs to be searched.
"""

import json
import logging
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock

from app.config import get_settings

logger = logging.getLogger(__name__)

_lock = Lock()

_SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    role        TEXT NOT NULL,
    content     TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id);

CREATE TABLE IF NOT EXISTS findings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL,
    topic       TEXT NOT NULL,
    content     TEXT NOT NULL,
    tools_used  TEXT NOT NULL,
    created_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_findings_session ON findings(session_id);
"""


@dataclass(frozen=True)
class Finding:
    """One piece of research we have already completed."""

    id: int
    topic: str
    content: str
    created_at: str


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    """Open the database, creating the folder on first use."""
    path = Path(get_settings().memory_db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    """Create the tables if they don't exist. Safe to call repeatedly."""
    with _lock, _connect() as conn:
        conn.executescript(_SCHEMA)
    logger.info("Memory database ready at %s", get_settings().memory_db_path)


def add_message(session_id: str, role: str, content: str) -> None:
    """Record one turn of the conversation."""
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (session_id, role, content, _now()),
        )


def recent_messages(session_id: str, limit: int = 6) -> list[tuple[str, str]]:
    """Return the most recent (role, content) pairs, oldest first."""
    with _lock, _connect() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit),
        ).fetchall()
    return [(row["role"], row["content"]) for row in reversed(rows)]


def save_finding(session_id: str, topic: str, content: str, tools_used: list[str]) -> None:
    """Remember a completed piece of research so it need not be repeated."""
    with _lock, _connect() as conn:
        conn.execute(
            "INSERT INTO findings (session_id, topic, content, tools_used, created_at)"
            " VALUES (?, ?, ?, ?, ?)",
            (session_id, topic, content, json.dumps(tools_used), _now()),
        )
    logger.info("Saved finding for session=%s topic=%r", session_id, topic)


def all_findings(session_id: str) -> list[Finding]:
    """Every finding remembered for this session, newest first."""
    with _lock, _connect() as conn:
        rows = conn.execute(
            "SELECT id, topic, content, created_at FROM findings"
            " WHERE session_id = ? ORDER BY id DESC",
            (session_id,),
        ).fetchall()
    return [
        Finding(
            id=row["id"],
            topic=row["topic"],
            content=row["content"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


def clear_session(session_id: str) -> int:
    """Forget everything for a session. Returns the number of rows removed."""
    with _lock, _connect() as conn:
        removed = conn.execute(
            "DELETE FROM messages WHERE session_id = ?", (session_id,)
        ).rowcount
        removed += conn.execute(
            "DELETE FROM findings WHERE session_id = ?", (session_id,)
        ).rowcount
    logger.info("Cleared %d rows for session=%s", removed, session_id)
    return removed
