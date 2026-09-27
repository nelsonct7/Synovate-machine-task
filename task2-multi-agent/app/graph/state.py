"""The shared state - the only channel through which the two agents communicate.

Each key is written by exactly one node:

    topic           supplied by the caller
    research_notes  written by the Research Agent  (Agent 1)
    summary         written by the Analyst Agent   (Agent 2)

Keeping one writer per key is what keeps the agents' responsibilities separate.
"""

from typing import TypedDict

from app.schemas.research import ResearchSummary


class ResearchState(TypedDict):
    """Everything the workflow carries from one node to the next."""

    topic: str
    research_notes: str
    summary: ResearchSummary | None
