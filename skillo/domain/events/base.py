from abc import ABC, abstractmethod
from datetime import datetime
from typing import Protocol, Type
from uuid import uuid4


class BaseEvent(ABC):
    """Base domain event."""

    def __init__(self):
        self.event_id = str(uuid4())
        self.occurred_at = datetime.utcnow()

    @property
    @abstractmethod
    def event_type(self) -> str:
        """Event type."""
        pass

    @property
    @abstractmethod
    def message(self) -> str:
        """Event message."""
        pass

    @property
    @abstractmethod
    def level(self) -> str:
        """Event level."""
        pass


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
