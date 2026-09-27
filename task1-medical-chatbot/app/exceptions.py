"""Application-specific errors.

Defining our own error types lets the route layer map a failure to the right HTTP
status without inspecting exception messages from third-party libraries.
"""


class MedicalChatbotError(Exception):
    """Base class for every error this application raises deliberately."""

    error_code = "internal_error"
    status_code = 500
    message = "An unexpected error occurred."

    def __init__(self, detail: str | None = None) -> None:
        self.detail = detail or self.message
        super().__init__(self.detail)


class LLMUnavailableError(MedicalChatbotError):
    """The language model could not be reached, or the request failed."""

    error_code = "llm_unavailable"
    status_code = 503
    message = "The assistant is temporarily unavailable. Please try again shortly."


class SessionNotFoundError(MedicalChatbotError):
    """Asked to clear a session that does not exist."""

    error_code = "session_not_found"
    status_code = 404
    message = "No conversation found for that session_id."
