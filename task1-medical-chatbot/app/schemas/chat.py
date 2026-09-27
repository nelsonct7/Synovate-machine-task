"""Request and response shapes for the chat endpoint.

FastAPI reads these classes to validate incoming JSON automatically. Anything
that doesn't match is rejected with a 422 before our code ever runs.
"""

import re

from pydantic import BaseModel, Field, field_validator

# Session IDs end up as dictionary keys and appear in logs, so keep them tame.
SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class ChatRequest(BaseModel):
    """One incoming user message."""

    session_id: str = Field(
        ...,
        min_length=1,
        max_length=64,
        description="Identifies the conversation. Send the same value to continue a chat.",
        examples=["nelson-001"],
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's question.",
        examples=["What are the common symptoms of iron deficiency?"],
    )

    @field_validator("session_id")
    @classmethod
    def session_id_must_be_safe(cls, value: str) -> str:
        if not SESSION_ID_PATTERN.fullmatch(value):
            raise ValueError(
                "session_id may contain only letters, numbers, hyphens and underscores"
            )
        return value

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message cannot be empty or only whitespace")
        return cleaned


class ChatResponse(BaseModel):
    """What we send back."""

    session_id: str = Field(..., description="Echoed back so the client can confirm the thread.")
    reply: str = Field(..., description="The assistant's answer, including the safety disclaimer.")
    in_domain: bool = Field(
        ...,
        description="False when the question was refused for being outside the medical domain.",
    )
    turn_count: int = Field(..., description="Number of messages now stored for this session.")
