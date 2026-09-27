"""API shapes for the assistant endpoint."""

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator

SESSION_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class AssistantRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64, examples=["nelson-001"])
    question: str = Field(..., min_length=3, max_length=1000,
                          examples=["What is the Atlas Enterprise uptime SLA?"])

    @field_validator("session_id")
    @classmethod
    def session_id_must_be_safe(cls, value: str) -> str:
        if not SESSION_ID_PATTERN.fullmatch(value):
            raise ValueError("session_id may contain only letters, numbers, hyphens and underscores")
        return value

    @field_validator("question")
    @classmethod
    def question_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("question cannot be empty or only whitespace")
        return cleaned


class AssistantAnswer(BaseModel):
    """The Analyst Agent's structured final answer."""

    summary: str = Field(..., description="A direct answer to the question, in plain language.")
    key_points: list[str] = Field(..., min_length=1)
    caveats: list[str] = Field(..., description="Limitations, uncertainties, or what was not covered.")
    confidence: Literal["low", "medium", "high"]


class ExecutionTrace(BaseModel):
    """What the system actually did. This is the evidence for requirement 3.8."""

    route: str = Field(..., description="The branch the Router chose.")
    route_reason: str
    agents_run: list[str] = Field(..., description="Which agents executed, in order.")
    tools_used: list[str] = Field(..., description="Which tools the Research Agent called.")
    from_memory: bool = Field(..., description="True when the answer reused earlier research.")


class AssistantResponse(BaseModel):
    session_id: str
    question: str
    answer: AssistantAnswer
    execution: ExecutionTrace
