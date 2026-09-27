"""The research endpoint."""

from fastapi import APIRouter

from app.graph.service import run_research
from app.schemas.research import ResearchRequest, ResearchResponse

router = APIRouter(prefix="/api/v1", tags=["research"])


@router.post(
    "/research",
    response_model=ResearchResponse,
    summary="Run the two-agent research workflow",
)
def research(request: ResearchRequest) -> ResearchResponse:
    """Agent 1 researches the topic, then Agent 2 produces the structured summary.

    The `summary` field is written entirely by Agent 2. `research_notes` is Agent 1's
    intermediate output, returned so the hand-off between agents is visible.
    """
    return run_research(request.topic)
