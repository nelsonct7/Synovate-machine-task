"""Application-specific errors."""


class AssistantError(Exception):
    """Base class for every error this application raises deliberately."""

    error_code = "internal_error"
    status_code = 500
    message = "An unexpected error occurred."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.message
        super().__init__(self.detail)


class LLMUnavailableError(AssistantError):
    """The language model could not be reached, or the request failed."""

    error_code = "llm_unavailable"
    status_code = 503
    message = "The research service is temporarily unavailable. Please try again shortly."


class GraphExecutionError(AssistantError):
    """The agent workflow failed to complete."""

    error_code = "graph_execution_failed"
    status_code = 500
    message = "The research workflow did not complete successfully."

class ToolExecutionError(AssistantError):
    """A tool failed while the agent was using it."""

    error_code = "tool_failed"
    status_code = 502
    message = "A research tool failed. The answer may be incomplete."

