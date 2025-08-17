from skillo.application.facade import ApplicationFacade
from skillo.domain.events import (
    DatabaseResetEvent,
    DocumentExportCompletedEvent,
    DocumentExportFailedEvent,
    DocumentUploadedEvent,
    DocumentUploadFailedEvent,
    MatchingCompletedEvent,
    MatchingFailedEvent,
)
from skillo.infrastructure.di_container import (
    ServiceContainerAdapter,
    create_container,
)
from skillo.ui.app import run_ui
from skillo.ui.components.notification import StreamlitNotificationHandler


def main():
    """Application entry point."""
    di_container = create_container()

    service_container = ServiceContainerAdapter(di_container)

    app_facade = ApplicationFacade(service_container)

    publisher = di_container.event_publisher()
    notification_handler = StreamlitNotificationHandler()

    publisher.subscribe(MatchingCompletedEvent, notification_handler)
    publisher.subscribe(MatchingFailedEvent, notification_handler)
    publisher.subscribe(DocumentUploadedEvent, notification_handler)
    publisher.subscribe(DocumentUploadFailedEvent, notification_handler)
    publisher.subscribe(DatabaseResetEvent, notification_handler)
    publisher.subscribe(DocumentExportCompletedEvent, notification_handler)
    publisher.subscribe(DocumentExportFailedEvent, notification_handler)

    run_ui(app_facade)


if __name__ == "__main__":
    main()
