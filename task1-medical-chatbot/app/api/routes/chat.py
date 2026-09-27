"""The chat endpoints.

This layer only translates between HTTP and the service layer. It contains no
LangChain code and no knowledge of how answers are produced.
"""

from fastapi import APIRouter, Path, status

from app.core import memory
from app.core.service import answer_question
from app.exceptions import SessionNotFoundError
from app.schemas.chat import SESSION_ID_PATTERN, ChatRequest, ChatResponse

router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/chat", response_model=ChatResponse, summary="Ask a medical question")
def chat(request: ChatRequest) -> ChatResponse:
    """Answer one question in the context of its conversation."""
    result = answer_question(session_id=request.session_id, question=request.message)
    return ChatResponse(
        session_id=request.session_id,
        reply=result.reply,
        in_domain=result.in_domain,
        turn_count=result.turn_count,
    )


@router.delete(
    "/chat/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Forget a conversation",
)
def clear_chat(
    session_id: str = Path(..., pattern=SESSION_ID_PATTERN.pattern),
) -> None:
    """Delete a session's stored history so the next message starts fresh."""
    if not memory.clear_session(session_id):
        raise SessionNotFoundError()
