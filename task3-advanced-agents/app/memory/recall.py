"""Finds past findings that might answer the current question.

Deliberately NOT an LLM call. Asking the model "does this old finding answer the new
question?" once per stored finding would cost one API request per finding, every turn.

Instead: cheap keyword matching here to shortlist candidates, then the Router agent
makes a single judgement call about whether any of them genuinely fits.
Cheap retrieval, then one expensive decision - rather than N expensive decisions.
"""

import logging
import re

from app.memory.store import Finding, all_findings

logger = logging.getLogger(__name__)

MAX_CANDIDATES = 3
MIN_OVERLAP = 2  # fewer shared words than this is almost always a coincidence

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "about", "an", "and", "are", "as", "at", "be", "by", "can", "do", "does",
    "for", "from", "how", "i", "in", "is", "it", "me", "of", "on", "or", "our",
    "please", "tell", "that", "the", "to", "us", "we", "what", "when", "which",
    "who", "why", "with", "you", "your",
}


def _tokenise(text: str) -> set[str]:
    return set(_WORD.findall(text.lower())) - _STOPWORDS


def find_candidates(session_id: str, question: str) -> list[Finding]:
    """Shortlist past findings whose topic overlaps the new question."""
    question_terms = _tokenise(question)
    if not question_terms:
        return []

    scored: list[tuple[int, Finding]] = []
    for finding in all_findings(session_id):
        overlap = question_terms & _tokenise(finding.topic)
        if len(overlap) >= MIN_OVERLAP:
            scored.append((len(overlap), finding))

    scored.sort(key=lambda row: row[0], reverse=True)
    candidates = [finding for _, finding in scored[:MAX_CANDIDATES]]

    logger.info(
        "[recall] %d candidate finding(s) for session=%s", len(candidates), session_id
    )
    return candidates
