from dataclasses import dataclass


@dataclass
class MatchingCompletedEvent:
    """Matching completed event."""

    message: str
    context: str

    @property
    def event_type(self) -> str:
        return "MATCHING_COMPLETED"

    @property
    def level(self) -> str:
        return "success"


@dataclass
class MatchingFailedEvent:
    """Matching failed event."""

    error_message: str
    context: str

    @property
    def event_type(self) -> str:
        return "MATCHING_FAILED"

    @property
    def message(self) -> str:
        return f"{self.context}: {self.error_message}"

    @property
    def level(self) -> str:
        return "error"
