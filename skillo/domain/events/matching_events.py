from .base import BaseEvent


class MatchingCompletedEvent(BaseEvent):
    """Matching completed event."""

    def __init__(self, message: str, context: str, result_count: int = 0):
        super().__init__()
        self._message = message
        self.context = context
        self.result_count = result_count

    @property
    def event_type(self) -> str:
        return "MATCHING_COMPLETED"

    @property
    def message(self) -> str:
        return self._message

    @property
    def level(self) -> str:
        return "success"


class MatchingFailedEvent(BaseEvent):
    """Matching failed event."""

    def __init__(
        self, error_message: str, context: str, exception_type: str = ""
    ):
        super().__init__()
        self.error_message = error_message
        self.context = context
        self.exception_type = exception_type

    @property
    def event_type(self) -> str:
        return "MATCHING_FAILED"

    @property
    def message(self) -> str:
        return f"{self.context}: {self.error_message}"

    @property
    def level(self) -> str:
        return "error"
