from typing import Protocol, Type


class BaseEvent(Protocol):
    """Base domain event protocol."""

    @property
    def event_type(self) -> str:
        """Event type."""
        ...

    @property
    def message(self) -> str:
        """Event message."""
        ...

    @property
    def level(self) -> str:
        """Event level."""
        ...


class EventHandler(Protocol):
    """Event handler protocol."""

    def handle(self, event: BaseEvent) -> None:
        """Handle domain event."""
        ...


class EventPublisher(Protocol):
    """Event publisher protocol."""

    def publish(self, event: BaseEvent) -> None:
        """Publish event to handlers."""
        ...

    def subscribe(
        self, event_type: Type[BaseEvent], handler: EventHandler
    ) -> None:
        """Subscribe handler to event type."""
        ...
