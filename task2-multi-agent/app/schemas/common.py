"""Shapes used by more than one endpoint."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Returned by GET /health."""

    status: str = Field(..., examples=["ok"])
    app: str
    version: str


class ErrorResponse(BaseModel):
    """A consistent error shape, so clients never have to parse a stack trace."""

    error: str = Field(..., description="Short machine-readable error code.")
    detail: str = Field(..., description="Human-readable explanation.")
