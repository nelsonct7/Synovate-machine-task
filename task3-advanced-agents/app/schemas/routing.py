"""The Router agent's decision.

Internal: this is a contract between agents, not part of the public API.
"""

from typing import Literal

from pydantic import BaseModel, Field

Route = Literal["answer_from_memory", "research", "direct_answer"]


class RouteDecision(BaseModel):
    """What the Router decided and why."""

    route: Route = Field(..., description="Which branch of the workflow should handle this.")
    reason: str = Field(..., description="One sentence naming what drove the decision.")
    memory_finding_id: int | None = Field(
        default=None,
        description="When route is answer_from_memory, the id of the finding being reused.",
    )
