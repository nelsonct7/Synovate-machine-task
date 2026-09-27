"""API shapes for the research endpoint, plus the structured summary itself."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ResearchRequest(BaseModel):
    """What the caller sends."""

    topic: str = Field(
        ...,
        min_length=3,
        max_length=300,
        description="The subject to research.",
        examples=["CRISPR gene editing for sickle cell disease"],
    )

    @field_validator("topic")
    @classmethod
    def topic_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("topic cannot be empty or only whitespace")
        return cleaned


class ResearchSummary(BaseModel):
    """The Analyst Agent's structured output.

    Claude is handed this class as a schema and must fill exactly these fields -
    it cannot reply with free-form prose. This is what makes the summary *structured*
    rather than just 'a summary' (requirement 2.5).
    """

    overview: str = Field(
        ...,
        description="Two or three sentences a non-specialist can follow.",
    )
    key_findings: list[str] = Field(
        ...,
        min_length=1,
        description="The 3 to 6 most important points from the research notes.",
    )
    implications: list[str] = Field(
        ...,
        min_length=1,
        description="What these findings mean in practice, for whom.",
    )
    open_questions: list[str] = Field(
        ...,
        min_length=1,
        description="What remains unresolved, disputed, or unknown.",
    )
    confidence: Literal["low", "medium", "high"] = Field(
        ...,
        description="How well the research notes support this summary.",
    )


class ResearchResponse(BaseModel):
    """What the caller gets back."""

    topic: str
    summary: ResearchSummary = Field(
        ...,
        description="Produced by the Analyst Agent - this is the final answer.",
    )
    research_notes: str = Field(
        ...,
        description=(
            "Intermediate output from the Research Agent. Returned so the state "
            "passing between the two agents is visible to a reviewer."
        ),
    )
