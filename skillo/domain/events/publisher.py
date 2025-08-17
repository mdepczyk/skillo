from typing import Dict, List, Type

from .base import BaseEvent, EventHandler, EventPublisher


class DomainEventPublisher(EventPublisher):
    """In-memory domain event publisher implementation."""

    def __init__(self) -> None:
        self._handlers: Dict[Type[BaseEvent], List[EventHandler]] = {}

    def publish(self, event: BaseEvent) -> None:
        """Publish event to all registered handlers."""
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        for handler in handlers:
            handler.handle(event)

    def subscribe(
        self, event_type: Type[BaseEvent], handler: EventHandler
    ) -> None:
        """Subscribe handler to event type."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)

    def clear(self) -> None:
        """Clear all subscriptions"""
        self._handlers.clear()
