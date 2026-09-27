"""The assistant endpoints."""

from fastapi import APIRouter, Path, status

from app.graph.service import ask
from app.memory.store import clear_session
from app.schemas.assistant import (
    SESSION_ID_PATTERN,
    AssistantRequest,
    AssistantResponse,
)

router = APIRouter(prefix="/api/v1", tags=["assistant"])


@router.post("/assistant", response_model=AssistantResponse, summary="Ask the research assistant")
def assistant(request: AssistantRequest) -> AssistantResponse:
    """Route the question, research it if needed, and return a structured answer.

    The `execution` block reports which agents ran and which tools were called, so
    you can see the system skipping work it has already done.
    """
    return ask(request.session_id, request.question)


@router.delete(
    "/assistant/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Forget everything remembered for a session",
)
def forget(session_id: str = Path(..., pattern=SESSION_ID_PATTERN.pattern)) -> None:
    """Delete this session's messages and findings."""
    clear_session(session_id)
