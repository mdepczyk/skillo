from skillo.domain.events import DatabaseResetEvent, EventPublisher
from skillo.domain.repositories import ManagementRepository


class ResetDatabase:
    """Reset database."""

    def __init__(
        self,
        management_repository: ManagementRepository,
        event_publisher: EventPublisher,
    ):
        """Initialize with dependencies."""
        self._management_repository = management_repository
        self._event_publisher = event_publisher

    def execute(self) -> bool:
        """Execute database reset workflow."""
        try:
            success = self._management_repository.reset_database()

            event = DatabaseResetEvent(
                success=success,
                error_message="" if success else "Failed to reset database",
            )
            self._event_publisher.publish(event)

            return success

        except Exception as e:
            error_msg = f"Database reset workflow failed: {str(e)}"
            event = DatabaseResetEvent(success=False, error_message=error_msg)
            self._event_publisher.publish(event)
            return False
