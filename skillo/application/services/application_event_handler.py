from skillo.application.protocols import EventHandler as AppEventHandler
from skillo.application.services.event_mapper import EventMapper
from skillo.domain.events.base import BaseEvent


class ApplicationEventHandler:
    """Converts domain events to application DTOs and forwards to UI handler."""

    def __init__(self, ui_handler: AppEventHandler):
        """Initialize with UI event handler."""
        self._ui_handler = ui_handler

    def handle(self, domain_event: BaseEvent) -> None:
        """Handle domain event by converting to DTO."""
        event_dto = EventMapper.to_dto(domain_event)
        self._ui_handler.handle(event_dto)
