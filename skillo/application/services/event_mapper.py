from skillo.application.dto import EventDto
from skillo.domain.events.base import BaseEvent


class EventMapper:
    """Maps domain events to application DTOs."""

    @staticmethod
    def to_dto(domain_event: BaseEvent) -> EventDto:
        """Convert domain event to application DTO."""
        return EventDto(
            event_type=domain_event.event_type,
            message=domain_event.message,
            level=domain_event.level,
        )
